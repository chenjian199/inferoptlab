# TP2 / DP4 / EP8：图模式纯 Decode Profiler 简版

采集完成：2026-11-26 17:23:15（北京时间）。

三组场景均已完成：4K / 16K / 64K 输入，输出固定 200 tokens，总并发 4。每个并发槽使用独立上下文并固定到一个 DP rank。

**24 个 GPU worker trace 齐备**，每个 trace 验证到 32 次图重放及 32 个 `context=0, generation=1` 的迭代标注。
每组先做无 Profiler 对照，再做采样请求；各轮 16 请求（并发×4），共 96 个完整的 200-token 请求。

原始上下文全命中，线上输入为 L+1（额外一个 P 产生的 seed）；全部请求验证 query=1、零抢占、输出 200。预热 Prefill 与 P→D 传输不计入本次 Decode 时间。

## running 条数与生效参数

| 参数 | 实际值 |
|---|---|
| tensor / pipeline / data / expert parallel | 2 / 1 / 4 / 8 |
| max_num_seqs（每个 DP 调度实例） | 16 |
| 配置的四个 DP 实例上限之和 | 64；不代表实际负载 |
| 本轮总并发 | 4，每个 DP 实例 1 |
| max_num_batched_tokens | 2048 |
| max_model_len | 73728 |
| enforce_eager | False |
| cudagraph_mode | [2, 1]（FULL_AND_PIECEWISE） |
| EP 通信后端 | allgather_reducescatter |
| GPU memory utilization | 0.9 |
| mamba_block_size / prefix_match_unit | 256 / 16 |
| 实际 attention cache block_size | 2176（自动推导，非 batched token 预算） |
| 量化 / 激活 dtype | compressed-tensors W8A8 / bfloat16 |
| 调度 | chunked prefill 开；async scheduling 关 |
| 采样窗口 | delay_iterations=8、max_iterations=32；实测采样 32 个，完整请求仍输出 200 |

实际配置见 [server-info](run-r2/server/server-info.json)，完整命令见 [launch](run-r2/server/launch.json)，冻结配方见 [snapshot](run-r2/snapshot.json)。

## 不启用 Profiler 的请求性能

以下是对照轮，未调用 start_profile。延迟为请求级均值/P95；E2E 仅针对缓存续接的 200-token 请求。

| 输入 | 请求数 | TTFT ms 平均/P95 | TPOT ms 平均/P95 | E2E s 平均/P95 | 输出 tok/s | 请求 req/s |
|---|---:|---:|---:|---:|---:|---:|
| 4K | 16 | 100.36 / 108.77 | 33.78 / 33.84 | 6.82 / 6.84 | 117.08 | 0.585 |
| 16K | 16 | 117.95 / 127.39 | 33.84 / 33.95 | 6.85 / 6.87 | 116.58 | 0.583 |
| 64K | 16 | 173.97 / 230.19 | 34.03 / 34.58 | 6.95 / 7.07 | 114.78 | 0.574 |

**调度实测**：96 个请求的观察记录中，每个 DP rank 的最大 running 和 scheduled 请求数均为 **1**，与总并发 4 的固定路由一致。

## GPU 采样窗口与热点

下面选用 DP0/TP0（EP0）作可读示例；八卡完整算子表见 [operators.md](operators/operators.md)。每张卡独立统计，跨卡时间不相加。

| 输入 | 图重放/迭代 | GPU kernel 调用数 | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|---:|---:|
| 4K | 32 / 32 | 79712 | 852.70 | 851.14 | 1238.87 |
| 16K | 32 / 32 | 79712 | 871.13 | 869.46 | 1276.37 |
| 64K | 32 / 32 | 79712 | 871.44 | 869.82 | 1271.53 |

kernel 时长和是采样窗口内 GPU 工作量；区间并集处理重叠。两者均不能直接当作 E2E 或无 Profiler 的单 token 延迟。

### 同卡算子类别对照（依据 kernel 名称）

各格为 32 迭代内的 kernel 时长和 ms / 调用数；类别只按名称归类，无法确定的名称保留在 other，不能当成模型模块的精确占比。

