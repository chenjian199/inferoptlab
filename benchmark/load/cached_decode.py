"""Full-context cached continuation with independent, sticky DP request slots.

The original L-token context must hit in full. The replay includes one P-produced
seed, so the wire prompt has L+1 tokens and the first D step computes one token.
This simulates a ready D context; it does not measure P-to-D transfer or claim
that cached_tokens / wire_prompt_tokens is 100%.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import urllib.request

from benchmark.common.io import file_hash, json_write, utc_now
from benchmark.load import dataset
from benchmark.load.adapters import aiperf, sglang, vllm
from benchmark.load.runner import lease
from benchmark.load.metrics.normalize import metric
from tools.specs import Catalog, SpecError, digest, read


def payload(model, ids, output, identity, stream=False):
    result = dict(model=model, prompt=ids, max_tokens=output, min_tokens=output,
        ignore_eos=True, temperature=0, return_token_ids=True, request_id=identity,
        stream=stream)
    if stream:
        result['stream_options'] = dict(include_usage=True)
    return result


def api(url, endpoint, body=None, rank=0, timeout=900):
    request = urllib.request.Request(url.rstrip('/')+endpoint,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type': 'application/json', 'X-data-parallel-rank': str(rank)})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        value = response.read()
        return json.loads(value) if value else None


def cache_evidence(response, context, output):
    usage = response.get('usage') or {}
    cached = (usage.get('prompt_tokens_details') or {}).get('cached_tokens')
    result = dict(context_tokens=context, wire_prompt_tokens=usage.get('prompt_tokens'),
        cached_context_tokens=cached, output_tokens=usage.get('completion_tokens'))
    result['valid'] = (type(cached) is int and cached == context
        and usage.get('prompt_tokens') == context+1 and usage.get('completion_tokens') == output)
    result['original_context_hit_ratio'] = cached/context if type(cached) is int else None
    result['wire_prompt_hit_ratio'] = cached/(context+1) if type(cached) is int else None
    return result


def scheduler_evidence(rows, expected, context, output):
    matched = {}
    issues = []
    for row in rows:
        identities = [identity for identity in expected if identity in row['request_id']]
        if not identities:
            continue
        if len(identities) != 1 or identities[0] in matched:
            issues.append('ambiguous or duplicate scheduler observation')
            continue
        identity = identities[0]
        matched[identity] = row
        if (row['dp_rank'] != expected[identity] or row['prompt_tokens'] != context+1
                or row['first_computed_tokens'] != context or row['first_query_tokens'] != 1
                or row['max_query_tokens'] != 1 or row['preemptions'] != 0
                or row['output_tokens'] != output or row['scheduled_tokens'] != output
                or row['steps'] != output):
            issues.append(identity+': routing/cache/query length/output count requirement failed')
    missing = sorted(set(expected)-set(matched))
    if missing:
        issues.append(f'{len(missing)} requests missing engine evidence')
    return dict(valid=not issues, issues=issues, requests=matched)


def observations(directory, kind):
    return [json.loads(line) for path in sorted(Path(directory).glob(kind+'-*.jsonl'))
        for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def make_fixture(slots, output, multiplier, model, point):
    sessions, expected = [], {}
    for slot, item in enumerate(slots):
        turns = []
        for turn in range(multiplier):
            identity = f'cachedD-{point}-s{slot:03d}-t{turn:02d}-end'
            request = payload(model, item['ids'], output, identity, stream=True)
            request['_inferoptlab_dp_rank'] = item['rank']
            turns.append(request)
            expected[identity] = item['rank']
        sessions.append(dict(session_id=f'{point}-s{slot:03d}', payloads=turns))
    return dict(data=sessions), expected


def profile_command(executable, serving, fixture, artifact, concurrency, count, timeout):
    return [executable, 'profile', '--model', serving['served_model'],
        '--tokenizer', serving['tokenizer_path'], '--url', serving['url'],
        '--endpoint-type', 'completions', '--endpoint', '/v1/completions', '--streaming',
        '--input-file', str(fixture), '--custom-dataset-type', 'inputs_json',
        '--dataset-sampling-strategy', 'sequential', '--no-allow-dataset-wrap',
        '--request-count', str(count), '--concurrency', str(concurrency),
        '--request-timeout-seconds', str(timeout), '--artifact-dir', str(artifact),
        '--ui-type', 'none', '--export-level', 'raw', '--use-server-token-count',
        '--server-metrics', serving['url'].rstrip('/')+'/metrics']


def validate_profile(artifact, expected, slots, context, output):
    """AIPerf measures all four turns; never silently accept a partial conversation."""
    path = artifact/'profile_export.jsonl'
    if not path.is_file():
        return dict(valid=False,issues=['AIPerf per-request export is missing'],count=0,requests=[])
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    planned = set()
    for identity in expected:
        session, turn = identity.removeprefix('cachedD-').removesuffix('-end').rsplit('-t',1)
        planned.add((session,int(turn)))
    values, seen, issues = [], set(), []
    for row in rows:
        meta, metrics = row['metadata'], row.get('metrics') or {}
        identity = (meta.get('conversation_id'), meta.get('turn_index'))
        if identity in seen or row.get('error') or meta.get('was_cancelled'):
            issues.append('duplicate/failed/cancelled AIPerf request')
        seen.add(identity)
        if (meta.get('benchmark_phase') != 'profiling'
                or metric(metrics,'input_sequence_length','tokens') != context+1
                or metric(metrics,'output_sequence_length','tokens') != output
                or metric(metrics,'usage_prompt_cache_read_tokens','tokens') != context):
            issues.append('AIPerf token counts/cache counts do not match protocol')
        values.append(dict(identity=identity, metrics=metrics))
    if len(rows) != len(expected) or len(seen) != len(expected):
        issues.append('request count differs from concurrency times multiplier')
    if seen != planned:
        issues.append('AIPerf session/turn identities differ from the frozen request set')
    return dict(valid=not issues, issues=issues, count=len(rows), raw_sha256=file_hash(path), requests=values)


def prepare_slots(tokenizer, serving, length, concurrency, dp, seed, directory, timeout):
    """One independent prompt per concurrent slot, reused for four sequential turns."""
    rng = random.Random(seed)
    slots = []
    for slot in range(concurrency):
        text = dataset.prompt(tokenizer, rng, length)
        ids = tokenizer.apply_chat_template([dict(role='user', content=text)], tokenize=True,
            add_generation_prompt=True, return_dict=True)['input_ids']
        assert len(ids) == length
        slots.append(dict(slot=slot, rank=slot % dp, context_ids=ids))
    assert len({digest(s['context_ids']) for s in slots}) == concurrency
    json_write(directory/'contexts.json', slots)
    reset = api(serving['url'], '/reset_prefix_cache', {})
    if reset.get('success') is not True:
        raise SpecError('cache reset did not succeed')
    json_write(directory/'reset.json', reset)
    # Keep preparation free of scored requests. Seed generation and a second
    # boundary-fill request are necessary for the hybrid KDA cache checkpoint.
    for item in slots:
        rank, slot = item['rank'], item['slot']
        first = api(serving['url'], '/v1/completions', payload(serving['served_model'],
            item['context_ids'], 1, f'fill-seed-{directory.name}-{slot}'), rank, timeout)
        token_ids = first['choices'][0]['token_ids']
        if len(token_ids) != 1 or first['usage']['prompt_tokens'] != length:
            raise SpecError('seed generation has incorrect lengths')
        item['ids'] = item['context_ids']+token_ids
        second = api(serving['url'], '/v1/completions', payload(serving['served_model'],
            item['ids'], 1, f'fill-boundary-{directory.name}-{slot}'), rank, timeout)
        json_write(directory/f'fill-{slot:03d}.json', dict(seed=first, boundary=second))
    json_write(directory/'slots.json', slots)
    return slots


def qualify_slots(slots, serving, length, observations_dir, directory, timeout, output=2):
    # Detect eviction with one request at a time before allowing a whole batch
    # to fall back to Prefill. This bounds the cost of an over-capacity group.
    residency=[]
    for item in slots:
        response=api(serving['url'],'/v1/completions',payload(serving['served_model'],
            item['ids'],1,f'audit-{directory.name}-s{item["slot"]:03d}'),item['rank'],timeout)
        json_write(directory/f'residency-{item["slot"]:03d}.json',response)
        residency.append(cache_evidence(response,length,1))
        if not residency[-1]['valid']:
            result=dict(valid=False,cache=residency,engine=dict(valid=False,issues=['resident context was evicted before concurrent replay'],requests={}),
                attention_valid=False,attention=[])
            json_write(directory/'qualification.json',result)
            return result
    marker = observations_dir/'qualification-active.txt'
    phase = directory.name
    marker.write_text(phase)
    expected = {}
    def one(item):
        identity = f'qualifyD-{phase}-s{item["slot"]:03d}-end'
        expected[identity] = item['rank']
        response = api(serving['url'], '/v1/completions',
            payload(serving['served_model'], item['ids'], output, identity), item['rank'], timeout)
        json_write(directory/f'replay-{item["slot"]:03d}.json', response)
        return cache_evidence(response, length, output)
    try:
        with ThreadPoolExecutor(max_workers=len(slots)) as pool:
            caches = list(pool.map(one, slots))
    finally:
        marker.unlink(missing_ok=True)
    engine = scheduler_evidence(observations(observations_dir, 'scheduler'), expected, length, output)
    attention = [r for r in observations(observations_dir, 'attention') if r['phase'] == phase]
    builders = {r['builder'] for r in attention}
    attention_ok = ('GDNAttentionMetadataBuilder' in builders
        and 'FlashMLASparseMetadataBuilder' in builders
        and all(r['num_prefills'] == 0 and r['num_prefill_tokens'] == 0 for r in attention))
    result = dict(valid=all(r['valid'] for r in caches) and engine['valid'] and attention_ok,
        cache=caches, engine=engine, attention_valid=attention_ok, attention=attention)
    json_write(directory/'qualification.json', result)
    return result


def run(catalog, plan, directory, only_qualify=False):
    errors = catalog.structural_errors(plan) or catalog.semantic_errors(plan)
    if errors:
        raise SpecError('\n'.join(errors))
    deployments = [catalog.get(r) for r in plan['deployment_refs']]
    workloads = [catalog.get(r) for r in plan['workload_refs']]
    for workload in workloads:
        if workload['requests']['content'] != 'random_independent':
            raise SpecError('this protocol requires independent slot contexts')
        if workload['requests'].get('count_multiplier') != plan['request_multiplier']:
            raise SpecError('plan request multiplier differs from workload')
        if workload['cache']['reset_between_runs']:
            raise SpecError('cached continuation retains contexts across group trials; reset_between_runs must be false')
    for deployment in deployments:
        if not deployment['prefix_cache']:
            raise SpecError('cached Decode requires prefix caching')
    directory = Path(directory).resolve()
    if not directory.is_relative_to((catalog.root/'experiments').resolve()):
        raise SpecError('outputs must be under experiments/')
    directory.mkdir(parents=True, exist_ok=True)
    frozen = dict(plan=plan, deployments=deployments, workloads=workloads,
        runtimes=[catalog.get(d['runtime_ref']) for d in deployments])
    snapshot = directory/'snapshot.json'
    if snapshot.exists() and read(snapshot) != frozen:
        raise SpecError('resume snapshot differs from the current recipes')
    json_write(snapshot, frozen)
    code_files = [Path(__file__), catalog.root/'benchmark/load/aiperf_hooks/sitecustomize.py',
        catalog.root/'benchmark/load/adapters/vllm.py',catalog.root/'tools/deployment/metax-vllm/observers/sitecustomize.py']
    json_write(directory/('code-'+str(time.time_ns())+'.json'),
        {p.relative_to(catalog.root).as_posix():file_hash(p) for p in code_files})
    state_path = directory/'state.json'
    state = read(state_path) if state_path.exists() else dict(created_at=utc_now(), points=[])
    executable = aiperf.check_installation()
    hooks = catalog.root/'tools/deployment/metax-vllm/observers'
    lengths = sorted({w['input']['tokens'] for w in workloads})
    with lease(catalog.root):
        for deployment in deployments:
            dep_id = deployment['id']
            dep_dir = directory/dep_id
            dep_dir.mkdir(exist_ok=True)
            server_dir=dep_dir/('server-'+str(time.time_ns()));server_dir.mkdir()
            obs = server_dir/'observations'
            runtime = catalog.get(deployment['runtime_ref'])
            server = vllm.Deployment(deployment, runtime, server_dir/'server.log',
                observation=dict(hooks=hooks, records=obs))
            state.update(status='starting', deployment=dep_id, server_attempt=str(server_dir),updated_at=utc_now())
            json_write(state_path, state)
            try:
                command = server.launch()
                json_write(server_dir/'launch.json', dict(command=command, container_id=server.container_id))
                serving = deployment['serving']
                sglang.wait_ready(serving, time.monotonic()+serving['startup_timeout_s'], server)
                info = api(serving['url'], '/server_info?config_format=json')
                json_write(server_dir/'server-info.json', info)
                issues = vllm.verify_server(deployment,info,max(lengths)+1+max(w['output']['tokens'] for w in workloads))
                if issues:
                    raise SpecError('live deployment differs from recipe: '+str(issues))
                attention=json.loads(runtime['launch_parameters'].get('--attention-config','{}'))
                actual_attention=info['vllm_config']['attention_config']
                if any(actual_attention.get(k)!=v for k,v in attention.items()):
                    raise SpecError('live attention configuration differs from RuntimeSpec')
                tokenizer = dataset.load_tokenizer(serving['tokenizer_path'])
                json_write(dep_dir/'tokenizer.json', dataset.tokenizer_fingerprint(serving['tokenizer_path']))
                state.update(status='qualifying_routes',updated_at=utc_now())
                json_write(state_path,state)
                route_dir=dep_dir/('routes-'+str(time.time_ns()));route_dir.mkdir()
                route_slots=prepare_slots(tokenizer,serving,min(lengths),deployment['parallelism']['dp'],
                    deployment['parallelism']['dp'],plan['seed'],route_dir,plan['request_timeout_s'])
                route_proof=qualify_slots(route_slots,serving,min(lengths),obs,route_dir,plan['request_timeout_s'])
                if not route_proof['valid']:
                    raise SpecError('all DP ranks must pass cached one-token Decode qualification before scoring')
                for length in lengths:
                    length_workloads = [w for w in workloads if w['input']['tokens'] == length]
                    concurrency_points = sorted({c for w in length_workloads for c in w['arrival']['load_points']})
                    for concurrency in concurrency_points:
                        group_name = f'l{length}-c{concurrency}'
                        planned = [dict(id=f'{dep_id}-l{length}-o{w["output"]["tokens"]}-c{concurrency}-r{r}',
                            deployment=dep_id,context_tokens=length,output_tokens=w['output']['tokens'],
                            concurrency=concurrency,repetition=r,requests=concurrency*plan['request_multiplier'])
                            for w in length_workloads if concurrency in w['arrival']['load_points']
                            for r in range(1,plan['repetitions']+1)]
                        finished={p.get('id') for p in state['points'] if p['status'] in {'completed','cache_residency_failed'}}
                        if not only_qualify and all(p['id'] in finished for p in planned):
                            continue
                        attempt = dep_dir/(group_name+'-'+str(time.time_ns()))
                        attempt.mkdir()
                        state.update(status='preparing', group=group_name, updated_at=utc_now())
                        json_write(state_path, state)
                        slots = prepare_slots(tokenizer, serving, length, concurrency,
                            deployment['parallelism']['dp'], plan['seed'], attempt, plan['request_timeout_s'])
                        qualification = qualify_slots(slots, serving, length, obs, attempt,
                            plan['request_timeout_s'])
                        if not qualification['valid']:
                            status='cache_residency_failed' if not all(r['valid'] for r in qualification['cache']) else 'decode_path_qualification_failed'
                            for point in planned:
                                if point['id'] not in finished:
                                    state['points'].append(dict(**point,status=status,directory=str(attempt),
                                        note='No performance point accepted; inspect cache, route and attention evidence.'))
                            json_write(state_path, state)
                            report(directory)
                            if status=='decode_path_qualification_failed':
                                raise SpecError('one-token cached replay did not qualify as device Decode')
                            continue
                        if only_qualify:
                            continue
                        for workload in length_workloads:
                            if concurrency not in workload['arrival']['load_points']:
                                continue
                            output = workload['output']['tokens']
                            for repetition in range(1, plan['repetitions']+1):
                                point = f'{dep_id}-l{length}-o{output}-c{concurrency}-r{repetition}'
                                if any(p.get('id') == point and p['status'] == 'completed' for p in state['points']):
                                    continue
                                point_dir = attempt/f'o{output}-r{repetition}'
                                point_dir.mkdir()
                                json_write(point_dir/'server.json',dict(server_attempt=str(server_dir),container_id=server.container_id))
                                fixture, expected = make_fixture(slots, output, plan['request_multiplier'],
                                    serving['served_model'], point+'-a'+digest(str(attempt))[:8])
                                json_write(point_dir/'inputs.json', fixture)
                                json_write(point_dir/'expected.json', expected)
                                cmd = profile_command(executable, serving, point_dir/'inputs.json',
                                    point_dir/'aiperf', concurrency, concurrency*plan['request_multiplier'], plan['request_timeout_s'])
                                env = os.environ.copy()
                                env['PYTHONPATH'] = str(catalog.root/'benchmark/load/aiperf_hooks')+os.pathsep+str(catalog.root)
                                env['AIPERF_DATASET_MMAP_CACHE_ENABLED']='false'
                                json_write(point_dir/'command.json', dict(argv=cmd, pythonpath=env['PYTHONPATH'],
                                    AIPERF_DATASET_MMAP_CACHE_ENABLED='false'))
                                state.update(status='scoring', point=point, updated_at=utc_now())
                                json_write(state_path, state)
                                with (point_dir/'aiperf.log').open('w') as log:
                                    process = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT,
                                        env=env, timeout=plan['point_timeout_s'])
                                engine = scheduler_evidence(observations(obs, 'scheduler'), expected, length, output)
                                json_write(point_dir/'engine-verification.json', engine)
                                profile = validate_profile(point_dir/'aiperf', expected, slots, length, output)
                                json_write(point_dir/'profile-verification.json', profile)
                                valid = process.returncode == 0 and engine['valid'] and profile['valid']
                                state['points'].append(dict(id=point, deployment=dep_id, context_tokens=length,
                                    output_tokens=output, concurrency=concurrency, repetition=repetition,
                                    requests=concurrency*plan['request_multiplier'], directory=str(point_dir),
                                    status='completed' if valid else 'invalid', finished_at=utc_now()))
                                json_write(state_path, state)
                                report(directory)
                                if not valid:
                                    raise SpecError(f'{point}: invalid performance/cache evidence')
            finally:
                server.close()
        state.update(status='finished_with_exclusions' if any(p['status']!='completed' for p in state['points']) else 'completed', updated_at=utc_now())
        json_write(state_path, state)
        report(directory)
    return state


def report(directory):
    directory=Path(directory)
    state=read(directory/'state.json')
    lines=['# Cached Decode 扫描','',f"更新时间：{utc_now()}；状态：{state['status']}",'',
        '每槽独立上下文；原始上下文 L 全部命中，线上的请求为 L+1（额外一个 P 端生成的 seed）。',
        '输出是 D 端新生成的 token，seed 不计入输出。未测量 P→D 传输；客户端时延包含调度、排队及流式传输。','',
        '| 部署 | 上下文 | 输出 | 并发 | 重复 | 请求数 | TPOT均值 ms | p50 | p95 | p99 | 首D token ms | 输出 tokens/s |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for point in state['points']:
        if point['status']!='completed':continue
        raw=Path(point['directory'])/'aiperf/profile_export_aiperf.json'
        if not raw.is_file():continue
        data=read(raw)
        tpot=data.get('inter_token_latency',{})
        values=[point['deployment'],point['context_tokens'],point['output_tokens'],point['concurrency'],point['repetition'],point['requests'],
            *[tpot.get(k) for k in ['avg','p50','p95','p99']],data.get('time_to_first_token',{}).get('avg'),
            data.get('output_token_throughput',{}).get('avg')]
        lines.append('| '+' | '.join(f'{v:.3f}' if isinstance(v,float) else str(v) for v in values)+' |')
    lines+=['','## 未纳入有效性能结果的测点','']
    for point in state['points']:
        if point['status']!='completed':
            lines.append(f"- {point.get('deployment')} / {point.get('id',point.get('group'))}: {point['status']}；证据 `{point['directory']}`")
    (directory/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--qualify-only', action='store_true')
    args = parser.parse_args()
    catalog = Catalog(args.root); catalog.load()
    try:
        run(catalog, read(args.plan), args.out, args.qualify_only)
    except Exception as exc:
        state_path=args.out/'state.json'
        if state_path.is_file():
            state=read(state_path);state.update(status='failed',error=repr(exc),updated_at=utc_now())
            json_write(state_path,state);report(args.out)
        raise


if __name__ == '__main__':
    main()
