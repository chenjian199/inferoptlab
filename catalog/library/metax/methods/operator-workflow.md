# GLM 模型基线与算子优化交接

> 2026-11-23 进展补充：本文下方保留 2026-11-22 的交接快照。后续已在独立 `glm53-heval-v1` 环境实现 HumanEval 固定数据、生成和隔离评分，先完成 smoke32（31/32），再完成全量（153/164，93.2927%）。最新入口为 [基线报告](../../../../experiments/evidence/metax/glm53/baseline_ops/BASELINE_REPORT.md) 和 [复现说明](humaneval.md)。数据/harness“尚未实现”的历史描述不再代表现状；性能、logits、独立进程重复性和算子替换仍待推进。32 个重叠题仅 23 个输出 token 完全一致，不能把 greedy 当作严格确定性保证。旧 dcc 和部署容器保留。

交接日期：2026-11-22，Asia/Shanghai。目标模型为 **GLM-5.3-Flash-W8A8，8×C500，TP8**。本文供新的工作分支或对话继续执行，包含现有成果、实验设计和交付门槛；后续基线与算子流程尚未实现或测量。

下一阶段顺序：**复现冻结环境 → 建立整模型正确性基线 → 建立整模型性能基线 → 提取实际热点算子 → 局部等价性与性能验证 → 单算子集成 → 整模型回归 → 冻结候选版本。** 先保留当前 vLLM 路线，SGLang 对照另立实验，避免同时改变框架、依赖与算子。

## 接手入口与保护范围

先读项目 [AGENTS.md](../../../../experiments/evidence/metax/intake/received-agents.md)、[实践知识库](../hwdoc/practice/README.md)、[已完成的部署案例](../hwdoc/practice/cases/2026-11-22-glm53-w8a8-tp8/README.md) 和 [问题与补丁](../hwdoc/practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)。精确的证据来源和 SHA256 以 [artifacts.json](../hwdoc/practice/cases/2026-11-22-glm53-w8a8-tp8/artifacts.json) 为准，当前部署记录为 [deployment_state.json](../../../../experiments/evidence/metax/glm53/deploy032/deployment_state.json)。

访问目标服务器沿用已有的跳板机连接方式：`inspur@172.16.0.38` → `metax@192.168.10.94`。凭据通过既有安全渠道使用，本文不保存密码、MIM 密钥、代理认证或订阅。MIM 登录和 Mihomo 代理已经配置过；先查看现状，不重复配置。原始 MIM 镜像未完整下载，当前可用基线是独立重建镜像。

必须保留 `dcc`、现有 `glm53-vllm032` 部署基线、旧源码、宿主驱动/SDK、标准模型文件及历史证据。新工作使用独立容器、源码工作区、缓存和输出目录。两个容器共享同一组 GPU，容器隔离不提供性能资源隔离；先检查 GPU 进程、显存、温度/功耗状态与其他作业，在共同的八卡资源锁下串行运行基线和候选。资源冲突时延后测量，不停止无关进程。

本次交接只创建文档，没有创建 Git 分支、启动服务或执行远程实验。本地 `H:\workspace\C500模型优化` 不是已确认的 Git checkout；实际框架仓库在远程源码目录。进入新分支时先确认仓库根、工作区差异和基点，再建立分支或独立 checkout，不对整个资料目录擅自 `git init`，不切换原运行容器挂载的源码分支。若新分支是对话分支，将本文作为首个上下文入口即可。

## 已有部署基线与尚未完成的验证

当前成果称为 **D0 部署功能基线**。后续建立的 **B0** 是从 D0 复现并补齐正确性、性能测量的实验对照；候选算子版本称为 **C1、C2…**。B0 含已有三项兼容修复，不以未修复的上游源码作为正常对照。

