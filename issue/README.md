# GLM 5.3 Flash C500 优化待办

状态：**待确认**。评审日期：2026-11-26。对象：GLM-5.3-Flash-W8A8、单机八卡 C500、vLLM/MetaX 当前冻结版本。

建议先做同口径基线和失败边界核验，再优先验证 **KDA 门控归一化的 OOT 分派、EP 准备与通信链、mHC 小 batch 调优**。这些方向已有实际热点和源码落点。Dense GEMV、MoE 后端调优也有价值，但需要先拿到真实 shape 和生效的内核选择。DeepEP 和异步调度先作为有条件实验，不默认开启。

这里已经完成数据分析和本地 issue 草案；没有实施优化、重启模型测试或创建远端 GitHub issue。本次只从 60 的固定镜像只读提取安装源码，临时容器未挂载 GPU、未联网，退出后自动清理。

## 阅读入口

- [部署结果与可比性](deployment-review.md)：各部署的已测范围、代表值、失败边界，以及哪些比较成立。
- [全部 166 条汇总记录](measurements.md)：均值/P95、TTFT、TPOT、E2E、输出/请求吞吐；缺失值明确留空。
- [源码分析与跨芯片借鉴](source-review.md)：实际调用链、已融合部分、不能直接套用的参数，以及公开来源。
- [统一实验与验收流程](workflow.md)：复用现有 workload/deployment/plan，如何把下列任务变成可回退的实验。
- [计算校验与输入指纹](evidence-audit.json)、[机器可读测点](measurements.json)、[安装源码指纹](source-manifest.json)。

166 条是分组后的**汇总记录数**，不是 166 次独立实验：60 的缓存扫描有 26 行合并了 78 次运行，64 的新表保留了 15 条逐轮记录，历史512输出扫描另列7点。旧扫描归档和它派生的报表只计一次；profiled 轮不混入 control 性能结果。

## 待确认任务表

所有任务初始状态均为 `proposed`；P0 为正确解释结果/恢复可测边界的前置任务，不代表已知性能修复。

| ID | 优先级 | 任务 | 当前判断 | 前置 |
|---|---|---|---|---|
| [001](001-controlled-baseline.md) | P0 | 固定同口径部署基线与阶段归因 | 当前已有多种部署结果，但未形成全形态受控对照 | 无 |
| [002](002-cache-and-runtime-failures.md) | P0 | 区分缓存不足与高并发非法访存，恢复可测边界 | 已见非法访存；不能统一归类为容量不足 | 001 的环境冻结 |
| [005](005-kda-gated-norm.md) | P1 | 为 KDA gated RMSNorm 补齐有效的 MetaX 执行路径 | **源码指向明确**：OOT 默认回退 native，trace 与碎片链吻合 | 001 |
| [003](003-ep-prepare-and-collectives.md) | P1 | 定位并减少 EP remap/清零与 collective 等待 | EP 增时主项有实测；清零不可直接删除 | 001；高并发依赖 002 |
| [004](004-mhc-small-batch.md) | P1 | 按 C500/4096 hidden size 重调 mHC 小 batch | 已有融合，但调度注释仍沿用 GB300/其它 hidden size 经验 | 001 |
| [006](006-dense-gemv.md) | P2 | 按模块与 shape 优化 BF16 GEMV 和 INT8 dense linear | 有明显热点、已有局部替换原型；两条精度路径须分开 | 001 |
| [007](007-moe-kernel-selection.md) | P2 | 验证并调优实际 MoE 内核选择 | 缺 JSON 不等于慢；mctlassEx 覆盖部分配置 | 001、003 的 shape 记录 |
| [008](008-deepep-candidate.md) | P2 | 评估 MetaX DeepEP 的实际 Decode 收益 | 有插件入口；W8A8/布局/graph 支持必须逐项验证 | 001、003、007 |
| [009](009-sparse-indexer.md) | P3 | 优化长上下文 indexer/top-k 和无效 metadata 工作 | 有随长度增长的热点，但当前总预算较小 | 001 |
| [010](010-dp-scheduling-gaps.md) | P2 | 定位图重放间隔与 DP 协调开销 | kernel 之外还有 GPU memset/memcpy，剩余间隔尚不能归 CPU | 001、003 |

建议第一批确认 **001、002、005、003、004**。001 不要求先跑完整大矩阵；先取相同协议的少量锚点建立可靠基线，再对单个候选做局部和端到端验证。已有全矩阵配方保留，后续按你的负载点扩展正式复测。

## 为什么没有直接写性能提升百分比

热点累计 duration 是可优化时间预算，不是收益承诺。005 能定位到可改的分派入口，004 能定位到平台相关调参点；它们仍须在关闭 profiler 后验证 TPOT/吞吐。003 的通信 duration 可能包含 rank 等待，007 的“默认配置”提示也可能与实际执行内核的选择无关。

不将“换 All-to-All”“删 fill”“打开所有融合开关”“照搬其它芯片调参值”作为现成优化。详细证据与否决条件分别写在任务内。跨芯片资料用于证明方法值得试验，不将其收益数字当成 C500 的预期结果。

## 如何确认与推进

可按 ID 确认一批任务，或在任务文件中补负责人、目标部署与性能门槛。确认后按 [workflow](workflow.md) 推进 `approved → investigating → implementing → validating → accepted/rejected`。只有结果可复现且通过正确性回归，才写入正式配方和基线；没有收益也保留结论，避免重复尝试。

离线复算命令：在项目根目录运行 `python -X utf8 issue/analyze_evidence.py`。它读取冻结文件并生成汇总，不连接服务器；依赖原始大数据仍保存在 `experiments/`、`outputs/`。
