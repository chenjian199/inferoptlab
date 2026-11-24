# MXC500 镜像与 Chart 家族清单

采集日期：2026-11-21（Asia/Shanghai）。[结论与文档交叉核对](README.md) · [结构化数据](images.json)

共 62 个家族，其中 61 个容器镜像家族、1 个 Helm Chart 家族。以下为本次浏览所见的近期样例，不表示所有历史版本，也不表示在目标服务器实测通过。

Driver 列为同一行样例卡片的“推荐安装”值，不是最低兼容值。未标注保持未知。名称:tag 未包含仓库前缀，不可直接当作完整 docker pull 地址。

## MXMACA（2 个家族）

来源：[MXC500 / MXMACA](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=MXMACA&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)；所有条目均为官网列出、未实测。

| 家族 / 用途 | 本次观察的近期样例名称:tag | 推荐 Driver | 页面更新时间 |
|---|---|---|---|
| **maca**<br>基础 SDK 开发与运行环境 | `maca:latest-ubuntu24.04-amd64` | 3.100.0 | 2026-11-16 18:45:26 |
| **maca-native**<br>保留的 maca-native 基础镜像分支；与 maca 的具体差异待查配套说明 | `maca-native:3.5.3.6-centos9-amd64` | 3.5.3.x | 2026-03-04 15:26:19 |

## AI（29 个家族）

来源：[MXC500 / AI](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=AI&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)；所有条目均为官网列出、未实测。

