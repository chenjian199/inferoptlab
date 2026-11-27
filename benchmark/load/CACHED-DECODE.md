# 完整上下文命中的 Decode 矩阵测试

性能扫描唯一入口是 `python -m benchmark.load.matrix_run`。所有部署轴、负载轴、请求倍率和测量规则集中在根目录 [benchmark-matrix.yaml](../../benchmark-matrix.yaml)，运行数据写入 `experiments/`。

## 并发与请求数

AIPerf 同时支持 `--concurrency C`（客户端在途请求数）与 `--request-count N`（本次发送的总请求数上限）。矩阵先按实际 KV 驻留容量裁剪 C，再计算 `N = C × requests.count_multiplier`，同时传给 AIPerf。例如 C=48、倍率=4，命令包含 `--concurrency 48 --request-count 192`。这不是 192 并发，也不是每个 DP rank 分别发送 192 个请求。

每个并发槽对应一个独立上下文和一个 AIPerf session，同槽包含倍率指定的多个顺序 turn；每次回放输入相同，不拼接前一轮输出。槽位 s 始终路由到 `s % DP`。AIPerf 负责闭环发送、流式计时和指标导出，预热及资格检查通过单独的 HTTP 请求完成，不计入 N。

只有导出完整 N 条有效请求才接受该测点，不能只看进程退出码。没有固定 200 请求下限，也不另设一个与倍率竞争的固定总数。参数说明见 [NVIDIA AIPerf 0.12 CLI 文档](https://docs.nvidia.com/aiperf/v0.12.0/reference/command-line-options)。

## 每个测点的缓存生命周期

每个部署×输入长度×有效并发×输出长度×重复轮依次执行：

1. 用固定 seed 准备每槽独立上下文，相同长度/并发下的不同输出轮使用相同输入。
2. 调用 `/reset_prefix_cache` 并要求成功。清理服务端前缀 KV 缓存，保留模型、图捕获和编译缓存。
3. 逐槽冷 Prefill 生成一个 seed token，再填充边界，以保存混合 KDA 状态。
4. 逐槽审计驻留情况，执行 2-token 并发资格检查，验证固定路由、完整上下文命中和 Decode 路径。
5. 独立启动 AIPerf，发送 N=C×倍率 个计分请求；只在当前测点各 turn 间保留缓存。
6. 验证每条计分请求的缓存长度、DP rank、query 长度、输出数和无抢占；调度、Attention 和客户端证据均有效才写入成绩。

切换输出长度或重复轮时重新执行上述步骤。失败重试先重启服务，再清缓存、预热和验真。每次尝试的观测标签包含完整路径摘要，避免旧记录混入。共同预热失败耗尽重试后，阻塞同输入/并发组的剩余输出；重复非法访存则隔离该部署，不把未测点标成成功。

预热和资格检查均不计入性能窗口，原始证据另存。容量计算见 [CAPACITY.md](CAPACITY.md)：这是当前池规格下的保守驻留预算，不把 max_num_seqs 当作缓存容量上限。

## 测量口径

- 原始上下文为 L，当前输入数组为 4096、16384、65536 token。
- P 生成一个 seed；D 请求携带 L+1 个输入，要求 cached_tokens=L。
- 首步与后续每步 query length 均须为 1，无抢占重算；输出 O 只计 D 端新增 token。
- 原始上下文命中率是 100%；完整 HTTP 输入命中率是 L/(L+1)，分别记录。
- TPOT=(末 token 到达时间−首 token 到达时间)/(O−1)。TTFT/E2E 包含客户端、排队和传输，不是 GPU kernel 独立耗时。
- 这是上下文已就绪的 D 端模拟，不包含真实 P→D KV/KDA 传输，不代替 PD 端到端成绩。
- 资格检查和计时阶段的 KDA、FlashMLA Attention 元数据都要求零 Prefill。观察器无 GPU 同步，但有 CPU 记录开销。

## 文件关系

| 文件 | 职责 |
|---|---|
| `benchmark-matrix.yaml` | 单文件部署、负载、请求和测量配置 |
| `benchmark/load/matrix_run.py` | 唯一性能扫描入口、容量裁剪、重试恢复、汇总 |
| `benchmark/load/matrix_config.py` | 矩阵展开、部署参数、配置回读、每 DP 池读取 |
| `benchmark/load/capacity.py` | KV 容量及并发映射算术 |
| `benchmark/load/decode_protocol.py` | 公共预热、固定路由、请求集、AIPerf 命令和验真，无扫描入口 |
| `benchmark/load/aiperf_hooks/sitecustomize.py` | 路由头、请求 ID、本地 tokenizer 支持 |
| `tools/deployment/metax-vllm/observers/sitecustomize.py` | 容量、调度、Attention 证据 |

AIPerf 0.12 的 payload-bytes 格式不保存 turn 请求头，因此使用 conversation 格式，并关闭 mmap 数据集缓存复用，避免读入旧路由格式；这些行为由回归测试覆盖。

## 执行与调整

在具备模型、镜像、设备和依赖的 Linux 主机项目根目录运行：

```bash
python -m benchmark.load.matrix_run benchmark-matrix.yaml \
  --out experiments/runs/glm53-matrix \
  --cache-dir "$PWD/experiments/cache"
```

加 `--preview` 仅检查展开和启动参数，不启动服务。

| 调整内容 | YAML 字段 |
|---|---|
| 并行、EP、模型长度、调度参数 | `deployment_matrix` 的数组 |
| 输入、输出、并发 | `workload_matrix.input_tokens/output_tokens/concurrency` |
| 请求倍率 | `requests.count_multiplier` |
| 重复轮数 | `requests.repetitions` |

实际命令保存在每点 `measurement/command.json`，观测标签在 `measurement/observation-phase.json`。`state.json` 记录进度与失败，`summary.csv` / `README.md` 汇总有效成绩。

恢复要求矩阵、代码、模型和数据指纹相同，并确认旧控制器已退出。修改配置或代码后使用新输出目录，不能混入冻结结果。公共租约防止重复启动。

Profiler 使用 `benchmark.breakdown.cached_decode_profile` 和 `DecodeProfilePlan`，作为专项诊断复用公共协议，不是另一套性能矩阵执行器。
