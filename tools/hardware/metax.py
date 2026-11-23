"""Parse recorded MetaX/Linux observations. Missing required facts fail export."""
import json
import re

from tools.specs import SpecError
from .probes.torch_bench import active_gpu_pids


def output(raw, name):
    command = raw['commands'][name]
    if command.get('returncode') != 0:
        raise SpecError(f'inventory command failed: {name}')
    return command['stdout']


def fields(text):
    return {k.strip(): v.strip() for k, v in re.findall(r'^\s*([^:\n]+?)\s*:\s*(.*?)\s*$', text, re.M)}


def gpu_blocks(text):
    matches = list(re.finditer(r'^GPU#(\d+)\s+\S+\s+([0-9a-fA-F:.]+)\s*$', text, re.M))
    return {int(m[1]): (m[2].lower(), fields(text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)]))
            for i, m in enumerate(matches)}


def kib(value):
    match = re.fullmatch(r'(\d+)\s+[kK][bB]', value)
    if not match:
        raise SpecError(f'unsupported memory unit: {value}')
    return int(match[1]) * 1024


def parse(raw):
    try:
        text = output(raw, 'gpu')
        gpu = json.loads(text[text.index('{'):])
        rows = sorted(((bdf.lower(), d) for bdf, d in gpu.items() if isinstance(d, dict) and 'device_id' in d),
                      key=lambda row: row[1]['device_id'])
        if not rows or len(rows) != gpu['attached_gpus']:
            raise SpecError('GPU count does not match inventory')
        hw = gpu_blocks(output(raw, 'hwinfo'))
        memory = gpu_blocks(output(raw, 'memory'))
        pci = {d['address'].lower(): d for d in raw['pci']}
        cpu = {d['field'].rstrip(':'): d['data'] for d in json.loads(output(raw, 'cpu'))['lscpu']}
        notes = ['Health requires separate diagnostics; inventory and GEMM do not certify link/ECC health.']
        unavailable = False
        devices = []
        for bdf, d in rows:
            i = d['device_id']
            if hw[i][0] != bdf or memory[i][0] != bdf:
                raise SpecError('ordinal/BDF mismatch across inventory commands')
            h, m, p = hw[i][1], memory[i][1], pci[bdf]
            reason = d.get('unavailable_reason')
            if reason:
                unavailable = True
                notes.append(f'GPU{i} unavailable: {reason}')
            for category in ('pci_event_info', 'ras_count'):
                for key, value in d.get(category, {}).items():
                    if value:
                        notes.append(f'GPU{i} {category}/{key}: {json.dumps(value)}')
            speed = re.fullmatch(r'([0-9.]+) GT/s(?: PCIe)?', p['current_link_speed'])
            if speed is None:
                raise SpecError('unrecognized PCIe speed')
            devices.append(dict(product=h['Model Name'], vendor=h['Manufacturer'], memory_type=h['Memory Type'],
                observed=dict(ordinal=i, pci_bus_id=bdf, board_serial=h['Board Serial Number'],
                    chip_serial=h['Chip Serial Number'], memory_bytes=kib(m['vram total']),
                    numa_node=int(p['numa_node']), local_cpus=p['local_cpulist'],
                    pcie_speed_gt_s=float(speed[1]), pcie_lanes=int(p['current_link_width']),
                    driver_reserved_bytes=kib(m['vram driver reserved']) if 'vram driver reserved' in m else None, observed_used_memory_bytes=kib(m['vram used']),
                    observed_utilization_percent=float(d['utilization']))))
        topology = []
        topo = raw['commands'].get('topology', {})
        # A failed topology query is recorded as unknown, never converted to a measured link.
        if topo.get('returncode') == 0:
            header = re.search(r'^\s+(GPU\d+(?:\s+GPU\d+)+)', topo['stdout'], re.M)
            order = [int(x) for x in re.findall(r'GPU(\d+)', header[1])] if header else []
            if len(devices) == 1:
                order = [devices[0]['observed']['ordinal']]
            if set(order) != {d['observed']['ordinal'] for d in devices}:
                raise SpecError('topology columns differ from inventory')
            matrix = {}
            for line in topo['stdout'].splitlines():
                match = re.match(r'^GPU(\d+)\s+(.*)', line)
                if match:
                    matrix[int(match[1])] = match[2].split()[:len(order)]
            if set(matrix) != set(order) or any(len(v) != len(order) for v in matrix.values()):
                raise SpecError('incomplete topology matrix')
            for i, ordinal in enumerate(order):
                if matrix[ordinal][i] != 'X':
                    raise SpecError('invalid topology diagonal')
                for j in range(i+1, len(order)):
                    link = matrix[ordinal][j]
                    if link != matrix[order[j]][i]:
                        raise SpecError('asymmetric topology matrix')
                    topology.append((ordinal, order[j], link))
        else:
            notes.append('Topology command unavailable; inter-device paths are unknown.')
        dram = re.search(r'^MemTotal:\s+(\d+) kB$', raw['meminfo'], re.M)
        os_name = re.search(r'^PRETTY_NAME="(.*)"$', raw['os_release'], re.M)
        discovery = dict(captured_at=raw['captured_at'], hostname=raw['hostname'], os=os_name[1], kernel=raw['kernel'],
            driver_version=gpu['driver_version'], device_runtime_version=gpu['maca_version'],
            management_tool_version=gpu['smi_version'], cpu_sockets=int(cpu['Socket(s)']),
            cores_per_socket=int(cpu['Core(s) per socket']), threads_per_core=int(cpu['Thread(s) per core']),
            logical_cpus=int(cpu['CPU(s)']), numa_nodes=int(cpu['NUMA node(s)']), dram_bytes=int(dram[1])*1024,
            availability='unavailable' if unavailable else ('occupied' if active_gpu_pids(output(raw, 'processes')) else 'idle'),
            health='degraded' if len(notes) > 1 and any('GPU' in n for n in notes[1:]) else 'unverified', health_notes=notes)
        return dict(discovery=discovery, devices=devices, topology=topology, cpu=cpu['Model name'],
                    nics=[n['ifname'] for n in json.loads(output(raw, 'nics')) if n['ifname'] != 'lo'])
    except (KeyError, IndexError, TypeError, ValueError, RuntimeError) as exc:
        raise SpecError(f'cannot normalize MetaX inventory: {exc}') from exc
