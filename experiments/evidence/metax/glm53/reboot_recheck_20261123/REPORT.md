# 普通重启后复查及备用通信路径模型对照

观察日期2026-11-23。**在仅实验环境禁用P2P后，八卡原32→候选32→恢复4对照已完成，单层替换筛查通过；MetaXLink硬件异常仍未恢复。** 用户报告已执行reboot；本轮核对boot_id由`e3fe7d15-d371-4fbd-b679-c949d7092f17`变为`02e79f83-9188-4b9a-bb4e-bed78f9e1a5e`，确认普通重启已发生。本轮助手未重启、热复位、修改驱动/固件或ACS参数。

## 重启没有修复MetaXLink

首次只读检查时尚未执行本轮任何GPU任务：八卡Available，驱动仍3.10.14，但卡6/7的port4已降为x4，卡6该口down、CE=2/UE=0。卡7该口当时显示up，与卡6不对称。普通reboot不等于断电冷启动，也不构成硬件恢复证明。证据`evidence/preflight.json`、`boot_link_events.json`。

基于明确异常的链路，本轮未重试默认P2P的八卡负载，也没有第二次热复位。改为在**新的实验容器**中设置`MCCL_P2P_DISABLE=1`，模型同时设置`disable_custom_all_reduce=True`，原环境配置不变。此设置是绕过P2P路径的验证，不是修复链路。

