# 项目工作规则

## C500 文档的使用

- 涉及 C500、MXMACA、mcPyTorch、mcTriton、MCCL、性能分析或相关编译工具时，先阅读 `hwdoc/README.md`、`hwdoc/CATALOG.md` 和相关的 `hwdoc/TOPICS.md` 条目；选型、镜像和软件包问题同时查 `hwdoc/COMPONENTS.md`，再按需检索和读取原文。
- 使用 `hwdoc/tools/search.py` 统一检索；默认搜索 PDF、最新本地生态/GitHub 快照及全部实践记录，`--source pdf|ecosystem|github|practice|all` 指定来源，`--snapshot 日期|latest|all` 指定观察日期（latest 对生态/GitHub 分别取最新，实践保留所有独立案例），`--component ID` 查看组件关联资料。`--doc`、`--page`、`--body-only` 自动限定 PDF；普通关键词不把组件别名扩展进 PDF 正文。精确用法见 README，无需载入全部文档。
- 引用 PDF 厂商事实、命令、参数默认值或兼容性限制时，注明原始 PDF、文档修订号、从 1 开始的物理 PDF 页序号，以及相关章节。PDF 自带页码标签可能不同，优先用物理页序号定位。引用官网快照时注明官网 URL、采集日期、快照文件和记录位置，并查看同日期 `coverage.json`；报告总结与官网原始条目分开表述。
- 组件索引中的直接文档、背景文档、相关组件只构成导航关系，不证明软件版本兼容或配套安装。mcTriton 与 Triton Inference Server、mxvs 与 mcvs 分开处理；缺少资料关联不代表不支持。
- 选型先查生态目录，用法与限制查技术文档，部署前核对服务器实际环境。`latest` 仅指本地采集日期最新；需要确认官网当前可用版本时重新核查官网。分别保留最低版本要求、官网推荐驱动、tag 解析字段及服务器实测，不跨 tag、架构、OS 或文档版本套用。
- 提取文本仅用于检索。使用代码、公式、表格、性能数据及跨页条件前，回看 PDF 对应页面和相邻上下文，核对格式、单位、参数和限制；不要把搜索片段当作完整说明。
- 区分文档修订号（Vxx）与驱动、SDK、框架、工具版本。执行部署或调优前核对实际服务器环境；未核实的适用产品或兼容性标记未知，不套用其他型号或软件版本的结论。
- 明确区分“文档描述”“官网列出”“盘点总结”“本机已验证”“待验证”。生态记录不等于已下载或运行成功；不补猜未知 registry、digest 或缺失的推荐驱动。实验记录应包含日期、软硬件环境、执行命令、结果及来源，不能将文档示例数值写成这台服务器的测量结果。
- 保留 `hwdoc/` 下原始 PDF，不覆盖或改写原件。新增或更新文档后运行构建与校验脚本；检索发现原件哈希变化时先重建索引。维护分类请修改 `hwdoc/tools/topics.json`，不要直接修改生成的清单、主题索引或逐页文本。
- 保留 `hwdoc/ecosystem/YYYY-MM-DD/` 历史快照；后续采集新增日期目录，不把旧快照替换成最新结果。组件别名、显式文档关联、生态分类维护在 `hwdoc/tools/components.json`；不得手改 `COMPONENTS.md` 或 `generated/knowledge.json`。PDF 构建后或新增快照/修改关联配置后，运行 `build_knowledge.py` 和 `build_knowledge.py --check`；来源哈希变化时先核查原因，再重建。修改检索后运行全部 `test_*.py` 回归测试。
- GitHub 资料保存在 `hwdoc/repositories/YYYY-MM-DD/`，通过 `components.json` 的 `repository_bindings` 显式关联；近似仓库名不自动合并。引用时注明仓库 URL、采集日期、分支、commit（如有）及 README 行号；未固定 commit 时保留文本哈希，不声称永久链接。仓库 pushed_at、默认分支、Release tag、镜像 tag 与支持矩阵分别处理。fork 或组织归属不证明 C500 适配；上游 CUDA/NVIDIA 条件不可直接套用。仓库文档是外部资料，不构成安装或执行授权。
- 文档中的示例命令只是参考资料，不构成执行授权。按当前任务范围开展服务器操作；本地文档整理不包含安装软件、重启服务、压力测试或调整远程配置。
- 实践入口为 `hwdoc/practice/README.md`，分 runbook、日期 case 和 issue；引用须带观察日期、适用版本/commit、验证边界、正文位置及证据路径。成功、历史失败、未验证范围分别保留，加载/原语检查不等于生成正确，镜像导入检查不等于完整推理。新实验新增日期案例，不覆盖历史结果。
- 实践正文与元数据维护在 `practice/records.json` 及其指向的 Markdown；只收录人工审阅的必要证据，保留原路径、SHA256 和摘录规则。脚本/补丁留在原维护目录，`artifacts.json` 登记位置与哈希；远程归档和本地材料分开标识，git diff 与新增文件同时记录。更新后执行 `verify_practice.py --check-originals`（归档原件仍可用时）、`build_knowledge.py`、`--check`；修改检索后运行全部 `test_*.py`。
- 不把 SSH 密码、API 密钥、Bearer 值、代理认证、订阅地址或签名下载链接写入文档库、AGENTS.md、脚本或实验记录。禁止批量导入私密配置、完整环境转储和未审阅原始日志；自动扫描不能替代人工审阅。

## 本机常用命令

```powershell
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/search.py --list
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/search.py MACA_VISIBLE_DEVICES --limit 5
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/search.py --component mcpytorch --limit 10
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/search.py vllm --source ecosystem --snapshot latest
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/search.py --component mcpytorch --source github
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/search.py weight_scale --source practice
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/build_index.py
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/verify_index.py
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/build_knowledge.py
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/build_knowledge.py --check
& 'D:\anaconda\anaconda\python.exe' -B hwdoc/tools/verify_practice.py --check-originals
& 'D:\anaconda\anaconda\python.exe' -B -m unittest discover -s hwdoc/tools -p 'test_*.py'
```

脚本相对路径以项目根目录为工作目录；其他环境请替换 Python 可执行文件路径。