| 项目 | 已保存的事实 |
|---|---|
| 设备和系统 | 8×C500，每卡 64 GiB；Ubuntu 22.04.5；宿主驱动 3.8.30 |
| 容器用户态 | MACA SDK 3.9.0.29；Python 3.12 |
| 上游源码 | vLLM v0.32.0，`5df63a7203cdb9328d824a27b682e77c7b9928be` |
| 插件源码 | vLLM-MetaX v0.32.0-dev，`0962c8735ffe4795800030680311410848512b82` 加三项局部修复 |
| 核心依赖 | Torch `2.10.0+metax3.9.0.8`；Triton `3.6.0+metax3.9.0.8`；mcoplib `0.4.14+gf3794c4.maca3.9.0.31.torch2.10` |
| Python 包 | Transformers 5.17.0；compressed-tensors 0.17.0；完整清单见 [environment_packages.json](../../../../experiments/evidence/metax/glm53/deploy032/evidence/environment_packages.json) |
| 实际导入 | `/work/src/vllm/vllm/__init__.py`；`/work/src/vllm-metax/vllm_metax/__init__.py`；平台 `MxsmlMacaPlatform` |
| 权重路径 | 宿主 `/NFS_62/Models/GLM_Series/GLM-5.3-Flash-W8A8`，容器只读 `/models/GLM-5.3-Flash-W8A8` |
| 权重 revision | ModelScope `metax-tech/GLM-5.3-Flash-W8A8`，`6df7a9b0309e530094e29b2a6ced3e21bed6c16d` |
| 权重完整性 | 59/59 文件哈希验证，47 分片，76108 张量；原索引 `total_size=[]` 未修改，结构检查因此保留 `complete=false`，张量数据/映射检查通过 |
| 运行配置 | TP8、mp、V2 runner、BF16 非量化部分、compressed-tensors W8A8、4K 上下文、单序列、同步调度、eager、prefix cache 关闭 |
| 真实生成 | 中文介绍、算术 2、2433 输入 token 中检索“青松”通过，均正常 stop |
| 新容器验证 | 实际导入路径、8 设备发现、pip check 通过；没有重新执行完整模型生成 |

**尚无合格的整模型性能基线或系统正确性基线。** 已有 3 个生成用例是 smoke，不是质量评测；约 184.47 秒加载与 57.39 秒生成阶段耗时含初始化/JIT 影响，不可作为吞吐、TTFT 或算子优化收益。高并发、异步调度、图执行、超过 4K、多模态与 SGLang 均未验收。V1 曾非法访问显存，最终 scale 修复后没有重测，不能视为问题已解决。

保留三项修复：MoE alignment 的 7/8 参数 ABI 桥接、INT8 sparse indexer 的 Tensor Q 契约、FP8 回退加载器对 INT8 `weight_scale` 的所有权修复。源码资产为 [tracked patch](../../../../experiments/evidence/metax/glm53/deploy032/evidence/vllm-metax_deployment.patch) **加** [新增 ABI 模块](../../../../experiments/evidence/metax/glm53/deploy032/moe_align_legacy_abi.py)，或匹配的完整源码归档；单独 git diff 会漏新增文件。

## 恢复和冻结 B0 的第一批工作

| 资产 | 标识 |
|---|---|
| 镜像 tag | `glm53-vllm032:verified-20261122` |
| 镜像 ID | `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285` |
| 源码包 | `/home/metax/glm53-vllm032/baseline/sources-20261122.tar.gz` |
| 源码包 SHA256 | `da769ed300e32876f2bd358a1c537a8618f7fdbc8f56830eacfec57f6d1ab592` |
| 脚本包 | `/home/metax/glm53-vllm032/baseline/deployment-scripts-20261122.tar.gz` |
| 脚本包 SHA256 | `d62bdbf93b61785422931fdde5b5cc4da960829645f729ddae38e094bc61d83f` |

这些是观察日的远程资产，不保证当前仍存在；先重新核对。依赖镜像依靠 editable 源码和编译产物挂载，必须恢复配套源码、脚本和只读权重。不要直接用该镜像 ID 启动后就宣布复现成功。

1. 保存当前宿主设备、驱动、容器、GPU 占用和源目录只读快照。检查上述哈希及权重 manifest；记录实际值，不能只拷贝旧 JSON 当新证据。
2. 建议建立 `/home/metax/glm53-baseline-ops/`，容器采用新的任务名。B0 和候选源码各自独立挂载，JIT/编译缓存分别管理。基线源码冻结后只读，缓存写入独立目录；每次运行都保存源码和缓存策略。
3. 参考 [create_bootstrap.sh](../../../../experiments/evidence/metax/glm53/deploy032/create_bootstrap.sh) 改造成接受任务名、根目录、image ID 的新入口。原脚本硬编码旧任务名，已存在同名容器时会复用；设置 `GLM53_IMAGE` 不会替换旧容器。不要原样执行它来创建新实验环境。
4. 重新验证每个 rank 的源码、版本、native 扩展、八卡计算和通信。使用基线原配置重新跑完整模型 smoke，补上“新容器完整推理”缺口。
5. 把三项兼容修复明确保存为 B0 patch/commit，记录 untracked 文件和哈希。若导入失败、scale 不合法、出现非法显存访问或输出回归，先恢复 D0 等价环境，暂停性能采样。

