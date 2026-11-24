"""Validate evidence, then generate versioned YAML recipes without overwriting."""
import copy
import hashlib
from pathlib import Path

import yaml

from tools.specs import Catalog, SpecError, key, read
from .metax import parse
from .probes.torch_bench import active_gpu_pids
from .runner import verify


def ref(doc):
    return {k: doc[k] for k in ('id', 'version')}


def meta(kind, identity, version, title, source=None, locator='/'):
    return dict(schema_version='0.2.0', kind=kind, id=identity, version=version, title=title,
                provenance=[dict(source_ref=ref(source), locator=locator)] if source else [], issues=[], extensions={})


def measurement_rows(attempt, protocol):
    """Match the full expected matrix; schema semantics independently recompute rates."""
    result = attempt['result']
    if attempt['status'] != 'measured' or attempt['returncode'] != 0 or result['status'] != 'measured':
        raise SpecError('unsuccessful GPU attempt cannot be exported as a measurement')
    if int(result['physical_ordinal']) != attempt['ordinal'] or result['device_index'] != 0:
        raise SpecError('physical/logical device mismatch')
    if result.get('visible_device_count', 1) != 1:
        raise SpecError('multiple GPUs were visible inside the isolated runtime')
    if result['protocol'] != protocol or result['isolation'] != 'exclusive_preflight_only':
        raise SpecError('executed protocol/isolation differs from plan')
    if result['timer'] != 'torch.cuda.Event.elapsed_time':
        raise SpecError('unexpected measurement timer')
    for name in ('before', 'after'):
        snapshot = attempt[name]
        if snapshot.get('returncode') != 0 or active_gpu_pids(snapshot['stdout']):
            raise SpecError('idle process preflight/postflight evidence missing')
    for name in ('warmup_iterations', 'iterations_per_sample', 'repeats'):
        if result[name] != protocol[name]:
            raise SpecError(f'protocol mismatch: {name}')
    expected = {(f'gemm_{dtype}_{m}x{n}x{k}'): ('gemm', f'torch.{dtype}', [m,n,k], None)
                for dtype in protocol['dtypes'] for m,n,k in protocol['gemm_shapes']}
    expected.update({f'device_copy_{mib}mib': ('device_copy', 'torch.float32', None, mib*1024**2)
                     for mib in protocol['copy_sizes_mib']})
    actual = result['measurements']
    if len(actual) != len(expected) or {m['name'] for m in actual} != set(expected):
        raise SpecError('measurement matrix incomplete or duplicated')
    rows = []
    for m in actual:
        metric, dtype, shape, payload = expected[m['name']]
        if (m['dtype'], m.get('shape_mnk'), m.get('payload_bytes')) != (dtype, shape, payload):
            raise SpecError('measurement shape/dtype/payload differs from plan')
        if len(m['samples_ms']) != protocol['repeats'] or (metric == 'gemm' and m.get('allow_tf32') is not False):
            raise SpecError('sample count or TF32 mode differs from protocol')
        formula = '2*M*N*K/(median_ms/1000)/1e12' if metric == 'gemm' else '2*payload_bytes/(median_ms/1000)/1e9'
        if m['formula'] != formula:
            raise SpecError('measurement formula differs from protocol')
        rows.append(dict(name=m['name'], metric=metric, dtype=dtype, shape_mnk=shape, payload_bytes=payload,
                         warmup_iterations=protocol['warmup_iterations'], iterations_per_sample=protocol['iterations_per_sample'],
                         **{k: m[k] for k in ('samples_ms', 'statistic', 'value', 'unit', 'correctness', 'formula')}))
    return rows


