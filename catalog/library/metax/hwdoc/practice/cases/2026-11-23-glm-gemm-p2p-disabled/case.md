# 重启后禁用 P2P 完成八卡 GEMM 单层替换对照

观察日期：2026-11-23。适用环境：H3C R5330 G7、C500 ×8、驱动 3.10.14；独立镜像 SHA256 `9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`。**本轮单层替换筛查通过，MetaXLink 故障仍未修复。** 完整命令、配置与证据入口见[实验报告](../../../../../../../experiments/evidence/metax/glm53/reboot_recheck_20261123/REPORT.md)。

## 重启后的硬件与通信边界

用户执行普通 reboot 后，boot_id 已变化。首次 GPU 作业前八卡均 Available，但卡6/7 的 port4 已为 x4，卡6该口 down、CE=2/UE=0，卡7该口 up。普通系统重启没有恢复该链路；不能将设备 Available 等同于互联健康。

只在新实验容器 `glm53-gemm-reboot-v1` 设置 `MCCL_P2P_DISABLE=1`，模型设置 `disable_custom_all_reduce=True`。文档依据为《沐曦通用GPU_MCCL编程指南》V08、物理 PDF 第32页 §4.2.2.21，禁用 PCIe 或 MetaXLink P2P，见[原PDF](../../../沐曦通用GPU_MCCL编程指南_CN_V08.pdf#page=32)。八卡小矩阵计算和 1/16/1024 元素 all-reduce 均通过；小型通信诊断日志观察到 SHM/direct/direct，不将其扩展为完整模型的传输抓包证明。

助手本轮没有重启、热复位或修改驱动。结束后八卡 Available、无 GPU 进程、驱动引用数0；卡6该口仍 down/x4、CE=2/UE=0，所选内核错误/状态事件无新增。故障具体硬件、固件或驱动原因仍待定位。证据为 `evidence/hardware_summary.json` 与 `evidence/transport_summary.json`。

## 实际加载环境与替换范围

实际加载 `/work/src/vllm` 和 `/work/src/vllm-metax`。展开源码没有 Git 元数据，改为对冻结源码归档逐文件核验：9,334 文件全部一致。来源记录为 vLLM `5df63a7203cdb9328d824a27b682e77c7b9928be`、vLLM-MetaX `0962c8735ffe4795800030680311410848512b82` 加原冻结修复，不声称本轮读取到 Git HEAD。

依赖实测：torch `2.10.0+metax3.9.0.8`、mcTriton `3.6.0+metax3.9.0.8`、mcoplib `0.4.14+gf3794c4.maca3.9.0.31.torch2.10`、vLLM `0.32.0+empty`、vLLM-MetaX `0.32.0+g0962c8.d20261122.maca3.9.0.29.torch2.10.0`。

八个 rank 仅替换 `language_model.model.layers.0.mlp.gate_up_proj`：`MergedColumnParallelLinear`、`CompressedTensorsW8A8Int8`，原内核为 `MctlassScaledMMLinearKernel`。INT8 权重 [K,N]=[4096,3072]，无 bias；保留原激活量化。候选返回自编 mcTriton GEMM 的结果，同时执行原内核作影子数值校验；不是原内核结果伪装为候选。未全局替换其他层。

## 同期原32、候选32、恢复4结果

同一 TP8 引擎依次执行三个阶段；固定 HumanEval 输入 token、greedy 配置、V2/eager、单序列，沿用隔离 CPU 评分。没有按测试修补生成程序或追加采样。

| 阶段 | 功能通过 | 对照结果 |
|---|---|---|
| 原实现32题 | 30/32 | HumanEval/110、37失败 |
| 候选32题 | 31/32 | 无原通过题退化；37转为通过，110仍失败 |
| 恢复原实现4题 | 4/4 | 四题 token 与原阶段完全一致 |

候选与原实现 24/32 题 token 完全相同，8题不同；三阶段均无截断、无评分基础设施错误。单轮多通过一题不证明候选普遍提升精度，也不解释历史相同 greedy 配置的9题分叉。逐题对照见 `evidence/comparison_summary.json`。

八个 rank 共执行候选 11,936 次、fallback=0，最大差异1个 BF16 ULP，最大绝对误差0.0009765625，符合事先契约。覆盖29种 [M,N,K]：N=3072、K=4096，M=1及28种96～356的 prefill 长度。保存每 rank 的首个 prefill/decode 共16份真实模型输入选定行列且保留完整K；整数累加对 CPU INT64 精确，明确顺序的 FP32 参考精确，FP64 参考在1 ULP内。证据摘要见 `evidence/verification_summary.json`，原始张量留在实验目录。

## 保留、复核与未验证范围

本次容器已停止。对照重启后初始快照，原六个容器身份、镜像、挂载及状态不变；历史基线65、重复性135、GEMM原型69及前次恢复33文件校验通过。新归档89文件已核验本地与远程 SHA256 及成员哈希；登记见 `artifacts.json`。离线复核入口：`python -B glmf/reboot_recheck_20261123/verify_results.py`。

只通过本轮备用通信路径下、单引擎、单层、32/32/4筛查。未完成全164题、多独立进程、固定前缀数值验收或性能验收；影子校验开销使本轮耗时不能作为优化性能结论。默认 P2P 和性能基线应等待维护方恢复互联链路。此记录接续[热复位复发案例](../2026-11-23-c500-warm-reset-recurrence/case.md)，不覆盖历史失败证据。
