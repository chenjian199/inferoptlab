# GLM Flash 五种并行形态的 Decode 延迟扫描

## 五种部署扩展

2026-11-25 的目标扩展为五种部署：TP8、TP8/EP8、TP4/DP2/EP8、TP2/DP4/EP8、TP1/DP8/EP8。五种部署 × 三种输入长度 × 两种输出长度 × 八个并发 × 三轮重复，共 **720 个计划点**。按用户最新要求，失败配置不反复重试，同配置剩余重复轮次跳过，其余点继续；完成意味着全部计划点都有明确结果或跳过原因，不能将失败和跳过计为有效测量。TP8 图执行版未包含在这五种中。

- [五种部署总计划](decode-five-layouts.yaml)：720 点的完整定义，用于核对覆盖范围。
- [原两种部署计划](decode-scan.yaml)：288 点，正在原批次中续测，保留已完成数据和跳过清单。
- [新增三种部署计划](decode-additional-layouts.yaml)：432 点，与原批次无重叠，复用同一组 Workload、Protocol、Scenario 和数据集指纹。

当前运行期间不要直接执行 720 点总计划，否则会重复已经完成的测试。先完成原批次，再执行新增三种部署的启动资格检查和补充计划。`supervise_scan.py --qualify-before-run --skip-failed-configurations` 会先启动各部署，核对服务配置及 128→32、65536→1 两组 API 探针。某种部署资格失败时，保留绑定该配方内容的失败记录，将其计划点标为 `skipped_startup_failure`，其余部署继续。清理失败仍停止，避免两个服务竞争设备；未取得任何启动记录或配方指纹不匹配也不能当作已确认的失败跳过。

五种部署均使用 73728 最大上下文、4096 调度 token 预算、chunked Prefill、eager 执行和关闭 prefix cache。每个 DP 引擎的最大在途序列数为 `128 / DP`，即 128、64、32 或 16，总额度保持 128。模型权重、运行镜像、采样协议和每点四倍并发的计分请求数不变。

## 完整扫描与断点续测

`tools/deployment/metax-vllm/supervise_scan.py` 在测试主机上每 60 秒记录一次进度，并在执行进程退出后续测未完成点。用 `nohup` 启动可让任务独立于 SSH 会话运行。状态目录保存 `state.json`、逐次巡检 `checks.jsonl`、固定的 `resolved.yaml` 和每次启动的命令及日志。

续测以 `(trial_id, repetition)` 区分测试点，核对完整快照和已完成点的原始数据哈希。本轮启用 `--skip-failed-configurations --max-stalled-attempts 1`：失败尝试保留在原目录与 `attempts` 中，后续同一 `trial_id` 的重复项标为 `skipped_failed_configuration`，其他输入、输出、并发和部署继续。已完成项不重测。执行策略单独保存在批次账本，不修改归档计划或降低测量参数。有失败的批次结束状态为 `finished_with_failures`，只有全部成功才是 `completed`。基础设施异常导致批次无法继续时记录 `needs_repair`，不循环重试同一失败点。

用户明确要求跳过某点时，在暂停批次的 `exclusions.json` 中列出计划指纹、原因、时间及具体 `(trial_id, repetition)`，然后使用相同的 `--resume` 命令。账本将这些项标为 `skipped_by_user`，保留此前失败目录和原始状态。2026-11-25 本轮明确排除了 TP2/DP4/EP8、4K 输入、50 tokens 输出、并发 128 的三轮重复。随后 16K/50、并发 64 失败，按新策略保留失败尝试并跳过该配置剩余两轮。最终报告分别统计成功、失败、用户跳过及失败后跳过项。详见[本轮排除记录与文件格式](../../../../experiments/evidence/glm53-short-output-skip-c128-20261125/README.md)。

