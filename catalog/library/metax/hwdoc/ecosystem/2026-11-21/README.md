# MXC500 软件生态与镜像盘点

采集日期：**2026-11-21，Asia/Shanghai**。范围：官网 MXC500 正式镜像目录、软件栈目录，以及本地 C500 技术文档。这里的“可用”指**官网列出或文档说明支持**；并不等于已在用户的 8 卡 C500 服务器下载、安装或验证成功。

## 阅读入口

| 文件 | 内容 |
|---|---|
| [镜像家族清单](IMAGE_CATALOG.md) | 62 个家族：2 个基础环境、29 个 AI、11 个 AI4S、20 个 Cloud-Tools；其中 1 个是 Helm Chart，其余是容器镜像家族 |
| [软件安装包目录](SOFTWARE_PACKAGES.md) | 67 个目录条目，包含 Driver、SDK、AI、AI4S、运维/性能工具和 DSL；与镜像家族有重叠 |
| [images.json](images.json) | 镜像家族、用途、完整名称:tag、页面推荐 Driver、更新时间、从 tag 解析出的 Python/PyTorch/OS/架构，以及来源 |
| [software_packages.json](software_packages.json) | 软件包分类目录，供后续程序检索 |
| [coverage.json](coverage.json) | 采集范围、观察数量、访问限制及未验证事项 |

本次浏览 AI 列表的全部 9 页（100 条/页），读到 815 条卡片记录，按名称:tag 去重观察到 711 项；页面存在重复条目和排序变化，**这个数字不是官网权威总量，也不保证覆盖所有标签**。其他分类读到 MXMACA 14、AI4S 28、Cloud-Tools 63 条卡片。本交付按家族保存近期样例和部分 Ubuntu 22.04/amd64 备选，不保存每一条扫描过的标签。历史版本下拉框、归档库、预发布目录未逐项穷举。

## 面向这台 8 卡 C500 的使用顺序

下面是结合目录和文档作出的选型建议，不是实测排名。

| 任务 | 优先查看 | 理由与前置核对 |
|---|---|---|
| 建立基础计算环境 | Driver、SDK、`maca-pytorch` | 先确认固件、驱动、SDK、框架与 Python 组合，再验证板卡可见性和基础计算 |
| 大模型推理与性能对比 | `vllm-metax`、`sglang` | 两套推理框架分别建立基线；按具体模型、精度和并行策略测试，不能仅凭版本新旧判断速度 |
| 复用模型配置和评测流程 | `modelzoo.llm.vllm`、`modelzoo.llm.sglang` | 适合查模型配置与评测入口；ModelZoo 自身的版本号不是底层 vLLM/SGLang 的版本号 |
| SFT / LoRA 微调 | `ms-swift`、`deepspeed`、`xtuner` | 按模型和微调方式选择，保持配套框架版本一致 |
| 强化学习与后训练 | `verl`、`slime` | 与普通推理镜像分开管理，核对 rollout 引擎及训练组件的组合 |
| 自定义算子与性能定位 | mcTriton、TileLang、mxcc、mcProfiler、mcTracer、mxvs | 核心开发组件不全以独立镜像发布，要同时看 SDK、PyTorch 安装包和 Perf 工具包 |
| 量化部署 | `maca-llm-quantizer` | 量化产物还需核对目标推理框架、模型和精度支持 |
| 集群化部署与监控 | `mx-exporter`、GPU Operator、调度与拓扑组件 | 适用于 Kubernetes/平台化场景；普通单机模型基线可先使用框架镜像 |

此前连通性测试读到目标主机为 `x86_64`、内核 `5.15.0-204-generic`。该结果只证明当时的主机架构和内核；OS 发行版、GPU 驱动、SDK、容器运行时、显存和互连拓扑仍未核对。本次盘点没有重新采集服务器环境。

## 重点镜像版本样例