def build(run, destination, catalog):
    run, destination = Path(run).resolve(), Path(destination).resolve()
    if not destination.is_relative_to(catalog.root):
        raise SpecError('export destination must be inside the repository for portable source references')
    if destination.is_relative_to(catalog.root/'schemas'):
        raise SpecError('schemas holds standards only; export to the repository root or a review directory')
    manifest, plan = verify(run)
    if manifest['status'] != 'complete':
        raise SpecError('incomplete runs cannot be exported; inspect report and rerun into a new directory')
    evidence = destination/'experiments/evidence'/plan['id']/plan['version']
    version = plan['version']
    documents = []
    for host_entry, host_plan in zip(manifest['hosts'], plan['hosts']):
        raw = read(run/host_entry['path'])
        if raw['ssh_host'] != host_plan['ssh']:
            raise SpecError('SSH alias differs from plan')
        facts = parse(raw['inventory'])
        indices = [d['observed']['ordinal'] for d in facts['devices']]
        selected = indices if host_plan['devices'] == 'all' else host_plan['devices']
        if raw['selected_devices'] != selected or len(selected) > host_plan['max_devices']:
            raise SpecError('selected device set differs from plan')
        prefix = f'{plan["id"]}-{host_entry["id"]}'
        source = meta('SourceDocument', f'source-{prefix}', version, f'{prefix} raw hardware evidence')
        source.update(path=(evidence/host_entry['path']).relative_to(catalog.root).as_posix(),
                      sha256=manifest['files'][host_entry['path']], media_type='application/json',
                      role='calibration' if manifest['mode'] == 'run' else 'machine_inventory', authority='machine_collected',
                      coverage=dict(status='partial', description='Inventory and selected single-device kernels; no collective or model performance.'))
        source['extensions']['hardware.manifest'] = dict(path=(evidence/'manifest.json').relative_to(catalog.root).as_posix(),
                                                       sha256=hashlib.sha256((run/'manifest.json').read_bytes()).hexdigest())
        documents.append(('sources', source))
        devices, by_ordinal = [], {}
        for device in facts['devices']:
            observed = device['observed']
            ordinal = observed['ordinal']
            profile = meta('HardwareSpec', f'{prefix}-gpu{ordinal}-device', version, device['product'], source, '/inventory')
            profile.update(profile_type='device', vendor=device['vendor'], product=device['product'],
                specifications=[dict(name='memory_capacity', quantity=dict(value=observed['memory_bytes'], unit='bytes', basis='measured'),
                                     precision=None, operation=None, conditions='Management-reported physical VRAM, including driver-reserved memory.')],
                interfaces=[dict(name='memory', properties=dict(type=device['memory_type'])),
                            dict(name='pcie', properties=dict(negotiated_speed_gt_s=observed['pcie_speed_gt_s'], lanes=observed['pcie_lanes']))],
                resources=dict(allocated_devices=None, nodes=[], topology=[]), capabilities=[])
            documents.append(('hardware', profile))
            mapped = dict(device_id=f'{host_entry["id"]}-gpu{ordinal}-{observed["board_serial"]}',
                          device_profile_ref=ref(profile), observed=observed)
            devices.append(mapped)
            by_ordinal[ordinal] = mapped
        hardware = meta('HardwareSpec', f'{prefix}-host', version, f'{raw["hostname"]} observed hardware', source, '/inventory')
        discovery = facts['discovery']
        discovery['inventory_source_ref'] = ref(source)
        hardware.update(profile_type='cluster', vendor='MetaX', product=raw['hostname'], specifications=[], interfaces=[],
            evidence_level='inspected', discovery=discovery, capabilities=[],
            resources=dict(allocated_devices=len(devices), nodes=[dict(node_id=host_entry['id'], devices=devices, cpu=facts['cpu'],
                dram_gb=discovery['dram_bytes']/1e9, nics=facts['nics'])],
                topology=[dict(**{'from': by_ordinal[i]['device_id'], 'to': by_ordinal[j]['device_id']}, link=link, plane=None)
                          for i,j,link in facts['topology']]))
        hardware['issues'].append(dict(code='health-not-certified', path='/discovery/health', status='unverified', blocking=True,
            reason='Review raw device errors and perform link/ECC diagnostics before using this node as an accepted hardware baseline.'))
        if any(d['observed']['driver_reserved_bytes'] is None for d in devices):
            hardware['issues'].append(dict(code='driver-reservation-unreported', path='/resources/nodes', status='missing', blocking=False,
                reason='This mx-smi/driver combination does not report driver-reserved memory; null means unknown, not zero.'))
        documents.append(('hardware', hardware))
        if manifest['mode'] == 'inspect':
            if raw['attempts']:
                raise SpecError('inspection contains unexpected GPU test attempts')
            continue
        if raw['image_id'] != host_plan['image'] or [a['ordinal'] for a in raw['attempts']] != selected:
            raise SpecError('image or measured device set differs from plan')
        for index, attempt in enumerate(raw['attempts']):
            rows = measurement_rows(attempt, plan['protocol'])
            measured, ordinal = attempt['result'], attempt['ordinal']
            # Runtime-visible VRAM may exclude reservations; never replace physical VRAM with it.
            observed = by_ordinal[ordinal]['observed']
            if not 0 < measured['memory_bytes'] <= observed['memory_bytes']:
                raise SpecError('runtime-visible memory exceeds discovered physical memory')
            identity = f'{prefix}-gpu{ordinal}'
            runtime = meta('RuntimeSpec', identity+'-runtime', version, f'{identity} calibration runtime', source, f'/attempts/{index}')
            runtime.update(engine='pytorch', version_label=measured['torch_version'], source_commit=None,
                container_digest=raw['image_id'], container_identity_kind='docker_image_id', driver=discovery['driver_version'],
                device_runtime='MACA '+discovery['device_runtime_version']+' (host)', compiler=None,
                libraries=measured['packages'], launch_parameters=dict(MACA_VISIBLE_DEVICES=str(ordinal), torch_num_threads=1, allow_tf32=False),
                status='environment_verified')
            documents.append(('runtimes', runtime))
            measurement = meta('HardwareMeasurement', identity+'-measurement', version, f'{identity} single-device kernel measurements',
                               source, f'/attempts/{index}/result')
            measurement.update(hardware_ref=ref(hardware), runtime_ref=ref(runtime), captured_at=measured['captured_at'],
                device_ids=[by_ordinal[ordinal]['device_id']], evidence_kind='measured', isolation=measured['isolation'],
                timer=measured['timer'], measurements=rows, limitations=[
                    'Selected shapes, dtypes and copy sizes only; not a theoretical peak or model throughput.',
                    'Device copy counts read plus write bytes; cache effects are possible, especially for small buffers.',
                    'No PCIe host transfer, P2P, collective, inter-node bandwidth or sustained thermal/power test.',
                    'Host idle snapshots and a cooperative lock do not guarantee exclusive access throughout the test.',
                    'Constant tensors provide a smoke correctness check, not comprehensive numerical validation.'])
            measurement['extensions']['hardware.protocol'] = copy.deepcopy(plan['protocol'])
            documents.append(('measurements', measurement))
    return manifest, evidence, documents


