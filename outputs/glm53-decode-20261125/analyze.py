import hashlib
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
import statistics
import yaml

OUT = Path(__file__).resolve().parent
source = json.loads((OUT / 'source-snapshot.json').read_text(encoding='utf-8'))
batch = source['batches'][0]
rows, requests, audit = [], [], []


def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-6), (a, b)


def percentile(values, q):
    values = sorted(values)
    i = (len(values)-1)*q
    return values[math.floor(i)] + (values[math.ceil(i)]-values[math.floor(i)])*(i-math.floor(i))


def local_time(value):
    return datetime.fromisoformat(value).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S') if value else None


for run in batch['runs']:
    files = run['files']
    record = json.loads(files['run.json'])
    config = yaml.safe_load(files['resolved.yaml'])
    if record['status'] != 'completed':
        continue
    for name, expected in run['hashes'].items():
        assert hashlib.sha256(files[name].encode()).hexdigest() == expected
    bundle = json.loads(files['summary.json'])
    decode = json.loads(files['decode.json'])
    raw = [json.loads(line) for line in files['requests.jsonl'].splitlines() if line.strip()]
    assert bundle['raw_sha256'] == decode['source_raw_sha256'] == run['native_raw_sha256']
    assert bundle['validity'] == 'valid' and decode['eligible_for_performance_comparison']
    assert not record['environment_issues'] and not bundle['counts']['failed'] and not bundle['counts']['missing']
    c = config['trial']['concurrency']
    n = bundle['counts']['planned']
    assert n == c * 4 == len(raw) == bundle['counts']['succeeded']
    inp, out = config['workload']['input']['tokens'], config['workload']['output']['tokens']
    dep = config['deployment']['parallelism']
    label = f"TP{dep['tp']}/DP{dep['dp']}/EP{dep['ep']}"
    tpot, decode_s, ttft, e2e = [], [], [], []
    for req in raw:
        assert req['status'] == 'success' and not req['issues']
        assert req['input_tokens'] == inp and req['output_tokens'] == out
        val = (req['e2e_latency'] - req['ttft'])/(req['output_tokens']-1)
        close(val, req['tpot'])
        tpot.append(val); decode_s.append((req['e2e_latency'] - req['ttft'])/1000)
        ttft.append(req['ttft']); e2e.append(req['e2e_latency'])
        requests.append([label, inp, out, c, config['trial']['repetition'], record['id'],
                         req['id'], req['request_id'], req['status'], req['input_tokens'],
                         req['output_tokens'], req['ttft'], req['e2e_latency'], None, None])
    for key, q in [('p50', .5), ('p95', .95), ('p99', .99)]:
        close(percentile(tpot, q), decode['tpot_ms'][key])
    close(statistics.mean(tpot), decode['tpot_ms']['mean'])
    close(statistics.mean(decode_s)*1000, decode['post_first_token_ms']['mean'])
    duration = (max(x['end_ns'] for x in raw)-min(x['start_ns'] for x in raw))/1e9
    close(duration, bundle['duration_s'])
    close(sum(x['output_tokens'] for x in raw)/duration, bundle['rates']['output_token_throughput'])
    rows.append([label, inp, out, c, config['trial']['repetition'], n, bundle['counts']['succeeded'],
                 bundle['counts']['failed'], decode['tpot_ms']['mean'], decode['tpot_ms']['p50'],
                 decode['tpot_ms']['p95'], decode['tpot_ms']['p99'],
                 decode['post_first_token_ms']['mean']/1000, bundle['statistics']['ttft']['mean'],
                 bundle['statistics']['e2e_latency']['mean']/1000,
                 bundle['rates']['output_token_throughput'], duration,
                 local_time(record['created_at']), local_time(record['finished_at']), record['id']])
    audit.append(dict(run_id=record['id'], requests=n, original_raw_sha256=bundle['raw_sha256'],
                      checks='hash identity, request counts, exact lengths, TPOT mean/p50/p95/p99, decode duration and throughput'))

status_names = dict(completed='完成', failed='失败', skipped_after_failure='未执行（前序失败）', interrupted='中止')
status = []
for entry in batch['state']['runs']:
    dep = entry['deployment'].replace('glm53-vllm-decode-', '').upper().replace('-', '/')
    workload = entry['scenario'].replace('glm53-vllm-decode-', '').split('-')
    inp = int(workload[0][:-1])*1024
    reason = '预热记录未通过完整性/长度检查，未开始计分采集' if entry['status'] == 'failed' else ('失败策略 stop' if entry['status'] == 'skipped_after_failure' else '')
    status.append([dep, inp, int(workload[1]), entry['concurrency'], entry['repetition'],
                   4*entry['concurrency'], status_names.get(entry['status'], entry['status']),
                   reason, entry.get('directory') or '', entry['trial_id']])

assert len(rows) == 7 and len(requests) == 508 and len(status) == 288
meta = dict(captured_at=local_time(source['captured_at']), batch=batch['name'],
            finished_at=local_time(batch['state'].get('finished_at')), completed=len(rows), requests=len(requests),
            failed=1, skipped=280, old_batch=source['batches'][1]['name'],
            controller=source['controller'], audit=audit)
payload = dict(meta=meta, results=rows, requests=requests, status=status)
(OUT / 'tables.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'verification.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
for row in rows:
    print('C=', row[3], 'N=', row[5], 'TPOT=', round(row[8], 3), 'tokens/s=', round(row[15], 3))
print('Verified:', len(rows), 'points,', len(requests), 'requests; snapshot', meta['captured_at'])
