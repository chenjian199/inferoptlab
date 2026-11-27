# 端到端拆分与算子测试准备

本模块从服务请求逐层定位到模块、kernel、通信和算子输入，再为独立测试准备可复现契约。提供离线规划、规范化 trace 汇总，以及 vLLM 原生 torch.profiler 的缓存 Decode 采集入口；mcTracer/mcProfiler 的原生采集、真实张量捕获与 GPU 重放尚未接入。

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

## 图模式下的缓存 Decode Profiler

配方入口为 [glm53-cached-decode-profiler.yaml](../../recipes/plans/breakdown/glm53-cached-decode-profiler.yaml)。复用 `DecodeProfilePlan`、`DeploymentSpec`、`WorkloadSpec` 与 `benchmark.load.decode_protocol` 的预热、DP 固定路由、请求集生成和验证逻辑，不在 Profiler 内重新定义模型或负载协议。

当前配方为 TP2/DP4/EP8、图执行、总并发 4、输入 4096/16384/65536、输出 200。`max_running_requests: 16` 映射到各 DP 调度实例的 `--max-num-seqs 16`，不代表本轮实际并发为 16 或 64。负载每个 DP rank 分配一个独立上下文，每轮 16 个请求（并发×4）。

在目标机器的项目根目录、具备 AIPerf 和 Docker 权限的执行环境内运行：

```bash
python -m benchmark.breakdown.cached_decode_profile \
  recipes/plans/breakdown/glm53-cached-decode-profiler.yaml \
  --out experiments/runs/glm53-decode-profiler-new \
  --delay-iterations 8 --profile-iterations 32
```

流程为：启动并验证实际 graph/并行/attention/profiler 配置 → 逐槽预热与缓存/路由/Decode 验证 → Profiler 未启动的 200-token 对照 → 再次验证缓存 → `/start_profile` → 相同配置的 200-token 请求 → `/stop_profile` → 核对八个 worker trace、逐请求的全上下文命中、query=1、零抢占和输出数。原生迭代计数由固定 vLLM 版本实现，实际采集窗口以 trace 内 execute 标注为准；不把配置值当作已采集迭代数。

Profiler 只采样部分迭代，HTTP 请求仍完整生成 200 tokens。采样的请求时延包含 Profiler 启停、导出干扰，不作为性能评分。每个场景独立保存 `control/`、`profiled/`、验证文件及 `traces.json`；原始 trace 写入该次 server 的 `observations/profiles/`，不放进源码或 recipes。

```bash
python -m benchmark.breakdown.torch_trace \
  experiments/runs/glm53-decode-profiler-new/server/observations/profiles \
  --out experiments/runs/glm53-decode-profiler-new/operator-summary
```

汇总按 worker/device 保留 kernel 调用数、总时长、均值、P95、最大值、区间并集和图重放事件，生成 Markdown 和完整 JSON。CPU 包含子调用的耗时、GPU kernel 时长和跨卡时间不能直接相加。图重放不会逐次重新进入全部 Python/ATen 调用，GPU kernel 名称与 CPU 算子记录的覆盖不同；不能伪造缺失的模块归属或 shape。kernel 名称分类只作检索提示。

参考 [vLLM Profiler 接口](https://domc.vllm.ai/en/latest/contributing/profiling/)；配方中的具体字段已依据目标镜像内的固定版本源码核对。
