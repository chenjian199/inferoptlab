# 60 / 61 / 64 / 65：GLM-5.3-Flash-W8A8 环境与性能差异核对

**结论：没有完全对齐，最显著的已确认差异是执行模式和并行配置。** 61 的 TP8 结果启用了图执行；60 当前简版结果来自 TP1/DP8/EP8、eager 执行。两者不能直接作为机器性能对比。核心软件比镜像名称看起来更接近：四机 vLLM 基础源码提交相同，抽查的 11 个关键源码文件、FlashMLA 二进制、MCCL 和 MACA runtime 文件哈希相同。不能据此认定 60 的镜像整体错误，也不能认定四机环境已经完全一致。

本次通过 SSH 只读采集了容器、已安装包、进程参数、模型元数据、源码指纹和既有运行日志，没有修改远端服务或启动新压测。主机/容器清单采集于 **2026-11-26 16:07（北京时间）**，后续补充了相关文件。其他同事在持续调整 64、65 的服务，本报告区分历史测点证据与采集时进程状态。

完整字段与原始日志链接见 [证据明细](details.md)，可机器读取的对照见 [comparison.json](comparison.json)，远端路径与本地文件映射见 [evidence-files.json](evidence-files.json)。

## 1. 差距有多大，比较对象是否一致

以下统一取 **4K 输入、20 输出、并发 1**。60 使用 [14:49 简版快照](../glm53-cached-decode-20261126/quick-read.md)，61 使用同事提供的 [TP8.md](../TP8.md)。延迟为平均值。

| 数据来源 | 并行形态 | 执行模式 | 重复/请求数 | TTFT ms | TPOT ms | E2E s | 输出 tok/s | 请求 req/s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 60 当前简版 | TP1 / DP8 / EP8 | eager | 3/12 | 301.19 | 166.47 | 3.46 | 5.77 | 0.289 |
| 61 TP8.md | TP8 / DP1 / EP 关 | graph | 1/4 | 28.45 | 18.75 | 0.38 | 51.77 | 2.588 |
| 61 TP8.md | TP8 / DP1 / EP8 | graph | 1/4 | 32.67 | 23.46 | 0.48 | 41.67 | 2.083 |

60 的 TPOT 分别约为 61 两组的 **8.88 倍、7.10 倍**。这里同时改变了 TP/DP、EP、图执行和部分调度参数，不能把这个倍数归因于某一个因素。

还有两个辅助证据：

- **60 曾测过 TP8/EP8 eager**：4K/20、并发 2、8 请求，TPOT 平均 **153.181 ms**；61 同形态 graph 为 **25.28 ms**，仍差约 **6.06 倍**。因此“仅仅因为这次拿 DP8 和 TP8 对比”不足以解释全部现象。但该预检与 61 还存在 attention 配置、运行时及补丁注入条件差别，不能当作只切换 graph 的实验。见 [60 启动命令](../glm53-cached-decode-20261126/observed-launch.json) 和 [AIPerf 原始数据](../glm53-cached-decode-20261126/preflight-evidence/observed-proof-4k-c2-1795667946786800114/aiperf/profile_export_aiperf.json)。
- **64 的 TP1/DP8、EP 关、eager 结果也慢**：4K/20、并发 1 的三轮 TPOT 分别 **155.375 / 153.497 / 152.712 ms**，与 60 属于相近量级。64 镜像不同于 60，却同样未得到 61 的低时延。这是排查方向的旁证，不是跨机受控实验。见 [64 已有结果](64-read_64_evidence.json)。

## 2. 硬件、镜像与源码

四机清单均显示 **8 张 MetaX C500、驱动 3.9.35、mx-smi 2.3.4、GPU BIOS 1.35.6.0**；CPU 型号均为 **Intel Xeon Gold 6530**，系统可见 128 个逻辑 CPU。这是型号和版本核对，不代表 GPU 时钟、温度、互连实测或历史负载完全相同。证据：[60](60-inventory.json)、[61](61-inventory.json)、[64](64-inventory.json)、[65](65-inventory.json)。