原 [run_inference.sh](../../../../experiments/evidence/metax/glm53/deploy032/run_inference.sh) 显式设置 V2、单序列和同步调度；直接运行 [infer_smoke.py](../../../../experiments/evidence/metax/glm53/deploy032/infer_smoke.py) 的默认 `max_num_seqs=2`，且不一定关闭异步，**不是相同配置**。新入口必须显式固定所有关键参数，并将 `report`、日志和锁改到新目录，避免覆盖 `/work/evidence/inference_smoke.json`。

## 整模型正确性基线

正确性需要三个互补的参照：B0 对照用于发现优化回归；小规模独立数学参考用于发现原实现与新实现共同的错误；有确定答案的数据用于检查模型任务表现。B0 本身不是数学真值，也不能用同一 W8A8 模型的自对照证明量化相对 BF16 无损。当前没有验证过完整 BF16 高精度模型参照；若以后补建，另记精度和资源条件。

### 固定输入与两条生成路线

首个公开任务回归已选定 HumanEval test 全量 164 题，每题一次生成，详见 [数据集选型](../../../../experiments/datasets/humaneval/SELECTION.md)；固定 32 题子集仅用于调通，不替代全量分数。数据尚未下载，评测协议待试运行冻结。另保留已有 3 个部署 smoke，并后续补充固定文本/token/logits 诊断样例，覆盖中文、英文、数字、JSON、重复输入、长前缀、不同上下文长度及请求间状态重置。HumanEval 编程题不能替代这些覆盖；本阶段不再把原建议的自定义 64 题作为首个正式任务基准。

每个样例保存 ID、来源/许可、原始文本、模板参数、实际 token IDs、长度、答案规则和 SHA256；约束模板后的输入长度加输出预算不超过 4096。tokenizer、chat_template、reasoning_effort、特殊 token 和停止规则都进入配置指纹。重复/合成性能输入与真实质量输入分开保存。

- **部署复现路线**：保留 temperature=1、top_p=0.95、seed=0、reasoning_effort=low 的原 smoke 配置，只判断任务答案和停止行为。固定 seed 不保证多卡逐 token 确定性。
- **诊断回归路线**：新增 greedy/确定性配置，用于定位首个分歧 token；这是待建立的新基线，不能复用旧失败或旧随机采样结果作 gold。测试集和判定规则先冻结，再运行候选。
- **固定前缀路线**：为 B0 和候选喂同一组前缀/continuation token，逐位置比较 logits 或指定 token 的 logprob。不要在双方已自由生成不同前缀后直接比较后续 logits。若使用 teacher forcing，要实现并验证可访问真实计算路径的工具，不能假设当前 API 自动支持所需数据。

### 数值和任务判定

先在 B0 独立重复运行，至少覆盖多次进程启动，量化环境自身的数值和输出抖动。把测得的波动、业务要求和局部算子误差一起用于制定阈值；阈值存入版本化配置，不能看到候选失败后放宽。

记录绝对误差、relative L2（明确分母和零范数处理）、有效位置误差分位数、top-1/top-k 一致率、首个 token 分歧位置，以及固定文本 NLL。KL 需要完整且一致归一化的分布，不能把截断 top-k 直接当完整分布计算 KL。采样位置覆盖 prefill、首个 decode 和后续 decode，保留 token 对齐信息。

要求输出与 cache 有效区域符合有限值约束；mask 中按语义允许的 `-inf` 与 padding 不应误判为数值故障。保留每个 rank 的 MLA INT8 scale 有限正值、INT8 量化路径和权重加载检查。确定答案、JSON 解析、终止条件等使用独立规则，不只判断非空输出。

