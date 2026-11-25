# InferOptLab

**跨模型、跨加速器、跨推理框架的端到端性能诊断与自动调优平台。**

English description: An evidence-driven platform for end-to-end LLM inference profiling, diagnosis, tuning, and validation across accelerators and serving engines.

中文名称建议：推理优化实验平台。仓库名建议：`inferoptlab`。Python 包名建议：`inferoptlab`。

## 当前交付状态

第一阶段已分为 [服务压测](benchmark/load/README.md)、[精度回归](benchmark/accuracy/README.md)、[端到端拆分与算子准备](benchmark/breakdown/README.md)，统一入口 `python -m benchmark {load,accuracy,breakdown}`。C500 移交资料通过 [catalog 资料库](catalog/README.md) 统一导航与检索，原件已按资料、方法、数据集和历史实验分类入库。精度/拆分目前提供协议及离线核验入口，尚未连接新机器上的生成、评分沙箱与原生 profiler。

2026-11-24 调整为 **标准、配方、实验数据分离**：`schemas/` 只保存定义和模板，所有实际配置统一放在 [recipes/](recipes/README.md)，运行数据、完整配方快照、查询索引和基线放在 [experiments/](experiments/README.md)。已加入“请求数 = 并发 × 倍率”和受管 SGLang 缓存填充/重放/逐请求验真。GLM Flash 八卡 C500 的 P/D 扫描候选已准备，使用方法与尚未完成的真机验证见 [P/D 扫描说明](docs/benchmark-cache-replay.md)。

新增 [可复用硬件测试工具](tools/hardware/README.md)：用 YAML 定义机器和测试矩阵，通过 `python -m tools.hardware` 完成探测、逐卡 GEMM/设备复制、证据归档和 YAML 配方导出。已在 metax C500 上跑通完整流程；支持多节点依次测试，集群通信性能仍需单独测量。

C500 服务环境的源码构建与启动入口见 [vLLM/MetaX 构建工具](tools/deployment/metax-vllm/README.md)：固定源码提交、校验 SDK 和 native wheel、构建独立镜像，并提供八卡通信、GLM 真实响应和 AIPerf 小规模流程检查。

`metax-60` 已通过源码镜像运行 GLM-5.3-Flash-W8A8，完成八卡功能、真实响应与三组 AIPerf 检查；镜像、部署配方、测量范围和访问命令见 [2026-11-24 复现报告](docs/metax-60-glm53-vllm-source-build-20261124.md)。当前使用公开依赖齐备的 vLLM/MetaX 0.32 分支，尚未完成正式性能基线。

