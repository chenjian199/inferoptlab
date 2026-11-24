# Agent 技能与工作流

这是随项目维护的 skill 源码目录。每个 `skills/<name>/SKILL.md` 可作为 Agent 的阶段入口；当前没有自动启动 Agent、部署到个人技能目录或安装外部插件。使用时让 Agent 读取对应文件，或由所用 Agent 平台配置项目技能目录。技能引用仓库相对路径，单独复制 SKILL.md 会丢失这些依赖。

| Skill | 负责工作 | 交付与边界 |
|---|---|---|
| [inferopt-benchmark](skills/inferopt-benchmark/SKILL.md) | 第一阶段：场景、运行准备、AIPerf 流程 | 原始 Run/测量/环境；不凭存在镜像认定运行可用 |
| [inferopt-diagnosis](skills/inferopt-diagnosis/SKILL.md) | 第二阶段：证据核验、可比性、假设 | DiagnosisReport；观察不直接升级根因 |
| [inferopt-analysis](skills/inferopt-analysis/SKILL.md) | 第三阶段：方法选择、专项设计与分析 | 任务包、采集要求、实验判定；计划不等于执行 |
| [inferopt-optimize](skills/inferopt-optimize/SKILL.md) | 第四阶段：配置/代码候选与验证交接 | 交接清单，未来任务/候选；Agent 不自封验收通过 |

## 共同约束

- **遵从任务范围**：沿用用户已授权的操作；技能本身不扩大 SSH、GPU、服务变更或发布权限，不对已授权步骤重复征求许可。缺资料时先完成不依赖它的本地工作，再指出具体缺口。
- **规约只有一份**：定义/模板/配方留在 `schemas/`，运行结果放 `experiments/runs/<阶段>/`；新增值沿用模板和验证器。原始证据不覆盖，模型/框架/精度/负载变化要留新身份。
- **证据分层**：来源报告、硬件实测、请求观察、根因假设、受控实验和 Agent 自报分别标记。未知用 null/缺口表示；硬件名义峰值不冒充目标 shape 的实测。
- **测量可比**：固定工作点、请求集、输出规则、cache、协议与实际设备映射；profiler 数据不替代无 profiler 验收；GPU 秒按实际设备集合计算。
- **开发与验收分离**：候选起始 unverified。Agent 可以读公开规则和开发用例，不能修改正式验收器/隐藏样本/评分口径来通过；独立验收记录与开发记录分开。
- **可停止、可恢复**：执行前具备范围、预算及恢复办法；超时/失败/预算耗尽保留记录，清理本任务拥有的资源。技能文字不替代执行层隔离或资源租约。

## 四步工作流

`确认目标与规约 → benchmark 原始证据 → diagnosis 可比性/假设 → analysis 专项证据 → optimization 候选 → 独立验收与 E2E 复测 → 更新配方及结论`

证据不足回到相应阶段；推翻假设也是有效产出。配置搜索可基于合格基线独立开展；代码热点任务需要真实调用点及专项证据。每次交接至少给出：输入文件/摘要、完成动作、产物位置、已证实与未知、阻塞事项及下一步。未执行的步骤不能写成已完成。

当前项目状态与机器边界见 [第四步说明](../optimization/README.md#预算终止与机器约束) 和 [集群记录](../docs/cluster-intake-20261123.md)。这次增加技能不触发远程测试。

## 简要使用示例

- “读取 `agent/skills/inferopt-diagnosis/SKILL.md`，分析封存的 Qwen 批次并列出缺失证据。”
- “读取 `agent/skills/inferopt-analysis/SKILL.md`，为 request-timing 细化最小控制实验。”
- “读取 `agent/skills/inferopt-optimize/SKILL.md`，生成第四步交接清单，不启动远程任务。”

这些是项目定义的工作流技能，不是 KDA 官方技能，也不代表已安装 KDA 后端。
