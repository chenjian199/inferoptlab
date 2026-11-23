"""Versioned reference resolution, matrix expansion and offline snapshots."""
from __future__ import annotations

import copy
import random
from urllib.parse import urlparse

from tools.specs import Catalog, SpecError, digest, key, references, walk
from benchmark.io import inside


def semantic_errors(catalog, doc, verify_sources=False):
    if doc['kind'] == 'ResolvedBenchmark':
        return snapshot_errors(catalog, doc, verify_sources)
    if doc['kind'] == 'MeasurementBundle':
        counts = doc['counts']
        errors = []
        if counts['succeeded'] + counts['failed'] != counts['planned']:
            errors.append('measurement success and failure counts must cover all planned requests')
        if doc['validity'] == 'valid' and (doc['issues'] or counts['missing']):
            errors.append('valid measurement cannot contain missing records or issues')
        return errors
    errors = []
    for path, reference, expected in references(doc):
        try:
            target = catalog.get(reference)
            if expected and target['kind'] != expected:
                errors.append(f'{path}: expected {expected}, got {target["kind"]}')
        except SpecError as exc:
            errors.append(str(exc))
    if errors:
        return errors
    if doc['kind'] == 'DeploymentSpec':
        serving = doc['serving']
        parsed = urlparse(serving['url'])
        if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in {'', '/'}:
            errors.append('serving.url must be an HTTP(S) base URL without credentials, query or path')
        devices = doc['devices']
        for field in ('rank', 'device_id', 'visible_index'):
            if len({d[field] for d in devices}) != len(devices):
                errors.append(f'device {field} values must be unique')
        if devices and sorted(d['rank'] for d in devices) != list(range(len(devices))):
            errors.append('ranks must be contiguous from zero')
        hardware = catalog.get(doc['hardware_ref'])
        inventory = {d['device_id'] for n in hardware['resources']['nodes'] for d in n['devices']}
        if devices and not {d['device_id'] for d in devices} <= inventory:
            errors.append('deployment devices must occur in the hardware inventory')
        selected={d['device_id'] for d in devices}
        nodes={n['node_id'] for n in hardware['resources']['nodes'] if any(d['device_id'] in selected for d in n['devices'])}
        if serving['management']=='sglang' and len(nodes)>1:
            errors.append('v1 managed adapter requires all selected devices on one node')
        runtime = catalog.get(doc['runtime_ref'])
        if runtime['engine'] not in {'sglang', 'vllm', 'vllm-metax'}:
            errors.append('deployment adapter requires SGLang or vLLM')
        if runtime['engine'] != 'sglang' and serving['management'] != 'external':
            errors.append('vLLM requires external service management')
    elif doc['kind'] == 'BenchmarkScenario':
        try:
            inside(catalog.root, doc['dataset_dir'])
        except SpecError as exc:
            errors.append(str(exc))
    elif doc['kind'] == 'BenchmarkPlan':
        study = catalog.get(doc['study_ref'])
        if study['budget']['max_candidates'] is not None and len(doc['deployment_refs'])>study['budget']['max_candidates']:
            errors.append('deployment count exceeds the Study candidate budget')
        if study['budget']['max_wall_hours'] is not None and doc['budget']['max_wall_seconds']>study['budget']['max_wall_hours']*3600:
            errors.append('plan wall-time budget exceeds the Study budget')
        for field in ('scenario_refs', 'deployment_refs'):
            if len({key(r) for r in doc[field]}) != len(doc[field]):
                errors.append(f'{field} must be unique')
        for reference in doc['deployment_refs']:
            deployment = catalog.get(reference)
            for field in ('model_ref', 'hardware_ref', 'runtime_ref'):
                if deployment[field] != study[field]:
                    errors.append(f'{deployment["id"]}: {field} differs from study')
            if deployment['mode'] not in study['allowed_deployment_modes']:
                errors.append(f'{deployment["id"]}: deployment mode not allowed by study')
        for reference in doc['scenario_refs']:
            scene = catalog.get(reference)
            if scene['case_ref'] not in study['case_refs']:
                errors.append(f'{scene["id"]}: case is outside study')
        for url in doc['aiperf']['server_metrics'] + doc['aiperf']['gpu_telemetry']:
            parsed = urlparse(url)
            if parsed.scheme not in {'http', 'https'} or not parsed.hostname or parsed.username or parsed.password:
                errors.append('telemetry endpoints must be HTTP(S) URLs without credentials')
    return errors