| 项目 | 60 | 61 | 64 | 65 |
|---|---|---|---|---|
| 对应服务容器 | inferoptlab-scan-38ffbe62b683 | glm53-vllm032 | c500-glm-runtime-20261124 | glm53-tp4dp2-ep1-graph-latest-20261126 |
| 镜像 ID 前 12 位 | `9d82e3b3cc52` | `94107f40d1ef` | `7b0b94ea49e7` | `7b0b94ea49e7` |
| Python 环境 | `/opt/vllm-env` | `/opt/conda` | `/opt/conda` | `/opt/conda` |
| vLLM 安装方式 | site-packages 安装包 | `/work/src` editable | `/work/src` editable | `/work/src` editable |
| 容器网络 | host | host | bridge | host |
| CPU quota / cpuset / 内存限额 | 无显式限制 | 无显式限制 | 无显式限制 | 无显式限制 |

完整镜像 ID：

```text
60 sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b
61 sha256:94107f40d1ef62628b70025ca3d7ae388bf108f7956ba41424ca00d0b443fb82
64 sha256:7b0b94ea49e73509d48a071ddf20c19682d5a8d444011a9690c6d4b0a675f3f5
65 sha256:7b0b94ea49e73509d48a071ddf20c19682d5a8d444011a9690c6d4b0a675f3f5
```

**只有 64 和 65 的镜像 ID 相同。** 但它们仍挂载外部源码和观察器；同一镜像 ID 不能锁定完整的实际运行环境。61 的容器在初次采集时为 `sleep infinity`，其 TP8 测试服务曾在容器内启动，历史启动证据位于 `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal`，不能拿容器初始命令代替测试启动命令。

四机对应基础源码版本：

```text
vLLM       5df63a7203cdb9328d824a27b682e77c7b9928be
vLLM-MetaX 0962c8735ffe4795800030680311410848512b82
```

61/64/65 来自实际 editable 源码仓库的 `git rev-parse HEAD`；60 安装目录没有 Git 元数据，提交号来自构建镜像标签，并用已安装文件内容交叉核对。**未执行全源码逐文件比较。**

61/64/65 的插件目录都包含 GLM W8A8 与 `moe_align_legacy_abi.py` 修改，因此不能把 Git HEAD 视为未经修改的代码。经内容哈希核对，60 对应的关键 GLM model、sparse indexer、MoE ABI 补丁、FlashMLA/稀疏 MLA 相关采样源码与其他三机一致；共 11 个文件一致，完整列表见 [源码指纹表](details.md)。

## 3. 已安装依赖与实际库文件

| 组件 | 60 | 61 | 64 | 65 |
|---|---|---|---|---|
| vLLM | 0.32.0+empty | 同左 | 同左 | 同左 |
| MetaX 插件构建版本 | 0.32.0+g0962c873.maca3.9.0.29.torch2.10.0 | 0.32.0+g0962c8.d20261124.maca3.9.0.29.torch2.10.0 | 同 61 | 同 61 |
| PyTorch | 2.10.0+metax3.9.0.8 | 同左 | 同左 | 同左 |
| Triton | 3.6.0+metax3.9.0.8 | 同左 | 同左 | 同左 |
| FlashMLA 包版本 | 1.0.1+metax3.9.0.8torch2.10 | 同左 | 同左 | 同左 |
| mcoplib | 0.4.14+gf3794c4.maca3.9.0.31.torch2.10 | 同左 | 同左 | 同左 |
| mctlassEx | 0.1.1+metax3.9.0.8torch2.10 | 同左 | 同左 | 同左 |
| DeepEP | 1.0.0+metax3.9.0.11torch2.10 | 同左 | 同左 | 同左 |
| compressed-tensors | 0.17.0 | 同左 | 同左 | 同左 |
| **服务端 Transformers** | **5.19.0** | **5.17.0** | **5.17.0** | **5.17.0** |
| AIPerf 客户端 | 0.12.0 | 0.12.0 | 0.12.0 | 0.12.0 |
| 客户端 Transformers | 5.24.0 | 5.24.0 | 5.24.0 | 5.24.1 |

61/64/65 还保留了旧版本 `flash_kda`、`flash-linear-attention`、`flash_prefill`、`flash_moba`、`maca-tile`，60 的服务 Python 环境没有这些包。**已安装不等于本次模型实际调用**，仅凭这些包的有无无法解释时延差距。采集未导入 GPU 框架，也没有为审计分配 GPU 显存。

除版本号外，实际服务 Python 环境中的以下文件四机哈希一致：