发生 token 分歧时，先检查 B0 自身抖动和 top-1/top-2 margin，再看 logits 与任务正确性。除明确规定必须精确一致的集合外，不能仅用输出字符串完全一致判断浮点等价，也不能以“文本看着正常”掩盖明显数值偏差。若条件不足，结果标记为未定，不计入通过率。

交付 `correctness_dataset.jsonl`、配置和指纹、逐样例结果、B0 重复性报告、预先确定的阈值以及生成 gold 的脚本。gold 不在普通候选测试时自动刷新；基线变更必须产生新的 B0 版本。

## 整模型性能基线

### 首版负载与测量口径

第一版继续采用 D0 的 TP8、V2、同步、单序列、eager、4K 配置。建议矩阵为输入 **128、512、2048、3072 token**，分别输出 **128、512 token**，共 8 格；输入长度指模板后的实际 token 数。无法达到目标长度的样例应报不满足条件，不用字符数代替 token 数。

对性能使用固定输出预算，并记录 EOS 策略。若通过忽略 EOS 强制生成固定长度，将其标记为专用性能负载，与自然终止的正确性测试分开。保存实际输入/输出 token 数，避免因候选提前停止而产生虚假加速。

| 指标 | 口径与采集条件 |
|---|---|
| 冷启动 | 进程启动、模型加载、编译/首次运行分别计时；不混入稳态请求延迟 |
| 稳态端到端延迟 | 请求提交至最后一个输出 token 完成；说明是否含模板/tokenize、排队和输出处理 |
| TTFT | 同一测量边界内请求提交至首个 token 可见；engine 与客户端口径分别报告 |
| TPOT | 多输出 token 请求的 `(最后 token 时间 − 首 token 时间)/(输出 token 数 − 1)`；单 token 请求记为不适用 |
| ITL | 流式逐 token 间隔分布；一个 chunk 含多 token 时不能直接当逐 token 时间 |
| 吞吐 | 指定稳态区间内实际输出 token 总数/墙钟时间；输入与输出吞吐分列 |
| 显存与设备 | 每 rank 峰值分配/保留量、可观测设备显存、功耗/温度/频率及后台负载；注明采集工具和间隔 |

现有 `LLM.generate()` 只提供整批完成结果，不能从总时长反推出 TTFT/ITL。先建可靠的离线整模型延迟与吞吐，再经验证的引擎事件或流式接口补齐 token 时序。HTTP 服务目前未部署；服务级指标另建同配置实验，明确网络、序列化、排队和客户端开销。

### 稳态与统计

先预热每个 shape，直到编译结束且延迟稳定；记录预热次数和停止判据。建议起步每格 5 次预热、30 次有效请求，至少 3 轮独立测量，根据抖动延长，作为实验协议而非既定厂商规范。少量样本不声称 p99 稳定：首版报告中位数、p90、离散程度和区间估计；要报告尾延迟应扩大样本并说明不确定性。

B0 与候选串行交替按 A/B/B/A 顺序测量，使用相同数据、顺序和运行配置。区间估计以独立轮次或成组请求为统计单位，不把同一请求内高度相关的 token 当独立样本。预先规定可接受回退和最小有意义收益；若 B0 噪声已大于目标收益，先解决测量稳定性。首轮可把 3% 延迟回退作为调查触发线，但它不是已批准的统一验收阈值，须依据 B0 波动校准并冻结。

常规基准关闭 profiler 和逐层 hooks，避免探针改变性能；profile 单独运行。主机计时必须覆盖设备完成，避免只测异步 launch；多 stream 和 TP8 使用经验证的同步/事件边界，整模型以请求实际完成墙钟为主。冷缓存、热缓存、编译缓存命中与 KV cache 策略分别记录，不能混合聚合。

并发 2/4/8、异步、图执行和更长上下文属于下一阶段的新配置基线。必须先通过各配置的正确性验证，再测性能；不要将它们与 B0 单序列结果混算收益。

## 从模型提取可复现算子

先基于真实负载 profile，再决定优化对象。用运行时调用定位 Python 模块 → dispatcher/算子 schema → native 或 Triton kernel，并记录实际选择的分支。已有数值检查可以复用思路，但不代表其中的随机形状覆盖了模型热点。

