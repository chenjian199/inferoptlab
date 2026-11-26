# 完整上下文命中的 Decode 测试

入口为 `python -m benchmark.load.cached_decode`，计划使用 `CachedDecodePlan`，
部署继续复用 `DeploymentSpec`，负载继续复用 `WorkloadSpec`。
GLM 首版计划在 `recipes/plans/benchmark/glm53-vllm/cached-decode.yaml`。
实际数据和启动命令写入 `experiments/`，不写入 benchmark 或 recipes。

## 测量口径

- 原始上下文为 L 个 token：4096、16384、65536。
- P 阶段生成一个 seed token；额外预热续接请求，使混合注意力模型保存 L 边界的 KDA 状态。
- D 请求发送原始上下文及 seed，共 L+1 个输入 token。必须观测到 cached_tokens=L，
  首步与后续每步的 query length 都为 1；不允许抢占重算。
- 输出长度 20、50 指 D 端新生成的 token，P 端 seed 不计入输出。
- 原始上下文命中率为 100%；完整 HTTP 输入命中率为 L/(L+1)。二者分别保存，不能混称。
- 模拟的是上下文已经就绪的 D 端续接；没有真实 KV/KDA 网络传输，不能用它替代 PD 部署端到端成绩。
- TPOT 为首个至末个 D 输出 token 的时间差除以 O-1。首 D token 时延包含客户端发送、排队及调度。
  不把客户端时延标成纯 GPU kernel 时间。

## 数据与请求流程

每个并发槽有独立随机上下文。槽位 `s` 固定到 `s % DP`，预热和每次重放使用同一个
`X-data-parallel-rank`。同槽的四个请求顺序执行，不把所有用户改成共享前缀。
AIPerf 负责闭环并发、四轮发送、流式计时和原始指标导出，总请求数为 `C × request_multiplier`。

每个长度/并发组依次执行：清缓存 → 冷 Prefill 生成 seed → 边界预热 → 并发验证 → 性能测量。
同组的输出长度和重复测量复用已验证的驻留上下文，`reset_between_runs: false`；切换长度或并发组时清缓存。
正式测量前，KDA 和 FlashMLA 元数据均须显示没有 Prefill；每条计分请求仍由调度器观测
缓存长度、DP rank、每步 token 数及抢占次数。缺少证据视为无效。
缓存不能同时驻留的组标记 `cache_residency_failed`，保留原始响应，不混入有效性能表。

当前镜像需要 `--mamba-block-size 256 --prefix-match-unit 16`；这是已固定源码上的配置，
新运行时必须重新验证。观察器不修改调度决策，不加入 GPU 同步；仍存在少量 CPU 观测开销。
TP1/DP8/EP8 使用 1024 的 Prefill 请求分块预算，以降低启动激活内存峰值。
独立的 MLA 上下文工作区保持原实现；没有跳过内存检查或截断 64K 输入。
当前 GLM 的缓存维度是 512，而镜像中的原生 MHA 上下文 gather 仅支持 320/576。
派生 RuntimeSpec `metax60-vllm-glm53-cached-decode` 显式设置 `sparse_mla_force_mqa: true`，
使用镜像已有的 Sparse MLA MQA 路径完成预热。原始 RuntimeSpec 和镜像均保留。
计分时每个 DP rank 最多只有 16 个单 token 请求，仍需逐点通过完整缓存和 Decode 路径验证。
注意力元数据只在预检时记录，计分阶段只记录逐请求调度汇总。

## 文件关系

| 文件 | 职责 |
|---|---|
| `schemas/definitions/cached-decode.json` | 计划字段与约束 |
| `recipes/plans/benchmark/glm53-vllm/cached-decode.yaml` | 两种部署、六组负载、倍率和重复次数 |
| `recipes/deployments/glm53-flash/c500/vllm/cached-decode/` | TP8/EP8、TP1/DP8/EP8 与缓存配置 |
| `recipes/workloads/glm53-vllm/cached-decode/` | 输入长度、输出长度、并发点、请求倍率 |
| `benchmark/load/cached_decode.py` | 预热、验证、AIPerf 执行、断点恢复和结果表 |
| `benchmark/load/aiperf_hooks/sitecustomize.py` | token-ID 输入的逐请求 DP 路由和请求 ID |
| `tools/deployment/metax-vllm/observers/sitecustomize.py` | 服务端调度及注意力路径证据 |

AIPerf 0.12 的 payload-bytes 缓存格式不保存每个 turn 的请求头，因此该协议显式使用
保留请求头的 conversation 格式。这个限制已覆盖在回归测试中；不能删掉后只看 HTTP 200。
本协议关闭 AIPerf mmap 数据集缓存复用，避免加载旧的、不带路由头的数据格式。

## 执行与调整

在已安装 `benchmark/requirements.txt`、能操作 Docker 的 Linux 客户端环境中，从项目根目录运行：

```bash
python -m benchmark.load.cached_decode \
  recipes/plans/benchmark/glm53-vllm/cached-decode.yaml \
  --out experiments/runs/glm53-cached-decode
```

模型路径、镜像和设备来自部署与运行时配方。只做预检可加 `--qualify-only`。
相同命令和输出目录用于恢复；已完成且快照相同的点不会重测。
恢复前必须确认旧进程已退出；公共 benchmark 租约阻止同时启动两轮测试。

修改并发：对应 workload 的 `arrival.load_points`。
修改长度：workload 的 `input.tokens` / `output.tokens` 及标签。
修改倍率：计划 `request_multiplier` 与 workload 的 `requests.count_multiplier` 保持一致；不一致会拒绝执行。
修改重复：计划 `repetitions`。首次冻结后修改配方必须使用新的输出目录。

`state.json` 展示当前部署、分组和计分测点；`README.md` 汇总有效性能点。
每点保留 `inputs.json`、AIPerf 全部导出、`engine-verification.json` 和
`profile-verification.json`；每组保留 seed、预热响应、缓存与注意力验证。
生成的性能数据不自动代表数值精度验收；冷运行和缓存运行的逐 token 一致性另行记录。
