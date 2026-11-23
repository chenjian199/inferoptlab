# 来源与事实边界

核对日期：2026-11-20。所有架构、模块、接口、状态、示例参数和实施顺序均为 InferOptLab 的建议设计；以下来源只支持相应外部项目事实。正式实施时应固定实际选定版本，不能以滚动文档代替版本确认。

| 编号 | 官方来源 | 本方案使用的事实 |
|---|---|---|
| S1 | [NVlabs/kda](https://github.com/NVlabs/kda) | KDA 是由 coding agent 执行内核研究/实现/验证/迭代的早期工作流；公开最小流程和工作区约定，Wishlist 当前列 B200/B300 |
| S1a | [KDA agent flow](https://github.com/NVlabs/kda/blob/main/docs/agent-flow.md) | 任务契约、验证、评估和候选记录的流程 |
| S1b | [KDA 基础提示](https://github.com/NVlabs/kda/blob/main/prompts/basic-flow.md) | 按任务补充输入、约束和验证入口 |
| S1c | [KDA 官方实战文章](https://nvlabs.github.io/kda/blog/2026-09-27-kda-for-kda/) | Agent 过拟合测试的实际案例及真实输入、数值与边界验证经验 |
| S2 | [vLLM Benchmark CLI](https://docs.vllm.ai/en/latest/benchmarking/cli/) | 客户端指标、benchmark 入口、缓存与比较语义 |
| S2a | [vLLM bench serve](https://docs.vllm.ai/en/latest/cli/bench/serve/) | 详细结果、分位数、goodput 选项等正式接口说明 |
| S3 | [SGLang Benchmark and Profiling](https://docs.sglang.io/docs/developer_guide/benchmark_and_profiling) | 在线、单批服务、离线、ModelRunner 的边界与 profiling |
| S3a | [SGLang Bench Serving](https://docs.sglang.io/docs/developer_guide/bench_serving) | 在线服务输入、端点、延迟/吞吐和输出 |
| S4 | [AIConfigurator](https://github.com/ai-dynamo/aiconfigurator) | 当前维护迁移状态，以及离线配置预测/搜索定位 |
| S5 | [AISim](https://github.com/ai-dynamo/aisim) | AISim 为继任项目，离线预测与候选搜索；文档/包名迁移及版本、数据身份要求 |

此前《跨模型跨 GPU 端到端优化自动分析实施方案 V2》提供本项目的业务目标与四阶段流程。本蓝图在它的基础上定义软件实现边界，没有重新验证原案例中的性能数字，也没有把不同文档中的数字合并为同一实验结果。

名称 InferOptLab 是本次建议的工程名。公开检索没有用于证明名称、商标、域名或包名的排他性；创建组织仓库时以实际可用性为准。
