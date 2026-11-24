# 端到端拆分与算子测试准备

本模块从服务请求逐层定位到模块、kernel、通信和算子输入，再为独立测试准备可复现契约。第一版提供离线规划和规范化 trace 汇总；mcTracer/mcProfiler 的原生采集、真实张量捕获与 GPU 重放尚未接入。

## 四层路径

1. **请求时间线**：请求 ID、输入/输出长度、排队、prefill、decode、调度、通信边界和客户端时延。不同计时域必须明确关联。
2. **模型模块**：层号与完整模块路径、实际计算路径、shape/dtype、各 rank/stream。名称包含 `self_attn` 不代表一定是标准全注意力。
3. **kernel / 通信**：记录 CPU launch、设备事件、复制、collective、相关 ID 与流依赖。保留重叠关系，kernel duration 求和不能充当 E2E 占比。
4. **算子独立测试**：轻量统计热 shape，再按容量上限捕获代表输入/状态；先 B0 捕获→B0 重放，随后才比较候选与独立数学参考。

首版计划在 `recipes/plans/breakdown/glm53-c500.yaml`，定义在 `schemas/definitions/breakdown.json`。计划覆盖 INT8 GEMM/量化、MoE alignment/routing/dispatch、稀疏注意力/indexer、KDA 状态、argmax、collective；这是待测试方向清单，不代表它们都已被证明是热点。

已有首个 [算子契约](operators/README.md) 引用移交包的真实 checkpoint 独立层记录，保留 `[K,N]=[4096,3072]`、stride `[1,4096]` 与三个测试形状。它明确标为合成激活和历史 GPU0 顺序切片试验，没有伪装成完整模型输入捕获或分布式性能结果。

## 捕获与计时要求

捕获记录 shape、dtype、stride、storage offset、alias、量化 scale/zero point、mask/routing/padding、设备、rank、stream、workspace、状态更新和输入/输出指纹。通信必须覆盖所有参与 rank 与集合调用顺序。权重按 tensor/shard/切片描述恢复，限制 activation/state 的保存容量，避免复制整模型。

计划暂设每批 fixture 上限 256 MiB、每算子最多 16 个 shape；这是新框架预算，不是从历史测量推得的推荐值。超预算须缩小范围或明确调整计划。

算子计时分 `kernel` 与 `wrapper`，后者包含必要的量化、转置、分配和调度；编译/输入创建单独计量。有状态算子每次恢复相同初态，设备 event 的 stream 与 MACA 计时能力须先验证。逐 shape 报告波动、workspace、误差、fallback；不简单平均 speedup，也不把影子校验或 profiler 开销混入正式性能分数。

## 命令与输出

```powershell
python -m benchmark breakdown plan recipes/plans/breakdown/glm53-c500.yaml --out experiments/runs/breakdown/preparation-new.yaml
python -m benchmark breakdown trace examples/traces/overlap.yaml --out experiments/runs/breakdown/overlap-synthetic-new.yaml
```

`plan` 输出完整依赖闭包、四层采集字段、算子契约和缺失条件。`trace` 使用 `TraceCapture` 契约，按 rank/clock domain 做区间并集，报告覆盖区间、分类与热点。不同 rank 或未同步时钟不相加，类别间也可能重叠；没有依赖图就不输出关键路径。第三步消费这些证据并规划下一轮专项实验。

`TraceCapture.evidence_kind: synthetic` 会保留为合成证据；导入规范化事件并不意味着原生 profiler 已适配。结果提供给 `diagnosis/` 和 `analysis/` 做归因及控制实验规划；算子更快之后仍需无仪器干扰的整模型 A/B 回归。

上面的 `examples/traces/overlap.yaml` 是已有合成 fixture，用于验证不同 rank 和重叠区间的算法；替换成经校验的真实 `TraceCapture` 后才汇总真实捕获。
