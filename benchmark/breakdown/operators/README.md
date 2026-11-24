# 算子独立测试契约

定义：`schemas/definitions/operator-case.json`。首份实际配方：`recipes/operators/glm53-gate-up.yaml`。`breakdown plan` 会展开它并核验来源及模型/硬件/Runtime 作用域。

首份记录来自移交包的独立层 JSON：第一层 `gate_up_proj`，`CompressedTensorsW8A8Int8`，原实现 `MctlassScaledMMLinearKernel`，INT8 权重 `[4096,3072]`、stride `[1,4096]`，MNK 形状为 `[1,3072,4096]`、`[17,3072,4096]`、`[173,3072,4096]`。原实验是真实 checkpoint 权重、合成激活，GPU0 顺序重放 TP8 分片。

历史结果不是新机器的测试输出。配方中 `numeric_budget: null`、`fixture_artifacts: []`、`baseline_self_replay: not_revalidated` 都会产生明确缺口。当前 OperatorCase v1 有意限定到这类历史 INT8 投影契约；attention、MoE、collective 等需按其状态和多 rank 语义扩展标准，不能只换算子名称。

后续执行器按以下顺序接入：

1. 核对源码/权重和输入来源，安全恢复 tensor 元数据及数值；本离线入口不会 `torch.load` 历史 `.pt`。
2. 验证 B0 捕获→B0 重放，含 stride、alias、量化与状态；自重放失败停止候选比较。
3. 同一输入比较 B0、候选和独立参考。先冻结数值预算，整数语义及 ABI 按契约精确校验。
4. 资格检查通过后，分别测 kernel 和 wrapper；固定 warmup/repeats/iterations、stream、cache 和 state 重置。
5. 单算子接入模型，记录命中/fallback 与各 rank 情况；功能/数值回归通过后才测整模型性能，保留恢复基线试验。

GPU 重放和计时执行器尚未连接；当前输出是可审查的准备计划，不会将声明的 `passed` 字段当作真实执行能力证明。
