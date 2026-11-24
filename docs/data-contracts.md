# 数据契约与任务对象

本文件描述完整平台执行期契约。规约语言已实现为 **v0.2.0**；第一版 [benchmark](../benchmark/README.md) 补充 Deployment、测试计划/矩阵/快照及 MeasurementBundle，Run 以独立制品目录和状态文件记录。字段和可运行工具以 [schemas/README.md](../schemas/README.md) 为准。完整 Candidate 血缘、分布式调度与独立质量验收仍待实现。

## 1. 四个层级必须区分

| 对象 | 表示什么 | 例子 |
|---|---|---|
| Study | 一次完整优化目标及其固定比较协议 | 某模型在固定 8 卡资源下优化两类负载 |
| Candidate | 一套完整可部署的配置和代码组合 | 聚合 TP4 两副本、指定后端和一组补丁 |
| Trial | 针对候选的一项实验设计 | 冷缓存短输入、并发 32、无 profiler、重复 3 轮 |
| Run | Trial 的一次实际执行/重复 | 第 2 轮运行，使用某组设备与环境快照 |

同一 Candidate 可用于多个 workload 和 Trial；同一 Trial 有多个 Run。失败重试使用新的 attempt，不冒充新的独立统计重复。Candidate 可以有多个父候选，表达组合集成。

## 2. 通用字段

实验执行期持久化对象计划包含 `schema_version`、对象 ID、创建时间、关联 Study/环境/来源及内容指纹。v0.2.0 输入配方采用稳定的 ID、配方版本、来源和问题清单，解析快照不插入当前时间，以保持相同输入的确定性哈希。指纹来自规范化配置和内容 hash，不能使用 `latest`、可移动 tag 或文件路径代替内容身份。执行期时间使用 UTC 存储；计时使用单调时钟并记录边界。

`schema_version` 使用语义明确的版本；不兼容字段变更应升级版本并提供迁移。未知字段不能静默丢弃；v0.2.0 在 `extensions` 下使用带点的命名空间键，如 `source.platform_settings` 或 `vendor_x.feature`。

## 3. 核心对象

| 对象 | 必需内容 | 冻结/校验要求 |
|---|---|---|
| `StudySpec` | 模型、框架、资源、负载、目标、SLO、允许变更、预算、停止条件 | 执行前解析模板并冻结 |
| `EnvironmentSnapshot` | 设备、拓扑、驱动、运行时、框架/库/编译器、容器、模型/分词器身份 | 保存采集时间、缺失字段、实际版本 |
| `WorkloadSpec` | 请求来源、长度分布、到达模式、输出策略、缓存和会话状态 | 数据集/请求清单/分词器和 seed 固定 |
| `DeploymentSpec` | 模式、角色、进程、设备与通信组、KV 交接、实际后端 | 能力和资源合法，实测配置回读 |
| `CandidateSpec` | 完整配置、基础源码、补丁、构建信息、父链、适用范围 | 不可变，改动即新 ID |
| `TrialSpec` | 候选、负载、实验目的、计时协议、重复、顺序、评分版本 | 禁止测后修改评分规则 |
| `RunRecord` | 预约、实际命令、环境、时间、attempt、状态、日志、退出原因 | 原始失败不可覆盖 |
| `MeasurementBundle` | 请求级数据、资源遥测、trace、统计、单位、数据有效性 | 聚合可从原始数据重算 |
| `Hypothesis` | 现象、机制解释、支持证据、替代解释、反证、下一实验 | 记录事实和推断的界限 |
| `OptimizationTask` | 基线、目标、语义、输入、可编辑范围、开发验证、预算、回接点 | 生成前冻结，开发验证与正式验收分离 |
| `CandidateBundle` | patch/commit、构建、形状范围、开发结果、dev_claims、回退 | 导入时独立验证状态默认 unverified |
| `AcceptanceReport` | 质量、可比性、SLO、收益、稳定性、回归、判定与理由 | 使用独立测量；accepted/rejected/inconclusive |

