# 精度与正确性测试

本模块把任务功能、模型数值和算子数值分开判断。AIPerf 的请求成功与性能 SLA 不能证明模型精度；总分相同也不能掩盖原来通过的题变错。

方法来自 [回归策略](../../catalog/library/metax/methods/regression-policy.md) 和 [HumanEval 复现协议](../../catalog/library/metax/methods/humaneval.md)。这里的链接均相对仓库位置，原始来源与 SHA-256 同时保存在实际配方。

## 四层检查

| 层 | 固定或比较的内容 | 判定 |
|---|---|---|
| 实验完整性 | 模型/权重/tokenizer/template、数据与任务顺序、输入 token、采样/停止条件、运行配置、源码/依赖、评分器、独立进程与原始制品 | 缺失、篡改、基础设施错误为 `invalid`，不算模型失分 |
| 算子数值 | B0、候选、独立数学参考；shape/dtype/stride/alias/量化 scale/状态更新、边界输入、fallback | 整数与索引契约精确；浮点容差逐算子预登记；NaN/Inf、错误状态等失败 |
| 模型数值 | 相同 token 前缀、相同位置 logits/中间状态；prefill 和 cached decode 分开校准 | 自由生成分叉后不直接逐位置比较 logits；不能套用统一 INT8 百分比容差 |
| 任务功能 | 同期 B0/C 各三个全新模型进程，交错运行，完整题集 | 稳定通过题退化为 `fail`；波动题通过次数下降或总分保护失败为 `inconclusive` |

四层全部满足后才进入性能收益验收。三轮工程门槛不构成统计非劣性证明。全量 HumanEval 仍只覆盖代码任务，不能等同全部模型能力。

## 首版配置

- 定义：`schemas/definitions/accuracy.json`；模板：`schemas/templates/accuracy/plan.yaml`。
- 配方：`recipes/plans/accuracy/glm53-humaneval-full164.yaml` 与 `glm53-humaneval-smoke32.yaml`。
- 数据 revision 与任务 ID 来自移交包真实 manifest；`full164` 固定完整集合，`smoke32` 只作筛查。
- 评分约束按历史协议录入：无网络、无 GPU、只读根目录、1 CPU、512 MiB、32 PID、CPU 8 秒/wall 10 秒；生成侧不接收原始测试或答案，不修复答案或重采样。
- `numerical.thresholds` 当前为空，明确表示缺少候选前冻结的数值门槛，不能据此验收候选。

当前模型/硬件/Runtime 引用用于历史作用域和新计划准备，不能证明新部署与历史运行完全相同。重建环境需要新的观测与版本。

## 可用命令

```powershell
# 展开协议、输入闭包和执行缺口
python -m benchmark accuracy plan recipes/plans/accuracy/glm53-humaneval-full164.yaml --out experiments/runs/accuracy/preparation-new.yaml

# 只读核验既有全量输出，不运行生成的 Python 代码
python -m benchmark accuracy inspect recipes/plans/accuracy/glm53-humaneval-full164.yaml --runs "experiments/evidence/metax/glm53/baseline_ops/runs/20261123_humaneval_v1_full164" --out experiments/runs/accuracy/historical-audit-new.yaml

# 未来取得同期六个独立 Run 后，做功能层比较
python -m benchmark accuracy compare recipes/plans/accuracy/glm53-humaneval-full164.yaml --baseline <b0-run1> <b0-run2> <b0-run3> --candidate <c-run1> <c-run2> <c-run3> --out experiments/runs/accuracy/comparison-new.yaml
```

每个输入 Run 需要 `generation_manifest.json`、`generations.jsonl`、`score_summary.json`、`correctness.jsonl`，沿用已有移交包格式。检查完整 task ID/顺序、重复记录、生成 SHA-256、输出 token 数、截断标记、提交代码哈希、逐题计数与汇总。比较还要求协议/评分指纹一致、六个不同目录和六个不同的记录进程身份；目录复制或重复使用同一 Run 不能充当独立重复。

`inspect` 的 `history_verified` 仅代表保存的数据相互一致；它没有重跑评分器，也未独立证明进程启动事实。比较结果是功能筛查，所有离线报告均固定 `new_gpu_execution: false`、`release_accepted: false`。历史 153/164 不是当前候选的最低总分规则。

首版没有连接生成器、CPU 评分沙箱、logits/张量采集和数值计算执行器。上述 sandbox 字段是将来执行器必须遵守的协议，不是当前 CLI 已执行的隔离措施。输出保存在 `experiments/runs/accuracy/`，不覆盖原始资料和历史分数。
