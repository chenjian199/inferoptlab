# 009 优化长上下文 indexer 与 top-k 的实际工作量

状态：proposed，待确认。优先级：P3。类型：长上下文算子。前置：001。

## 证据与预算

旧TP8 c1的 `topk_2pass_row_kernel` 加权均值随4K/16K/64K约17.414/24.491/38.457μs增长。新TP2/DP4/EP8的indexer_or_topk类为24.190/27.008/31.805ms每32步单卡，4K→64K只增加约7.615ms累计kernel时间，优先级低于当前通信、GEMV、mHC。

现有family只是名称分类；top-k可能属于attention或MoE，先确定模块，不按名称统一归为路由。完整attention还包含投影、缓存与metadata，不能用attention类占比很低就忽略整个模块。

## 代码与最小计划

落点：[MetaX sparse_indexer](../outputs/collectives-20261126/source/vllm-metax/vllm_metax/models/glm5next/metax/sparse_indexer.py)、`get_indexer_topk`与 `sparse_mla_index_remap` 调用链。当前存在buffer初始化、按真实seq_lens选择、pool索引与remap多个分支。

- [ ] 记录真实context_lens、max_model_len、topk_tokens、pool设置、row count、stride与padding。区别实际64K扫描和按max_model_len无效扫描。
- [ ] 将top-k实例映射到模块；分别计MQA logits、选择、remap、cache写入和metadata。优先检查不必要的重复metadata重建与已知等价的remap。
- [ ] 只有consumer不会读未初始化部分时才缩小fill范围；page table、序列长度、缓存block会变，不能跨请求盲目复用metadata。
- [ ] 不减小top-k、不缩短可见上下文，不打开改变attention语义的近似策略；先试同精度/同索引结果的shape专门化。

## 验收与否决

索引集合、顺序/tie处理、边界mask与原实现一致；64K局部耗时下降且端到端可重复改善。若总改善低于基线波动，保留局部结果，优先资源投入005/003/004。

[AMD GLM优化跟踪](https://github.com/vllm-project/vllm/issues/57230)包含remap与indexer方向，可借鉴“明确冗余后再删除”的方法；其prefill清理优化不能直接宣称会改善本次纯Decode。
