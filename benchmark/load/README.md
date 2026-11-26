# 服务压测：AIPerf

这是 [benchmark 三模块](../README.md) 中的压测模块，入口为 `python -m benchmark load ...`。

完整上下文缓存命中的 D 端续接测试见 [Cached Decode 流程](CACHED-DECODE.md)。该入口验证独立上下文、DP 固定路由和单 token 调度，并逐请求拒绝缓存未命中的结果。

本模块实现“版本化规约 → 请求集 → 部署/连接服务 → AIPerf 测量 → 结果归档 → SLA 与报告”。离线规约和编排工具可以在 Windows 使用；真实 AIPerf 执行在 Linux 测试机上进行。支持管理 SGLang 进程、MetaX vLLM Docker 部署，或连接已有 SGLang/vLLM 服务。模型和环境的未确认字段仍阻塞正式冻结；小模型流程验证的范围与结果见 [集群检查记录](../../docs/cluster-intake-20261123.md)。

GLM Flash 八卡 C500 当前使用六种配置的完整正式扫描，负载点和手动增加部署的说明见 [扫描计划表](../../recipes/plans/benchmark/glm53-vllm/README.md)。`qualify` 生成绑定配置哈希的启动记录，`run --qualification` 检查记录并复用原有请求集、AIPerf、指标和归档链路。该完整计划要求所有配置通过资格检查，不使用候选筛选步骤。

## 从这里开始

先在仓库根目录预览，不需要 GPU、AIPerf 或模型权重：

```powershell
python -m pip install -r schemas/requirements.txt
python tools/specs.py validate
python -m benchmark load plan recipes/plans/benchmark/smoke.yaml
python -m benchmark load plan recipes/plans/benchmark/compare.yaml --out experiments/runs/benchmark/compare.draft.yaml
python -m unittest discover -s tests -v
```

`plan` 成功表示配置结构与引用合法。输出中的 `execution_issues` 是实际执行前必须补齐的配置；`formal_readiness_issue_count` 包括模型、环境等正式冻结要求，`source_issues` 单独报告当前原始附件的缺失或哈希不符。文件是否暂时在场不会改变草案内容哈希；正式冻结和正式执行必须核对原附件。草案预览不会启动服务或发送请求。`--out` 使用独占创建，重复生成请更换文件名。

现有原始附件若未放在 SourceDocument 指定位置，`python tools/specs.py validate --sources` 会失败。单元测试用临时合成来源测试哈希和冻结规则；原始附件的独立集成检查会明确跳过，不能将其解释为原文件已通过核验。

## 配置的归属

| 内容 | 位置 | 职责 |
|---|---|---|
| 模型、硬件、Runtime | `recipes/` | 保持单一身份、版本和指纹 |
| Workload、Protocol、Case、SLA、Study | `recipes/` | 定义测什么、如何计时与验收 |
| 场景 | `recipes/scenarios/` | 引用一个 Case，指定请求集目录 |
| 部署配方 | `recipes/deployments/<model>/<hardware>/<engine>/` | 并行、调度、设备映射、服务接入 |
| 测试计划 | `recipes/plans/benchmark/` | 选择场景和部署、设置预算、遥测、运行顺序 |
| 定义、模板、参数示例 | `schemas/definitions/`、`schemas/templates/`、`examples/parameters/` | 新配置也通过现有规约工具创建和校验 |

目录中的 YAML 都使用 `{id, version}` 精确引用，文件名不参与身份判断。`tools/specs.py` 统一递归扫描根目录 `recipes/` 并检查全局唯一 ID。参数文件和结果不要放到配置目录中。所有实际数据由 [experiments/](../../experiments/README.md) 管理，`benchmark/` 仅保留实现和使用说明。

新增对象为 `DeploymentSpec`、`BenchmarkScenario`、`BenchmarkPlan`、`ResolvedBenchmark`、`MeasurementBundle`。规约版本保持 `0.2.0`，新增定义不改写原始来源配方。测量协议的 `execution.warmup_request_count` 是可选的结构扩展，第一版执行器要求明确填写。

## 首版计划与场景

