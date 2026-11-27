# 002 区分缓存容量与高并发非法访存并恢复可测边界

状态：proposed，待确认。优先级：P0。类型：稳定性与吞吐边界。前置：001环境冻结。

## 问题与已有证据

61的TP8在4K/C16、16K/C8、64K/C4出现服务端失败，后续点被跳过。[环境核对](../outputs/environment-alignment-20261126/README.md)已有illegal memory access、KDA scatter_states栈及后续MCCL异常。新的TP4/DP2 CSV虽然写 `cache_residency_failed`，note明确描述pynccl all_gatherv非法访存。**异常标签不能当成KV物理容量测量。**

源码检查：[scatter_states.py](../outputs/optimization-review-20261126/source/vllm/model_executor/layers/mamba/ops/scatter_states.py)24–40行按state_idx写入，mask限制行内offset，没有kernel内的state_idx范围保护；这只是必须核验输入索引有效性的地方，不证明它就是根因。GPU异步报错可能出现在后续通信调用。

## 最小计划

2026-11-27后续更新：本轮Sparse Prefill非法访存已定位到32位索引乘行跨度的溢出，并以64位乘法修复。C500 BF16 512/512内核数值、地址边界和图模式4K/C32的128/512输出回归通过，正式矩阵恢复为r2。见[修复与验收](../outputs/sparse-prefill-fix-20261127/README.md)。其他历史KDA/通信异常仍需分别核实。

2026-11-27补充：已修复矩阵资格请求ID碰撞及输出间缓存隔离，31项流程测试通过。同步真机诊断在TP8/EP关闭、4K/C32的第30条逐槽预热仍复现非法访存，驱动指向`sparse_attn_global_fwd_kernel`，不是已确认的KDA根因。见[诊断记录](../outputs/matrix-repair-20261127/README.md)及其原始日志。当前停止正式扫描，内核修复和原失败场景回归尚未完成。

- [ ] 先选同一形态的相邻通过/失败点：TP8 64K/C2与C4，或TP4/DP2 4K/C32与C64。逐请求保存预热→驻留→正式请求的时间线。
- [ ] 同步记录KV blocks、KDA state slots、每DP实际batch、graph捕获尺寸与实际尺寸、首个错误及worker退出；将容量不足、索引/内存异常、路由/取证失败分别编码。
- [ ] 仅在短诊断重放中启用同步定位/索引断言；核对cache slot生命周期、copy-on-write、state_idx范围、重复索引、spec/padding条目与graph复用。诊断开销不进入性能结果。
- [ ] 比较eager与graph复现情况，检查pynccl all_gatherv输入sizes、缓冲区容量、地址生命周期和各rank调用顺序。错误暴露于通信不等于通信库本身错误。
- [ ] 确认根因后制作最小修复和边界回归，再恢复失败点；容量确实不足则保留明确的不可测原因，不修改独立上下文协议来凑通过。

## 验收与停止条件

原失败点在相同协议下多轮无非法访存；输出/状态与原实现的有效点一致；graph与非graph的索引契约均正确。边界点高并发缓存100%驻留才能计为纯Decode有效性能，否则只计运行成功不计该协议分数。

不能通过仅捕获异常继续、把失败改成跳过、禁用正确性检查或增加memory utilization来声称修复。若容量不足被证实，交付容量模型与准入规则也可关闭该诊断任务，但不写“性能提升”。

恢复高并发可能比优化小算子更影响可用吞吐；当前不能预测提升倍数。[原TP8分析](../outputs/TP8_耗时占比与优化方向分析.md)中吞吐随并发仍增长，也未证明已经饱和。
