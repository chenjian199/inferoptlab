"""Normalize native AIPerf JSONL records; retain failed and missing requests."""
from __future__ import annotations

import json
import math
from pathlib import Path

from benchmark.io import file_hash

LATENCY = {'ttft':'time_to_first_token','e2e_latency':'request_latency'}


def number(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value>=0


def metric(metrics, name, unit):
    item=metrics.get(name)
    if not isinstance(item,dict) or not number(item.get('value')):
        return None
    value=item['value']
    if unit=='ms':
        factor={'ns':1e-6,'us':1e-3,'ms':1,'s':1000}.get(item.get('unit'))
        return value*factor if factor else None
    if item.get('unit')!=unit or value!=int(value):
        return None
    return int(value)


def statistics(values):
    values=sorted(values)
    def percentile(q):
        rank=(len(values)-1)*q
        lo=math.floor(rank)
        hi=math.ceil(rank)
        return values[lo]+(values[hi]-values[lo])*(rank-lo)
    if not values:
        return dict(count=0,**{k:None for k in ['mean','min','max','p50','p90','p95','p99']})
    return dict(count=len(values),mean=sum(values)/len(values),min=values[0],max=values[-1],
        p50=percentile(.5),p90=percentile(.9),p95=percentile(.95),p99=percentile(.99))


def normalize(path, expected_ids, input_tokens, output_tokens, run_id, comparison_sha256, evidence_kind='measured'):
    path=Path(path)
    issues=[]
    by_id={}
    request_ids=set()
    observed=0
    try:
        stream=path.open(encoding='utf-8')
    except OSError:
        stream=[]
        issues.append('per-request AIPerf export is missing')
    try:
        for index,line in enumerate(stream,1):
            if not line.strip():
                continue
            try:
                raw=json.loads(line)
                metadata=raw['metadata']
                if metadata.get('benchmark_phase')=='warmup':
                    continue
                if metadata.get('benchmark_phase')!='profiling':
                    issues.append(f'line {index}: unknown benchmark phase')
                    continue
                observed+=1
                logical=metadata.get('conversation_id')
                request_id=metadata.get('x_request_id')
                if logical not in expected_ids or metadata.get('turn_index',0)!=0:
                    issues.append(f'line {index}: unexpected logical request')
                    continue
                if logical in by_id or not request_id or request_id in request_ids:
                    issues.append(f'line {index}: duplicate/missing request identity')
                    continue
                request_ids.add(request_id)
                metrics=raw.get('metrics') or {}
                record=dict(id=logical,request_id=request_id,status='failed' if raw.get('error') or metadata.get('was_cancelled') else 'success',
                    error=raw.get('error'),start_ns=metadata.get('request_start_ns'),end_ns=metadata.get('request_end_ns'),
                    ttft=metric(metrics,'time_to_first_token','ms'),e2e_latency=metric(metrics,'request_latency','ms'),
                    input_tokens=metric(metrics,'input_sequence_length','tokens'),output_tokens=metric(metrics,'output_sequence_length','tokens'),
                    tpot=None,itl=None,issues=[])
                if record['output_tokens'] is None:
                    record['output_tokens']=metric(metrics,'output_token_count','tokens')
                if not (number(record['start_ns']) and number(record['end_ns']) and record['end_ns']>=record['start_ns']):
                    record['issues'].append('missing or invalid lifecycle timestamps')
                    record['start_ns']=record['end_ns']=None
                if record['status']=='success':
                    for name,target in [('input_tokens',input_tokens),('output_tokens',output_tokens)]:
                        if record[name]!=target:
                            record['issues'].append(f'{name}: expected {target}, observed {record[name]}')
                    if record['ttft'] is None or record['e2e_latency'] is None or record['e2e_latency']<record['ttft']:
                        record['issues'].append('missing or inconsistent latency metrics')
                    elif record['output_tokens'] is not None and record['output_tokens']>1:
                        record['tpot']=(record['e2e_latency']-record['ttft'])/(record['output_tokens']-1)
                by_id[logical]=record
                issues.extend(f'{logical}: {reason}' for reason in record['issues'])
            except (ValueError,KeyError,TypeError,AttributeError) as exc:
                issues.append(f'line {index}: malformed AIPerf record ({type(exc).__name__})')
    finally:
        if hasattr(stream,'close'):
            stream.close()
    records=[]
    for logical in expected_ids:
        records.append(by_id.get(logical,dict(id=logical,request_id=None,status='missing',error='missing record',start_ns=None,end_ns=None,
            ttft=None,e2e_latency=None,input_tokens=None,output_tokens=None,tpot=None,itl=None,issues=['missing record'])))
    missing=sum(r['status']=='missing' for r in records)
    if missing:
        issues.append(f'{missing} planned requests have no terminal record')
    succeeded=sum(r['status']=='success' for r in records)
    duration=None
    if records and all(r['start_ns'] is not None and r['end_ns'] is not None for r in records):
        span=max(r['end_ns'] for r in records)-min(r['start_ns'] for r in records)
        if span>0:
            duration=span/1e9
    if duration is None:
        issues.append('complete measurement duration unavailable; throughput/goodput not inferred from process wall time')
    stats={name:statistics([r[name] for r in records if r['status']=='success' and r[name] is not None])
           for name in ['ttft','tpot','e2e_latency','input_tokens','output_tokens']}
    rates=dict(success_rate=succeeded/len(expected_ids) if expected_ids else None,
        request_throughput=succeeded/duration if duration else None,
        input_token_throughput=sum(r['input_tokens'] or 0 for r in records if r['status']=='success')/duration if duration else None,
        output_token_throughput=sum(r['output_tokens'] or 0 for r in records if r['status']=='success')/duration if duration else None)
    # Unknown token counts must not become zero-token throughput.
    for name in ('input','output'):
        if any(r['status']=='success' and r[name+'_tokens'] is None for r in records):
            rates[name+'_token_throughput']=None
    bundle=dict(schema_version='0.2.0',kind='MeasurementBundle',run_id=run_id,comparison_sha256=comparison_sha256,
        evidence_kind=evidence_kind,validity='incomplete' if missing else 'invalid' if issues else 'valid',issues=sorted(set(issues)),
        counts=dict(planned=len(expected_ids),observed=observed,succeeded=succeeded,failed=len(expected_ids)-succeeded,missing=missing),
        duration_s=duration,statistics=stats,rates=rates,
        semantics=dict(latency_population='successful_requests',rate_window='first AIPerf request_start_ns to last request_end_ns, including recorded failures/timeouts',
            percentile_method='linear interpolation at (n-1)*q',tpot='client (request_latency - TTFT)/(actual output tokens - 1); requires single-token streaming; not a token-level ITL distribution'),
        raw_sha256=file_hash(path) if path.is_file() else None)
    return records,bundle
