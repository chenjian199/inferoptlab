# 010 定位图重放间隔与 DP 协调开销

状态：proposed，待确认。优先级：P2。类型：模型执行与调度。前置：001、003。

## 证据与问题

F已实际开启graph，每卡32次重放；配置max_num_seqs=16/DP，实际每DP running=1。4K单卡kernel union约851.14ms，而首末kernel跨度1238.87ms，但不能把差额直接判为CPU空闲。

本次补计GPU memcpy/memset后，4K记录到的设备活动union约985.592ms，首末活动跨度1239.081ms，未覆盖区间253.490ms；16K/64K未覆盖约273.610/268.045ms。它们也可能包含同步、graph边界、DP协调、采集器及未记录活动。[重新计算](source-review.md)

## 最小计划

- [ ] 在同一时间轴上关联CPU schedule、DP协调、H2D/D2H、graph launch、device events、流式发送；统一timestamp单位，跨rank比较前核对时钟偏移。
- [ ] 把已有profile与不启用profiler的短设备事件采样对照，判断采样器放大了哪些间隔；不得用profiled客户端延迟计算优化收益。
- [ ] 按实际每DP token数/图尺寸检查padding和dummy运行；全局C4时各DP1是受控负载，不为提高“利用率”改变负载定义。
- [ ] 若瓶颈确在主机/DP协调，才试窄范围减少重复metadata构造、缩短同步链或异步调度；异步候选先核对模型/后端/图模式兼容及缓存状态生命周期。
- [ ] max_num_seqs调整只用于验证调度/捕获尺寸影响，不把上限从16改为128就解释为running128。所有候选保存实际running和scheduled。

## 验收与停止条件

必须说明减少的具体等待链，并在profiler关闭后证明同一请求集延迟/吞吐改善。不能只凭graph跨度缩短或CPU占比下降报告性能提升。

若主要间隔来自内存操作或collective等待，交回003/007，不同时打开异步、DBO、不同batch预算等多个开关。若采样器造成大部分现象，完成诊断即可，不为减少测量开销修改线上调度。