| 文件 | SHA-256 |
|---|---|
| `flash_mla_cuda.cpython-312-x86_64-linux-gnu.so` | `78565ee0361ee0598b0dd187c5132bec2d0ac3bd27bc4ce2edcdedd4f39299fc` |
| `/opt/maca/lib/libmccl.so` | `6e6fc4c5e4d6de13c787fef547852307deecba94fccc1f9f46b87669a126845e` |
| `/opt/maca/lib/libmcruntime.so` | `d14efe482d8336e736c3e5ce7d36ec1b7a7409f20282eea8d000d4bd02bcbd76` |

60 底层 `/opt/conda` 里还存在另一份旧 FlashMLA，不能把它与服务实际使用的 `/opt/vllm-env` 混淆。本次比较使用服务环境内的文件。这里验证的是文件指纹，没有对每个 worker 的全部已加载映射及 JIT 产物做一致性证明。

同样，宿主机 `mx-smi` 的 MACA 显示为 3.8.3.17，镜像继承标签还可能写着 SDK 3.8.2.6；它们不能代替容器内后续安装的 3.9.0.29 SDK 信息。60 的包管理记录与复制进镜像的文件也可能不同。**判断 runtime 是否相同应以实际路径、文件和构建记录交叉验证，不能只比较标签。**

指纹原件：[60](60-fingerprint_60.json)、[61](61-fingerprint_61.json)、[64](64-fingerprint_64.json)、[65](65-fingerprint_65.json)；61 客户端版本额外通过实际 venv 查询，见 [client61](61-client61.json)。

## 4. 模型是否对齐

| 机器 | 实际挂载的宿主机模型目录 |
|---|---|
| 60 | `/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8` |
| 61 | `/data/glm53/models/GLM-5.3-Flash-W8A8` |
| 64 | `/data/ubuntu-models/GLM-5.3-Flash-W8A8` |
| 65 | `/data/heyi/c500-glm5.3/GLM-5.3-Flash-W8A8` |

四机均为 GLM-5.3-Flash-W8A8，`config.json` 中架构为 `Glm5NextForConditionalGeneration`。四机的 **config、generation_config、权重索引、tokenizer.json、tokenizer_config.json 五个文件 SHA-256 完全一致**。例如 config 哈希为 `671a1dec45411c0d126573646ec7173aa1b4fd02aaaab62be8613b9c08e3018e`；全部哈希保存在 [comparison.json](comparison.json)。

权重均为 **47 个 safetensors 分片、总计 328,471,503,836 字节**，逐个文件名和大小完全一致。没有发现模型配置或 tokenizer 不同的证据。

**本次没有重新读取四机全部约 328 GB 权重计算逐分片哈希，因此尚不能声称权重逐字节一致。** 当前结论是元数据、分片清单及大小一致。要把权重完全一致作为正式验收条件，应补充与实际文件绑定的完整分片哈希清单。

## 5. 启动参数没有统一

下表以相关运行保存的 `/server_info` 为依据。60 对应当前 r3 DP8；61 对应 TP8.md 的正式 graph 测试；64 对应已完成的 4K EP 关测试；65 对应已有 4K 尝试保存的 server-info。

| 参数 | 60 r3 | 61 TP8.md | 64 4K EP 关 | 65 4K 尝试历史快照 |
|---|---|---|---|---|
| TP / PP / DP | 1 / 1 / 8 | 8 / 1 / 1 | 1 / 1 / 8 | 4 / 1 / 2 |
| EP | 开，EP8 | 分别关 / 开 EP8 | 关 | 关 |
| enforce_eager | **true** | **false** | **true** | **false** |
| 生效 cudagraph_mode | NONE (`0`) | FULL_AND_PIECEWISE (`[2,1]`) | NONE | FULL_AND_PIECEWISE |
| max_model_len | 73728 | 73728 | 16896 | 65557 |
| max_num_batched_tokens | **1024** | **4096** | **2048** | **4096** |
| max_num_seqs | **16** | **128** | **16** | **64** |
| gpu_memory_utilization | 0.90 | 0.90 | **0.915** | 0.90 |
| mamba_block_size | 256 | 256 | 256 | **16** |
| prefix_match_unit | 16 | 16 | 16 | **null** |
| sparse_mla_force_mqa | true | true | true | **false** |
| 自动推导 cache block_size | 4352 | 640 | 4352 | 1152 |
| V2 model runner 环境项 | true | true | server-info 未暴露该项 | true |

共同部分包括 BF16、compressed-tensors、prefix caching、chunked prefill、关闭 async scheduling、关闭 custom all-reduce。EP 开启的 60/61 使用 `allgather_reducescatter`；EP 关闭时，不能因为配置中仍有这个默认值就声称执行了同样的 EP 通信。

