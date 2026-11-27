# 003 优化 EP 准备操作与 collective 关键路径

状态：proposed，待确认。优先级：P1。类型：因果归因后局部实现。前置：001，高并发依赖002。

## 证据与假设

你的TP8五组profile配对中，collective解释累计kernel净增的57.93%–71.15%。指定AllReduce调用数相同，但加权duration增加45.59%–72.03%；EP还增加copy/index/fill。新TP2/DP4/EP8图模式则明显是AG/RS，4K/32步/DP0TP0 collective约197.060ms，占kernel sum23.11%。[复算记录](evidence-audit.json)

假设分成两类：准备链能减少不必要的中间读写；通信duration中可能有前序计算/专家不均衡导致的等待。只有实际传输字节、组和rank到达时间一致时，才判断通信算法本身效率。

## 可改的源码位置

- `fused_moe.py::_prepare_expert_assignment`：默认不在align时过滤无效专家。
- `vllm/.../moe_align_block_size.py:164–165`：`expert_map[expert_ids]`额外映射。
- `TritonExperts.apply:638–639`：EP/SPLIT_K条件下清零中间结果；SPLIT_K1和2的要求分别检查。
- `AllGatherReduceScatterManager.dispatch/combine` 与 `pynccl`：变长size、通信组、量化激活及scale/路由元数据。

文件链接和实际分支见[源码分析第4、7节](source-review.md)。当前mcoplib alignment只支持旧ABI，不支持scatter_idx输出。

## 最小实验与改动顺序

- [ ] 用TP8 EP关/开、TP2/DP4/EP8两个独立基线，记录每层每步logical/physical rank、tensor shape/dtype/bytes、有效token、padding、expert_map范围、每专家token数。
- [ ] 对齐各rank时钟与事件，拆出前序计算、collective到达、传输和完成；不可把最早进入而等最久的rank判成慢卡。
- [ ] 验证index/cast是否来自EP映射；优先评估在align输出时直接生成本地expert IDs、静态expert_map类型一次转换、复用不变工作区。每步token→expert路由仍会改变，不能缓存动态映射结果。
- [ ] 对清零做读写覆盖证明：非本地专家、空专家、SPLIT_K累加、padding、连续两次不同路由均覆盖。只有计算/归并能保证无效项为零时，才将clear融合进写入或reduce。
- [ ] 补采native memset来源：4K每卡32步2688次×512KiB、95.502ms，不能将它们自动归为上面的BF16 fill。若来自mctlass workspace，转交007做实际原生入口优化。
- [ ] 原语对照采用实际小消息、相同通信组和拓扑，并测试多个TP组同时工作；已有大消息峰值只作背景，不作为收益预测。

## 验收与收益边界

局部必须看到目标链的调用/临时字节/时长下降，专家路由和数值契约不变；关闭profiler后按[共同流程](workflow.md)验证TPOT与吞吐。通信kernel duration下降但前序计算增加，或总TPOT不变，不算完成。

不直接删零、不将AllReduce替换成非等价A2A、不靠启用EPLB猜测解决。若主要是迟到rank的计算，任务结论应指向006/007的负载和shape优化；若是原语延迟，再试拓扑/后端，并记录无法优化的部分。