def scenario_parts(catalog, reference):
    scenario = catalog.get(reference)
    case = catalog.get(scenario['case_ref'])
    return scenario, case, catalog.get(case['workload_ref']), catalog.get(case['protocol_ref'])


def execution_issues(catalog, plan):
    """Implementable protocol requirements, distinct from full formal readiness."""
    issues = []
    from benchmark.adapters import for_runtime
    for reference in plan['deployment_refs']:
        deployment = catalog.get(reference)
        runtime = catalog.get(deployment['runtime_ref'])
        issues.extend(f'{deployment["id"]}: {e}' for e in for_runtime(runtime).configuration_issues(deployment, runtime))
    for reference in plan['scenario_refs']:
        scene, case, workload, protocol = scenario_parts(catalog, reference)
        local = []
        if protocol['method'] not in {'full_request', 'prefill_one_token'}:
            local.append('v1 supports full_request and prefill_one_token; cached/fake prefill needs a dedicated protocol')
        if workload['arrival']['mode'] != 'closed_loop' or workload['arrival']['load_unit'] != 'concurrency':
            local.append('v1 execution requires closed_loop concurrency')
        if not workload['arrival']['load_points']:
            local.append('load points are missing')
        if workload['requests']['count'] and any(c > workload['requests']['count'] for c in workload['arrival']['load_points']):
            local.append('request count must be at least the largest concurrency point')
        if not workload['input']['tokens'] or not workload['output']['tokens'] or not workload['requests']['count']:
            local.append('exact input/output token lengths and request count are required')
        if any(catalog.get(r)['mode'] not in protocol['allowed_deployment_modes'] for r in plan['deployment_refs']):
            local.append('deployment mode is not allowed by the selected protocol')
        if workload['requests']['seed'] is None:
            local.append('request seed is required')
        if workload['generation'] != dict(ignore_eos=True, sampling='greedy', stop_policy='fixed_output_tokens'):
            local.append('v1 requires greedy, ignore_eos=true, fixed_output_tokens')
        if workload['cache']['prefix_reuse'] != 'disabled' or workload['cache']['preparation'] != 'disable_prefix_cache':
            local.append('v1 requires disable_prefix_cache; cache reuse must be tested separately')
        timing = protocol['timing']
        if (timing['window'], timing['start'], timing['finish']) != ('fixed_request_set', 'first_actual_send', 'last_completion_or_timeout'):
            local.append('unsupported measurement window')
        if timing['ttft_boundary'] != 'client_submit_to_first_content_token':
            local.append('unsupported TTFT boundary')
        if workload['output']['tokens'] != 1 and timing['tpot_boundary'] != 'first_to_last_token_over_n_minus_one':
            local.append('unsupported TPOT boundary')
        execution = protocol['execution']
        if execution.get('warmup_request_count') is None or not execution['repetitions'] or not execution['timeout_s']:
            local.append('numeric warmup_request_count, repetitions and timeout_s are required')
        if execution['profiler_during_scoring'] is not False:
            local.append('profiling during scoring must be disabled')
        if protocol['accounting'] != dict(primary_population='all_planned_requests', failure_policy='retain_in_denominator', logical_request_deduplication=True):
            local.append('unsupported failure accounting')
        if plan['mode'] == 'exploratory' and case['purpose'] != 'diagnostic':
            local.append('exploratory mode requires an explicitly diagnostic Case; contract cases require formal mode')
        issues.extend(f'{scene["id"]}: {message}' for message in local)
    return sorted(set(issues))