def export(run, destination, catalog=None):
    catalog = catalog or Catalog()
    catalog.load()
    manifest, evidence, documents = build(run, destination, catalog)
    paths = []
    for group, doc in documents:
        path = Path(destination).resolve()/'recipes'/group/f'{doc["id"]}-{doc["version"]}.yaml'
        if key(doc) in catalog.documents or path.exists():
            raise SpecError(f'recipe identity/path already exists: {doc["id"]}@{doc["version"]}; use a new plan version')
        catalog.documents[key(doc)] = doc
        catalog.paths[key(doc)] = path
        paths.append(path)
    if evidence.exists():
        raise SpecError(f'evidence already exists: {evidence}')
    for _, doc in documents:
        errors = catalog.structural_errors(doc)
        if not errors:
            errors = catalog.semantic_errors(doc)
        if errors:
            raise SpecError(f'{doc["id"]}: ' + '\n'.join(errors))
    # Copy only verified files, preserving the run's manifest and exact executed scripts.
    evidence.mkdir(parents=True, exist_ok=False)
    for name in [*manifest['files'], 'manifest.json']:
        target = evidence/name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as stream:
            stream.write((Path(run)/name).read_bytes())
    verify(evidence)
    for (group, doc), path in zip(documents, paths):
        errors = catalog.semantic_errors(doc, verify_sources=True)
        if errors:
            raise SpecError('\n'.join(errors))
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            yaml.safe_dump(doc, stream, allow_unicode=True, sort_keys=False)
    return paths
