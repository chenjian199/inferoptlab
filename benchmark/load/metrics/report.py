"""Readable reports; keep repetitions separate instead of averaging percentiles."""
import json
from pathlib import Path


def fmt(value):
    return '—' if value is None else f'{value:.3f}' if isinstance(value,(float,int)) else str(value).replace('|','\\|').replace('\n',' ')


def run_report(directory, record, bundle, sla):
    lines=['# Benchmark run', '',f'- Run: `{record["id"]}`',f'- State: `{record["status"]}`',
        f'- Evidence: `{bundle["evidence_kind"]}`; validity: `{bundle["validity"]}`',
        f'- Performance SLA: `{sla["status"]}`; correctness/quality: `{sla["quality_status"]}`',
        f'- Requests: {bundle["counts"]}',f'- Measurement duration: {fmt(bundle["duration_s"])} s','',
        '| Metric | Mean | p50 | p90 | p95 | p99 | Samples |','|---|---:|---:|---:|---:|---:|---:|']
    for name,stats in bundle['statistics'].items():
        lines.append('| '+name+' | '+' | '.join(fmt(stats[k]) for k in ['mean','p50','p90','p95','p99','count'])+' |')
    lines+=['','Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.','',
            '| Rate | Value |','|---|---:|']
    lines += ['| '+name+' | '+fmt(value)+' |' for name,value in bundle['rates'].items()]
    if sla['joint']:
        lines+=['', 'Joint request SLO: `'+json.dumps(sla['joint'],ensure_ascii=False)+'`']
    issues=list(dict.fromkeys(bundle['issues']+record.get('environment_issues',[])+sla['reasons']+([record['error']] if record.get('error') else [])))
    if issues:
        lines+=['','Observations / unresolved conditions:','']+['- '+str(x) for x in issues]
    (Path(directory)/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def batch_report(directory, ledger):
    lines=['# Benchmark comparison','','Rows are independent runs. Comparison requires identical fingerprints AND verified environments with valid data. Unverified/incomplete/failed runs remain visible and are not eligible for ranking. No best-run selection or averaging of percentiles.','',
        '| Deployment | Scenario | Concurrency | Repeat | State | TTFT p95 ms | TPOT p95 ms | Output tokens/s | SLA | Comparison |',
        '|---|---|---:|---:|---|---:|---:|---:|---|---|']
    for row in ledger:
        values=[row['deployment'],row['scenario'],row['concurrency'],row['repetition'],row['status'],None,None,None,'not_evaluated',row.get('comparison_sha256','')[:12]]
        if row.get('directory'):
            run=Path(directory)/row['directory']
            if (run/'summary.json').exists():
                summary=json.loads((run/'summary.json').read_text(encoding='utf-8'))
                values[5]=summary['statistics']['ttft']['p95']
                values[6]=summary['statistics']['tpot']['p95']
                values[7]=summary['rates']['output_token_throughput']
                values[8]=json.loads((run/'sla.json').read_text(encoding='utf-8'))['status']
        lines.append('| '+' | '.join(fmt(v) for v in values)+' |')
    lines+=['','Small exploratory request sets do not establish tail-latency confidence. Quality acceptance is a separate step.']
    (Path(directory)/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