候选范围包括 W8A8 linear、量化与 scale 处理、MoE routing/alignment/experts、sparse indexer、稀疏 MLA、KDA prefill/decode 和通信。这里只是候选清单，优先级由 profile 决定。区分每次调用耗时、调用次数、整请求累计耗时和关键路径；有重叠执行时不能将所有 kernel 时间相加当整模型墙钟。建议先选高占比、边界清晰且能独立重放的单一算子。

### 算子清单与输入契约

每条提取记录至少包含：

- 稳定 operator ID、层/模块路径、phase（prefill/decode）、step、rank、TP/EP 切分方式、实际函数/schema、源码 commit 和 kernel 实现哈希。
- 每个输入/输出的 shape、dtype、stride、layout、storage offset、contiguous 状态、别名关系与原地修改约定；保留实际 TP8 本地 shape，而不是直接用未切分模型维度。
- INT8 scale 的粒度、dtype、舍入/饱和规则、zero point、scale 折叠位置；MoE 的 expert IDs/map、top-k 权重及 padding；attention 的 mask、位置、序列长度、KV 布局；KDA 的历史 state 和索引。
- 设备、stream、workspace、缓存/状态输入输出、随机种子和环境开关；对通信算子保存所有参与 rank 的对应输入与集合调用顺序，不能只用一个 rank 的局部回放证明等价。
- 代表 shape 的出现次数、累计耗时和样本来源。覆盖真实分布，也补齐空输入、尾块、非连续布局、极端值和边界长度。

采用两阶段采集：先用轻量计数得到 shape/路径分布，再限额抓取代表输入。采集运行不进入性能样本。权重优先保存 tensor 名称、shard、切片/变换说明和权重哈希，重放时从只读模型恢复；必要的 activation/state 单独保存大小受控的安全张量文件和 JSON 元数据。限制总容量，避免复制整模型或全量 KV cache；使用固定测试语料，日志不含用户秘密。

保存 tensor 数值后必须能恢复 stride、alias、workspace 和状态语义；仅把所有输入转成 contiguous 会漏掉真实缺陷。先证明 **B0 捕获 → B0 重放** 在约定误差内一致，才能把该样本用于验证候选。不能重放的样本标记失败，不纳入“等价通过”统计。

## 局部等价性与算子性能验证

### 正确性三方对照

对同一冻结输入分别运行 B0 实现、候选实现和可行的小规模独立参考。INT8 参考显式重现量化/反量化、scale 广播、舍入和饱和；不要拿未量化 FP32 matmul 与完整 W8A8 路径的差异直接判为候选错误。参考不调用被测候选核，尽量减少与生产路径共享实现。

整数索引、routing、shape、mask、padding 和 ABI 行为要求按契约精确一致；浮点输出按 dtype/算子/shape 使用预先冻结的误差预算。报告最大绝对误差、relative L2、误差分布与有限性，处理全零参考和很小分母。已有 MoE 测试中的阈值只适用于当时的随机输入，不复制成全模型统一容差。

对原地或有状态算子，B0 与候选从独立且等价的输入/state 副本启动，验证输出、state 更新和未允许修改的输入。覆盖连续多步 decode、不同序列映射、padded slot、reset 和请求交替，防止仅首步正确。对替换范围外的 dtype/shape 验证 fallback；对未支持的 scatter/布局明确拒绝或回落，不静默产生结果。

### 可比较的微基准

正确性通过后再测性能。分别报告 kernel 设备执行时间与 wrapper 端到端时间；后者包括必要的转置、量化、临时分配、dispatch 和同步。输入创建、磁盘读取、首次编译不混入稳态 kernel 时间，同时单独记录编译成本、workspace 和额外内存。

验证设备事件计时在当前 MACA 后端有效；多 stream kernel 不能用错误 stream 上的事件计时。有状态算子每轮恢复相同 state，恢复时间是否计入要写明；不能循环使用不断增长或被污染的 KV/state。固定 cache 策略，对重复权重造成的热缓存与真实模型中的访问模式分别评估。

逐 shape 输出 B0/Candidate 延迟、speedup、波动、workspace 与误差；按真实出现频率/基线耗时做加权估计，并列最差回退。不能只展示最佳 shape 或简单平均 speedup。预估整模型上限可用关键路径占比和 Amdahl 关系辅助筛选，最终收益必须由整模型 A/B 确认。