环境变量依据：《沐曦通用GPU_MCCL编程指南》V08，物理PDF第32页§4.2.2.21，禁用基于PCIe或MetaXLink的P2P传输；原文已核对，见[原PDF](../../../../../catalog/library/metax/hwdoc/沐曦通用GPU_MCCL编程指南_CN_V08.pdf#page=32)。实际传输还需结合本轮日志，不能仅按变量推断。

本轮已核对实际加载路径`/work/src/vllm`及`/work/src/vllm-metax`；它们是冻结归档的展开目录，没有Git元数据，`git rev-parse`返回128，不以空输出冒充commit。改为与原`sources-20261122.tar.gz`逐文件比较，9,334文件全部一致，归档SHA256为`da769ed300e32876f2bd358a1c537a8618f7fdbc8f56830eacfec57f6d1ab592`。来源commit沿用原归档记录，当前文件一致性由哈希证明。详细见`pilot/evidence/source_archive_check.json`。

## 独立环境和通信检查

容器`glm53-gemm-reboot-v1`，远程根目录`/home/metax/glm53-reboot-recheck-20261123/pilot`，镜像固定`9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`；只读原冻结源码/权重、独立缓存/结果。完整创建命令、配置、输入哈希见`pilot/container_plan.json`、`inputs_sha256.json`及`evidence/runtime_scope.json`。驱动仍3.10.14，与历史153/164基线的3.8.30不同。

八卡各自8×8 FP32矩阵计算对CPU参考精确；1/16/1024元素all-reduce在所有rank均得到36，进程退出0。MCCL INFO通道日志显示SHM/direct/direct。各卡计算和通信分别保存回执；范围只是小型计算/collective，不是硬件压力测试。检查后八卡仍Available，卡6UE仍0，链路异常并未消除。

完整模型使用V2/eager、TP8、单序列、无prefix cache、无async scheduling，原量化及已有修复保持。八个worker均实际发现`language_model.model.layers.0.mlp.gate_up_proj`，为`MergedColumnParallelLinear`+`CompressedTensorsW8A8Int8`+`MctlassScaledMMLinearKernel`；权重[K,N]=[4096,3072]、stride=[1,4096]、INT8、无bias，scheme未被其他层共享。依赖实测为torch2.10.0+metax3.9.0.8、mcTriton3.6.0+metax3.9.0.8、mcoplib0.4.14+gf3794c4.maca3.9.0.31.torch2.10、vLLM0.32.0+empty、vLLM-MetaX0.32.0+g0962c8.d20261122.maca3.9.0.29.torch2.10.0。

## 模型对照协议

保持冻结GEMM原型、原激活量化、预登记≤1 BF16 ULP契约、固定HumanEval32输入token及greedy配置。在同一个TP8模型进程、相同备用通信条件下，依次执行原32题→仅第一层gate_up_proj候选32题→恢复原对象4题，沿用CPU隔离评分。

不能将旧驱动/旧通信路径的153/164直接作为本轮对照；本轮只做32题筛查及恢复验证，不代表完整164题、多独立进程、性能或长期可靠性验收。

## 对照结果

| 阶段 | 功能通过 | 与本轮原实现比较 |
|---|---|---|
| 原GEMM32题 | 30/32（93.75%） | 失败HumanEval/110、HumanEval/37 |
| 候选GEMM32题 | 31/32（96.875%） | 无通过题退化；HumanEval/37由失败变通过；HumanEval/110仍失败 |
| 恢复原GEMM4题 | 4/4 | 4题输出token均与原阶段完全一致，功能结果一致 |

三阶段无截断、无评分基础设施错误。每题仅一次生成，未按测试修改生成代码、补采样或重试挑选；评分使用原固定提取器和无网络CPU隔离容器。证据：`pilot/runs/*/{generation_manifest.json,generations.jsonl,correctness.jsonl,score_summary.json}`及`pilot/comparison_summary.json`。

候选与原实现24/32题token完全相同；另外8题为HumanEval/144、94、6、117、10、40、72、37。这是原/候选不同计算路径的观测，**不是历史同greedy配置9题分叉的原因闭环**。本轮31比30多一题也不证明候选普遍提高准确率；单轮、32题、不同通信/驱动环境不能替代全量独立进程验收。

八个rank均实际安装候选并恢复原对象。每rank候选调用1492次，共**11936次**；fallback=0。候选每次返回自身输出，并同时执行原GEMM做影子校验；全元素有限、相对原GEMM最大差异**1 BF16 ULP**、最大绝对误差**0.0009765625**，符合事前契约。该校验开销和完整INT32中间矩阵使本轮耗时不适合作性能比较。

实际覆盖29种[M,N,K]，N=3072/K=4096，M为1及28种prefill长度（96～356）。每rank保存首个prefill/decode共16份实际模型输入的选定行列，保留完整K：整数累加对CPU INT64精确，明确顺序FP32参考精确，FP64参考≤1 BF16 ULP。这次捕获来自完整模型，区别于前一轮“真实权重+合成激活”的独立层测试。完整统计和哈希见`pilot/evidence/replacement_stats.json`、`real_inputs/`。

## 最终设备状态与环境保持

运行结束后已停止本次容器；无GPU进程、驱动引用数0，八卡均Available。卡6/7的port4仍x4，卡6仍down、CE=2/UE=0，卡7仍up；计数与开跑前一致，所选内核MetaXLink/错误/状态事件没有新增。**备用传输让本轮推理可用，没有修复该链路。** 证据`evidence/final_health.json`、`final_kernel_events.json`。

对照本轮重启后的初始快照，原六个容器身份、镜像、挂载内容和运行状态不变。旧基线65文件、重复性135文件、GEMM原型69文件、前一次恢复33文件的哈希检查通过。原归档/源码/权重未改写，新结果单独保存。

## 继续工作的建议与入口

本轮已建立“自编GEMM→单层对象替换→局部数值检查→模型功能评分→恢复原对象”的可运行流程。维护源码仍在本次`pilot/harness/`和原`glmf/gemm_replace_20261123/harness/`，不是把补丁写入生产环境。继续扩大层/shape时，保持量化契约、按目标层显式允许列表接入、记录命中/fallback，并在新结果目录运行。

离线复核：`python -B glmf/reboot_recheck_20261123/verify_results.py`；只检查证据、原环境及历史哈希，不执行生成代码或GPU推理。`analyze_pilot.py`生成逐题对照。`launch_model.py`必须在通过本次通信检查的新目录/独立容器使用；现有结果拒绝覆盖，不能原地重跑。

后续默认P2P或性能基线仍需维护方恢复卡6—卡7互联路径；不要把备用路径作为默认链路已修复的依据。若要正式接纳候选，按`glmf/repeatability_20261123/REGRESSION_POLICY.md`继续完整164题、多独立进程和固定前缀数值验证；本轮不额外开展这些测试，也不宣称全模型或发布验收完成。
