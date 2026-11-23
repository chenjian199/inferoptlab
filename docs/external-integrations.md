# 外部组件与适配边界

查证日期：2026-11-20。以下外部状态来自当日官方公开资料；InferOptLab 尚未实现或实测这些适配器。运行时应锁定具体版本，不能将 `main` 文档当成任意已发布版本的保证。

## 1. 核心原则

外部组件提供工具和候选依据，InferOptLab 保留实验身份、测量口径、状态机及验收规则。核心只接收自己的版本化对象，外部命令、字段、路径和兼容判断放入适配器。

| 组件 | 适合复用 | InferOptLab 仍需负责 |
| --- | --- | --- |
| KDA | 编程 Agent 的研究、实现和迭代工作流 | 任务契约、资源预算、候选包、独立验收 |
| AISim | 性能预测、部署候选搜索、离线分析 | 适用性判断、误差校准、实测确认 |
| vLLM benchmark | 在线与离线测量、参数扫描、详细结果 | 固定测量语义、负载及缓存状态 |
| SGLang benchmark/profiling | 不同层级的性能测量和 trace | 区分测量边界、版本映射、证据关联 |
| 推理框架及厂商运行时 | 模型执行、并行和内存等具体实现 | 能力探测、构建身份、生命周期管理 |

KDA 的接入契约见 [kda-integration.md](kda-integration.md)。此处的适配器名称均为本项目设计，不是第三方提供的统一接口。

## 2. AISim 与 AIConfigurator

查证时，AIConfigurator README 已说明进入向 AISimulate 迁移的维护阶段，新功能和模型覆盖移向继任项目。[1] 该继任链接目前重定向至 `ai-dynamo/aisim`，README 名称为 AISim，并介绍独立于 Dynamo 的预测及搜索能力。[2]

因此，新设计采用可选 `PerformanceModel` 插件：优先评估 AISim，旧 AIConfigurator 仅作为需要时的兼容适配。不要把任一项目设成核心启动的必要依赖，也不要把项目名称里的 disaggregation 理解成只允许 P/D 分离。

AISim 当前 README 同时提醒包名迁移及发布差异：`main` 的说明可能先于可安装 wheel。实施时应核验实际包、CLI、导入名和依赖组合，不能直接假设最新文档示例在现有环境可运行。[2]

### 预测结果必须独立存储

每份预测应关联模型及权重身份、GPU/互联、框架版本、并行配置、负载、预测器版本和性能数据集版本。数据集固定完整 commit SHA，并保留文件 hash；实际能力以选定版本和支持矩阵为准。

记录至少区分 `predicted` 与 `measured`。预测用于裁剪和排序候选，不能填入实测吞吐或宣称目标已达成。超出数据覆盖范围时保存外推标记和不确定性；缺少目标国产 GPU 的可信数据时，可以禁用预测器并执行实测搜索。

聚合部署与 P/D 分离使用相同预算、请求分布和 SLO 进行候选筛选。最终排名由实测确认；若预测与实测偏差过大，应降低预测器权重并保留误差证据。

## 3. vLLM benchmark 接入

官方 benchmark CLI 提供在线 serving、离线吞吐及扫描等入口。文档明确指出指标术语可能因工具而异；重复请求还可能复用 prefix cache，影响结果。[3]

适配器按实际框架版本选择命令和解析器，并记录完整原始输出。统一层另外保存：

- 测量边界：客户端、服务端或设备；服务端 queue time 与客户端 TTFT 分字段。
- 测量窗口：包含哪些启动、warmup、稳态和收尾阶段。
- 负载：请求到达方式、并发上限、实际发送量、完成量、失败和超时。
- 缓存：冷/热、重置方式、共享前缀及复用策略。
- 指标公式：输出 token 计数、吞吐分母、ITL/TPOT 的样本和聚合方式。

工具返回同名指标不代表公式相同。解析器无法确认语义时保留原值并标记不可比较，不强制转换成可排名结果。

## 4. SGLang benchmark 与 profiling 接入

当前官方文档区分四种边界：[4]

| 测试层级 | HTTP | 调度器 | 适合回答的问题 |
| --- | --- | --- | --- |
| 在线 serving | 有 | 有 | 实际服务吞吐与请求延迟 |
| 单批 server | 有 | 有 | 单批服务开销，通常不能代表稳态 |
| 离线 throughput | 无 | 有 | 去除 HTTP 后的吞吐 |
| 单批 ModelRunner | 无 | 无 | 静态执行与算子分析 |

这些结果分别归档，不能将静态 ModelRunner 耗时直接充当在线服务性能。当前文档示例使用 `sglang.benchmark.serving` 等路径；旧版本可能使用不同入口，适配器需要版本映射或明确的能力探测。

profiling 任务与正式计分分开运行，避免采样开销污染收益。分布式 trace 保留 rank、设备、时钟信息和运行身份；P/D 两侧的采样不能被误认为单一连续时间线。原始 trace 与解析摘要同时保存，解析器版本也进入证据链。

## 5. 版本化适配器与验收

建议维护“外部版本—功能—解析器—已验证环境”的兼容矩阵。每个适配器提供 `probe`、执行和解析能力；不支持的功能返回结构化原因。

正式启用前，先用小型真实案例核对命令、输出语义、失败处理和资源回收，再跑目标负载。升级框架或外部工具时保留旧基线，重新验证发生变化的接口；预测报告、开发微基准和最终端到端结果始终独立标识。

## 官方资料

1. [AIConfigurator 仓库与迁移说明](https://github.com/ai-dynamo/aiconfigurator)
2. [AISim 官方仓库](https://github.com/ai-dynamo/aisim)
3. [vLLM Benchmark CLI](https://docs.vllm.ai/en/latest/benchmarking/cli/)
4. [SGLang Benchmark and Profiling](https://docs.sglang.io/docs/developer_guide/benchmark_and_profiling)