| 计划 | 部署方式 | 场景 | 实际 Run 数 |
|---|---|---|---:|
| `smoke.yaml` | 连接已有服务 | 128 输入 / 16 输出，4 请求，并发 1，一轮 | 1 |
| `attached.yaml` | 连接已有服务 | 短、长输入 | 18 |
| `baseline.yaml` | 管理一份 SGLang 部署 | 短、长输入 | 18 |
| `compare.yaml` | baseline / chunk4096 / chunk8192 | 短、长输入 | 54 |
| `parallel.yaml` | TP8/PP1/EP8 与 TP4/PP2/EP4 | 短、长输入 | 36 |
| `qwen-metax-pipeline-plan.yaml` | MetaX 单卡 Qwen3-0.6B，已有 vLLM 服务 | 128/16、1024/32（并发 1、2）、8192/32 | 4 |

短输入为 **4096 tokens**，长输入为 **65536 tokens**；都生成 **1024 tokens**。每点 32 个正式请求，并发 `[1, 4, 16]`，重复三轮，每轮另用四个不同的请求预热。这是用于搭建流程的探索配置，样本量不代表 p99 已具备验收置信度；容量附近和过载点应在第一轮之后按预算调整。

这些是新建的诊断 Case，未把资料中的 `4K`、`50K` 或 Decode 缓存冲突擅自转换成确定合同条件。现有合同 Case 保持原样。新增其他模型时，创建对应模型的 Case/Study 和部署引用，不能将 DeepSeek 的 Case 直接用于 GLM。

当前支持聚合部署、单轮文本聊天、固定输出、greedy、闭环并发，以及 `full_request`、`prefill_one_token` 和受管 SGLang 的 `prefix_reuse_decode`。请求数可固定，也可按并发倍率展开。开环 QPS、trace replay、fakePrefill、P/D 分离部署与多机部署仍显式拒绝。P/D 阶段分别测试不等于 P/D 分离部署。

新增 [GLM Flash 八卡 C500 P/D 扫描](../../docs/benchmark-cache-replay.md)：请求数为并发 × 4，P 输出 1 token，D 使用同一请求文件先填充再重放；并发为 `[1,2,4,8,16,32,64,128]`，每阶段 144 个候选 Run。具体倍率、协议、并行配置与完整执行步骤见该文档。

## 连接已经启动的服务

在 Linux 测试环境安装固定版本的工具：

```bash
python -m pip install -r benchmark/requirements.txt
```

这安装 `aiperf==0.12.0`。SGLang、模型权重和设备驱动应由测试环境按 Runtime 配方准备；模块不会自动下载安装大型权重或改变驱动。

修改 `recipes/deployments/deepseek-v4-flash/bw1000/sglang/attached.yaml`：

- `serving.url`：OpenAI 兼容服务的基础 URL，例如 `http://127.0.0.1:8000`，不要带 `/v1`。
- `serving.served_model`：`/v1/models` 中实际的模型 ID。
- `serving.tokenizer_path`：测试机上的本地 tokenizer 目录；需包含相同聊天模板。
- `parallelism`、`scheduling`：待测服务的实际配置。
- `devices`：实际 rank、唯一设备 ID 与可见设备索引；与 HardwareSpec 的设备清单对应。
- `serving.device_visibility_env`：NVIDIA 用 `CUDA_VISIBLE_DEVICES`；海光环境按实际运行库确认 `HIP_VISIBLE_DEVICES` 或 `ROCR_VISIBLE_DEVICES`。

服务应关闭 prefix cache，采用单 token 流式返回，并开放 `/get_server_info` 供配置回读；SGLang 的 Prometheus 指标需要启用 `--enable-metrics`。配置回读缺失或不符时，探索测试保留数据并标记 `unverified`，不会成为已验证的可比较结果。

vLLM 的 Runtime `engine` 可为 `vllm` 或 `vllm-metax`，目前只支持 `external`。适配器回读 `/server_info?config_format=json`，只存储 `vllm_config`，不归档服务器环境变量；该开发接口需要独立启用，本次服务只监听 loopback。MetaX 使用 `MACA_VISIBLE_DEVICES`，客户端通过 `mx-smi -j` 和 `--show-hwinfo` 核对板卡序列号、BDF 与内核驱动；采集容器需要能够读取管理设备。`management_runtime_version` 记录采集进程自己的 MACA 用户态库，不能代替服务容器 Runtime 或宿主机安装版本。该探针验证设备身份，不替代硬件健康、HBM/互联性能或 GPU 遥测验证。

Qwen 计划有独立 Case/Study/模型引用，短长输入长度是小模型流程验证专用。请求长度计算显式要求 `return_dict=True`，只统计 `input_ids`。不要用这些小样本替代 GLM 的正式性能与 SLA 测量。

