# GLM 模型基线与算子实验

初始化日期：2026-11-22。这里承接 [交接文档](../../../../../catalog/library/metax/methods/operator-workflow.md) 的代码、配置与结果组织。HumanEval 数据已固定，生成和隔离评分已实现；本轮状态见 [WORK_STATE.json](WORK_STATE.json)，执行方式和边界见 [复现说明](../../../../../catalog/library/metax/methods/humaneval.md)。性能基线与算子实验尚未执行。

2026-11-23 已建立首份任务精度基线：**HumanEval 全量 153/164（93.2927%）**，smoke32 为 31/32；canonical 164/164 验证评分器。结果、失败题目及非严格重复性的边界见 [基线报告](BASELINE_REPORT.md)。

首个端到端任务精度回归选用 **HumanEval test 全量 164 题**，每题生成一次，报告本项目固定协议下的 pass@1。32 题子集仅用于前期调通，不能替代全量分数。理由、来源和速度判断边界见 [数据集选型](../../../../datasets/humaneval/SELECTION.md)。

## 目录入口

```text
baseline_ops/
  configs/
    d0_environment.json          # 历史部署配置，须在新环境重新验证
    humaneval_regression.json    # 历史 pilot 前协议模板
    humaneval_regression.frozen.json # 全量开始前冻结的实测配置和哈希
    performance.json             # 整模型性能负载草案
    thresholds.json              # 等待 B0 自重复后冻结的门槛
    candidate.json              # 默认关闭候选替换
  datasets/
    SELECTION.md
    source_catalog.json         # 三个数据集的官方来源和观察日期
    humaneval/manifest.json      # 已固定 revision/文件哈希/164与32题ID
    raw/                        # 原始数据缓存，默认不提交
    prepared/                   # 冻结样例/token 文件，默认不提交
  harness/                      # 生成、代码提取、隔离评分、汇总与离线核验
  evidence/humaneval_v1/         # 实际输入tokens、环境和执行源码快照
  operators/
    _template/                  # 算子契约模板，尚无候选实现
  runs/
    _template/                  # 运行资产模板，不是真实实验
    <run_id>/                   # 不可覆盖的实验目录
```

主要子目录有 README。模板 JSON 中的 `null` 表示尚未确定；`draft`、`template_not_run`、`observed_not_revalidated` 不得被当作已通过状态。本轮保留历史 pilot 输入字面内容，实际全量协议另存 `.frozen.json` 并绑定运行清单。性能和阈值模板中的空值仍待后续实验填充。

## 首批实现顺序

1. 在新实验目录/容器复现 D0，检查来源、权重与八卡 smoke，保留原 `dcc` 和 `glm53-vllm032`。
2. 下载并固定 HumanEval revision、164 个唯一任务 ID、许可与文件哈希，分离生成输入和评分用测试。
3. 实现生成适配器、CPU 隔离测试执行器及评分器；先验证官方 canonical solution，再调通固定的 32 题子集。不得把 canonical solution 或隐藏测试输入模型。
4. 校准提示词、代码提取规则、输出预算和超时，验证后冻结协议；完整跑 164 题。当前 smoke32/full164 的重叠题用于同引擎重复性观察，独立进程 B0 自重复仍待实施。greedy 配置与此前部署时随机采样 smoke 分开记录。
5. 再建立独立的性能测量。HumanEval 的总运行耗时包含题目差异和评分开销，不代替固定输入/输出长度的性能矩阵。

比较候选时使用同一任务 ID、模板、解码参数、测试和资源限制，同时输出 B0 对→候选错、B0 错→候选对、双方对、双方错四类任务清单。仅比较总分可能掩盖相互抵消的退化；通过率也不能替代局部算子数值等价性和 logits 回归。

大张量、权重、trace 和实际运行结果默认不进入 Git；小型配置和模板可提交。实际结果需按 SHA256 清单归档。本轮远程动作限定在 `/home/metax/glm53-baseline-ops` 和新容器 `glm53-heval-v1`；保留原 `dcc`、`glm53-vllm032` 与模型目录。