| 类别 | 4K | 16K | 64K |
|---|---:|---:|---:|
| attention | 17.056 / 704 | 17.069 / 704 | 17.069 / 704 |
| collective | 197.060 / 7008 | 208.139 / 7008 | 203.986 / 7008 |
| gemm | 238.546 / 11808 | 238.651 / 11808 | 238.595 / 11808 |
| indexer_or_topk | 24.190 / 3072 | 27.008 / 3072 | 31.805 / 3072 |
| kda_or_state | 17.643 / 2176 | 17.653 / 2176 | 17.665 / 2176 |
| mhc | 85.266 / 5760 | 85.368 / 5760 | 85.365 / 5760 |
| moe_gemm | 98.112 / 2688 | 102.225 / 2688 | 101.432 / 2688 |
| moe_routing_or_compute | 20.958 / 4032 | 20.975 / 4032 | 20.983 / 4032 |
| normalization | 1.428 / 384 | 1.431 / 384 | 1.429 / 384 |
| other | 128.991 / 35104 | 129.165 / 35104 | 129.637 / 35104 |
| quantization | 23.450 / 6976 | 23.442 / 6976 | 23.474 / 6976 |

### 4K：DP0/TP0 前 10 个 GPU kernel

| kernel | 32 迭代调用数 | 总 ms | 每次平均 μs | 每次 P95 μs |
|---|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 98.885 | 73.575 | 123.226 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.830 | 61.026 | 69.879 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 62.832 | 46.750 | 90.131 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 55.935 | 17.836 | 32.212 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.825 | 14.870 | 15.270 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.081 | 14.776 | 15.160 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 41.522 | 30.895 | 20.515 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 35.281 | 26.250 | 48.200 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.850 | 25.930 | 26.729 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 30.951 | 28.448 | 29.877 |

### 16K：DP0/TP0 前 10 个 GPU kernel

| kernel | 32 迭代调用数 | 总 ms | 每次平均 μs | 每次 P95 μs |
|---|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 100.437 | 74.730 | 123.730 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.824 | 61.022 | 69.800 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 65.590 | 48.802 | 90.569 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 55.973 | 17.849 | 32.173 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.873 | 14.887 | 15.310 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.138 | 14.796 | 15.160 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 38.291 | 28.490 | 21.437 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 36.634 | 27.258 | 48.248 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.844 | 25.926 | 26.730 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 30.957 | 28.454 | 29.840 |

### 64K：DP0/TP0 前 10 个 GPU kernel

| kernel | 32 迭代调用数 | 总 ms | 每次平均 μs | 每次 P95 μs |
|---|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 102.071 | 75.945 | 128.946 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.823 | 61.021 | 69.825 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 65.062 | 48.409 | 90.160 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 55.930 | 17.835 | 32.102 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.886 | 14.891 | 15.311 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.121 | 14.790 | 15.150 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 36.370 | 27.061 | 48.005 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.783 | 25.880 | 26.680 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 34.672 | 25.798 | 21.145 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 30.977 | 28.471 | 29.830 |

## 文件与计时边界

- [完整算子调用/耗时表](operators/operators.md)：逐卡 GPU kernel、CPU 算子；JSON 保留完整模板名、最大耗时和分类提示。
- [原始 trace 目录](run-r2/server/observations/profiles)：24 份 `.pt.trace.json.gz`，可解压后在本地 Perfetto 查看；文件名包含场景和 DP/TP/EP rank。
- [运行状态](run-r2/state.json)、[server 日志](run-r2/server/server.log)、各场景 `control/` 与 `profiled/` 保存请求指标和验证证据。
- [可复用采集入口](../../benchmark/breakdown/cached_decode_profile.py)；[部署配方](../../recipes/deployments/glm53-flash/c500/vllm/cached-decode/tp2-dp4-ep8-profiler.yaml)。
- CPU 算子耗时包含子调用；图重放不重新执行所有 Python/ATen 调用。GPU kernel 记录与 CPU 调用覆盖不同，不能补造缺失的算子 shape 或模块层级。
- `profiled/` 请求时延含采样和 trace 导出干扰，仅作诊断；GPU trace 不是 200 个输出 token 的完整时间线，而是其中 32 个迭代。
- 首轮 r1 在 16K 复验时因请求标识重名中止，原始缓存实际全命中。已修正场景标识，并使用 r2 重新完成全部三组；本报告仅使用 r2。
- 本轮结束后，控制器自动停止并清理其拥有的模型服务；这里的 running=1 指采样期间的观测值。

本地重建报告：`python outputs/glm53-tp2-dp4-ep8-profiler-20261126/summarize_results.py`。
