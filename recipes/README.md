# 来源配方与实机配方

这里统一保存可编辑、可引用的实际配方；定义与创建模板在 [schemas/](../schemas/README.md)，原始数据与实验结果在 [experiments/](../experiments/README.md)。`benchmark/` 等模块仅保存实现。

精度计划位于 `plans/accuracy/`，端到端拆分计划位于 `plans/breakdown/`，算子独立测试契约位于 `operators/`。首次录入了 GLM HumanEval full164/smoke32 和 layer0 gate_up INT8 历史形状契约，数据来源见 [资料库映射](../catalog/library/metax/README.md)。这些准备计划不代表已在新机器执行。

| 子目录 | 内容 |
|---|---|
| `models/`、`hardware/`、`runtimes/` | 模型身份、物理资源、运行环境 |
| `workloads/`、`protocols/`、`slas/` | 请求负载、测量方法、验收约束 |
| `test-cases/`、`studies/` | 场景组合与实验范围 |
| `deployments/`、`scenarios/` | 并行/调度/服务配置、请求集位置 |
| `plans/benchmark/`、`plans/hardware/`、`plans/diagnosis/`、`plans/analysis/` | 各阶段可复用执行计划 |
| `analysis/` | 专项分析的方法配方 |
| `sources/`、`observations/`、`measurements/` | 来源登记、历史报告与硬件测量配方；原始数据保存在 experiments |

新增 [GLM Flash P 扫描](plans/benchmark/glm53-flash-prefill.yaml)、[D 扫描](plans/benchmark/glm53-flash-decode.yaml)，部署候选位于 `deployments/glm53-flash/c500/sglang/`。参数位置、请求倍率、缓存生命周期与真机验证限制见 [详细说明](../docs/benchmark-cache-replay.md)。

模型配方按 [家族与具体模型](models/README.md) 归档，目录移动不改变 `id` 与 `version`。当前入口和文档使用实际路径，不做旧路径兼容。实验快照保存当时的配方内容；后续修改已冻结配方的事实或测量条件时应创建新版本。

硬件采集与校准已固化到 [tools/hardware](../tools/hardware/README.md)。统一入口在 metax 上的新一次结果见 [主机清单](hardware/metax-hardware-baseline-metax-host-1.0.0.yaml)、[GPU0 实测](measurements/metax-hardware-baseline-metax-gpu0-measurement-1.0.0.yaml) 和 [完整证据](../experiments/evidence/metax-hardware-baseline/1.0.0/manifest.json)。它们是独立观测，保留下方历史结果与故障记录；后续新集群按相同流程导出。

## Metax 实机配方（2026-11-23）

已使用现有 SSH alias `metax` 免密连接 `63metax`。真实模型路径为 `/NFS_62/Models`。

| 配方 | 已确认的内容 |
|---|---|
| [8 卡 C500 实机](hardware/metax-c500-8gpu.yaml) | 8 张卡的序列号、PCI BDF、NUMA/CPU 亲和、PCIe 32 GT/s ×16、逐卡显存及占用；主机 CPU/DRAM、驱动和 MACA；全部卡对拓扑 |
| [C500 单卡识别](hardware/metax-c500-observed.yaml) | MetaX C500、HBM2e、65536 MiB = 64 GiB；与历史产品规格分开登记 |
| [GLM-5.3-Flash-W8A8](models/glm/glm-5.3-flash/metax-glm-5.3-flash-w8a8.yaml) | 45 层、hidden 4096、288 routed experts / top-8；34 层线性注意力 + 11 层稀疏注意力；视觉配置、1 层 MTP、实际量化例外模块 |
| [DeepSeek-V4-Flash-w8a8-mtp](models/deepseek/deepseek-v4-flash/metax-deepseek-v4-flash-w8a8-mtp.yaml) | 43 层、hidden 4096、256 routed experts / top-6；压缩比例、RoPE、索引器和 1 层 MTP；Ascend 动态 W8A8 布局 |
| [DeepSeek-V4.1-Flash-1017-w8a8](models/deepseek/deepseek-v4.1-flash/metax-deepseek-v4.1-flash-w8a8.yaml) | 40 层、hidden 5120、384 routed experts / top-6；视觉配置、Engram 权重/scale 存储、3 层 MTP；重复 tensor 和容量限制 |
| [GLM 实际 Runtime](runtimes/metax-vllm-glm53-observed.yaml) | vLLM-MetaX 0.32.0 包版本、镜像 ID、MACA/驱动、环境变量、实际离线 LLM 设置、TP8/PP1/DP1 和采样参数 |
| [C500 GPU0 实测](measurements/metax-c500-gpu0-20261123.yaml) | 本次独立执行的 GEMM/设备复制微基准，保留 5 组耗时及推导公式 |

