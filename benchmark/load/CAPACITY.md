# 预热驻留容量、并发扫描与指标口径

配置入口是 [benchmark-matrix.yaml](../../benchmark-matrix.yaml)。用户定义的容量是：**能同时保留多少条独立预热上下文，并为这些请求预留输出增长空间**。它不是同一时刻的Running请求数。

当前正式入口是 [matrix_run.py](matrix_run.py)：每种部署启动后直接采集实际缓存池、计算并发预算，裁剪预设点并运行AIPerf。[capacity.py](capacity.py) 提供算术函数；[matrix_config.py](matrix_config.py) 提供部署展开与实际池读取。独立容量预扫执行器已删除，下文边界调查仅保留为方法说明，不是可执行入口。

## ITL与TPOT：本项目实际是同一口径

对输出O≥2的请求，记t0为发出时间，t1为首个有效输出到达时间，tO为最后有效输出到达时间：

```text
TTFT = t1 − t0
E2E  = tO − t0
TPOT = (tO − t1)/(O−1) = (E2E−TTFT)/(O−1)
AIPerf 0.12 ITL = (E2E−TTFT)/(O−1)
```

相同token计数、请求集合和时间边界下，ITL与TPOT逐请求相等，平均值和P95也应相等，允许浮点舍入误差。项目normalizer的TPOT由E2E/TTFT计算，ITL读取AIPerf指标，保留两列可交叉核验。

**两列的P95都是“每请求平均token耗时”的P95，不是逐token间隔的P95。** 若准确记录每个token的到达时刻，单请求所有间隔的平均等于TPOT，但间隔的P95与请求平均值的P95不同。AIPerf的ICL是流式内容chunk间隔；一个chunk可能包含多个token，不能默认ICL=逐token间隔。

