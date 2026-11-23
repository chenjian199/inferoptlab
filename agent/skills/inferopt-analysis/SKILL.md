---
name: inferopt-analysis
description: 在 InferOptLab 项目中将归因假设转成第三阶段专项任务，使用分析方法卡细化 trace 采集、控制实验、正确性、证伪条件与优化交接。
---

先读 [共同约束](../../README.md) 和 [analysis 入口](../../../analysis/README.md)，只加载本任务需要的 [方法卡](../../../schemas/recipes/analysis/)。

1. 对齐 DiagnosisReport、AnalysisPlan 和模型/硬件/runtime 身份；无基线的 GLM 任务保留 awaiting_baseline。
2. 用 `python -m analysis plan <计划路径> --diagnosis <归因结果> --out <新目录>` 生成专项任务；无 diagnosis 依赖的计划省略该参数。
3. 围绕假设选最小证据集：真实 shape/layout/dtype、请求/step/layer/kernel 关联、clock domain/rank、采集窗口、丢事件及 profiler 干扰。匹配硬件微基准范围，不借用不相关峰值。
4. 设计单因素控制实验、支持和推翻条件、独立正确性检查，计算实际设备集合对应预算。真实采集需要现成或实现并验证的适配器；当前 planner 不执行 GPU 工作。
5. 归一化事件可用 `python -m analysis trace <TraceCapture路径> --out <新文件>` 离线汇总。合成数据明确标记 synthetic；没有依赖图就不声称已求关键路径。
6. 交接专项证据、未解问题、源码/调用点缺口、候选改动方向和回退要求；尚未执行的实验保持空结果。

重叠事件用区间并集，跨 rank/时钟域不直接相加或相减；未覆盖窗口不等于设备空闲。布局/量化/稀疏/MoE/MTP 等使用对应方法卡的语义与质量约束，不假定所有模型都有相同模块。
