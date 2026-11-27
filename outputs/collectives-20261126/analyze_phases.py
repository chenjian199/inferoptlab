"""Source-based traffic model joined to the frozen 91-point observation.

Logical sent bytes are analytical; this is deliberately not a hardware counter.
The estimate covers 42 MoE dispatch/combine pairs and 45 attention SP pairs.
"""
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
SNAPSHOT = ROOT / 'outputs/glm53-short-output-20261126'
manifest = json.loads((SNAPSHOT / 'markdown-source.json').read_text(encoding='utf-8'))
environment = json.loads((OUT / 'environment-verification.json').read_text(encoding='utf-8'))
config = environment['model_config']['text_config']
assert config['hidden_size'] == 4096 and config['num_hidden_layers'] == 45
assert config['first_k_dense_replace'] == 3 and config['num_experts_per_tok'] == 8
assert config['mhc'] is True and config['dtype'] == 'bfloat16'
assert environment['model_config_sha256'] == '671a1dec45411c0d126573646ec7173aa1b4fd02aaaab62be8613b9c08e3018e'


def read_archive(ref):
    payload = (ROOT / ref['path']).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == ref['sha256']
    return json.loads(gzip.decompress(payload))


core = read_archive(manifest['core'])
extra = read_archive(manifest['details'])
assert extra['source_sha256'] == manifest['core']['sha256']


def union_seconds(intervals):
    intervals = sorted(intervals)
    start, end = intervals[0]
    total = 0
    for left, right in intervals[1:]:
        if left > end:
            total += end - start
            start, end = left, right
        else:
            end = max(end, right)
    return (total + end - start) / 1e9


def histogram(metrics, name):
    series = metrics[name]['series']
    count = sum(s['stats'].get('count', 0) for s in series)
    total = sum(s['stats'].get('sum', 0) for s in series)
    return {'count': count, 'sum': total, 'mean': total / count if count else None}


rows = []
for entry in core['runs']:
    ledger = entry['ledger_entry']
    if ledger['status'] != 'completed':
        continue
    files = entry['files']
    for item in files.values():
        assert hashlib.sha256(item['text'].encode()).hexdigest() == item['sha256']
    summary = json.loads(files['summary.json']['text'])
    run = json.loads(files['run.json']['text'])
    decode = json.loads(files['decode.json']['text'])
    requests = [json.loads(line) for line in files['requests.jsonl']['text'].splitlines()]
    tp = 4 if 'tp4-dp2' in ledger['deployment'] else 2
    assert 'tp4-dp2' in ledger['deployment'] or 'tp2-dp4' in ledger['deployment']
    n = 4 * ledger['concurrency']
    assert len(requests) == n == summary['counts']['succeeded']
    assert all(r['status'] == 'success' for r in requests)
    input_tokens = run['dataset_manifest']['input_tokens']
    output_tokens = run['dataset_manifest']['output_tokens']
    assert all(r['input_tokens'] == input_tokens and r['output_tokens'] == output_tokens for r in requests)
    prefill, post_first = [], []
    for r in requests:
        first = r['start_ns'] + round(r['ttft'] * 1e6)
        assert r['start_ns'] < first < r['end_ns']
        prefill.append((r['start_ns'], first))
        post_first.append((first, r['end_ns']))
    windows = {'client_prefill_including_queue': union_seconds(prefill),
               'client_post_first_token': union_seconds(post_first)}
    # Sum logical outbound bytes over the eight GPUs; do not double count receive.
    # 42 MoE layers: INT8 hidden + FP32 weights/INT32 ids + FP32 scale, BF16 output.
    moe_bytes = 42 * (8 - 1) * (4096 + 8 * 4 + 8 * 4 + 4 + 4096 * 2)
    # 45 attention layers: BF16 all-gather then BF16 reduce-scatter in each TP group.
    attention_bytes = 45 * 2 * (tp - 1) * 4096 * 2
    per_token = moe_bytes + attention_bytes
    item = extra['files'][ledger['directory'] + '/raw/aiperf/server_metrics_export.json']
    assert hashlib.sha256(item['text'].encode()).hexdigest() == item['sha256']
    metrics = json.loads(item['text'])['metrics']
    server = {name: histogram(metrics, 'vllm:' + name) for name in [
        'request_prefill_time_seconds', 'request_decode_time_seconds',
        'request_prefill_kv_computed_tokens', 'request_num_preemptions']}
    row = dict(ledger, tp=tp, dp=8 // tp, input_tokens=input_tokens,
               output_tokens=output_tokens, requests=n,
               core_logical_bytes_per_unpadded_token=per_token,
               moe_bytes_per_unpadded_token=moe_bytes,
               attention_bytes_per_unpadded_token=attention_bytes,
               client_phase_union_seconds=windows, server=server,
               server_request_count_matches=all(v['count'] == n for v in server.values()),
               ttft_mean_s=summary['statistics']['ttft']['mean'] / 1000,
               tpot_mean_ms=decode['tpot_ms']['mean'],
               post_first_mean_s=decode['post_first_token_ms']['mean'] / 1000,
               tpot_p95_ms=decode['tpot_ms']['p95'],
               measured_window_s=summary['duration_s'],
               output_tokens_per_s=summary['rates']['output_token_throughput'])
    for phase, tokens, window in [
        ('prefill', n * input_tokens, windows['client_prefill_including_queue']),
        ('decode', n * (output_tokens - 1), windows['client_post_first_token'])]:
        volume = tokens * per_token
        row[phase] = dict(valid_token_count=tokens, core_logical_bytes_estimated=volume,
                          equivalent_aggregate_GBps=volume / window / 1e9,
                          estimated_bytes_not_counter=True)
    rows.append(row)

