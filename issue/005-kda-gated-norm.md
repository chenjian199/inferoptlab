# 005 修正 KDA gated RMSNorm 的 OOT 回退并验证融合收益

状态：proposed，待确认。优先级：P1，建议首批实现候选。类型：局部后端适配。前置：001。

## 实际证据

当前MetaX为 `PlatformEnum.OOT`。`CustomOp.dispatch_forward`选择`forward_oot`，其默认调用`forward_native`；KDA所用`FusedRMSNormGated`提供`forward_cuda`却未覆盖`forward_oot`。模型 `self.o_norm(core_attn_out, g2)` 因而存在回退至cast/pow/mean/rsqrt/mul/sigmoid链的明确静态路径。[完整源码链及链接](source-review.md)

新4K trace中recurrent、mean、pow、rsqrt、sigmoid均1088次/32步，即34次/步。旧TP8分析里十个对应候选核占4K/C1约7.52%、C8约5.76%。这支持该路径是实际热点，但收益不能直接取整个other类别占比。

## 最小实现

- [ ] 在不计分的短诊断中记录类的实际module、`_forward_method`、是否有外部替换，确认运行分派与静态源码一致；采集真实x/g的3D shape和stride。
- [ ] 首选给该类增加MetaX专用OOT实现，复用并验证已存在的 `rms_norm_gated` Triton kernel。它对D≤512处理row-strided gate，必须保留H与g_stride_n；不能把gate盲目flatten后假设连续。
- [ ] 若既有Triton核在MACA不支持或更慢，再实现小范围mcTriton核；不先扩展到所有gated norm或所有OOT算子。
- [ ] 保持sigmoid而非SiLU、逐head归一化、权重广播、FP32统计、eps、BF16输出，核对x/g非连续、零/极值输入和可选residual/prenorm分支。未覆盖分支明确保留原实现。
- [ ] 在实际graph replay下确认碎片核被目标融合核取代，没有新增host同步、device-to-host或每步编译；不修改KDA recurrent状态更新语义。

## 验收与回退

局部：对真实输入/权重与FP32参考比较，登记容差，禁止NaN/Inf；输出shape/dtype/stride契约一致。模型：固定请求与seed做原→候选→恢复，覆盖4K/16K/64K和长生成；对非bitwise相同结果评估logits/token差异，不仅检查文本能生成。

性能：统计融合前后同一链的kernel总时间与调用数；最终以profiler关闭、相同图模式下TPOT/吞吐为准。该改动按模块开关回退，不全局替换 `CustomOp.forward_oot`。若实际绑定已绕过native或融合更慢，则撤回性能假设并保留调查结论。

[FlashInfer对应方法](https://docs.flashinfer.ai/generated/flashinfer.norm.rmsnorm_sigmoid_gate.html)说明门控归一化融合的工程路线；它的SM/head-dim限制不适用于直接在C500启用。本任务优先使用本机现有Triton源码，避免引入不相容的CUDA实现。
