# GLM 单层 INT8 GEMM 替换原型

观察日期：2026-11-23。**自编mcTriton INT8 GEMM、真实权重分片上的vLLM量化层替换和恢复均通过局部验证；完整八卡模型验证被GPU6设备错误阻断，尚未完成。** 本轮只验证可替换性与正确性，不测速度、不声明已优化性能或可正式发布。

历史greedy问题已登记为[待定位问题](../../../../../catalog/library/metax/hwdoc/practice/cases/2026-11-23-glm-greedy-repeatability/issues.md)。原 `../baseline_ops` 和 `../repeatability_20261123` 保持冻结；本次全部新文件在本目录，远程根目录为 `/home/metax/glm53-gemm-20261123`，实验容器为 `glm53-gemm-v1`。

## 可用基础软件栈

| 路线 | 用途与可控范围 | 本机盘点 | 本轮选择 |
|---|---|---|---|
| mcBLAS / mcBLASLt | 调用现成矩阵库；可通过C/C++扩展接入；不等于自行实现底层kernel | SDK已有共享库、静态库、设备二进制与mcBLAS头文件 | 后续可做库调用对照；本轮未编译这条路线 |
| mcTlass | 类似CUTLASS的C++模板路线，可组合GEMM组件 | SDK已有653个`.h/.hpp/.cuh`头文件；公开仓库提供模板代码 | 后续C++优化候选；公开分支不证明与本机二进制一一对应 |
| mctlassEx | 已有GEMM/GroupedGEMM等接口及优化实现 | Python包装、扩展`.so`、`libmctlassEx.so`及`.mcfb`；SDK该目录仅1个上述扩展名头文件 | 当前选中dense linear的原实现；本次未找到它的完整实现源码，开源覆盖范围仍须单独核对 |
| mcTriton | Python编写GPU kernel，JIT生成MACA代码 | 已装`3.6.0+metax3.9.0.8`，配torch`2.10.0+metax3.9.0.8` | **首个原型**；无需改变镜像/依赖或重建vLLM |
| MXMACA C++ + mxcc + runtime | 直接编写、编译和加载GPU核函数；控制布局、同步、指令等 | 已有`/opt/maca/mxgpu_llvm/bin/mxcc`，查询版本成功；SDK头文件/运行库存在 | 接入层建立后可另做C++实现，不在本轮同时维护第二套GEMM |

以上“本机盘点”见 `evidence/stack_inventory.json`、`installed_mctlassEx.json`，文件存在不等于所有API已经运行验证。

厂商资料核对：