```bash
# 在测试主机的项目根目录执行；CLIENT_ROOT、CLIENT_IMAGE、QUALIFICATION 指向已验证的客户端和资格记录。
SESSION=experiments/evidence/glm53-short-output-session
nohup python3 -u tools/deployment/metax-vllm/supervise_scan.py \
  --plan recipes/plans/benchmark/glm53-vllm/decode-scan.yaml \
  --qualification "$QUALIFICATION" \
  --client-root "$CLIENT_ROOT" --client-image "$CLIENT_IMAGE" \
  --state-dir "$SESSION" --interval 60 \
  --skip-failed-configurations --max-stalled-attempts 1 \
  > "${SESSION}.log" 2>&1 < /dev/null &

# 实时进度：包括当前部署、场景、并发、轮次、执行阶段和最近完成点的性能。
watch -n 10 "python3 -m json.tool $SESSION/state.json"
tail -f "$SESSION/checks.jsonl"

# 手动续测使用原批次快照，不重新解析可能已修改的配方。
python3 tools/deployment/metax-vllm/run_scan.py \
  --client-root "$CLIENT_ROOT" --client-image "$CLIENT_IMAGE" \
  run "$BATCH/resolved.yaml" --qualification "$QUALIFICATION" \
  --out "$(dirname "$BATCH")" --resume "$BATCH" --skip-failed-configurations
```

如果需要临时停止并在结束后恢复本项目已有的服务，可额外指定 `--restore-service` 和匹配的 `--service-label`。程序只停止空闲且所有权标签匹配的服务。机器重启或强制杀进程后若留下执行锁，须先核实原进程和容器是否退出；不会自动删除未知所有者的锁。

入口：[decode-scan.yaml](decode-scan.yaml)。本轮按用户确认，允许正常 Prefill，只分析首 token 之后的客户端延迟；**不声称隔离设备纯 Decode，也不要求全缓存复用**。2026-11-25 用户改为直接测试性能：使用 `mode: exploratory` 采集下面的完整矩阵，保留已通过的启动资格，不等待功能回归和绝对精度验收。这里 exploratory 表示验收状态，不表示缩小测试规模或粗筛。

## 固定矩阵

| 维度 | 值 |
|---|---|
| 部署 | TP4/PP1/DP2/EP8；TP2/PP1/DP4/EP8 |
| 输入 tokens | 4096、16384、65536（K=1024，包含 chat template） |
| 输出 tokens | 20、50，与每个输入长度做笛卡尔积 |
| 并发 | 1、2、4、8、16、32、64、128，全服务总并发 |
| 每点计分请求 | 严格 `4 × C`，不设置最小 200 请求下限；不含预热 |
| 独立重复 | 3；每次均保留结果，不挑最快的一次 |
| 总规模 | 2 × 3 × 2 × 8 × 3 = 288 Runs；36,720 个计分请求 |
| 预热 | 每点 `max(4, C)`，独立进程、独立数据，不计入得分 |
| 上下文上限 | 73728，覆盖 65536 + 50 |
| 调度 token budget | 每个 DP 引擎 `max_num_batched_tokens=4096`；chunked Prefill 开启 |
| 最大在途序列 | DP2 每个引擎 64；DP4 每个引擎 32；合计 128 |
| 其它 | eager、同步调度、prefix cache 关闭、显存比例 0.9、allgather_reducescatter |
| KV block | 由该镜像按混合注意力状态自动推导；记录实际值，不把 4096 token budget 当成 KV block |

低并发不会占满所有 DP 引擎；这是总并发曲线的一部分。长输入高并发可能排队或发生缓存压力，失败/超时不得删去。14 天预算是执行上限，不是运行时长预测；达到预算的未执行点必须保留为 skipped。

输出由 512/1024 改为 20/50 后，计分输出 token 总量从 28,200,960 降至 1,285,200（约为原来的 4.56%）。这是生成量变化，不是整轮耗时比例：Prefill、预热、服务启动及数据校验仍需时间。短输出下 TPOT 分别覆盖 19/49 个 token 间隔，应按短输出测试解释，不能与旧长输出结果直接合并。

## 修改位置与引用关系

- [部署参数](../../../deployments/glm53-flash/c500/vllm/decode/)：TP/DP/EP、服务启动、context、每个 DP 的序列数和调度预算。
- [六组 workload](../../../workloads/glm53-vllm/decode/)：`input.tokens`、`output.tokens`、`arrival.load_points`、`requests.count_multiplier`。本轮不设置 `min_count`。
- [协议](../../../protocols/glm53-vllm/decode-post-first.yaml)：计时口径、预热、超时、重复次数。
- [TestCase](../../../test-cases/glm53-vllm/decode/) → Workload/Protocol；[Scenario](../../../scenarios/glm53-vllm/decode/) → TestCase/数据目录；[Study](../../../studies/glm53-vllm-decode-scan.yaml) → 模型/硬件/Runtime/允许用例；Plan 只组合这些引用。