主机为双路 Hygon C86-4G 7470，共 96 物理核、192 线程；系统报告 DRAM `1081901404160` bytes。8 卡共 512 GiB 显存，GPU0–3 与 GPU4–7 各形成一个 `MX1` 连接组，跨组为 `SYS`。`MX1` 只表示拓扑连通类型，链路实际吞吐需要另测。

采集时驱动 `3.10.14`、MACA `3.9.0.29`、mx-smi `2.3.4`。存在 GPU6/7 相关 MetaXLink port4 降宽和错误历史；重启复查仍标记降级。现有 GLM 实验设置 `MCCL_P2P_DISABLE=1` 和 `disable_custom_all_reduce=true`。这会影响多卡性能，配方的 `discovery.health` 保留 `degraded`，正式冻结会被阻止。第一次 inventory 显示卡正在使用，随后 GPU 作业结束，本次校准前后进程清单均为空；这些观测分别保留时间，不把第一次快照改成后来状态。

### 本次单卡实测

| 测项 | 条件 | 结果（按 5 组单次耗时中位数计算） |
|---|---|---:|
| FP16 GEMM | M=N=K=4096，`torch.mm` | 225.29 TFLOPS |
| BF16 GEMM | M=N=K=4096，`torch.mm` | 224.98 TFLOPS |
| FP32 GEMM | M=N=K=4096，关闭 TF32 | 29.30 TFLOPS |
| 设备内复制 | 256 MiB，按读+写共 512 MiB 计流量 | 1364.89 GB/s |

每项预热 10 次，每组循环 20 次，共 5 组；使用 GPU Event 同步计时。GEMM 为 `2*M*N*K / seconds / 1e12`，复制为 `2*payload_bytes / seconds / 1e9`。测试在单独的临时容器中使用 GPU0，约束为 `MACA_VISIBLE_DEVICES=0`，结束后已清理该容器；未修改、重启或停止已有实验。使用的镜像是本机 Docker image ID，字段 `container_identity_kind` 明确区分它与 registry manifest digest。

这些结果只覆盖指定单卡、形状和实现。未测 INT8 GEMM、H2D/D2H、跨卡带宽或端到端 token 吞吐。常量矩阵输出检查用于排除执行错误，模型质量还需独立验收。原始记录见 [calibration-v3.json](../experiments/evidence/metax/20261123/calibration-v3.json)，实际执行脚本见 [calibration-v3.probe.py](../experiments/evidence/metax/20261123/calibration-v3.probe.py)，两者通过 SHA-256 关联。较早失败尝试保留在同目录，没有生成有效测量配方。

### 权重检查与部署限制

| 本机目录 | 索引关联分片数 | 分片文件总量 | 已知部署状态 |
|---|---:|---:|---|
| GLM-5.3-Flash-W8A8 | 47 | 305.91 GiB | 现有离线 vLLM-MetaX 实验已加载 text 路径 |
| DeepSeek-V4-Flash-w8a8-mtp | 70 | 279.41 GiB | Ascend 量化格式，C500 loader/转换未验证 |
| DeepSeek-V4.1-Flash-1017-w8a8 | 142 | 727.68 GiB | 超过 512 GiB；需 Engram/offload/更多设备方案；6 个 tensor 跨分片重复待核对 |

