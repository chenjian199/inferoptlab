# 007 验证 MoE 配置生效路径并调优实际内核

状态：proposed，待确认。优先级：P2。类型：后端调优。前置：001、003的shape取证。

## 证据与关键限制

新日志缺少 `H=4096,E=36,N=2048,device_name=MXC500,dtype=int8_w8a8.json`；MoE GEMM在4K/32步单卡约98.112ms。E=36来自当前EP8分片，不是其它部署的通用E。

源码 `maybe_override_stage_block_size_m` 通过mctlass选择器覆盖BLOCK_SIZE_M，`invoke_fused_moe_triton_kernel`在当前INT8/MCTLASS分支调用原生 `cutlass_moe_mm_w8a8`，并不把整份Triton调优配置传给该调用。**因此先证明可控参数，再调优，不能把补JSON等同于优化。**[代码与日志](source-review.md)

## 最小计划

- [ ] 记录两个stage实际M/N/K、每专家token直方图、top-k、local/global E、padding、配置lookup key、原生get_kernel_m结果与最终kernel标识。
- [ ] 分析4K/32步2688次×512KiB memset的原生调用相关性：是否为两个MoE GEMM的workspace初始化、是否全buffer清零、能否按有效范围初始化或与消费核融合。该猜测先用correlation/调用边界证实。
- [ ] 原生路线：只扫描实际提供的算法/布局/工作区接口；没有暴露的旋钮不写入无效JSON。向厂商反馈真实小M shape及空专家分布时，附最小replay。
- [ ] Triton路线：单独切换实际backend后，用真实路由分布扫描stage1/2参数；同时测prepare、activation/quant、combine，防止GEMM局部快但全MoE慢。
- [ ] 分别覆盖TP8 EP关、TP8 EP开与TP2/DP4/EP8；权重分片和专家数改变后重新验证查表与workspace，不重用不匹配配置。

## 验收与停止条件

首先证明“改动使实际kernel/参数改变”；其次数值、过滤非本地专家、SPLIT_K累加与top-k语义正确；最后端到端目标负载改善。若JSON只改变日志而未改变实际执行，立即停止该路线。

其它芯片的经验也支持这个顺序：[AITER GLM5.3报告](https://github.com/ROCm/aiter/issues/5156)中调优候选并未胜过已有ASM路径；[EP查表键报告](https://github.com/ROCm/aiter/issues/3999)提示应核验真实路由键。两者仅作方法参考，不认为MetaX存在同一缺陷。
