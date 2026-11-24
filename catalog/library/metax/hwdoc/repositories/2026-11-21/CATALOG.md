# MetaX-MACA 公开仓库清单

采集日期：2026-11-21。共 66 个公开仓库；来源为 GitHub API 与默认分支 README。

[盘点结论](README.md) · [机器可读清单](repositories.json) · [覆盖范围](coverage.json)

Fork 为 GitHub 元数据标记，不是适配完成度；非 Fork 也可能包含上游代码。pushed_at 是仓库推送时间，不是默认分支提交时间。
许可证仅按 GitHub SPDX 字段记录，空值/NOASSERTION 不作推断，具体依赖和子目录另行核对。

## 推理与后训练（9）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [AIModels](https://github.com/MetaX-MACA/AIModels) | SGLang PD 分离部署方案，包含 C500 等型号配套表 | `master` | 否 | 2026-06-17T07:54:15Z | Apache-2.0 | README 明确提及 C500；本机未验证 |
| [LMCache](https://github.com/MetaX-MACA/LMCache) | KV Cache 管理框架 fork；默认 README 未确认 C500 条件 | `dev` | 是 | 2026-09-15T01:53:24Z | Apache-2.0 | 顶层 README 未确认 C500 条件 |
| [Mooncake](https://github.com/MetaX-MACA/Mooncake) | 分布式 KV 缓存与传输引擎，README 提及 MACA 传输支持 | `main` | 是 | 2026-09-17T23:47:18Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [Onnxruntime](https://github.com/MetaX-MACA/Onnxruntime) | ONNX Runtime 代码仓库；具体 MetaX 构建条件需查对应分支 | `2.25.2` | 否 | 2025-06-06T02:20:04Z | MIT | 顶层 README 未确认 C500 条件 |
| [ppl.llm.serving](https://github.com/MetaX-MACA/ppl.llm.serving) | PPL 大模型服务工程；具体平台适用性待核对 | `2.20.2` | 否 | 2025-06-05T06:18:41Z | Apache-2.0 | 顶层 README 未确认 C500 条件 |
| [sglang](https://github.com/MetaX-MACA/sglang) | SGLang 推理框架 fork；顶层说明仍以上游为主 | `main` | 是 | 2026-11-17T04:18:57Z | Apache-2.0 | 顶层 README 未确认 C500 条件 |
| [verl-metax](https://github.com/MetaX-MACA/verl-metax) | verl 的独立 MetaX 硬件插件，查看准确版本契约 | `main` | 否 | 2026-10-14T02:21:11Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [vLLM-metax](https://github.com/MetaX-MACA/vLLM-metax) | vLLM 的 MetaX 硬件插件；重点查看发布分支和匹配镜像 | `master` | 否 | 2026-11-20T10:33:30Z | Apache-2.0 | README 提及 C 系列；C500 具体组合待核对 |
| [vllm-omni-metax](https://github.com/MetaX-MACA/vllm-omni-metax) | 多模态多阶段推理适配插件，依赖 vllm-metax 后端 | `main` | 否 | 2026-11-17T05:45:05Z | 未识别 | README 提及 C 系列；C500 具体组合待核对 |

## 框架与编译（7）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [mcApex](https://github.com/MetaX-MACA/mcApex) | 混合精度与分布式训练扩展；顶层 README 保留上游介绍 | `2.25.2` | 否 | 2025-06-04T08:04:05Z | BSD-3-Clause | 顶层 README 未确认 C500 条件 |
| [mcPytorch](https://github.com/MetaX-MACA/mcPytorch) | PyTorch 的 MetaX 后端实现，默认 2.4；另有版本分支 | `2.4` | 否 | 2026-08-03T02:18:58Z | NOASSERTION | README 有 MXC500 镜像示例；需匹配分支 |
| [mcTriton](https://github.com/MetaX-MACA/mcTriton) | Triton 算子编译器适配；与 Triton Inference Server 分开 | `3.0` | 否 | 2026-06-02T11:12:19Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcTVM](https://github.com/MetaX-MACA/mcTVM) | TVM 编译框架 fork，默认 dev；适配范围需看具体子目录 | `dev` | 是 | 2026-11-06T01:09:13Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcXformer](https://github.com/MetaX-MACA/mcXformer) | Transformer 算子与组件工程；顶层适配约束待核对 | `2.22.0` | 否 | 2025-06-05T03:58:31Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [mxJitify](https://github.com/MetaX-MACA/mxJitify) | 运行时编译辅助库；上游 CUDA 说明不能作为 C500 安装依据 | `jitify2` | 否 | 2025-08-21T10:13:59Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [mxNumbax](https://github.com/MetaX-MACA/mxNumbax) | Numba 相关 Python 编译工程，默认 MACA 命名分支 | `2.1.9-maca` | 否 | 2025-08-22T08:21:57Z | NOASSERTION | 顶层 README 未确认 C500 条件 |

## 算子与数学库（16）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [flashattn](https://github.com/MetaX-MACA/flashattn) | FlashAttention 代码仓库；上游要求仍需区分 | `2.25.2` | 否 | 2026-05-20T13:57:27Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [FlashMLA](https://github.com/MetaX-MACA/FlashMLA) | MACA 上的 MLA/注意力实现，README 明确提及 C500/C600 | `main` | 是 | 2026-07-06T09:11:09Z | NOASSERTION | README 明确提及 C500；本机未验证 |
| [mcdf](https://github.com/MetaX-MACA/mcdf) | DataFrame 数据处理生态工程，默认 MACA 命名分支 | `2.1.9-maca` | 否 | 2025-08-22T05:49:29Z | Apache-2.0 | 顶层 README 未确认 C500 条件 |
| [mcEigen](https://github.com/MetaX-MACA/mcEigen) | Eigen 线性代数工程；与本地 mcEigen 手册关联 | `main` | 否 | 2025-06-17T05:47:50Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [mcFaiss](https://github.com/MetaX-MACA/mcFaiss) | 向量相似度检索和聚类库 fork | `1.10.0-maca` | 是 | 2025-09-01T09:55:44Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [McFlashInfer](https://github.com/MetaX-MACA/McFlashInfer) | MACA 平台 LLM 推理算子及内核生成库 | `master` | 否 | 2026-03-09T05:47:28Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcFlashMLA](https://github.com/MetaX-MACA/mcFlashMLA) | 另一份 MACA FlashMLA 实现，README 明确提及 C500；单独保留 | `main` | 是 | 2026-07-06T09:08:40Z | NOASSERTION | README 明确提及 C500；本机未验证 |
| [mcoplib](https://github.com/MetaX-MACA/mcoplib) | MetaX 高性能算子库，README 含 vLLM/SGLang 配套关系 | `main` | 否 | 2026-11-20T09:55:17Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcpy](https://github.com/MetaX-MACA/mcpy) | 数组计算生态工程，默认 MACA 命名分支 | `2.1.9-maca` | 否 | 2025-08-22T07:49:36Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [mcSolver](https://github.com/MetaX-MACA/mcSolver) | MetaX GPU 加速矩阵分解与线性方程求解库 | `2.25.2` | 否 | 2025-06-04T09:58:07Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcSparse](https://github.com/MetaX-MACA/mcSparse) | MetaX 稀疏线性代数基础库 | `2.25.2` | 否 | 2025-06-04T10:26:08Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcTlass](https://github.com/MetaX-MACA/mcTlass) | 仓库清单可见，常见根 README 未取得；用途和构建要求待确认 | `2.20.2` | 否 | 2025-06-05T04:01:31Z | NOASSERTION | 未取得根 README；未知 |
| [mxCuco](https://github.com/MetaX-MACA/mxCuco) | 并发数据结构相关工程；默认 MACA 命名分支 | `2.1.9-maca` | 否 | 2025-08-21T08:42:50Z | Apache-2.0 | 顶层 README 未确认 C500 条件 |
| [mxRmmx](https://github.com/MetaX-MACA/mxRmmx) | GPU 内存管理工程，README 含 MACA_PATH 构建提示 | `2.1.9-maca` | 否 | 2025-08-21T10:21:05Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [TileKernels-Metax](https://github.com/MetaX-MACA/TileKernels-Metax) | 基于 TileLang 的算子库 fork；默认 README 仍列 NVIDIA 要求 | `dev` | 是 | 2026-07-08T01:16:05Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [TileOPs-Metax](https://github.com/MetaX-MACA/TileOPs-Metax) | 基于 TileLang 的 LLM 算子库 fork，默认 dev | `dev` | 是 | 2026-11-21T14:37:20Z | NOASSERTION | 顶层 README 未确认 C500 条件 |

## 通信与存储（8）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [3FS](https://github.com/MetaX-MACA/3FS) | 分布式文件系统 fork，未从 README 确认 C500 适配 | `main` | 是 | 2025-02-28T01:22:58Z | MIT | 顶层 README 未确认 C500 条件 |
| [DeepEP](https://github.com/MetaX-MACA/DeepEP) | DeepEP 上游 fork；与 MXDeepEP 分开记录 | `main` | 是 | 2025-02-26T09:54:18Z | MIT | 顶层 README 未确认 C500 条件 |
| [fio](https://github.com/MetaX-MACA/fio) | 增加 MACA libmcfile I/O 引擎的 fio 工程 | `master` | 是 | 2026-11-09T02:50:15Z | GPL-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mccl-nccl](https://github.com/MetaX-MACA/mccl-nccl) | MCCL 集合通信库工程，README 明确要求 MXMACA 环境 | `2.20.5` | 否 | 2026-06-24T08:23:08Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mccl_tests](https://github.com/MetaX-MACA/mccl_tests) | MCCL 性能与通信测试工具；执行前确认资源影响 | `main` | 否 | 2026-06-03T08:00:17Z | BSD-3-Clause | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [mcfile-python](https://github.com/MetaX-MACA/mcfile-python) | MACA mcFile 的 Python 接口 | `mx-dev` | 是 | 2026-09-17T03:18:26Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [MXDeepEP](https://github.com/MetaX-MACA/MXDeepEP) | 专家并行通信工程；顶层 README 保留上游 NVIDIA 条件 | `main` | 否 | 2026-09-17T08:02:53Z | MIT | 顶层 README 未确认 C500 条件 |
| [mxFIO](https://github.com/MetaX-MACA/mxFIO) | MACA MAS 存储测试工程；与 fio 分开保留 | `main` | 否 | 2025-10-22T01:46:04Z | GPL-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |

## 示例与性能实践（5）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [gpuBenchmark](https://github.com/MetaX-MACA/gpuBenchmark) | 支持 MetaX/NVIDIA 的基准测试集合，具体数值不是本机结果 | `main` | 否 | 2025-04-15T09:24:32Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [maca-samples](https://github.com/MetaX-MACA/maca-samples) | MXMACA 基础 GPU 编程示例集合 | `main` | 否 | 2025-08-15T08:33:08Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [modelzoo](https://github.com/MetaX-MACA/modelzoo) | 历史 ModelZoo 导航和模型资源入口 | `main` | 否 | 2023-06-08T07:25:31Z | Apache-2.0 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [op_optimization](https://github.com/MetaX-MACA/op_optimization) | C500 与 TileLang 算子优化竞赛、指南入口 | `master` | 否 | 2026-05-26T09:49:36Z | 未识别 | README 明确提及 C500；本机未验证 |
| [QuickGuide](https://github.com/MetaX-MACA/QuickGuide) | 根 README 只有标题，需进一步查看仓库内容 | `main` | 否 | 2025-07-30T06:08:41Z | 未识别 | 顶层 README 未确认 C500 条件 |

## 监控与工程工具（7）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [go-mxsml](https://github.com/MetaX-MACA/go-mxsml) | MXSML Go 绑定 | `main` | 否 | 2026-11-05T07:25:58Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [goutils](https://github.com/MetaX-MACA/goutils) | 通用 Go 工具包，不等于 GPU 计算框架 | `main` | 否 | 2026-11-08T11:03:01Z | Apache-2.0 | 顶层 README 未确认 C500 条件 |
| [MetaX-MACA.github.io](https://github.com/MetaX-MACA/MetaX-MACA.github.io) | 组织网页工程；常见根 README 未取得 | `main` | 否 | 2025-11-05T03:40:54Z | 未识别 | 未取得根 README；未知 |
| [mxDlrover](https://github.com/MetaX-MACA/mxDlrover) | 分布式训练管理 DLRover fork | `0.4.0-maca` | 是 | 2026-01-09T02:34:51Z | NOASSERTION | 顶层 README 未确认 C500 条件 |
| [mxExporter](https://github.com/MetaX-MACA/mxExporter) | 基于 MXSML 的 MetaX GPU Prometheus 指标导出工具 | `main` | 否 | 2026-06-08T10:07:53Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [pymxsml](https://github.com/MetaX-MACA/pymxsml) | MXSML Python 绑定，README 有 MXC500 示例输出 | `main` | 否 | 2026-03-19T06:26:19Z | NOASSERTION | README 有 MXC500 示例；非支持矩阵 |
| [simple-jenkins-githubaction](https://github.com/MetaX-MACA/simple-jenkins-githubaction) | 触发 Jenkins 的 CI Action；非模型运行依赖 | `main` | 否 | 2026-05-26T08:26:20Z | MIT | 顶层 README 未确认 C500 条件 |

## AI4S 与科学计算（10）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [AI4S-Framework](https://github.com/MetaX-MACA/AI4S-Framework) | DeepXDE、PaddleScience、PhysicsNeMo 等适配方案集合 | `main` | 否 | 2026-08-24T02:19:00Z | 未识别 | README 提及 C 系列；C500 具体组合待核对 |
| [GeoScience](https://github.com/MetaX-MACA/GeoScience) | 地球科学模型与应用集合 | `main` | 否 | 2026-08-19T05:56:40Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [hpc_warp](https://github.com/MetaX-MACA/hpc_warp) | Warp v1.8.1 的 MetaX 适配，README 指向配套镜像 | `releases/v1.8.1` | 是 | 2026-01-13T07:54:38Z | Apache-2.0 | README 提及 C 系列；C500 具体组合待核对 |
| [LifeScience](https://github.com/MetaX-MACA/LifeScience) | 生命科学与蛋白质、分子应用集合 | `main` | 否 | 2026-10-13T02:25:49Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [Materials](https://github.com/MetaX-MACA/Materials) | 材料科学模型与计算方案集合 | `main` | 否 | 2026-10-13T02:31:16Z | 未识别 | README 提及 C 系列；C500 具体组合待核对 |
| [MedicalImage](https://github.com/MetaX-MACA/MedicalImage) | 医学影像模型与适配方案集合 | `main` | 否 | 2026-10-13T02:30:02Z | 未识别 | README 提及 C 系列；C500 具体组合待核对 |
| [metax-ai4s](https://github.com/MetaX-MACA/metax-ai4s) | AI4S 领域总导航 | `main` | 否 | 2026-10-10T11:52:32Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [metax-lifescience-toolkit](https://github.com/MetaX-MACA/metax-lifescience-toolkit) | 生命科学 Agent skills 工具包；本次只盘点，未安装技能 | `main` | 否 | 2026-09-22T02:59:37Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [Physics](https://github.com/MetaX-MACA/Physics) | 物理仿真及科学机器学习框架集合 | `main` | 否 | 2026-11-18T02:43:42Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |
| [WeatherForecast](https://github.com/MetaX-MACA/WeatherForecast) | 气象预报模型集合 | `main` | 否 | 2026-10-13T02:39:41Z | 未识别 | README 有 MetaX/MACA 线索；C500 条件待核对 |

## 应用解决方案（4）

| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |
|---|---|---|---|---|---|---|
| [Autonomous_Driving_Simulation](https://github.com/MetaX-MACA/Autonomous_Driving_Simulation) | 自动驾驶场景重建、编辑与数据增强方案 | `master` | 否 | 2025-05-29T08:05:59Z | Apache-2.0 | README 提及 C 系列；C500 具体组合待核对 |
| [DocFlowAI](https://github.com/MetaX-MACA/DocFlowAI) | 文档结构化与多模态解析方案 | `main` | 否 | 2025-07-28T07:33:38Z | AGPL-3.0 | README 提及 C 系列；C500 具体组合待核对 |
| [Embodied_AI_Simulation](https://github.com/MetaX-MACA/Embodied_AI_Simulation) | 具身智能仿真方案 | `main` | 否 | 2025-06-18T01:17:55Z | Apache-2.0 | README 提及 C 系列；C500 具体组合待核对 |
| [VirtualHuman](https://github.com/MetaX-MACA/VirtualHuman) | 虚拟人应用迁移方案 | `main` | 否 | 2025-12-24T03:13:23Z | NOASSERTION | README 有 MetaX/MACA 线索；C500 条件待核对 |

## 逐仓库证据与分支观察

### 3FS

- 来源：[https://github.com/MetaX-MACA/3FS](https://github.com/MetaX-MACA/3FS)；归档=False，禁用=False。
- [README 快照](readmes/3FS.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/3FS/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### AI4S-Framework

- 来源：[https://github.com/MetaX-MACA/AI4S-Framework](https://github.com/MetaX-MACA/AI4S-Framework)；归档=False，禁用=False。
- [README 快照](readmes/AI4S-Framework.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/AI4S-Framework/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：33（查看完整上下文，不作自动兼容结论）。

### AIModels

- 来源：[https://github.com/MetaX-MACA/AIModels](https://github.com/MetaX-MACA/AIModels)；归档=False，禁用=False。
- [README 快照](readmes/AIModels.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/AIModels/master/README.md)；分支 `master`；commit `未固定，已保存文本 SHA256`。
- 核对事项：此仓库实际为 PD 分离方案，不能因名称相近而关联到 AI4S aimodels-maca 镜像。表中具体 SDK 要求仅针对对应 SGLang 行。
- 原文候选行：14, 70, 118, 149, 176, 203, 230, 261, 267（查看完整上下文，不作自动兼容结论）。

### Autonomous_Driving_Simulation

- 来源：[https://github.com/MetaX-MACA/Autonomous_Driving_Simulation](https://github.com/MetaX-MACA/Autonomous_Driving_Simulation)；归档=False，禁用=False。
- [README 快照](readmes/Autonomous_Driving_Simulation.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/Autonomous_Driving_Simulation/master/README.md)；分支 `master`；commit `未固定，已保存文本 SHA256`。

### DeepEP

- 来源：[https://github.com/MetaX-MACA/DeepEP](https://github.com/MetaX-MACA/DeepEP)；归档=False，禁用=False。
- [README 快照](readmes/DeepEP.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/DeepEP/3885404ffb31a3d9cbd238aa1a366408881bb069/README.md)；分支 `main`；commit `3885404ffb31a3d9cbd238aa1a366408881bb069`。
- 核对事项：fork 与 MXDeepEP 是不同仓库；顶层 NVIDIA 要求不证明 C500 支持或不支持。
- 原文候选行：41, 43, 285（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/DeepEP/branches?per_page=100)：`main`。
- [Release API](https://api.github.com/repos/MetaX-MACA/DeepEP/releases?per_page=3)：本次返回空列表。

### DocFlowAI

- 来源：[https://github.com/MetaX-MACA/DocFlowAI](https://github.com/MetaX-MACA/DocFlowAI)；归档=False，禁用=False。
- [README 快照](readmes/DocFlowAI.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/DocFlowAI/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### Embodied_AI_Simulation

- 来源：[https://github.com/MetaX-MACA/Embodied_AI_Simulation](https://github.com/MetaX-MACA/Embodied_AI_Simulation)；归档=False，禁用=False。
- [README 快照](readmes/Embodied_AI_Simulation.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/Embodied_AI_Simulation/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### fio

- 来源：[https://github.com/MetaX-MACA/fio](https://github.com/MetaX-MACA/fio)；归档=False，禁用=False。
- [README 快照](readmes/fio.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/fio/master/README.md)；分支 `master`；commit `未固定，已保存文本 SHA256`。

### flashattn

- 来源：[https://github.com/MetaX-MACA/flashattn](https://github.com/MetaX-MACA/flashattn)；归档=False，禁用=False。
- [README 快照](readmes/flashattn.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/flashattn/2.25.2/README.md)；分支 `2.25.2`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：69, 72（查看完整上下文，不作自动兼容结论）。

### FlashMLA

- 来源：[https://github.com/MetaX-MACA/FlashMLA](https://github.com/MetaX-MACA/FlashMLA)；归档=False，禁用=False。
- [README 快照](readmes/FlashMLA.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/FlashMLA/b246af19465084b1a97d4de480c3ea0c1b356e4c/README.md)；分支 `main`；commit `b246af19465084b1a97d4de480c3ea0c1b356e4c`。
- 核对事项：README 明确写 C500/C600，但本机仍待验证；不与 mcFlashMLA 合并成同一版本。
- 原文候选行：2（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/FlashMLA/branches?per_page=100)：`main`。
- [Release API](https://api.github.com/repos/MetaX-MACA/FlashMLA/releases?per_page=3)：本次返回空列表。

### GeoScience

- 来源：[https://github.com/MetaX-MACA/GeoScience](https://github.com/MetaX-MACA/GeoScience)；归档=False，禁用=False。
- [README 快照](readmes/GeoScience.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/GeoScience/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：34（查看完整上下文，不作自动兼容结论）。

### go-mxsml

- 来源：[https://github.com/MetaX-MACA/go-mxsml](https://github.com/MetaX-MACA/go-mxsml)；归档=False，禁用=False。
- [README 快照](readmes/go-mxsml.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/go-mxsml/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### goutils

- 来源：[https://github.com/MetaX-MACA/goutils](https://github.com/MetaX-MACA/goutils)；归档=False，禁用=False。
- [README 快照](readmes/goutils.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/goutils/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### gpuBenchmark

- 来源：[https://github.com/MetaX-MACA/gpuBenchmark](https://github.com/MetaX-MACA/gpuBenchmark)；归档=False，禁用=False。
- [README 快照](readmes/gpuBenchmark.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/gpuBenchmark/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：5, 26（查看完整上下文，不作自动兼容结论）。

### hpc_warp

- 来源：[https://github.com/MetaX-MACA/hpc_warp](https://github.com/MetaX-MACA/hpc_warp)；归档=False，禁用=False。
- [README 快照](readmes/hpc_warp.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/hpc_warp/releases/v1.8.1/README.md)；分支 `releases/v1.8.1`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：24（查看完整上下文，不作自动兼容结论）。

### LifeScience

- 来源：[https://github.com/MetaX-MACA/LifeScience](https://github.com/MetaX-MACA/LifeScience)；归档=False，禁用=False。
- [README 快照](readmes/LifeScience.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/LifeScience/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：58（查看完整上下文，不作自动兼容结论）。

### LMCache

- 来源：[https://github.com/MetaX-MACA/LMCache](https://github.com/MetaX-MACA/LMCache)；归档=False，禁用=False。
- [README 快照](readmes/LMCache.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/LMCache/dev/README.md)；分支 `dev`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：47, 55, 81（查看完整上下文，不作自动兼容结论）。

### maca-samples

- 来源：[https://github.com/MetaX-MACA/maca-samples](https://github.com/MetaX-MACA/maca-samples)；归档=False，禁用=False。
- [README 快照](readmes/maca-samples.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/maca-samples/e6de14cc4d9248768d066a1475450ed7705fd766/README.md)；分支 `main`；commit `e6de14cc4d9248768d066a1475450ed7705fd766`。
- [分支 API](https://api.github.com/repos/MetaX-MACA/maca-samples/branches?per_page=100)：`main`。
- [Release API](https://api.github.com/repos/MetaX-MACA/maca-samples/releases?per_page=3)：本次返回空列表。

### Materials

- 来源：[https://github.com/MetaX-MACA/Materials](https://github.com/MetaX-MACA/Materials)；归档=False，禁用=False。
- [README 快照](readmes/Materials.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/Materials/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：34（查看完整上下文，不作自动兼容结论）。

### mcApex

- 来源：[https://github.com/MetaX-MACA/mcApex](https://github.com/MetaX-MACA/mcApex)；归档=False，禁用=False。
- [README 快照](readmes/mcApex.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcApex/2.25.2/README.md)；分支 `2.25.2`；commit `未固定，已保存文本 SHA256`。

### mccl-nccl

- 来源：[https://github.com/MetaX-MACA/mccl-nccl](https://github.com/MetaX-MACA/mccl-nccl)；归档=False，禁用=False。
- [README 快照](readmes/mccl-nccl.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mccl-nccl/2.20.5/README.md)；分支 `2.20.5`；commit `未固定，已保存文本 SHA256`。

### mccl_tests

- 来源：[https://github.com/MetaX-MACA/mccl_tests](https://github.com/MetaX-MACA/mccl_tests)；归档=False，禁用=False。
- [README 快照](readmes/mccl_tests.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mccl_tests/1e44d4af1b177f2ab9e23bdd0b393ad757d08f4e/README.md)；分支 `main`；commit `1e44d4af1b177f2ab9e23bdd0b393ad757d08f4e`。
- [分支 API](https://api.github.com/repos/MetaX-MACA/mccl_tests/branches?per_page=100)：`main`。
- [Release API](https://api.github.com/repos/MetaX-MACA/mccl_tests/releases?per_page=3)：本次返回空列表。

### mcdf

- 来源：[https://github.com/MetaX-MACA/mcdf](https://github.com/MetaX-MACA/mcdf)；归档=False，禁用=False。
- [README 快照](readmes/mcdf.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcdf/2.1.9-maca/README.md)；分支 `2.1.9-maca`；commit `未固定，已保存文本 SHA256`。

### mcEigen

- 来源：[https://github.com/MetaX-MACA/mcEigen](https://github.com/MetaX-MACA/mcEigen)；归档=False，禁用=False。
- [README 快照](readmes/mcEigen.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcEigen/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### mcFaiss

- 来源：[https://github.com/MetaX-MACA/mcFaiss](https://github.com/MetaX-MACA/mcFaiss)；归档=False，禁用=False。
- [README 快照](readmes/mcFaiss.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcFaiss/1.10.0-maca/README.md)；分支 `1.10.0-maca`；commit `未固定，已保存文本 SHA256`。

### mcfile-python

- 来源：[https://github.com/MetaX-MACA/mcfile-python](https://github.com/MetaX-MACA/mcfile-python)；归档=False，禁用=False。
- [README 快照](readmes/mcfile-python.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcfile-python/mx-dev/README.md)；分支 `mx-dev`；commit `未固定，已保存文本 SHA256`。

### McFlashInfer

- 来源：[https://github.com/MetaX-MACA/McFlashInfer](https://github.com/MetaX-MACA/McFlashInfer)；归档=False，禁用=False。
- [README 快照](readmes/McFlashInfer.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/McFlashInfer/master/README.md)；分支 `master`；commit `未固定，已保存文本 SHA256`。

### mcFlashMLA

- 来源：[https://github.com/MetaX-MACA/mcFlashMLA](https://github.com/MetaX-MACA/mcFlashMLA)；归档=False，禁用=False。
- [README 快照](readmes/mcFlashMLA.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcFlashMLA/c2dbf6e9328f839b96970662e6ec379b6d79d6c8/README.md)；分支 `main`；commit `c2dbf6e9328f839b96970662e6ec379b6d79d6c8`。
- 核对事项：README 明确写 C500；与 FlashMLA 分开保留 commit、分支和条件。
- 原文候选行：2（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/mcFlashMLA/branches?per_page=100)：`main`、`mcFlashMLA`。
- [Release API](https://api.github.com/repos/MetaX-MACA/mcFlashMLA/releases?per_page=3)：本次返回空列表。

### mcoplib

- 来源：[https://github.com/MetaX-MACA/mcoplib](https://github.com/MetaX-MACA/mcoplib)；归档=False，禁用=False。
- [README 快照](readmes/mcoplib.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcoplib/0e64378285a5c693b15a57f7c03b600a520ce1fa/README.md)；分支 `main`；commit `0e64378285a5c693b15a57f7c03b600a520ce1fa`。
- 核对事项：README 的配套表使用 release/v0.4.x 标签形式，API 实际分支为 mcoplib-0.4.x、Release tag 为 mcoplib_0.4.x；三者必须分开核对。
- 原文候选行：67, 502（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/mcoplib/branches?per_page=100)：`main`、`mcoplib_params_dump`、`mcoplib_0.2.0`、`mcoplib_0.3.0`、`mcoplib_0.3.1`、`mcoplib_0.4.0`、`mcoplib_0.4.1`、`mcoplib_0.4.2`、`mcoplib_0.4.3`、`mcoplib-0.4.4`、`mcoplib-0.4.5`、`mcoplib-0.4.6`、`mcoplib-0.4.7`、`mcoplib-0.4.8`、`mcoplib-0.4.9`、`mcoplib-0.4.10`、`mcoplib-0.4.11`、`mcoplib-0.4.12`、`mcoplib-0.4.13`、`mcoplib-0.4.14`、`mcoplib-0.4.15`、`mcoplib-0.4.16`、`vllm0.13.0_sglang0.5.6`、`vllm_0120_sgl_056`、`vllm_0130_sglang_057`。
- [Release API](https://api.github.com/repos/MetaX-MACA/mcoplib/releases?per_page=3)：`mcoplib_0.4.16`、`mcoplib_0.4.15`、`mcoplib_0.4.14`。

### mcpy

- 来源：[https://github.com/MetaX-MACA/mcpy](https://github.com/MetaX-MACA/mcpy)；归档=False，禁用=False。
- [README 快照](readmes/mcpy.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcpy/2.1.9-maca/README.md)；分支 `2.1.9-maca`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：49（查看完整上下文，不作自动兼容结论）。

### mcPytorch

- 来源：[https://github.com/MetaX-MACA/mcPytorch](https://github.com/MetaX-MACA/mcPytorch)；归档=False，禁用=False。
- [README 快照](readmes/mcPytorch.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcPytorch/b3db5eed6a6e330133cd3d4b173f8da392aa6bcb/README.md)；分支 `2.4`；commit `b3db5eed6a6e330133cd3d4b173f8da392aa6bcb`。
- 核对事项：默认 2.4 不能代表全部版本；API 还列出 2.8.0-maca3.8.0 和 2.10.0-maca3.8.0。旧 README 镜像示例不得覆盖新 PDF/镜像约束。
- 原文候选行：14, 23, 24（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/mcPytorch/branches?per_page=100)：`2.0`、`2.4`、`2.8.0-maca3.8.0`、`2.10.0-maca3.8.0`、`dependabot/bundler/ios/TestApp/bundler-00f0729802`。
- [Release API](https://api.github.com/repos/MetaX-MACA/mcPytorch/releases?per_page=3)：本次返回空列表。

### mcSolver

- 来源：[https://github.com/MetaX-MACA/mcSolver](https://github.com/MetaX-MACA/mcSolver)；归档=False，禁用=False。
- [README 快照](readmes/mcSolver.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcSolver/2.25.2/README.md)；分支 `2.25.2`；commit `未固定，已保存文本 SHA256`。

### mcSparse

- 来源：[https://github.com/MetaX-MACA/mcSparse](https://github.com/MetaX-MACA/mcSparse)；归档=False，禁用=False。
- [README 快照](readmes/mcSparse.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcSparse/2.25.2/README.md)；分支 `2.25.2`；commit `未固定，已保存文本 SHA256`。

### mcTlass

- 来源：[https://github.com/MetaX-MACA/mcTlass](https://github.com/MetaX-MACA/mcTlass)；归档=False，禁用=False。
- 常见根 README 未取得；不代表仓库无其他文档。

### mcTriton

- 来源：[https://github.com/MetaX-MACA/mcTriton](https://github.com/MetaX-MACA/mcTriton)；归档=False，禁用=False。
- [README 快照](readmes/mcTriton.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcTriton/7dd407c26568fceaca44cb894138e5202d369805/README.md)；分支 `3.0`；commit `7dd407c26568fceaca44cb894138e5202d369805`。
- 核对事项：存在 3.0 与 3.6 分支；本次 README 取自默认 3.0，不能据此推定 3.6 构建要求。
- [分支 API](https://api.github.com/repos/MetaX-MACA/mcTriton/branches?per_page=100)：`3.0`、`3.6`。
- [Release API](https://api.github.com/repos/MetaX-MACA/mcTriton/releases?per_page=3)：本次返回空列表。

### mcTVM

- 来源：[https://github.com/MetaX-MACA/mcTVM](https://github.com/MetaX-MACA/mcTVM)；归档=False，禁用=False。
- [README 快照](readmes/mcTVM.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcTVM/dev/README.md)；分支 `dev`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：29, 60（查看完整上下文，不作自动兼容结论）。

### mcXformer

- 来源：[https://github.com/MetaX-MACA/mcXformer](https://github.com/MetaX-MACA/mcXformer)；归档=False，禁用=False。
- [README 快照](readmes/mcXformer.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mcXformer/2.22.0/README.md)；分支 `2.22.0`；commit `未固定，已保存文本 SHA256`。

### MedicalImage

- 来源：[https://github.com/MetaX-MACA/MedicalImage](https://github.com/MetaX-MACA/MedicalImage)；归档=False，禁用=False。
- [README 快照](readmes/MedicalImage.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/MedicalImage/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：46（查看完整上下文，不作自动兼容结论）。

### metax-ai4s

- 来源：[https://github.com/MetaX-MACA/metax-ai4s](https://github.com/MetaX-MACA/metax-ai4s)；归档=False，禁用=False。
- [README 快照](readmes/metax-ai4s.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/metax-ai4s/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：238（查看完整上下文，不作自动兼容结论）。

### metax-lifescience-toolkit

- 来源：[https://github.com/MetaX-MACA/metax-lifescience-toolkit](https://github.com/MetaX-MACA/metax-lifescience-toolkit)；归档=False，禁用=False。
- [README 快照](readmes/metax-lifescience-toolkit.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/metax-lifescience-toolkit/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：15（查看完整上下文，不作自动兼容结论）。

### MetaX-MACA.github.io

- 来源：[https://github.com/MetaX-MACA/MetaX-MACA.github.io](https://github.com/MetaX-MACA/MetaX-MACA.github.io)；归档=False，禁用=False。
- 常见根 README 未取得；不代表仓库无其他文档。

### modelzoo

- 来源：[https://github.com/MetaX-MACA/modelzoo](https://github.com/MetaX-MACA/modelzoo)；归档=False，禁用=False。
- [README 快照](readmes/modelzoo.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/modelzoo/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 核对事项：保留历史入口；不得等同于官网当前各 ModelZoo 镜像。

### Mooncake

- 来源：[https://github.com/MetaX-MACA/Mooncake](https://github.com/MetaX-MACA/Mooncake)；归档=False，禁用=False。
- [README 快照](readmes/Mooncake.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/Mooncake/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：23, 197, 199, 201, 203（查看完整上下文，不作自动兼容结论）。

### mxCuco

- 来源：[https://github.com/MetaX-MACA/mxCuco](https://github.com/MetaX-MACA/mxCuco)；归档=False，禁用=False。
- [README 快照](readmes/mxCuco.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxCuco/2.1.9-maca/README.md)；分支 `2.1.9-maca`；commit `未固定，已保存文本 SHA256`。

### MXDeepEP

- 来源：[https://github.com/MetaX-MACA/MXDeepEP](https://github.com/MetaX-MACA/MXDeepEP)；归档=False，禁用=False。
- [README 快照](readmes/MXDeepEP.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/MXDeepEP/5ce9cce6efc06f2596b8f395e5cae3c78494699a/README.md)；分支 `main`；commit `5ce9cce6efc06f2596b8f395e5cae3c78494699a`。
- 核对事项：根 README 仍列 Hopper/CUDA/NVLink/NVSHMEM；仓库另有 build.md 和 maca_tools，但本次未审计其源码或构建流程。C500 部署条件待核实。
- 原文候选行：41, 43, 285（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/MXDeepEP/branches?per_page=100)：`main`。
- [Release API](https://api.github.com/repos/MetaX-MACA/MXDeepEP/releases?per_page=3)：本次返回空列表。

### mxDlrover

- 来源：[https://github.com/MetaX-MACA/mxDlrover](https://github.com/MetaX-MACA/mxDlrover)；归档=False，禁用=False。
- [README 快照](readmes/mxDlrover.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxDlrover/0.4.0-maca/README.md)；分支 `0.4.0-maca`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：16（查看完整上下文，不作自动兼容结论）。

### mxExporter

- 来源：[https://github.com/MetaX-MACA/mxExporter](https://github.com/MetaX-MACA/mxExporter)；归档=False，禁用=False。
- [README 快照](readmes/mxExporter.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxExporter/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### mxFIO

- 来源：[https://github.com/MetaX-MACA/mxFIO](https://github.com/MetaX-MACA/mxFIO)；归档=False，禁用=False。
- [README 快照](readmes/mxFIO.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxFIO/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### mxJitify

- 来源：[https://github.com/MetaX-MACA/mxJitify](https://github.com/MetaX-MACA/mxJitify)；归档=False，禁用=False。
- [README 快照](readmes/mxJitify.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxJitify/jitify2/README.md)；分支 `jitify2`；commit `未固定，已保存文本 SHA256`。

### mxNumbax

- 来源：[https://github.com/MetaX-MACA/mxNumbax](https://github.com/MetaX-MACA/mxNumbax)；归档=False，禁用=False。
- [README 快照](readmes/mxNumbax.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxNumbax/2.1.9-maca/README.rst)；分支 `2.1.9-maca`；commit `未固定，已保存文本 SHA256`。

### mxRmmx

- 来源：[https://github.com/MetaX-MACA/mxRmmx](https://github.com/MetaX-MACA/mxRmmx)；归档=False，禁用=False。
- [README 快照](readmes/mxRmmx.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/mxRmmx/2.1.9-maca/README.md)；分支 `2.1.9-maca`；commit `未固定，已保存文本 SHA256`。

### Onnxruntime

- 来源：[https://github.com/MetaX-MACA/Onnxruntime](https://github.com/MetaX-MACA/Onnxruntime)；归档=False，禁用=False。
- [README 快照](readmes/Onnxruntime.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/Onnxruntime/2.25.2/README.md)；分支 `2.25.2`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：5（查看完整上下文，不作自动兼容结论）。

### op_optimization

- 来源：[https://github.com/MetaX-MACA/op_optimization](https://github.com/MetaX-MACA/op_optimization)；归档=False，禁用=False。
- [README 快照](readmes/op_optimization.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/op_optimization/67875de0d2f159f7380ad6471a34bf8c6551a8f1/README.md)；分支 `master`；commit `67875de0d2f159f7380ad6471a34bf8c6551a8f1`。
- 原文候选行：11, 41, 55（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/op_optimization/branches?per_page=100)：`master`。
- [Release API](https://api.github.com/repos/MetaX-MACA/op_optimization/releases?per_page=3)：本次返回空列表。

### Physics

- 来源：[https://github.com/MetaX-MACA/Physics](https://github.com/MetaX-MACA/Physics)；归档=False，禁用=False。
- [README 快照](readmes/Physics.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/Physics/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：58（查看完整上下文，不作自动兼容结论）。

### ppl.llm.serving

- 来源：[https://github.com/MetaX-MACA/ppl.llm.serving](https://github.com/MetaX-MACA/ppl.llm.serving)；归档=False，禁用=False。
- [README 快照](readmes/ppl.llm.serving.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/ppl.llm.serving/2.20.2/README.md)；分支 `2.20.2`；commit `未固定，已保存文本 SHA256`。

### pymxsml

- 来源：[https://github.com/MetaX-MACA/pymxsml](https://github.com/MetaX-MACA/pymxsml)；归档=False，禁用=False。
- [README 快照](readmes/pymxsml.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/pymxsml/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 核对事项：MXC500 出现在示例输出中，属于示例线索，不是完整支持矩阵。
- 原文候选行：28, 94（查看完整上下文，不作自动兼容结论）。

### QuickGuide

- 来源：[https://github.com/MetaX-MACA/QuickGuide](https://github.com/MetaX-MACA/QuickGuide)；归档=False，禁用=False。
- [README 快照](readmes/QuickGuide.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/QuickGuide/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### sglang

- 来源：[https://github.com/MetaX-MACA/sglang](https://github.com/MetaX-MACA/sglang)；归档=False，禁用=False。
- [README 快照](readmes/sglang.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/sglang/e55a35fbcd491eeb3743be9b021534512c6acf85/README.md)；分支 `main`；commit `e55a35fbcd491eeb3743be9b021534512c6acf85`。
- 原文候选行：64（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/sglang/branches?per_page=100)：`main`、`release/v0.5.7`、`release/v0.5.10`、`release/v0.5.12`、`release/v0.5.14-cr1`、`release/v0.5.14-cr2`、`release/v0.5.14`、`release/v0.5.19`、`release/v0.5.21`、`release/v0.5.22-cr1`。
- [Release API](https://api.github.com/repos/MetaX-MACA/sglang/releases?per_page=3)：本次返回空列表。

### simple-jenkins-githubaction

- 来源：[https://github.com/MetaX-MACA/simple-jenkins-githubaction](https://github.com/MetaX-MACA/simple-jenkins-githubaction)；归档=False，禁用=False。
- [README 快照](readmes/simple-jenkins-githubaction.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/simple-jenkins-githubaction/main/README)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### TileKernels-Metax

- 来源：[https://github.com/MetaX-MACA/TileKernels-Metax](https://github.com/MetaX-MACA/TileKernels-Metax)；归档=False，禁用=False。
- [README 快照](readmes/TileKernels-Metax.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/TileKernels-Metax/0266ab740980de7dc03a828b8259cd73d100c2eb/README.md)；分支 `dev`；commit `0266ab740980de7dc03a828b8259cd73d100c2eb`。
- 核对事项：默认 dev README 列 NVIDIA SM90/SM100 与 CUDA13.1；仓库名中的 Metax 不足以证明该分支在 C500 可用。
- 原文候选行：5, 22（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/TileKernels-Metax/branches?per_page=100)：`dev`、`main`。
- [Release API](https://api.github.com/repos/MetaX-MACA/TileKernels-Metax/releases?per_page=3)：本次返回空列表。

### TileOPs-Metax

- 来源：[https://github.com/MetaX-MACA/TileOPs-Metax](https://github.com/MetaX-MACA/TileOPs-Metax)；归档=False，禁用=False。
- [README 快照](readmes/TileOPs-Metax.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/TileOPs-Metax/916221870e092fff9c2219ef7d15f2e52299e141/README.md)；分支 `dev`；commit `916221870e092fff9c2219ef7d15f2e52299e141`。
- 核对事项：默认 dev README 主要为上游算子项目说明；尚未从顶层资料确认 C500 运行条件。
- 原文候选行：33, 76, 149（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/TileOPs-Metax/branches?per_page=100)：`dev`、`main`、`stats`。
- [Release API](https://api.github.com/repos/MetaX-MACA/TileOPs-Metax/releases?per_page=3)：本次返回空列表。

### verl-metax

- 来源：[https://github.com/MetaX-MACA/verl-metax](https://github.com/MetaX-MACA/verl-metax)；归档=False，禁用=False。
- [README 快照](readmes/verl-metax.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/verl-metax/b39f7ce49014b605369344287896849a8457a76f/README.md)；分支 `main`；commit `b39f7ce49014b605369344287896849a8457a76f`。
- 核对事项：README 的硬件验证是项目维护者声明，不是本服务器实测；要求 verl-metax 0.9.0 与 verl 0.9.0 对齐，并提示不要同时自动加载两个 MetaX 插件。
- 原文候选行：3, 12, 15, 17, 18, 20, 86（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/verl-metax/branches?per_page=100)：`main`、`release/v0.9.0`。
- [Release API](https://api.github.com/repos/MetaX-MACA/verl-metax/releases?per_page=3)：本次返回空列表。

### VirtualHuman

- 来源：[https://github.com/MetaX-MACA/VirtualHuman](https://github.com/MetaX-MACA/VirtualHuman)；归档=False，禁用=False。
- [README 快照](readmes/VirtualHuman.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/VirtualHuman/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。

### vLLM-metax

- 来源：[https://github.com/MetaX-MACA/vLLM-metax](https://github.com/MetaX-MACA/vLLM-metax)；归档=False，禁用=False。
- [README 快照](readmes/vLLM-metax.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/vLLM-metax/5d0b6a8ebbdcf145cc87e53c594b4ca64d120024/README.md)；分支 `master`；commit `5d0b6a8ebbdcf145cc87e53c594b4ca64d120024`。
- 核对事项：默认 master 跟踪上游；README 区分 master、dev、releases 分支，并要求 vLLM 与插件同版本。当前 README 的 Python>=3.12 不可套用官网历史 py310 镜像。
- 原文候选行：52, 58, 65, 74（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/vLLM-metax/branches?per_page=100)：`fix-int8-w8a8-mla`、`master`、`releases/v0.8.5`、`releases/v0.10.2`、`releases/v0.11.2`、`releases/v0.12.0`、`releases/v0.13.0`、`releases/v0.14.0`、`releases/v0.15.0`、`releases/v0.17.0`、`releases/v0.18.0`、`releases/v0.19.0`、`releases/v0.20.0`、`releases/v0.21.0`、`releases/v0.22.0`、`releases/v0.23.0`、`releases/v0.24.0`、`releases/v0.25.0`、`releases/v0.26.0`、`releases/v0.27.0`、`releases/v0.28.0`、`releases/v0.29.0`、`support_deep_gemm_fp8`、`support-flashinfermla`、`switch-to-torch-stable-api`、`v0.9.1-dev`、`v0.10.1.1-dev`、`v0.10.2-dev`、`v0.11.0-dev`、`v0.11.1rc6-dev`、`v0.11.2-dev`、`v0.12.0-dev`、`v0.13.0-dev`、`v0.14.0-dev`、`v0.15.0-dev`、`v0.17.0-dev`、`v0.18.0-dev`、`v0.19.0-dev`、`v0.20.0-dev`、`v0.21.0-dev`、`v0.22.0-dev`、`v0.23.0-dev`、`v0.24.0-dev`、`v0.25.0-dev`、`v0.26.0-dev`、`v0.27.0-dev`、`v0.28.0-dev`、`v0.29.0-dev`、`v0.30.0-dev`、`v0.32.0-dev`、`vllm-cpu-dockerfile`。
- [Release API](https://api.github.com/repos/MetaX-MACA/vLLM-metax/releases?per_page=3)：`v0.29.0`、`v0.28.0`、`v0.27.0`。

### vllm-omni-metax

- 来源：[https://github.com/MetaX-MACA/vllm-omni-metax](https://github.com/MetaX-MACA/vllm-omni-metax)；归档=False，禁用=False。
- [README 快照](readmes/vllm-omni-metax.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/vllm-omni-metax/679716dd798afc2d3cae5852e7ddfff308507550/README.md)；分支 `main`；commit `679716dd798afc2d3cae5852e7ddfff308507550`。
- 核对事项：当前 main README 指向 0.32.0 软件栈；官网快照中的 0.26.0 样例是另一版本，不能直接混装。
- 原文候选行：11（查看完整上下文，不作自动兼容结论）。
- [分支 API](https://api.github.com/repos/MetaX-MACA/vllm-omni-metax/branches?per_page=100)：`main`、`release/v0.18.0`、`release/v0.19.0rc1`、`v0.20.0-dev`、`v0.22.0-dev`、`v0.26.0-dev`。
- [Release API](https://api.github.com/repos/MetaX-MACA/vllm-omni-metax/releases?per_page=3)：本次返回空列表。

### WeatherForecast

- 来源：[https://github.com/MetaX-MACA/WeatherForecast](https://github.com/MetaX-MACA/WeatherForecast)；归档=False，禁用=False。
- [README 快照](readmes/WeatherForecast.txt) · [采集来源](https://raw.githubusercontent.com/MetaX-MACA/WeatherForecast/main/README.md)；分支 `main`；commit `未固定，已保存文本 SHA256`。
- 原文候选行：30（查看完整上下文，不作自动兼容结论）。

