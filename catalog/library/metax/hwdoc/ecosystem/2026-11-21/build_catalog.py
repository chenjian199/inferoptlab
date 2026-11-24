"""Generate an offline catalogue from the public UI observations on 2026-11-21.

This script does not crawl the website, download packages, or install software.
The rows are family-level observations, not an exhaustive tag/registry export.
"""
from pathlib import Path
from urllib.parse import urlencode
import json
import re

ROOT = Path(__file__).resolve().parent
BASE = "https://developer.metax-tech.com/softnova/"

# category | family | distinct observed cards | representative tag | recommended driver | website updated | Ubuntu 22 amd64 example
OBSERVATIONS = """MXMACA|maca|9|maca:latest-ubuntu24.04-amd64|3.100.0|2026-11-16 18:45:26|maca:latest-ubuntu22.04-amd64
MXMACA|maca-native|5|maca-native:3.5.3.6-centos9-amd64|3.5.3.x|2026-03-04 15:26:19|maca-native:3.5.3.6-ubuntu22.04-amd64
AI|mmcv|42|mmcv:2.2.0-maca.ai3.10.1.2-torch2.4-py310-kylinv11-amd64|3.100.0|2026-11-18 16:47:56|mmcv:2.2.0-maca.ai3.8.0.10-torch2.4-py38-ubuntu22.04-amd64
AI|diffusers.training|33|diffusers.training:0.28.0-maca.ai3.10.1.2-torch2.4-py310-ubuntu24.04-amd64|3.100.0|2026-11-18 16:47:56|diffusers.training:0.28.0-maca.ai3.8.0.10-torch2.4-py312-ubuntu22.04-amd64
AI|onnxruntime|31|onnxruntime:1.19.2-maca.ai3.10.1.3-torch2.4-py312-ubuntu24.04-amd64|3.100.0|2026-11-18 16:47:56|onnxruntime:1.12.0-maca.ai3.8.0.10-torch2.4-py38-ubuntu22.04-amd64
AI|modelzoo.llm.transformers|33|modelzoo.llm.transformers:1.0.1-maca.ai3.10.1.2-torch2.4-py310-ubuntu24.04-amd64|3.100.0|2026-11-18 16:47:56|modelzoo.llm.transformers:1.0.1-maca.ai3.8.0.10-torch2.4-py312-ubuntu22.04-amd64
AI|tensorflow2|8|tensorflow2:2.13.1-maca.ai3.10.1.2-py310-ubuntu24.04-amd64|3.100.0|2026-11-18 16:47:56|tensorflow2:2.13.1-maca.ai3.8.0.10-py310-ubuntu22.04-amd64
AI|paddle-metax|16|paddle-metax:3.5.0-maca.ai3.10.1.2-py312-kylinv11-amd64|3.100.0|2026-11-18 16:47:56|paddle-metax:3.5.0-maca.ai3.8.0.10-py310-ubuntu22.04-amd64
AI|cv-cuda|23|cv-cuda:0.16.0-maca.ai3.10.1.2-torch2.4-py310-kylinv11-amd64|3.100.0|2026-11-18 16:47:56|cv-cuda:0.16.0-maca.ai3.8.0.10-torch2.4-py312-ubuntu22.04-amd64
AI|modelzoo.cnn.training|29|modelzoo.cnn.training:1.0.0-maca.ai3.10.1.2-torch2.4-py310-ubuntu24.04-amd64|3.100.0|2026-11-18 16:47:56|modelzoo.cnn.training:1.0.0-maca.ai3.8.0.10-torch2.4-py310-ubuntu22.04-amd64
AI|modelzoo.llm.diffusers|30|modelzoo.llm.diffusers:1.0.3-maca.ai3.10.1.1-torch2.8-py310-kylinv11-amd64|3.100.0|2026-11-18 16:47:56|modelzoo.llm.diffusers:1.0.0-maca.ai3.7.0.8-torch2.4-py38-ubuntu22.04-amd64
AI|slime|2|slime:0.4.0-maca.ai3.9.0.0-torch2.10-py312-kylinv11-amd64|3.9.0|2026-11-18 15:31:21|
AI|maca-pytorch|11|maca-pytorch:3.10.1.2-torch2.10-py312-ubuntu24.04-amd64|3.100.0|2026-11-16 18:45:26|maca-pytorch:3.10.1.2-torch2.4-py310-ubuntu22.04-amd64
AI|vllm-metax|81|vllm-metax:0.29.0-maca.ai3.9.0.9-torch2.10-py310-ubuntu24.04-amd64|3.9.0|2026-11-05 17:58:32|vllm-metax:0.28.0-maca.ai3.8.2.401-torch2.10-py312-ubuntu22.04-amd64
AI|modelzoo.llm.vllm|63|modelzoo.llm.vllm:1.0.3-maca.ai3.9.0.9-torch2.10-py312-ubuntu24.04-amd64|3.9.0|2026-11-05 17:58:32|modelzoo.llm.vllm:1.0.3-maca.ai3.8.2.401-torch2.10-py312-ubuntu22.04-amd64
AI|verl|15|verl:0.9.0-maca.ai3.8.0.9-torch2.10-py312-ubuntu24.04-amd64|3.8.0|2026-10-12 18:30:53|verl:0.8.0-maca.ai3.7.1.9-torch2.8-py312-ubuntu22.04-amd64
AI|diffsynth-studio|1|diffsynth-studio:2.0.12-maca.ai3.9.0.3-torch2.8-py312-ubuntu24.04-amd64|3.9.0|2026-10-09 17:58:42|
AI|ms-swift|18|ms-swift:4.4.3-maca.ai3.8.0.109-torch2.10-py312-kylinv11-amd64|3.8.0|2026-09-29 20:10:49|ms-swift:4.4.3-maca.ai3.8.0.109-torch2.10-py312-ubuntu22.04-amd64
AI|modelzoo.cnn.inference|29|modelzoo.cnn.inference:1.0.0-maca.ai3.9.0.12-torch2.4-py310-kylinv11-amd64|3.9.0|2026-09-28 16:09:37|modelzoo.cnn.inference:1.0.0-maca.ai3.8.0.10-torch2.4-py310-ubuntu22.04-amd64
AI|paddle|29|paddle:2.6.0-maca.ai3.9.0.10-py312-ubuntu24.04-amd64|3.9.0|2026-09-28 15:46:08|paddle:2.6.0-maca.ai3.8.0.10-py312-ubuntu22.04-amd64
AI|sglang|53|sglang:0.5.14-maca.ai3.8.2.122-torch2.10-py310-kylinv11-amd64|3.8.2|2026-09-23 18:02:20|sglang:0.5.14-maca.ai3.8.2.122-torch2.10-py312-ubuntu22.04-amd64
AI|modelzoo.llm.sglang|28|modelzoo.llm.sglang:1.0.3-maca.ai3.8.2.125-torch2.10-py312-kylinv11-amd64|3.8.2|2026-09-23 18:02:20|modelzoo.llm.sglang:1.0.3-maca.ai3.8.2.125-torch2.10-py312-ubuntu22.04-amd64
AI|vllm-omni-metax|4|vllm-omni-metax:0.26.0-maca.ai3.8.2.0-torch2.10-py312-kylinv11-amd64|3.8.2|2026-09-18 18:04:12|vllm-omni-metax:0.26.0-maca.ai3.8.2.0-torch2.10-py312-ubuntu22.04-amd64
AI|megatron-lm|27|megatron-lm:0.17.0-maca.ai3.7.0.9-torch2.8-py310-kylinv11-amd64|3.7.0|2026-08-07 19:06:10|megatron-lm:0.17.0-maca.ai3.7.0.9-torch2.8-py310-ubuntu22.04-amd64
AI|maca-llm-quantizer|2|maca-llm-quantizer:1.4.0-maca.ai3.7.0.4-torch2.6-py310-ubuntu22.04-amd64|3.7.0|2026-07-13 16:54:16|maca-llm-quantizer:1.4.0-maca.ai3.7.0.4-torch2.6-py310-ubuntu22.04-amd64
AI|deepspeed|27|deepspeed:0.16.5-maca.ai3.7.0.6-torch2.6-py312-ubuntu22.04-amd64|3.7.0|2026-05-09 18:31:10|deepspeed:0.16.5-maca.ai3.7.0.6-torch2.6-py312-ubuntu22.04-amd64
AI|colossalai|24|colossalai:0.5.0-maca.ai3.5.3.15-torch2.4-py310-kylinv11-amd64|3.5.3.x|2026-03-04 16:28:25|colossalai:0.5.0-maca.ai3.5.3.15-torch2.4-py310-ubuntu22.04-amd64
AI|internlm|24|internlm:0.2.1-maca.ai3.5.3.15-torch2.4-py312-kylinv10-arm64|3.5.3.x|2026-03-04 16:28:25|internlm:0.2.1-maca.ai3.5.3.15-torch2.4-py310-ubuntu22.04-amd64
AI|xtuner|19|xtuner:0.2.0-maca.ai3.5.3.15-torch2.6-py312-ubuntu22.04-amd64|3.5.3.x|2026-03-04 16:28:25|xtuner:0.2.0-maca.ai3.5.3.15-torch2.6-py312-ubuntu22.04-amd64
AI|triton-inference-server|6|triton-inference-server:2.64.0-maca.ai3.3.0.301-torch2.8-py310-ubuntu22.04-amd64|3.3.0.x|2026-02-04 18:21:27|triton-inference-server:2.64.0-maca.ai3.3.0.301-torch2.8-py310-ubuntu22.04-amd64
AI|vllm|3|vllm:maca.ai3.1.0.7-torch2.6-py310-ubuntu22.04-amd64|3.1.0.x|2025-09-29 19:22:21|vllm:maca.ai3.1.0.7-torch2.6-py310-ubuntu22.04-amd64
AI4S|monai-maca|2|monai-maca:1.5.2-3.10.1.2-ubuntu24.04-amd64|3.100.0|2026-11-18 16:11:48|
AI4S|neuralgcm-maca|3|neuralgcm-maca:1.2.2-3.10.1.2-ubuntu24.04-amd64|3.100.0|2026-11-18 16:11:48|neuralgcm-maca:1.2.2-3.5.3.6-ubuntu22.04-amd64
AI4S|physicsnemo-maca|4|physicsnemo-maca:2.0.0-3.10.1.2-torch2.8-py312-ubuntu24.04-amd64|3.100.0|2026-11-18 16:11:48|physicsnemo-maca:1.0.1-3.7.0.6-ubuntu22.04-amd64
AI4S|aimodels-maca|3|aimodels-maca:0.7.4-3.10.1.2-torch2.8-py312-ubuntu24.04-amd64|3.100.0|2026-11-18 16:11:48|aimodels-maca:0.7.4-3.5.3.6-ubuntu22.04-amd64
AI4S|pyg_lib-maca|5|pyg_lib-maca:v0.4.0-3.10.1.2-torch2.4-py310-ubuntu22.04-amd64|3.100.0|2026-11-18 16:11:48|pyg_lib-maca:v0.4.0-3.10.1.2-torch2.4-py310-ubuntu22.04-amd64
AI4S|boltz-maca|2|boltz-maca:v2.2.0-3.9.0.12-torch2.8-py312-ubuntu24.04-amd64|3.9.0|2026-09-29 16:32:59|boltz-maca:v2.2.0-3.5.3.6-ubuntu22.04-amd64
AI4S|dgl-maca|1|dgl-maca:2.4-3.9.0.12-ubuntu22.04-amd64|3.9.0|2026-09-29 16:32:59|dgl-maca:2.4-3.9.0.12-ubuntu22.04-amd64
AI4S|warp-maca|2|warp-maca:1.8.1-3.7.0.6-ubuntu22.04-amd64|3.7.0|2026-05-09 18:01:35|warp-maca:1.8.1-3.7.0.6-ubuntu22.04-amd64
AI4S|deepxde-pytorch-maca|2|deepxde-pytorch-maca:v1.14.0-3.7.0.6-ubuntu24.04-amd64|3.7.0|2026-05-09 18:01:35|
AI4S|deepxde-paddle-maca|2|deepxde-paddle-maca:v1.14.0-3.7.0.6-ubuntu22.04-amd64|3.7.0|2026-05-09 18:01:35|deepxde-paddle-maca:v1.14.0-3.7.0.6-ubuntu22.04-amd64
AI4S|diffdock-maca|2|diffdock-maca:v1.1.3-3.7.0.6-torch2.4-py310-ubuntu22.04-amd64|3.7.0|2026-05-09 18:01:35|diffdock-maca:v1.1.3-3.7.0.6-torch2.4-py310-ubuntu22.04-amd64
Cloud-Tools|operator-bundle|1|operator-bundle:0.16.2||2026-11-06 17:25:18|
Cloud-Tools|operator-catalog|1|operator-catalog:0.16.2||2026-11-06 17:25:18|
Cloud-Tools|operator-controller|3|operator-controller:0.16.2||2026-11-02 14:55:43|
Cloud-Tools|gpu-scheduler|3|gpu-scheduler:0.16.2||2026-11-02 14:55:43|
Cloud-Tools|gpu-device|3|gpu-device:0.16.2-amd64||2026-11-02 14:55:43|
Cloud-Tools|vc-webhook-manager|6|vc-webhook-manager:0.16.2-vc.v1.9.0-arm64||2026-11-02 14:55:43|
Cloud-Tools|container-runtime|3|container-runtime:0.16.2-arm64||2026-11-02 14:55:43|
Cloud-Tools|dlrover-master|3|dlrover-master:0.16.2||2026-11-02 14:55:43|
Cloud-Tools|vc-scheduler|6|vc-scheduler:0.16.2-vc.v1.9.0||2026-11-02 14:55:43|
Cloud-Tools|gpu-aware|3|gpu-aware:0.16.2-amd64||2026-11-02 14:55:43|
Cloud-Tools|elasticjob-controller|3|elasticjob-controller:0.16.2-arm64||2026-11-02 14:55:43|
Cloud-Tools|driver-manager|3|driver-manager:0.16.2-arm64||2026-11-02 14:55:43|
Cloud-Tools|vc-controller-manager|6|vc-controller-manager:0.16.2-vc.v1.9.0||2026-11-02 14:55:43|
Cloud-Tools|topo-master|3|topo-master:0.16.2||2026-11-02 14:55:43|
Cloud-Tools|gpu-label|3|gpu-label:0.16.2-amd64||2026-11-02 14:55:43|
Cloud-Tools|mx-exporter|3|mx-exporter:0.16.2-amd64||2026-11-02 14:55:43|
Cloud-Tools|topo-worker|3|topo-worker:0.16.2-arm64||2026-11-02 14:55:43|
Cloud-Tools|controller-exporter|3|controller-exporter:0.16.2-amd64||2026-11-02 14:55:43|
Cloud-Tools|metax-operator|1|metax-operator:latest|3.9.0|2026-11-02 14:55:43|
Cloud-Tools|driver-image|3|driver-image:latest-arm64||2026-10-20 17:45:54|"""

