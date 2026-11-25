# GLM-5.3-Flash-W8A8 / C500 八卡正式扫描

当前入口是 [full-scan.yaml](full-scan.yaml)。六种配置使用同一套负载点、请求数和重复次数，完整执行矩阵，不设置粗筛、细筛或优胜者晋级。模型、硬件和 Runtime 继续引用已有规约。

`mode: formal` 已设置，执行器要求冻结后的配置快照。配方定义完成不代表已启动扫描或通过 SLA 验收；当前仍有模型、来源、SLA 口径和数据集指纹待补齐。可以先预览完整矩阵、准备数据和验证启动，正式 `run` 保留原有冻结检查。

## 六种配置与完整矩阵

| 形态 | TP | PP | DP | EP | 每个 DP 引擎 max_num_seqs | 部署文件 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A | 8 | 1 | 1 | 1（关闭 EP） | 128 | [a-tp8.yaml](../../../deployments/glm53-flash/c500/vllm/scan/a-tp8.yaml) |
| B | 8 | 1 | 1 | 8 | 128 | [b-tp8-ep8.yaml](../../../deployments/glm53-flash/c500/vllm/scan/b-tp8-ep8.yaml) |
| C | 4 | 1 | 2 | 8 | 64 | [c-tp4-dp2-ep8.yaml](../../../deployments/glm53-flash/c500/vllm/scan/c-tp4-dp2-ep8.yaml) |
| D | 2 | 1 | 4 | 8 | 32 | [d-tp2-dp4-ep8.yaml](../../../deployments/glm53-flash/c500/vllm/scan/d-tp2-dp4-ep8.yaml) |
| E | 1 | 1 | 8 | 8 | 16 | [e-tp1-dp8-ep8.yaml](../../../deployments/glm53-flash/c500/vllm/scan/e-tp1-dp8-ep8.yaml) |
| F：TP8 图执行 | 8 | 1 | 1 | 1（关闭 EP） | 128 | [f-tp8-graph.yaml](../../../deployments/glm53-flash/c500/vllm/scan/f-tp8-graph.yaml) |

E 是新增并行形态，尚未做真机资格检查。A—D、F 以前验证过的上下文设置与本轮不同，也需要重新验证；不能沿用原启动结论。A—E 是五种并行形态，F 与 A 使用相同并行形态并开启图执行，作为同等完整扫描的一组配置。

为了让每种配置执行相同长度组合，六份部署统一设置 `max_model_len: 147456`、`max_num_batched_tokens: 4096`、chunked prefill 开启、prefix caching 关闭、显存比例 0.90。A—E 设置 `--enforce-eager: true`，F 设置 `--enforce-eager: false`，并要求回读到实际启用的图模式和捕获尺寸；这不等同于启用 torch.compile。KV block 由后端选择并记录实际值。EP 共享 TP×DP ranks，不额外乘卡数；这些参数是可比较的固定起点，尚未证明性能最优。

| 场景 | 输入 token | 输出 token | 修改负载的文件 |
| --- | ---: | ---: | --- |
| P 4K | 4096 | 1 | [p-4k.yaml](../../../workloads/glm53-vllm/scan/p-4k.yaml) |
| P 64K | 65536 | 1 | [p-64k.yaml](../../../workloads/glm53-vllm/scan/p-64k.yaml) |
| P 128K | 131072 | 1 | [p-128k.yaml](../../../workloads/glm53-vllm/scan/p-128k.yaml) |
| E2E 16K/2K | 16384 | 2048 | [e2e-16k.yaml](../../../workloads/glm53-vllm/scan/e2e-16k.yaml) |
| E2E 64K/1K | 65536 | 1024 | [e2e-64k.yaml](../../../workloads/glm53-vllm/scan/e2e-64k.yaml) |
| E2E 128K/1K | 131072 | 1024 | [e2e-128k.yaml](../../../workloads/glm53-vllm/scan/e2e-128k.yaml) |

全部使用并发 `[1, 2, 4, 8, 16, 32, 64, 128]`，每点 3 轮：**6 × 6 × 8 × 3 = 864 个计时 Run**。这不包含启动探测与独立预热，也不是请求数量。重复轮内的部署顺序按种子打乱，各 workload 内按 `load_points` 顺序执行。

纯 D 尚未加入本次正式矩阵：历史 4096-token 重放只命中 3840 token，不能满足 100% 缓存命中；DP>1 的缓存路由也未验证。E2E 仍会报告 TPOT，但不标作独立纯 Decode 测量。PP>1 也未纳入当前后端的可执行形态。

## 手动修改并发、长度与请求数

**负载修改入口是 `recipes/workloads/glm53-vllm/scan/`，不用改 ModelSpec。** 一份 workload 供六种配置共同使用，所以同一个场景只需修改一次。

