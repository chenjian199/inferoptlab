# C500 通信带宽与 GLM-5.3 阶段传输量

**原模型扫描已停止；通信 microbenchmark 已完成 36 个任务、576 个测点，全部数值正确性检查通过。**

[逐消息大小完整结果](bandwidth-details.md) · [91 点阶段传输量推算](phase-analysis.md) · [机器可读计算结果](phase-estimates.json) · [原始通信记录](raw/bandwidth-state.json)

## 先看结论

- 全部 8 卡、相同 `S=256 MiB` 时，两次 All-to-All 为 **14.801 ms / 31.74 GB/s**，All-Gather＋Reduce-Scatter 为 **4.084 ms / 115.01 GB/s**，后者耗时约为前者的 **1/3.62**。这是相同 S 的通信原语对比，不是模型加速比。
- 差异随消息大小变化：8 KiB 时，上述耗时比只有 **1.21×**。Decode 的小消息不能套用大消息峰值带宽。
- 当前两种部署都使用 AG＋RS；这批 91 点不是 A2A 与 AG＋RS 的模型 A/B 测试。源码确认二者 MoE 均走 EP8，Attention 分别走 TP4、TP2。
- 理想无 padding 的主要通信量：TP4 约 **5.845 MB/token**，TP2 约 **4.370 MB/token**，TP4 多 **33.7%**；MoE 部分相同，差别来自 Attention 的 TP 通信。均为 8 卡合计逻辑发送量。
- 历史数据推算的阶段有效带宽：Prefill **15.56–59.23 GB/s**，Decode **0.014–0.563 GB/s**，均为 8 卡合计估计值。Decode 的字节量少但耗时长，不能仅凭这一差距判定链路带宽不足；还要区分消息延迟、计算/显存访问、padding 和调度等待。

## 实测条件与计时口径

