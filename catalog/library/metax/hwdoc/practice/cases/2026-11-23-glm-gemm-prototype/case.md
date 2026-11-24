# C500 GLM INT8 GEMM替换原型

观察日期：2026-11-23；适用镜像`9bbf20dbcaaf`，vLLM `5df63a72`、MetaX `0962c873`加既有冻结修复，MACA3.9.0.29、torch2.10.0+metax3.9.0.8、mcTriton3.6.0+metax3.9.0.8。本轮宿主驱动3.10.14，与历史基线3.8.30不同。详细源码路径、hash、命令、PDF原文页码见[实验报告](../../../../../../../experiments/evidence/metax/glm53/gemm_replace_20261123/README.md)与其`evidence/`。

## 可替换边界与路线

本机SDK含mcBLAS/mcBLASLt库、mcTlass模板头文件、MACA C++/mxcc；Python环境含mcTriton。首轮选mcTriton实现INT8×INT8→INT32累加→FP32尺度计算→BF16输出，不重建vLLM。其他路线仅盘点，未编译验证。资料依据、厂商PDF修订号和物理页见实验报告“可用基础软件栈”，不可把头文件存在当成API验证。

实际安装调用链：`CompressedTensorsW8A8Int8`→`MctlassScaledMMLinearKernel`→原`scaled_int8_quant`→`cutlass_scaled_mm`→`mctlassEx_w8a8_scaled_mm_azp`→mctlassEx Python包装/动态库。上层可读源码、部分mcoplib为Triton源码，选中GEMM最终加载`.so/.mcfb`。本轮未找到mctlassEx完整底层实现源码；这不等于证明该组件全部闭源，也不能将mcTlass公开模板直接视为该二进制的同版本源码。

替换位置是单个量化层的`scheme.kernel`对象。保留原量化；候选输出返回调用者，同时执行原GEMM作影子校验；退出时恢复原kernel对象。完整模型目标仅第一层`gate_up_proj`，完整模型路径另有scheme共享检查，但未执行到此处。该原型仍依赖原库作量化/校验/其他层，不是移除厂商库的方案。

## 实测通过范围

- 独立GEMM：故障前8卡各7组，56/56通过，涵盖尾块、stride、极值、scalar/channel尺度；整数对CPU INT64精确，明确FP32运算顺序精确，FP64/原GEMM按事前契约≤1 BF16 ULP。
- 实际GLM checkpoint第一层gate/up权重和scale按TP8切8份，**在GPU0顺序执行，激活合成**。通过真实安装的vLLM量化scheme执行原实现→候选→恢复，M=1/17/173、N=3072、K=4096，共24/24通过。
- 17/24组与原GEMM逐元素相同，全部≤1 BF16 ULP，最大绝对误差0.0078125；24次候选命中、0 fallback；24组恢复结果完全相同。16份选定行列捕获又核对CPU整数和浮点参考。
- 原基线65文件、重复性实验135文件、原4个容器身份/状态/挂载内容保持；本次实验容器已停止。新归档69文件，本地/远程包SHA256一致。

证据为本目录`evidence/verification_summary.json`、`isolated_layer_result.json`及`artifacts.json`所列原件。原始设备测试、代码和量化层捕获只在实验维护目录保存，不复制为第二套知识库脚本。

## 未验证与失败尝试

完整TP8在MCCL初始化处阻塞，**尚未注入候选**；无本轮模型生成或HumanEval评分。原因边界见[设备问题](issues.md)。局部ULP合格不能代替端到端正确性，尤其不能保证greedy逐token一致；不宣称性能提升、全模型替换通过或可发布。

初版Triton遗漏`tl.dot(out_dtype=tl.int32)`而被编译拒绝；修正后56组通过。独立层v1缺少TP元数据组、v2缺少VllmConfig，v3补齐后24组通过。曾在日志未采全时初步误判v3停在初始化，成功日志/结果已推翻；维护入口v4只改FileStore唯一命名，重跑被旧捕获文件保护中止，没有覆盖成功结果。具体版本和修正见实验目录`isolated_attempts.json`，成功源码固定为`isolated_layer_probe.v3.py`。

## 继续方法

先恢复GPU6并验证8卡通信；之后在新结果目录记录当时驱动和软件指纹，在同环境运行原32→候选32→恢复4。确认8卡目标层均实际命中、无意外fallback，再按冻结回归规则扩展164题和独立进程复核。勿把旧驱动153/164直接作为新驱动对照。首次流程建立后，再依次增加层/shape，或将候选实现换成mcTlass/C++，沿用量化契约与可恢复入口。

本地只读回归入口：`python -B glmf/gemm_replace_20261123/harness/verify_experiment.py`，只验证证据完整性，不运行GPU、不证明新的执行成功。
