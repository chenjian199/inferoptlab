# MetaX / C500 资料入口

原包：[先读我](../../../experiments/evidence/metax/intake/先读我_移交包.md)。文档检索：[资料说明](hwdoc/README.md)、[16 份文档清单](hwdoc/CATALOG.md)、[主题](hwdoc/TOPICS.md)、[组件](hwdoc/COMPONENTS.md)。来源身份由 [collection.yaml](collection.yaml) 固定，文档与方法导航见 [index.yaml](index.yaml)。

## 如何用于本项目

| 资料 | 可复用内容 | 接入位置 |
|---|---|---|
| [HumanEval 复现协议](methods/humaneval.md) | 冻结任务、生成/评分隔离、输入 token 与评分器指纹、CPU 沙箱约束 | `benchmark/accuracy/`，HumanEval full164 / smoke32 配方 |
| [重复性与回归策略](methods/regression-policy.md) | 同期 B0/C 各三进程、稳定题不得退化、波动题单独判断、相同前缀数值比较 | 精度功能检查与数值验收协议 |
| [基线与算子优化交接](methods/operator-workflow.md) | E2E→模块→kernel、真实输入捕获、B0 自重放、三方参考、kernel/wrapper 分开计时 | `benchmark/breakdown/` 与 `operators/` |
| [重复性报告](../../../experiments/evidence/metax/glm53/repeatability_20261123/REPORT.md) | 同路径与跨路径必须分组、首次差异边界、采集范围与未证明事项 | 固定前缀与状态测试的设计依据 |
| [单层 GEMM 对照报告](../../../experiments/evidence/metax/glm53/reboot_recheck_20261123/REPORT.md) | 单层开关、fallback 覆盖、各 rank 记录、恢复基线、局部误差与任务回归分开 | 算子候选接入与后续验收要求 |
| mcTracer V08 / mcProfiler V06 导航 | 采集工具的原文与环境要求入口 | profiler 适配调研；当前未接入原生采集器 |
| mcPyTorch V16 / MCCL V08 / mcEigen V03 等 | 框架、通信、数学库资料与版本范围 | 环境及实现适配的资料依据 |

厂商工具的具体命令、默认值和兼容条件仍需查看原 PDF 与物理页号，本项目没有据文档名称猜测运行参数。历史源码可作为参数化适配参考，不在此复制成“已经支持所有机器”的执行器。

## 必须保留的结果边界

- 历史全量 HumanEval 为 **153/164**，属于当时冻结环境。当前离线入口可检查输出哈希、逐题评分与汇总一致性，不重新运行生成或评分。
- 重复性报告的三进程稳定性来自 **32 题子集**，不能自动扩展成完整 164 题的稳定集合。
- 普通重启后的候选对照为另一环境中的 **原 32 → 候选 32 → 恢复 4**；通信绕行、硬件异常与影子校验开销必须保留，不能拿它证明正式 E2E 性能收益。
- 第一份算子配方记录的是 **真实 checkpoint 权重 + 合成激活**、GPU0 依次重放 TP8 切片；后续报告另有真实模型输入捕获，二者不能混称。
- 某一实验的 1 BF16 ULP 或某组 logits 最大差值，只属于该实验条件。新算子的数值预算需要单独冻结。

## 数据流

资料库提供方法和来源 → `schemas/` 约束字段 → `recipes/` 组合当前机器/模型/协议 → `benchmark/` 采集或离线核验 → `experiments/` 保存结果 → `diagnosis/` 解释现象 → `analysis/` 规划专项实验 → `optimization/` 准备候选与回归。资料库保存可复用知识，实验仓储保存每次具体发生了什么。