例如一个请求输出3个token，两个间隔分别1ms、9ms，该请求TPOT/ITL=5ms，不能用5ms描述两个间隔的尾延迟。见 [AIPerf 0.12官方定义](https://docs.nvidia.com/aiperf/v0.12.0/reference/ai-perf-metrics-reference)。此前将本项目ITL一律解释为逐token分布是错误的。

## 分开三个数量

| 数量 | 含义 | 是否直接裁剪扫描 |
|---|---|---|
| KV驻留容量C_cache | 可保留独立预热上下文并预留Decode空间的条数 | 是 |
| Running上限 | 每个DP引擎的max_num_seqs等调度限制 | 否 |
| 客户端并发C_client | 同时在途请求总数，包含Waiting和Running | 与预设值、C_cache取最小值 |

缓存能容纳64条、max_num_seqs=16时，可以全部预热后发并发64，16条运行、其余排队。原始上下文必须在等待期间仍驻留。TTFT/E2E反映排队；TPOT不包含首token之前的等待，但可能包含首token之后的调度停顿。

max_num_seqs和max_num_batched_tokens仍作为部署扫描轴：它们影响启动内存画像、图捕获和可分配KV内存，因而**间接**改变C_cache；不能再作为显式条数上限取min。

## DP合计不能当作单rank容量

2026-11-27从60固定镜像读取的 [core_client.py](../../outputs/capacity-review-20261127/source/vllm/v1/engine/core_client.py) 明确对所有DP EngineCore返回的num_gpu_blocks求和。因此API的server-info报告DP合计；EngineCore日志中的最大并发比值则来自本地池。

| 旧部署 | server-info总块数 | DP | 每rank块数（均匀池） |
|---|---:|---:|---:|
| TP1/DP8/EP8 | 232 | 8 | **29** |
| TP2/DP4/EP8 | 1480 | 4 | **370** |

此前把232当作每rank容量，解释错误。必须优先采集每rank真实值；历史证据不足时才注明均匀池假设做除法，不能对异构DP池求平均后当作每rank容量。

旧DP8的4K/C16通过、C32失败，即每rank2条通过、4条回放失败；17～31没有测。真实池只有29块，但失败仍需区分物理容量、缓存保留策略、路由和边界状态，不能把失败标签当作精确容量测量。

## 完整容量公式

| 符号 | 含义 |
|---|---|
| L | 原始输入token数：4096/16384/65536 |
| O | 预留输出长度；本轮统一取max(128,512)=512 |
| S=L+1+O | 预留总长度；1为P端真实seed |
| B[r,p] | DP引擎r的缓存池p的物理块数，TP容量不相加 |
| R[r,p] | 不可用于请求的块，如null block；每池扣一次 |
| a[g] | 普通attention组g每块容纳的token数 |
| b[r,p](L,O) | 一条独立上下文在池p中的驻留+输出预留块数 |

普通完整Attention组的主体需求是`ceil(S/a[g])`。混合模型在同一个池里把各组实际需求相加：

```text
b = Attention输入及输出块
  + 原始前缀需要保留的KDA状态
  + Decode正在更新的KDA状态
  + 后端确实需要的ring / checkpoint / 写时复制块
```

同一物理块被多处引用只算一次。KDA不是“每token保存完整状态”，不能把Mamba的block_size当成Attention页大小。W8A8也不意味着KV一定是INT8。

若b是可加、覆盖预热和回放峰值的可靠预算，每rank容量为：

```text
K[r] = min_p floor((B[r,p]−R[r,p]) / b[r,p](L,O))
```

这里**没有max_num_seqs，也没有max_num_batched_tokens**。为每条请求预留完整输出空间，不借助“只有16条Running”挤出更大容量。

更精确地，如果块共享或预热临时峰值不能用可加预算表达，应计算物理块集合：

```text
Demand[r,p](n,L,O) = max over t |在时刻t必须保留的物理块集合|
K[r] = max n，使全部池满足 Demand[r,p](n,L,O) <= B[r,p]−R[r,p]
```

时间范围包括逐槽seed/边界填充、保留所有原始上下文、完整输出、四次回放和两种输出切换。失效但可淘汰的旧缓存不是“必须保留集合”；缓存策略未及时淘汰它们造成的失败单独归因。

## DP聚合与扫描点

固定路由slot_id%DP时，C条请求分给rank r的条数为：

```text
n[r](C) = floor(C/DP) + (1 if r < C%DP else 0)
C_cache = min_r(DP*K[r]+r)   # r从0开始
```

均匀池简化为`C_cache=DP*K`。异构池不能简单相加，否则轮询路由可能先挤满某个rank。

```text
C_scan = sorted(unique(min(c,C_cache) for c in 预设并发数组))
N_requests = 实际并发 × 4
```

容量24、预设[1,2,4,8,16,32,64,128]时，扫描[1,2,4,8,16,24]，最后一点96请求。即使max_num_seqs=16也保留24。容量0不生成计时点；但保守估计为0时应收紧预算或验证，不能宣称物理容量为0。

## 实际历史池的数值重算

完整表、来源和复算脚本见 [容量重算报告](../../outputs/capacity-review-20261127/README.md)。当前有6种EP/并行组合的历史池，另2种无对应快照。

这些历史GLM组的启动容量模型可以复核为：

```text
b_runtime(S) = ceil(S/A) + 4×2 + 1 = ceil(S/A)+9
```

含一个完整Attention组、四个align-mode KDA组、一个ring组。用日志最大长度代入，`每rank块数/b_runtime`与6份server-info的kv_cache_max_concurrency一致，是DP总块数解释的交叉证据。

反复复用还需保护原始状态。报告使用**显式保守假设**：每个KDA组另留1块原始前缀状态，另留1块Attention尾页副本：

```text
b_reserved(S) = ceil(S/A)+9+4+1 = ceil(S/A)+14
K_budget = floor((B_rank−1)/b_reserved(S))
```

这是可复算预算，**不是已测出的精确最大条数**。状态可能与运行态共享，真实上限可以更高；缓存策略也可能使可达容量低于预算，仍需峰值/回放验证。14仅对应该历史布局和这些预留假设，不是所有vLLM模型的通用常数。

例：旧TP2/DP4/EP8，1480/4=370块/rank，A=2176，L=4096，O=512：

```text
S = 4096+1+512 = 4609
Attention页数 = ceil(4609/2176) = 3
b_reserved = 3+14 = 17
每rank预算 = floor((370−1)/17) = 21
总预算 = 4×21 = 84
扫描 = [1,2,4,8,16,32,64,84]
```

这不会被max_num_seqs=16裁成64。并发84时每rank21条在途，最多16条同时调度。

## 可选的边界调查算法（本轮不执行）

1. 展开48种部署，逐个启动采集每rank池、组规格、真实auto长度和配置指纹。不复用另一EP开关或token预算的容量。
2. 每个L按512输出预留，检查`L+1+512 <= resolved_max_model_len`。不满足则记录长度超限，不暗改输入。
3. 按组规格计算块集合或可加预算；每项写明来源：主体页、原始状态、工作状态、副本、固定保留块。
4. 按候选容量逐槽seed、边界填充并固定DP路由，采集池峰值、原始上下文驻留情况。
5. 两种输出、每槽4次回放都验证；只回放1/2 token不能证明完整Decode安全。
6. 若预算保守，逐步增加到首个**确认的容量不足**，再定位最后通过与首个不足之间的整数边界，复验边界及边界+1。只有确认需求单调时才二分。路由、边界状态或非法访存故障不当作容量上界。
7. 记录预算、最后通过、首个容量不足、未验证区间。只测到128且通过，要写“至少128”，不能写“最大128”。
8. 用最终确认容量裁剪预设数组、去重并重新计算请求数。计时阶段仍逐请求验证L全命中、query=1、无抢占和输出长度。

## 新矩阵状态

48种部署=4个TP/DP形态×2个EP开关×2个max_num_seqs×3个token预算，模型长度auto、图模式开启。预设并发为`[1,2,4,8,16,32,48,64,80,96,112,128]`，乘以3种输入和2种输出，裁剪前3456个计时点。

2026-11-27先启动独立容量预检，随后按用户要求停止，切换为正式矩阵扫描。历史容量表仍只作对照，新配置使用本轮每个DP引擎的实际池计算预算。启动任务不代表全部测完。

正式扫描不搜索整数边界。每rank使用引擎按`L+1+max(O)`解析的组需求之和，加4个原始KDA状态块及1个Attention尾页副本，扣除池固定预留后取整。只接受已核对的4个align-mode Mamba组、1个MLA组、1个ring组；布局不匹配时报错，不能套用常数。通过2-token短检查确认预热/路由后，完整输出与4轮复用的检查在正式计时请求中完成，无效点单独留档。

每个输出长度及重复轮都独立清理前缀缓存、使用固定seed重新准备相同输入；只在当前计时轮的4次请求内保留缓存。资格请求ID包含完整尝试路径的摘要，避免不同`warmup`目录的观测混淆。共同预热失败重试耗尽后，该输入/并发组的其他输出标记阻塞；重复设备非法访存则隔离整个部署，剩余点未测，不称为成功完成。

在目标Linux主机的项目根目录执行（需可用的模型、镜像、设备和Python依赖）：

```bash
python -m benchmark.load.matrix_run benchmark-matrix.yaml \
  --out experiments/runs/glm53-matrix \
  --cache-dir "$PWD/experiments/cache"
```

结果包含：`matrix.yaml`冻结输入、`identity.json`身份记录、`expanded-deployments.json`部署清单、每次启动的`launch.json`/`server-info.json`/`per-rank-capacity.json`、每个长度的`capacity-l*.json`预算和预设到实际并发映射，以及性能`summary.csv`/`README.md`。请求数按实际并发×4重新计算。模型启动失败、长度超限、协议错误均保留证据，不伪造容量值。

远端控制器及轻量结果收集说明见 [正式扫描记录](../../outputs/matrix-scan-20261127/README.md)。[旧预检记录](../../outputs/capacity-scan-20261127/README.md)仅作历史证据。
