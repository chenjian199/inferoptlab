# 第一阶段测试模块

`benchmark/` 现在是三个并列测试模块，配置与数据继续分别放在 `recipes/`、`experiments/`。

```text
benchmark/
  load/                  # AIPerf 服务压测、并发/参数扫描、P/D 缓存流程
    adapters/            # AIPerf、SGLang、vLLM、MetaX 环境适配
    metrics/             # 客户端指标、SLA 和报告
  accuracy/              # 功能回归、数值验收协议、历史输出离线核验
  breakdown/             # E2E/模块/kernel 拆分与规范化 trace 汇总
    operators/           # 算子捕获/重放契约与资格检查
  common/                # 文件/路径、进程管理、离线报告公共契约
  cli.py                 # 统一命令分发
```

| 模块 | 回答的问题 | 当前可执行能力 |
|---|---|---|
| [load](load/README.md) | 指定配置和负载下，服务吞吐、TTFT、TPOT、失败率如何？ | 已有 AIPerf 编排、数据准备、P/D 流程和结果复算 |
| [accuracy](accuracy/README.md) | 功能是否退化，数值和状态是否仍符合契约？ | 协议展开、历史 HumanEval 逐题核验、三对三功能比较；生成/沙箱/数值采集适配待接入 |
| [breakdown](breakdown/README.md) | 时间花在哪里，哪些模块/算子值得单独测？ | 分层采集与算子重放规划、重叠感知 trace 汇总；原生 profiler/GPU 重放适配待接入 |

## 统一入口

```powershell
python -m benchmark load plan recipes/plans/benchmark/glm53-flash-decode.yaml
python -m benchmark accuracy plan recipes/plans/accuracy/glm53-humaneval-full164.yaml --out experiments/runs/accuracy/new-plan.yaml
python -m benchmark breakdown plan recipes/plans/breakdown/glm53-c500.yaml --out experiments/runs/breakdown/new-plan.yaml
```

命令必须显式选择 `load`、`accuracy` 或 `breakdown`。根目录参数放在模块后，例如 `python -m benchmark load --root <根目录> plan ...`。Python 导入使用 `benchmark.load.*`、`benchmark.accuracy.*`、`benchmark.breakdown.*` 和 `benchmark.common.*`。各模块也可通过 `python -m benchmark.load` 等独立入口执行。

模块在结构上并列，不代表在同一组 GPU 上同时压测、采集 profiler 和运行精度评测。性能运行保持无诊断 hook；带 profiler 或影子数值校验的数据另行归档。

## 与第二、三步的边界

第一步的三个模块负责测量、准备测量和核验原始结果。`diagnosis/` 使用证据做归因，`analysis/` 选择专项方法并规划控制实验。规范化 trace 汇总由 `benchmark/breakdown/trace.py` 实现，通过 `python -m benchmark breakdown trace ...` 执行。

本次从 [C500 资料库](../catalog/library/metax/README.md) 提炼方法。历史资料未修改，尚未接入的执行器明确输出 `awaiting_evidence`，不会生成虚构测量或接纳结论。
