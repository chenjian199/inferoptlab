# GLM Flash：八卡 C500 的 Prefill / Decode 扫描

本次把实际配方与执行代码分离，并实现闭环请求倍率与缓存重放。下列 GLM 配置引用已采集的模型、八卡清单和镜像包信息，但尚未在 GLM 上执行。当前主机仍可能被其他服务占用，不能把计划通过校验解释成设备空闲或模型加载已经验证。

## 文件关系

```text
schemas/definitions/ + schemas/templates/      标准和创建方式
                 ↓ 校验
recipes/plans/benchmark/glm53-flash-*.yaml      选择 Study、部署和场景，限定预算
  ├── studies/glm53-flash-c500-*.yaml          模型、硬件、Runtime、Case 范围
  ├── deployments/glm53-flash/c500/sglang/     TP/PP/EP、分块、设备、服务方式
  └── scenarios/glm53-flash-*.yaml            Case 引用、请求集目录
        └── test-cases/glm53-flash-*.yaml      模型 + Workload + Protocol + SLA
              ├── workloads/                 长度、并发、请求倍率、种子、缓存要求
              └── protocols/                 计时口径、预热、重复、缓存填充规则
                 ↓ prepare / plan / run
experiments/datasets/ → experiments/runs/benchmark/<batch>/
                 ↓ 原生指标复算、完整证据校验
experiments/records/ → index.json → baselines/
```

索引中的 `recipe_snapshot` 保存依赖闭包，即使以后源码配方升级，旧结果仍能恢复原配置。

## 参数在哪里修改

| 参数 | 首版值 | 位置 |
|---|---|---|
| 模型 | 已采集的 `cluster-glm53-flash-w8a8` | Study 与 Deployment 的 `model_ref` |
| 硬件 | `metax-four-node-inventory-metax-60-host` 的 8 张 C500 | `hardware_ref`、Deployment 的 `devices` |
| 并行候选 | TP8/PP1/EP8；TP4/PP2/EP4；DP1 | `recipes/deployments/glm53-flash/c500/sglang/` 的 `parallelism` |
| 分块 | TP8 候选分别 4096、8192；TP4/PP2 候选 4096 | `scheduling.chunked_prefill_tokens` |
| 并发 | `[1,2,4,8,16,32,64,128]` | `recipes/workloads/glm53-flash-*.yaml` 的 `arrival.load_points` |
| 请求数 | `count: null`，`count_multiplier: 4` | Workload 的 `requests` |
| 输入 | short=4096，long=8192，包含聊天模板 | Workload 的 `input.tokens` |
| P 输出 | 1 token | Prefill Workload 的 `output.tokens` |
| D 输出 | 128 tokens | Decode Workload 的 `output.tokens` |
| 重复与预热 | 3 轮；每次 4 个独立预热请求 | `recipes/protocols/glm53-flash-*.yaml` 的 `execution` |
| D 缓存命中 | 每请求目标 1.0；最多 0 个未命中 token | Workload 的 `cache.target_hit_ratio`；Protocol 的 `cache_replay.max_uncached_tokens_per_request` |
| 填充输出 | 1 token | Protocol 的 `cache_replay.fill_output_tokens` |
| 服务缓存开关 | P=false；D=true | Deployment 的 `prefix_cache` |

3 个部署 × 2 个长度 × 8 个并发 × 3 轮 = **每阶段 144 个 Run，P+D 共 288 个**。EP 共享 TP ranks，不再乘 EP 计算卡数。TP4/PP2/EP4 是待验证候选，不能假设厂商 GLM loader 已支持 PP 或特定 EP 组合。计划使用 `failure_policy: stop`，遇到无效或失败配置保留数据并停止后续发送。

并发 1、32、128 时分别发送 4、128、512 个正式请求。`count_multiplier: 3` 则变成 3、96、384；倍率必须为正整数，只支持 `closed_loop` + `concurrency`，不可与固定 `count` 同时生效。不同并发点有独立请求集 `.../c1/`、`.../c32/`、`.../c128/`。总请求数不包含预热和缓存填充；D 还会为同一请求集完整填充一次。倍率决定样本量，不保证长时间稳态，低并发点的小样本不能直接用于可靠 p99 验收。

short/long 是新的探索长度，未将历史 64K 等合同要求改成 8K。需要扩大上下文时新增 Workload/Case/Scene 版本，并重新准备请求集、核验服务上下文和缓存容量。

## Prefill 流程

关闭 prefix cache → 核验设备、服务配置和 tokenizer → 独立预热 → 按指定并发发送正式请求，每请求只输出 1 token → 统计 TTFT、输入长度、请求吞吐、成功率和失败分母。

