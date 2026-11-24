# HumanEval v1 复现与证据

这份说明记录本轮实际执行路径。历史结果不可覆盖；`runs/_template/` 与 [configs/thresholds.json](../../../../experiments/evidence/metax/glm53/baseline_ops/configs/thresholds.json) 仍是后续性能/算子工作的模板，不属于本轮精度结果。

## 固定输入与执行身份

- 数据：`openai/openai_humaneval`，test，revision `7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544`；164 题，smoke32 ID 清单见 [datasets/humaneval/manifest.json](../../../../experiments/datasets/humaneval/manifest.json)。
- 远程实验根目录：`/home/metax/glm53-baseline-ops`；新容器：`glm53-heval-v1`；运行 label：`20261123_humaneval_v1`。
- 推理镜像 ID：`sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`。完整创建参数见 [evidence/humaneval_v1/create_container.json](../../../../experiments/evidence/metax/glm53/baseline_ops/evidence/humaneval_v1/create_container.json)。
- 源码恢复自 `/home/metax/glm53-vllm032/baseline/sources-20261122.tar.gz`，SHA256 `da769ed300e32876f2bd358a1c537a8618f7fdbc8f56830eacfec57f6d1ab592`；使用新目录的只读源码挂载、独立缓存。
- 历史执行脚本归档：`evidence/humaneval_v1/harness-executed/`；环境实际导入路径和依赖版本见 `frozen_baseline_check.json`，八卡模型状态见 `generation_environment.json`。
- [configs/humaneval_regression.frozen.json](../../../../experiments/evidence/metax/glm53/baseline_ops/configs/humaneval_regression.frozen.json) 是全量开始前的冻结记录；内含原始 pilot 配置、实际模板与脚本哈希和评分限制。不要将其内嵌历史草案的 null 值当作已解析参数；以冻结包的顶层字段及运行清单为准。

## 已执行的生成与评分入口

下列是远程 Linux 主机上的实际命令结构，仅用于说明本轮运行。已有结果目录、进程日志不允许复用。主机 launcher 持有 `/home/metax/.glm53-c500-tp8.lock`；不要绕过锁并发启动第二个 TP8 实验。

```sh
python3 -u /home/metax/glm53-baseline-ops/harness/run_generation_host.py

python3 -u /home/metax/glm53-baseline-ops/harness/evaluate_humaneval.py \
  --run /home/metax/glm53-baseline-ops/runs/canonical_v1 --canonical --selftest

python3 -u /home/metax/glm53-baseline-ops/harness/evaluate_humaneval.py \
  --run /home/metax/glm53-baseline-ops/runs/20261123_humaneval_v1_smoke32

python3 -u /home/metax/glm53-baseline-ops/harness/evaluate_humaneval.py \
  --run /home/metax/glm53-baseline-ops/runs/20261123_humaneval_v1_full164
```

顺序为：环境检查 → 模型载入 → smoke32 生成 → canonical 全通过及 sandbox 自检、smoke32 评分完成 → 固定协议与 gate → 同一引擎 full164 生成 → full164 隔离评分。canonical 评分可以在生成阶段独立运行。gate 保存于 `evidence/authorize_full_20261123_humaneval_v1.json`，不是“全部题必须通过”的门槛。

生成容器只获得 prompts 和 task IDs；`scoring/scoring.jsonl` 留在主机。每道题的提交代码与原始测试通过 stdin 发给新的 CPU 沙箱。沙箱无网络、无 bind mount、无 GPU，UID/GID 65534，根文件系统只读，1 CPU/512 MiB/32 PID，单题 CPU 8 秒、wall 10 秒、容器外层 45 秒。评分 Python 使用 `-I -S`，仅标准库。本地协议不等同于官方 leaderboard harness。

本轮曾因推理容器 root 创建结果目录，导致主机评分器无法新建文件；只调整这两个新 run 目录自身的 UID/GID 为 metax，未递归变更部署目录。首次失败日志保留在远程，调整证据为 `output_ownership_fix.json`。重试的是尚未执行的评分阶段，不是模型生成。

## 本地只读核验与汇总

在项目根目录用现有 Python 运行：

```powershell
python -B -m unittest discover -s glmf/baseline_ops/harness -p 'test_*.py'
python -B glmf/baseline_ops/harness/verify_baseline.py
python -B glmf/baseline_ops/harness/summarize_baseline.py `
  --full glmf/baseline_ops/runs/20261123_humaneval_v1_full164 `
  --smoke glmf/baseline_ops/runs/20261123_humaneval_v1_smoke32 `
  --output glmf/baseline_ops/baseline_summary.recomputed.json
```

汇总命令拒绝覆盖 output，第二次重算请换新的输出文件名。验证和汇总都不会执行模型生成的代码，也不会连接远程服务器。

## 下一轮回归

先将本轮 evidence/configs/runs/data 与执行源码作为不可变基线归档，保留 SHA256 清单。新实验使用新根目录、新容器和新 label；当前历史 launcher 固定了路径与 label，须在新副本中参数化后才能复用。新的 launcher 应在启动前验证冻结输入/脚本哈希并拒绝覆盖证据，配置解析以已填实测值的冻结协议为准。

保持题集、原始测试、提示模板、tokenizer、采样和评分资源限制一致。比较逐题的 B0 对→候选错、B0 错→候选对以及 token/logits 差异，不能仅凭总通过率不变判断没有退化。32 题与全量中的重叠题使用同一已载入引擎，无法替代独立进程重复性验证。整模型固定长度性能基线、数值/logits 基线和算子替换验证仍需单独实施。