PURPOSES = {
    "maca": "基础 SDK 开发与运行环境", "maca-native": "保留的 maca-native 基础镜像分支；与 maca 的具体差异待查配套说明",
    "mmcv": "OpenMMLab 视觉基础库", "diffusers.training": "扩散模型训练与 LoRA 微调",
    "onnxruntime": "传统 CNN / Transformer 的 ONNX 推理环境", "modelzoo.llm.transformers": "Transformers 推理评测样例",
    "tensorflow2": "TensorFlow 训练与 XLA 环境", "paddle-metax": "Paddle 新分支及 MetaX 后端",
    "cv-cuda": "视觉预处理与图像/视频流水线", "modelzoo.cnn.training": "经典视觉模型训练与评测",
    "modelzoo.llm.diffusers": "图像生成模型推理评测", "slime": "面向 SGLang 的分布式后训练",
    "maca-pytorch": "PyTorch 通用计算与训练环境", "vllm-metax": "vLLM 插件式 MetaX 推理服务",
    "modelzoo.llm.vllm": "vLLM 模型配置、推理与性能/精度评测", "verl": "分布式强化学习后训练",
    "diffsynth-studio": "多模态与视频生成模型训练", "ms-swift": "SFT、LoRA 与强化学习后训练",
    "modelzoo.cnn.inference": "ONNX 视觉/NLP 模型推理与精度评测", "paddle": "Paddle 2.6 及更早的保留分支",
    "sglang": "LLM 推理服务", "modelzoo.llm.sglang": "SGLang 模型配置与评测",
    "vllm-omni-metax": "多模态、多阶段模型推理", "megatron-lm": "分布式预训练",
    "maca-llm-quantizer": "大模型量化及推理部署前处理", "deepspeed": "分布式训练与微调",
    "colossalai": "大模型分布式训练", "internlm": "InternLM 系列训练环境", "xtuner": "全参及 LoRA 微调",
    "triton-inference-server": "多模型推理服务管理；区别于 mcTriton 算子编程", "vllm": "vLLM 0.10.0 及更早的保留分支",
    "monai-maca": "医学影像模型开发", "neuralgcm-maca": "神经网络与物理结合的气候模拟",
    "physicsnemo-maca": "物理 AI 与科学计算", "aimodels-maca": "AI 天气模型集合",
    "pyg_lib-maca": "图神经网络基础组件", "boltz-maca": "生物分子建模与药物研究",
    "dgl-maca": "DGL 图神经网络", "warp-maca": "Python 数值模拟与 JIT",
    "deepxde-pytorch-maca": "基于 PyTorch 的物理信息网络/微分方程求解", "deepxde-paddle-maca": "基于 Paddle 的物理信息网络/微分方程求解",
    "diffdock-maca": "分子对接模型",
    "operator-bundle": "Operator OLM Bundle", "operator-catalog": "Operator OLM Catalog",
    "operator-controller": "GPU Operator 控制器", "gpu-scheduler": "GPU/sGPU 拓扑感知调度",
    "gpu-device": "GPU 设备资源上报", "vc-webhook-manager": "Volcano Webhook",
    "container-runtime": "MetaX 容器运行时", "dlrover-master": "DLRover 任务主控",
    "vc-scheduler": "Volcano 调度", "gpu-aware": "GPU 拓扑感知", "elasticjob-controller": "DLRover 弹性任务控制",
    "driver-manager": "节点 Driver/SDK 管理", "vc-controller-manager": "Volcano 控制器",
    "topo-master": "集群拓扑管理", "gpu-label": "节点 GPU 信息发现", "mx-exporter": "GPU 监控指标导出",
    "topo-worker": "节点拓扑采集", "controller-exporter": "Operator 管理驱动时的配套组件",
    "metax-operator": "GPU Operator Helm Chart（不是 Docker 镜像）", "driver-image": "内核驱动负载镜像",
}

