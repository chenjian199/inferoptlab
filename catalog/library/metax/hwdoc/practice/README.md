# C500 实践知识库

这里保存可复用的操作方法、带日期的部署案例，以及有证据的故障修复。实践结论只适用于各记录声明的软件版本、硬件和运行配置；组件关联仅用于导航。

## 操作指南

- [MIM 登录与下载排障](runbooks/mim-auth-and-download.md)：区分鉴权、manifest、blob 传输，判断是否支持真正的断点续传。
- [Mihomo 下载代理](runbooks/mihomo-download-proxy.md)：私密输入、回环监听、按进程使用、验证与停用。
- [MetaX 独立软件环境](runbooks/isolated-metax-environment.md)：保留原环境、固定源码与依赖、构建和确认实际加载路径。
- [推理验收与基线冻结](runbooks/inference-validation-and-freeze.md)：从加载和算子检查到真实生成，保存可复现资产与验证边界。

## 部署案例

[2026-11-22 GLM-5.3-Flash-W8A8 八卡部署](cases/2026-11-22-glm53-w8a8-tp8/README.md) 包含软件版本、真实生成结果、失败路线和三项源码修复。原始 MIM 镜像没有完整下载，成功基线来自缓存基础镜像和官方 SDK、wheel 的独立重建。

## 检索与引用

在项目根目录运行 `python catalog/library/metax/hwdoc/tools/search.py MIM --source practice`，或 `python catalog/library/metax/hwdoc/tools/search.py weight_scale --source practice --full`。默认 `--source all` 包含实践；`--component vllm-metax` 和 `--topic inference` 可筛选关联记录。

实践中的日期是观察日期，不是版本优先级。默认及 `--snapshot latest` 均保留所有实践记录；`--snapshot YYYY-MM-DD` 精确筛选观察日期；`--snapshot all` 同时展开网页历史快照。不同日期的独立案例不互相替代。

引用包含记录标题、观察日期、文件及章节/行号、适用版本、验证范围和证据路径。检索片段不能替代原文中的限制。指南是从案例提炼的方法；案例中“已验证”也不表示文中的所有建议均执行过。

## 新增与维护

1. 新建 `cases/YYYY-MM-DD-主题/`，保留旧案例。正文写清环境、复现入口、结果、失败尝试及未验证范围；结构化摘要放入 `case.json`。
2. 只将人工审阅的必要证据存入 `evidence/`。若摘录原记录，写明原路径、原 SHA256、摘录字段和处理方式。`artifacts.json` 保存原脚本/补丁、镜像、远程归档的位置与哈希；历史哈希不等于当前远程资产可用性检查。
3. 原脚本仍在 `glmf/` 维护；不复制第二套可执行代码。跟踪文件 diff 与新增未跟踪文件分别登记。远程归档只记录已有证据，不假称已下载到本地。
4. 在 `records.json` 显式登记 runbook/case/issue。正文必须在 `practice/` 内；问题条目可用唯一的 `## ` 标题定位。填写日期、组件、主题、适用范围、验证状态、覆盖范围文件及带 SHA256 的证据。组件新增/别名维护在 `../tools/components.json`。
5. 运行 `python catalog/library/metax/hwdoc/tools/build_knowledge.py`、`python catalog/library/metax/hwdoc/tools/build_knowledge.py --check` 和 `python -B -m unittest discover -s hwdoc/tools -p 'test_*.py'`。`generated/knowledge.json` 与 `COMPONENTS.md` 由构建生成，禁止手改。

只有 `records.json` 指向的 Markdown 正文进入全文检索。实践 Markdown/JSON 均参与来源哈希检查，证据不会自动展开成全文命中；增删改后需重建。原 `glmf` 文件不自动收录，也不因后续实验改动而覆盖历史证据。

入库前检查正文、结构化字段、链接和证据，剔除密码、API key、Bearer 值、代理认证信息、订阅地址、签名下载链接及完整环境转储。只保留状态码、版本、哈希与必要结果。自动扫描不能替代人工审阅；不要把私密值放入扫描命令或错误输出。

本库维护不包含服务器安装、重启、推理或压力测试授权。操作指南命令须结合当前任务和资源占用执行。

## 未闭环问题

- [2026-11-23 GLM历史greedy分叉](cases/2026-11-23-glm-greedy-repeatability/issues.md)：独立进程重复稳定，历史9题分叉唯一根因未复现；保留原基线与判定边界。
- [2026-11-23 GPU6不可用](cases/2026-11-23-glm-gemm-prototype/issues.md)：阻断完整TP8模型对照；未重置设备或修改驱动。
- [2026-11-23 一次热复位后复发](cases/2026-11-23-c500-warm-reset-recurrence/case.md)：后续获授权尝试GPU4～7热复位，短暂恢复后在首个all-reduce中同一端口再次报错；尚未重启主机，等待进一步处理选择。

## 算子替换实践

- [2026-11-23 GLM INT8 GEMM原型](cases/2026-11-23-glm-gemm-prototype/case.md)：mcTriton独立56组、真实权重与合成激活的vLLM量化层24组通过；完整模型尚未验证，边界与后续入口一并保留。

- [2026-11-23 重启后备用通信下的八卡模型对照](cases/2026-11-23-glm-gemm-p2p-disabled/case.md)：后续用户普通重启后链路仍异常；仅实验内禁用P2P完成原32题30/32、候选32题31/32、恢复4题4/4，无通过题退化。单层替换筛查通过，硬件仍未修复；前述案例保留各自当时的状态。