连接远端 URL 时，本地设备探测只代表压测客户端；远端设备清单需要后续 Worker/平台探测证据，当前会标记未验证。

准备请求集并执行：

```bash
python -m benchmark load prepare recipes/plans/benchmark/smoke.yaml --tokenizer /absolute/path/to/tokenizer
python -m benchmark load run recipes/plans/benchmark/smoke.yaml

python -m benchmark load prepare recipes/plans/benchmark/attached.yaml --tokenizer /absolute/path/to/tokenizer
python -m benchmark load run recipes/plans/benchmark/attached.yaml
```

`prepare` 使用本地 tokenizer，不下载模型、不执行 tokenizer 的远程代码。它核对 **聊天模板展开后** 的输入 token 数，保存请求文件、独立预热文件、稳定 session ID 和 tokenizer 文件指纹。某些 tokenizer 无法用内置合成器精确构造目标长度时，会报错；可为单场景计划通过 `--input <text.jsonl>` 导入已经准备的文本，仍需精确分词校验。

已有请求集不覆盖。修改长度、种子、请求数或 tokenizer 后，需要使用新的场景/请求集目录。为正式冻结回填 `WorkloadSpec.requests.request_set_sha256` 时，使用请求集 `manifest.json` 中 `files.requests.jsonl.sha256`；不要将整个 manifest 的哈希填入该字段。

## 管理部署与切换配方

`baseline.yaml`、`chunk4096.yaml`、`chunk8192.yaml` 和 `tp4-pp2-ep4.yaml` 的 `serving.management` 为 `sglang`。除上面的字段外，还需填写：

- `serving.model_path`：测试机已准备好的模型路径。
- `devices`：完整设备映射。首版适配器要求单机、`dp=1`，每个 PP stage 包含 TP ranks；EP 共享这些 ranks，不能再乘一次 EP 计算卡数。
- Runtime 中的固定环境、版本和公共启动参数。

托管进程在当前 Python 环境启动，`serving.url` 必须为本机 HTTP 地址。模块先检查端口占用，只停止自己启动的进程组；已有外部服务不会被终止。不要在同一端口保留手动服务后直接运行托管计划。

配置支持 TP/PP/EP/DP 的表达，首版托管执行将 DP 限制为 1。TP4/PP2/EP4 是未验证候选；模型、框架版本和硬件必须实际支持它才能执行成功。PP 参数出现在 Schema 中不等于该模型已支持流水线并行。

`chunked_prefill_tokens` 对应 Prefill 分块，`kv_page_tokens` 对应 KV page，`max_running_requests` 对应服务调度上限。未填写的调度字段保留后端默认值，并归档服务端回读结果。

公共 `Runtime.launch_parameters` 和 `Deployment.backend_options` 都使用明确的 `--flag` 名称。相互重复或与并行/缓存/端口等受管字段冲突时拒绝执行，不静默覆盖。修改已被实验引用的配置时创建新版本。

```bash
python -m benchmark load plan recipes/plans/benchmark/compare.yaml
python -m benchmark load run recipes/plans/benchmark/compare.yaml
```

执行顺序按重复轮次交错部署，使用固定种子。一个部署内顺序跑场景和负载点；切换部署前回收受管进程。工作区租约阻止本模块同时抢占同一工作区的测试资源，它不是集群调度器，也无法替其他工作区预约机器。

## 采集与统计

AIPerf 命令固定工具版本、请求文件、顺序采样、随机种子、并发、输出策略、超时和导出级别。预热在单独进程和独立制品目录执行；正式命令的内置预热为零。客户端原始结果使用 `--export-level raw` 保存。

每个 Run 保存：

```text
experiments/runs/benchmark/<batch-id>/
  resolved.yaml                 # 完整配置引用闭包与矩阵
  datasets/                     # 本批次归档的固定请求集
  batch.json                    # 所有计划执行、跳过和失败状态
  report.md                     # 配方/场景/负载/重复逐行对比
  <run-id>/
    resolved.yaml               # 该次执行的展开配置和批次快照引用
    environment.json            # 环境探测、服务配置、声明的设备
    commands.json               # 实际启动与 AIPerf 参数数组
    run.json                    # 状态、时间、attempt、错误
    raw/aiperf/                 # AIPerf 原始制品
    raw/warmup/                 # 预热原始制品
    raw/cache-fill/             # Decode 请求集缓存填充原始制品
    cache-lifecycle.json         # 清空、填充状态与同一输入哈希
    cache-replay.json            # 逐请求缓存 token、残余 token、验真结果
    logs/
    requests.jsonl              # 包含失败和缺失项的请求清单
    summary.json                # MeasurementBundle
    sla.json                    # 性能 SLA 判定
    report.md
```