PACKAGE_GROUPS = [
    ("Driver", "基础环境", "download?package_kind=Driver&dimension=metax&deliver_type=分层包", ["Driver"]),
    ("SDK", "基础环境", "sdk?package_kind=SDK&dimension=metax&deliver_type=分层包", ["SDK", "SDK-Python", "MXRDMA"]),
    ("AI", "训练框架", "ai-download?package_kind=AI&dimension=metax&deliver_type=分层包", ["ColossalAI", "DeepSpeed", "Diffusers.Training", "InternLM", "Megatron LM", "Paddle【2.6.0版本及以下】", "Paddle【3.3.0版本及以上】", "Pytorch", "TensorFlow2", "XTuner", "Verl", "ms-swift", "JAX", "DiffSynth-Studio", "Slime"]),
    ("AI", "推理框架", "ai-download?package_kind=AI&dimension=metax&deliver_type=分层包", ["ONNXRuntime", "Triton-Inference-Server", "vLLM【0.10.0版本及以下】", "vLLM【0.10.2版本及以上】", "SGLANG", "IREE"]),
    ("AI", "工具库", "ai-download?package_kind=AI&dimension=metax&deliver_type=分层包", ["BitsAndBytes", "CV-CUDA", "MMCV", "Ray【2.46.0版本及以下】", "Ray【2.48.0版本及以上】", "mcoplib", "transformerengine", "mooncake", "LMCache", "DeepGEMM", "liger-kernel"]),
    ("AI", "ModelZoo", "ai-download?package_kind=AI&dimension=metax&deliver_type=分层包", ["Modelzoo.CNN.Inference", "Modelzoo.llm.SGLang", "Modelzoo.CNN.Training", "Modelzoo.LLM.Diffusers", "Modelzoo.LLM.Transformers", "Modelzoo.LLM.vLLM"]),
    ("AI4S", "基础库", "ai4science?package_kind=AI4S&dimension=metax&deliver_type=分层包", ["PhysicsNeMo", "PyG", "Warp"]),
    ("Tools", "科学计算加速工具包", "tools?package_kind=Tools&dimension=metax&deliver_type=分层包", ["mcpy", "mcdf", "mcfaiss", "mcvs"]),
    ("Tools", "GPU集群管理工具", "tools?package_kind=Tools&dimension=metax&deliver_type=分层包", ["mxdcm"]),
    ("Tools", "云平台工具", "tools?package_kind=Tools&dimension=metax&deliver_type=分层包", ["device-plugin-source", "dlrover", "kubectl-plugins", "metax-arena", "metax-docker", "metax-gpu-k8s", "metax-gpu-k8s-package-base", "metax-gpu-openshift", "metax-gpu-scheduler", "metax-k8s-driver-image", "mx-exporter", "mxkind", "volcano"]),
    ("Tools", "Perf工具", "tools?package_kind=Tools&dimension=metax&deliver_type=分层包", ["linux-perf-kit", "mac-perf-kit", "win-perf-kit"]),
    ("DSL", "编译器", "dsl?package_kind=dsl&dimension=metax&deliver_type=分层包", ["TileLang"]),
]


