# C500 组件关联索引

由 tools/build_knowledge.py 生成；维护 tools/components.json，勿手改本文件。

[使用说明](README.md) · [PDF 清单](CATALOG.md) · [PDF 主题](TOPICS.md) · [实践知识](practice/README.md)

关联用于定位资料，不构成版本兼容、配套安装或服务器验证结论。直接文档为对应组件资料；背景文档仅供查阅。
相同名称可自动关联；近似名称需显式配置。无 PDF 关联表示尚未建立映射，不代表不支持。
版本、tag、推荐驱动保留在日期快照中；最低版本、推荐版本和实测结果不得互相替代。

组件导航条目：161（含文档组件及发行分支，不是独立软件产品数）。

## 日期快照

- [ecosystem / 2026-11-21](ecosystem/2026-11-21/README.md) · [覆盖范围](ecosystem/2026-11-21/coverage.json)
- [github / 2026-11-21](repositories/2026-11-21/README.md) · [覆盖范围](repositories/2026-11-21/coverage.json)

最新指本地采集日期最新，不能代表官网当前最新版本。

## 按主题定位

<a id="topic-environment"></a>
### 环境检查与安装

[设备卡序配置](#device-order) · [Driver](#driver) · [MXMACA / SDK](#maca) · [maca-native](#maca-native) · [mcPyTorch / maca-pytorch](#mcpytorch) · [Mihomo 下载代理](#mihomo) · [MIM 镜像服务](#mim) · [MXRDMA](#mxrdma) · [mxvs](#mxvs) · [运行时 API](#runtime-api) · [SDK-Python](#sdk-python)

<a id="topic-inference"></a>
### 模型运行与推理

[AI 推理综合手册](#ai-inference) · [AIModels PD 分离方案](#aimodels-pd) · [BitsAndBytes](#bitsandbytes) · [IREE](#iree) · [LMCache](#lmcache) · [maca-llm-quantizer](#maca-llm-quantizer) · [mcPyTorch / maca-pytorch](#mcpytorch) · [modelzoo.cnn.inference](#modelzoo.cnn.inference) · [modelzoo.llm.diffusers](#modelzoo.llm.diffusers) · [modelzoo.llm.sglang](#modelzoo.llm.sglang) · [modelzoo.llm.transformers](#modelzoo.llm.transformers) · [modelzoo.llm.vllm](#modelzoo.llm.vllm) · [mooncake](#mooncake) · [ONNX Runtime](#onnxruntime) · [Autonomous_Driving_Simulation](#repo-autonomous_driving_simulation) · [DocFlowAI](#repo-docflowai) · [Embodied_AI_Simulation](#repo-embodied_ai_simulation) · [modelzoo](#repo-modelzoo) · [ppl.llm.serving](#repo-ppl.llm.serving) · [VirtualHuman](#repo-virtualhuman) · [SGLang](#sglang) · [Triton Inference Server](#triton-inference-server) · [vLLM 旧分支](#vllm) · [vLLM-MetaX](#vllm-metax) · [vllm-omni-metax](#vllm-omni-metax)

<a id="topic-profiling"></a>
### 性能分析与基准测试

[GPU 基准测试集合](#gpu-benchmark) · [linux-perf-kit](#linux-perf-kit) · [mac-perf-kit](#mac-perf-kit) · [MCCL 通信测试](#mccl-tests) · [mcProfiler](#mcprofiler) · [mcTracer](#mctracer) · [mxvs](#mxvs) · [C500 算子优化实践](#op-optimization) · [QuickGuide](#repo-quickguide) · [win-perf-kit](#win-perf-kit)

<a id="topic-communication"></a>
### 多卡与多机通信

[AIModels PD 分离方案](#aimodels-pd) · [DeepEP / MXDeepEP](#deepep) · [设备卡序配置](#device-order) · [MCCL](#mccl) · [MCCL 通信测试](#mccl-tests) · [mooncake](#mooncake) · [mxvs](#mxvs) · [3FS](#repo-3fs) · [DeepEP](#repo-deepep) · [fio](#repo-fio) · [mcfile-python](#repo-mcfile-python) · [mxFIO](#repo-mxfio) · [运行时 API](#runtime-api)

<a id="topic-kernels"></a>
### 算子与 GPU 编程

[cv-cuda](#cv-cuda) · [DeepGEMM](#deepgemm) · [liger-kernel](#liger-kernel) · [MXMACA C++ 编程](#maca-cpp) · [MACA 编程示例](#maca-samples) · [mcBLAS](#mcblas) · [mcoplib](#mcoplib) · [mcTriton](#mctriton) · [mmcv](#mmcv) · [mxcc](#mxcc) · [C500 算子优化实践](#op-optimization) · [flashattn](#repo-flashattn) · [FlashMLA](#repo-flashmla) · [McFlashInfer](#repo-mcflashinfer) · [mcFlashMLA](#repo-mcflashmla) · [mcSolver](#repo-mcsolver) · [mcSparse](#repo-mcsparse) · [mcTlass](#repo-mctlass) · [mxCuco](#repo-mxcuco) · [mxRmmx](#repo-mxrmmx) · [QuickGuide](#repo-quickguide) · [TileKernels-Metax](#repo-tilekernels-metax) · [TileOPs-Metax](#repo-tileops-metax) · [运行时 API](#runtime-api) · [TileLang](#tilelang) · [transformerengine](#transformerengine)

<a id="topic-development"></a>
### 编译与开发工具

[MXMACA Clangd](#clangd) · [MXMACA / SDK](#maca) · [MXMACA C++ 编程](#maca-cpp) · [MACA 编程示例](#maca-samples) · [mcEigen](#mceigen) · [mcTriton](#mctriton) · [mxcc](#mxcc) · [go-mxsml](#repo-go-mxsml) · [goutils](#repo-goutils) · [mcApex](#repo-mcapex) · [mcTVM](#repo-mctvm) · [mcXformer](#repo-mcxformer) · [MetaX-MACA.github.io](#repo-metax-maca.github.io) · [mxJitify](#repo-mxjitify) · [mxNumbax](#repo-mxnumbax) · [pymxsml](#repo-pymxsml) · [QuickGuide](#repo-quickguide) · [simple-jenkins-githubaction](#repo-simple-jenkins-githubaction) · [TileLang](#tilelang)

<a id="topic-libraries"></a>
### 数学库与接口参考

[mcBLAS](#mcblas) · [mcdf](#mcdf) · [mcEigen](#mceigen) · [mcfaiss](#mcfaiss) · [mcpy](#mcpy) · [mcvs](#mcvs) · [flashattn](#repo-flashattn) · [FlashMLA](#repo-flashmla) · [McFlashInfer](#repo-mcflashinfer) · [mcFlashMLA](#repo-mcflashmla) · [mcSolver](#repo-mcsolver) · [mcSparse](#repo-mcsparse) · [mcTlass](#repo-mctlass) · [mxCuco](#repo-mxcuco) · [mxRmmx](#repo-mxrmmx) · [TileKernels-Metax](#repo-tilekernels-metax) · [TileOPs-Metax](#repo-tileops-metax)

<a id="topic-training"></a>
### 训练、微调与后训练

[BitsAndBytes](#bitsandbytes) · [colossalai](#colossalai) · [deepspeed](#deepspeed) · [diffsynth-studio](#diffsynth-studio) · [diffusers.training](#diffusers.training) · [internlm](#internlm) · [JAX](#jax) · [mcPyTorch / maca-pytorch](#mcpytorch) · [Megatron LM](#megatron-lm) · [modelzoo.cnn.training](#modelzoo.cnn.training) · [ms-swift](#ms-swift) · [Paddle 旧分支](#paddle) · [Paddle-MetaX](#paddle-metax) · [Ray【2.46.0版本及以下】](#ray-2.46.0) · [Ray【2.48.0版本及以上】](#ray-2.48.0) · [mcApex](#repo-mcapex) · [mcTVM](#repo-mctvm) · [mcXformer](#repo-mcxformer) · [modelzoo](#repo-modelzoo) · [mxJitify](#repo-mxjitify) · [mxNumbax](#repo-mxnumbax) · [ppl.llm.serving](#repo-ppl.llm.serving) · [slime](#slime) · [tensorflow2](#tensorflow2) · [transformerengine](#transformerengine) · [verl](#verl) · [verl MetaX 硬件插件](#verl-metax) · [xtuner](#xtuner)

<a id="topic-ai4s"></a>
### 科学计算与 AI4S

[aimodels-maca](#aimodels-maca) · [boltz-maca](#boltz-maca) · [deepxde-paddle-maca](#deepxde-paddle-maca) · [deepxde-pytorch-maca](#deepxde-pytorch-maca) · [dgl-maca](#dgl-maca) · [diffdock-maca](#diffdock-maca) · [monai-maca](#monai-maca) · [neuralgcm-maca](#neuralgcm-maca) · [PhysicsNeMo](#physicsnemo) · [PyG](#pyg) · [AI4S-Framework](#repo-ai4s-framework) · [GeoScience](#repo-geoscience) · [LifeScience](#repo-lifescience) · [Materials](#repo-materials) · [MedicalImage](#repo-medicalimage) · [metax-ai4s](#repo-metax-ai4s) · [metax-lifescience-toolkit](#repo-metax-lifescience-toolkit) · [Physics](#repo-physics) · [WeatherForecast](#repo-weatherforecast) · [Warp](#warp)

<a id="topic-cloud"></a>
### 容器、集群与运维

[container-runtime](#container-runtime) · [controller-exporter](#controller-exporter) · [device-plugin-source](#device-plugin-source) · [dlrover](#dlrover) · [dlrover-master](#dlrover-master) · [driver-image](#driver-image) · [driver-manager](#driver-manager) · [elasticjob-controller](#elasticjob-controller) · [gpu-aware](#gpu-aware) · [gpu-device](#gpu-device) · [gpu-label](#gpu-label) · [gpu-scheduler](#gpu-scheduler) · [kubectl-plugins](#kubectl-plugins) · [metax-arena](#metax-arena) · [metax-docker](#metax-docker) · [metax-gpu-k8s](#metax-gpu-k8s) · [metax-gpu-k8s-package-base](#metax-gpu-k8s-package-base) · [metax-gpu-openshift](#metax-gpu-openshift) · [metax-gpu-scheduler](#metax-gpu-scheduler) · [metax-k8s-driver-image](#metax-k8s-driver-image) · [metax-operator](#metax-operator) · [mx-exporter](#mx-exporter) · [mxdcm](#mxdcm) · [mxkind](#mxkind) · [operator-bundle](#operator-bundle) · [operator-catalog](#operator-catalog) · [operator-controller](#operator-controller) · [Ray【2.46.0版本及以下】](#ray-2.46.0) · [Ray【2.48.0版本及以上】](#ray-2.48.0) · [go-mxsml](#repo-go-mxsml) · [goutils](#repo-goutils) · [MetaX-MACA.github.io](#repo-metax-maca.github.io) · [pymxsml](#repo-pymxsml) · [simple-jenkins-githubaction](#repo-simple-jenkins-githubaction) · [topo-master](#topo-master) · [topo-worker](#topo-worker) · [vc-controller-manager](#vc-controller-manager) · [vc-scheduler](#vc-scheduler) · [vc-webhook-manager](#vc-webhook-manager) · [volcano](#volcano)

<a id="ai-inference"></a>
## AI 推理综合手册 (`ai-inference`)

主题：inference

检索别名：AI推理、MacaRT

- 直接文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）

<a id="aimodels-maca"></a>
## aimodels-maca (`aimodels-maca`)

主题：ai4s

检索别名：aimodels-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[aimodels-maca](ecosystem/2026-11-21/images.json) (images, `/families/34`)

<a id="aimodels-pd"></a>
## AIModels PD 分离方案 (`aimodels-pd`)

主题：inference, communication

检索别名：AIModels、PD分离

- 背景文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[AIModels](repositories/2026-11-21/repositories.json) (repository, `/repositories/2`)
- 相关入口（不自动扩展检索范围）：[sglang](#sglang)、[mooncake](#mooncake)
- 说明：此 GitHub 仓库是 PD 分离方案，不与 AI4S aimodels-maca 镜像混同。

<a id="bitsandbytes"></a>
## BitsAndBytes (`bitsandbytes`)

主题：training, inference

检索别名：BitsAndBytes

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[BitsAndBytes](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/25`)

<a id="boltz-maca"></a>
## boltz-maca (`boltz-maca`)

主题：ai4s

检索别名：boltz-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[boltz-maca](ecosystem/2026-11-21/images.json) (images, `/families/36`)

<a id="clangd"></a>
## MXMACA Clangd (`clangd`)

主题：development

检索别名：clangd

- 直接文档：[沐曦通用GPU_MXMACA Clangd用户手册 · V03](generated/documents/clangd-v03.md)（章节与物理页定位见链接）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="colossalai"></a>
## colossalai (`colossalai`)

主题：training

检索别名：colossalai

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[colossalai](ecosystem/2026-11-21/images.json) (images, `/families/26`)；[ColossalAI](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/4`)

<a id="container-runtime"></a>
## container-runtime (`container-runtime`)

主题：cloud

检索别名：container-runtime

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[container-runtime](ecosystem/2026-11-21/images.json) (images, `/families/48`)

<a id="controller-exporter"></a>
## controller-exporter (`controller-exporter`)

主题：cloud

检索别名：controller-exporter

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[controller-exporter](ecosystem/2026-11-21/images.json) (images, `/families/59`)

<a id="cv-cuda"></a>
## cv-cuda (`cv-cuda`)

主题：kernels

检索别名：cv-cuda

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[cv-cuda](ecosystem/2026-11-21/images.json) (images, `/families/8`)；[CV-CUDA](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/26`)

<a id="deepep"></a>
## DeepEP / MXDeepEP (`deepep`)

主题：communication

检索别名：DeepEP、MXDeepEP

- 直接文档：[沐曦通用GPU_DeepEP多机通信内存注册环境变量配置说明 · V01](generated/documents/deepep-v01.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[MXDeepEP](repositories/2026-11-21/repositories.json) (repository, `/repositories/44`)
- 相关入口（不自动扩展检索范围）：[sdk-python](#sdk-python)
- 说明：关联多机通信配置资料；不推定其他 SDK 或单机环境适用。

<a id="deepgemm"></a>
## DeepGEMM (`deepgemm`)

主题：kernels

检索别名：DeepGEMM

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[DeepGEMM](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/34`)

<a id="deepspeed"></a>
## deepspeed (`deepspeed`)

主题：training

检索别名：deepspeed

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[deepspeed](ecosystem/2026-11-21/images.json) (images, `/families/25`)；[DeepSpeed](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/5`)

<a id="deepxde-paddle-maca"></a>
## deepxde-paddle-maca (`deepxde-paddle-maca`)

主题：ai4s

检索别名：deepxde-paddle-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[deepxde-paddle-maca](ecosystem/2026-11-21/images.json) (images, `/families/40`)

<a id="deepxde-pytorch-maca"></a>
## deepxde-pytorch-maca (`deepxde-pytorch-maca`)

主题：ai4s

检索别名：deepxde-pytorch-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[deepxde-pytorch-maca](ecosystem/2026-11-21/images.json) (images, `/families/39`)

<a id="device-order"></a>
## 设备卡序配置 (`device-order`)

主题：environment, communication

检索别名：MACA_VISIBLE_DEVICES

- 直接文档：[沐曦通用GPU_MACA_VISIBLE_DEVICES配置工具介绍 · V01](generated/documents/device-order-v01.md)（章节与物理页定位见链接）

<a id="device-plugin-source"></a>
## device-plugin-source (`device-plugin-source`)

主题：cloud

检索别名：device-plugin-source

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[device-plugin-source](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/50`)

<a id="dgl-maca"></a>
## dgl-maca (`dgl-maca`)

主题：ai4s

检索别名：dgl-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[dgl-maca](ecosystem/2026-11-21/images.json) (images, `/families/37`)

<a id="diffdock-maca"></a>
## diffdock-maca (`diffdock-maca`)

主题：ai4s

检索别名：diffdock-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[diffdock-maca](ecosystem/2026-11-21/images.json) (images, `/families/41`)

<a id="diffsynth-studio"></a>
## diffsynth-studio (`diffsynth-studio`)

主题：training

检索别名：diffsynth-studio

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[diffsynth-studio](ecosystem/2026-11-21/images.json) (images, `/families/16`)；[DiffSynth-Studio](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/17`)

<a id="diffusers.training"></a>
## diffusers.training (`diffusers.training`)

主题：training

检索别名：diffusers.training

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[diffusers.training](ecosystem/2026-11-21/images.json) (images, `/families/3`)；[Diffusers.Training](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/6`)

<a id="dlrover"></a>
## dlrover (`dlrover`)

主题：cloud

检索别名：dlrover、mxDlrover

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[dlrover](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/51`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxDlrover](repositories/2026-11-21/repositories.json) (repository, `/repositories/45`)

<a id="dlrover-master"></a>
## dlrover-master (`dlrover-master`)

主题：cloud

检索别名：dlrover-master

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[dlrover-master](ecosystem/2026-11-21/images.json) (images, `/families/49`)

<a id="driver"></a>
## Driver (`driver`)

主题：environment

检索别名：Driver

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[Driver](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/0`)
- 实践 2026-11-23 / case：[C500卡6热复位后MetaXLink错误复发](practice/cases/2026-11-23-c500-warm-reset-recurrence/case.md)（行 1；warm_reset_transient_recovery_then_recurrence；适用范围见原文）
- 实践 2026-11-23 / case：[重启后禁用P2P完成八卡GLM GEMM单层32/32/4对照](practice/cases/2026-11-23-glm-gemm-p2p-disabled/case.md)（行 1；tp8_single_layer_pilot_passed_p2p_disabled_hardware_unresolved；适用范围见原文）

<a id="driver-image"></a>
## driver-image (`driver-image`)

主题：cloud

检索别名：driver-image

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[driver-image](ecosystem/2026-11-21/images.json) (images, `/families/61`)

<a id="driver-manager"></a>
## driver-manager (`driver-manager`)

主题：cloud

检索别名：driver-manager

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[driver-manager](ecosystem/2026-11-21/images.json) (images, `/families/53`)

<a id="elasticjob-controller"></a>
## elasticjob-controller (`elasticjob-controller`)

主题：cloud

检索别名：elasticjob-controller

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[elasticjob-controller](ecosystem/2026-11-21/images.json) (images, `/families/52`)

<a id="gpu-aware"></a>
## gpu-aware (`gpu-aware`)

主题：cloud

检索别名：gpu-aware

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[gpu-aware](ecosystem/2026-11-21/images.json) (images, `/families/51`)

<a id="gpu-benchmark"></a>
## GPU 基准测试集合 (`gpu-benchmark`)

主题：profiling

检索别名：gpuBenchmark

- 背景文档：[沐曦通用GPU_mcProfiler使用手册 · V06](generated/documents/mcprofiler-v06.md)（章节与物理页定位见链接）
- 背景文档：[沐曦通用GPU_mcTracer使用手册 · V08](generated/documents/mctracer-v08.md)（章节与物理页定位见链接）
- 背景文档：[沐曦通用GPU_mxvs测试工具套件使用手册 · V26](generated/documents/mxvs-v26.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[gpuBenchmark](repositories/2026-11-21/repositories.json) (repository, `/repositories/13`)

<a id="gpu-device"></a>
## gpu-device (`gpu-device`)

主题：cloud

检索别名：gpu-device

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[gpu-device](ecosystem/2026-11-21/images.json) (images, `/families/46`)

<a id="gpu-label"></a>
## gpu-label (`gpu-label`)

主题：cloud

检索别名：gpu-label

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[gpu-label](ecosystem/2026-11-21/images.json) (images, `/families/56`)

<a id="gpu-scheduler"></a>
## gpu-scheduler (`gpu-scheduler`)

主题：cloud

检索别名：gpu-scheduler

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[gpu-scheduler](ecosystem/2026-11-21/images.json) (images, `/families/45`)

<a id="internlm"></a>
## internlm (`internlm`)

主题：training

检索别名：internlm

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[internlm](ecosystem/2026-11-21/images.json) (images, `/families/27`)；[InternLM](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/7`)

<a id="iree"></a>
## IREE (`iree`)

主题：inference

检索别名：IREE

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[IREE](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/24`)

<a id="jax"></a>
## JAX (`jax`)

主题：training

检索别名：JAX

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[JAX](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/16`)

<a id="kubectl-plugins"></a>
## kubectl-plugins (`kubectl-plugins`)

主题：cloud

检索别名：kubectl-plugins

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[kubectl-plugins](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/52`)

<a id="liger-kernel"></a>
## liger-kernel (`liger-kernel`)

主题：kernels

检索别名：liger-kernel

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[liger-kernel](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/35`)

<a id="linux-perf-kit"></a>
## linux-perf-kit (`linux-perf-kit`)

主题：profiling

检索别名：linux-perf-kit

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[linux-perf-kit](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/63`)

<a id="lmcache"></a>
## LMCache (`lmcache`)

主题：inference

检索别名：LMCache

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[LMCache](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/33`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[LMCache](repositories/2026-11-21/repositories.json) (repository, `/repositories/16`)

<a id="mac-perf-kit"></a>
## mac-perf-kit (`mac-perf-kit`)

主题：profiling

检索别名：mac-perf-kit

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mac-perf-kit](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/64`)

<a id="maca"></a>
## MXMACA / SDK (`maca`)

主题：environment, development

检索别名：MXMACA、MACA SDK、SDK

- 直接文档：[沐曦通用GPU_MXMACA C++编程指南 · V06](generated/documents/maca-cpp-v06.md)（章节与物理页定位见链接）
- 直接文档：[沐曦通用GPU_运行时API编程指南 · V18](generated/documents/runtime-api-v18.md)（章节与物理页定位见链接）
- 直接文档：[沐曦通用GPU_mxcc编译器用户指南 · V06](generated/documents/mxcc-v06.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[maca](ecosystem/2026-11-21/images.json) (images, `/families/0`)；[SDK](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/1`)
- 实践 2026-11-22 / runbook：[MetaX 独立推理环境的构建与溯源](practice/runbooks/isolated-metax-environment.md)（行 1；case_derived_guidance；适用范围见原文）
- 说明：SDK 与基础镜像的导航关联；不代表所有版本包含相同组件。

<a id="maca-cpp"></a>
## MXMACA C++ 编程 (`maca-cpp`)

主题：kernels, development

检索别名：MACA C++

- 直接文档：[沐曦通用GPU_MXMACA C++编程指南 · V06](generated/documents/maca-cpp-v06.md)（章节与物理页定位见链接）
- 直接文档：[沐曦通用GPU_MXMACA编译器内建函数编程指南 · V01](generated/documents/builtins-v01.md)（章节与物理页定位见链接）
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="maca-llm-quantizer"></a>
## maca-llm-quantizer (`maca-llm-quantizer`)

主题：inference

检索别名：maca-llm-quantizer

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[maca-llm-quantizer](ecosystem/2026-11-21/images.json) (images, `/families/24`)

<a id="maca-native"></a>
## maca-native (`maca-native`)

主题：environment

检索别名：maca-native

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[maca-native](ecosystem/2026-11-21/images.json) (images, `/families/1`)

<a id="maca-samples"></a>
## MACA 编程示例 (`maca-samples`)

主题：development, kernels

检索别名：maca-samples

- 背景文档：[沐曦通用GPU_MXMACA C++编程指南 · V06](generated/documents/maca-cpp-v06.md)（章节与物理页定位见链接）
- 背景文档：[沐曦通用GPU_运行时API编程指南 · V18](generated/documents/runtime-api-v18.md)（章节与物理页定位见链接）
- 背景文档：[沐曦通用GPU_mxcc编译器用户指南 · V06](generated/documents/mxcc-v06.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[maca-samples](repositories/2026-11-21/repositories.json) (repository, `/repositories/17`)

<a id="mcblas"></a>
## mcBLAS (`mcblas`)

主题：libraries, kernels

检索别名：mcBLAS

- 直接文档：[沐曦通用GPU_mcBLAS API参考 · V05](generated/documents/mcblas-v05.md)（章节与物理页定位见链接）
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="mccl"></a>
## MCCL (`mccl`)

主题：communication

检索别名：MCCL、mccl-nccl

- 直接文档：[沐曦通用GPU_MCCL编程指南 · V08](generated/documents/mccl-v08.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mccl-nccl](repositories/2026-11-21/repositories.json) (repository, `/repositories/20`)
- 实践 2026-11-23 / issue：[GPU6不可用阻断八卡GEMM模型验证](practice/cases/2026-11-23-glm-gemm-prototype/issues.md)（行 3；scoped_server_validation_model_blocked；适用范围见原文）
- 实践 2026-11-23 / case：[C500卡6热复位后MetaXLink错误复发](practice/cases/2026-11-23-c500-warm-reset-recurrence/case.md)（行 1；warm_reset_transient_recovery_then_recurrence；适用范围见原文）
- 实践 2026-11-23 / case：[重启后禁用P2P完成八卡GLM GEMM单层32/32/4对照](practice/cases/2026-11-23-glm-gemm-p2p-disabled/case.md)（行 1；tp8_single_layer_pilot_passed_p2p_disabled_hardware_unresolved；适用范围见原文）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="mccl-tests"></a>
## MCCL 通信测试 (`mccl-tests`)

主题：communication, profiling

检索别名：mccl_tests

- 背景文档：[沐曦通用GPU_MCCL编程指南 · V08](generated/documents/mccl-v08.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mccl_tests](repositories/2026-11-21/repositories.json) (repository, `/repositories/21`)
- 相关入口（不自动扩展检索范围）：[mccl](#mccl)

<a id="mcdf"></a>
## mcdf (`mcdf`)

主题：libraries

检索别名：mcdf

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mcdf](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/46`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcdf](repositories/2026-11-21/repositories.json) (repository, `/repositories/22`)

<a id="mceigen"></a>
## mcEigen (`mceigen`)

主题：libraries, development

检索别名：mcEigen

- 直接文档：[曦云系列_通用计算GPU_mcEigen用户指南 · V03](generated/documents/mceigen-v03.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcEigen](repositories/2026-11-21/repositories.json) (repository, `/repositories/23`)

<a id="mcfaiss"></a>
## mcfaiss (`mcfaiss`)

主题：libraries

检索别名：mcfaiss、mcFaiss

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mcfaiss](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/47`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcFaiss](repositories/2026-11-21/repositories.json) (repository, `/repositories/24`)

<a id="mcoplib"></a>
## mcoplib (`mcoplib`)

主题：kernels

检索别名：mcoplib

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mcoplib](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/30`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcoplib](repositories/2026-11-21/repositories.json) (repository, `/repositories/28`)
- 实践 2026-11-22 / issue：[MoE alignment 的 7 与 8 参数 ABI](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 13；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[INT8 sparse indexer 的 Tensor 契约](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 23；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-23 / issue：[GLM历史9题greedy分叉尚未复现](practice/cases/2026-11-23-glm-greedy-repeatability/issues.md)（行 5；open_root_cause_not_reproduced；适用范围见原文）
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 实践 2026-11-23 / case：[重启后禁用P2P完成八卡GLM GEMM单层32/32/4对照](practice/cases/2026-11-23-glm-gemm-p2p-disabled/case.md)（行 1；tp8_single_layer_pilot_passed_p2p_disabled_hardware_unresolved；适用范围见原文）

<a id="mcprofiler"></a>
## mcProfiler (`mcprofiler`)

主题：profiling

检索别名：mcProfiler

- 直接文档：[沐曦通用GPU_mcProfiler使用手册 · V06](generated/documents/mcprofiler-v06.md)（章节与物理页定位见链接）
- 相关入口（不自动扩展检索范围）：[linux-perf-kit](#linux-perf-kit)、[win-perf-kit](#win-perf-kit)

<a id="mcpy"></a>
## mcpy (`mcpy`)

主题：libraries

检索别名：mcpy

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mcpy](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/45`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcpy](repositories/2026-11-21/repositories.json) (repository, `/repositories/29`)

<a id="mcpytorch"></a>
## mcPyTorch / maca-pytorch (`mcpytorch`)

主题：environment, inference, training

检索别名：mcPyTorch、PyTorch、maca-pytorch、mcPytorch

- 直接文档：[沐曦通用GPU_mcPyTorch用户指南 · V16](generated/documents/mcpytorch-v16.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[maca-pytorch](ecosystem/2026-11-21/images.json) (images, `/families/12`)；[Pytorch](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/11`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcPytorch](repositories/2026-11-21/repositories.json) (repository, `/repositories/30`)
- 实践 2026-11-22 / runbook：[MetaX 独立推理环境的构建与溯源](practice/runbooks/isolated-metax-environment.md)（行 1；case_derived_guidance；适用范围见原文）

<a id="mctracer"></a>
## mcTracer (`mctracer`)

主题：profiling

检索别名：mcTracer

- 直接文档：[沐曦通用GPU_mcTracer使用手册 · V08](generated/documents/mctracer-v08.md)（章节与物理页定位见链接）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="mctriton"></a>
## mcTriton (`mctriton`)

主题：kernels, development

检索别名：mcTriton、Triton 编译器

- 直接文档：[沐曦通用GPU_mcTriton用户指南 · V08](generated/documents/mctriton-v08.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcTriton](repositories/2026-11-21/repositories.json) (repository, `/repositories/34`)
- 实践 2026-11-22 / runbook：[MetaX 独立推理环境的构建与溯源](practice/runbooks/isolated-metax-environment.md)（行 1；case_derived_guidance；适用范围见原文）
- 实践 2026-11-23 / issue：[GLM历史9题greedy分叉尚未复现](practice/cases/2026-11-23-glm-greedy-repeatability/issues.md)（行 5；open_root_cause_not_reproduced；适用范围见原文）
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 实践 2026-11-23 / case：[重启后禁用P2P完成八卡GLM GEMM单层32/32/4对照](practice/cases/2026-11-23-glm-gemm-p2p-disabled/case.md)（行 1；tp8_single_layer_pilot_passed_p2p_disabled_hardware_unresolved；适用范围见原文）
- 相关入口（不自动扩展检索范围）：[mcpytorch](#mcpytorch)
- 说明：算子编程组件；与 Triton Inference Server 分开。发行入口可参考 PyTorch 配套说明，具体版本需核对。

<a id="mcvs"></a>
## mcvs (`mcvs`)

主题：libraries

检索别名：mcvs

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mcvs](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/48`)

<a id="megatron-lm"></a>
## Megatron LM (`megatron-lm`)

主题：training

检索别名：megatron-lm、Megatron LM

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[megatron-lm](ecosystem/2026-11-21/images.json) (images, `/families/23`)；[Megatron LM](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/8`)

<a id="metax-arena"></a>
## metax-arena (`metax-arena`)

主题：cloud

检索别名：metax-arena

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-arena](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/53`)

<a id="metax-docker"></a>
## metax-docker (`metax-docker`)

主题：cloud

检索别名：metax-docker

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-docker](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/54`)

<a id="metax-gpu-k8s"></a>
## metax-gpu-k8s (`metax-gpu-k8s`)

主题：cloud

检索别名：metax-gpu-k8s

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-gpu-k8s](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/55`)

<a id="metax-gpu-k8s-package-base"></a>
## metax-gpu-k8s-package-base (`metax-gpu-k8s-package-base`)

主题：cloud

检索别名：metax-gpu-k8s-package-base

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-gpu-k8s-package-base](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/56`)

<a id="metax-gpu-openshift"></a>
## metax-gpu-openshift (`metax-gpu-openshift`)

主题：cloud

检索别名：metax-gpu-openshift

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-gpu-openshift](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/57`)

<a id="metax-gpu-scheduler"></a>
## metax-gpu-scheduler (`metax-gpu-scheduler`)

主题：cloud

检索别名：metax-gpu-scheduler

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-gpu-scheduler](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/58`)

<a id="metax-k8s-driver-image"></a>
## metax-k8s-driver-image (`metax-k8s-driver-image`)

主题：cloud

检索别名：metax-k8s-driver-image

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-k8s-driver-image](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/59`)

<a id="metax-operator"></a>
## metax-operator (`metax-operator`)

主题：cloud

检索别名：metax-operator

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[metax-operator](ecosystem/2026-11-21/images.json) (images, `/families/60`)

<a id="mihomo"></a>
## Mihomo 下载代理 (`mihomo`)

主题：environment

检索别名：Mihomo、Clash

- 本地 PDF：未建立关联。
- 实践 2026-11-22 / runbook：[Mihomo 下载代理的配置与验证](practice/runbooks/mihomo-download-proxy.md)（行 1；case_derived_guidance；适用范围见原文）
- 实践 2026-11-22 / case：[2026-11-22 GLM-5.3-Flash-W8A8 八卡部署](practice/cases/2026-11-22-glm53-w8a8-tp8/README.md)（行 1；historical_case_with_scoped_evidence；适用范围见原文）
- 说明：部署基础设施导航；不表示厂商 C500 软件兼容认证。

<a id="mim"></a>
## MIM 镜像服务 (`mim`)

主题：environment

检索别名：MIM、Docker registry

- 本地 PDF：未建立关联。
- 实践 2026-11-22 / runbook：[MIM 登录与镜像下载排障](practice/runbooks/mim-auth-and-download.md)（行 1；case_derived_guidance；适用范围见原文）
- 实践 2026-11-22 / case：[2026-11-22 GLM-5.3-Flash-W8A8 八卡部署](practice/cases/2026-11-22-glm53-w8a8-tp8/README.md)（行 1；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[MIM 鉴权成功后大层下载仍失败](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 5；historical_case_with_scoped_evidence；适用范围见原文）
- 说明：部署基础设施导航；不表示厂商 C500 软件兼容认证。

<a id="mmcv"></a>
## mmcv (`mmcv`)

主题：kernels

检索别名：mmcv

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mmcv](ecosystem/2026-11-21/images.json) (images, `/families/2`)；[MMCV](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/27`)

<a id="modelzoo.cnn.inference"></a>
## modelzoo.cnn.inference (`modelzoo.cnn.inference`)

主题：inference

检索别名：modelzoo.cnn.inference

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[modelzoo.cnn.inference](ecosystem/2026-11-21/images.json) (images, `/families/18`)；[Modelzoo.CNN.Inference](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/36`)

<a id="modelzoo.cnn.training"></a>
## modelzoo.cnn.training (`modelzoo.cnn.training`)

主题：training

检索别名：modelzoo.cnn.training

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[modelzoo.cnn.training](ecosystem/2026-11-21/images.json) (images, `/families/9`)；[Modelzoo.CNN.Training](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/38`)

<a id="modelzoo.llm.diffusers"></a>
## modelzoo.llm.diffusers (`modelzoo.llm.diffusers`)

主题：inference

检索别名：modelzoo.llm.diffusers

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[modelzoo.llm.diffusers](ecosystem/2026-11-21/images.json) (images, `/families/10`)；[Modelzoo.LLM.Diffusers](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/39`)

<a id="modelzoo.llm.sglang"></a>
## modelzoo.llm.sglang (`modelzoo.llm.sglang`)

主题：inference

检索别名：modelzoo.llm.sglang

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[modelzoo.llm.sglang](ecosystem/2026-11-21/images.json) (images, `/families/21`)；[Modelzoo.llm.SGLang](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/37`)

<a id="modelzoo.llm.transformers"></a>
## modelzoo.llm.transformers (`modelzoo.llm.transformers`)

主题：inference

检索别名：modelzoo.llm.transformers

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[modelzoo.llm.transformers](ecosystem/2026-11-21/images.json) (images, `/families/5`)；[Modelzoo.LLM.Transformers](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/40`)

<a id="modelzoo.llm.vllm"></a>
## modelzoo.llm.vllm (`modelzoo.llm.vllm`)

主题：inference

检索别名：modelzoo.llm.vllm

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[modelzoo.llm.vllm](ecosystem/2026-11-21/images.json) (images, `/families/14`)；[Modelzoo.LLM.vLLM](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/41`)

<a id="monai-maca"></a>
## monai-maca (`monai-maca`)

主题：ai4s

检索别名：monai-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[monai-maca](ecosystem/2026-11-21/images.json) (images, `/families/31`)

<a id="mooncake"></a>
## mooncake (`mooncake`)

主题：communication, inference

检索别名：mooncake、Mooncake

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mooncake](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/32`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[Mooncake](repositories/2026-11-21/repositories.json) (repository, `/repositories/42`)

<a id="ms-swift"></a>
## ms-swift (`ms-swift`)

主题：training

检索别名：ms-swift

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[ms-swift](ecosystem/2026-11-21/images.json) (images, `/families/17`)；[ms-swift](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/15`)

<a id="mx-exporter"></a>
## mx-exporter (`mx-exporter`)

主题：cloud

检索别名：mx-exporter、mxExporter

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mx-exporter](ecosystem/2026-11-21/images.json) (images, `/families/57`)；[mx-exporter](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/60`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxExporter](repositories/2026-11-21/repositories.json) (repository, `/repositories/46`)

<a id="mxcc"></a>
## mxcc (`mxcc`)

主题：development, kernels

检索别名：mxcc

- 直接文档：[沐曦通用GPU_mxcc编译器用户指南 · V06](generated/documents/mxcc-v06.md)（章节与物理页定位见链接）
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="mxdcm"></a>
## mxdcm (`mxdcm`)

主题：cloud

检索别名：mxdcm

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mxdcm](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/49`)

<a id="mxkind"></a>
## mxkind (`mxkind`)

主题：cloud

检索别名：mxkind

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[mxkind](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/61`)

<a id="mxrdma"></a>
## MXRDMA (`mxrdma`)

主题：environment

检索别名：MXRDMA

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[MXRDMA](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/3`)

<a id="mxvs"></a>
## mxvs (`mxvs`)

主题：environment, profiling, communication

检索别名：mxvs

- 直接文档：[沐曦通用GPU_mxvs测试工具套件使用手册 · V26](generated/documents/mxvs-v26.md)（章节与物理页定位见链接）
- 相关入口（不自动扩展检索范围）：[maca](#maca)
- 说明：不与官网目录中的 mcvs 合并；二者关系待核实。

<a id="neuralgcm-maca"></a>
## neuralgcm-maca (`neuralgcm-maca`)

主题：ai4s

检索别名：neuralgcm-maca

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[neuralgcm-maca](ecosystem/2026-11-21/images.json) (images, `/families/32`)

<a id="onnxruntime"></a>
## ONNX Runtime (`onnxruntime`)

主题：inference

检索别名：onnxruntime、ONNX Runtime、Onnxruntime

- 背景文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[onnxruntime](ecosystem/2026-11-21/images.json) (images, `/families/4`)；[ONNXRuntime](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/19`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[Onnxruntime](repositories/2026-11-21/repositories.json) (repository, `/repositories/51`)

<a id="op-optimization"></a>
## C500 算子优化实践 (`op-optimization`)

主题：kernels, profiling

检索别名：op_optimization

- 背景文档：[沐曦通用GPU_mcTriton用户指南 · V08](generated/documents/mctriton-v08.md)（章节与物理页定位见链接）
- 背景文档：[沐曦通用GPU_mxcc编译器用户指南 · V06](generated/documents/mxcc-v06.md)（章节与物理页定位见链接）
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[op_optimization](repositories/2026-11-21/repositories.json) (repository, `/repositories/52`)
- 相关入口（不自动扩展检索范围）：[tilelang](#tilelang)

<a id="operator-bundle"></a>
## operator-bundle (`operator-bundle`)

主题：cloud

检索别名：operator-bundle

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[operator-bundle](ecosystem/2026-11-21/images.json) (images, `/families/42`)

<a id="operator-catalog"></a>
## operator-catalog (`operator-catalog`)

主题：cloud

检索别名：operator-catalog

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[operator-catalog](ecosystem/2026-11-21/images.json) (images, `/families/43`)

<a id="operator-controller"></a>
## operator-controller (`operator-controller`)

主题：cloud

检索别名：operator-controller

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[operator-controller](ecosystem/2026-11-21/images.json) (images, `/families/44`)

<a id="paddle"></a>
## Paddle 旧分支 (`paddle`)

主题：training

检索别名：paddle

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[paddle](ecosystem/2026-11-21/images.json) (images, `/families/19`)；[Paddle【2.6.0版本及以下】](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/9`)

<a id="paddle-metax"></a>
## Paddle-MetaX (`paddle-metax`)

主题：training

检索别名：paddle-metax

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[paddle-metax](ecosystem/2026-11-21/images.json) (images, `/families/7`)；[Paddle【3.3.0版本及以上】](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/10`)

<a id="physicsnemo"></a>
## PhysicsNeMo (`physicsnemo`)

主题：ai4s

检索别名：PhysicsNeMo

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[physicsnemo-maca](ecosystem/2026-11-21/images.json) (images, `/families/33`)；[PhysicsNeMo](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/42`)

<a id="pyg"></a>
## PyG (`pyg`)

主题：ai4s

检索别名：PyG

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[pyg_lib-maca](ecosystem/2026-11-21/images.json) (images, `/families/35`)；[PyG](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/43`)
- 说明：同生态的目录关联，不将 PyG 与 pyg_lib 视为相同发行物。

<a id="ray-2.46.0"></a>
## Ray【2.46.0版本及以下】 (`ray-2.46.0`)

主题：training, cloud

检索别名：Ray【2.46.0版本及以下】

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[Ray【2.46.0版本及以下】](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/28`)

<a id="ray-2.48.0"></a>
## Ray【2.48.0版本及以上】 (`ray-2.48.0`)

主题：training, cloud

检索别名：Ray【2.48.0版本及以上】

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[Ray【2.48.0版本及以上】](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/29`)

<a id="repo-3fs"></a>
## 3FS (`repo-3fs`)

主题：communication

检索别名：3FS

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[3FS](repositories/2026-11-21/repositories.json) (repository, `/repositories/0`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-ai4s-framework"></a>
## AI4S-Framework (`repo-ai4s-framework`)

主题：ai4s

检索别名：AI4S-Framework

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[AI4S-Framework](repositories/2026-11-21/repositories.json) (repository, `/repositories/1`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-autonomous_driving_simulation"></a>
## Autonomous_Driving_Simulation (`repo-autonomous_driving_simulation`)

主题：inference

检索别名：Autonomous_Driving_Simulation

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[Autonomous_Driving_Simulation](repositories/2026-11-21/repositories.json) (repository, `/repositories/3`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-deepep"></a>
## DeepEP (`repo-deepep`)

主题：communication

检索别名：DeepEP

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[DeepEP](repositories/2026-11-21/repositories.json) (repository, `/repositories/4`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-docflowai"></a>
## DocFlowAI (`repo-docflowai`)

主题：inference

检索别名：DocFlowAI

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[DocFlowAI](repositories/2026-11-21/repositories.json) (repository, `/repositories/5`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-embodied_ai_simulation"></a>
## Embodied_AI_Simulation (`repo-embodied_ai_simulation`)

主题：inference

检索别名：Embodied_AI_Simulation

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[Embodied_AI_Simulation](repositories/2026-11-21/repositories.json) (repository, `/repositories/6`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-fio"></a>
## fio (`repo-fio`)

主题：communication

检索别名：fio

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[fio](repositories/2026-11-21/repositories.json) (repository, `/repositories/7`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-flashattn"></a>
## flashattn (`repo-flashattn`)

主题：kernels, libraries

检索别名：flashattn

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[flashattn](repositories/2026-11-21/repositories.json) (repository, `/repositories/8`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-flashmla"></a>
## FlashMLA (`repo-flashmla`)

主题：kernels, libraries

检索别名：FlashMLA

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[FlashMLA](repositories/2026-11-21/repositories.json) (repository, `/repositories/9`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-geoscience"></a>
## GeoScience (`repo-geoscience`)

主题：ai4s

检索别名：GeoScience

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[GeoScience](repositories/2026-11-21/repositories.json) (repository, `/repositories/10`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-go-mxsml"></a>
## go-mxsml (`repo-go-mxsml`)

主题：cloud, development

检索别名：go-mxsml

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[go-mxsml](repositories/2026-11-21/repositories.json) (repository, `/repositories/11`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-goutils"></a>
## goutils (`repo-goutils`)

主题：cloud, development

检索别名：goutils

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[goutils](repositories/2026-11-21/repositories.json) (repository, `/repositories/12`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-lifescience"></a>
## LifeScience (`repo-lifescience`)

主题：ai4s

检索别名：LifeScience

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[LifeScience](repositories/2026-11-21/repositories.json) (repository, `/repositories/15`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-materials"></a>
## Materials (`repo-materials`)

主题：ai4s

检索别名：Materials

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[Materials](repositories/2026-11-21/repositories.json) (repository, `/repositories/18`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcapex"></a>
## mcApex (`repo-mcapex`)

主题：development, training

检索别名：mcApex

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcApex](repositories/2026-11-21/repositories.json) (repository, `/repositories/19`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcfile-python"></a>
## mcfile-python (`repo-mcfile-python`)

主题：communication

检索别名：mcfile-python

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcfile-python](repositories/2026-11-21/repositories.json) (repository, `/repositories/25`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcflashinfer"></a>
## McFlashInfer (`repo-mcflashinfer`)

主题：kernels, libraries

检索别名：McFlashInfer

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[McFlashInfer](repositories/2026-11-21/repositories.json) (repository, `/repositories/26`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcflashmla"></a>
## mcFlashMLA (`repo-mcflashmla`)

主题：kernels, libraries

检索别名：mcFlashMLA

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcFlashMLA](repositories/2026-11-21/repositories.json) (repository, `/repositories/27`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcsolver"></a>
## mcSolver (`repo-mcsolver`)

主题：kernels, libraries

检索别名：mcSolver

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcSolver](repositories/2026-11-21/repositories.json) (repository, `/repositories/31`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcsparse"></a>
## mcSparse (`repo-mcsparse`)

主题：kernels, libraries

检索别名：mcSparse

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcSparse](repositories/2026-11-21/repositories.json) (repository, `/repositories/32`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mctlass"></a>
## mcTlass (`repo-mctlass`)

主题：kernels, libraries

检索别名：mcTlass

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcTlass](repositories/2026-11-21/repositories.json) (repository, `/repositories/33`)
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mctvm"></a>
## mcTVM (`repo-mctvm`)

主题：development, training

检索别名：mcTVM

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcTVM](repositories/2026-11-21/repositories.json) (repository, `/repositories/35`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mcxformer"></a>
## mcXformer (`repo-mcxformer`)

主题：development, training

检索别名：mcXformer

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mcXformer](repositories/2026-11-21/repositories.json) (repository, `/repositories/36`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-medicalimage"></a>
## MedicalImage (`repo-medicalimage`)

主题：ai4s

检索别名：MedicalImage

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[MedicalImage](repositories/2026-11-21/repositories.json) (repository, `/repositories/37`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-metax-ai4s"></a>
## metax-ai4s (`repo-metax-ai4s`)

主题：ai4s

检索别名：metax-ai4s

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[metax-ai4s](repositories/2026-11-21/repositories.json) (repository, `/repositories/38`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-metax-lifescience-toolkit"></a>
## metax-lifescience-toolkit (`repo-metax-lifescience-toolkit`)

主题：ai4s

检索别名：metax-lifescience-toolkit

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[metax-lifescience-toolkit](repositories/2026-11-21/repositories.json) (repository, `/repositories/39`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-metax-maca.github.io"></a>
## MetaX-MACA.github.io (`repo-metax-maca.github.io`)

主题：cloud, development

检索别名：MetaX-MACA.github.io

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[MetaX-MACA.github.io](repositories/2026-11-21/repositories.json) (repository, `/repositories/40`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-modelzoo"></a>
## modelzoo (`repo-modelzoo`)

主题：inference, training

检索别名：modelzoo

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[modelzoo](repositories/2026-11-21/repositories.json) (repository, `/repositories/41`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mxcuco"></a>
## mxCuco (`repo-mxcuco`)

主题：kernels, libraries

检索别名：mxCuco

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxCuco](repositories/2026-11-21/repositories.json) (repository, `/repositories/43`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mxfio"></a>
## mxFIO (`repo-mxfio`)

主题：communication

检索别名：mxFIO

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxFIO](repositories/2026-11-21/repositories.json) (repository, `/repositories/47`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mxjitify"></a>
## mxJitify (`repo-mxjitify`)

主题：development, training

检索别名：mxJitify

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxJitify](repositories/2026-11-21/repositories.json) (repository, `/repositories/48`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mxnumbax"></a>
## mxNumbax (`repo-mxnumbax`)

主题：development, training

检索别名：mxNumbax

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxNumbax](repositories/2026-11-21/repositories.json) (repository, `/repositories/49`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-mxrmmx"></a>
## mxRmmx (`repo-mxrmmx`)

主题：kernels, libraries

检索别名：mxRmmx

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[mxRmmx](repositories/2026-11-21/repositories.json) (repository, `/repositories/50`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-physics"></a>
## Physics (`repo-physics`)

主题：ai4s

检索别名：Physics

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[Physics](repositories/2026-11-21/repositories.json) (repository, `/repositories/53`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-ppl.llm.serving"></a>
## ppl.llm.serving (`repo-ppl.llm.serving`)

主题：inference, training

检索别名：ppl.llm.serving

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[ppl.llm.serving](repositories/2026-11-21/repositories.json) (repository, `/repositories/54`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-pymxsml"></a>
## pymxsml (`repo-pymxsml`)

主题：cloud, development

检索别名：pymxsml

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[pymxsml](repositories/2026-11-21/repositories.json) (repository, `/repositories/55`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-quickguide"></a>
## QuickGuide (`repo-quickguide`)

主题：development, profiling, kernels

检索别名：QuickGuide

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[QuickGuide](repositories/2026-11-21/repositories.json) (repository, `/repositories/56`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-simple-jenkins-githubaction"></a>
## simple-jenkins-githubaction (`repo-simple-jenkins-githubaction`)

主题：cloud, development

检索别名：simple-jenkins-githubaction

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[simple-jenkins-githubaction](repositories/2026-11-21/repositories.json) (repository, `/repositories/58`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-tilekernels-metax"></a>
## TileKernels-Metax (`repo-tilekernels-metax`)

主题：kernels, libraries

检索别名：TileKernels-Metax

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[TileKernels-Metax](repositories/2026-11-21/repositories.json) (repository, `/repositories/59`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-tileops-metax"></a>
## TileOPs-Metax (`repo-tileops-metax`)

主题：kernels, libraries

检索别名：TileOPs-Metax

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[TileOPs-Metax](repositories/2026-11-21/repositories.json) (repository, `/repositories/60`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-virtualhuman"></a>
## VirtualHuman (`repo-virtualhuman`)

主题：inference

检索别名：VirtualHuman

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[VirtualHuman](repositories/2026-11-21/repositories.json) (repository, `/repositories/62`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="repo-weatherforecast"></a>
## WeatherForecast (`repo-weatherforecast`)

主题：ai4s

检索别名：WeatherForecast

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[WeatherForecast](repositories/2026-11-21/repositories.json) (repository, `/repositories/65`)
- 说明：GitHub 仓库导航；C500 适用性以具体分支资料为准。

<a id="runtime-api"></a>
## 运行时 API (`runtime-api`)

主题：environment, kernels, communication

检索别名：runtime API、运行时API

- 直接文档：[沐曦通用GPU_运行时API编程指南 · V18](generated/documents/runtime-api-v18.md)（章节与物理页定位见链接）
- 相关入口（不自动扩展检索范围）：[maca](#maca)

<a id="sdk-python"></a>
## SDK-Python (`sdk-python`)

主题：environment

检索别名：SDK-Python

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[SDK-Python](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/2`)

<a id="sglang"></a>
## SGLang (`sglang`)

主题：inference

检索别名：sglang

- 背景文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[sglang](ecosystem/2026-11-21/images.json) (images, `/families/20`)；[SGLANG](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/23`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[sglang](repositories/2026-11-21/repositories.json) (repository, `/repositories/57`)

<a id="slime"></a>
## slime (`slime`)

主题：training

检索别名：slime

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[slime](ecosystem/2026-11-21/images.json) (images, `/families/11`)；[Slime](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/18`)

<a id="tensorflow2"></a>
## tensorflow2 (`tensorflow2`)

主题：training

检索别名：tensorflow2

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[tensorflow2](ecosystem/2026-11-21/images.json) (images, `/families/6`)；[TensorFlow2](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/12`)

<a id="tilelang"></a>
## TileLang (`tilelang`)

主题：kernels, development

检索别名：TileLang

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[TileLang](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/66`)

<a id="topo-master"></a>
## topo-master (`topo-master`)

主题：cloud

检索别名：topo-master

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[topo-master](ecosystem/2026-11-21/images.json) (images, `/families/55`)

<a id="topo-worker"></a>
## topo-worker (`topo-worker`)

主题：cloud

检索别名：topo-worker

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[topo-worker](ecosystem/2026-11-21/images.json) (images, `/families/58`)

<a id="transformerengine"></a>
## transformerengine (`transformerengine`)

主题：training, kernels

检索别名：transformerengine

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[transformerengine](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/31`)

<a id="triton-inference-server"></a>
## Triton Inference Server (`triton-inference-server`)

主题：inference

检索别名：Triton-Inference-Server

- 背景文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[triton-inference-server](ecosystem/2026-11-21/images.json) (images, `/families/29`)；[Triton-Inference-Server](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/20`)
- 说明：推理服务框架；不是 mcTriton。

<a id="vc-controller-manager"></a>
## vc-controller-manager (`vc-controller-manager`)

主题：cloud

检索别名：vc-controller-manager

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[vc-controller-manager](ecosystem/2026-11-21/images.json) (images, `/families/54`)

<a id="vc-scheduler"></a>
## vc-scheduler (`vc-scheduler`)

主题：cloud

检索别名：vc-scheduler

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[vc-scheduler](ecosystem/2026-11-21/images.json) (images, `/families/50`)

<a id="vc-webhook-manager"></a>
## vc-webhook-manager (`vc-webhook-manager`)

主题：cloud

检索别名：vc-webhook-manager

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[vc-webhook-manager](ecosystem/2026-11-21/images.json) (images, `/families/47`)

<a id="verl"></a>
## verl (`verl`)

主题：training

检索别名：verl

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[verl](ecosystem/2026-11-21/images.json) (images, `/families/15`)；[Verl](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/14`)

<a id="verl-metax"></a>
## verl MetaX 硬件插件 (`verl-metax`)

主题：training

检索别名：verl-metax

- 本地 PDF：未建立关联。
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[verl-metax](repositories/2026-11-21/repositories.json) (repository, `/repositories/61`)
- 相关入口（不自动扩展检索范围）：[verl](#verl)
- 说明：插件与上游 verl 分开记录；关系不证明任意版本配套。

<a id="vllm"></a>
## vLLM 旧分支 (`vllm`)

主题：inference

检索别名：vllm

- 背景文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[vllm](ecosystem/2026-11-21/images.json) (images, `/families/30`)；[vLLM【0.10.0版本及以下】](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/21`)
- 实践 2026-11-22 / runbook：[推理验收与基线冻结](practice/runbooks/inference-validation-and-freeze.md)（行 1；case_derived_guidance；适用范围见原文）
- 实践 2026-11-22 / case：[2026-11-22 GLM-5.3-Flash-W8A8 八卡部署](practice/cases/2026-11-22-glm53-w8a8-tp8/README.md)（行 1；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[MoE alignment 的 7 与 8 参数 ABI](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 13；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[V1 非法显存访问的未闭环状态](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 42；historical_case_with_scoped_evidence；适用范围见原文）

<a id="vllm-metax"></a>
## vLLM-MetaX (`vllm-metax`)

主题：inference

检索别名：vllm-metax、vLLM-metax

- 背景文档：[沐曦通用GPU_AI推理用户手册 · V21](generated/documents/ai-inference-v21.md)（章节与物理页定位见链接）
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[vllm-metax](ecosystem/2026-11-21/images.json) (images, `/families/13`)；[vLLM【0.10.2版本及以上】](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/22`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[vLLM-metax](repositories/2026-11-21/repositories.json) (repository, `/repositories/63`)
- 实践 2026-11-22 / runbook：[MetaX 独立推理环境的构建与溯源](practice/runbooks/isolated-metax-environment.md)（行 1；case_derived_guidance；适用范围见原文）
- 实践 2026-11-22 / runbook：[推理验收与基线冻结](practice/runbooks/inference-validation-and-freeze.md)（行 1；case_derived_guidance；适用范围见原文）
- 实践 2026-11-22 / case：[2026-11-22 GLM-5.3-Flash-W8A8 八卡部署](practice/cases/2026-11-22-glm53-w8a8-tp8/README.md)（行 1；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[MoE alignment 的 7 与 8 参数 ABI](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 13；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[INT8 sparse indexer 的 Tensor 契约](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 23；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[FP8 兼容加载器吞掉 INT8 scale](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 32；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[V1 非法显存访问的未闭环状态](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 42；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-22 / issue：[冻结成功但 image ID 解析失败](practice/cases/2026-11-22-glm53-w8a8-tp8/issues.md)（行 49；historical_case_with_scoped_evidence；适用范围见原文）
- 实践 2026-11-23 / issue：[GLM历史9题greedy分叉尚未复现](practice/cases/2026-11-23-glm-greedy-repeatability/issues.md)（行 5；open_root_cause_not_reproduced；适用范围见原文）
- 实践 2026-11-23 / case：[GLM INT8 GEMM原型与vLLM量化层替换](practice/cases/2026-11-23-glm-gemm-prototype/case.md)（行 1；scoped_server_validation_model_blocked；适用范围见原文）
- 实践 2026-11-23 / issue：[GPU6不可用阻断八卡GEMM模型验证](practice/cases/2026-11-23-glm-gemm-prototype/issues.md)（行 3；scoped_server_validation_model_blocked；适用范围见原文）
- 实践 2026-11-23 / case：[C500卡6热复位后MetaXLink错误复发](practice/cases/2026-11-23-c500-warm-reset-recurrence/case.md)（行 1；warm_reset_transient_recovery_then_recurrence；适用范围见原文）
- 实践 2026-11-23 / case：[重启后禁用P2P完成八卡GLM GEMM单层32/32/4对照](practice/cases/2026-11-23-glm-gemm-p2p-disabled/case.md)（行 1；tp8_single_layer_pilot_passed_p2p_disabled_hardware_unresolved；适用范围见原文）
- 说明：推理手册是背景入口；旧版表格不证明新 tag 的兼容性。

<a id="vllm-omni-metax"></a>
## vllm-omni-metax (`vllm-omni-metax`)

主题：inference

检索别名：vllm-omni-metax

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[vllm-omni-metax](ecosystem/2026-11-21/images.json) (images, `/families/22`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[vllm-omni-metax](repositories/2026-11-21/repositories.json) (repository, `/repositories/64`)

<a id="volcano"></a>
## volcano (`volcano`)

主题：cloud

检索别名：volcano

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[volcano](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/62`)

<a id="warp"></a>
## Warp (`warp`)

主题：ai4s

检索别名：Warp、hpc_warp

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[warp-maca](ecosystem/2026-11-21/images.json) (images, `/families/38`)；[Warp](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/44`)
- [2026-11-21 / github](repositories/2026-11-21/README.md)：[hpc_warp](repositories/2026-11-21/repositories.json) (repository, `/repositories/14`)

<a id="win-perf-kit"></a>
## win-perf-kit (`win-perf-kit`)

主题：profiling

检索别名：win-perf-kit

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[win-perf-kit](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/65`)

<a id="xtuner"></a>
## xtuner (`xtuner`)

主题：training

检索别名：xtuner

- 本地 PDF：未建立关联。
- [2026-11-21 / ecosystem](ecosystem/2026-11-21/README.md)：[xtuner](ecosystem/2026-11-21/images.json) (images, `/families/28`)；[XTuner](ecosystem/2026-11-21/software_packages.json) (packages, `/entries/13`)

