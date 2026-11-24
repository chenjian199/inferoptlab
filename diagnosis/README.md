# 第二步：归因

本模块将第一步归档变成**可核验观察、可证伪假设和下一项测量需求**。当前实现可离线运行，不连接 SSH、不加载模型、不启动 profiler，也不从端到端曲线自动认定某个 kernel 是根因。

第三步见 [专项分析模块](../analysis/README.md)，三个阶段的整体设计与现有资料映射见 [阶段设计](../docs/diagnosis-analysis.md)。这里的“第二步”是用户工作流编号，不是旧路线图中负责配置搜索的 M2。

## 运行当前真实示例

在仓库根目录执行，依赖与 `schemas/requirements.txt` 相同，不需要 PyTorch：

```powershell
python -m diagnosis plan recipes/plans/diagnosis/qwen-metax.yaml
python -m diagnosis run recipes/plans/diagnosis/qwen-metax.yaml --out experiments/runs/diagnosis/my-qwen
python tools/specs.py validate experiments/runs/diagnosis/my-qwen/diagnosis.yaml
```

输出目录必须不存在。已生成的实际例子是 `experiments/runs/diagnosis/qwen-metax-v1/`，包含 `diagnosis.yaml` 和 `report.md`。归因任务不会覆盖第一步原始数据。

## 模块划分

| 文件 | 职责 | 失败时的行为 |
|---|---|---|
| `contracts.py` | 结构、引用、内容摘要、trace 时间边界校验 | 拒绝非法对象 |
| `evidence.py` | 封存清单、运行/快照/数据集关联及原始指标复算 | 篡改、错配或缺失必需制品时报错 |
| `engine.py` | 按单变量分组、描述性比较、规则生成假设 | 无匹配数据就不比较；无根因证据就保留未知 |
| `report.py` | 人类可读报告 | 保留失败与限制，不只展示好结果 |
| `cli.py` | `seal / plan / run` | 只做本地文件处理 |

## 输入规约

`DiagnosisPlan` 位于 `recipes/plans/diagnosis/`，纳入 `tools/specs.py validate`：

- `study_ref`：精确 Study 身份。读取 benchmark 内嵌快照后，核对该 Study 的实际内容，不能只比较名字。
- `batches[]`：批次目录、封存清单路径、清单 SHA-256。清单覆盖使用到的原始请求、汇总、环境、请求集和解析后配置。
- `method_refs[]`：第三步方法目录，决定可建议的测量方法；没有方法时不会编造实验实现。
- `calibration_refs[]`：真实 `HardwareMeasurement`，仍需目标设备、运行库、dtype、shape、布局与计时匹配。
- `historical_refs[]`：来自原表格/图片/报告的 `ReportedMeasurements`。用于研究线索，不进入实测因果证据。
- `policy`：样本门槛与观察触发条件。当前默认单点至少 32 请求、至少 3 个独立重复；这只是配置的证据下限，不是 p99 统计充分性保证。

新批次可先封存：

```powershell
python -m diagnosis seal experiments/runs/benchmark/YOUR_BATCH --out experiments/runs/benchmark/YOUR_BATCH/sha256.json
```

命令要求批次处于终态，生成清单并打印其 SHA-256。清单目录必须包含批次目录。将输出路径和摘要填入新 DiagnosisPlan 后再运行。封存证明的是“此后未改变”，不能把人为生成的数据认证为真实测量。

模板：`schemas/templates/diagnosis/plan.yaml`。除 ID/title 外，可覆盖 Study、批次、方法、校准、历史引用和 policy：

```powershell
python tools/specs.py instantiate schemas/templates/diagnosis/plan.yaml --params examples/parameters/diagnosis-plan.yaml --out experiments/runs/new-diagnosis.yaml
```

示例参数继承 Qwen 数据。新模型必须同时更换 Study 和输入批次，确认后放入 `recipes/plans/diagnosis/`；不能只改名称。

## 处理顺序