- 主机：`metax-60 / gpu-node-060`，8×C500 64 GiB。`mx-smi topo -m` 显示 0–3 为 MX 组、4–7 为 MX 组，跨组为 NODE；NODE 表示经过同 NUMA 内的 PCIe/主机桥路径。
- 使用与模型相同的固定镜像 `sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b`，PyTorch `2.10.0+metax3.9.0.8`。通过 PyTorch distributed 的 `nccl` 后端调用沐曦通信实现；未运行 NVIDIA GPU/NCCL 性能程序。
- 每种原语：BF16，消息 8 KiB 到 256 MiB、按 2 倍递增；预热 10 次，每个样本连续 20 次操作，采 5 个样本。每个样本取最慢 rank 的同步主机耗时，表格用 5 个样本的中位数。包含 Python 调用开销，非纯 kernel 时间。
- 所有组顺序执行，各组的测试不同时争用互联；不代表模型中多个 TP 组并发时的带宽。每点先验证非零输入的结果，随后测量；All-Reduce 计时重复用零输入，避免累加溢出。
- `S`：AG 的总输出/RS 的总输入字节数；A2A、All-Reduce 为每 rank 完整数组字节数。AG 输入为 S/N，RS 输出为 S/N；A2A 每 rank 输入与输出均为 S。两种组合的输入语义不同。
- `algbw=S/t`；AG、RS、A2A 的 `busbw=algbw×(N−1)/N`；All-Reduce 及这里的两次调用组合再乘 2。该值是归一化逻辑带宽，不是每根 PCIe/MX 链路的实测计数；不能把全部 8 卡 AG 的 busbw 当作一根跨组链路速率。公式沿用 [NCCL-tests 带宽定义](https://raw.githubusercontent.com/NVIDIA/nccl-tests/master/doc/PERFORMANCE.md)。

## 256 MiB 下各分组对比

以下均为归一化 busbw，单位十进制 GB/s；两次 A2A 与 AG＋RS 同样计入两次通信量。

| GPU 组 | A2A | AG | RS | All-Reduce | 两次 A2A | AG＋RS |
| --- | --- | --- | --- | --- | --- | --- |
| 全部 8 卡 / EP8 | 31.72 | 118.85 | 111.32 | 119.26 | 31.74 | 115.01 |
| 0–3，MX 组 / TP4 | 125.85 | 132.58 | 128.34 | 135.41 | 126.09 | 130.56 |
| 4–7，MX 组 / TP4 | 125.84 | 132.60 | 128.29 | 135.30 | 126.00 | 130.55 |
| 0、1，MX 组 / TP2 | 45.95 | 88.14 | 85.28 | 90.09 | 45.94 | 86.63 |
| 0、4，跨组 NODE | 35.50 | 35.05 | 33.36 | 36.38 | 35.53 | 34.17 |
| 0、2、4、6，跨组 4 卡 | 36.51 | 70.35 | 67.84 | 72.32 | 36.37 | 69.10 |

![C500 通信带宽随消息大小变化](bandwidth.png)

## EP8：从 Decode 小消息到 Prefill 大消息

| S | 两次 A2A(ms) | AG＋RS(ms) | 两次 A2A(GB/s) | AG＋RS(GB/s) | 耗时比 A2A/AGRS |
| --- | --- | --- | --- | --- | --- |
| 8 KiB | 0.1321 | 0.1088 | 0.11 | 0.13 | 1.21× |
| 64 KiB | 0.1237 | 0.1044 | 0.93 | 1.10 | 1.19× |
| 1 MiB | 0.1505 | 0.1115 | 12.19 | 16.45 | 1.35× |
| 32 MiB | 2.0166 | 0.6727 | 29.12 | 87.29 | 3.00× |
| 64 MiB | 3.9025 | 1.1899 | 30.09 | 98.70 | 3.28× |
| 256 MiB | 14.8007 | 4.0844 | 31.74 | 115.01 | 3.62× |

Decode 假设一次调度有 C 个有效 token，则 EP8 的 INT8 dispatch 激活总量约 C×4096 B，BF16 combine 总量约 C×8192 B，另有路由元数据和 padding。C=1–128 对应约 4 KiB–512 KiB / 8 KiB–1 MiB，属于小消息区。最低 4 KiB 的 dispatch 小于本次 8 KiB 起点，没有对它外推带宽。

Prefill 的 4096 是每个 DP 引擎的 batch token 上限；TP4/DP2 全忙时最多约 8192 token/步，MoE dispatch/combine 激活约 32/64 MiB；TP2/DP4 全忙时最多约 16384 token/步，对应 64/128 MiB。64K 输入会拆成多个 chunk，不能把 64K×并发都当作一次消息。实际每步 token 数旧数据未记录。

## 与已有模型耗时对照

下面使用 20-token 输出的代表点。通信量按同一源码模型推算；阶段带宽用客户端区间并集。完整 91 点及服务端阶段均值见详细文件。

| TP/DP/EP | 输入 | C | TTFT均值(s) | 首token后均值(s) | P有效GB/s(估) | D有效GB/s(估) |
| --- | --- | --- | --- | --- | --- | --- |
| 4/2/8 | 4K | 1 | 0.940 | 3.396 | 25.458 | 0.0327 |
| 4/2/8 | 4K | 32 | 3.903 | 12.185 | 49.731 | 0.2182 |
| 4/2/8 | 64K | 1 | 13.941 | 3.352 | 27.475 | 0.0331 |
| 4/2/8 | 64K | 32 | 188.297 | 16.512 | 53.883 | 0.0158 |
| 2/4/8 | 4K | 1 | 1.150 | 3.409 | 15.560 | 0.0244 |
| 2/4/8 | 4K | 32 | 5.467 | 11.566 | 37.920 | 0.1564 |
| 2/4/8 | 64K | 1 | 17.319 | 3.369 | 16.536 | 0.0246 |
| 2/4/8 | 64K | 32 | 146.850 | 26.830 | 48.721 | 0.0145 |

在 64K、C32 这两个点，平均 TTFT 已经大于首 token 后耗时；不能把整个扫描的等待都归因于 Decode。服务端 Prefill 计时与客户端 TTFT 也不同，后者还包含排队等开销。

## 目前能与不能下的结论

可以确认这台机器的消息大小、卡组和通信原语会显著改变可达到的带宽；8 卡大消息下 AG＋RS 明显快于等 S 的两次 A2A。可以按固定源码和实际 token 数计算核心通信量估计，并与实测阶段耗时对照。

**不能把本报告的阶段推算写成“模型实际链路带宽实测”。** 旧数据缺少每次 collective 的调用 trace 和链路字节计数；SP padding、空闲 DP 的 dummy token、变长 all_gatherv/reduce_scatterv、embedding/logits 与控制流量未完整计入。阶段 GB/s 与单组 microbenchmark busbw 的范围不同，不能相除得到利用率或通信占比。

同样不能直接宣布更换 MoE backend 能获得上述倍数收益。真正的 A2A dispatch 取决于 top-k 路由、目的 rank 去重、数据压缩及不均衡；当前均匀 A2A microbenchmark 只测基础原语。

## 证据与复现

- 通信探针：[collective_bandwidth.py](../../tools/hardware/probes/collective_bandwidth.py)；逐任务实际命令、设备序列、开始结束时间：[bandwidth-state.json](raw/bandwidth-state.json)。
- 每点的 5 次样本及所有 rank 耗时：`raw/gpu*-*.jsonl`；逐任务日志：`raw/gpu*-*.log`；独立重算校验：[verification.json](verification.json)。环境、模型配置指纹与设备可见性：[environment-verification.json](environment-verification.json)。
- 模型阶段计算：[analyze_phases.py](analyze_phases.py)，以原先 91 点冻结快照为输入，不混入中断测点或 warmup。服务端 91 点计数均与客户端一致，未见 preemption；计算出的 Prefill KV token 总量均等于实际输入 token 总量。
- 固定镜像源码摘录：[parallel.py](source/vllm/vllm/config/parallel.py)、[GLM 模型实现](source/vllm-metax/vllm_metax/models/glm5next/common/model.py)、[量化后 dispatch](source/vllm/vllm/model_executor/layers/fused_moe/prepare_finalize/naive_dp_ep.py)、[AG/RS 分组](source/vllm/vllm/distributed/device_communicators/all2all.py)、[变长集合通信](source/vllm/vllm/distributed/device_communicators/pynccl.py)。

本次结束后停止专用通信容器，保留已停止的模型扫描，不自动恢复性能矩阵。