Plan 不复制 workload 的并发与长度配置。调整后重新生成数据、更新指纹并生成新的 resolved snapshot；不要修改已归档 Run。新增长度对时增加 Workload、TestCase、Scenario，并同时加入 Study 的 `case_refs` 与 Plan 的 `scenario_refs`。修改部署后必须重新取得对应启动资格。

## 指标

每个成功且记录完整的请求计算：

```text
post_first_token_ms = request_latency_ms - TTFT_ms
TPOT_ms = post_first_token_ms / (actual_output_tokens - 1)
```

报告 mean、p50、p95、p99 和样本数。`decode.json`/`decode.md` 是本轮主报告；TTFT 和全时间窗口吞吐继续保存作诊断证据。**并发请求的 Prefill、调度和客户端流传输仍可影响 TPOT，不能把全窗口 output tokens/s 称为纯 Decode 吞吐。** TPOT 的分位数是请求均值的分位数，不是逐 token ITL 分布。

本轮没有绑定不匹配长度或统计口径未确认的 SLA，报告不得据此标记业务 SLA 达标。

## 执行前置条件

1. 完整权重指纹：`tools/hardware/probes/checkpoint_payload.py` 逐字节读取全部索引分片，检查索引/头、布局和读取期间文件稳定性。模型配方 `cluster-glm53-flash-w8a8@1.1.0` 绑定清单来源。这个身份是本地内容地址，不是伪造的上游 release revision，也不证明数值正确。
2. 当前硬件：八卡身份/PCIe/ECC/RAS 观测，加同镜像八 rank 的 all-reduce/all-gather/reduce-scatter、拷贝和小规模 FP32 GEMM 正确性检查。检查范围必须写明，不等于全面厂商认证。
3. 两种部署启动资格：实际启动本轮配方，检查配置、卡绑定、128→32 与 65536→1 API 探针。旧 32K 配方的成功记录不能直接替代。
4. 同期功能回归已按用户要求中止，已有原始输出和评分记录保留。该检查不再阻塞本轮性能采集；不能把未完成的对比标记为通过。
5. 验收边界：没有可信外部参考和预登记的同前缀数值容差。数值/质量政策仍未补齐，本轮仅采集性能证据，不建立验收通过的基线，不宣称模型绝对精度合格。模型、硬件等 readiness issues 继续保存在 resolved snapshot 中。
6. 请求集：AIPerf 客户端准备 48 份逐并发 fixture，逐条核对完整模板 token 数和哈希；同一个 fixture 在两种部署间复用。

前置运行入口是 `tools/deployment/metax-vllm/preflight.py`，通过参数指定 Plan、TP8 参考、HumanEval 数据、评分镜像和允许临时停止的原服务。它检查明确的所有权 label 和服务空闲状态，持有实验锁，退出时恢复原容器。它不会执行性能扫描；失败记录保持原样，新尝试使用新目录。

```bash
# 仓库根目录；只做离线矩阵检查
python -m benchmark load plan recipes/plans/benchmark/glm53-vllm/decode-scan.yaml

# 查看实际入口及所有必填路径，不依赖某个固定工作区目录
python tools/deployment/metax-vllm/preflight.py --help
python -m benchmark.accuracy.live --help

# 直接性能采集；资格记录必须对应当前部署、模型、硬件与 Runtime
# 在已安装项目依赖及指定版本 AIPerf 的 Linux 环境执行
python -m benchmark load run recipes/plans/benchmark/glm53-vllm/decode-scan.yaml \
  --qualification experiments/evidence/glm53-decode-preflight/20261125/live-r3/startup/qualification.json

# 将来需要正式验收时，补齐前置条件并把计划改为 formal 后再冻结
python -m benchmark load plan recipes/plans/benchmark/glm53-vllm/decode-scan.yaml \
  --freeze --out experiments/runs/benchmark/decode-resolved.yaml
```

本轮前置证据位置：`experiments/evidence/glm53-decode-preflight/20261125/`；20/50 输出的新数据集位置：`experiments/datasets/glm53-vllm/decode-short-output/`。Workload、TestCase 和 Scenario 使用带 20/50 的新标识，旧请求集哈希已清除，需要重新准备并绑定。旧 `decode/`、`decode-fourfold/` 数据和已归档批次保留，不与新批次混合。真实性能 Run 将进入 `experiments/runs/benchmark/` 并登记知识库。无完整性能结果时不建立性能基线。
