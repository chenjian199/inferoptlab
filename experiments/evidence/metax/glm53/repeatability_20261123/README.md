# GLM greedy 重复性排查

观察日期：2026-11-23。保留 `../baseline_ops/` 的 HumanEval v1 原始分数、文件与归档；本目录是新的诊断实验，不覆盖或刷新 gold。

本轮已完成。先读 [REPORT.md](REPORT.md) 查看实测结论与尚未解决的历史归因，再读 [REGRESSION_POLICY.md](../../../../../catalog/library/metax/methods/regression-policy.md) 和 `configs/regression_policy-v1.json` 执行后续算子验收。三个新 runner 进程加原版 runner 对照均为31/32且逐 token 一致；108次诊断的同路径比较全等。不能据此宣称所有请求确定或历史问题已修复。

远程根目录 `/home/metax/glm53-repeatability-20261123`，容器 `glm53-repeat-v1`。复用同一固定镜像和只读基线源码、只读权重；新建脚本、输入、缓存与结果目录。已有 9,334 个源码文件及 8 个符号链接与冻结 archive 核对一致。

## 已冻结实验设计

| 进程 | 执行内容 | 目的 |
|---|---|---|
| A | 固定 smoke32 同序执行两遍 | 同进程重复 |
| B | 新进程同序 smoke32，再倒序 smoke32 | 跨进程及顺序影响 |
| C | 新进程同序 smoke32；历史 9 题启用 top-5 logprobs 执行两遍 | 跨进程及自由生成首处分歧 |
| D1 / D2 | 两个额外新进程；9 个共同前缀分别按 prefill / 强制前缀 cached decode 执行，各重复三遍 | 共108个目标决策的层输出、完整 processed logits、greedy 决策与跨进程数值变化 |
| Legacy | 额外新进程；原版生成脚本的 smoke32 流程 | 排除新 runner 的导入、tokenizer 与预检流程差异 |

全程共享八卡资源锁，阶段串行。A/B/C 的 plain 请求参数与原始基线一致，输入直接使用冻结 token IDs。D1/D2 的前缀由历史两份输出的共同 token 前缀构成；同时测试整体 prefill，以及通过 V2 `trace_decode_token_ids` 强制历史共同前缀后的目标决策。后者保持 cached decode 路径，但不冒充历史运行状态的精确重放。由于 input processor 将生成长度截到 trace 长度，cached 探针追加一个终止占位 token，并在 trace 覆盖之前保存 sampler 的实际 greedy 决策和 logits；返回序列的最后一个占位 token 不能用作模型决策。启用 trace replay 和采集层输出会改变执行条件、同步 GPU，因此诊断结果与无 hook 的功能评测分开解释。

v4 首次 cached 探针因上述长度语义触发断言退出，证据保存在 `evidence/failed_diagnostic_v4/`。v5 修正诊断脚本后另起进程；不修改推理源码、不删除失败证据，失败探针不计入正式108次观测。

编译缓存从原实验复制到新目录；原缓存不写入。一个 root-only 的 vLLM modelinfos JSON 未复制，在新目录重新生成。日志仍可能出现新 shape 的 JIT 编译；不声称所有请求都是纯热缓存。本轮没有启用或验证上游 batch-invariant 开关，也没有改动算子实现。

## 目录

- `configs/plan.json`：A/B/C 在运行前冻结的设置、顺序和采样参数。
- `data/`：原始冻结 prompt/token manifest、9 个共同前缀探针；不含隐藏测试或 canonical solution。
- `harness/`：独立进程生成、隔离评分、层/logit 观察、离线分析和功能回归检查。
- `runs/`：每轮不可覆盖的生成和评分结果。
- `evidence/`：实际进程、源码核对和诊断证据。诊断脚本在执行前的修订单独留存，plain runner 未改变。
- `WORK_STATE.json`：当前状态。
- `REGRESSION_POLICY.md`：后续算子替换的判定方法与尚待校准的数值边界。

本轮评分器只将 ROOT 改为新实验目录，代码提取逻辑、原始测试、沙箱镜像与资源限制沿用已验证版本。评分前后记录源码哈希，不把新 evaluator 文件哈希误认为新的评分算法。

本地检查：

```powershell
& 'D:\anaconda\anaconda\python.exe' -B -m unittest discover -s glmf/repeatability_20261123/harness -p 'test_*.py'
& 'D:\anaconda\anaconda\python.exe' -B glmf/repeatability_20261123/harness/verify_experiment.py
```

分析脚本拒绝覆盖汇总；只有全部计划运行生成、评分完成后才生成最终结论。`analyze_tensors.py` 在固定镜像中以 CPU 方式分析本任务自产生的张量（`weights_only=True`），不会执行模型答案。

本次目录已冻结，重新生成/分析应创建新的实验目录并明确修改 ROOT 和运行标签，不直接重跑写入当前目录的脚本。`check_functional_gate.py --baseline B0_1 B0_2 B0_3 --candidate C_1 C_2 C_3 --scope full164 --output NEW_RESULT.json` 仅是功能层检查入口；输入格式见本次 generation manifest，独立进程、全局输入哈希、局部和模型数值层仍须按规则验证。
