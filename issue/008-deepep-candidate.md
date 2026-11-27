# 008 对照验证 MetaX DeepEP 的 Decode 整体收益

状态：proposed，待确认。优先级：P2，有条件候选。类型：通信与MoE后端联动。前置：001、003、007。

## 已知支持与未知部分

插件有 `MacaDeepEPLLPrepareAndFinalize`，已装MetaX `deep_ep 1.0.0+metax3.9.0.11torch2.10`。INT8 oracle有batched选择，batched expert声明支持static-channel weight/dynamic-token activation。入口存在不等于GLM当前W8A8、shape、graph和cache组合已完整验证。

当前AG/RS已跑通。基础通信实测在EP8/8KiB处AG+RS比两次均匀A2A快，不能凭“MoE一般用All-to-All”就直接切换。真实dispatch有top-k去重、rank目标及padding，与该microbenchmark输入语义不同。[通信结果](../outputs/collectives-20261126/README.md)

## 最小计划

- [ ] 核对installed Buffer签名、包实际路径、hidden4096、专家数、top-k、dtype、scale布局、max_tokens_per_rank、graph捕获要求。
- [ ] 用真实路由样本独立验证dispatch→batched experts→combine，对比AG/RS数值与专家权重应用次数；专门测试空rank、全本地/跨组路由和不均衡分布。
- [ ] W8A8当前未必使用低精度dispatch：源码use_fp8_dispatch取决于quant_dtype及block_shape。保存真实wire tensor dtype，不将W8A8模型自动等同于INT8通信。
- [ ] 分别测prepare/compute/combine和合计设备关键路径；记录额外工作区是否挤占KV，不能降低缓存命中或通过减少独立上下文换速度。
- [ ] 从TP2/DP4/EP8 C4的稳定锚点开始，验证graph，再扩展C8/16；对TP1/DP8另测，不能共用收益结论。

## 验收与否决

同输入、图模式和缓存证明下端到端改善，且内存容量、尾延迟、输出与回退通过共同流程。后端/量化/捕获不支持则标记unsupported并保留清晰原因，不为消除报错改模型精度或路由语义。

[当前NVIDIA DeepEP上游](https://github.com/deepseek-ai/DeepEP)的硬件和API已经不同于本机MetaX包，不能直接升级替换。借鉴的是布局和通信协同方法；当前本机究竟快多少，必须由上述A/B得出。
