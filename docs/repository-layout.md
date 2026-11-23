# 建议仓库结构

第四步新增 `optimization/`（离线交接 CLI、交接逻辑和后续执行接口）、`agent/skills/`（四个阶段的项目技能）与 `runs/optimization/`（生成结果）。入口见 [第四步说明](../optimization/README.md) 和 [技能约束](../agent/README.md)。

本文件描述当前实现和未来运行目录。当前已提供规约工具、`benchmark/` 测试模块、`diagnosis/` 离线归因与 `analysis/` 专项规划/trace 汇总。新阶段的实际目录、契约及边界见 [阶段设计](diagnosis-analysis.md)；以下 `src/` 中的完整平台模块仍是后续蓝图，不要求现在把已运行代码迁入该布局。

```text
inferoptlab/
  README.md
  pyproject.toml                     # 实施时新增，依赖和 CLI 入口
  docs/
    architecture.md
    data-contracts.md
    measurement.md
    validation.md
    platform-adapters.md
    kda-integration.md
    external-integrations.md
    roadmap.md
    backlog.md
    adr/
  schemas/                          # 规约体系统一入口
    definitions/                    # 校验规则，如 model.json、hardware.json
      legacy/                       # 旧版规则
    templates/                      # 创建模板，如 models/model.yaml
    recipes/                        # 来源配方、Case/Study、报告结果
    examples/                       # 模板参数示例
    requirements.txt                # 离线规约工具依赖
    README.md
  tools/specs.py                    # 已实现：validate/instantiate/resolve/freeze
  benchmark/                        # 已实现的第一步测试闭环
    cli.py                          # plan/prepare/run/analyze/report
    planner.py                      # 规约解析、快照、矩阵与预算
    runner.py                       # 顺序执行、进程所有权、归档
    dataset.py                      # 固定请求集与精确长度
    adapters/                       # AIPerf / 单机 SGLang
    metrics/                        # 归一化、SLA、报告
    scenarios/                      # 引用 Case
    recipes/                        # 模型/硬件/框架部署配方
    plans/                          # 基线、分块、并行布局比较
    README.md
  tests/test_specs.py               # 已实现：结构、语义、快照与兼容性检查
  tests/test_benchmark.py           # 已实现：合成流程、失败处理、统计与重算
  configs/
    studies/                        # 实际 Study，引用密钥而不保存密钥
    platforms/                      # 平台清单与待探测参数
    engines/                        # 框架版本和参数映射
    policies/                       # 测量、正确性、评分策略
  examples/                         # 旧版架构与任务设计示例
  catalog/
    mechanisms/                     # 开放机制卡与区分实验
    probes/                         # 可复用的能力/校准实验
  src/inferoptlab/
    domain/                         # 对象、ID、单位、枚举、不变量
    application/                    # 创建 Study、执行实验、导入候选等用例
    orchestrator/                   # 状态机、预算、租约、恢复
    inventory/                      # 软硬件与模型清单、能力协商
    measurement/                    # benchmark、校准、归一化、有效性
    diagnosis/                      # 可比性、关键路径、假设、未解释问题
    search/                         # 条件候选空间、策略、剪枝、成本
    optimizers/
      configuration.py              # 修改已有可用配置
      code.py                       # 代码优化器通用接口
      task_packager.py              # 任务包导出与候选包导入
    validation/                     # 正确性、局部、E2E、统计、组合回归
    adapters/
      devices/                      # nvidia / ascend / metax / hygon，逐个实现
      engines/                      # sglang / vllm，逐个验证具体版本
      models/                       # 模型结构、形状与状态类型
      profilers/                    # 各平台 trace 与计数器采集
      benchmarks/                   # vLLM / SGLang / 自有负载驱动器
      executors/                    # local / ssh / container，后续 k8s
      code_optimizers/               # kda_workflow / external_agent / manual
      performance_models/           # empirical / aisim 等可选预测器
    registry/                       # 元数据、事件、制品、候选血缘
    reporting/                      # 结构化报告与展示层
    cli/                            # 调用 application 的薄入口
  tests/
    unit/                           # 状态机、评分公式、条件候选约束
    contracts/                      # 适配器返回、Schema、解析器 fixture
    integration/                    # 构建/启动/测量/清理的控制路径
    qualification/                  # 需要真机的资格测试
  tools/                            # 开发辅助与证据导出
  .gitignore
```

## 依赖方向

`cli → application → domain + ports`。具体 adapter 实现 ports；控制端通过依赖注入选用 adapter。`domain` 不反向依赖 CLI、数据库或厂商 SDK。

尽量让状态和对象只存在一个定义：先把本蓝图 Schema 演化成可执行契约，运行时代码从其生成或用契约测试保证一致。不要在 CLI、Worker、KDA 适配层各维护一份不同的 StudySpec。

## 什么放 Git，什么放制品库

| 内容 | 位置 |
|---|---|
| 源码、设计、契约、公开小型测试 fixture、机制卡 | Git |
| 每次实际运行的完整配置快照、命令、元数据 | 实验仓储，按 Run 导出 |
| 模型权重、原始 trace、大日志、构建镜像、真实请求数据 | 制品存储或受控数据源 |
| API key、SSH 凭据和访问令牌 | 运行环境的 secret 引用 |
| 候选补丁 | 工作分支/工作区 + 制品快照，记录基础 commit |

首版可以将 `artifacts/` 和 `runs/` 放本地，但必须排除于 Git；最终复现包引用内容 hash。不要把十几 GB 的 trace 或模型权重提交到源码仓库。

## 目标 CLI 设计（待实现）

```bash
inferoptlab inspect --target configs/platforms/lab.yaml
inferoptlab study validate configs/studies/demo.yaml
inferoptlab study plan configs/studies/demo.yaml
inferoptlab study run configs/studies/demo.yaml
inferoptlab study resume STUDY_ID
inferoptlab study report STUDY_ID
inferoptlab task export TASK_ID --format kda-workspace
inferoptlab candidate import CANDIDATE_BUNDLE
inferoptlab candidate verify CANDIDATE_ID
inferoptlab study package STUDY_ID
```

上述命令不属于已交付的可运行功能。`plan` 应只生成可审查计划；`run` 根据已冻结 Study 和资源配置执行。配置未解析、必要能力未验证或预算冲突时返回具体错误，不替用户猜测资源。
