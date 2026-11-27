"""Create a compact Markdown report from a hash-verified downloaded scan archive."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import tarfile


def percentile(values, quantile=0.95):
    ordered = sorted(values)
    position = (len(ordered)-1)*quantile
    low = math.floor(position)
    high = math.ceil(position)
    return ordered[low]+(ordered[high]-ordered[low])*(position-low)


def value(metrics, name, unit, field='value'):
    item = metrics[name]
    if item['unit'] != unit:
        raise ValueError(f'{name}: unexpected unit {item["unit"]}')
    result = item[field]
    if not isinstance(result, (float, int)) or not math.isfinite(result):
        raise ValueError(f'{name}: missing or invalid numeric value')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', default='r3')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    archive_bytes = (root/f'scan-{args.attempt}-metrics.tar.gz').read_bytes()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode='r:gz') as archive:
        files = {m.name: archive.extractfile(m).read() for m in archive.getmembers() if m.isfile()}
    manifest = json.loads(files['download-manifest.json'])
    for entry in manifest['files']:
        if hashlib.sha256(files[entry['path']]).hexdigest() != entry['sha256']:
            raise ValueError('snapshot hash mismatch: '+entry['path'])
    load = lambda name: json.loads(files[name])
    state, frozen = load('state.json'), load('snapshot.json')
    captured = datetime.fromtimestamp(manifest['captured_at_unix'], timezone.utc)
    stamp = captured.strftime('%Y%m%dT%H%M%SZ')
    evidence = root/'reports'
    evidence.mkdir(exist_ok=True)
    archived = evidence/f'snapshot-{stamp}.tar.gz'
    if archived.exists() and archived.read_bytes() != archive_bytes:
        raise ValueError('refusing to overwrite a different snapshot')
    archived.write_bytes(archive_bytes)
    groups = defaultdict(list)
    point_ids = set()
    for point in state['points']:
        if point['status'] != 'completed':
            continue
        if point['id'] in point_ids:
            raise ValueError('duplicate completed point: '+point['id'])
        point_ids.add(point['id'])
        rel = Path(point['directory']).relative_to(Path(manifest['remote_run'])).as_posix()
        engine, checked = load(rel+'/engine-verification.json'), load(rel+'/profile-verification.json')
        if not engine['valid'] or not checked['valid']:
            raise ValueError('completed point lacks valid evidence: '+point['id'])
        raw_name = rel+'/aiperf/profile_export.jsonl'
        if hashlib.sha256(files[raw_name]).hexdigest() != checked['raw_sha256']:
            raise ValueError('per-request data differs from validated data')
        rows = [json.loads(line) for line in files[raw_name].splitlines() if line.strip()]
        if len(rows) != point['requests'] or len(engine['requests']) != len(rows):
            raise ValueError('request count does not match recipe and engine evidence')
        for row in rows:
            metrics = row['metrics']
            if (row.get('error') or row['metadata'].get('was_cancelled')
                    or row['metadata']['benchmark_phase'] != 'profiling'
                    or value(metrics, 'input_sequence_length', 'tokens') != point['context_tokens']+1
                    or value(metrics, 'usage_prompt_cache_read_tokens', 'tokens') != point['context_tokens']
                    or value(metrics, 'output_sequence_length', 'tokens') != point['output_tokens']):
                raise ValueError('invalid cached Decode request: '+point['id'])
        summary = load(rel+'/aiperf/profile_export_aiperf.json')
        tokens = sum(value(row['metrics'], 'output_sequence_length', 'tokens') for row in rows)
        request_rate = value(summary, 'request_throughput', 'requests/sec', 'avg')
        token_rate = value(summary, 'output_token_throughput', 'tokens/sec', 'avg')
        if request_rate <= 0:
            raise ValueError('nonpositive profiling throughput')
        # AIPerf throughput uses its profiling start/end interval. Its separately
        # exported benchmark_duration uses request boundaries and is shorter.
        # Retain the native rate denominator and verify it against start/end.
        duration = len(rows)/request_rate
        wall_interval = (datetime.fromisoformat(summary['end_time'])
                         - datetime.fromisoformat(summary['start_time'])).total_seconds()
        assert math.isclose(duration, wall_interval, rel_tol=1e-7, abs_tol=2e-6)
        assert math.isclose(token_rate, tokens/duration, rel_tol=1e-7)
        for name in ('time_to_first_token', 'inter_token_latency', 'request_latency'):
            samples = [value(row['metrics'], name, 'ms') for row in rows]
            assert math.isclose(statistics.fmean(samples), value(summary, name, 'ms', 'avg'), rel_tol=1e-7)
            assert math.isclose(percentile(samples), value(summary, name, 'ms', 'p95'), rel_tol=1e-7)
        key = (point['deployment'], point['context_tokens'], point['output_tokens'], point['concurrency'])
        groups[key].append(dict(point=point, rows=rows, duration=duration, tokens=tokens,
                                request_rate=request_rate, token_rate=token_rate))

    combined = []
    for (deployment, length, output, concurrency), trials in sorted(groups.items()):
        rows = [row for trial in trials for row in trial['rows']]
        duration = sum(trial['duration'] for trial in trials)
        result = dict(deployment=deployment, input_tokens=length, output_tokens=output,
                      concurrency=concurrency, repetitions=len(trials), requests=len(rows),
                      duration_s=duration, point_ids=[t['point']['id'] for t in trials])
        for short, name in [('ttft', 'time_to_first_token'), ('tpot', 'inter_token_latency'), ('e2e', 'request_latency')]:
            samples = [value(row['metrics'], name, 'ms') for row in rows]
            result[short] = dict(mean_ms=statistics.fmean(samples), p95_ms=percentile(samples))
        result['output_throughput'] = dict(mean=sum(t['tokens'] for t in trials)/duration,
                                          p95_across_trials=percentile([t['token_rate'] for t in trials]))
        result['request_throughput'] = dict(mean=len(rows)/duration,
                                           p95_across_trials=percentile([t['request_rate'] for t in trials]))
        combined.append(result)

    counts = Counter(p['status'] for p in state['points'])
    planned = sum(len(w['arrival']['load_points'])*frozen['plan']['repetitions']
                  for w in frozen['workloads'])*len(frozen['deployments'])
    local_time = captured.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    lines = ['# GLM-5.3-Flash-W8A8 纯 Decode 测试简版', '',
             f'数据快照：**{local_time}（北京时间）**。只包含本次 cached-decode {args.attempt} 的有效性能点，扫描仍可能继续。', '',
             f'已完成 **{counts["completed"]}/{planned} 个有效测点**，合并为 **{len(combined)} 组配置、{sum(r["requests"] for r in combined)} 个请求**；'
             f'缓存验证未通过 **{counts["cache_residency_failed"]} 个测点**，未纳入性能统计。', '',
             '每个并发槽使用独立上下文；每轮请求数为并发 × 4。表中延迟为 **均值 / P95**，'
             '将同配置各轮原始请求合并计算，P95 使用线性插值。请求数是各轮合计。', '',
             '- TTFT：缓存就绪后，从请求发出至首个 D 输出 token 的时间，包含网络、排队与调度。',
             '- TPOT：每请求首个至末个输出 token 的耗时除以输出数减一；P95 是请求级 TPOT 的分位数。',
             '- E2E：本次缓存续接请求的完整客户端时延；不包含预热 Prefill，也不包含 P→D 传输。',
             '- token 吞吐量只统计 D 新生成的输出 token；两种吞吐量的均值均按总量 / 累计 AIPerf profiling 时长计算，排除预热和轮间空闲，保持 AIPerf 原生速率口径。',
             '- 吞吐量 P95 在文末单列，基于各轮整体速率，不能与请求级延迟 P95 混为同一种统计。', '',
             '有效测点要求原始上下文 L 全命中、每步 query=1、零抢占重算；HTTP 输入为 L+1，额外一个是 P 产生的 seed。', '']
    short_names = {d['id']: f'TP{d["parallelism"]["tp"]}/DP{d["parallelism"]["dp"]}/EP{d["parallelism"]["ep"]}'
                   for d in frozen['deployments']}
    for deployment in frozen['deployments']:
        dep_id = deployment['id']
        records = [r for r in combined if r['deployment'] == dep_id]
        lines += ['## '+short_names[dep_id], '']
        if not records:
            lines += ['此快照中尚无已完成的有效测点。', '']
            continue
        lines += ['| 输入 | 输出 | 并发 | 重复/请求数 | TTFT ms 均值/P95 | TPOT ms 均值/P95 | E2E s 均值/P95 | 输出 tok/s | 请求 req/s |',
                  '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for r in records:
            pair = lambda key, divisor=1: f'{r[key]["mean_ms"]/divisor:.2f} / {r[key]["p95_ms"]/divisor:.2f}'
            lines.append(f'| {r["input_tokens"]//1024}K | {r["output_tokens"]} | {r["concurrency"]} | '
                         f'{r["repetitions"]}/{r["requests"]} | {pair("ttft")} | {pair("tpot")} | '
                         f'{pair("e2e", 1000)} | {r["output_throughput"]["mean"]:.2f} | {r["request_throughput"]["mean"]:.3f} |')
        lines += ['']
    lines += ['## 缓存未通过与待测范围', '',
              '| 部署 | 输入 | 已完成全部重复的并发 | 缓存未全驻留的并发 | 待完成的并发 |',
              '|---|---|---|---|---|']
    for deployment in frozen['deployments']:
        dep_id = deployment['id']
        for length in sorted({w['input']['tokens'] for w in frozen['workloads']}):
            workloads = [w for w in frozen['workloads'] if w['input']['tokens'] == length]
            done, failed, pending = [], [], []
            for concurrency in sorted({c for w in workloads for c in w['arrival']['load_points']}):
                points = [p for p in state['points'] if p['deployment'] == dep_id and
                          p['context_tokens'] == length and p['concurrency'] == concurrency]
                required = sum(frozen['plan']['repetitions'] for w in workloads if concurrency in w['arrival']['load_points'])
                if len(points) == required and all(p['status'] == 'completed' for p in points): done.append(concurrency)
                elif len(points) == required and all(p['status'] == 'cache_residency_failed' for p in points): failed.append(concurrency)
                else: pending.append(concurrency)
            show = lambda values: '、'.join(map(str, values)) or '—'
            lines.append(f'| {short_names[dep_id]} | {length//1024}K | {show(done)} | {show(failed)} | {show(pending)} |')
    lines += ['', '缓存未通过指预热后上下文没有全部驻留；它是当前运行配置的验证结果，不等于所有 KV 配置下的硬件容量上限。', '',
              '<details>', '<summary>吞吐量均值与 P95（P95 为轮次级统计）</summary>', '',
              '每轮生成一个整体 tok/s 与 req/s；以下 P95 对同配置的这些轮次速率计算。通常只有三轮，供观察重复性。', '',
              '| 部署 | 输入/输出 | 并发 | 轮数 | 输出 tok/s 均值/P95 | 请求 req/s 均值/P95 |',
              '|---|---|---:|---:|---:|---:|']
    for r in combined:
        token, request = r['output_throughput'], r['request_throughput']
        lines.append(f'| {short_names[r["deployment"]]} | {r["input_tokens"]//1024}K/{r["output_tokens"]} | '
                     f'{r["concurrency"]} | {r["repetitions"]} | {token["mean"]:.2f} / {token["p95_across_trials"]:.2f} | '
                     f'{request["mean"]:.3f} / {request["p95_across_trials"]:.3f} |')
    lines += ['', '</details>', '',
              f'[固定原始快照](reports/{archived.name}) · [汇总数值与测点索引](quick-read.json) · [逐轮性能表](scan-{args.attempt}/README.md)', '',
              '本表为采集时快照；逐轮性能表可能随后台采集更新。汇总脚本：`summarize_scan.py`。', '']
    (root/'quick-read.md').write_text('\n'.join(lines), encoding='utf-8')
    result = dict(captured_at=captured.isoformat(), source_archive=archived.relative_to(root).as_posix(),
                  source_sha256=hashlib.sha256(archive_bytes).hexdigest(), counts=dict(counts),
                  groups=combined, planned_points=planned)
    (root/'quick-read.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(captured_at=local_time, counts=dict(counts), groups=len(combined),
                         requests=sum(r['requests'] for r in combined)), ensure_ascii=False))


if __name__ == '__main__':
    main()
