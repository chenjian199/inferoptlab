"""Profile cached Decode with native vLLM torch.profiler and a clean control run.

Reuses DeploymentSpec, WorkloadSpec, DecodeProfilePlan and cached-decode evidence.
Profiler latency is diagnostic and never substitutes for the unprofiled control.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

from benchmark.common.io import file_hash, json_write, utc_now
from benchmark.load import decode_protocol as cd, dataset
from benchmark.load.adapters import aiperf, sglang, vllm
from benchmark.load.runner import lease
from tools.specs import Catalog, SpecError, read


def profile_api(url, endpoint, body=None):
    request = urllib.request.Request(url.rstrip('/')+endpoint,
        data=json.dumps(body or {}).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request, timeout=900) as response:
        return dict(status=response.status, body=response.read().decode(errors='replace'))


def capture_trial(catalog, serving, slots, workload, plan, directory, observations, executable, identity):
    directory.mkdir()
    output, length = workload['output']['tokens'], workload['input']['tokens']
    fixture, expected = cd.make_fixture(slots, output, plan['request_multiplier'], serving['served_model'], identity)
    json_write(directory/'inputs.json', fixture)
    json_write(directory/'expected.json', expected)
    count = len(slots)*plan['request_multiplier']
    command = cd.profile_command(executable, serving, directory/'inputs.json', directory/'aiperf', len(slots), count, plan['request_timeout_s'])
    env = os.environ.copy()
    env['PYTHONPATH'] = str(catalog.root/'benchmark/load/aiperf_hooks')+os.pathsep+str(catalog.root)
    env['AIPERF_DATASET_MMAP_CACHE_ENABLED'] = 'false'
    json_write(directory/'command.json',dict(argv=command,started_at=utc_now()))
    with (directory/'aiperf.log').open('w',encoding='utf-8') as log:
        process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
            env=env, timeout=plan['point_timeout_s'])
    engine = cd.scheduler_evidence(cd.observations(observations,'scheduler'),expected,length,output)
    profile = cd.validate_profile(directory/'aiperf',expected,slots,length,output)
    json_write(directory/'engine-verification.json',engine)
    json_write(directory/'profile-verification.json',profile)
    if process.returncode or not engine['valid'] or not profile['valid']:
        raise SpecError(f'{identity}: request/cache/Decode evidence failed')
    return dict(directory=str(directory),valid=True,requests=count,finished_at=utc_now(),
                metrics=read(directory/'aiperf/profile_export_aiperf.json'))


def run(catalog, plan, directory, delay, iterations):
    errors=catalog.structural_errors(plan) or catalog.semantic_errors(plan)
    if errors:raise SpecError(str(errors))
    if len(plan['deployment_refs'])!=1 or plan['repetitions']!=1:
        raise SpecError('profiling requires one deployment and one paired trial per workload')
    deployment=catalog.get(plan['deployment_refs'][0]); runtime=catalog.get(deployment['runtime_ref'])
    workloads=[catalog.get(ref) for ref in plan['workload_refs']]
    if deployment['backend_options'].get('--enforce-eager') is not False:
        raise SpecError('this profile plan must explicitly request graph mode')
    for workload in workloads:
        if (len(workload['arrival']['load_points'])!=1 or workload['requests']['content']!='random_independent'
            or workload['requests'].get('count_multiplier')!=plan['request_multiplier'] or workload['cache']['reset_between_runs']):
            raise SpecError('one concurrency with independent retained contexts and matching multiplier required')
    profiler=json.loads(deployment['backend_options']['--profiler-config'])
    if profiler.get('profiler')!='torch' or profiler.get('torch_profiler_dir')!='/inferoptlab-observations/profiles':
        raise SpecError('torch profiler must write into the mounted observations/profiles directory')
    directory=Path(directory).resolve()
    if not directory.is_relative_to((catalog.root/'experiments').resolve()):
        raise SpecError('profile output must be under experiments/')
    directory.mkdir(parents=True,exist_ok=True)
    if (directory/'state.json').exists():raise SpecError('use a new output directory; profile windows are immutable')
    json_write(directory/'snapshot.json',dict(plan=plan,deployment=deployment,runtime=runtime,workloads=workloads,
        profiling=dict(delay_iterations=delay,max_iterations=iterations,control='same requests with profiler inactive')))
    json_write(directory/'code.json',{p.relative_to(catalog.root).as_posix():file_hash(p) for p in [
        Path(__file__),catalog.root/'benchmark/load/decode_protocol.py',
        catalog.root/'benchmark/load/aiperf_hooks/sitecustomize.py',
        catalog.root/'tools/deployment/metax-vllm/observers/sitecustomize.py']})
    state=dict(status='starting',started_at=utc_now(),points=[])
    def save(**updates):
        state.update(**updates,updated_at=utc_now());json_write(directory/'state.json',state)
        print(json.dumps({k:v for k,v in state.items() if k!='points'},ensure_ascii=False),flush=True)
    observations=directory/'server/observations';observations.mkdir(parents=True)
    server=vllm.Deployment(deployment,runtime,directory/'server/server.log',
        observation=dict(hooks=catalog.root/'tools/deployment/metax-vllm/observers',records=observations))
    save()
    with lease(catalog.root):
        try:
            command=server.launch();json_write(directory/'server/launch.json',dict(command=command,container_id=server.container_id))
            serving=deployment['serving']
            sglang.wait_ready(serving,time.monotonic()+serving['startup_timeout_s'],server)
            info=cd.api(serving['url'],'/server_info?config_format=json');json_write(directory/'server/server-info.json',info)
            issues=vllm.verify_server(deployment,info,max(w['input']['tokens']+1+w['output']['tokens'] for w in workloads))
            if issues:raise SpecError(str(issues))
            attention=json.loads(runtime['launch_parameters'].get('--attention-config','{}'))
            if any(info['vllm_config']['attention_config'].get(k)!=v for k,v in attention.items()):
                raise SpecError('live attention configuration differs from runtime')
            actual=info['vllm_config']['profiler_config']
            if any(actual.get(k)!=v for k,v in profiler.items()):raise SpecError('profiler config differs from recipe')
            tokenizer=dataset.load_tokenizer(serving['tokenizer_path']);executable=aiperf.check_installation()
            for workload in workloads:
                length=workload['input']['tokens']; concurrency=workload['arrival']['load_points'][0]
                name=f'l{length}-o{workload["output"]["tokens"]}-c{concurrency}'
                point=directory/name;point.mkdir()
                save(status='preparing',scenario=name)
                slots=cd.prepare_slots(tokenizer,serving,length,concurrency,deployment['parallelism']['dp'],plan['seed'],point,plan['request_timeout_s'])
                qualified=cd.qualify_slots(slots,serving,length,observations,point,plan['request_timeout_s'])
                if not qualified['valid']:
                    state['points'].append(dict(scenario=name,status='qualification_failed',directory=str(point)))
                    save(status='qualification_failed');continue
                save(status='control',scenario=name)
                control=capture_trial(catalog,serving,slots,workload,plan,point/'control',observations,executable,name+'-control')
                # Recheck residency after the control before enabling instrumentation.
                check=point/(name+'-before-profile');check.mkdir()
                qualified=cd.qualify_slots(slots,serving,length,observations,check,plan['request_timeout_s'])
                if not qualified['valid']:raise SpecError('cached contexts no longer qualify before profiling')
                save(status='profiling',scenario=name)
                trace_dir=observations/'profiles';before=set(trace_dir.glob('*'))
                json_write(point/'start-profile.json',profile_api(serving['url'],'/start_profile',
                    dict(profile_prefix=name,delay_iterations=delay,max_iterations=iterations)))
                try:
                    sampled=capture_trial(catalog,serving,slots,workload,plan,point/'profiled',observations,executable,name+'-profiled')
                finally:
                    json_write(point/'stop-profile.json',profile_api(serving['url'],'/stop_profile'))
                traces=[p for p in sorted(set(trace_dir.glob('*'))-before) if p.name.endswith(('.pt.trace.json.gz','.pt.trace.json'))]
                json_write(point/'traces.json',[dict(path=str(p),bytes=p.stat().st_size,sha256=file_hash(p)) for p in traces])
                expected_ranks=len(deployment['devices'])
                if len(traces)!=expected_ranks:raise SpecError(f'expected {expected_ranks} worker traces, found {len(traces)}')
                state['points'].append(dict(scenario=name,status='completed',directory=str(point),traces=len(traces),control=control,profiled=sampled))
                save(status='scenario_completed')
            save(status='completed' if all(p['status']=='completed' for p in state['points']) else 'finished_with_exclusions')
        except Exception as exc:
            save(status='failed',error=repr(exc));raise
        finally:
            server.close()
    return state


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan',type=Path)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--delay-iterations',type=int,default=8)
    parser.add_argument('--profile-iterations',type=int,default=32)
    args=parser.parse_args()
    if args.delay_iterations<0 or args.profile_iterations<1:parser.error('invalid profiling iteration limits')
    catalog=Catalog(args.root);catalog.load()
    run(catalog,read(args.plan),args.out,args.delay_iterations,args.profile_iterations)


if __name__=='__main__':main()
