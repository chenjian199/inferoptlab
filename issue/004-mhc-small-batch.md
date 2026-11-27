# 004 为 C500 的真实小 batch 调优 mHC

状态：proposed，待确认。优先级：P1。类型：kernel调优。前置：001。

## 为什么值得做

TP8/EP关4K/C1中两个mHC主核占累计kernel时间约15.43%；新TP2/DP4/EP8中mHC约85.266ms/32步、占10.00%。两种形态都有稳定热点。

但模型已经使用融合post/pre/norm，[当前TileLang源码](../outputs/optimization-review-20261126/source/vllm_metax/model_executor/kernels/mhc/tilelang_kernels.py)64行附近仍以GB300、hidden5120/7168为调参背景；本轮是C500/4096。应验证小M线程/切分选择，不重复“开启融合”。

## 实现范围

入口 `mhc_fused_post_pre_split_config`、`compute_mhc_pre_num_splits`、`mhc_pre_big_fuse_with_norm_tilelang`、`mhc_fused_tilelang`；配套warmup/capture从同一dispatch规则取值。`tilelang.py`的调用、fake/meta路径与输出缓冲区契约同时维护。

- [ ] 从实际worker采集hidden4096、hc_mult、M、stride、dtype、sinkhorn参数；M使用每rank的实际token数，不用全局C直接代替。
- [ ] 对M=1/2/4/8/16/32及实际graph padding形状建立replay，比较threads、tile_n、n_splits和单/多block策略；根据整除与资源约束筛选，非法组合不编译。
- [ ] 保持Sinkhorn迭代数、eps、FP32累加与BF16回写；不通过减少迭代或改变算法质量拿速度。
- [ ] 对比当前融合路径与有依据的候选；验证启动预编译覆盖、graph capture/replay无新增分配、后续恢复原配方。
- [ ] 对每个候选分别测局部设备时间和关闭profiler后的TPOT，避免为了减少一次launch而增加寄存器/同步成本。

## 验收与否决

目标shape数值符合事先登记的误差契约，长生成状态不漂移；实际trace命中候选；至少目标小M簇有可复现局部优势，端到端收益满足共同流程。其它M若退化，收窄dispatch覆盖范围。

时间预算：当前F中该类别若减少20%，对应kernel累计预算减少约2%；这不是TPOT收益预测。若C500现配置已经接近候选最优，保留调优结果并关闭任务，不为配置表存在而强行修改。