统计包括 TTFT、客户端 E2E、平均 TPOT、实际输入/输出 token 数、mean/p50/p90/p95/p99、成功率和吞吐。时延单位为 ms。TPOT 使用 `(request_latency - TTFT)/(actual_output_tokens - 1)`，单 token 输出记为不适用；没有逐 token 时间戳时不提供真实 ITL 分布。

计时跨度使用 AIPerf 的首个 `request_start_ns` 到最后 `request_end_ns`，包含有终态记录的失败和超时。延迟分位数使用成功请求，失败仍保留在固定请求集合分母；若请求缺失、时间戳不完整，吞吐和 goodput 记为空，不拿整个子进程耗时替代。长度不符、重复 ID、未知字段含义或缺失必需指标都会保留原因。

SLA 支持确定阈值、单位转换、case 统计量、请求级联合合格率和 goodput。缺少指标、未定阈值/比较符、不支持的统计人口或归一化方式会输出 `inconclusive`。质量和条件性提升要求仍需独立验收器；`sla.status=passed` 仅表示本次性能约束，`acceptance_status` 不会伪装成全 Study 已验收。

在计划的 `aiperf` 字段中填写 `server_metrics` 或 `gpu_telemetry` 的 HTTP(S) 端点。`required_telemetry` 可为 `none/server/gpu/both`；必需遥测缺失时结果不完整。硬件原始指标随 AIPerf 制品保存，首版统一汇总表主要覆盖客户端指标。NVIDIA 可用 DCGM；海光的采集接口仍需实际平台适配，不能把 NVIDIA 探测结果套到 BW1000。

`unverified`、`invalid`、`failed`、`completed_with_errors` 等状态保留在报告，不参与推荐排名。三轮结果逐行展示，不选最好一轮，不平均各轮 p95 充当总体 p95。

## 离线重算与正式冻结

```bash
python -m benchmark load analyze experiments/runs/benchmark/<batch-id>/<run-id> --out experiments/runs/reanalysis/<new-id>
python -m benchmark load report experiments/runs/benchmark/<batch-id>
python tools/specs.py validate experiments/runs/benchmark/<batch-id>/<run-id>/summary.json
```

重算核对原始数据哈希、批次快照、试验 ID 和请求集指纹，并继承采集/执行时已记录的有效性问题。重算不会生成新的 GPU 测量证据。

执行结束自动在 `experiments/records/` 登记逐 Run 完整记录，并重建查询索引。查询和基线命令见 [实验仓储说明](../../experiments/README.md)。旧批次可以手动登记；失败数据保留，但不会成为有效基线。

需要正式输入冻结时，创建 `mode: formal` 的计划，补齐模型、资源、Runtime、请求集、协议和来源问题，再执行：

```bash
python -m benchmark load plan <formal-plan.yaml> --freeze --out experiments/runs/benchmark/formal.frozen.yaml
python -m benchmark load run experiments/runs/benchmark/formal.frozen.yaml
```

`run` 拒绝以草案运行正式计划。冻结仍不替代现场环境验证或质量验收。当前附带的真实模型/硬件记录保持未验证状态，默认探索计划没有附加猜测的 SLA。

## 验证与参考

自动化覆盖配置引用、矩阵预算、快照篡改、固定数据、超时清理、失败分母、单位、联合 SLA、结果归档和离线重算。测试中的原生 AIPerf 格式样本、tokenizer 和进程结果都是合成 fixture，不能用于性能结论。真实资格测试还需要目标 Linux 主机、权重、tokenizer、设备清单和已验证 Runtime。

参考上一级 Dynamo 的 `recipes/qwen3.6-35b/run-all-benchmarks.sh`、`perf.yaml` 和 `components/src/dynamo/profiler/utils/aiperf.py`，以及 [AIPerf 自定义数据集](https://docs.nvidia.com/aiperf/v0.12.0/tutorials/datasets-inputs/custom-dataset-guide)、[命令选项](https://docs.nvidia.com/aiperf/v0.12.0/reference/command-line-options)、[硬件遥测](https://docs.nvidia.com/aiperf/v0.12.0/tutorials/metrics-analysis/gpu-telemetry-with-ai-perf)。本模块为独立适配实现，没有复制 Dynamo 的部署脚本。
