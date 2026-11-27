# 001 建立同口径的部署与阶段基线

状态：proposed，待确认。优先级：P0。类型：实验基线。前置：无。

## 问题与已有证据

现有结果同时包含含Prefill的eager扫描、缓存Decode、20/50/200输出，以及不同机器上的图模式。它们可以定位线索，不能直接证明某一部署或开关带来几倍加速。[部署盘点](deployment-review.md)中D/E新增结果还缺对应的冻结运行配置。

此外，EP关闭且DP>1时插件仍可能走AG/RS，不能用“EP1”文件名替代运行时专家分片、通信组证明。源码落点为 `vllm_metax/model_executor/layers/fused_moe/all2all_utils.py::maybe_make_prepare_finalize` 和 `AllGatherReduceScatterManager._get_comm_group`，见[源码分析](source-review.md)。

## 最小计划

- [ ] 为每次运行固定image digest、vLLM/MetaX安装源码hash、原生库hash、模型/tokenizer指纹、实际server-info、launch/env白名单、物理卡与rank映射。
- [ ] 补齐D/E对应的原始profile、缓存proof和运行快照；不能补齐的保留为参考，不进入受控A/B。
- [ ] 复用现有workload与plan，选4K/20/C1、4K/20/C4作为跨历史数据锚点；4K/200/C4、64K/200/C4作为本轮优化锚点。所有请求N=4C、每槽独立上下文。
- [ ] 在同一机器同一环境下，以TP8 EP关/开、TP4/DP2 EP关/EP8、TP2/DP4/EP8 graph为候选；TP1/DP8/EP8 graph先做启动及容量验证，通过再纳入。不得承诺全部形态已可测。
- [ ] 固定graph后比较部署；需要解释历史eager差异时，另建单因素eager/graph配对。不要同时切换attention、compile、max_num_seqs。
- [ ] 逐rank记录实际专家权重shape、TP/DP/EP组和token数。DP固定路由的C4负载不保证每种形态每rank相同batch，需同时报告全局与局部工作量。
- [ ] 输出语义保持不变：全命中的是原始L，线上L+1；记录seed、query=1、抢占、是否提前EOS。另设cold Prefill诊断，不将其混入Decode样本。

## 完成标准

同协议的对照能从run ID追溯到配置、原始请求与缓存证据；能够回答EP关闭是否改变分片和通信组、graph是否真实重放、各DP实际running多少。产出候选部署在指定锚点的延迟/吞吐表及不可测原因，后续任务引用这些基线。

这项任务本身不承诺性能提升。若某部署尚未稳定，先完成其已通过锚点，并将失败交给[002](002-cache-and-runtime-failures.md)，不把前置任务扩成无边界的大矩阵。
