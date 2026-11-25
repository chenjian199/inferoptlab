# metax-60 GLM 源码镜像与流程验证证据

说明与复现命令见[报告](../../../../docs/metax-60-glm53-vllm-source-build-20261124.md)。本目录不包含镜像层、SDK 安装包或模型权重。

- `qualification.json`：本次成功验证汇总，对应 `recipes/sources/source-metax60-glm53-source-build.yaml`。
- `version-selection.json`：上游与 MetaX 版本选择及未发布依赖限制。
- `Dockerfile`：远端实际构建文件。
- `evidence/image*.json`、`evidence/image-build/`：镜像身份、导入路径、构建依赖锁、补丁和 SDK 安装记录。
- `evidence/sources.json`、`evidence/dependencies.json`：下载来源与哈希。
- `evidence/gpu8/` 和三份算子检查 JSON：实际 GPU/通信/算子验证。
- `evidence/service-reasoning/`、`evidence/server-config-reasoning.json`：最终服务启动参数、实际配置和日志。
- `evidence/api-reasoning/`：成功的最终答案检查；`evidence/api/` 为首次失败记录。
- `client/`：成功 AIPerf 三组场景，每组包含独立预热、四个正式请求、数据集、命令、日志和原始导出。
- `client-attempt0/`、`client-attempt1/`：客户端离线 tokenizer 路径解析失败，尚未发送测试请求。
- `evidence/client-project-manifest.json`：执行时客户端项目源码 SHA-256 清单。
- `evidence/final-state.json`：交付时服务健康状态、容器清单、GPU 和磁盘状态。
- `logs/`：构建与验证日志，包含失败或中止的早期尝试。
- `manifest.json`：归档文件哈希与大小，不包含自身。

三组成功请求均为并发 1、正式请求数 4，不能作为 p99、并发扩展性、纯 decode 或正式精度结论。最终服务容器名为 `inferoptlab-glm53-vllm-r1`；不带 `-r1` 的记录对应首次启动。