检查覆盖 `config.json`、tokenizer、chat template（存在时）、量化描述、索引、所有索引关联分片 header、文件大小、tensor dtype/shape/offset 和可选 QuaRot 文件。JSON Schema 用于这些结构化字段的类型校验；语义校验进一步检查 top-k、混合层序列、CPU 拓扑、显存容量与性能计算口径。Safetensors header 解析依据 [官方格式说明](https://github.com/huggingface/safetensors/blob/main/README.md#format)。

数百 GB 的权重 payload 未逐字节读取，所以 `weights_sha256: null`、`payload_verified: false`；`manifest_sha256` 只覆盖名称、大小和 header 指纹。`tokenizer.sha256` 明确取 `tokenizer.json` 文件的字节哈希，其余 tokenizer 配置分别列在 `checkpoint.auxiliary_files`。没有证据的上游 revision、质量策略和 EP 有效配置仍留空。`*.final.json` 是当前模型配方引用的完整采集；更早的扫描记录保留用于追溯，其中 DeepSeek 初次扫描尚未识别厂商索引，不作为当前配方输入。

GLM 使用 compressed-tensors，INT8 权重按 channel、激活按 token 动态量化，包含大量 BF16 非量化模块。DeepSeek 包内的 `quant_model_description.json` 为 Ascend `W8A8_DYNAMIC` 格式，不能仅按目录名直接套用 GLM 参数。DeepSeek 的 tokenizer_config 没有 chat template，需要显式提供并冻结其内容。

GLM 的模型配置允许 1048576 上下文，但已观察到的运行只设 `max_model_len=4096`、`max_num_seqs=1`、`max_num_batched_tokens=4096`、开启 chunked prefill、关闭 prefix cache、eager 执行；`speculative_config=None` 表示本次没有使用权重中存在的 MTP。配方不把模型上限等同于已验证的服务长度。真实程序是离线 LLM 实验，当前没有已验证的 OpenAI HTTP endpoint；接入 AIPerf 前需要启动并核验服务。C500 遥测需要 MACA/mx-smi 适配，不能直接依赖 NVIDIA DCGM。

### 复查与扩展

```powershell
python tools/specs.py validate recipes/hardware/metax-c500-8gpu.yaml --sources
python tools/specs.py validate recipes/models/glm/glm-5.3-flash/metax-glm-5.3-flash-w8a8.yaml --sources
python tools/specs.py validate recipes/measurements/metax-c500-gpu0-20261123.yaml --sources
python -m tools.hardware plan recipes/plans/hardware/metax.yaml
python -m tools.hardware inspect recipes/plans/hardware/metax.yaml --out experiments/runs/hardware/metax-next-inspect
python -m tools.hardware inspect-model --host metax --model /NFS_62/Models/GLM_Series/GLM-5.3-Flash-W8A8 --out experiments/runs/hardware/metax-next-model.json
```

按硬件计划指定设备与镜像，空闲时执行校准（拒绝被占用设备；创建并清理自己的隔离容器）：

```powershell
python -m tools.hardware run recipes/plans/hardware/metax.yaml --out experiments/runs/hardware/metax-next-calibration
python -m tools.hardware export experiments/runs/hardware/metax-next-calibration --out experiments/runs/hardware/metax-next-recipes
```

原始输出路径须为新文件，避免覆盖证据。采集器仅读取元数据；校准器会执行短时 GPU 运算。新增实机配方使用 [models/inspected](../schemas/templates/models/inspected.yaml)、[hardware/inspected](../schemas/templates/hardware/inspected.yaml)、[hardware/measurement](../schemas/templates/hardware/measurement.yaml) 三个模板。校验通过表示结构与证据一致性检查通过，正式部署还需解决上述冻结阻塞项。

## 首版资料录入（历史批次）

这里是用户提供资料的结构化版本，配方语言为 `0.2.0`，首版配方版本为 `1.0.0`。数值来自仓库中的原图、报告和项目管理表；未通过外部网站补齐硬件参数或模型身份，也没有执行 GPU 复测。

共 **140 个配方**：12 个模型、9 个硬件描述、22 个 SLA、28 个 Workload、7 个测量协议、3 个 Runtime、40 个 TestCase、1 个 Study、11 个来源记录和 7 组报告结果。Schema/模板/操作方法见 [规约入口](../schemas/README.md)。

## 三类核心配方

| 类别 | 首版范围 |
|---|---|
| [models/](models/) | 行业表中的 DeepSeek-V4.1-Flash、DeepSeek-V4-Pro、GLM-5.3、Kimi-K3、Qwen3.8-27B、Qwen3.8-2.4T-A95B；项目 DeepSeek-V4 Flash W8A8；GLM-5.3 flash INT8/FP8/INT4；报告 GLM-5.2 W8A8、Kimi-K2.7-Code W4A16 |
| [hardware/](hardware/) | C500、BW1000、L20、H20；只知型号的 BW1100/BW1301/H20-141G；型号待确认的 FP8 超节点；待填写实际节点清单的 BW1000 集群 |
| [slas/](slas/) | 行业表 4 组共享 SLA；DeepSeek 合同序号 5–8 的 Prefill/Decode 共 8 组；赤兔报告 5 个 Case 的 Prefill/Decode 共 10 组 |

40 个 Case = 行业 16 个 + DeepSeek 合同 8 个 + 赤兔报告 10 个 + GLM P/D 诊断 6 个。行业 SLA 可复用于多个模型；测试 Case 保留模型引用和 P0 优先级。首版 Study 为 [deepseek-bw1000-contract](studies/deepseek-bw1000-contract.yaml)。

## 来源和录入覆盖

| 来源记录 | 已结构化内容 | 保留的限制 |
|---|---|---|
| [行业 SLA 截图](sources/source-industry-sla.yaml) | 6 个完整模型行、16 个模型/长度组合，TTFT/TPOT、P0 | 底部裁切行、右侧不可读列不补齐；K、统计量及比较符未明确 |
| [GLM 汇总截图](sources/source-glm53-summary.yaml) | [27 个比较单元格](observations/glm53-h20-relative-summary.yaml)，含灰色“不支持”和黄色“待补充” | 相对 H20 百分比不是自身优化收益；跨 Case 汇总规则未知 |
| [GLM Prefill 截图](sources/source-glm53-prefill.yaml) | [75 行](observations/glm53-prefill-matrix.yaml)，5 平台×15 负载点，吞吐、平均 TTFT、缓存命中和比较比例 | 部分镜像/表头截断；超节点具体型号不明；IFB 与 PD 配置不同 |
| [Decode 上半图](sources/source-glm53-decode-a.yaml)、[续图](sources/source-glm53-decode-b.yaml) | [354 行](observations/glm53-decode-visible-series.yaml)，6 平台×59 可见负载点；RPS、生成吞吐、平均 TPOT；其中 40 行保留原表空白 | 辅助百分比列未重复转录；右侧无表头裁切列与不可见的 128K/bs32 不猜测 |
| [C500 规格截图](sources/source-metax-c500.yaml) | 算力、显存、带宽、板卡功耗、视频、形态、PCI ID、PCIe、VBIOS、MetaXLink | 原图 `384 GB（双向）` 缺时间单位，保留原文，不写成 GB/s |
| [三芯片对比图](sources/source-chip-comparison.yaml) | BW1000/L20/H20 的 FP16 算力和带宽 | 不从型号推导显存容量，不声称规格已实测 |
| [DeepSeek 项目表](sources/source-deepseek-project.yaml) | 合同 5–8、P/D 方法、框架标签、RLC 参数、[6 项优化记录](observations/deepseek-optimization-claims.yaml) | 缓存与条件提升比例冲突；不是合同原件；历史收益不相加 |
| [赤兔技术报告](sources/source-bw1000-report.yaml) | 5 Case 的目标、方法、[10 行最终 P/D 结果](observations/chitu-final-phase-results.yaml)、[4 行质量分数](observations/chitu-quality-results.yaml)、[冲突总结值](observations/chitu-kimi-conflicting-summary.yaml) | 逐算子微基准/逐页优化过程未全部结构化；部分基线身份和卡数口径不明确 |
| [设计 V1](sources/source-design-v1.yaml)、[设计 V2](sources/source-design-v2.yaml) | 文件哈希和架构依据登记 | 作为设计来源，不从设计示例制造合同约束或测量数据 |

结果表共 477 行。表格 `locator` 可定位原页、原行或负载点；每个来源记录固定原文件 SHA-256。`extraction.omissions` 和 `coverage` 明确未录入范围；`complete_visible` 仅指可读且约定录入的表格内容，并不表示恢复了被遮挡的字段。

## 首版必须保留的待确认事项

- **行业需求**：`TTFT 1–3s / 10–30s` 是区间；没有说明均值、分位数和严格比较符，不能擅自固化为 p95 或区间上限。
- **长度单位**：行业表和 DeepSeek 表未定义 K=1000 还是 1024，保留标签且 `tokens: null`。赤兔报告明确了换算；GLM 负载结合输入长度数值展开。Prefill 输出 1 token 与业务原始输出长度分别记录。
- **DeepSeek 缓存**：1.3 的 NO prefix cache、1.4 Decode 启用 cache、3.5 的 99% 命中是不同描述，当前标为冲突；不能默默挑选其中一个。
- **DeepSeek 条件目标**：开箱达标后的额外提升出现 25% 与 20% 两种表述，尚未固化成统一门槛。
- **归一化**：“折合 8 卡”是 QPS 口径；真实节点、NIC、卡清单未知。赤兔报告“平均到每机”也不能直接改成每卡。
- **模型与软件**：显示名称、W8A8/W4A16 标签和分支版本不等同冻结后的权重、tokenizer、量化实现、源码 commit 或镜像 digest。
- **质量验收**：报告三次取最高不等同均值；“下降不超过 5%”缺相对比例/百分点约定以及评测器、评测集版本。
- **证据冲突**：Kimi 长输入 Prefill 分项表给出 126%，总结出现 108.40%，分别保留；不人为选择或平均。

这些配方可以查询、组合、校验和解析，但首版真实 Study 会被阻止冻结。补齐来源并解决问题时发布新的配方版本，保留初版资料所表达的事实与不确定性。
