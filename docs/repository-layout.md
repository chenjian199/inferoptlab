# 当前目录与工作流程

本项目以当前目录和规约版本为唯一入口。定义、实际配置、实现代码、知识资料与运行结果分别保存；代码不自动寻找旧目录，也不转换旧版契约。

```text
inferoptlab/
  schemas/
    definitions/                    # 当前 JSON Schema
    templates/                      # 新配置的参数化模板
  recipes/
    models/<family>/<model>/        # 按家族与具体模型归档的实际模型配方
    hardware/ runtimes/             # 实际硬件和软件身份
    deployments/ scenarios/         # 部署配置与请求场景
    workloads/ protocols/ slas/      # 请求、测量与验收条件
    plans/                          # 硬件及各阶段执行计划
    operators/                      # 实际算子测试契约
    sources/ observations/          # 来源登记和结构化历史观测
  examples/
    parameters/                     # 模板参数示例
    traces/                         # 明确标记的合成 trace
  catalog/
    mechanisms/                     # 机制卡
    library/metax/
      hwdoc/                        # PDF、索引、生态快照、实践资料、检索工具
      methods/                      # 精度回归与算子优化方法
      collection.yaml               # 来源范围与固定哈希
      index.yaml                    # 可重建导航
  benchmark/
    load/                           # AIPerf 服务压测与 P/D 工作负载
    accuracy/                       # 精度协议、原始输出核验与功能比较
    breakdown/
      operators/                    # 算子捕获、自重放与数值验收契约
    common/                         # 公共制品和进程工具
  diagnosis/                        # 第二步：基于测量证据提出归因假设
  analysis/                         # 第三步：选择方法与规划控制实验
  optimization/                     # 第四步：候选范围、验证要求和交接
  tools/
    hardware/                       # 盘点、校准、模型元数据采集
    specs.py                        # 规约校验、模板展开和冻结
    experiments.py                  # 结果登记、索引、查询和基线标签
    import_inspected_model.py       # 将核验后的模型观察导入配方
  experiments/
    datasets/                       # 数据集与请求夹具
    evidence/                       # 原始观察和历史实验附件
      metax/glm53/                  # GLM 移交实验、张量与历史脚本快照
      metax/intake/                 # 接收清单和整理后的文件核验记录
    runs/                           # 本次运行及派生报告
    records/                        # 完整测试配置与结果关联
    baselines/                      # 显式基线标签
    index.json                      # 可重建查询索引
  contracts/                        # 跨阶段接口
  agent/skills/                     # 四个阶段的工作约束
  tests/                            # 合成契约测试和历史证据回归
  docs/                             # 设计说明及后续路线
```

## 工作流程

1. 从资料库确认方法与适用范围，用硬件工具采集机器和模型身份。
2. 用 schema 模板创建实际配方，补齐部署、数据集、并行组合、请求倍率和验收条件。
3. 第一阶段分别准备或运行服务压测、精度检查、分层/算子测试，将配置闭包与证据保存到实验目录。
4. 第二阶段从证据建立假设；第三阶段规划可区分假设的控制实验，所需采集仍由第一阶段测试模块承担。
5. 第四阶段形成候选范围与验证交接；实际候选仍需正确性、数值、无 profiler 的性能测量和回归证据。
6. 合格运行才能登记相应基线，资料库只接收经过审阅且有来源的可复用结论。

## 当前命令边界

```powershell
python tools/specs.py validate
python -m catalog verify metax
python -m catalog search metax weight_scale --source practice
python -m tools.hardware plan recipes/plans/hardware/metax.yaml
python -m benchmark load plan recipes/plans/benchmark/glm53-flash-decode.yaml
python -m benchmark accuracy --help
python -m benchmark breakdown --help
python -m diagnosis --help
python -m analysis --help
python -m optimization --help
python -m tools.experiments query
```

统一 benchmark 命令必须选择模块；trace 汇总只有 `benchmark breakdown trace` 入口。规约只接受当前 `schema_version: 0.2.0`，Study 的定义直接位于 `schemas/definitions/study.json`。

历史附件内的脚本、远程命令和环境路径是实验记录，不属于当前可执行 API。布局整理的文件清单用于审计，不参与路径解析。新执行适配器的能力范围以各模块 README 为准；精度与算子模块尚未接入的执行能力不能由目录存在推断。

后续集中调度、Candidate 血缘和多机制品服务见 [路线图](roadmap.md)，不在当前目录中预留第二套配置体系或命令别名。
