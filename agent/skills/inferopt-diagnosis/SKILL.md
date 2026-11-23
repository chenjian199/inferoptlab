---
name: inferopt-diagnosis
description: 在 InferOptLab 项目中核验封存的 benchmark 证据、复算指标和可比性，生成第二阶段归因观察、可证伪假设及缺失证据清单。
---

先读 [共同约束](../../README.md) 和 [diagnosis 使用说明](../../../diagnosis/README.md)。需要查看来源如何影响分析时读 [阶段设计](../../../docs/diagnosis-analysis.md)。

1. 选择 DiagnosisPlan，核对批次、manifest 摘要、Study 和方法引用。优先读取现有封存资料。
2. 用 `python -m diagnosis plan <计划路径>` 检查输入，再用 `python -m diagnosis run <计划路径> --out <新目录>` 生成结果。
3. 检查完整性、身份、请求指标复算、无效运行和分组；输入长度比较不能混入不同输出长度，比较配置时不能悄悄改变请求集/cache/协议。
4. 输出观察、替代解释、样本/重复限制、需补的专项证据和真实路径。把假设与对应 AnalysisMethod 交给第三步。

发现摘要或身份不符时修复数据来源/重新归档，不通过改摘要掩盖变化。失败运行保留并排除于合格比较；没有 trace 和受控干预就不能确认 kernel 根因。规则未覆盖的问题保留为未解释项，历史收益不迁移为当前收益。
