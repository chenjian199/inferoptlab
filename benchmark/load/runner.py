"""Sequential execution with owned deployments and immutable raw artifacts."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
import uuid
from contextlib import contextmanager
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from urllib.parse import urlparse

from tools.specs import SpecError, digest, write
from benchmark.load import dataset
from benchmark.load.adapters import aiperf, sglang
from benchmark.load.adapters import for_runtime
from benchmark.common.io import inside, json_write, jsonl_write, utc_now
from benchmark.load.planner import embedded_catalog, scenario_parts, snapshot_errors
from benchmark.load.metrics.normalize import normalize
from benchmark.load.metrics.evaluate import evaluate
from benchmark.load.metrics.report import batch_report, run_report
from benchmark.load.counts import at_point, fixture_name, fixture_source, protocol_at_point


@contextmanager
def lease(root):
    """Serialize runs in this workspace; never infer ownership from a PID alone."""
    path=root/'experiments/runs/benchmark/.execution.lock'
    path.parent.mkdir(parents=True,exist_ok=True)
    try:
        stream=path.open('x',encoding='utf-8')
    except FileExistsError as exc:
        raise SpecError(f'benchmark lease exists: {path}; inspect its owner before removing a stale lock') from exc
    token=uuid.uuid4().hex
    try:
        with stream:
            json.dump(dict(pid=os.getpid(),host=platform.node(),token=token,created_at=utc_now()),stream)
        yield
    finally:
        if path.exists() and json.loads(path.read_text(encoding='utf-8')).get('token')==token:
            path.unlink()


def environment(visibility_env='CUDA_VISIBLE_DEVICES'):
    packages={}
    for name in ('aiperf','sglang','vllm','transformers'):
        try:
            packages[name]=version(name)
        except PackageNotFoundError:
            packages[name]=None
    result=dict(collected_at=utc_now(),host=platform.node(),platform=platform.platform(),python=platform.python_version(),packages=packages)
    if visibility_env=='MACA_VISIBLE_DEVICES':
        from benchmark.load.adapters.metax import inventory
        result['device_probe']=inventory()
        return result
    if visibility_env!='CUDA_VISIBLE_DEVICES':
        result['device_probe']=dict(provider=visibility_env,status='unavailable',output=None)
        return result
    try:
        probe=subprocess.run(['nvidia-smi','--query-gpu=index,uuid,name,driver_version,memory.total','--format=csv,noheader'],
            capture_output=True,text=True,timeout=10,check=False,**({'creationflags':subprocess.CREATE_NO_WINDOW} if os.name=='nt' else {}))
        result['device_probe']=dict(provider='nvidia-smi',status='observed' if probe.returncode==0 else 'failed',output=probe.stdout,stderr=probe.stderr)
    except (OSError,subprocess.TimeoutExpired):
        result['device_probe']=dict(provider='nvidia-smi',status='unavailable',output=None)
    return result


def execute(catalog, snapshot, output_root, qualification=None):
    output_root=Path(output_root).resolve()
    if not output_root.is_relative_to((catalog.root/'experiments').resolve()):
        raise SpecError('benchmark output must be inside experiments/ so records remain portable')
    errors=catalog.structural_errors(snapshot) or snapshot_errors(catalog,snapshot,verify_sources=snapshot.get('state')=='frozen')
    if errors:
        raise SpecError('\n'.join(errors))
    catalog=embedded_catalog(catalog,snapshot)
    plan=catalog.get(snapshot['plan_ref'])
    if snapshot['execution_issues']:
        raise SpecError('execution blocked:\n'+'\n'.join(snapshot['execution_issues']))
    if plan['mode']=='formal' and snapshot['state']!='frozen':
        raise SpecError('formal execution requires a frozen ResolvedBenchmark')
    receipt = None
    if plan.get('qualification_required'):
        if qualification is None:
            raise SpecError('this plan requires --qualification before execution')
        from benchmark.load.qualification import verify_receipt
        receipt = verify_receipt(catalog,snapshot,qualification)
    executable=aiperf.check_installation(plan['aiperf']['version'])
    if os.name!='posix':
        raise SpecError('live benchmark execution requires Linux; prepare/plan/analyze/report are portable')
    with lease(catalog.root):
        return _execute(catalog,snapshot,plan,executable,Path(output_root),receipt)


def _execute(catalog,snapshot,plan,executable,output_root,qualification=None):
    batch_id='batch-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8]
    directory=output_root.resolve()/batch_id
    directory.mkdir(parents=True,exist_ok=False)
    write(directory/'resolved.yaml',snapshot)
    if qualification is not None:
        json_write(directory/'qualification.json',qualification)
    deadline=time.monotonic()+plan['budget']['max_wall_seconds']
    study=catalog.get(plan['study_ref'])
    allocated=catalog.get(study['hardware_ref'])['resources']['allocated_devices']
    device_hours=study['budget']['max_device_hours']
    if device_hours is not None:
        if not allocated:
            raise SpecError('device-hour budget requires a concrete allocated-device count')
        deadline=min(deadline,time.monotonic()+3600*device_hours/allocated)
    ledger=[]
    state=dict(id=batch_id,status='preparing',created_at=utc_now(),plan_sha256=snapshot['content_sha256'],runs=ledger)
    json_write(directory/'batch.json',state)
    active=None
    active_id=None
    active_command=None
    manifests={}
    try:
        # Copy once; every subsequent run uses the archived fixture, not the mutable source.
        for reference in plan['scenario_refs']:
            scene,case,workload,protocol=scenario_parts(catalog,reference)
            points=workload['arrival']['load_points'] if workload['requests'].get('count_multiplier') is not None else [workload['arrival']['load_points'][0]]
            for concurrency in points:
                name=fixture_name(scene,workload,concurrency)
                target=directory/'datasets'/name
                shutil.copytree(inside(catalog.root,fixture_source(scene,workload,concurrency)),target)
                for deployment_ref in plan['deployment_refs']:
                    deployment=catalog.get(deployment_ref)
                    manifest=dataset.verify(at_point(workload,concurrency),protocol_at_point(protocol,concurrency),deployment['serving']['tokenizer_path'],target)
                    manifests[name]=manifest
        state['status']='running'
        for trial in snapshot['trials']:
            deployment=catalog.get(trial['deployment_ref'])
            scene,case,workload,protocol=scenario_parts(catalog,trial['scenario_ref'])
            fixture_id=fixture_name(scene,workload,trial['concurrency'])
            workload=at_point(workload,trial['concurrency'])
            protocol=protocol_at_point(protocol,trial['concurrency'])
            entry=dict(trial_id=trial['id'],deployment=deployment['id'],scenario=scene['id'],concurrency=trial['concurrency'],repetition=trial['repetition'],status='pending',directory=None)
            ledger.append(entry)
            if time.monotonic()>=deadline or state['status']=='stopped':
                entry['status']='skipped_budget' if state['status']!='stopped' else 'skipped_after_failure'
                continue
            run_id='run-'+uuid.uuid4().hex[:16]
            run_dir=directory/run_id
            run_dir.mkdir()
            (run_dir/'logs').mkdir()
            entry['directory']=run_id
            fixture=directory/'datasets'/fixture_id
            manifest=manifests[fixture_id]
            comparison=digest(dict(contract=trial['comparison_sha256'],dataset=manifest['files'],tokenizer=manifest['tokenizer']['sha256']))
            entry['comparison_sha256']=comparison
            record=dict(id=run_id,trial_id=trial['id'],repetition=trial['repetition'],attempt=1,status='starting',created_at=utc_now(),
                plan_sha256=snapshot['content_sha256'],comparison_sha256=comparison,dataset_manifest=manifest,environment_issues=[],error=None)
            write(run_dir/'resolved.yaml',dict(snapshot_sha256=snapshot['content_sha256'],trial=trial,deployment=deployment,
                case=case,workload=workload,protocol=protocol,dataset_manifest=manifest,batch_snapshot='../resolved.yaml'))
            commands={}
            run_deadline=min(deadline,time.monotonic()+plan['budget']['run_timeout_s'])
            raw=run_dir/'raw/aiperf'
            raw.mkdir(parents=True)
            process_result=None
            interrupted=False
            try:
                if active_id!=deployment['id']:
                    if active:
                        active.close()
                    adapter=for_runtime(catalog.get(deployment['runtime_ref']))
                    active=adapter.Deployment(deployment,catalog.get(deployment['runtime_ref']),run_dir/'logs/server.log')
                    active_id=None
                    active_command=active.launch()
                    active_id=deployment['id']
                commands['server']=active_command
                json_write(run_dir/'commands.json',commands)
                serving=deployment['serving']
                sglang.wait_ready(serving,min(run_deadline,time.monotonic()+serving['startup_timeout_s']),active.process)
                sglang.smoke(serving,timeout=max(.01,min(30,run_deadline-time.monotonic())))
                info,issues=adapter.inspect_server(serving)
                issues+=adapter.verify_server(deployment,info,workload['input']['tokens']+workload['output']['tokens'])
                env=environment(serving['device_visibility_env'])
                env.update(server_info=info,declared_devices=deployment['devices'],runtime_ref=deployment['runtime_ref'])
                local_server=urlparse(serving['url']).hostname in {'localhost','127.0.0.1','::1'}
                env['device_probe']['location']='server_host' if local_server else 'client_host'
                if not local_server:
                    issues.append('remote serving device inventory is not verified by the local client probe')
                if not deployment['devices']:
                    issues.append('physical device allocation is not bound/verified')
                if env['device_probe']['status']!='observed':
                    issues.append('device inventory/driver probe unavailable; platform adapter evidence is missing')
                elif deployment['devices'] and env['device_probe']['provider']=='mx-smi':
                    from benchmark.load.adapters.metax import binding_issues
                    issues+=binding_issues(env['device_probe'],deployment['devices'],catalog.get(deployment['hardware_ref']))
                elif deployment['devices']:
                    observed={}
                    for line in env['device_probe'].get('output','').splitlines():
                        columns=[s.strip() for s in line.split(',')]
                        if len(columns)>=2:
                            observed[columns[0]]=columns[1]
                    for binding in deployment['devices']:
                        if observed.get(str(binding['visible_index']))!=binding['device_id']:
                            issues.append(f'device index/UUID mapping is unverified: rank {binding["rank"]}')
                record['environment_issues']=sorted(set(issues))
                json_write(run_dir/'environment.json',env)
                if plan['mode']=='formal' and issues:
                    raise SpecError('formal environment verification failed: '+'; '.join(issues))
                if protocol['method']=='prefix_reuse_decode' and issues:
                    raise SpecError('cache replay requires verified service configuration and device bindings: '+'; '.join(issues))
                # Verify archived hashes again immediately before sending any workload.
                dataset.verify(workload,protocol,serving['tokenizer_path'],fixture,retokenize=False)
                if protocol['execution']['warmup_request_count']:
                    commands['warmup']=aiperf.command(executable,plan,deployment,workload,protocol,trial['concurrency'],fixture,run_dir/'raw/warmup',warmup=True)
                    json_write(run_dir/'commands.json',commands)
                    warm=aiperf.run(commands['warmup'],run_dir/'logs/warmup.log',max(.01,run_deadline-time.monotonic()))
                    if warm['returncode']!=0 or warm['timed_out']:
                        raise SpecError('warmup failed or exceeded deadline')
                    _,warm_bundle=normalize(run_dir/'raw/warmup/profile_export.jsonl',manifest['files']['warmup.jsonl']['session_ids'],
                        workload['input']['tokens'],workload['output']['tokens'],run_id+'-warmup',comparison)
                    if warm_bundle['validity']!='valid' or warm_bundle['counts']['failed']:
                        raise SpecError('warmup records failed completeness/length checks')
                if protocol['method']=='prefix_reuse_decode':
                    from benchmark.load.cache import fill
                    fill(executable,plan,deployment,workload,protocol,trial['concurrency'],fixture,run_dir,run_deadline,commands)
                if time.monotonic()>=run_deadline:
                    raise SpecError('run budget exhausted before profiling')
                commands['aiperf']=aiperf.command(executable,plan,deployment,workload,protocol,trial['concurrency'],fixture,raw)
                json_write(run_dir/'commands.json',commands)
                record['status']='profiling'
                json_write(run_dir/'run.json',record)
                process_result=aiperf.run(commands['aiperf'],run_dir/'logs/aiperf.log',run_deadline-time.monotonic())
                if process_result['timed_out'] or process_result['returncode']!=0:
                    raise SpecError('AIPerf failed or exceeded run deadline; partial exports are retained')
                record['status']='completed'
            except KeyboardInterrupt:
                interrupted=True
                record.update(status='interrupted',error='interrupted by user')
                state['status']='stopped'
            except (SpecError,OSError,ValueError,KeyError,subprocess.SubprocessError) as exc:
                record.update(status='failed',error=str(exc))
                if active:
                    active.close()
                    active=None
                    active_id=None
            finally:
                record.update(finished_at=utc_now(),process=process_result)
                records,bundle=normalize(raw/'profile_export.jsonl',manifest['files']['requests.jsonl']['session_ids'],
                    workload['input']['tokens'],workload['output']['tokens'],run_id,comparison)
                collection_issues=aiperf.telemetry_issues(raw,plan['aiperf']['required_telemetry'])
                if protocol['method']=='prefix_reuse_decode':
                    from benchmark.load.cache import verify_replay
                    cache_result=verify_replay(run_dir,manifest['files']['requests.jsonl']['session_ids'],workload,protocol,manifest['files']['requests.jsonl']['sha256'])
                    bundle['cache_replay']=cache_result
                    json_write(run_dir/'cache-replay.json',cache_result)
                    collection_issues+=cache_result['issues']
                if record['status']!='completed':
                    collection_issues.append(record['error'] or 'execution did not complete')
                if collection_issues:
                    bundle['issues']+=collection_issues
                    bundle['validity']='incomplete'
                if record['status']=='completed' and bundle['validity']!='valid':
                    record['status']='invalid'
                if record['status']=='completed' and bundle['counts']['failed']:
                    record['status']='completed_with_errors'
                if record['status']=='completed' and record['environment_issues']:
                    record['status']='unverified'
                sla=catalog.get(case['sla_ref']) if case['sla_ref'] else None
                hardware=catalog.get(deployment['hardware_ref'])
                verdict=evaluate(sla,bundle,records,hardware['resources']['allocated_devices'],record['environment_issues'])
                jsonl_write(run_dir/'requests.jsonl',records)
                json_write(run_dir/'summary.json',bundle)
                json_write(run_dir/'sla.json',verdict)
                json_write(run_dir/'run.json',record)
                run_report(run_dir,record,bundle,verdict)
                entry['status']=record['status']
                if record['status']!='completed' and plan['failure_policy']=='stop':
                    state['status']='stopped'
                json_write(directory/'batch.json',state)
                batch_report(directory,ledger)
            if interrupted:
                # Remaining planned trials are recorded as skipped on the next iterations.
                continue
        state['status']='completed' if all(e['status']=='completed' for e in ledger) else 'completed_with_errors'
    except BaseException as exc:
        state.update(status='failed',error=str(exc))
        raise
    finally:
        if active:
            active.close()
        state['finished_at']=utc_now()
        json_write(directory/'batch.json',state)
        batch_report(directory,ledger)
    from tools.experiments import register_batch, index
    register_batch(catalog,directory)
    index(catalog)
    return directory,state
