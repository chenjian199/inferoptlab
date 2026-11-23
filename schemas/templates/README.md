# 规约创建模板

模板生成可编辑的 YAML 配方；字段约束由 [`schemas/`](../README.md) 决定。基础规约在 `schemas/recipes/`，部署/场景/测试计划在 `benchmark/` 对应子目录。模板本身不是已验证的模型或硬件配置。

| 模板 | 参数示例 |
|---|---|
| [diagnosis/plan](diagnosis/plan.yaml) | [diagnosis-plan.yaml](../examples/diagnosis-plan.yaml) |
| [analysis/plan](analysis/plan.yaml) | [analysis-plan.yaml](../examples/analysis-plan.yaml) |
| [analysis/method](analysis/method.yaml) | [analysis-method.yaml](../examples/analysis-method.yaml) |
| [models/model](models/model.yaml) | [models-model.yaml](../examples/models-model.yaml) |
| [hardware/device](hardware/device.yaml) | [hardware-device.yaml](../examples/hardware-device.yaml) |
| [hardware/cluster](hardware/cluster.yaml) | [hardware-cluster.yaml](../examples/hardware-cluster.yaml) |
| [slas/sla](slas/sla.yaml) | [slas-sla.yaml](../examples/slas-sla.yaml) |
| [slas/latency](slas/latency.yaml) | [slas-latency.yaml](../examples/slas-latency.yaml) |
| [workloads/workload](workloads/workload.yaml) | [workloads-workload.yaml](../examples/workloads-workload.yaml) |
| [protocols/measurement](protocols/measurement.yaml) | [protocols-measurement.yaml](../examples/protocols-measurement.yaml) |
| [runtimes/runtime](runtimes/runtime.yaml) | [runtimes-runtime.yaml](../examples/runtimes-runtime.yaml) |
| [test-cases/test-case](test-cases/test-case.yaml) | [test-cases-test-case.yaml](../examples/test-cases-test-case.yaml) |
| [studies/study](studies/study.yaml) | [studies-study.yaml](../examples/studies-study.yaml) |
| [validation/policy](validation/policy.yaml) | [validation-policy.yaml](../examples/validation-policy.yaml) |
| [deployments/deployment](deployments/deployment.yaml) | [deployments-deployment.yaml](../examples/deployments-deployment.yaml) |
| [benchmarks/scenario](benchmarks/scenario.yaml) | [benchmarks-scenario.yaml](../examples/benchmarks-scenario.yaml) |
| [benchmarks/plan](benchmarks/plan.yaml) | [benchmarks-plan.yaml](../examples/benchmarks-plan.yaml) |
| [models/inspected](models/inspected.yaml) | [models-inspected.yaml](../examples/models-inspected.yaml) |
| [hardware/inspected](hardware/inspected.yaml) | [hardware-inspected.yaml](../examples/hardware-inspected.yaml) |
| [hardware/measurement](hardware/measurement.yaml) | [hardware-measurement.yaml](../examples/hardware-measurement.yaml) |

实机模板适用于已有探测证据的模型和集群；测量模板适用于带原始计时的硬件微基准。对应示例来自本次 `63metax` 采集，只能作为字段组织参考；迁移到另一机器必须替换硬件序列号、文件指纹、时间和来源。性能数值会按原始样本重新计算校验。

参数示例主要从首版来源配方取值，并用 `example-` ID 避免覆盖。`slas-latency` 和 `validation-policy` 是明确标注的演示值，不能直接作为新增合同目标或验收策略。

## 新增一个具体规约

1. 选择对应模板，复制参数示例，修改 `id`、名称、领域字段和来源；不知道的字段使用 Schema 允许的 `null`/`unspecified` 并记录 `issues`。
2. 使用 `python tools/specs.py instantiate <模板> --params <参数> --out <新配方>` 创建配方。
3. 执行 `python tools/specs.py validate <新配方>`，确认后放入对应配置目录。基础规约登记到 `schemas/recipes/`；部署、场景、计划分别登记到 `benchmark/recipes/`、`benchmark/scenarios/`、`benchmark/plans/`。有原始附件时加 `--sources` 核对哈希。
4. 在 TestCase 中组合模型、负载、测量协议和 SLA；在 Study 中引用 Case、集群与运行环境。
5. 用 `resolve` 检查依赖闭包，解决冻结阻塞项后再用 `freeze`。冻结只固定输入，不产生性能证明。

模板内 `{$param: threshold_ms}` 替换整个节点，保留数值/布尔/列表类型，不执行字符串插值、Python 或 Shell。未知参数、缺失必填参数、类型错误、未声明的 `$param` 都会报错。嵌套对象在生成后由目标 Schema 再校验。

v0.2.0 不支持多层 `extends` 或隐式深度合并。需要复用时优先引用既有版本化配方；模板调整不会回写已经创建的配方。
