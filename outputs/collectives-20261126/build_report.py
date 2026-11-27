"""Verify completed microbenchmarks and render a reproducible Markdown report."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
state = json.loads((OUT / 'raw/bandwidth-state.json').read_text())
assert state['status'] == 'completed', 'Wait for all bounded jobs to complete'
assert len(state['jobs']) == 36
rows = []
hashes = {}
for job in state['jobs']:
    assert job['status'] == 'completed' and job['points'] == 16
    p = OUT / 'raw' / (job['id'] + '.jsonl')
    hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    assert hashes[p.name] == job['sha256']
    records = [json.loads(line) for line in p.read_text().splitlines()]
    assert [r['size_bytes'] for r in records] == state['sizes']
    for r in records:
        assert r['correctness'] == 'passed' and r['physical_devices'] == ','.join(map(str, job['devices']))
        assert r['world_size'] == len(job['devices']) and r['operation'] == job['operation']
        assert len(r['samples_ms']) == len(r['rank_samples_ms']) == 5
        for sample, ranks in zip(r['samples_ms'], r['rank_samples_ms']):
            assert len(ranks) == r['world_size'] and sample == max(ranks)
            assert all(math.isfinite(x) and x > 0 for x in ranks)
        median = statistics.median(r['samples_ms'])
        factor = (r['world_size'] - 1) / r['world_size']
        calls = 2 if r['operation'] in ['all_reduce', 'all_gather_reduce_scatter', 'all_to_all_roundtrip'] else 1
        assert math.isclose(median, r['median_ms'])
        assert math.isclose(r['size_bytes'] * factor * calls / (median * 1e6), r['bus_GBps'])
        assert math.isclose(r['size_bytes'] / (median * 1e6), r['algorithm_GBps'])
        rows.append(r)
assert len(rows) == 576
lookup = {(r['physical_devices'], r['operation'], r['size_bytes']): r for r in rows}
phase = json.loads((OUT / 'phase-estimates.json').read_text(encoding='utf-8'))


def at(g, op, size):
    return lookup[(g, op, size)]


def table(headers, values):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(str, row)) + ' |' for row in values])


groups = [('0,1,2,3,4,5,6,7', '全部 8 卡 / EP8'), ('0,1,2,3', '0–3，MX 组 / TP4'),
          ('4,5,6,7', '4–7，MX 组 / TP4'), ('0,1', '0、1，MX 组 / TP2'),
          ('0,4', '0、4，跨组 NODE'), ('0,2,4,6', '0、2、4、6，跨组 4 卡')]
ops = [('all_to_all', 'All-to-All'), ('all_gather', 'All-Gather'),
       ('reduce_scatter', 'Reduce-Scatter'), ('all_reduce', 'All-Reduce'),
       ('all_to_all_roundtrip', '两次 All-to-All'), ('all_gather_reduce_scatter', 'All-Gather + Reduce-Scatter')]
size = 256 * 1024**2
g8 = groups[0][0]
a2a = at(g8, 'all_to_all_roundtrip', size)
agrs = at(g8, 'all_gather_reduce_scatter', size)
ratio = a2a['median_ms'] / agrs['median_ms']
tiny = at(g8, 'all_to_all_roundtrip', 8192)['median_ms'] / at(g8, 'all_gather_reduce_scatter', 8192)['median_ms']
lines = ['# C500 通信带宽与 GLM-5.3 阶段传输量', '',
    '**原模型扫描已停止；通信 microbenchmark 已完成 36 个任务、576 个测点，全部数值正确性检查通过。**', '',
    '[逐消息大小完整结果](bandwidth-details.md) · [91 点阶段传输量推算](phase-analysis.md) · [机器可读计算结果](phase-estimates.json) · [原始通信记录](raw/bandwidth-state.json)', '',
    '## 先看结论', '',
    f'- 全部 8 卡、相同 `S=256 MiB` 时，两次 All-to-All 为 **{a2a["median_ms"]:.3f} ms / {a2a["bus_GBps"]:.2f} GB/s**，All-Gather＋Reduce-Scatter 为 **{agrs["median_ms"]:.3f} ms / {agrs["bus_GBps"]:.2f} GB/s**，后者耗时约为前者的 **1/{ratio:.2f}**。这是相同 S 的通信原语对比，不是模型加速比。',
    f'- 差异随消息大小变化：8 KiB 时，上述耗时比只有 **{tiny:.2f}×**。Decode 的小消息不能套用大消息峰值带宽。',
    '- 当前两种部署都使用 AG＋RS；这批 91 点不是 A2A 与 AG＋RS 的模型 A/B 测试。源码确认二者 MoE 均走 EP8，Attention 分别走 TP4、TP2。',
    '- 理想无 padding 的主要通信量：TP4 约 **5.845 MB/token**，TP2 约 **4.370 MB/token**，TP4 多 **33.7%**；MoE 部分相同，差别来自 Attention 的 TP 通信。均为 8 卡合计逻辑发送量。',
    '- 历史数据推算的阶段有效带宽：Prefill **15.56–59.23 GB/s**，Decode **0.014–0.563 GB/s**，均为 8 卡合计估计值。Decode 的字节量少但耗时长，不能仅凭这一差距判定链路带宽不足；还要区分消息延迟、计算/显存访问、padding 和调度等待。', '',
    '## 实测条件与计时口径', '',
    '- 主机：`metax-60 / gpu-node-060`，8×C500 64 GiB。`mx-smi topo -m` 显示 0–3 为 MX 组、4–7 为 MX 组，跨组为 NODE；NODE 表示经过同 NUMA 内的 PCIe/主机桥路径。',
    '- 使用与模型相同的固定镜像 `sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b`，PyTorch `2.10.0+metax3.9.0.8`。通过 PyTorch distributed 的 `nccl` 后端调用沐曦通信实现；未运行 NVIDIA GPU/NCCL 性能程序。',
    '- 每种原语：BF16，消息 8 KiB 到 256 MiB、按 2 倍递增；预热 10 次，每个样本连续 20 次操作，采 5 个样本。每个样本取最慢 rank 的同步主机耗时，表格用 5 个样本的中位数。包含 Python 调用开销，非纯 kernel 时间。',
    '- 所有组顺序执行，各组的测试不同时争用互联；不代表模型中多个 TP 组并发时的带宽。每点先验证非零输入的结果，随后测量；All-Reduce 计时重复用零输入，避免累加溢出。',
    '- `S`：AG 的总输出/RS 的总输入字节数；A2A、All-Reduce 为每 rank 完整数组字节数。AG 输入为 S/N，RS 输出为 S/N；A2A 每 rank 输入与输出均为 S。两种组合的输入语义不同。',
    '- `algbw=S/t`；AG、RS、A2A 的 `busbw=algbw×(N−1)/N`；All-Reduce 及这里的两次调用组合再乘 2。该值是归一化逻辑带宽，不是每根 PCIe/MX 链路的实测计数；不能把全部 8 卡 AG 的 busbw 当作一根跨组链路速率。公式沿用 [NCCL-tests 带宽定义](https://raw.githubusercontent.com/NVIDIA/nccl-tests/master/doc/PERFORMANCE.md)。', '',
    '## 256 MiB 下各分组对比', '',
    '以下均为归一化 busbw，单位十进制 GB/s；两次 A2A 与 AG＋RS 同样计入两次通信量。', '',
    table(['GPU 组', 'A2A', 'AG', 'RS', 'All-Reduce', '两次 A2A', 'AG＋RS'], [
        [label] + [f'{at(g, op, size)["bus_GBps"]:.2f}' for op, _ in ops] for g, label in groups]), '',
    '## EP8：从 Decode 小消息到 Prefill 大消息', '',
    table(['S', '两次 A2A(ms)', 'AG＋RS(ms)', '两次 A2A(GB/s)', 'AG＋RS(GB/s)', '耗时比 A2A/AGRS'], [
        [f'{s/1024:g} KiB' if s < 1024**2 else f'{s/1024**2:g} MiB',
         f'{at(g8,"all_to_all_roundtrip",s)["median_ms"]:.4f}',
         f'{at(g8,"all_gather_reduce_scatter",s)["median_ms"]:.4f}',
         f'{at(g8,"all_to_all_roundtrip",s)["bus_GBps"]:.2f}',
         f'{at(g8,"all_gather_reduce_scatter",s)["bus_GBps"]:.2f}',
         f'{at(g8,"all_to_all_roundtrip",s)["median_ms"]/at(g8,"all_gather_reduce_scatter",s)["median_ms"]:.2f}×']
        for s in [8192,65536,1048576,33554432,67108864,268435456]]), '',
    'Decode 假设一次调度有 C 个有效 token，则 EP8 的 INT8 dispatch 激活总量约 C×4096 B，BF16 combine 总量约 C×8192 B，另有路由元数据和 padding。C=1–128 对应约 4 KiB–512 KiB / 8 KiB–1 MiB，属于小消息区。最低 4 KiB 的 dispatch 小于本次 8 KiB 起点，没有对它外推带宽。', '',
    'Prefill 的 4096 是每个 DP 引擎的 batch token 上限；TP4/DP2 全忙时最多约 8192 token/步，MoE dispatch/combine 激活约 32/64 MiB；TP2/DP4 全忙时最多约 16384 token/步，对应 64/128 MiB。64K 输入会拆成多个 chunk，不能把 64K×并发都当作一次消息。实际每步 token 数旧数据未记录。', '',
    '## 与已有模型耗时对照', '',
    '下面使用 20-token 输出的代表点。通信量按同一源码模型推算；阶段带宽用客户端区间并集。完整 91 点及服务端阶段均值见详细文件。', '',
    table(['TP/DP/EP', '输入', 'C', 'TTFT均值(s)', '首token后均值(s)', 'P有效GB/s(估)', 'D有效GB/s(估)'], [
        [f'{r["tp"]}/{r["dp"]}/8', f'{r["input_tokens"]//1024}K', r['concurrency'],
         f'{r["ttft_mean_s"]:.3f}', f'{r["post_first_mean_s"]:.3f}',
         f'{r["prefill"]["equivalent_aggregate_GBps"]:.3f}', f'{r["decode"]["equivalent_aggregate_GBps"]:.4f}']
        for r in phase['rows'] if r['input_tokens'] in [4096,65536] and r['output_tokens']==20 and r['concurrency'] in [1,32]]), '',
    '在 64K、C32 这两个点，平均 TTFT 已经大于首 token 后耗时；不能把整个扫描的等待都归因于 Decode。服务端 Prefill 计时与客户端 TTFT 也不同，后者还包含排队等开销。', '',
    '## 目前能与不能下的结论', '',
    '可以确认这台机器的消息大小、卡组和通信原语会显著改变可达到的带宽；8 卡大消息下 AG＋RS 明显快于等 S 的两次 A2A。可以按固定源码和实际 token 数计算核心通信量估计，并与实测阶段耗时对照。', '',
    '**不能把本报告的阶段推算写成“模型实际链路带宽实测”。** 旧数据缺少每次 collective 的调用 trace 和链路字节计数；SP padding、空闲 DP 的 dummy token、变长 all_gatherv/reduce_scatterv、embedding/logits 与控制流量未完整计入。阶段 GB/s 与单组 microbenchmark busbw 的范围不同，不能相除得到利用率或通信占比。', '',
    '同样不能直接宣布更换 MoE backend 能获得上述倍数收益。真正的 A2A dispatch 取决于 top-k 路由、目的 rank 去重、数据压缩及不均衡；当前均匀 A2A microbenchmark 只测基础原语。', '',
    '## 证据与复现', '',
    '- 通信探针：[collective_bandwidth.py](../../tools/hardware/probes/collective_bandwidth.py)；逐任务实际命令、设备序列、开始结束时间：[bandwidth-state.json](raw/bandwidth-state.json)。',
    '- 每点的 5 次样本及所有 rank 耗时：`raw/gpu*-*.jsonl`；逐任务日志：`raw/gpu*-*.log`；独立重算校验：[verification.json](verification.json)。环境、模型配置指纹与设备可见性：[environment-verification.json](environment-verification.json)。',
    '- 模型阶段计算：[analyze_phases.py](analyze_phases.py)，以原先 91 点冻结快照为输入，不混入中断测点或 warmup。服务端 91 点计数均与客户端一致，未见 preemption；计算出的 Prefill KV token 总量均等于实际输入 token 总量。',
    '- 固定镜像源码摘录：[parallel.py](source/vllm/vllm/config/parallel.py)、[GLM 模型实现](source/vllm-metax/vllm_metax/models/glm5next/common/model.py)、[量化后 dispatch](source/vllm/vllm/model_executor/layers/fused_moe/prepare_finalize/naive_dp_ep.py)、[AG/RS 分组](source/vllm/vllm/distributed/device_communicators/all2all.py)、[变长集合通信](source/vllm/vllm/distributed/device_communicators/pynccl.py)。', '',
    '本次结束后停止专用通信容器，保留已停止的模型扫描，不自动恢复性能矩阵。', '']
(OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
details = ['# 通信 microbenchmark 全部结果', '', '[返回摘要](README.md)', '',
           '每行 5 个样本，每个样本重复该行操作 20 次；组合操作每次含两个 collective。时间取每轮最慢 rank，均值/中位数/min/max 均针对这 5 个样本，非逐调用分位数。algbw/busbw 用中位数计算。', '']
for g, label in groups:
    for op, title in ops:
        details += [f'## {label} · {title}', '',
                    table(['S(KiB)', '均值(ms)', '中位数(ms)', 'min(ms)', 'max(ms)', 'algbw(GB/s)', 'busbw(GB/s)'], [
                        [f'{s/1024:g}'] + [f'{at(g,op,s)[k]:.6f}' for k in ['mean_ms','median_ms','min_ms','max_ms','algorithm_GBps','bus_GBps']]
                        for s in state['sizes']]), '']
(OUT / 'bandwidth-details.md').write_text('\n'.join(details), encoding='utf-8')
verification = dict(jobs=36, points=576, samples=2880, correctness='all_passed',
    recalculated=['max_rank_per_sample','median','algorithm_GBps','bus_GBps'],
    jsonl_sha256=hashes, phase_points=91,
    source_core_sha256=phase['source']['core']['sha256'],
    source_details_sha256=phase['source']['details']['sha256'],
    microbenchmark_timing='synchronized host batches; maximum rank; median of 5 batches',
    physical_link_counters_collected=False, historical_model_collective_trace_available=False,
    original_scan_resumed=False)
(OUT / 'verification.json').write_text(json.dumps(verification, indent=2), encoding='utf-8')
print(json.dumps(dict(points=len(rows), ep8_256MiB_agrs_over_a2a=ratio, ep8_8KiB_ratio=tiny)))
