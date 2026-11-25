# GLM-5.3-Flash-W8A8 / C500 扫描准备验证

在 metax-60（172.17.0.60）实际启动并验证 12 个配置。启动/API 资格通过 11 项，未通过 1 项。该记录覆盖启动资格和小规模压测流程；尚未执行完整性能扫描，也不代表精度或正式 SLA 验收。

## 启动与配置验证

| 配置 | TP / PP / DP / EP | 最大上下文 | token 预算 | 每 DP 序列上限 | 实际 KV block | 结果 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| glm53-vllm-a-tp8 | 8 / 1 / 1 / 1 | 32768 | 4096 | 128 | 640 | passed |
| glm53-vllm-b-tp8-ep8 | 8 / 1 / 1 / 8 | 32768 | 4096 | 128 | 640 | passed |
| glm53-vllm-c-tp4-dp2-ep8 | 4 / 1 / 2 / 8 | 32768 | 4096 | 64 | 1152 | passed |
| glm53-vllm-d-tp2-dp4-ep8 | 2 / 1 / 4 / 8 | 32768 | 4096 | 32 | 2176 | passed |
| glm53-vllm-a-budget2048 | 8 / 1 / 1 / 1 | 32768 | 2048 | 128 | 640 | passed |
| glm53-vllm-a-budget8192 | 8 / 1 / 1 / 1 | 32768 | 8192 | 128 | 640 | passed |
| glm53-vllm-a-seqs64 | 8 / 1 / 1 / 1 | 32768 | 4096 | 64 | 640 | passed |
| glm53-vllm-a-seqs256 | 8 / 1 / 1 / 1 | 32768 | 4096 | 256 | 640 | passed |
| glm53-vllm-a-graph | 8 / 1 / 1 / 1 | 32768 | 4096 | 128 | 640 | passed |
| glm53-vllm-a-context64k | 8 / 1 / 1 / 1 | 73728 | 4096 | 128 | 640 | passed |
| glm53-vllm-a-context128k | 8 / 1 / 1 / 1 | 147456 | 4096 | 128 | 640 | passed |
| glm53-vllm-a-cache | 8 / 1 / 1 / 1 | 32768 | 4096 | 128 | 640 | failed |

所有候选均完成服务配置回读和精确输入探测：128→32，以及各阶段最大输入长度→1。64K、128K 分别为 65536、131072 个实际输入 token。吞吐和延迟不由启动耗时推算。

图执行候选实际启用 Breakable CUDA Graph，`cudagraph_mode=[2,1]`，捕获尺寸覆盖 1—256；`torch.compile` 的 mode 仍为 0。不同并行形态的 KV block 由后端自动选择，实际值如表所示。

## 缓存 Decode 的实际边界

缓存候选的服务启动、配置核对和响应长度均正常，但相同 4096-token 输入重放只命中 3840 token（93.75%），剩余 256 token。它不满足本协议要求的 100% 命中且未命中=0，因此资格状态为 failed，04-cache 不能进入正式压测。

[原始缓存响应](startup-r2/04-cache/glm53-vllm-a-cache/cache-replay.json)保留服务返回的 usage。不能降低阈值后仍称为同一个纯 Decode 协议；后续需要验证混合注意力状态缓存/请求尾部处理，或另外定义明确允许残余 Prefill 的缓存请求协议。

## AIPerf 流程验证

| Run | 并发 | 请求数 | 成功 / 失败 / 缺失 | 状态 | 指标完整性 |
| --- | ---: | ---: | --- | --- | --- |
| run-d1822b2123064f45 | 1 | 4 | 4 / 0 / 0 | completed | valid |
| run-45fb66a83a5e4efe | 2 | 8 | 8 / 0 / 0 | completed | valid |

请求长度为 128→32；C=1、2 分别发送 N=4、8 个计时请求，每点另有 4 个独立预热请求。复用现有 prepare、run、指标归一化、SLA 评估和 ExperimentRecord 登记，没有另建结果格式。原始 AIPerf 导出、逐请求记录、服务指标、实际命令、环境、数据集和解析后的规约快照均保留在各批次中。

- 批次 `batch-20261124T120300Z-b51b3daf`：`completed`；仓库相对路径 `experiments/runs/benchmark/batch-20261124T120300Z-b51b3daf`。

首次控制进程在测量完成后的自动登记环节退出：临时远端工作副本漏传了现有登记器所依赖的 diagnosis 模块。补齐完整项目模块后，使用 tools.experiments register 对同一批次离线复算并成功登记；没有重跑 GPU 或修改原始测量。原始 pipeline-smoke.log、退出状态和 registration-recovery.json 均保留。

这 12 个计时请求用于检查流程，不用于推断 P95/P99 稳定性或选定性能最优参数。05—07 全量复测尚未执行。

## 证据与恢复

- `startup-r2/`：本轮最终资格记录、配置回读、设备身份、API 响应和服务日志。
- `startup/` 与 `controller/`：早期控制端依赖和端口 TIME_WAIT 问题的失败尝试；已修复后重试，不把这些归类为模型/硬件不支持。
- `startup-r2/00-layout/resolved.yaml`：根据原始输入恢复，其 canonical SHA-256 与原始资格记录完全一致，恢复说明另存于 snapshot-recovery.json；其余阶段在执行时直接保存快照。
- `execution-source.tar.gz`：验证结束时的代码、规约副本；阶段实际配置以各阶段 resolved.yaml 为准。`execution-source-manifest.json` 与 `import-manifest.json` 保存文件摘要。
- `control-environment.json`、`client-preflight.json`：独立控制端依赖与 AIPerf 0.12 客户端检查。
- `summary.json`：机器可读汇总；详细资格与运行记录保持各自的内容哈希。
- 已恢复 `inferoptlab-glm53-vllm-r1`，18081 `/health` 返回 200；本次拥有的测试容器已清理。见 `restoration.json`。

本地回归：134 项测试（133 项通过、1 项跳过），392 份规约通过结构、引用及语义校验。两组原始结果在本地重算均为 valid，按项目现有 1e-12 浮点容差与原记录一致；实验索引无错误，新来源文件哈希已核对。详见 `local-verification.json`。

本轮沿用行业 GLM-5.3 的优化约束作为 Flash 诊断参考，模型差异、统计口径及原始附件缺口仍然保留。C500 专用 MoE 调优文件缺失、权重完整性与精度验收也没有因启动成功而自动完成。