单 token 不计算 TPOT/ITL。TTFT 仍包含客户端提交、排队、调度及首 token 返回，不是孤立 Prefill kernel 时间。

## Decode 缓存重放

1. 在本工具自己管理的 SGLang 服务上开启 prefix cache 与 `--enable-cache-report`，核验设备和服务配置；无法确认则禁止重放。
2. 完成独立预热后，调用 `/flush_cache`，必须返回成功。已有外部服务不允许被本流程清空缓存。
3. AIPerf 使用归档的 **同一份 `requests.jsonl`** 完整运行，输出固定 1 token。填充的请求数、成功状态、实际输入/输出 token 必须匹配。
4. 不再清空缓存，正式 AIPerf 进程重放该文件，保持相同 tokenizer、输入顺序、并发和种子，输出 128 tokens。
5. 每个正式请求读取 `usage_prompt_cache_read_tokens`，计算命中比例与残余输入 tokens。缺失、重复、失败、token 长度不符或任一请求未满足要求，结果无效。填充过程和正式结果分别归档，填充耗时不混入正式吞吐。
6. 每个 Run（包括每个并发点和重复轮次）重新清空并填充，避免上一个点的缓存状态影响下一个点。

实现见 `benchmark/load/cache.py`；离线重算、归因和实验登记都会重新校验填充与重放证据，不只相信结果中的一个 passed 字段。P/D 使用相同 seed、长度、请求数与 tokenizer 时输入文本相同，`manifest.input_content_sha256` 可独立验证；P/D 的 session ID 不同，因此请求文件整体哈希可以不同。D 的填充与正式测量则使用逐字节相同的请求文件。

当前严格要求 100% 命中。后端可能因最后 token、页边界、KV 容量、缓存驱逐、混合注意力状态或模型实现而无法达到；届时会暴露每请求残余 token，不能默默降为 99%。如实验目标允许残余，需通过新的协议/Workload 版本明确阈值并说明依据。

结果标为 `measurement_scope: cached_request_decode`、`strict_device_decode: false`。主要观察 TPOT 和输出吞吐；TTFT 与客户端窗口仍存在。严格的设备侧 Decode 时间、完全排除调度和残余 Prefill，需要后续 profiler/引擎计时适配。

## 本地预览与测试机执行

无需 GPU 的预览：

```powershell
python tools/specs.py validate
python -m benchmark load plan recipes/plans/benchmark/glm53-flash-prefill.yaml
python -m benchmark load plan recipes/plans/benchmark/glm53-flash-decode.yaml
```

准备好空闲测试节点和隔离运行环境之后，在该 Linux 环境安装 AIPerf 0.12.0。Runtime 引用的 Docker image ID 来自 metax-60 的既有采集，执行器不会自动拉取或启动该镜像；受管 SGLang 通过当前 Python 环境启动。需要先核验模型 loader、真实服务参数、依赖版本和设备映射，并记录所用容器身份。不能直接将 metax-60 的设备 ID 和路径用于旧 `metax`。

```bash
python -m benchmark load prepare recipes/plans/benchmark/glm53-flash-prefill.yaml --tokenizer /mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8
python -m benchmark load prepare recipes/plans/benchmark/glm53-flash-decode.yaml --tokenizer /mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8
# 先在新版本计划中缩小到一个部署/场景/并发，完成实际资格验证后再跑全矩阵
python -m benchmark load run recipes/plans/benchmark/glm53-flash-prefill.yaml
python -m benchmark load run recipes/plans/benchmark/glm53-flash-decode.yaml
```

`prepare` 不覆盖已有数据。正式冻结时，将每点 manifest 中 `files.requests.jsonl.sha256` 填入 `requests.request_set_sha256_by_concurrency`（例如 `"1": <sha>`，直到 `"128": <sha>`），并补齐全部来源、权重和 Runtime 阻塞项；固定请求数模式继续使用单个 `request_set_sha256`。

`--input` 目前只支持单场景、恰好匹配该点请求数的文本文件；多并发倍率扫描默认使用确定性合成数据，尚未提供一次导入语料池再自动切片的 CLI。第二步归因仍严格要求请求集可比，不会把不同倍率请求集合自动视为受控因果对照；扫描点可通过实验索引和批次报告查看。

官方依据：[AIPerf 0.12 的服务商缓存字段](https://docs.nvidia.com/aiperf/v0.12.0/reference/vendor-usage-field-reference)、[缓存 usage 指标实现](https://github.com/ai-dynamo/aiperf/blob/v0.12.0/src/aiperf/metrics/types/usage_cache_metrics.py)、[SGLang v0.5.14 HTTP 缓存清理接口](https://github.com/sgl-project/sglang/blob/v0.5.14/python/sglang/srt/entrypoints/http_server.py)。厂商分支的实际行为仍需真机资格验证。