**61 确实捕获了图，不只是配方命名写了 graph。** 日志同时包含 `enforce_eager=False`、`cudagraph_mode=FULL_AND_PIECEWISE`，以及 `Graph capturing finished ... took 0.49/0.50 GiB`。这里 `compilation_config.mode=NONE` 不等于 CUDA/MACA 图未启用，torch 编译模式和图执行是不同配置项。`--enforce-eager` 禁用图执行的语义可参考 [vLLM 官方说明](https://docs.vllm.ai/en/stable/configuration/conserving_memory/)，实际生效情况以本次固定版本日志为准。

**65 的记录存在明显时间差。** 16:07 抓到的进程命令已经要求 `mamba-block-size=256`、`prefix-match-unit=16`、`sparse_mla_force_mqa=true`，而之前保存的 server-info 是 16/null/false。说明启动命令与已保存的服务快照不能拼成一套“已验证配置”；可能涉及服务重启或旧 endpoint，现有证据不能确定具体原因。后续读取 18082 的 server-info 时连接被拒绝，因此未取得这组新参数生效后的快照。需要以新启动实例的就绪检查和 server-info 重新绑定。

此外，64 的容器为 bridge 网络，其他三个相关容器为 host；60 与其他三机的 `LD_LIBRARY_PATH` 中 mxshmem 等路径不同。这些都应固化，但当前没有证据表明它们造成了约 7 倍差距。全部参数及启动日志见 [details.md](details.md)，65 进程参数见 [65-runtime.json](65-runtime.json)。

## 6. 测试器和纯 Decode 协议核对

61 的原始正式结果位于容器 `glm53-vllm032` 内：

```text
/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal
```

已取回并自动核对 **18 个 AIPerf profile**：TTFT/TPOT/E2E 的均值和 P95、输出吞吐、请求吞吐、请求数，均与 `outputs/TP8.md` 的 18 行在显示精度上完全一致。

这 18 个点的 `engine-verification.json` 和 `profile-verification.json` 均为 valid。逐请求检查确认：原始上下文 L 已计算，HTTP 输入 L+1、每步 query=1、输出 20、零抢占。不是把正常长 Prefill 混入某一侧，也不是把 20 个输出误记成 1 个。

| 测试协议 | 60 | 61 |
|---|---|---|
| AIPerf | 0.12.0 | 0.12.0 |
| 请求接口 | streaming completions | 同左 |
| 原始上下文 | 每并发槽独立，L 全缓存 | 同左 |
| 额外输入 | P 产生的一个 seed，HTTP 长度 L+1 | 同左 |
| 每轮请求数 | 并发 × 4 | 并发 × 4 |
| 每配置重复数 | **3** | **1** |
| 输入长度 | 4096 / 16384 / 65536 | 同左 |
| 输出长度 | **20 / 50** | **20** |
| seed | 20261125 | 20261125 |
| AIPerf 输入 hook | 相同 SHA-256 | 相同 SHA-256 |
| 服务观察器 | 与 61/64 同哈希 | 与 60/64 同哈希 |

以上协议一致不等于实际发送的每个 token ID 完全一致：P 产生的 seed 可能随推理结果变化，本次没有对四机全部 fixture 做逐 token 一致性证明。性能比较时仍应冻结并核对输入 manifest。

TTFT 是缓存就绪后首个 D 输出的客户端耗时；TPOT 是每请求 `(最后输出时间−首输出时间)/(输出数−1)`，其 P95 为请求级分位数。均不包含预热 Prefill 或 P→D 真实 KV 传输。相同协议下图执行会改变时延，但仍不能把本次结果当作完整 PD 分离系统的端到端性能。

四机扫描脚本并非完全相同：

- 61 增加了异常后重启、跳过同组更高并发的分支；有效性能点仍检查 engine/profile。见 [60↔61 脚本差异](code-diff-60-61.txt)。
- 64 增加 external 服务的观察目录和就绪检查处理。见 [60↔64 差异](code-diff-60-64.txt)。
- 65 的主扫描脚本与 60 相同，但观察器额外处理 qualification 标记被删除时的竞态。见 [60↔65 观察器差异](code-diff-60-65.txt)。

因此未来应统一 benchmark 代码版本和观察器哈希；不能仅写“AIPerf 0.12.0”就视为整个测试工具一致。

## 7. 61 的失败点不能直接归为容量上限

61 两组分别在 4K/C16、16K/C8、64K/C4 遇到服务失败，随后跳过更高并发。原始 server.log 中有：

```text
RuntimeError: Triton Error [MACA]: an illegal memory access was encountered
RuntimeError: Worker failed with error 'CUDA error: an illegal memory access was encountered ...'
RuntimeError: NCCL error: unhandled maca error
```

例如 EP 关、4K 的堆栈经过 `glm5next/common/kda.py` 中 `scatter_states`，最终在 Triton launch 报非法访问。这只是错误被观察到的调用位置，异步设备错误可能晚于真正故障发生，**还不能据此定位根因到某个算子实现或断言 graph 本身有 bug**。

61 脚本在服务失联后设置 `capacity_limit`，把后面的点标成 `skipped_server_capacity`。这个标签表达了跳过策略，**不是显存不足证明**；应与 60 的 `cache_residency_failed` 区分。相关完整日志与 state 均已保存并在 [证据明细](details.md) 中链接。

65 已保存的两次尝试则分别报 `context 65556 is below required 65557` 与 `resume snapshot differs from the current recipes`，这两份 state 的 points 都为空，不能拿来补充有效性能结论。见 [65 状态与脚本证据](65-additional_65.json)。

## 8. 当前能确定什么，下一步怎样排除变量

| 判断 | 证据强度 |
|---|---|
| 四机的完整实验环境没有对齐 | 已证实：镜像、安装方式、Transformers、启动参数和部分测试代码不同 |
| 60/61 的基础 vLLM 提交不同导致差距 | 现有证据不支持：提交号一致，关键源码采样一致 |
| 核心 FlashMLA/MCCL/runtime 文件不同导致差距 | 采样文件哈希相同，现有证据不支持 |
| 模型配置/tokenizer 不同 | 五个元数据文件哈希相同，现有证据不支持 |
| 权重全部逐字节一致 | 未完成四机全分片哈希验证 |
| eager/graph 是主要排查对象 | 强候选：直接配置和日志证实，60/64 eager 与 61 graph 差异显著；尚无单变量 A/B |
| 单独打开 graph 就一定恢复 61 性能并稳定跑完 | 尚不能保证，61 高并发已有服务端故障 |
| 61 硬件比 60 快约 7–9 倍 | 不能由这些不等配置的结果推出 |

建议先做以下小规模受控核对，再决定是否重新跑全矩阵。这是后续建议，本次未执行：

1. **固定单机、镜像和挂载源码**，使用 TP8/DP1/EP8、4K 输入、20 输出、并发 1/2/4；固定 tokenizer、输入数据、cache/attention 参数、观察器和 AIPerf，分别 eager 与 graph，每点仍按并发×4、重复 3 次。保持 L 全命中和 query=1 验证，记录实际 server-info 与图捕获完成日志。
2. **只有执行模式的影响已量化后，再交换镜像**。保持步骤 1 的所有运行参数不变，同时固定外部源码/补丁挂载；否则“镜像 A/B”仍混入代码变化。服务端 Transformers 也统一固定版本。
3. **把同一部署迁到 61**，对照输入 manifest 和权重完整校验清单，比较同形态同模式的性能；这才用于判断机器、驱动配置或主机负载差异。
4. **单独检查失败边界**：复现 61 的 4K/C16 等点，区分缓存驻留失败、显存不足、图/内核异常、通信后续错误。故障未解释前，不把更高并发跳过标签作为容量曲线。

每个有效结果应绑定：镜像 ID、外部源码及补丁哈希、服务 Python 包版本、关键 native 库哈希、模型/输入 manifest、启动 argv/env、实际 server-info、AIPerf 与 hook 版本、观察器版本、运行实例和采集时间。项目已有 snapshot/launch/server-info 结构可以承载这些信息；主要需要补齐和严格绑定，避免分别保存的命令、服务快照、结果来自不同实例。

## 9. 本地复核

```powershell
python outputs/environment-alignment-20261126/build_comparison.py
```

脚本仅从本地已采集证据生成表格并检查：18 行性能数字及请求数匹配、18 个点的缓存/调度与 profile 验证通过、47 个权重分片清单一致、11 个采样源码哈希一致。它不会连接远端、修改服务或重新运行测试。

所有本次审计文件均放在 `outputs/environment-alignment-20261126/`，没有改动部署配方和生产代码，也没有执行 Git 暂存、提交或推送。