## 集成替换与整模型回归

第一轮只替换一个 operator ID。实现显式的 baseline/candidate 开关，基线为默认；候选入口保留 shape、dtype、layout、quant schema 和设备约束，未覆盖输入走经过测试的 B0 fallback。开关按新实验代码实现，不在未核查的框架里假设已有同名环境变量。

| 关卡 | 必须提交的证据 | 失败后的处理 |
|---|---|---|
| G0 环境复现 | 新容器 TP8 smoke、来源/权重指纹、既有三项修复测试 | 修复环境，不开始收益比较 |
| G1 B0 冻结 | 数据集、正确性自重复、性能噪声、阈值和原始测量 | 继续校准 B0，不调整候选放行标准 |
| G2 提取有效 | B0 捕获和 B0 重放等价，真实 shape 覆盖率 | 修复输入/state 契约 |
| G3 局部通过 | 独立参考、边界/多步/fallback 用例、微基准 | 保存失败样本并回到算子实现 |
| G4 路径生效 | 8 ranks 的实现哈希、命中/fallback 计数、目标路径 profile | 定位未生效/错误 dispatch，不宣称优化 |
| G5 模型正确 | 全部冻结功能集、固定前缀/logits、生成、cache/reset、多步回归 | 用首分歧层定位；切回 B0 |
| G6 模型性能 | 相同配置的配对多轮 A/B、内存、各负载回退及区间 | 评估无收益或回退，不能只凭 kernel 加速合入 |
| G7 可恢复 | 关闭候选后回到 B0 的功能/性能范围；归档源码和报告 | 修复不可逆 patch/状态污染 |

路径验证在诊断运行采集计数，正式计时关闭昂贵探针。单卡局部测试通过不能替代 8 rank 的实际调用、布局和通信检查。正确性与性能分别保留采集模式和原始数据，避免 hooks 把回归结果与基准混在一起。

异常处理限定于当前实验容器及已确认的 worker。出现非法显存访问后结束受影响进程上下文，重新验证设备再测，不能忽略错误继续统计。任何候选都应保留一条可复现的 `baseline` 路径；不要通过卸载原 provider 或覆盖原包实现无法切回的替换。

## 建议代码和结果组织

以下目录骨架已于 2026-11-22 建立，入口为 [baseline_ops/README.md](../../../../experiments/evidence/metax/glm53/baseline_ops/README.md)。配置与算子/运行模板已存在，harness 和算子 Python 实现仍待创建，实际运行目录尚未生成。首个实现阶段先参数化 root/container/output，所有运行目录不可覆盖；协议与 harness 的版本同样计入基线。

```text
glmf/baseline_ops/
  README.md
  configs/                 # 基线环境、负载、阈值、候选开关
  datasets/                # 固定样例与 token manifest
  harness/                 # preflight、正确性、性能、profile、报告
  operators/
    <operator_id>/
      contract.json
      capture.py
      replay.py
      reference.py
      candidate.py
      test_equivalence.py
      bench.py
      integration.py
  runs/<run_id>/
    manifest.json
    environment.json
    correctness.jsonl
    performance.jsonl
    operator_coverage.json
    report.md
```

大张量、完整 trace、模型和镜像保留在服务器结果目录，以哈希引用，不进入 Git。`run_id` 使用含时区时间加配置摘要，manifest 至少记录 baseline ID、candidate ID、Git commit/dirty patch 哈希、镜像 ID、权重 revision、tokenizer/数据集/配置哈希、命令、8 rank 来源、设备状态、编译与缓存策略、起止时间、退出码、产物哈希和未完成项。

建议 harness 提供独立阶段：环境检查、部署复现、正确性 gold 生成、正确性对比、整模型性能、采集、算子重放、局部正确性、局部性能、候选集成回归和报告。正式 CLI 的名字和参数在实现时确定；不要将这些阶段描述当作当前可执行命令。

## 现有代码可复用范围

