# 第三步：专项分析

本模块把第二步的假设展开为**可实施、可证伪、可交接的专项任务包**。也支持在尚无基线时，依据已检查的模型和硬件生成准备清单。当前包含 11 份详细方法、任务规划器和离线 trace 区间汇总器。

首版所有方法的 `implementation: planning_only`。没有自动启动 mcProfiler、Nsight、rocprof 或框架 profiler；任务中的工具名表示拟接入来源，能力状态保留 `unverified`。真实采集需要后续实现并资格验证适配器。

## 直接查看或复现

```powershell
python -m analysis plan recipes/plans/analysis/qwen-metax.yaml --diagnosis experiments/runs/diagnosis/qwen-metax-v1/diagnosis.yaml --out experiments/runs/analysis/my-qwen
python -m analysis plan recipes/plans/analysis/glm53-flash-w8a8-c500.yaml --out experiments/runs/analysis/my-glm-flash
python -m analysis plan recipes/plans/analysis/glm53-w4a8-c500.yaml --out experiments/runs/analysis/my-glm-w4a8
python -m analysis plan recipes/plans/analysis/glm53-w8a8-c500.yaml --out experiments/runs/analysis/my-glm-w8a8
```

输出 `analysis.yaml` 与完整 `report.md`，目录须不存在。Qwen 关联已完成的第一步与第二步；GLM 计划使用实际模型配置和新集群硬件清单，但没有虚构推理基线或运行时配方。

## 模块与数据

| 模块/目录 | 作用 |
|---|---|
| `planner.py` | 核对归因来源、模型作用域、适用性、资源和预算，展开任务 |
| `trace.py` | 按时钟域/rank 合并重叠区间，生成热点工作量和覆盖度 |
| `plans/` | Qwen 与三种 GLM 的实际分析计划 |
| `examples/` | 明确标为 synthetic 的 trace 契约样例 |
| `recipes/analysis/` | 11 份可复用方法卡，保持 YAML 格式 |
| `schemas/templates/diagnosis/`、`schemas/templates/analysis/` | DiagnosisPlan、AnalysisPlan、AnalysisMethod 模板 |

新任务仍从模板创建，不需复制 Python 代码：

```powershell
python tools/specs.py instantiate schemas/templates/analysis/plan.yaml --params examples/parameters/analysis-plan.yaml --out experiments/runs/new-analysis.yaml
python tools/specs.py instantiate schemas/templates/analysis/method.yaml --params examples/parameters/analysis-method.yaml --out experiments/runs/new-method.yaml
```

生成后替换目标模型/硬件/runtime、归因引用、方法和预算。新增方法注册到 `recipes/analysis/` 并加入 Plan 的 `method_refs`。开放的 tags 和实验字段不限制优化方向；首版已有 MoE、单卡通信、量化、MTP 的确定性不适用判断，其余方法条件仍需人工/适配器确认。

## 11 个专项

| 方法 ID | 主要问题 | 关键证据 | 最小区分实验 |
|---|---|---|---|
| `request-timing` | 高 TTFT/TPOT 来自哪里 | 请求关联、排队/调度/设备边界、时钟域 | 固定低负载变化长度，再固定长度变化并发 |
| `compute-gemm` | 实际 GEMM 是否慢于匹配实现 | M/N/K、dtype、stride、后端、device-event 样本 | 同 shape、同精度切换一个合法后端 |
| `memory-state` | 容量、流量还是状态生命周期限制 | 权重/KV/辅助状态/工作区、申请释放、读写流量 | 单独扫描上下文、并发或 page |
| `materialization` | 拷贝、padding、索引是否冗余 | 生产者/消费者、alias/stride、复制字节和调用数 | 直接生产目标布局或仅融合转换 |
| `communication` | 链路慢、消息多还是 rank 等待 | 进程组、payload、padding、rank 到达、NIC 拓扑 | 同有效消息量比较通信组合或变长传输 |
| `attention-compressor` | 稀疏/线性/压缩路径谁主导 | 层类型、q/kv 长度、top-k、压缩比、索引时间 | 同语义切换后端或分片压缩实现 |
| `moe-routing` | 专家负载、padding 或 EP 不均 | 专家直方图、真实小 M、dispatch/combine | 同资源改专家放置或 grouped GEMM |
| `scheduling-graphs` | chunk、batch、eager/graph 的影响 | 实际 step token、队列、graph hit、launch gap | 单因素扫描参数或比较已验证图路径 |
| `precision-kernels` | 混合量化是否使用正确执行路径 | 模块分组、packed layout、scale、dispatch、参考输出 | 保持量化语义切换实现，变精度另立合同 |
| `speculation` | MTP 是否减少总生成成本 | proposed/accepted/emitted、draft/verify 时间、额外资源 | 关闭与一个有限 draft 长度比较 |
| `host-serving` | 客户端、分词、CPU、网络是否限速 | actual send、CPU profile、连接/SSE 时间 | 服务不变，仅改变客户端供给或 CPU 放置 |

