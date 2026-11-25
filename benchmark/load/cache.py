"""Owned-service cache lifecycle and per-request replay verification.

Native API: SGLang v0.5.14 POST /flush_cache (200 means successful).
vLLM v0.32 POST /reset_prefix_cache requires HTTP 200 AND success=true.
AIPerf v0.12.0 metric: usage_prompt_cache_read_tokens, unit tokens.
No mock fallback and no inference of hit ratio from TTFT or aggregate gauges.
"""
import copy
import json
import time
from urllib.request import Request, urlopen

from tools.specs import SpecError, read
from benchmark.load.adapters import aiperf
from benchmark.common.io import json_write, file_hash, utc_now
from benchmark.load.metrics.normalize import normalize, metric


def verify_reset(response):
    if response['status'] != 200 or response['endpoint'] not in {'/flush_cache', '/reset_prefix_cache'}:
        raise SpecError('cache reset did not succeed')
    if response['endpoint'] == '/reset_prefix_cache' and json.loads(response['body']).get('success') is not True:
        raise SpecError('vLLM cache reset returned success=false; outstanding cache blocks must drain')


def fill(executable, plan, deployment, workload, protocol, concurrency, fixture, run_dir, deadline, commands):
    management = deployment['serving']['management']
    if management not in {'sglang', 'vllm-docker'}:
        raise SpecError('cache reset requires an owned service')
    lifecycle = dict(status='resetting', reset_at=utc_now(), input_sha256=file_hash(fixture/'requests.jsonl'),
                     measurement_scope='cached_request_decode', strict_device_decode=False)
    json_write(run_dir/'cache-lifecycle.json', lifecycle)
    remaining=deadline-time.monotonic()
    if remaining <= 0:
        raise SpecError('deadline exhausted before cache reset')
    endpoint = '/flush_cache' if management == 'sglang' else '/reset_prefix_cache'
    request=Request(deployment['serving']['url'].rstrip('/')+endpoint,data=b'',method='POST')
    with urlopen(request,timeout=min(30,remaining)) as response:
        lifecycle['reset_response']=dict(endpoint=endpoint,status=response.status,body=response.read().decode('utf-8'))
        json_write(run_dir/'cache-lifecycle.json', lifecycle)
        verify_reset(lifecycle['reset_response'])
    lifecycle['status']='filling'
    json_write(run_dir/'cache-lifecycle.json',lifecycle)
    fill_workload=copy.deepcopy(workload)
    fill_workload['output']['tokens']=protocol['cache_replay']['fill_output_tokens']
    output=run_dir/'raw/cache-fill'
    commands['cache_fill']=aiperf.command(executable,plan,deployment,fill_workload,protocol,concurrency,fixture,output)
    json_write(run_dir/'commands.json',commands)
    remaining=deadline-time.monotonic()
    if remaining<=0:raise SpecError('deadline exhausted before cache fill')
    process=aiperf.run(commands['cache_fill'],run_dir/'logs/cache-fill.log',remaining)
    ids=[json.loads(line)['session_id'] for line in (fixture/'requests.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    _,bundle=normalize(output/'profile_export.jsonl',ids,workload['input']['tokens'],fill_workload['output']['tokens'],'cache-fill','0'*64)
    lifecycle.update(fill_process=process,fill_summary=bundle,filled_at=utc_now())
    ok=process['returncode']==0 and not process['timed_out'] and bundle['validity']=='valid' and not bundle['counts']['failed']
    lifecycle['status']='filled' if ok else 'fill_failed'
    lifecycle['fill_raw_sha256']=bundle['raw_sha256']
    json_write(run_dir/'cache-lifecycle.json',lifecycle)
    if not ok:raise SpecError('cache fill failed or input/output lengths were not verified')
    if file_hash(fixture/'requests.jsonl')!=lifecycle['input_sha256']:
        raise SpecError('cache-fill inputs changed before replay')


def assess(raw, expected_ids, workload, protocol):
    """Every scored request must have its own measured cache count."""
    result=dict(status='invalid',measurement_scope='cached_request_decode',strict_device_decode=False,
                target_hit_ratio=workload['cache']['target_hit_ratio'],
                max_uncached_tokens_per_request=protocol['cache_replay']['max_uncached_tokens_per_request'],
                requests=[],issues=[],raw_sha256=file_hash(raw) if raw.is_file() else None)
    seen=set()
    if not raw.is_file():
        result['issues'].append('cache replay export missing')
        return result
    for line in raw.read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        try:
            row=json.loads(line);meta=row['metadata']
            if meta.get('benchmark_phase')=='warmup':continue
            identity=meta.get('conversation_id')
            if meta.get('benchmark_phase')!='profiling' or identity not in expected_ids or identity in seen or meta.get('turn_index',0)!=0:
                raise ValueError('unexpected/duplicate cache replay request')
            seen.add(identity)
            values=row.get('metrics') or {}
            prompt=metric(values,'input_sequence_length','tokens')
            cached=metric(values,'usage_prompt_cache_read_tokens','tokens')
            if row.get('error') or meta.get('was_cancelled') or prompt!=workload['input']['tokens'] or cached is None or cached!=int(cached) or not 0<=cached<=prompt:
                raise ValueError('missing/invalid per-request cache usage or failed request')
            uncached=prompt-cached;ratio=cached/prompt
            result['requests'].append(dict(id=identity,prompt_tokens=prompt,cached_tokens=cached,uncached_tokens=uncached,hit_ratio=ratio))
            if ratio<result['target_hit_ratio'] or uncached>result['max_uncached_tokens_per_request']:
                result['issues'].append(identity+': cache reuse requirement not met')
        except (ValueError,KeyError,TypeError,AttributeError) as exc:
            result['issues'].append(str(exc))
    if len(result['requests'])!=len(expected_ids):result['issues'].append('not every planned request has verified cache evidence')
    if not result['issues']:result['status']='passed'
    return result


def verify_replay(run_dir, expected_ids, workload, protocol, input_sha256):
    """Recompute both fill and replay evidence, including on offline reads."""
    result=assess(run_dir/'raw/aiperf/profile_export.jsonl',expected_ids,workload,protocol)
    try:
        lifecycle=read(run_dir/'cache-lifecycle.json')
        if lifecycle.get('status')!='filled':raise SpecError('cache fill lifecycle is incomplete')
        if lifecycle['input_sha256']!=input_sha256:raise SpecError('cache fill used a different request dataset')
        verify_reset(lifecycle['reset_response'])
        process=lifecycle['fill_process']
        if process['returncode']!=0 or process['timed_out']:raise SpecError('cache fill process failed')
        _,filled=normalize(run_dir/'raw/cache-fill/profile_export.jsonl',expected_ids,workload['input']['tokens'],
                           protocol['cache_replay']['fill_output_tokens'],'cache-fill','0'*64)
        if filled!=lifecycle['fill_summary'] or filled['raw_sha256']!=lifecycle['fill_raw_sha256']:
            raise SpecError('cache fill export differs from recorded evidence')
        if filled['validity']!='valid' or filled['counts']['failed']:
            raise SpecError('cache fill request set is incomplete or invalid')
    except (SpecError,OSError,KeyError,TypeError,ValueError) as exc:
        result['issues'].append('cache lifecycle: '+str(exc))
        result['status']='invalid'
    return result