- 《沐曦通用GPU_mcBLAS API参考》V05，物理PDF第8页“1简介/1.2安装mcBLAS”、第9页“1.3 Hello mcBLAS”：BLAS、SDK分发及C接口/链接入口；[原PDF](../../../../../catalog/library/metax/hwdoc/沐曦通用GPU_mcBLAS%20API参考_CN_V05.pdf#page=8)。
- 《沐曦通用GPU_mcTriton用户指南》V08，物理PDF第5页“1概述/1.1适用产品”、第6页“2快速安装”：MACA后端、C500和Triton3.6/torch2.10配套说明；[原PDF](../../../../../catalog/library/metax/hwdoc/沐曦通用GPU_mcTriton用户指南_CN_V08.pdf#page=5)。文档大版本配套不是任意wheel补丁版本兼容保证。
- 《沐曦通用GPU_mxcc编译器用户指南》V06，物理PDF第6页“1概述/1.1适用产品”；《沐曦通用GPU_MXMACA C++编程指南》V06，物理PDF第9～10页“1.1适用产品/2.1函数执行空间标识符”；[mxcc原PDF](../../../../../catalog/library/metax/hwdoc/沐曦通用GPU_mxcc编译器用户指南_CN_V06.pdf#page=6)、[C++原PDF](../../../../../catalog/library/metax/hwdoc/沐曦通用GPU_MXMACA%20C++编程指南_CN_V06.pdf#page=10)。本轮只用于路线判断，未执行文档示例。
- 公开[mcTlass仓库](https://github.com/MetaX-MACA/mcTlass)及[README_MX](https://github.com/MetaX-MACA/mcTlass/blob/2.20.2/README_MX.md)，观察日2026-11-23、分支`2.20.2`，README第4～22行描述C++模板GEMM与header-only结构；README自身标题为2.10，不能混同分支名、SDK版本或mctlassEx版本。本次未固定该仓库commit，不使用移动分支作为永久复现依据。
- [mcoplib](https://github.com/MetaX-MACA/mcoplib)、[mcTriton](https://github.com/MetaX-MACA/mcTriton)、[maca-samples](https://github.com/MetaX-MACA/maca-samples)有公开仓库。此前本地快照见 `hwdoc/repositories/2026-11-21/coverage.json`，仅覆盖公开资料且不构成服务器验证；本轮网页重新核查用于确认公开入口，不替换已冻结的软件版本。

## 当前dense linear的实际调用边界

本次固定镜像为 `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`；只读挂载原基线源码与权重，使用独立缓存和结果目录。vLLM上游commit为`5df63a7203cdb9328d824a27b682e77c7b9928be`，MetaX为`0962c8735ffe4795800030680311410848512b82`加已有冻结修复。

```text
CompressedTensorsW8A8Int8.apply_weights
  → MctlassScaledMMLinearKernel.apply_weights             [Python源码]
    → scaled_int8_quant                                 [保留原量化]
    → _python_api_ops.cutlass_scaled_mm                  [Python源码]
      → torch.ops.vllm.mctlassEx_w8a8_scaled_mm_azp       [注册的扩展入口]
        → mctlass_scaled_gemm / mctlassEx                [Python包装 + .so]
          → libmctlassEx.so / mctlassEx_xcore1000.mcfb    [当前加载的二进制]
```

原环境并非“全部源码”或“全部闭源动态库”的单一路线：vLLM/MetaX接入代码可读，mcoplib同时包含Triton Python源码和编译扩展，选中GEMM最终调用mctlassEx二进制。不能因文件名含`cutlass`就认定它调用NVIDIA原版CUTLASS；也不能从`.so`存在推断该实现一定不开源。完整开源覆盖需要逐组件、逐commit核对。

精确安装文件、注册schema、实际加载的库、源码路径与哈希见 `stack_inventory.json`、`gemm_callchain.json` 和 `installed_mctlassEx.json`。

## 替换设计和正确性契约

完整模型接入脚本只选 `language_model.model.layers.0.mlp.gate_up_proj`。设计是在八个worker中检查它的实际scheme/kernel和权重dtype，确认scheme没有被其他层共享，然后仅将该层的`scheme.kernel`换成实验包装器。不改源码文件、全局注册表、量化规则、其他层、MoE或TP通信。撤销时恢复原对象。这段完整模型路径尚未到达；已实际执行的是下述独立量化层中的同一包装器。

GEMM计算为 `C_int32 = A_int8 @ B_int8`，随后按 `((C_int32.float() * scale_a) * scale_b).to(bfloat16)`反量化。保留原`scaled_int8_quant`。范围是对称INT8、二维正stride、scalar/per-row A scale、scalar/per-column B scale、无bias，K不超过131071以避免最坏情况下INT32累加溢出；其他契约回退原实现并计数。首轮模型试验要求实际目标层fallback=0。

阈值在运行前固定于 `configs/contract-v1.json`：整数累加对CPU INT64参考精确；浮点epilogue对明确顺序的FP32参考精确；对FP64参考及原GEMM最多1个BF16 ULP（按较大绝对值定义、含subnormal下限），有限且shape/dtype一致。此为该原型的预登记边界，不能复制成所有算子的通用容差。

包装器在每次候选调用中同时计算原GEMM用于比较，**返回给调用者的是候选结果**。独立量化层已验证这一调用路径；完整模型尚未执行。保留INT32中间矩阵和同步检查是为了验证；它们会增加耗时、显存及原算子调用，不能据此评判速度，也不证明可以卸载原mctlassEx库。

## 验证顺序与文件

1. `test_device.py`：8卡×7组，共56组；含非整tile、正非连续stride、极值、零输入、prefill/decode M、scalar/per-channel scales；CPU INT64/FP32/FP64参考及可适用形状的原GEMM对照。初版忘记显式指定`tl.dot(out_dtype=tl.int32)`导致编译拒绝，失败记录和v1源码保留，修正后全部通过。
2. `isolated_layer_probe.py`：读取冻结checkpoint第一层gate/up的真实INT8权重与scale，将8份TP8分片依次放在GPU0。每份调用实际安装的`CompressedTensorsW8A8Int8`和原`MctlassScaledMMLinearKernel`，保持原量化，执行原实现→候选→恢复。激活为合成BF16输入；不是完整模型中采集的激活。
3. `run_model.py`与`evaluate_humaneval.py`已实现原32题→候选32题→恢复4题及隔离评分，但本次只到TP8通信初始化。**上述生成和评分均未执行，没有本轮HumanEval分数。** 测试/canonical材料仅在主机评分目录，不挂载给模型容器。
4. 已停止本次容器。对照本轮开始快照，旧4个容器身份、镜像、运行状态与挂载内容一致（Docker返回的Mounts顺序不同，比较前按Destination排序）。原基线65文件、重复性实验135文件哈希校验均通过。

## 实测结果与边界

| 检查 | 结果 | 验证范围 |
|---|---|---|
| 独立GEMM | 56/56通过，8卡各7组 | 发生卡故障之前的测试；不代表当前8卡健康 |
| 实际权重量化层 | 24/24通过，8份分片×M=1/17/173 | 全部在GPU0依次执行；每份处理后权重[K,N]=[4096,3072]，stride=[1,4096]；M=17激活非连续 |
| 与原GEMM比较 | 17/24组逐元素相同，全部≤1 BF16 ULP，最大绝对误差0.0078125 | 已登记容差内，不是bitwise等价；不保证完整模型greedy token相同 |
| 整数和epilogue参考 | 16份选定行列捕获，INT32对CPU INT64精确；FP32顺序参考精确；FP64≤1 ULP | 完整K，最多4行×8列；权重真实、激活合成，文件见`evidence/real_inputs/` |
| 命中和恢复 | 24次候选命中，0次fallback；24组恢复原实现后完全相同 | 验证对象级替换/恢复；未覆盖所有不支持分支的自动fallback |
| 完整TP8模型 | 未验证 | 初始化通信阻塞，尚未注入候选，不归因为候选GEMM错误 |

详情见`evidence/device_tests.json`、`isolated_layer_result.json`与`verification_summary.json`。独立层成功运行的源码是`evidence/isolated_layer_probe.v3.py`，哈希见`isolated_inputs_v3.json`。维护入口仅另将FileStore路径改为唯一名字（v4）；该次重跑触发现有捕获文件保护而中止，没有覆盖成功结果。v1缺少TP元数据组，v2缺少当前VllmConfig；补齐后v3通过。曾在结果采集前将v3误判为初始化卡住，完整日志和24组结果已推翻该假设，见`isolated_attempts.json`。保留尝试日志，不将初步诊断当作事实。

## 八卡验证的设备阻断

本轮实测宿主驱动为3.10.14，先前冻结基线为3.8.30；进入本轮前宿主已重启/版本发生变化，本任务未升级驱动或重启。不能直接将新环境结果视为原驱动上的回归，也不能据此证明驱动变化导致故障。

GPU6（0000:5b:00.0）先出现MetaXLink宽度变化，随后报告EID 0x2119不可纠正错误/AER Unsupported Request，状态变为Not Available。完整模型在MCCL初始化处停住，停止实验容器后状态仍未恢复。限定时长的诊断进程临时设置`MCCL_P2P_DISABLE=1`，rank6仍在创建队列时失败并SIGSEGV，未完成all-reduce。关闭P2P并未绕过此设备错误。

该变量的文档依据是《沐曦通用GPU_MCCL编程指南》V08，物理PDF第32页§4.2.2.21：[原PDF](../../../../../catalog/library/metax/hwdoc/沐曦通用GPU_MCCL编程指南_CN_V08.pdf#page=32)。仅在诊断exec设置，未写全局配置。ACS参数只读记录为N，未改PCIe/驱动参数。内核原日志留远程，入库仅选取必要事件并记录SHA256，见`hardware_issue_summary.json`。

继续条件：先由维护方恢复GPU6并确认8卡Available，再做最小通信检查；通过后在新的结果目录、记录当时驱动与软件指纹，执行同环境原32→候选32→恢复4。不能把历史153/164直接当作新驱动对照，也不能用局部≤1 ULP代替模型正确性。不得盲目重试或自动重置设备。

此处是单层接入可行性实验，**不是全模型算子替换验收**；未做多独立进程完整164题、CUDA graph/compile、并发、任意量化格式或性能对照。正式验收仍按[已冻结回归规则](../../../../../catalog/library/metax/methods/regression-policy.md)。

本地证据回归：`python -B glmf/gemm_replace_20261123/harness/verify_experiment.py`。它检查数值摘要、输入哈希、捕获存在性、原环境保持及历史归档；不重新执行GPU或模型，不能取代运行验证。GPU测试入口为`test_device.py`、`isolated_layer_probe.py`；远程执行须使用新结果目录并持有现有GPU资源锁，避免覆盖或同时占用。

`harness/`为维护源码，`configs/`为事前协议，`runs/`为生成/评分，`evidence/`为实际环境、分层结果和原始资产哈希。新实验不要覆盖已有结果目录；推广时沿用同样契约与入口，逐个增加layer allowlist与shape覆盖。