def parse_tag(tag):
    def match(pattern):
        found = re.search(pattern, tag)
        return found[1] if found else None
    py = match(r"-py(\d+)(?:-|$)")
    return {"image_name_and_tag": tag,
            "package_version_prefix": tag.split(":", 1)[1].split("-")[0],
            "torch_from_tag": match(r"-torch([\d.]+)(?:-|$)"),
            "python_from_tag": py[0] + "." + py[1:] if py else None,
            "os_from_tag": match(r"-(ubuntu[\d.]+|kylinv\d+|kylin\d+[a-z]?|centos\d+|rocky\d+)(?:-|$)"),
            "architecture_from_tag": match(r"-(amd64|arm64)$"),
            "uses_mutable_latest_tag": ":latest" in tag,
            "registry": None, "digest": None, "pull_tested": False}


def main():
    images = []
    for line in OBSERVATIONS.splitlines():
        category, family, count, tag, driver, updated, ubuntu = line.split("|")
        source = BASE + "docker?" + urlencode({"chip_name": "MXC500", "package_kind": category, "dimension": "docker", "deliver_type": "分层包"})
        item = {"category": category, "family": family, "artifact_kind": "helm_chart" if family == "metax-operator" else "container_image",
                "purpose": PURPOSES[family], "observed_distinct_cards": int(count),
                "representative": parse_tag(tag) | {"recommended_driver": driver or None, "website_updated_at": updated},
                "ubuntu22_amd64_example": parse_tag(ubuntu) if ubuntu else None,
                "source_url": source, "source_filter": "MXC500; all architectures/OS/Python; normal release catalogue",
                "verification": "public_listing_observed_not_downloaded_or_run"}
        images.append(item)
    packages = [{"category": cat, "group": group, "name": name, "source_url": BASE + path,
                 "observed_section": "MXC500" if cat not in ("SDK", "Driver") else "category_entry; SDK detail separately filtered to MXC500",
                 "verification": "directory_entry_observed; individual package versions not exhaustively opened"}
                for cat, group, path, names in PACKAGE_GROUPS for name in names]
    metadata = {"observed_on": "2026-11-21", "timezone": "Asia/Shanghai", "chip_filter": "MXC500",
                "scope": "public family-level catalogue plus representative tags; not exhaustive registry/history export",
                "server_validation": "not performed; no remote changes, downloads, pulls or installs",
                "image_family_count": len(images), "package_directory_entry_count": len(packages),
                "scan_observations": {"MXMACA": {"cards": 14, "families": 2}, "AI": {"pages": 9, "page_size": 100, "cards_read": 815, "unique_tags_observed": 711, "families": 29}, "AI4S": {"cards": 28, "families": 11}, "Cloud-Tools": {"cards": 63, "families": 20, "includes_helm_chart": True}},
                "limitations": ["AI pagination showed repeated tags and ordering changes; observed counts are not authoritative site totals.",
                                "Historical-version dropdowns, archive and preview catalogues were not exhaustively expanded.",
                                "Copying a Docker pull command redirected to login; registry prefixes were not guessed.",
                                "Ubuntu 22 examples are alternatives and may be older; the representative driver's recommendation must not be applied to them.",
                                "The family catalogue saves representative observations, not every scanned tag or full raw page text.",
                                "The SDK compatible-resources button returned HTTP 500; a full paired-resource BOM was not obtained.",
                                "Signed download URLs were not stored; stable source pages are provided instead."]}
    for filename, data in [("images.json", {**metadata, "families": images}), ("software_packages.json", {"observed_on": metadata["observed_on"], "entries": packages}), ("coverage.json", metadata)]:
        (ROOT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# MXC500 镜像与 Chart 家族清单", "", "采集日期：2026-11-21（Asia/Shanghai）。[结论与文档交叉核对](README.md) · [结构化数据](images.json)", "",
             "共 62 个家族，其中 61 个容器镜像家族、1 个 Helm Chart 家族。以下为本次浏览所见的近期样例，不表示所有历史版本，也不表示在目标服务器实测通过。",
             "", "Driver 列为同一行样例卡片的“推荐安装”值，不是最低兼容值。未标注保持未知。名称:tag 未包含仓库前缀，不可直接当作完整 docker pull 地址。", ""]
    for category in ("MXMACA", "AI", "AI4S", "Cloud-Tools"):
        rows = [r for r in images if r["category"] == category]
        lines += [f"## {category}（{len(rows)} 个家族）", "", f"来源：[MXC500 / {category}]({rows[0]['source_url']})；所有条目均为官网列出、未实测。", "",
                  "| 家族 / 用途 | 本次观察的近期样例名称:tag | 推荐 Driver | 页面更新时间 |", "|---|---|---|---|"]
        for r in rows:
            e = r["representative"]
            lines.append(f"| **{r['family']}**<br>{r['purpose']} | `{e['image_name_and_tag']}` | {e['recommended_driver'] or '未标注'} | {e['website_updated_at']} |")
        lines.append("")
    lines += ["## Ubuntu 22.04 / amd64 备选样例", "", "这部分便于按常见容器系统筛选，不代表服务器宿主 OS 已核实。样例可能比上表旧；必须重新查看它自身的推荐 Driver 和配套要求。未列出不代表不存在。", "",
              "| 家族 | 观察到的备选名称:tag |", "|---|---|"]
    lines += [f"| {r['family']} | `{r['ubuntu22_amd64_example']['image_name_and_tag']}` |" for r in images if r["ubuntu22_amd64_example"]]
    (ROOT / "IMAGE_CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    lines = ["# MXC500 软件安装包目录", "", "采集日期：2026-11-21。共 67 个分类目录条目（分支分开计数）；与镜像家族存在重叠，不能相加为独立软件总数。", "",
             "这里只确认官网目录列出。SDK、TileLang 和 linux-perf-kit 的具体包版本另见[盘点报告](README.md)。其余没有逐项验证包版本、下载权限或运行结果。", ""]
    for cat, group, path, names in PACKAGE_GROUPS:
        lines += [f"## {cat} / {group}", "", f"[官方入口]({BASE + path})；进入后选择 MXC500。", "", "、".join(f"`{name}`" for name in names), ""]
    (ROOT / "SOFTWARE_PACKAGES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(images)} family records and {len(packages)} software directory entries.")


if __name__ == "__main__":
    main()