| 家族 / 用途 | 本次观察的近期样例名称:tag | 推荐 Driver | 页面更新时间 |
|---|---|---|---|
| **mmcv**<br>OpenMMLab 视觉基础库 | `mmcv:2.2.0-maca.ai3.10.1.2-torch2.4-py310-kylinv11-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **diffusers.training**<br>扩散模型训练与 LoRA 微调 | `diffusers.training:0.28.0-maca.ai3.10.1.2-torch2.4-py310-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **onnxruntime**<br>传统 CNN / Transformer 的 ONNX 推理环境 | `onnxruntime:1.19.2-maca.ai3.10.1.3-torch2.4-py312-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **modelzoo.llm.transformers**<br>Transformers 推理评测样例 | `modelzoo.llm.transformers:1.0.1-maca.ai3.10.1.2-torch2.4-py310-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **tensorflow2**<br>TensorFlow 训练与 XLA 环境 | `tensorflow2:2.13.1-maca.ai3.10.1.2-py310-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **paddle-metax**<br>Paddle 新分支及 MetaX 后端 | `paddle-metax:3.5.0-maca.ai3.10.1.2-py312-kylinv11-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **cv-cuda**<br>视觉预处理与图像/视频流水线 | `cv-cuda:0.16.0-maca.ai3.10.1.2-torch2.4-py310-kylinv11-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **modelzoo.cnn.training**<br>经典视觉模型训练与评测 | `modelzoo.cnn.training:1.0.0-maca.ai3.10.1.2-torch2.4-py310-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **modelzoo.llm.diffusers**<br>图像生成模型推理评测 | `modelzoo.llm.diffusers:1.0.3-maca.ai3.10.1.1-torch2.8-py310-kylinv11-amd64` | 3.100.0 | 2026-11-18 16:47:56 |
| **slime**<br>面向 SGLang 的分布式后训练 | `slime:0.4.0-maca.ai3.9.0.0-torch2.10-py312-kylinv11-amd64` | 3.9.0 | 2026-11-18 15:31:21 |
| **maca-pytorch**<br>PyTorch 通用计算与训练环境 | `maca-pytorch:3.10.1.2-torch2.10-py312-ubuntu24.04-amd64` | 3.100.0 | 2026-11-16 18:45:26 |
| **vllm-metax**<br>vLLM 插件式 MetaX 推理服务 | `vllm-metax:0.29.0-maca.ai3.9.0.9-torch2.10-py310-ubuntu24.04-amd64` | 3.9.0 | 2026-11-05 17:58:32 |
| **modelzoo.llm.vllm**<br>vLLM 模型配置、推理与性能/精度评测 | `modelzoo.llm.vllm:1.0.3-maca.ai3.9.0.9-torch2.10-py312-ubuntu24.04-amd64` | 3.9.0 | 2026-11-05 17:58:32 |
| **verl**<br>分布式强化学习后训练 | `verl:0.9.0-maca.ai3.8.0.9-torch2.10-py312-ubuntu24.04-amd64` | 3.8.0 | 2026-10-12 18:30:53 |
| **diffsynth-studio**<br>多模态与视频生成模型训练 | `diffsynth-studio:2.0.12-maca.ai3.9.0.3-torch2.8-py312-ubuntu24.04-amd64` | 3.9.0 | 2026-10-09 17:58:42 |
| **ms-swift**<br>SFT、LoRA 与强化学习后训练 | `ms-swift:4.4.3-maca.ai3.8.0.109-torch2.10-py312-kylinv11-amd64` | 3.8.0 | 2026-09-29 20:10:49 |
| **modelzoo.cnn.inference**<br>ONNX 视觉/NLP 模型推理与精度评测 | `modelzoo.cnn.inference:1.0.0-maca.ai3.9.0.12-torch2.4-py310-kylinv11-amd64` | 3.9.0 | 2026-09-28 16:09:37 |
| **paddle**<br>Paddle 2.6 及更早的保留分支 | `paddle:2.6.0-maca.ai3.9.0.10-py312-ubuntu24.04-amd64` | 3.9.0 | 2026-09-28 15:46:08 |
| **sglang**<br>LLM 推理服务 | `sglang:0.5.14-maca.ai3.8.2.122-torch2.10-py310-kylinv11-amd64` | 3.8.2 | 2026-09-23 18:02:20 |
| **modelzoo.llm.sglang**<br>SGLang 模型配置与评测 | `modelzoo.llm.sglang:1.0.3-maca.ai3.8.2.125-torch2.10-py312-kylinv11-amd64` | 3.8.2 | 2026-09-23 18:02:20 |
| **vllm-omni-metax**<br>多模态、多阶段模型推理 | `vllm-omni-metax:0.26.0-maca.ai3.8.2.0-torch2.10-py312-kylinv11-amd64` | 3.8.2 | 2026-09-18 18:04:12 |
| **megatron-lm**<br>分布式预训练 | `megatron-lm:0.17.0-maca.ai3.7.0.9-torch2.8-py310-kylinv11-amd64` | 3.7.0 | 2026-08-07 19:06:10 |
| **maca-llm-quantizer**<br>大模型量化及推理部署前处理 | `maca-llm-quantizer:1.4.0-maca.ai3.7.0.4-torch2.6-py310-ubuntu22.04-amd64` | 3.7.0 | 2026-07-13 16:54:16 |
| **deepspeed**<br>分布式训练与微调 | `deepspeed:0.16.5-maca.ai3.7.0.6-torch2.6-py312-ubuntu22.04-amd64` | 3.7.0 | 2026-05-09 18:31:10 |
| **colossalai**<br>大模型分布式训练 | `colossalai:0.5.0-maca.ai3.5.3.15-torch2.4-py310-kylinv11-amd64` | 3.5.3.x | 2026-03-04 16:28:25 |
| **internlm**<br>InternLM 系列训练环境 | `internlm:0.2.1-maca.ai3.5.3.15-torch2.4-py312-kylinv10-arm64` | 3.5.3.x | 2026-03-04 16:28:25 |
| **xtuner**<br>全参及 LoRA 微调 | `xtuner:0.2.0-maca.ai3.5.3.15-torch2.6-py312-ubuntu22.04-amd64` | 3.5.3.x | 2026-03-04 16:28:25 |
| **triton-inference-server**<br>多模型推理服务管理；区别于 mcTriton 算子编程 | `triton-inference-server:2.64.0-maca.ai3.3.0.301-torch2.8-py310-ubuntu22.04-amd64` | 3.3.0.x | 2026-02-04 18:21:27 |
| **vllm**<br>vLLM 0.10.0 及更早的保留分支 | `vllm:maca.ai3.1.0.7-torch2.6-py310-ubuntu22.04-amd64` | 3.1.0.x | 2025-09-29 19:22:21 |

