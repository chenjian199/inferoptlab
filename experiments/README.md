# 实验数据与基线

这里是四个阶段共用的数据仓储。实现代码留在 `benchmark/`、`diagnosis/`、`analysis/`、`optimization/`，可编辑配置放在根目录 `recipes/`；每次运行保存当时完整配置，后续修改配方不会改变已有结果的含义。

```text
experiments/
  datasets/                   # 新计划使用的请求集和 tokenizer/输入内容指纹
  runs/
    benchmark/<batch-id>/      # 完整快照、数据集副本、各 Run、原生输出和日志
    accuracy/                 # 精度准备、历史审计和功能比较
    breakdown/                # 分层采集准备、算子契约检查、trace 汇总
    hardware/                 # 硬件探测与微基准
    diagnosis/                # 第二步结果
    analysis/                 # 第三步结果
    optimization/             # 第四步交接
  evidence/                   # 原始资料、机器采集和已封存历史运行
  records/<run-id>.yaml        # 不可覆盖的 ExperimentRecord
  baselines/<name>.yaml        # 不可覆盖的 BaselineRecord
  index.json                  # 可重建查询索引，不是原始证据
  layout-migration.json       # 本次目录迁移、文件数量与字节保真校验标记
```

## 一份结果对应什么

`ExperimentRecord` 持有模型、硬件、Runtime、部署引用，P/D/E2E 方法，并发、重复轮次、运行状态，以及完整依赖闭包 `recipe_snapshot`、本次展开配置 `run_configuration`、设备与服务配置回读、实际命令数组、MeasurementBundle、SLA 判定和制品清单。请求数已展开成该并发点的确切值。

记录中的 `artifacts` 钉住完整快照、Run 文件和数据集的 SHA-256。登记时复算原生请求指标与缓存填充/重放证据，查询时核对记录摘要、关键字段和所有制品哈希。制品被改动或缺失时，从有效查询结果排除，并在 `errors` 中显示原因；不能通过刷新索引抹掉问题。

执行正常收尾后自动登记；有结果的失败 Run 同样可查。启动前失败或被预算跳过的试验保留在批次 `batch.json` 中，没有伪造的 Run/测量记录。异常导致未登记时可在问题处理后手动登记终态批次。

## 查询与历史登记

在仓库根目录运行：

```powershell
# 重建本地索引并查看完整性问题
python -m tools.experiments index

# 按模型、硬件、阶段和状态组合过滤
python -m tools.experiments query --model cluster-glm53-flash-w8a8 --phase decode --status completed
python -m tools.experiments query --hardware metax-four-node-inventory-metax-60-host
python -m tools.experiments query --module accuracy
python -m tools.experiments query --module breakdown

# 旧批次也可以登记；重复登记相同内容是幂等的
python -m tools.experiments register experiments/evidence/benchmark-qualification/20261123/project/runs/benchmark/batch-20261123T085945Z-ccf82622
```

查询返回 `runs`、`sources`、`baselines` 和 `errors`。`sources.integrity` 区分 `verified/missing/changed`；来源文档与历史报告属于来源数据，不会自动转成独立实测 Run。当前实现是可复建的本地结构化索引；还没有向量检索、自然语言检索或跨机器集中数据库。第二至四步报告目前通过 `runs/` 与证据引用保存，尚未全部转换成逐 Run 查询对象。

新增 `offline_reports` 索引精度/拆分模块的 `BenchmarkOfflineReport`，检查内容摘要、嵌入配置与原始制品哈希；查询可用 `--module`。这些报告始终保持 `new_gpu_execution: false`、`release_accepted: false`，不会混入性能 Run 或成为实测性能基线。规范化 TraceSummary 仍按文件保存。

## 基线

```powershell
python -m tools.experiments baseline my-workflow-baseline --runs <run-id> --purpose workflow --note "小模型流程资格验证"
python -m tools.experiments baseline glm53-decode-baseline-v1 --runs <run-id-1> <run-id-2> --purpose performance --note "固定模型、部署和协议下的正式性能基线"
```

两类基线都要求独立实测、执行完成、指标有效、零失败；同一标签的记录须来自相同模型、硬件、Runtime、部署。`performance` 额外要求冻结输入与性能 SLA 通过。基线标签保留选定 Run 和记录哈希，禁止同名覆盖，不会默认取最好的一轮。正式基线的稳定性和质量验收仍需独立证据，标签不等于完整 Study 验收。

历史 Qwen 只有小样本流程验证，应使用 `workflow`。GLM 新计划是候选配置，目前不能登记为已测性能基线。

## 迁移与保存

运行器、配方与报告直接使用当前仓库路径，不再提供历史路径重定向。原始测量数据保留观测事实；布局调整时显式更新引用并重建派生报告和索引，不能通过忽略哈希差异来接受损坏数据。MetaX 移交资料的逐文件接收摘要与当前位置见 `evidence/metax/intake/organized-files.json`，仅用于来源审计，不参与运行时路径解析。

`datasets/`、`runs/`、`records/`、`baselines/` 和索引默认忽略 Git，使用制品备份保存；只备份 `index.json` 无法恢复实验。代码仓库保留可审查的小型历史来源证据，模型权重不放在这里。需要跨机器共享时一起传输记录及其引用的制品，使用相对仓库路径重新校验。

`.gitattributes` 禁止 Git 转换 `evidence/` 的换行符，避免 Windows/Linux 之间的自动换行转换破坏已登记 SHA-256。归档内的历史 `runs/` 已从通用忽略规则中排除；活动运行仍忽略。