def expand(catalog, plan):
    trials = []
    repetitions = [scenario_parts(catalog, r)[3]['execution']['repetitions'] or 1 for r in plan['scenario_refs']]
    rng = random.Random(plan['order_seed'])
    for repeat in range(1, max(repetitions) + 1):
        deployments = list(plan['deployment_refs'])
        rng.shuffle(deployments)
        for deployment in deployments:
            for reference in plan['scenario_refs']:
                scene, case, workload, protocol = scenario_parts(catalog, reference)
                if repeat > (protocol['execution']['repetitions'] or 1):
                    continue
                for concurrency in workload['arrival']['load_points']:
                    fingerprint = dict(case=case, workload=workload, protocol=protocol,
                        study=catalog.get(plan['study_ref']), aiperf=plan['aiperf'], concurrency=concurrency,
                        documents=[digest(d) for d in catalog.closure(case)])
                    item = dict(deployment_ref=deployment, scenario_ref=reference, concurrency=int(concurrency), repetition=repeat,
                                comparison_sha256=digest(fingerprint))
                    identity={k:v for k,v in item.items() if k!='repetition'}
                    trials.append(dict(id='trial-' + digest(identity)[:16], **item))
    if not trials:
        raise SpecError('no trials: populate workload load_points first')
    if len(trials) > plan['budget']['max_runs']:
        raise SpecError(f'matrix has {len(trials)} runs, exceeding max_runs={plan["budget"]["max_runs"]}')
    return trials


def resolve(catalog, plan, freeze=False, verify_sources=None):
    if plan.get('kind') != 'BenchmarkPlan':
        raise SpecError('expected BenchmarkPlan')
    errors = catalog.structural_errors(plan)
    if errors:
        raise SpecError('\n'.join(errors))
    documents = catalog.closure(plan)
    for document in documents:
        errors += catalog.structural_errors(document)
        errors += catalog.semantic_errors(document, verify_sources=freeze if verify_sources is None else verify_sources)
    if errors:
        raise SpecError('\n'.join(errors))
    readiness = catalog.readiness_issues(documents)
    readiness=sorted(set(readiness))
    runnable = execution_issues(catalog, plan)
    if freeze and (readiness or runnable):
        raise SpecError('cannot freeze benchmark:\n' + '\n'.join(sorted(set(readiness + runnable))))
    payload = dict(schema_version='0.2.0', kind='ResolvedBenchmark', plan_ref=dict(id=plan['id'], version=plan['version']),
        state='frozen' if freeze else 'draft', documents=[dict(ref=dict(id=d['id'],version=d['version']),sha256=digest(d),document=copy.deepcopy(d)) for d in documents],
        readiness_issues=readiness, execution_issues=runnable, trials=expand(catalog, plan))
    return dict(**payload, content_sha256=digest(payload))


def embedded_catalog(catalog, snapshot):
    embedded = Catalog(catalog.root)
    for entry in snapshot['documents']:
        document = entry['document']
        errors = embedded.structural_errors(document)
        if document.get('kind') in {'ResolvedBenchmark', 'ResolvedStudy', 'RecipeTemplate', 'MeasurementBundle'}:
            errors.append('nested snapshots, results and templates are not benchmark inputs')
        if errors:
            raise SpecError('\n'.join(errors))
        if key(entry['ref']) != key(document) or digest(document) != entry['sha256']:
            raise SpecError('embedded document identity/hash mismatch')
        if key(document) in embedded.documents:
            raise SpecError('duplicate embedded document')
        embedded.documents[key(document)] = document
    return embedded


def snapshot_errors(catalog, snapshot, verify_sources=False):
    try:
        if digest({k:v for k,v in snapshot.items() if k != 'content_sha256'}) != snapshot['content_sha256']:
            return ['benchmark snapshot content hash mismatch']
        embedded = embedded_catalog(catalog, snapshot)
        plan = embedded.get(snapshot['plan_ref'])
        # Recompute closure, readiness and matrix, rather than trusting a frozen flag.
        expected = resolve(embedded, plan, freeze=snapshot['state'] == 'frozen', verify_sources=verify_sources)
        if expected != snapshot:
            return ['snapshot closure, matrix or computed issues differ from embedded inputs']
        return []
    except (SpecError, KeyError, ValueError) as exc:
        return [str(exc)]