辅助对象包括 `CapabilityReport`、`ResourceLease`、`WorkerJob`、`ArtifactRef`、`PredictionResult`、`UnexplainedIssue` 和 `MechanismCard`。不要把优化器产生的自然语言报告当作 MeasurementBundle。

## 4. 指标必须自带语义

每项标准指标包含：

```yaml
metric: client_ttft_ms
value: 123.4                 # 仅说明结构，非实测
unit: ms
scope: request
aggregation: p95
population: completed_requests
sample_count: 1000
measurement_boundary: client_submit_to_first_content_token
measurement_window_ref: window-001
evidence_kind: measured
source_run_ids: [run-001]
parser_version: REPLACE_EXACT_VERSION
validity: valid
```

必须将以下情况分开：

- `null + unsupported`：工具不能提供该测量。
- `null + missing`：应该有，但丢失了。
- `null + not_applicable`：例如输出只有一个 token 时，TPOT 无定义。
- `0 + valid`：实际值确实为零。

跨 GPU、跨 rank、跨流的时间不能未经消重累加为 E2E 时间。统计对象和分位数计算方式必须固定。原始指标无法映射时保留厂商字段并标记不可比较。

## 5. 可比性指纹

对每个比较集合生成 `comparison_contract_digest`。至少覆盖：模型/权重/分词器、质量策略、资源预算、负载清单和到达过程、缓存准备、输出规则、计时边界、评分协议、重复与停止规则。

环境和框架也保存完整指纹，但允许 Study 明确把其中某项声明为自变量。例如框架版本比较需要显式登记两个版本；不能因为版本不同而拒绝一个本来就是比较版本的 Study。代码补丁实验则要求除授权改动外其他关键条件一致。

比较器返回 `comparable`、`incomparable` 或 `insufficient_evidence` 及逐字段原因。不同协议的记录可以并排展示，但不能直接计算“本次优化提升”。

## 6. 资源与部署表示

资源预算需要区分分配总量和实际活动量。固定 8 卡预算时，即使一个候选仅激活 4 卡，每卡归一化若采用分配口径，分母仍为 8；若希望比较 4 卡成本效率，应另开明确的成本目标或分别报告两种分母。

`DeploymentSpec` 保存显式 device IDs 与 group membership。P/D、draft、辅助角色均计入唯一设备集合；同设备多个并行维度不能重复计数。显存预算还需叠加共享设备上所有角色。

示例里的 `tp`、`dp`、`ep` 是给框架解析器的候选约束；真正启动计划必须展开为 rank 到设备映射。解析器不能用所有并行度的简单乘积代替真实拓扑。

## 7. CodeOptimizationBackend 的边界

本项目的接口草案见 [interfaces.py](../contracts/interfaces.py)。它表达自定义插件协议，不是 KDA 官方接口。实现可以启动 KDA 风格工作流、其他 Agent、传统 autotuner，或接收工程师提供的补丁。

任务包包含公开开发材料及固定的计算要求。正式验收器只向优化器公开规则，不公开隐藏输入或可写评分路径。外层保存正式验证器 hash，运行时检查未被候选修改。

## 8. 候选包与复现包

候选包应有 `manifest.json`，列出文件、hash、基础 commit、patch、依赖和适用范围。导入先检查清单与路径，再构建，不立即信任包内结果。

最终复现包包括：

1. 冻结的 Study、环境和负载引用。
2. 基线与候选的完整配置、补丁和构建标识。
3. 实际执行命令、版本、种子及设备映射。
4. 原始测量、统计方法、有效性与失败记录。
5. 假设、实验、候选和验收之间的引用关系。
6. 适用范围、覆盖缺口、未解决问题、恢复/回退方式。

不需要把模型权重和全部大型制品内嵌进包，但必须能按内容身份定位和校验。凭据不进入包。