1. 校验 Plan、引用和路径，检查封存清单摘要以及每个文件摘要。
2. 读取批次内嵌 `ResolvedBenchmark`，核对 ledger、Trial、Run、Deployment、Case、Workload、Protocol。
3. 核对请求集清单、tokenizer 指纹及 run 中的比较指纹。
4. 从 AIPerf `profile_export.jsonl` 重新计算计数、长度、TTFT/TPOT、E2E 与吞吐，核对保存的统计；跨 Python 版本只允许 `1e-12` 的浮点末位误差。
5. 保留失败、不完整、未验证环境的 run，明确排除原因。它们不进入曲线归因。
6. 建立单变量分组：输入长度或并发。不同输出长度、模型、部署、运行库、服务配置、协议、缓存与生成规则不会混为同一组。
7. 形成描述性比较，按独立 `repetition` 计数，不能把 attempt 重试当重复；重复 Run 和重复重复号均拒绝。
8. 应用有限规则，将观察映射为一个或多个解释，附替代解释、缺失证据、证伪条件和专项引用。
9. 输出报告、依赖快照和摘要。历史材料缺失附件会显示在 context 中，不会悄悄变成已验证来源。

## 比较边界

输入长度变化时，请求文本必然变化；程序固定生成方式、seed、输出长度、tokenizer、cache、协议和并发，明确标注这一内容差异。并发变化时则要求同输入长度和同请求集 SHA-256。运行配置以归档的实际服务配置参与分组。

目前不支持“任意允许字段路径”比较，避免一次放行多处变化。跨框架、跨精度、跨 GPU 数或配置搜索候选的收益比较，后续应引入明确的实验自变量与独立验收策略。

每个点有多个独立重复时，对 run 的均值等权汇总；不会把所有请求混池后制造很大的样本量。当前不执行显著性检验、置信区间或容量拟合。

触发规则：

| 规则 | 当前处理 | 不作出的结论 |
|---|---|---|
| 长输入 TTFT 比值 ≥ 1.5 | 建议请求时序、注意力、GEMM、调度专项 | “存在 attention 性能 bug” |
| 并发扩展效率 < 0.8 | 建议队列、客户端、调度与内存专项 | “GPU 利用率不足” |
| 只有 E2E 指标 | 生成阶段边界缺失假设 | 纯 prefill/纯 decode 时长或热点占比 |
| 样本/重复不足 | 标注观察，不满足证据门槛 | 显著收益或尾延迟合格 |

阈值可在 Plan 中改，但只是实验分流规则，不是 SLA 或异常的普适定义。

## 输出规约

`DiagnosisReport` 包含：

- `artifacts`：使用到的文件路径、摘要和角色。
- `catalog_snapshot`：Plan 及依赖的完整版本化对象，避免方法卡修改后悄悄改变旧报告含义。
- `runs`：合格/排除状态、原因、原始计数、指标和模型/硬件/运行时作用域。
- `comparisons`：固定维度、前后 Run、绝对值、比值、样本门槛和局限。
- `hypotheses`：观察、可能机制、替代解释、证据 ID、缺失证据、专项引用和证伪条件。
- `unexplained`：未解释问题，不能因为未命中规则而丢弃。
- `context`：历史数据/校准及来源问题。
- `content_sha256`：报告内容摘要。

首版总体状态只有 `needs_evidence / no_valid_runs`。假设不会自动提升为“已确认根因”，预计收益保持 `null`，不生成貌似精确的收益排名。

## 当前真实结果

Qwen 单卡、eager、小样本数据给出两个可比较方向：

- 输入 1024→8192、输出固定 32、并发 1：TTFT 40.90→218.48 ms，约 5.34 倍；TPOT 23.758→23.750 ms，基本不变。需要拆分排队、host 和真实 prefill 设备时间；更多输入带来的正常计算增长也能解释此现象。
- 输入 1024、输出 32，并发 1→2：输出吞吐 41.07→75.48 tokens/s，约 1.84 倍，扩展效率约 0.919。没有触发默认 0.8 的低扩展规则，也不能推断更高并发已经具备足够容量。

128/16 的 smoke 因输出长度不同，不参与上述比较。每点仅 4 请求、1 次重复，所有比较均标为不满足配置的样本门槛。
