# 评测与基准执行入口

HumanEval 生成和隔离评分已实现。2026-11-23 的执行源码逐文件副本位于 `../evidence/humaneval_v1/harness-executed/`，其 SHA256 与 `../configs/humaneval_regression.frozen.json` 对应。历史执行副本不可覆盖。原部署脚本位于 `../../deploy032/`，原容器及输出保留。

## 已实现的 HumanEval 流程

- `prepare_dataset.py`：固定官方数据集 revision，验证 164 个唯一 ID，分离 prompt 与评分材料，保存确定的 smoke32 IDs。
- `generate_humaneval.py`：独立 TP8 容器中离线生成；每题一次、逐题落盘，先 smoke32，经评分完成 gate 后跑 full164。保存完整输出、token IDs、停止原因和每卡源码/INT8 状态。历史版本中的主机路径、容器名和协议位置固定于本次部署。
- `run_generation_host.py`：持有八卡实验锁，执行环境检查和生成，保留进程退出状态。历史版本的 label 固定，不能原地重复运行。
- `code_adapter.py`：冻结的代码提取规则；不修补缺失缩进，不按测试结果修改答案。
- `evaluate_humaneval.py`：主机调度、每题一个无网络 CPU Docker 沙箱，非 root、只读根文件系统、无挂载/GPU、限制内存/进程/CPU/时间。只使用原始 HumanEval tests，不使用 HumanEval+。
- `summarize_baseline.py`：离线汇总完整分数，逐题比较 smoke32 与 full164 重叠题，报告 token 差异和通过/失败迁移。

隔离评分先用全部 164 个 canonical solutions 验证，再检查错误断言、无限循环、提前退出和隔离属性。生成失败不重新采样；基础设施错误使整轮不完整。Docker 共享主机内核，此处记录的是已检查的容器隔离条件，不宣称虚拟机级隔离。

生成入口使用原始配置 `protocol-v1.json`；其中 `draft`/`null` 是 pilot 前模板的历史字面值。正式全量运行前，具体生效设置、模板/tokenizer/代码哈希、沙箱限制和 pilot 结果已写入单独的 `protocol-v1.frozen.json`，本地副本为 `../configs/humaneval_regression.frozen.json`。评估与复现以这份冻结包及实际运行清单共同为准，不能将原模板中的空值解释为运行时未设置。

本次部署命令和只读结果重算见 [复现说明](../../../../../../catalog/library/metax/methods/humaneval.md)。这些历史脚本不会自动为下一轮创建完整新环境；新轮次必须先复制到新实验根目录并修订路径/label，或实现新的参数化 launcher，保证结果和 evidence 不被覆盖。

## 后续模块

| 待实现模块 | 职责 |
|---|---|
| 通用 preflight/launcher | 将本轮固定部署脚本参数化，支持新的实验目录、容器和不可覆盖的证据 |
| compare_correctness | 扩展现有逐题比较到任意 B0/候选输入，绑定协议哈希和环境 |
| benchmark_model | 固定性能矩阵、预热、同步和多轮配对测量；不复用功能评测总耗时作性能基准 |
| profile_and_capture | 只在诊断运行采集真实热点、shape、rank 和输入/state 契约 |
| report | 校验 run 完整性，分别汇总功能、数值和性能结果，记录证据路径与哈希 |

约束：每轮独立 `run_id`，输出目录必须新建；配置为 draft/null 时不能启动正式验收。运行时保存生效参数，不能依赖旧脚本中的默认值。失败必须有明确状态/退出码；未实现模块不能生成伪通过结果。生成、评分、性能与 profile 各自记录时间和资源，不将探针开销混入正式性能数据。
