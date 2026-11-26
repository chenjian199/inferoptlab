"""Request-level latency after first token, explicitly excluding isolated-device claims."""
from benchmark.common.io import json_write
from benchmark.load.metrics.normalize import statistics


def report(directory, records, bundle, environment_issues):
    samples = []
    for row in records:
        if row['status'] != 'success' or row.get('issues'):
            continue
        first, total, count = row['ttft'], row['e2e_latency'], row['output_tokens']
        if first is None or total is None or count is None or count < 2 or total < first:
            continue
        samples.append(dict(request_id=row['id'], post_first_token_ms=total - first,
                            tpot_ms=(total - first) / (count - 1), output_tokens=count))
    eligible = bundle['validity'] == 'valid' and not environment_issues and not bundle['counts']['failed']
    value = dict(scope='client_post_first_token_full_request', strict_device_decode=False,
                 includes_prefill_in_duration=False, concurrent_prefill_interference_possible=True,
                 source_raw_sha256=bundle['raw_sha256'], eligible_for_performance_comparison=eligible,
                 acceptance_passed=False, counts=bundle['counts'], samples=samples,
                 post_first_token_ms=statistics([s['post_first_token_ms'] for s in samples]),
                 tpot_ms=statistics([s['tpot_ms'] for s in samples]),
                 semantics='Per request: request_latency minus TTFT; TPOT divides by actual output tokens minus one. '
                           'Includes client/stream transport overhead and potential scheduling interference. '
                           'Full-window output throughput is not isolated Decode throughput.')
    json_write(directory / 'decode.json', value)
    def cell(x):
        return '—' if x is None else f'{x:.3f}'
    lines = ['# 首 token 之后的解码指标', '',
             '正常执行 Prefill；仅将本请求 TTFT 从延迟中扣除。并发请求的 Prefill 仍可能干扰 Decode，不能称为设备纯 Decode。', '',
             '| 指标（ms） | mean | p50 | p95 | p99 | 样本数 |', '|---|---:|---:|---:|---:|---:|']
    for label, key in [('TPOT', 'tpot_ms'), ('首 token 后耗时', 'post_first_token_ms')]:
        stats = value[key]
        lines.append('| ' + label + ' | ' + ' | '.join(cell(stats[k]) for k in ['mean', 'p50', 'p95', 'p99', 'count']) + ' |')
    lines += ['', '失败与缺失请求仍保留在总请求分母；分位数只使用有效成功请求。',
              f'数据可用于性能比较：{eligible}；精度/发布验收：未由本报告判定。']
    (directory / 'decode.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return value