以下各行的版本来自官网相应卡片，均为“官网列出，待本机验证”。**推荐 Driver 是该 tag 的页面推荐值，不能套用到同家族的其他 tag。** 来源：[AI 镜像目录](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=AI&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)。

| 软件 | 本次观察版本 / 构建 | PyTorch / Python | 容器 OS / 架构样例 | 推荐 Driver |
|---|---|---|---|---|
| maca-pytorch | `3.10.1.2` | `2.10 / 3.12` | Ubuntu 24.04 / amd64 | `3.100.0` |
| vllm-metax | `0.29.0 / maca.ai3.9.0.9` | `2.10 / 3.10` | Ubuntu 24.04 / amd64 | `3.9.0` |
| vllm-metax（Ubuntu 22 备选） | `0.28.0 / maca.ai3.8.2.401` | `2.10 / 3.12` | Ubuntu 22.04 / amd64 | `3.8.2` |
| sglang | `0.5.14 / maca.ai3.8.2.122` | `2.10 / 3.12` | Ubuntu 22.04 / amd64 | `3.8.2` |
| vllm-omni-metax | `0.26.0 / maca.ai3.8.2.0` | `2.10 / 3.12` | Ubuntu 22.04 / amd64 | `3.8.2` |
| ms-swift | `4.4.3 / maca.ai3.8.0.109` | `2.10 / 3.12` | Ubuntu 22.04 / amd64 | `3.8.0` |
| verl | `0.9.0 / maca.ai3.8.0.9` | `2.10 / 3.12` | Ubuntu 24.04 / amd64 | `3.8.0` |
| slime | `0.4.0 / maca.ai3.9.0.0` | `2.10 / 3.12` | Kylin v11 / amd64 | `3.9.0` |
| megatron-lm | `0.17.0 / maca.ai3.7.0.9` | `2.8 / 3.10` | Ubuntu 22.04 / amd64 | `3.7.0` |
| deepspeed | `0.16.5 / maca.ai3.7.0.6` | `2.6 / 3.12` | Ubuntu 22.04 / amd64 | `3.7.0` |
| maca-llm-quantizer | `1.4.0 / maca.ai3.7.0.4` | `2.6 / 3.10` | Ubuntu 22.04 / amd64 | `3.7.0` |
| onnxruntime | `1.19.2 / maca.ai3.10.1.3` | `2.4 / 3.12` | Ubuntu 24.04 / amd64 | `3.100.0` |
| triton-inference-server | `2.64.0 / maca.ai3.3.0.301` | `2.8 / 3.10` | Ubuntu 22.04 / amd64 | `3.3.0.x` |

此表是少量样例，并非将这些版本拼成一个统一环境。可直接复制检索的完整名称:tag 见[镜像清单](IMAGE_CATALOG.md)。`3.100.0` 按官网原样记录，不擅自改写为 `3.10.0`。

其他 AI 家族也已入表：TensorFlow2、Paddle / Paddle-MetaX、ColossalAI、InternLM、DiffSynth-Studio、Diffusers.Training、CV-CUDA、MMCV，以及 CNN、Transformers、Diffusers 等 ModelZoo。老 `vllm` 和新 `vllm-metax` 分开记录；官网分别以 0.10.0 及以下、0.10.2 及以上区分两条分支。

## 独立安装包与 SDK 组件

除了镜像，官网的软件栈入口还列有下列资源。安装包目录与镜像目录并非一一对应；本次没看到独立镜像不等于该组件无法使用。