当前已实现 **v0.2 规约基础、benchmark、第二/三步分析与第四步交接骨架，日期 2026-11-23**：提供版本化规约、离线校验/冻结、AIPerf 测试编排、单机 SGLang 启动器、vLLM 外部服务接入、请求集管理、指标统计和报告。已采集 C500、GLM/DeepSeek/Qwen 元数据并完成 GPU0 微基准及 Qwen 单卡 E2E 流程；详情见 [实机配方](recipes/README.md#metax-实机配方2026-11-23) 与 [集群检查和流程验证](docs/cluster-intake-20261123.md)。分布式 Worker、真实 profiler 适配与 KDA 自动调用仍待实现。

新增 [第二步归因](diagnosis/README.md) 和 [第三步专项分析](analysis/README.md)：从已有真实归档复算指标、检查可比性并产生待验证假设，按 11 类方法生成带采集字段、控制实验、证伪条件、正确性和预算的专项任务。Qwen 与三种 GLM 均有实际作用域的计划；完整设计见 [阶段设计与资料映射](docs/diagnosis-analysis.md)。专项 GPU 采集和因果实验尚未执行。

从 [规约入口](schemas/README.md) 和 [测试模块使用说明](benchmark/README.md) 开始。创建方法见 [模板目录](schemas/templates/README.md)，历史资料录入见 [首版来源配方](recipes/README.md)。`tools/specs.py` 支持结构与组合语义校验、模板实例化、Study 解析和快照冻结；benchmark 配置也纳入统一目录校验。来源缺失与冲突会阻止正式冻结。来源报告数据不等于本平台独立测量。

```powershell
python -m pip install -r schemas/requirements.txt
python tools/specs.py validate
python -m benchmark load plan recipes/plans/benchmark/compare.yaml
python -m unittest discover -s tests -v
```

原始 PDF、图片和文档放回 SourceDocument 指定路径后，使用 `python tools/specs.py validate --sources` 核对哈希；缺失附件不会被视为已经通过核验。真实测试前还需填写服务地址、模型/tokenizer 路径与实际设备映射，详见 [benchmark/README.md](benchmark/README.md)。

新增 [第四步优化交接](optimization/README.md) 与 [Agent 技能目录](agent/README.md)：离线核验第三步任务，生成优化前提和缺口清单；四个阶段各有一个 SKILL.md。配置/代码候选、独立验收和回退已划分接口，尚未接入自动执行。

## 项目目标

输入一个模型、一组计算资源、代表性负载和性能/质量约束，完成：

1. 冻结模型、环境、负载、计时口径和允许变更范围。
2. 建立硬件校准、端到端性能和热点证据。
3. 找出有证据支持的问题，保留未解释问题，提出可证伪的优化假设。
4. 搜索部署与运行配置，或生成代码改动；KDA 可作为其中一个代码优化后端。
5. 独立检查正确性、局部性能、整体性能、稳定性与回归。
6. 交付有适用范围的推荐方案、失败原因和可复现证据。

聚合部署与 P/D 分离属于同一候选空间；只有在相同资源、模型、负载和 SLO 下的实测结果才参与同组排名。最终输出是“在已测空间与给定预算内表现最好的合格候选”，不声称全局最优。

## 推荐阅读顺序

| 文档 | 用途 |
|---|---|
| [项目架构](docs/architecture.md) | 模块边界、双闭环、执行状态机、存储与部署 |
| [仓库目录](docs/repository-layout.md) | 从蓝图扩展成实际代码仓库的目录与依赖方向 |
| [数据契约](docs/data-contracts.md) | Study、Candidate、Trial、Run、证据和任务包 |
| [测量与实验](docs/measurement.md) | 测什么、如何比较、如何从异常产生假设 |
| [独立验收](docs/validation.md) | SLO、正确性、统计、组合回归和判定规则 |
| [平台适配](docs/platform-adapters.md) | 设备、框架、拓扑、能力与支持状态 |
| [KDA 接入](docs/kda-integration.md) | 自建适配接口、任务包、候选包与外部验收 |
| [外部组件](docs/external-integrations.md) | KDA、AISim、vLLM、SGLang 的复用边界 |
| [实施路线](docs/roadmap.md) | 从第一条真实闭环到多平台扩展 |
| [开发任务](docs/backlog.md) | 可直接拆成仓库 Issue 的任务与完成条件 |
| [设计决策](docs/adr/0001-core-decisions.md) | 首版必须保持一致的架构决策 |
| [来源](docs/sources.md) | 官方资料与事实边界 |

## 核心设计

- 模块化 Python 单体控制端，独立执行的 Worker；第一版不要求 Kubernetes。
- 一套版本化数据对象，贯穿配置搜索、代码优化和最终验收。
- 优化器提出候选，Worker 实际执行，独立验收器作出结论。
- 所有优化方向从机制库注册；未知问题可以追加机制，不能被预设分类过滤掉。
- 环境能力以实际探测与验证为依据；无法确认的能力记为 `unverified`。
- 原始数据、预测结果、Agent 自报结果、独立实测结果分开保存。

## 从这份蓝图开始建仓库

1. 在自己的组织或账号下创建 `inferoptlab`，把本目录内容作为设计起点。
2. 首先完成 [M0](docs/roadmap.md)：版本化对象、指标口径、环境与负载冻结、实验存储和资源预约。
3. 选择一个已经能稳定推理的平台/框架/模型组合，完成两类负载的完整闭环。
4. 按 [Backlog](docs/backlog.md) 的 P0 顺序开发，不先铺开所有厂商或复杂 Web 页面。
5. 每新增适配器都要通过同一套契约测试和真机资格测试，才将其标为支持。

### 首次可演示的完成条件

给定一个真实 Study，系统可以恢复中断的实验，比较少量配置，解释一个瓶颈，导出一个代码优化任务，接收一个候选补丁并完成独立端到端验收，最后生成包含失败候选的完整报告。

## 示例

- [Study 示例](examples/study.example.yaml)：目标、资源、负载、搜索空间与停止条件。
- [部署示例](examples/deployments.example.yaml)：由当前 DeploymentSpec 模板展开的候选配置，设备与后端能力仍待验证。
- [优化任务示例](examples/optimization-task.example.yaml)：发给 KDA 或其他执行器的任务契约。
- [机制卡示例](catalog/mechanisms/reduce-redundant-materialization.yaml)：从证据到实验，而非固定优化白名单。

示例中的阈值、形状和预算仅说明结构，不是对 DeepSeek/BW1000 或其他硬件的推荐参数。真实阈值由目标工作负载决定。

## 许可证与第三方代码

本蓝图没有替你决定项目开源许可证或发布到外部仓库。创建仓库时按团队要求选择许可证。外部项目采用适配器引用，保留来源与版本；不要把 KDA 等项目的工作流、代码和第三方子模块视为统一许可证直接复制。
