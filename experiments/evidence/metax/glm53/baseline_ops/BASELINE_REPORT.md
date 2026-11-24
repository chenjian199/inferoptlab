# GLM-5.3-Flash-W8A8 · HumanEval v1 精度基线

观察日期：2026-11-23，Asia/Shanghai。当前状态：**模型生成与隔离评分完成；全量 153/164，pass@1 = 93.2927%**。

本轮在 8×C500 上从既有 D0 部署创建独立实验环境，评估当前 W8A8 模型在本项目固定 chat 提示协议下的 HumanEval 原始测试通过率。每题一次生成，不按测试结果重新采样、补缩进或修复答案。它是端到端编程任务精度参考，不代表完整 B0 的性能、logits 或算子等价性门槛已经建立。

## 结果

| 阶段 | 通过 / 总题数 | pass@1 | 用途 |
|---|---:|---:|---|
| Canonical solutions | 164 / 164 | 100% | 验证评分实现，不是模型分数 |
| 固定 smoke32 | 31 / 32 | 96.875% | 先行调通 |
| 全量 HumanEval | **153 / 164** | **93.2927%** | 当前模型任务精度基线 |

两轮均没有输出截断或基础设施错误。smoke32 的 `HumanEval/37` 首行缺少缩进，按固定规则记为 `parse_failure`，保留原输出，没有修复。全量 11 题均记为 `test_failure`，子进程退出码为 1；该类别包含断言失败或运行时异常，本轮未采集具体异常栈，不进一步假定失败原因。

全量失败 ID：`HumanEval/83`、`93`、`97`、`114`、`116`、`120`、`130`、`132`、`133`、`137`、`145`。完整原始输出、提交代码和评分见 run 中 JSONL；没有删除失败样例或重新生成。

重叠的 32 题：23/32 输出 token 完全一致；9 题不同，分别为 `HumanEval/10`、`37`、`89`、`94`、`123`、`144`、`148`、`156`、`162`。31 题两次均通过，`37` 由失败变为通过，无通过→失败。这是相同协议下的重复性观察，期间没有算子优化或答案修复，不能解释为优化收益。**greedy/seed=0 没有在本轮实现严格 token 重复性；原因未定位，不能直接将 token 全等设为候选验收门槛。**

全量输出 8,509 token，逐题生成耗时合计约 1,597.04 秒；隔离评分进程约 30.10 秒。前者不包含模型加载和两阶段之间的等待，不构成稳态性能基线。[机器可读汇总](baseline_summary.json) 保存逐题迁移及产物哈希。

## 固定数据与协议