## AI4S（11 个家族）

来源：[MXC500 / AI4S](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=AI4S&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)；所有条目均为官网列出、未实测。

| 家族 / 用途 | 本次观察的近期样例名称:tag | 推荐 Driver | 页面更新时间 |
|---|---|---|---|
| **monai-maca**<br>医学影像模型开发 | `monai-maca:1.5.2-3.10.1.2-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:11:48 |
| **neuralgcm-maca**<br>神经网络与物理结合的气候模拟 | `neuralgcm-maca:1.2.2-3.10.1.2-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:11:48 |
| **physicsnemo-maca**<br>物理 AI 与科学计算 | `physicsnemo-maca:2.0.0-3.10.1.2-torch2.8-py312-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:11:48 |
| **aimodels-maca**<br>AI 天气模型集合 | `aimodels-maca:0.7.4-3.10.1.2-torch2.8-py312-ubuntu24.04-amd64` | 3.100.0 | 2026-11-18 16:11:48 |
| **pyg_lib-maca**<br>图神经网络基础组件 | `pyg_lib-maca:v0.4.0-3.10.1.2-torch2.4-py310-ubuntu22.04-amd64` | 3.100.0 | 2026-11-18 16:11:48 |
| **boltz-maca**<br>生物分子建模与药物研究 | `boltz-maca:v2.2.0-3.9.0.12-torch2.8-py312-ubuntu24.04-amd64` | 3.9.0 | 2026-09-29 16:32:59 |
| **dgl-maca**<br>DGL 图神经网络 | `dgl-maca:2.4-3.9.0.12-ubuntu22.04-amd64` | 3.9.0 | 2026-09-29 16:32:59 |
| **warp-maca**<br>Python 数值模拟与 JIT | `warp-maca:1.8.1-3.7.0.6-ubuntu22.04-amd64` | 3.7.0 | 2026-05-09 18:01:35 |
| **deepxde-pytorch-maca**<br>基于 PyTorch 的物理信息网络/微分方程求解 | `deepxde-pytorch-maca:v1.14.0-3.7.0.6-ubuntu24.04-amd64` | 3.7.0 | 2026-05-09 18:01:35 |
| **deepxde-paddle-maca**<br>基于 Paddle 的物理信息网络/微分方程求解 | `deepxde-paddle-maca:v1.14.0-3.7.0.6-ubuntu22.04-amd64` | 3.7.0 | 2026-05-09 18:01:35 |
| **diffdock-maca**<br>分子对接模型 | `diffdock-maca:v1.1.3-3.7.0.6-torch2.4-py310-ubuntu22.04-amd64` | 3.7.0 | 2026-05-09 18:01:35 |

## Cloud-Tools（20 个家族）

来源：[MXC500 / Cloud-Tools](https://developer.metax-tech.com/softnova/docker?chip_name=MXC500&package_kind=Cloud-Tools&dimension=docker&deliver_type=%E5%88%86%E5%B1%82%E5%8C%85)；所有条目均为官网列出、未实测。

| 家族 / 用途 | 本次观察的近期样例名称:tag | 推荐 Driver | 页面更新时间 |
|---|---|---|---|
| **operator-bundle**<br>Operator OLM Bundle | `operator-bundle:0.16.2` | 未标注 | 2026-11-06 17:25:18 |
| **operator-catalog**<br>Operator OLM Catalog | `operator-catalog:0.16.2` | 未标注 | 2026-11-06 17:25:18 |
| **operator-controller**<br>GPU Operator 控制器 | `operator-controller:0.16.2` | 未标注 | 2026-11-02 14:55:43 |
| **gpu-scheduler**<br>GPU/sGPU 拓扑感知调度 | `gpu-scheduler:0.16.2` | 未标注 | 2026-11-02 14:55:43 |
| **gpu-device**<br>GPU 设备资源上报 | `gpu-device:0.16.2-amd64` | 未标注 | 2026-11-02 14:55:43 |
| **vc-webhook-manager**<br>Volcano Webhook | `vc-webhook-manager:0.16.2-vc.v1.9.0-arm64` | 未标注 | 2026-11-02 14:55:43 |
| **container-runtime**<br>MetaX 容器运行时 | `container-runtime:0.16.2-arm64` | 未标注 | 2026-11-02 14:55:43 |
| **dlrover-master**<br>DLRover 任务主控 | `dlrover-master:0.16.2` | 未标注 | 2026-11-02 14:55:43 |
| **vc-scheduler**<br>Volcano 调度 | `vc-scheduler:0.16.2-vc.v1.9.0` | 未标注 | 2026-11-02 14:55:43 |
| **gpu-aware**<br>GPU 拓扑感知 | `gpu-aware:0.16.2-amd64` | 未标注 | 2026-11-02 14:55:43 |
| **elasticjob-controller**<br>DLRover 弹性任务控制 | `elasticjob-controller:0.16.2-arm64` | 未标注 | 2026-11-02 14:55:43 |
| **driver-manager**<br>节点 Driver/SDK 管理 | `driver-manager:0.16.2-arm64` | 未标注 | 2026-11-02 14:55:43 |
| **vc-controller-manager**<br>Volcano 控制器 | `vc-controller-manager:0.16.2-vc.v1.9.0` | 未标注 | 2026-11-02 14:55:43 |
| **topo-master**<br>集群拓扑管理 | `topo-master:0.16.2` | 未标注 | 2026-11-02 14:55:43 |
| **gpu-label**<br>节点 GPU 信息发现 | `gpu-label:0.16.2-amd64` | 未标注 | 2026-11-02 14:55:43 |
| **mx-exporter**<br>GPU 监控指标导出 | `mx-exporter:0.16.2-amd64` | 未标注 | 2026-11-02 14:55:43 |
| **topo-worker**<br>节点拓扑采集 | `topo-worker:0.16.2-arm64` | 未标注 | 2026-11-02 14:55:43 |
| **controller-exporter**<br>Operator 管理驱动时的配套组件 | `controller-exporter:0.16.2-amd64` | 未标注 | 2026-11-02 14:55:43 |
| **metax-operator**<br>GPU Operator Helm Chart（不是 Docker 镜像） | `metax-operator:latest` | 3.9.0 | 2026-11-02 14:55:43 |
| **driver-image**<br>内核驱动负载镜像 | `driver-image:latest-arm64` | 未标注 | 2026-10-20 17:45:54 |

## Ubuntu 22.04 / amd64 备选样例

这部分便于按常见容器系统筛选，不代表服务器宿主 OS 已核实。样例可能比上表旧；必须重新查看它自身的推荐 Driver 和配套要求。未列出不代表不存在。

| 家族 | 观察到的备选名称:tag |
|---|---|
| maca | `maca:latest-ubuntu22.04-amd64` |
| maca-native | `maca-native:3.5.3.6-ubuntu22.04-amd64` |
| mmcv | `mmcv:2.2.0-maca.ai3.8.0.10-torch2.4-py38-ubuntu22.04-amd64` |
| diffusers.training | `diffusers.training:0.28.0-maca.ai3.8.0.10-torch2.4-py312-ubuntu22.04-amd64` |
| onnxruntime | `onnxruntime:1.12.0-maca.ai3.8.0.10-torch2.4-py38-ubuntu22.04-amd64` |
| modelzoo.llm.transformers | `modelzoo.llm.transformers:1.0.1-maca.ai3.8.0.10-torch2.4-py312-ubuntu22.04-amd64` |
| tensorflow2 | `tensorflow2:2.13.1-maca.ai3.8.0.10-py310-ubuntu22.04-amd64` |
| paddle-metax | `paddle-metax:3.5.0-maca.ai3.8.0.10-py310-ubuntu22.04-amd64` |
| cv-cuda | `cv-cuda:0.16.0-maca.ai3.8.0.10-torch2.4-py312-ubuntu22.04-amd64` |
| modelzoo.cnn.training | `modelzoo.cnn.training:1.0.0-maca.ai3.8.0.10-torch2.4-py310-ubuntu22.04-amd64` |
| modelzoo.llm.diffusers | `modelzoo.llm.diffusers:1.0.0-maca.ai3.7.0.8-torch2.4-py38-ubuntu22.04-amd64` |
| maca-pytorch | `maca-pytorch:3.10.1.2-torch2.4-py310-ubuntu22.04-amd64` |
| vllm-metax | `vllm-metax:0.28.0-maca.ai3.8.2.401-torch2.10-py312-ubuntu22.04-amd64` |
| modelzoo.llm.vllm | `modelzoo.llm.vllm:1.0.3-maca.ai3.8.2.401-torch2.10-py312-ubuntu22.04-amd64` |
| verl | `verl:0.8.0-maca.ai3.7.1.9-torch2.8-py312-ubuntu22.04-amd64` |
| ms-swift | `ms-swift:4.4.3-maca.ai3.8.0.109-torch2.10-py312-ubuntu22.04-amd64` |
| modelzoo.cnn.inference | `modelzoo.cnn.inference:1.0.0-maca.ai3.8.0.10-torch2.4-py310-ubuntu22.04-amd64` |
| paddle | `paddle:2.6.0-maca.ai3.8.0.10-py312-ubuntu22.04-amd64` |
| sglang | `sglang:0.5.14-maca.ai3.8.2.122-torch2.10-py312-ubuntu22.04-amd64` |
| modelzoo.llm.sglang | `modelzoo.llm.sglang:1.0.3-maca.ai3.8.2.125-torch2.10-py312-ubuntu22.04-amd64` |
| vllm-omni-metax | `vllm-omni-metax:0.26.0-maca.ai3.8.2.0-torch2.10-py312-ubuntu22.04-amd64` |
| megatron-lm | `megatron-lm:0.17.0-maca.ai3.7.0.9-torch2.8-py310-ubuntu22.04-amd64` |
| maca-llm-quantizer | `maca-llm-quantizer:1.4.0-maca.ai3.7.0.4-torch2.6-py310-ubuntu22.04-amd64` |
| deepspeed | `deepspeed:0.16.5-maca.ai3.7.0.6-torch2.6-py312-ubuntu22.04-amd64` |
| colossalai | `colossalai:0.5.0-maca.ai3.5.3.15-torch2.4-py310-ubuntu22.04-amd64` |
| internlm | `internlm:0.2.1-maca.ai3.5.3.15-torch2.4-py310-ubuntu22.04-amd64` |
| xtuner | `xtuner:0.2.0-maca.ai3.5.3.15-torch2.6-py312-ubuntu22.04-amd64` |
| triton-inference-server | `triton-inference-server:2.64.0-maca.ai3.3.0.301-torch2.8-py310-ubuntu22.04-amd64` |
| vllm | `vllm:maca.ai3.1.0.7-torch2.6-py310-ubuntu22.04-amd64` |
| neuralgcm-maca | `neuralgcm-maca:1.2.2-3.5.3.6-ubuntu22.04-amd64` |
| physicsnemo-maca | `physicsnemo-maca:1.0.1-3.7.0.6-ubuntu22.04-amd64` |
| aimodels-maca | `aimodels-maca:0.7.4-3.5.3.6-ubuntu22.04-amd64` |
| pyg_lib-maca | `pyg_lib-maca:v0.4.0-3.10.1.2-torch2.4-py310-ubuntu22.04-amd64` |
| boltz-maca | `boltz-maca:v2.2.0-3.5.3.6-ubuntu22.04-amd64` |
| dgl-maca | `dgl-maca:2.4-3.9.0.12-ubuntu22.04-amd64` |
| warp-maca | `warp-maca:1.8.1-3.7.0.6-ubuntu22.04-amd64` |
| deepxde-paddle-maca | `deepxde-paddle-maca:v1.14.0-3.7.0.6-ubuntu22.04-amd64` |
| diffdock-maca | `diffdock-maca:v1.1.3-3.7.0.6-torch2.4-py310-ubuntu22.04-amd64` |