| 类别 | 官网列出的内容 | 本次核查深度 |
|---|---|---|
| Driver | 固件/驱动安装入口 | 确认入口，未按目标服务器 OS/内核生成驱动安装方案 |
| SDK | C/C++ 运行时、编译器、通信库、算子库、调试和示例组件 | 打开 MXC500 / Linux / x86_64 / DEB / 离线安装路径 |
| SDK-Python | MXDeepEP、MXMesh、MIXL、maca.bindings、maca.core 等 | 官网分类说明；未逐个核对组件版本 |
| MXRDMA | MetaxLink-E 的 RDMA 用户态驱动组件 | 官网分类说明；不推断这台 C500 的链路能力 |
| AI 独立包补充 | JAX、IREE、BitsAndBytes、Ray、mcoplib、transformerengine、mooncake、LMCache、DeepGEMM、liger-kernel 等 | 确认 MXC500 目录条目，未逐个展开版本 |
| 科学计算加速工具包 | mcpy、mcdf、mcfaiss、mcvs | 保留官网名称；`mcvs` 与文档中的 `mxvs` 名称不同，不合并为同一工具 |
| 性能工具包 | linux-perf-kit、mac-perf-kit、win-perf-kit | 核查 Linux 包样例，并与 mcProfiler / mcTracer 文档关联 |
| DSL | TileLang | 查看 MXC500 的 x86_64 与 aarch64 包样例 |