例如编辑 `e2e-16k.yaml` 中以下字段，其余字段保留：

```yaml
input:
  label: '8192'
  tokens: 8192
  k_multiplier: null
  origin: explicit_tokens
output:
  label: '1024'
  tokens: 1024
  k_multiplier: null
  origin: explicit_tokens
arrival:
  mode: closed_loop
  load_unit: concurrency
  load_points: [1, 4, 8, 16, 32, 48, 64, 96, 128]
requests:
  content: random_independent
  request_set_sha256: null
  seed: 20261123
  count: null
  count_multiplier: 4
  min_count: 200
```

- `arrival.load_points`：客户端并发点及其执行顺序，与部署的服务端在途序列上限分开设置。上例会加入 48、96 并发点。
- `input.tokens` / `output.tokens`：每个请求的固定实际 token 数；`label` 同步修改。P 协议的输出保持 1；要测多 token 输出，使用 E2E workload 和协议。
- `requests.count_multiplier`：请求倍率。保留 `min_count: 200` 时，`N=C×max(4,ceil(200/C))`；例如 C=16 时 N=208，C=128 时 N=512。若只需要 N=4C，删除 `min_count`，并保持 `count: null`。
- 重复次数在 [scan/p.yaml](../../../protocols/glm53-vllm/scan/p.yaml) 和 [scan/e2e.yaml](../../../protocols/glm53-vllm/scan/e2e.yaml) 的 `execution.repetitions`。预热为 `max(4,C)`，不计入上述 N。

**长度序列由多个 workload 组成。** 当前 `input.tokens`、`output.tokens` 是整数，不接受数组；也不会自动把输入长度数组与输出长度数组做笛卡尔积。计划 `scenario_refs` 中每一项关联一个明确的输入/输出组合，各组合可以有自己的并发序列。

调整已有长度：编辑对应 workload，再同步 `recipes/test-cases/glm53-vllm/scan/` 中该 case 的 `declared_context`。若新长度不再对应原 SLA，应改为匹配的 SLA 引用或 `sla_ref: null`，不能把 16K/2K 的约束自动用到 8K/1K。

增加一个长度组合：复制一组 workload、test-case、scenario，赋予新的唯一 `id`；case 引用新的 workload 和相应 P/E2E 协议，scenario 引用该 case 并使用独立 `dataset_dir`。将 case 加到 [研究规约](../../../studies/glm53-vllm-full-scan.yaml) 的 `case_refs`，将 scenario 加到 `full-scan.yaml` 的 `scenario_refs`。删除或调整组合顺序则修改 `scenario_refs`。

修改后还要检查：

1. 每份部署的 `scheduling.max_model_len >= input.tokens + output.tokens`。增大上下文或改部署参数，需要重新验证该部署；同一部署改负载也需检查已有资格覆盖的输入长度。
2. 重新生成请求集。已有数据集目录不会被覆盖，改动后使用新的 scenario `dataset_dir`，保留旧数据及对应结果。
3. 正式冻结前将每档 `manifest.json` 中 `files.requests.jsonl.sha256` 填入 workload 的 `requests.request_set_sha256_by_concurrency`，例如 `"16": <该档 SHA-256>`。改并发、长度、倍率或种子后重新生成，不复用旧指纹。
4. 用 `plan` 查看展开数量和阻塞项。总 Run 数不能超过 `budget.max_runs`；预算耗尽或遇到失败会保留已有结果并停止，不缩减样本后冒充完整扫描。

## 手动增加部署参数组合

以增加一个 TP8、token budget=8192 的配置为例，不需要修改扫描器代码：

1. 复制 `recipes/deployments/glm53-flash/c500/vllm/scan/a-tp8.yaml` 为同目录 `g-tp8-budget8192.yaml`。文件名可以自行选择，身份由内容中的 `id` 和 `version` 决定。
2. 将 `id` 改为 `glm53-vllm-scan-g-tp8-budget8192`，更新 `title`，将 `scheduling.max_num_batched_tokens` 改为 `8192`。模型、硬件、runtime 引用和八卡设备绑定保持一致。
3. 在 `full-scan.yaml` 的 `deployment_refs` 末尾添加：

   ```yaml
   - id: glm53-vllm-scan-g-tp8-budget8192
     version: 1.0.0
   ```

4. 将 `recipes/studies/glm53-vllm-full-scan.yaml` 的 `budget.max_candidates` 从 6 改为至少 7。上述默认负载下，矩阵会自动变为 `7×6×8×3=1008` 个 Run；不需要复制 workload 或 scenario。
5. 运行下面的校验和预览命令，使用新输出目录对完整计划重新 `qualify`，再冻结执行。新增配置不能引用旧配置的启动资格；原始资格文件不手改。