每份卡均包含：来源、适用范围、信号、替代解释、必需证据、采集字段及单位、步骤和交付物、实验控制项、支持/证伪条件、计算公式及边界、正确性检查、混杂因素、完成条件、优化交接和回退要求。

## 任务状态与优先级

| 状态 | 含义 |
|---|---|
| `needs_capture` | 有同作用域 E2E 基线，缺专项证据 |
| `awaiting_baseline` | 只有模型/环境信息，先建立推理基线 |
| `not_applicable` | 已检查的架构或分配资源不适用该专项 |
| `deferred_budget` | 超出本次任务数或拟议采集预算，保留任务 |

与归因假设直接关联的方法排在前面，其余按 Plan 顺序。暂不计算“预计收益分数”，因为关键路径比例和可改善空间尚无证据。

每个任务保留完整 `method_snapshot`、模型架构/精度、资源与基线 Run ID，以及 `available_evidence / missing_evidence`。`result: null` 和 `execution_authorized: false` 表示本次规划工具没有执行任务；它不是另设用户确认流程，也不改变已给出的授权范围。

预算上限为：`每次采集秒数 × 最小重复数 × 最大变体数 × 实际分配卡数`。不通过 TP/PP/EP 的简单乘积推卡数。启动/编译、无 profiler 控制、独立验收需由后续执行计划另计；当前值是保守采集包络，不是耗时预测。

## 原生 trace 接入边界

目前只接收归一化 `TraceCapture`，不把未知版本的 profiler JSON 猜成既有格式。适配器应明确转换：

1. 工具和版本、原始文件摘要、对应 Run 与采集协议。
2. `ns` 时间单位及每个 `clock_domain` 的窗口。
3. 事件 ID、rank、stream、category、name、start、duration。
4. profiler 开销与丢失事件说明；跨节点事件关联/时钟校准作为后续证据扩展。

示例为人工构造的区间，运行不会测量任何硬件：

```powershell
python -m benchmark breakdown trace examples/traces/overlap.yaml --out experiments/runs/analysis/overlap.yaml
```

rank 0 的 `[0,60]` 和 `[40,80]` 合并后覆盖 80 ns，不能累加成 100 ns。rank 1 独立计算 90 ns，也不能与 rank 0 相加为请求延迟。输出保留 category union、热点调用数/累计工作时间、窗口未覆盖区间；不同 category 的 union 仍可能重叠。

`uncovered_window_ns` 仅代表没有捕获到这些事件，不等于 GPU 真正空闲。没有因果依赖图时，`critical_path` 固定为 `null`，不产出热点的 E2E 占比。`synthetic` 来源始终保留；外部标注的 `measured` 仍需通过真实采集资格检查，不能因为满足此格式就宣称已经验证 profiler。

## 如何交接到优化

专项任务满足完成条件后，先形成诊断结论和局部复现包，再对接已有 `OptimizationTask`：

| 任务包中的内容 | OptimizationTask 对应域 |
|---|---|
| 假设 ID、证据及已验证目标 | `problem` |
| 真正调用点、父源码/patch/镜像 | `baseline`、`integration` |
| 实际 shape/dtype/stride 与输入 | `workloads` |
| 数值/别名/状态/质量政策 | `semantics` |
| 合法改动、开发测量、回退 | `edit_scope`、`development`、`integration` |
| 独立验收与留出数据 | `acceptance` |

当前只提供交接要求，不生成带占位路径的“可执行 KDA 任务”，也不调用 KDA。局部加速之后仍必须做固定点 E2E A/B；重新搜索带来的收益单列，组合收益不能相加。

## 当前平台差异

- Qwen 是 BF16 dense、单卡部署：MoE、跨卡通信、权重量化和无 draft 的 MTP 专项标为不适用；其余 7 项待采集。
- GLM Flash W8A8：按实际 45 层、288 专家/top-8、34 linear/11 sparse 建立方法作用域；不能套用标准 MHA KV 估计。
- 完整版 GLM W4A8：Linear W8A8 与 FusedMoE W4A8 分别分析，不把 I32 packing 当 FP32 权重。
- 完整版 GLM W8A8：约 703.95 GiB 文件量超过当前引用的单台 8×64 GiB；规划保留容量前置问题，不自动改成跨机或 offload。
- 新集群 runtime 尚未选定/验证，且清点时 GPU 被占用，三份 GLM 计划全部处于基线前的准备状态。

这些结果都来自已有配方与归档。本次没有登录集群、启动服务或开始 GLM 性能测量。

## 第四步交接入口

生成的 AnalysisReport 可交给 `python -m optimization plan <analysis.yaml> --out <新目录>`，输出配置/代码优化前的证据缺口、正确性要求和回退清单。说明见 [第四步](../optimization/README.md)，Agent 工作流见 [技能目录](../agent/README.md)。当前专项计划不会被升级为已确认热点或可执行优化任务。