| 材料 | 用途及限制 |
|---|---|
| [infer_smoke.py](../../../../experiments/evidence/metax/glm53/deploy032/infer_smoke.py)、[run_inference.sh](../../../../experiments/evidence/metax/glm53/deploy032/run_inference.sh) | D0 的 3 请求功能复现；须参数化路径，不能作为现成性能 harness |
| [worker_provenance.py](../../../../experiments/evidence/metax/glm53/deploy032/worker_provenance.py) | rank 来源、量化与 scale 检查，包含诊断 hooks；性能运行禁用逐层采集 |
| [check_gpu8.py](../../../../experiments/evidence/metax/glm53/deploy032/check_gpu8.py) | 设备计算和通信检查；不替代完整模型验收 |
| [test_glm_mla_scale_loader.py](../../../../experiments/evidence/metax/glm53/deploy032/test_glm_mla_scale_loader.py) | INT8 scale 所有权与 FP8 fallback 回归，必须保留 |
| [test_glm_indexer_int8.py](../../../../experiments/evidence/metax/glm53/deploy032/test_glm_indexer_int8.py)、[test_moe_alignment_compat.py](../../../../experiments/evidence/metax/glm53/deploy032/test_moe_alignment_compat.py) | Tensor 契约与旧 ABI 的专项回归 |
| [test_int8_linear.py](../../../../experiments/evidence/metax/glm53/deploy032/test_int8_linear.py)、[test_sparse_mla.py](../../../../experiments/evidence/metax/glm53/deploy032/test_sparse_mla.py)、[test_kda_numerics.py](../../../../experiments/evidence/metax/glm53/deploy032/test_kda_numerics.py)、[test_moe_w8a8.py](../../../../experiments/evidence/metax/glm53/deploy032/test_moe_w8a8.py) | 独立参考的起点；补实际 shape、stride、state 与覆盖范围后再用作算子验收 |
| [test_cache_consistency.py](../../../../experiments/evidence/metax/glm53/deploy032/test_cache_consistency.py) | 排障起点；历史诊断脚本，不视为已有通过的通用 cache 回归套件 |
| [freeze_baseline.py](../../../../experiments/evidence/metax/glm53/deploy032/freeze_baseline.py)、[validate_baseline_host.py](../../../../experiments/evidence/metax/glm53/deploy032/validate_baseline_host.py) | 归档与新容器检查的参考；任务名/目录硬编码，先参数化，保留 Docker 29 解析修复 |

查工具时使用 `catalog/library/metax/hwdoc/tools/search.py --component mcprofiler`、`--component mctracer`、`--component mctriton` 和 `--component op-optimization`。本地资料是入口，实际 profiler 的命令、版本兼容性和可采指标要在该环境核对；本文不指定未经验证的厂商参数。引用 PDF 参数须回看原页并按 AGENTS 记录版本和物理页号。

## 分阶段交付与新分支起步指令

首个可交付版本只完成 G0–G1：新的可复现 B0、正确性数据和协议、稳态性能矩阵及噪声报告。接着完成一个真实热点的 G2–G7，形成可运行的算子替换样板。最后再扩展其他算子、并发与调度模式；不得为追求一次覆盖全部路径而失去稳定对照。

阶段完成后，把已实测结果追加到 `hwdoc/practice/cases/新日期-主题/`，通过 `records.json` 登记并构建索引。本文的规划不自动当作实测实践入库；后续报告明确区分计划、运行失败、通过和未验证。知识库文档维护不包含擅自重新配置代理、升级驱动或停止现有任务。

可将下面内容作为新分支首条任务：

> 请先阅读 `AGENTS.md` 和 `glmf/HANDOFF_BASELINE_OPERATOR_OPTIMIZATION.md`，以现有 GLM-5.3-Flash-W8A8 八卡部署为 D0，保留 dcc、原独立部署、宿主机和权重。先检查真实源码仓库与远程资产，在新实验目录/容器中复现 D0，补齐新容器完整 TP8 smoke，再实施 G0–G1，建立固定数据、正确性协议和稳态性能 B0。所有关键配置显式固定，原 smoke 脚本参数化后使用，不覆盖历史证据。B0 冻结后依据真实 profile 选择一个热点，按 G2–G7 完成捕获重放、独立参考、局部性能、显式开关集成和整模型 A/B 回归。不要将现有 3 个 smoke 当作完整正确性或性能基线；先报告环境核验结果、首批实现内容和实际产物路径，再逐阶段推进。
