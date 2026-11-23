"""Verify sealed artifacts and recompute requests; never infer from chart pixels."""
import json
import math
from pathlib import Path

from tools.specs import SpecError, digest, read
from benchmark.io import inside, file_hash
from benchmark.cli import load_snapshot
from benchmark.planner import embedded_catalog, scenario_parts
from benchmark.metrics.normalize import normalize
from benchmark.adapters.aiperf import telemetry_issues


def close(a,b):
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(close(a[k],b[k]) for k in a)
    if isinstance(a,list):return isinstance(b,list) and len(a)==len(b) and all(close(x,y) for x,y in zip(a,b))
    if isinstance(a,float):return isinstance(b,(float,int)) and math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
    return a==b


def sealed_files(root,entry):
    path=inside(root,entry['manifest'])
    if file_hash(path)!=entry['manifest_sha256']:raise SpecError('evidence manifest hash mismatch')
    manifest=read(path)
    result={}
    for name,expected in manifest.items():
        p=inside(path.parent,name)
        if not isinstance(expected,str) or len(expected)!=64 or file_hash(p)!=expected:
            raise SpecError('sealed artifact hash mismatch: '+name)
        result[p]=expected
    return result


def load_batch(catalog,entry,study_ref):
    files=sealed_files(catalog.root,entry)
    directory=inside(catalog.root,entry['directory'])
    artifacts=[]
    def require(path,role):
        path=path.resolve()
        if path not in files:raise SpecError('artifact missing from sealed manifest: '+str(path))
        relative=path.relative_to(catalog.root).as_posix()
        artifacts.append(dict(path=relative,sha256=files[path],role=role))
        return relative
    require(directory/'batch.json','batch');require(directory/'resolved.yaml','benchmark_snapshot')
    batch=read(directory/'batch.json')
    snap=load_snapshot(catalog,directory/'resolved.yaml')
    embedded=embedded_catalog(catalog,snap)
    plan=embedded.get(snap['plan_ref'])
    if plan['study_ref']!=study_ref:raise SpecError('batch belongs to a different study')
    # Reject an identically named study whose actual scope changed after collection.
    if digest(embedded.get(study_ref))!=digest(catalog.get(study_ref)):raise SpecError('study differs from captured definition')
    if batch['plan_sha256']!=snap['content_sha256']:raise SpecError('batch/snapshot fingerprint mismatch')
    if batch['status'] not in {'completed','completed_with_errors','failed','stopped'}:raise SpecError('batch is not terminal')
    trials={t['id']:t for t in snap['trials']}
    seen=set();rows=[]
    for item in batch['runs']:
        trial=trials.get(item['trial_id'])
        if trial is None or item['trial_id'] in seen:raise SpecError('unknown or duplicated trial in batch')
        seen.add(item['trial_id'])
        if item['repetition']!=trial['repetition'] or item['concurrency']!=trial['concurrency']:
            raise SpecError('ledger trial settings differ from snapshot')
        if not item.get('directory'):continue
        run_dir=inside(directory,item['directory'])
        record=read(run_dir/'run.json');original=read(run_dir/'summary.json')
        scope_record=read(run_dir/'resolved.yaml')
        ids=[require(run_dir/n,n) for n in ('run.json','summary.json','resolved.yaml')]
        if record['trial_id']!=trial['id'] or record['plan_sha256']!=snap['content_sha256'] or record['status']!=item['status'] or record['repetition']!=trial['repetition']:
            raise SpecError('run/ledger/snapshot identity mismatch')
        scene,case,workload,protocol=scenario_parts(embedded,trial['scenario_ref'])
        deployment=embedded.get(trial['deployment_ref'])
        for key,expected in [('trial',trial),('deployment',deployment),('case',case),('workload',workload),('protocol',protocol)]:
            if scope_record[key]!=expected:raise SpecError('run resolved scope differs: '+key)
        manifest=record['dataset_manifest']
        fixture=directory/'datasets'/scene['id']
        ids.append(require(fixture/'manifest.json','dataset_manifest'))
        if read(fixture/'manifest.json')!=manifest:raise SpecError('dataset manifest differs from run')
        for name in ('requests.jsonl','warmup.jsonl'):
            ids.append(require(fixture/name,'dataset'))
            if file_hash(fixture/name)!=manifest['files'][name]['sha256']:raise SpecError('dataset hash mismatch')
        comparison=digest(dict(contract=trial['comparison_sha256'],dataset=manifest['files'],tokenizer=manifest['tokenizer']['sha256']))
        if record['comparison_sha256']!=comparison or original['comparison_sha256']!=comparison:raise SpecError('comparison fingerprint mismatch')
        reasons=[]
        raw=run_dir/'raw/aiperf/profile_export.jsonl'
        if raw.exists():ids.append(require(raw,'native_requests'))
        if original['raw_sha256']!=(file_hash(raw) if raw.exists() else None):raise SpecError('raw export hash mismatch')
        records,bundle=normalize(raw,manifest['files']['requests.jsonl']['session_ids'],workload['input']['tokens'],workload['output']['tokens'],record['id'],comparison)
        # Invalid/failed runs remain visible, but cannot produce causal comparisons.
        if record['status']!='completed':reasons.append('run status: '+record['status'])
        if original['evidence_kind']!='measured':reasons.append('not independently measured')
        if original['validity']!='valid' or bundle['validity']!='valid':reasons.append('invalid or incomplete measurement')
        if bundle['counts']['failed']:reasons.append('request failures present')
        for k in ('counts','statistics','rates','duration_s'):
            if not close(bundle[k],original[k]):raise SpecError('raw recomputation differs from stored '+k)
        reasons+=record['environment_issues']
        env_path=run_dir/'environment.json'
        environment={}
        if env_path.exists():
            ids.append(require(env_path,'environment'));environment=read(env_path)
        else:reasons.append('environment evidence missing')
        if environment:
            if environment.get('runtime_ref')!=deployment['runtime_ref'] or environment.get('declared_devices')!=deployment['devices']:
                reasons.append('environment runtime/device declaration differs from deployment')
            probe=environment.get('device_probe',{})
            if probe.get('status')!='observed' or probe.get('location')!='server_host':
                reasons.append('server-host device inventory is not verified')
            elif probe.get('provider')=='mx-smi':
                from benchmark.adapters.metax import binding_issues
                reasons+=binding_issues(probe,deployment['devices'],embedded.get(deployment['hardware_ref']))
            elif probe.get('provider')=='nvidia-smi':
                observed={}
                for line in probe.get('output','').splitlines():
                    columns=[s.strip() for s in line.split(',')]
                    if len(columns)>=2:observed[columns[0]]=columns[1]
                if any(observed.get(str(b['visible_index']))!=b['device_id'] for b in deployment['devices']):
                    reasons.append('NVIDIA ordinal/UUID mapping differs from deployment')
            else:reasons.append('device inventory provider has no offline verifier')
            from benchmark.adapters import for_runtime
            try:
                reasons+=for_runtime(embedded.get(deployment['runtime_ref'])).verify_server(
                    deployment,environment.get('server_info'),workload['input']['tokens']+workload['output']['tokens'])
            except SpecError as exc:reasons.append('server configuration: '+str(exc))
        if not reasons:
            rawdir=run_dir/'raw/aiperf'
            require(rawdir/'profile_export_aiperf.json','collector_aggregate')
            if plan['aiperf']['required_telemetry'] in {'server','both'}:require(rawdir/'server_metrics_export.json','server_telemetry')
            reasons+=telemetry_issues(rawdir,plan['aiperf']['required_telemetry'])
        d={k:v for k,v in deployment.items() if k not in {'id','version','title','provenance','issues','extensions'}}
        p={k:v for k,v in protocol.items() if k not in {'id','version','title','provenance','issues','extensions'}}
        w=dict(output=workload['output']['tokens'],content=workload['requests']['content'],seed=workload['requests']['seed'],
               request_count=workload['requests']['count'],generation=workload['generation'],cache=workload['cache'],
               arrival_mode=workload['arrival']['mode'],load_unit=workload['arrival']['load_unit'])
        identity=dict(deployment=d,protocol=p,workload=w,tokenizer=manifest['tokenizer']['sha256'],
                      server_info=environment.get('server_info'),client_packages=environment.get('packages'),
                      device_driver=environment.get('device_probe',{}).get('driver_version'))
        rows.append(dict(run_id=record['id'],trial_id=trial['id'],scenario=scene['id'],repetition=trial['repetition'],
            concurrency=trial['concurrency'],input_tokens=workload['input']['tokens'],output_tokens=workload['output']['tokens'],
            status=record['status'],eligible=not reasons,reasons=sorted(set(reasons)),counts=bundle['counts'],
            metrics=dict(ttft_mean_ms=bundle['statistics']['ttft']['mean'],tpot_mean_ms=bundle['statistics']['tpot']['mean'],
                e2e_mean_ms=bundle['statistics']['e2e_latency']['mean'],output_tokens_per_s=bundle['rates']['output_token_throughput']),
            grouping=dict(input_tokens=digest({**identity,'concurrency':trial['concurrency']}),
                          concurrency=digest({**identity,'input_tokens':workload['input']['tokens'],'request_set':manifest['files']['requests.jsonl']['sha256']})),
            dataset_sha256=manifest['files']['requests.jsonl']['sha256'],artifact_ids=ids,
            scope=dict(model_ref=deployment['model_ref'],hardware_ref=deployment['hardware_ref'],runtime_ref=deployment['runtime_ref'],
                       deployment_ref=trial['deployment_ref'],protocol_ref=case['protocol_ref'],case_ref=scene['case_ref'])))
    if set(trials)!=seen:raise SpecError('batch ledger does not account for every planned trial')
    return rows,artifacts,[v['document'] for v in snap['documents']]
