"""Full-context cached continuation with independent, sticky DP request slots.

The original L-token context must hit in full. The replay includes one P-produced
seed, so the wire prompt has L+1 tokens and the first D step computes one token.
This simulates a ready D context; it does not measure P-to-D transfer or claim
that cached_tokens / wire_prompt_tokens is 100%.
Shared by matrix_run and profiler diagnostics; this module has no scan entrypoint.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import random
import urllib.request

from benchmark.common.io import file_hash, json_write
from benchmark.load import dataset
from benchmark.load.metrics.normalize import metric
from tools.specs import SpecError, digest


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
    """AIPerf measures every configured turn; never silently accept a partial conversation."""
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
    """One independent prompt per concurrent slot, reused for the configured number of sequential turns."""
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


def qualification_phase(directory):
    return directory.name+'-'+digest(str(directory.resolve()))[:16]


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
    # Directory basenames such as "warmup" repeat across points. Include the
    # full attempt path so old engine observations can never match a new trial.
    phase = qualification_phase(directory)
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
