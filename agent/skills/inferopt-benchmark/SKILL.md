---
name: inferopt-benchmark
description: 在 InferOptLab 项目中准备或运行第一阶段 AIPerf benchmark，核对模型、硬件、场景、协议和部署配方，归档可复算的请求及环境证据。
---

先读 [共同约束](../../README.md)，再按任务阅读 [benchmark 入口](../../../benchmark/README.md)。硬件采集任务另读 [硬件工具](../../../tools/hardware/README.md)。以这些文件所在仓库为项目根目录运行命令。

1. 从现有 `schemas/recipes/`、`benchmark/recipes/`、`benchmark/scenarios/` 和计划选择真实模型变体、设备、runtime 与短/长场景，核对路径、量化、tokenizer 和协议；缺失值保持未确认。
2. 用 `python tools/specs.py validate` 和 `python -m benchmark plan <计划路径>` 做本地检查，区分流程资格测试与正式 SLA 测量。
3. 需要真机执行时先核对当前用户授权、设备身份/占用、服务归属、预算和恢复方法。项目机器约束见共同文档；已授权任务按范围推进。
4. 按 benchmark README 的实际命令执行与归档，保留启动参数、环境、原始请求、失败/超时、预热、测量及清理记录。没有可用执行器时报告能力缺口，不临时声称支持。
5. 终态批次可用 `python -m diagnosis seal <批次目录> --out <新清单路径>` 封存；把目录、清单摘要和运行有效性交给下一阶段。

不要把 SSE chunk 间隔称为 token ITL；单输出 token 的 TPOT 不可测。模型文件与镜像存在只能证明清单就绪，不能证明 loader、设备运行或性能达标。硬件校准仅用于其设备/runtime/shape 范围。