来源：[软件栈入口](https://developer.metax-tech.com/softnova)、[SDK 分类](https://developer.metax-tech.com/softnova/sdk?package_kind=SDK&dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)、[AI 安装包](https://developer.metax-tech.com/softnova/ai-download?package_kind=AI&dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)、[工具包](https://developer.metax-tech.com/softnova/tools?package_kind=Tools&dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)。

已展开核对的具体包：

| 包 | 页面标注 | 来源 |
|---|---|---|
| `maca-sdk-3.10.1.11-deb-x86_64.tar.xz` | 5.88 GB；2026-11-16 更新；所选 MACA `3.10.1` 依赖 Driver `≥ 3.7.0` | [SDK 下载入口](https://developer.metax-tech.com/softnova/download?dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85&package_kind=SDK&chip_name=)，需按上述路径重新选择 |
| `linux-perf-kit_3.10.1.11.tar.gz` | 787.51 MB；最低兼容 MACA `3.10.1` | [Linux Perf Kit](https://developer.metax-tech.com/softnova/tools/linux-perf-kit?dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85&package_kind=Tools&series_name=linux-perf-kit&series_label=Perf%E5%B7%A5%E5%85%B7&chip_name=MXC500) |
| `maca-tilelang-py310-3.10.1.0-x86_64.tar.xz` / `maca-tilelang-py312-3.10.1.0-x86_64.tar.xz` | Python 3.10 / 3.12；页面标注发布系列 3.10.1 | [MXC500 TileLang](https://developer.metax-tech.com/softnova/dsl/TileLang?dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85&package_kind=TileLang&chip_name=MXC500) |
| `maca-tilelang-py310-3.9.0.2-aarch64.tar.xz` / `maca-tilelang-py312-3.9.0.2-aarch64.tar.xz` | ARM 示例，和 x86 包的发布构建不同 | 同上 |

**三个版本字段要分开看：镜像推荐 Driver、SDK 最低 Driver、工具包最低 MACA。** SDK 可安装的最低条件，不等于某个新镜像的全部功能在该驱动上都已验证。此次 SDK 的“配套推荐”按钮返回 HTTP 500，未取得完整配套资源表。

## AI4S 与云平台覆盖

[AI4S 镜像目录](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=AI4S&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85) 本次观察到 11 个家族，样例均为 amd64：

| 场景 | 软件及观察版本 |
|---|---|
| 物理与数值模拟 | PhysicsNeMo `2.0.0`、Warp `1.8.1`、DeepXDE PyTorch/Paddle `v1.14.0` |
| 图学习 | PyG `v0.4.0`、DGL `2.4` |
| 天气与气候 | ai-models `0.7.4`、NeuralGCM `1.2.2` |
| 生物分子研究 | Boltz `v2.2.0`、DiffDock `v1.1.3` |
| 医学影像开发 | MONAI `1.5.2` |

这些版本用于说明软件覆盖，不是行业应用效果或准确性保证。软件栈的 [AI4Science 独立包目录](https://developer.metax-tech.com/softnova/ai4science?package_kind=AI4S&dimension=metax&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85) 本次只显示 MXC500 的 PhysicsNeMo、PyG、Warp 三项，不能把镜像目录和独立包目录当成相同集合。

[Cloud-Tools](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=Cloud-Tools&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85) 主要为 `0.16.2` 系列组件，包括 Operator、GPU 发现/资源上报、容器运行时、驱动管理、GPU/Volcano 调度、拓扑采集、DLRover 弹性任务及监控。`metax-operator:latest` 的按钮为 **helm pull**，应按 Helm Chart 管理；`driver-image:latest-*` 和 `maca:latest-*` 是可变标签，正式实验应在成功获取后补记镜像 digest。

## 与本地技术文档的交叉核对

下列为“文档描述”。页码全部是 **从 1 开始的物理 PDF 页序号**。已重新读取完整相关页面；mcTriton 版本配套、vLLM 版本映射和 DeepEP 跨页表格另外进行了渲染核对。

| 事项 | 文档说明及对本次选型的影响 | 原始来源 |
|---|---|---|
| PyTorch 交付组成 | 安装压缩包内含 PyTorch、Torchvision、Torchaudio、Apex、FlashAttention、Triton 等 wheel；查独立镜像以外的组件时，应同时查看框架安装包 | [沐曦通用GPU_mcPyTorch用户指南_CN_V16.pdf](../../沐曦通用GPU_mcPyTorch用户指南_CN_V16.pdf#page=8)，V16，PDF 7–8 页，“概述 / 快速安装” |
| mcTriton 版本对应 | 文档列出 Triton 3.0.0 对应 Torch 2.4/2.6/2.8，Triton 3.6 对应 Torch 2.10；Triton wheel 随 PyTorch 压缩包提供。它是算子编程工具，区别于 `triton-inference-server` | [沐曦通用GPU_mcTriton用户指南_CN_V08.pdf](../../沐曦通用GPU_mcTriton用户指南_CN_V08.pdf#page=5)，V08，PDF 5–6 页，“概述 / 快速安装” |
| MacaRT 与 ONNXRuntime | 本地手册说明 `onnxruntime` 容器包含 MacaRT 和工具链；因此目录中的 ONNXRuntime 是传统模型推理的重要入口 | [沐曦通用GPU_AI推理用户手册_CN_V21.pdf](../../沐曦通用GPU_AI推理用户手册_CN_V21.pdf#page=16)，V21，PDF 15–16 页，“环境依赖及 MacaRT 安装 / 使用 MacaRT 容器镜像” |
| 老手册不代表当前最新版本 | 手册表 8.1 展示的 vLLM-metaX 版本映射到 0.15.0，正文的部分能力限制针对更早版本；官网本次已观察到 0.29.0。因此不把旧表和旧限制外推到新镜像 | [沐曦通用GPU_AI推理用户手册_CN_V21.pdf](../../沐曦通用GPU_AI推理用户手册_CN_V21.pdf#page=65)，V21，PDF 65–66 页，“8 MacaRT-vLLM-metax / 表 8.1” |
| ModelZoo 的用途 | 文档说明 ModelZoo.LLM.SGLang 镜像提供源代码及评测入口；它适合定位模型配置和测试流程，不应与纯框架镜像混为一类 | [沐曦通用GPU_AI推理用户手册_CN_V21.pdf](../../沐曦通用GPU_AI推理用户手册_CN_V21.pdf#page=87)，V21，PDF 87 页，“14.4.1 源码镜像获取” |
| mcProfiler | 文档将 Windows GUI 放在 win-perf-kit 中，通过 Linux 侧实际采样使用；本地 Windows + 远程 Linux 的组合与其工作方式相符，具体权限和工具配套仍需核对 | [沐曦通用GPU_mcProfiler使用手册_CN_V06.pdf](../../沐曦通用GPU_mcProfiler使用手册_CN_V06.pdf#page=7)，V06，PDF 7 页，“2.1 安装 / 2.2.1 前置要求” |
| mcTracer | 文档说明跟随 MXMACA 软件包安装到 `/opt/maca/bin`，是 Linux 侧跟踪工具；不必仅在独立 Docker 镜像列表中找它 | [沐曦通用GPU_mcTracer使用手册_CN_V08.pdf](../../沐曦通用GPU_mcTracer使用手册_CN_V08.pdf#page=7)，V08，PDF 7 页，“2.1 安装 / 2.2 使用” |
| mxvs | 文档说明其覆盖带宽、算力等验收测试，SDK 安装过程提供该工具；可作为后续硬件基线入口。本次没有执行验收或压力测试 | [沐曦通用GPU_mxvs测试工具套件使用手册_CN_V26.pdf](../../沐曦通用GPU_mxvs测试工具套件使用手册_CN_V26.pdf#page=11)，V26，PDF 11–12 页，“概述 / 工具部署” |
| DeepEP / mxshmem | 针对 DeepEP Low Latency 多机通信场景，内存注册方式随 SDK Release、Linux Kernel、部分版本下的 MOFED 改变；这不是可无条件套用到所有单机任务的环境变量 | [沐曦通用GPU_DeepEP多机通信内存注册环境变量配置说明_CN_V01.pdf](../../沐曦通用GPU_DeepEP多机通信内存注册环境变量配置说明_CN_V01.pdf#page=5)，V01，PDF 5–7 页，“适用场景 / 配置说明 / 客户使用建议” |

DeepEP 文档中，SDK Release `3.8.3–3.10.0` 且内核 `< 5.16` 时还需检查 MOFED；SDK Release `≥ 3.10.1` 改为根据内核能力选择方式。此前主机内核为 5.15，因此将来开展相关多机实验时需要按实际 SDK/MOFED 组合核查，而不能从镜像名称直接推断配置。[同一 DeepEP 文档，V01，PDF 6–7 页，表 2.2–2.3](../../沐曦通用GPU_DeepEP多机通信内存注册环境变量配置说明_CN_V01.pdf#page=6)。

## 获取地址与可复现记录

本次点击镜像目录的“docker pull 命令复制”跳转到登录页，故镜像表只保存官网显示的名称:tag 和稳定页面入口，不猜仓库前缀。SDK 离线页面提供的 wget 地址带有效期签名，提示 8 小时有效；签名地址不作为长期索引保存。

以下为官方 SGLang v0.5.14 快速开始页面公开提供的 **Ubuntu / amd64 样例**，仅供查阅，未实际拉取：

```bash
docker pull cr.metax-tech.com/public-ai-release/maca/sglang:0.5.14-maca.ai3.8.2.122-torch2.10-py310-ubuntu22.04-amd64
```

来源：[SGLang MetaX v0.5.14，快速开始，“拉取镜像”](https://developer.metax-tech.com/llm-inference/sgldocs/v0.5.14/getting_started/quick_start.html#_2)。注意该公开样例为 Python 3.10，目录中另外观察到 Python 3.12 的同系列镜像。不能以一个公开地址推导所有家族的 registry 路径。

后续选定环境时，建议为每项记录：完整 registry/name:tag、实际 digest、Driver/SDK/框架/Python 版本、容器 OS/架构、获取日期、模型和精度配置、测试结果。保持“官网列出 / 文档描述 / 已成功拉取 / 本机验证通过”四个状态分开。

## 维护方式

这是一次有日期的离线盘点，不会自动跟随网站更新。`build_catalog.py` 根据本次人工转录的家族观察记录重新生成两份清单和 JSON，不访问网站、不下载软件。更新时应重新查看官方筛选结果和配套文档，保存新的日期目录，并重新核对推荐 Driver；不要仅替换镜像 tag 中的版本数字。

原始 PDF、既有逐页索引及服务器配置均保持原样。所有环境建议都需要在确认实际服务器软件栈后落实。