rows.sort(key=lambda r: (-r['tp'], r['input_tokens'], r['output_tokens'], r['concurrency']))
assert len(rows) == 91
assert all(r['server_request_count_matches'] for r in rows)
assert all(r['server']['request_num_preemptions']['sum'] == 0 for r in rows)
assert all(r['server']['request_prefill_kv_computed_tokens']['sum'] == r['requests'] * r['input_tokens'] for r in rows)
payload = dict(source=manifest, model_config_sha256=environment['model_config_sha256'], model=dict(hidden_size=4096, layers=45, moe_layers=42,
    expert_parallel=8, top_k=8, dispatch_activation_dtype='int8', combine_dtype='bfloat16',
    evidence='pinned-image source-derived, not an execution trace',
    excluded=['padding', 'idle DP dummy tokens', 'recomputation', 'embedding/logits',
              'final hidden gather', 'control messages', 'packet headers', 'multi-hop traffic']),
    rows=rows)
(OUT / 'phase-estimates.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')


def table(headers, values):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, row)) + ' |' for row in values])


lines = ['# Prefill / Decode 传输量推算与已测耗时', '',
    '**91 个历史有效测点；通信量按固定镜像源码推算，带宽为阶段有效带宽估计，不是网卡或互联链路计数器实测。**', '',
    '[返回通信对比](README.md) · [原始性能简版](../glm53-short-output-20261126/markdown/quick-read.md) · [逐点计算数据](phase-estimates.json)', '',
    '## 计算范围与公式', '',
    '当前两种配方均为 `allgather_reducescatter`、EP 开启、TP>1、DP>1。固定版本的 `use_sequence_parallel_moe` 因而为真：MoE 走 EP8，Attention 的 SP 通信走各自 TP4 或 TP2 组。此处不能把 MoE 简化成 DP2/DP4 通信。', '',
    '模型有 45 层、42 个 MoE 层、hidden_size=4096、top-k=8。按无 LoRA 的 INT8 Triton 路径，MoE dispatch 先量化为 INT8；combine 为 BF16。每 token 的 dispatch 为 4096 B 激活 + 32 B 路由权重 + 32 B expert id + 4 B scale = 4164 B；combine 为 8192 B。', '',
    '统计口径是 **8 卡合计逻辑发送量**，接收不再重复相加。均衡 ring 等价模型下：', '',
    '```text',
    'MoE / token = 42 × (8−1) × (4164+8192) = 3,632,664 B',
    'Attention SP / token = 45 × 2 × (TP−1) × 8192 B',
    'TP4 核心通信 / token = 5,844,504 B',
    'TP2 核心通信 / token = 4,369,944 B',
    'Prefill = 请求数 × 实际输入 tokens × 每 token 核心通信量',
    'Decode = 请求数 × (实际输出 tokens−1) × 每 token 核心通信量',
    '阶段有效带宽 = 估计通信量 / 对应客户端阶段时间区间的并集长度',
    '```', '',
    '这是主要数据路径的理想无 padding 估计，未覆盖完整实际流量。不能用模型权重大小乘输出 token 数替代卡间通信量：权重读取主要是显存流量。上下文从 4K 增至 64K 会增加 Prefill token 总数，但 Decode 每步传送的 hidden-state 宽度仍为 4096；历史 KV 也不会因此每步完整广播一次。', '',
    '## 每个请求的核心通信量', '',
    table(['输入 / 输出', 'TP4 Prefill (GB)', 'TP4 Decode (GB)', 'TP2 Prefill (GB)', 'TP2 Decode (GB)', 'Prefill / Decode 量比'], [
        [f'{inp//1024}K / {out}', f'{inp*5844504/1e9:.3f}', f'{(out-1)*5844504/1e9:.3f}',
         f'{inp*4369944/1e9:.3f}', f'{(out-1)*4369944/1e9:.3f}', f'{inp/(out-1):.1f}×']
        for inp in [4096,16384,65536] for out in [20,50]]), '',
    '## 91 个有效点', '',
    'P/D 流量为该测点全部计分请求的 8 卡合计估计值，单位十进制 GB。P/D GB/s 分母分别使用 `请求发出→首 token` 和 `首 token→结束` 的时间区间并集，不将重叠请求时间相加。P 包含排队、传输和调度；D 可能受同时进行的 Prefill 干扰。两个阶段的时间并集可能重叠，不能相加作为总时长。', '',
    table(['部署 TP/DP/EP', '输入/输出', 'C', '请求数', 'TTFT 均值(s)', 'TPOT 均值/P95(ms)',
           'P 估计(GB)', 'D 估计(GB)', 'P 有效(GB/s)', 'D 有效(GB/s)'], [
        [f'{r["tp"]}/{r["dp"]}/8', f'{r["input_tokens"]//1024}K/{r["output_tokens"]}', r['concurrency'], r['requests'],
         f'{r["ttft_mean_s"]:.3f}', f'{r["tpot_mean_ms"]:.2f}/{r["tpot_p95_ms"]:.2f}',
         f'{r["prefill"]["core_logical_bytes_estimated"]/1e9:.3f}', f'{r["decode"]["core_logical_bytes_estimated"]/1e9:.3f}',
         f'{r["prefill"]["equivalent_aggregate_GBps"]:.3f}', f'{r["decode"]["equivalent_aggregate_GBps"]:.4f}'] for r in rows]), '',
    '## 为什么还不能称为模型实际链路带宽', '',
    '- 旧数据没有记录每次 collective 的 tensor shape、dtype、分组、调用时长和链路计数器，无法事后恢复精确实测流量。',
    '- SP 按 TP 对 token 补齐，DP 空闲 rank 还可能运行 dummy token。低并发时这些开销不可忽略；本表未计入。模型最终 hidden gather、embedding/logits、调度元数据、重计算等也未计入。',
    '- 各 rank token 数不相等时，当前 vLLM 的 all_gatherv 使用分组 Broadcast，reduce_scatterv 使用分组 Reduce；它们与均衡 AG/RS microbenchmark 的通信算法不同。',
    '- 阶段耗时包含计算、显存访问、调度及同步，不等于 collective 独占耗时。阶段有效 GB/s 不能直接除以 microbenchmark busbw 当作链路利用率。',
    '- A2A microbenchmark 使用均匀等分消息，没有 expert 路由、top-k 复制、按目的 rank 合并或负载不均，不能代替 DeepEP 等 MoE 通信实现。', '',
    '如需真正的模型通信带宽，下一次只需做两种部署各一次短采样：在 Prefill/Decode 调用边界记录实际 token 数与 padding、每次 collective 的分组/shape/dtype、设备事件耗时，并同步采集互联计数器。流量与耗时必须来自同一测量范围。', '',
    '服务端 Prefill/Decode histogram 的计数、总和、加权均值另存于 JSON；如果采样边界导致服务端请求数与客户端不一致，会保留 `server_request_count_matches=false`，不用于本表分母。', '']
(OUT / 'phase-analysis.md').write_text('\n'.join(lines), encoding='utf-8')
print(json.dumps(dict(points=len(rows), server_count_mismatches=sum(not r['server_request_count_matches'] for r in rows),
                     bytes_per_token={'tp4':5844504,'tp2':4369944},
                     phase_bandwidth_ranges={phase:[min(r[phase]['equivalent_aggregate_GBps'] for r in rows),
                         max(r[phase]['equivalent_aggregate_GBps'] for r in rows)] for phase in ['prefill','decode']})))