```bash
python tools/specs.py validate
python -m benchmark.load plan recipes/plans/benchmark/glm53-vllm/full-scan.yaml
```

常用部署字段对应关系：

| 想扫描的服务参数 | 修改字段 |
| --- | --- |
| TP / PP / DP / EP | `parallelism.tp / pp / dp / ep` |
| 服务上下文上限 | `scheduling.max_model_len` |
| 每个 DP 引擎在途序列上限 | `scheduling.max_running_requests` |
| vLLM chunked prefill 的调度 token 预算 | `scheduling.max_num_batched_tokens` |
| 是否开启 chunked prefill | `scheduling.enable_chunked_prefill` |
| 显存利用比例 | `backend_options.--gpu-memory-utilization` |
| eager / 图执行 | `backend_options.--enforce-eager`，false 为图执行候选 |
| KV block | `scheduling.kv_page_tokens`；null 表示后端选择 |

八卡形态必须满足 `TP×PP×DP=8`；EP 关闭时填 1，开启时等于 TP×DP。当前后端的 PP 支持范围仍需遵守，不能只因 YAML 合法就认为启动可行。服务调度字段不要同时写入 `backend_options`，否则会被冲突检查拒绝。vLLM 不使用 `chunked_prefill_tokens`，该字段保持 null。

模型结构、权重精度等字段仍由 ModelSpec 提供；改变模型或运行镜像是新的模型/环境实验，需同步 Study 引用，不能只改服务参数掩盖变化。

## 正式执行流程

从项目根目录运行。以下 `RUN_ID` 每次使用新值。当前只准备了配方，没有启动这轮 GPU 扫描。

```bash
PLAN=recipes/plans/benchmark/glm53-vllm/full-scan.yaml
RUN_ID=glm53-full-001
OUT=experiments/evidence/startup/$RUN_ID

python -m benchmark.load plan "$PLAN"
python -m benchmark.load qualify "$PLAN" --out "$OUT"
```

`qualify` 是必要的启动与 API 检查，不是性能筛选；六种配置均须通过。某一项失败时修正配方并重新验证，不自动选出子集执行。本轮 E 尚未验证，其显存容量与后端行为以实机结果为准。

使用已有独立 AIPerf 客户端准备请求集：

```bash
python tools/deployment/metax-vllm/run_scan.py \
  --client-root "$CLIENT_ROOT" --client-image "$CLIENT_IMAGE" \
  prepare "$PLAN"
```

`CLIENT_ROOT` 是包含客户端 venv 的目录，`CLIENT_IMAGE` 是该环境的固定镜像；完整项目副本需包含 `diagnosis/` 等结果登记依赖。模型路径和推理镜像从部署及 Runtime 引用读取。

补齐请求集指纹、模型/来源证据和 SLA 口径后，冻结并执行同一个完整计划：

```bash
FROZEN=experiments/plans/$RUN_ID.frozen.yaml
python -m benchmark.load plan "$PLAN" --freeze --out "$FROZEN"

python tools/deployment/metax-vllm/run_scan.py \
  --client-root "$CLIENT_ROOT" --client-image "$CLIENT_IMAGE" \
  run "$FROZEN" --qualification "$OUT/qualification.json"
```

当前 `--freeze` 仍会报告真实阻塞项，不应通过手填“已验证”状态绕过。行业 GLM-5.3 的 SLA 目前是 Flash 的参考，模型名称差异、阈值范围及统计口径尚未解决；case 仍保留 diagnostic 目的，不伪造合同验收依据。

每请求超时 3600 秒、每个 Run 上限 12 小时，整个计划上限 336 小时（14 天），允许最多 2000 个 Run 以便手动增减扫描点。它们是停止预算，不是预计耗时。低并发、长输出和至少 200 请求会显著增加运行时间；修改预算时同步 Study 的 `max_wall_hours`。

结果仍归档到 `experiments/runs/benchmark/`，保存完整引用快照、数据集、资格记录、命令、服务实际配置、AIPerf 原始输出、逐请求指标和 SLA 判定，并登记到实验索引。

## 历史验证

[2026-11-24 真机验证报告](../../../../experiments/evidence/metax-60-glm53-scan/20261124/README.md)保留旧配置的启动、缓存边界和 12 请求流程验证。旧 `00—08` 计划及 `screen/confirm` 配方是此前阶段设计记录，当前完整扫描不引用它们；历史快照和原始测量不改写。

当前分工：Model/Hardware/Runtime 定义固定对象与环境，Deployment 定义服务端参数，Workload 定义请求与并发，Protocol 定义测量方法，Scenario 关联 case 与请求集，Plan 组织完整矩阵。没有增加重复的模型参数或另一个扫描配置解析器。