- 官方数据集：[openai/openai_humaneval](https://huggingface.co/datasets/openai/openai_humaneval/tree/7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544)，test，revision `7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544`。原始 parquet SHA256：`2f2871a15fbc95b6c683043359f4ed8e144c5a1c4f24f25f66bc51f598dfcfb6`。
- 164 个唯一 task ID 与固定 smoke32 清单见 [数据 manifest](../../../../datasets/humaneval/manifest.json)。smoke 按 `SHA256("glm53-humaneval-smoke-v1:" + task_id)` 排序取前 32，未按难度或运行结果筛选。
- 每题一次，temperature=0、top_p=1、seed=0、max_tokens=1024、ignore_eos=false。提示要求续写函数并保留缩进；reasoning_effort=low。所有输入实际 token IDs 与 tokenizer/template 哈希保存在 `evidence/humaneval_v1/prompt_manifest.json`。
- 生成阶段严格只读 prompt/task_id，评分数据和 canonical solution 不挂载进推理容器。prompt 原带示例保留。
- [冻结协议](configs/humaneval_regression.frozen.json) 在 full164 开始前写入，SHA256：`b2101df2e975a6b1816b65380969d0b0caa8f93a87958a6844279c11b8514cbf`。历史 pilot 输入原样内嵌，其中 draft/null 字段由顶层实际哈希、评分限制和运行清单补齐；不是另一次未执行的协议。

## 实测软件环境

新容器为 `glm53-heval-v1`，实验目录 `/home/metax/glm53-baseline-ops`。推理镜像 ID 为 `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`。实际导入的是独立恢复后只读挂载的 `/work/src/vllm` 与 `/work/src/vllm-metax`。

| 组件 | 本轮实际导入版本 |
|---|---|
| vLLM | `0.32.0+empty` |
| vLLM-MetaX | `0.32.0+g0962c8.d20261122.maca3.9.0.29.torch2.10.0` |
| torch | `2.10.0+metax3.9.0.8` |
| triton | `3.6.0+metax3.9.0.8` |
| mcoplib | `0.4.14+gf3794c4.maca3.9.0.31.torch2.10` |
| transformers | `5.17.0` |
| compressed-tensors | `0.17.0` |

`pip check` 通过。每个 rank 已记录源码路径、V2 runner、INT8 参数以及 33 个 MLA INT8 scale 有限且为正。来源 archive 哈希核对通过；对应 D0 的 upstream commit `5df63a7203cdb9328d824a27b682e77c7b9928be`、MetaX commit `0962c8735ffe4795800030680311410848512b82` 加三项兼容修复，详见历史 D0 记录和 `source_restore.json`。

运行设置：TP8、mp、compressed-tensors、BF16 非量化计算 dtype、V2、eager、单序列、max_model_len=4096、max_num_batched_tokens=4096、显存比例 0.9、关闭 prefix caching/async scheduling。逐题验证输入长度加 1024 输出预算不超过 4096；没有静默裁剪。W8A8 checkpoint 不表示所有层都采用 INT8，实际量化类和参数 dtype 按 worker 证据记录。

标准模型目录只读挂载。本轮未重新对全部约 328 GB 权重计算哈希；权重全文件哈希证据沿用 D0 revision `6df7a9b0309e530094e29b2a6ced3e21bed6c16d` 的历史记录。原 index 的 `metadata.total_size=[]` 保留，不能把历史结构检查写成无条件完全通过。

## 隔离评分与验证边界

每题一个 CPU Docker 沙箱：无网络、无 bind mount/GPU/Docker socket，UID/GID 65534，只读根文件系统、drop all capabilities、no-new-privileges，1 CPU、512 MiB、32 PID、16 MiB 临时目录。CPU 8 秒、wall 10 秒、容器外层 45 秒，4 个评分任务并行。Python `-I -S` 仅使用标准库；镜像 ID 固定为 `sha256:96bbee871d4ea038b123276eacd65f77825b093b9255157938e0b1628e121f0b`。

164 个官方 canonical solutions 全部通过。错误断言、无限循环、提前退出和隔离属性四组自检通过；隔离探针核验非 root、no-new-privileges、seccomp、无 GPU/source/socket、不可写根目录及不可连接外网。Docker 仍共享宿主内核，不宣称虚拟机级隔离。

使用原始 HumanEval tests 和本项目冻结的 chat 代码适配/评分脚本，不是官方 leaderboard harness，也不是 HumanEval+。提取规则允许明确的完整函数或函数续写，处理 think 结束标记和单一代码围栏，但不猜测性补缩进、不修复程序。原始输出、实际提交代码及逐题评分保留。

smoke32 与 full164 使用同一已载入引擎、不同请求顺序；重叠题可用于观察重复性，不能代替独立进程 B0 自重复。不将任务通过率或输出 token 相同等同于算子数值等价。未建立 BF16 模型对照，无法据此量化 INT8 的精度损失。

## 产物与后续

- [复现说明](../../../../../catalog/library/metax/methods/humaneval.md)：生成/隔离评分入口、不可覆盖要求和后续新轮次注意事项。
- `runs/canonical_v1/`、`runs/20261123_humaneval_v1_smoke32/`、`runs/20261123_humaneval_v1_full164/`：原始结果。
- `evidence/humaneval_v1/`：输入 token、执行源码副本、版本/worker 信息、进程状态及旧容器前后核对。
- 本地代码提取、逐题比较和容器挂载比较 9 项测试已通过；离线完整性检查已通过，入口为 `harness/verify_baseline.py`，产物清单为 `artifact_manifest.json`，核验结果为 `verification.json`。
- 可迁移归档为 `archives/20261123_humaneval_v1.tar.gz`，包哈希见 `archive_receipt.json`。包含数据、执行源码、逐题结果和报告；模型权重、镜像和 D0 完整源码 archive 仍通过路径/ID/SHA256 引用，不在小型结果包中。

原 `dcc`、`glm53-vllm032` 的容器 ID、镜像 ID、创建时间、启动时间、运行状态和全部挂载字段前后相同。Docker 返回的挂载数组顺序有变化，比较时按完整条目排序，保留原始前后记录。只停止本次新建的 `glm53-heval-v1`，保留其环境与所有挂载文件；生成和评分进程均退出 0。新容器 idle `sleep` 在 stop 超时后退出 137，与模型任务失败区分。`mx-smi` 显示八卡利用率 0%、每卡 858 MiB、无进程；该查询退出码为 4、部分字段 N/A/MACA unknown，保留原输出，不将其记为完整设备健康检查通过。

任务耗时只用于记录此次精度负载成本，不代替固定输入/输出长度、预热、重复轮次和配对测量的整模型性能基线。算子替换前仍需建立独立重复性、logits/数值参考和固定性能矩阵。
