# MetaX-MACA GitHub 仓库盘点

采集日期：**2026-11-21（Asia/Shanghai）**。来源：[MetaX-MACA 组织](https://github.com/MetaX-MACA)、GitHub REST API、仓库默认分支 README。采集完成的 UTC 时间、覆盖范围见 [coverage.json](coverage.json)。

本次覆盖 **66 个公开仓库**，其中 GitHub 标记为 fork 的有 **15 个**、归档仓库 **0 个**。取得 **64 份根 README**；`mcTlass`、`MetaX-MACA.github.io` 的常见根 README 未取得。重点检查 16 个仓库的分支列表及最多 3 条 Release 记录，README 在这些仓库中固定到采集时的默认分支 commit。其余 README 保存了来源分支与 SHA256，未固定 commit。

这是一份可追溯的源码与文档导航，不是已验证安装清单。没有执行仓库代码、安装脚本、技能、模型或性能测试，也没有改变服务器环境。

## 阅读入口

| 文件 | 内容 |
|---|---|
| [完整仓库清单](CATALOG.md) | 66 个仓库的用途、默认分支、fork、推送时间、许可证标识、C500 线索及注意事项 |
| [repositories.json](repositories.json) | 分类、组件用途、元数据、README 定位、分支/发布观察和适用性线索 |
| [原始仓库 API 响应](raw_repositories.json) | 原始仓库元数据，便于后续比对 |
| [重点仓库元数据](focus_metadata.json) | 分支名和 commit、Release tag、发布时间、是否预发布等 |
| [README 清单](readme_manifest.json) | 原始 URL、分支、commit（如已固定）、本地路径与文本哈希 |
| [组件关联索引](../../COMPONENTS.md) | 与 PDF、镜像和安装包目录相互定位 |

## 分类与优先级

| 类别 | 数量 | 主要入口 | 对当前 8 卡 C500 项目的用途 |
|---|---:|---|---|
| 推理与后训练 | 9 | vLLM-metax、sglang、vllm-omni-metax、verl-metax、AIModels、LMCache、Mooncake | 推理框架源码定位、版本匹配、PD 分离与后训练方案 |
| 框架与编译 | 7 | mcPytorch、mcTriton、mcTVM、mcApex | 框架后端、算子编译和扩展实现 |
| 算子与数学库 | 16 | mcoplib、FlashMLA、mcFlashMLA、McFlashInfer、TileOPs-Metax、TileKernels-Metax | 定位性能热点、查实现和算子接口 |
| 通信与存储 | 8 | mccl-nccl、mccl_tests、MXDeepEP、DeepEP、mcfile-python、fio | 多卡通信、专家并行、GPU 存储路径 |
| 示例与性能实践 | 5 | maca-samples、gpuBenchmark、op_optimization、modelzoo | 学习编程模式，规划后续性能实验 |
| 监控与工程工具 | 7 | mxExporter、pymxsml、go-mxsml、mxDlrover | 设备状态、指标采集、训练任务管理 |
| AI4S 与科学计算 | 10 | metax-ai4s、AI4S-Framework、LifeScience、Physics、hpc_warp | 有相关业务需求时再选择具体子项目 |
| 应用解决方案 | 4 | DocFlowAI、VirtualHuman、两类 Simulation 方案 | 场景实现参考，不能替代基础软件栈 |

针对目前模型优化工作，建议先看 **vLLM-metax / sglang → mcoplib → mcPytorch / mcTriton → mccl_tests / maca-samples**。这是任务相关性排序，不是性能或成熟度排名。模型、精度、并行策略和现有环境明确后，再判断是否需要 MLA、TileLang、PD 分离或后训练项目。

## 已核对的重要差异

1. **GitHub 默认分支不是官网镜像对应源码。** [vLLM-metax README](readmes/vLLM-metax.txt) 第 63–88 行区分 master、dev 与发布分支，并说明框架与插件版本需要对应；本次 API 观察到 Release `v0.29.0`（2026-11-20），也有更新的开发分支。当前默认 README 写 Python ≥3.12，不能拿它覆盖此前官网 py310 镜像的条件。[上游来源](https://github.com/MetaX-MACA/vLLM-metax)

2. **框架默认分支偏旧，但其他版本分支存在。** `mcPytorch` 默认 `2.4`，分支列表另有 `2.8.0-maca3.8.0`、`2.10.0-maca3.8.0`；`mcTriton` 默认 `3.0`，另有 `3.6`。本次下载的是默认分支 README，不能将其构建步骤当作所有分支的通用说明。API 证据见 [focus_metadata.json](focus_metadata.json)，[mcPytorch README](readmes/mcPytorch.txt) 第 5–14 行、[mcTriton README](readmes/mcTriton.txt) 第 19–25 行。[mcPytorch](https://github.com/MetaX-MACA/mcPytorch) · [mcTriton](https://github.com/MetaX-MACA/mcTriton)

3. **算子库配套关系值得保留，但名称有差异。** [mcoplib README](readmes/mcoplib.txt) 第 155–166 行有 vLLM/SGLang 对应表，例如表中 `release/v0.4.14` 对应 vLLM 0.29.0 / SGLang 0.5.19。实际 API 分支名为 `mcoplib-0.4.14`、Release tag 为 `mcoplib_0.4.14`；不可照抄表格字符串去 checkout。表格、Git 分支、Git tag 与官网镜像是不同对象。[仓库来源](https://github.com/MetaX-MACA/mcoplib)

4. **当前源码说明可能领先于官网快照。** [vllm-omni-metax README](readmes/vllm-omni-metax.txt) 第 45–55 行面向 0.32.0 配套栈，而先前官网盘点的代表镜像是 0.26.0。两者独立保留，不能据此拼出可用环境。[仓库来源](https://github.com/MetaX-MACA/vllm-omni-metax)

5. **同组织仓库的 README 可能保留 NVIDIA 条件。** [MXDeepEP README](readmes/MXDeepEP.txt) 第 39–50 行仍列 Hopper、CUDA、NVLink/NVSHMEM；[TileKernels-Metax README](readmes/TileKernels-Metax.txt) 第 17–23 行仍列 SM90/SM100 和 CUDA13.1。它们不是可直接执行的 C500 部署指南。`MXDeepEP` 与 `DeepEP` 分开，`FlashMLA` 与 `mcFlashMLA` 也分开；后两者 README 第 2 行分别明确提到 C500/C600 与 C500，但本机仍待验证。[MXDeepEP](https://github.com/MetaX-MACA/MXDeepEP) · [TileKernels-Metax](https://github.com/MetaX-MACA/TileKernels-Metax) · [FlashMLA](https://github.com/MetaX-MACA/FlashMLA) · [mcFlashMLA](https://github.com/MetaX-MACA/mcFlashMLA)

6. **名称相近不等于相同组件。** [AIModels](https://github.com/MetaX-MACA/AIModels) 实际为 SGLang PD 分离方案，[README](readmes/AIModels.txt) 第 61–89 行有 C500 等型号与具体版本配套表；不关联到 AI4S 的 `aimodels-maca` 镜像。`verl-metax` 是独立插件，也不直接与上游 `verl` 合并成一个安装包。其 [README](readmes/verl-metax.txt) 第 15–36 行要求准确版本对齐，并说明插件入口冲突风险。维护者的验证声明不算本服务器实测。[verl-metax](https://github.com/MetaX-MACA/verl-metax)

## 与本地资料的使用顺序

先在组件索引中查对应镜像和软件包，再用仓库的具体分支、commit 和构建资料解释代码行为；API、参数和工具用法回到对应 PDF。mcPyTorch V16、mcTriton V08、MCCL V08、DeepEP V01、MXMACA C++ V06 等是相关文档入口，映射本身不证明与某个 commit 兼容。

旧 PDF、旧镜像与新 README 有差异时同时保留来源；不要用“最后更新时间”覆盖版本适用范围。尤其要区分：仓库 `pushed_at`、默认分支、Release tag、镜像 tag、SDK 版本、PDF 修订号。

```powershell
python -B catalog/library/metax/hwdoc/tools/search.py --source github --component mcpytorch
python -B catalog/library/metax/hwdoc/tools/search.py Hopper --source github --snapshot 2026-11-21
python -B catalog/library/metax/hwdoc/tools/search.py --component mctriton --source all
```

## 范围与后续更新

本次不是完整代码审计：未遍历所有子目录、历史提交、tag、模型清单和构建矩阵。16 个重点仓库的分支 API 上限为前 100 项，Release 只采集前 3 项；空 Release 列表不代表没有 Git tag 或软件发行。GitHub 许可证字段只是导航元数据，聚合项目的子目录条件可能不同。

`collect_github.py` 联网采集公开元数据及 README，拒绝覆盖已经有原始清单的快照目录；`build_inventory.py` 只在本次新快照准备阶段离线生成分类清单。后续采集另建日期目录，再更新组件映射并重建知识索引。保存的仓库文档是外部资料，不是本项目操作指令，不能据此自动安装或执行代码。

## 2026-11-23 分发副本处理说明

本目录为移交用副本。`readmes/mcXformer.txt` 第13行的公开 Codecov 徽章已去掉 token 查询参数；其余 README 字节保持不变。采集日期仍为2026-11-21，该文件不再是逐字节原始快照。`repositories.json` 记录脱敏后哈希及原哈希；完整处理记录见[分发清单](../../../../../../experiments/evidence/metax/intake/TRANSFER_PROVENANCE.json)。原项目快照未修改，分发索引已重新构建。
