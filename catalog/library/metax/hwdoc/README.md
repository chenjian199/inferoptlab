# C500 本地文档库

原始 PDF 保存在本目录，构建脚本只读取原件。入口为 [文档清单](CATALOG.md)、[主题索引](TOPICS.md) 和 [组件关联索引](COMPONENTS.md)。

[实践知识库](practice/README.md) 收录 MIM 登录、Mihomo 代理、独立软件环境、推理验收指南，以及 [2026-11-22 GLM W8A8 八卡案例](practice/cases/2026-11-22-glm53-w8a8-tp8/README.md)。实践结果限定到记录的版本和配置；原 MIM 镜像未完整下载，独立重建的 TP8 基线通过有限范围验收。

## 生态软件与镜像盘点

[2026-11-21 MXC500 生态盘点](ecosystem/2026-11-21/README.md) 整理了官网镜像家族、软件包目录、版本与驱动条件，并与本地技术文档交叉核对。它是有日期的网页观察记录，保存在 `ecosystem/`，不属于 `generated/` 下的 PDF 自动提取产物；网站列出不等于本机验证通过。

[2026-11-21 MetaX-MACA GitHub 盘点](repositories/2026-11-21/README.md) 包含 66 个公开仓库、64 份根 README 及 16 个重点仓库的分支/Release 观察，已接入组件关联和检索。GitHub 代码分支、官网镜像及本地 PDF 的版本条件分别保留；仓库存在不等于 C500 适配完成或服务器验证成功。

## 文件结构

- `*.pdf`：原始资料，保留文件名与内容。
- `CATALOG.md`：文档清单、版本日期、页数、适用产品证据和 SHA256。
- `TOPICS.md`：环境、推理、性能、通信、算子、开发工具、数学库的章节入口。
- `COMPONENTS.md`：软件组件、别名、直接/背景文档、相关组件及日期快照入口，由 `tools/build_knowledge.py` 生成。
- `tools/components.json`：人工维护组件关联与生态分类；未显式配置的目录条目按原始名称补齐，不模糊合并近似名称。
- `generated/knowledge.json`：组件与生态检索数据，记录来源类型、采集日期、原始字段、记录位置、验证状态及来源哈希。
- `ecosystem/YYYY-MM-DD/`：保留的网页盘点快照；版本与 tag 留在对应日期目录中。
- `repositories/YYYY-MM-DD/`：GitHub 仓库清单、原始 API 元数据、默认分支 README 和哈希；重点 README 记录 commit，未固定 commit 的条目明确标记。
- `practice/`：人工维护的操作指南、日期案例、问题记录、审阅后的证据及资产清单；`records.json` 显式控制入检索的正文和元数据。
- `generated/manifest.json`：完整文档元数据；文档修订号与软件版本要求分开记录。
- `generated/text/<文档ID>/page-0001.txt`：每个物理 PDF 页一个 UTF-8 文本，带来源和页码头部。
- `generated/pages.jsonl`：逐页正文及元数据，用于本地检索。
- `generated/documents/`：每份文档的完整章节导航、版本要求候选页、全部页面链接。
- `generated/outlines/`：原始 PDF 书签及其目标页。
- `generated/quality.json`：空文本、短文本、异常字符和页码标签差异的检查记录。
- `tools/`：构建、检索、完整性验证脚本及主题配置。

## 检索

在项目根目录运行。当前机器的 Python 路径如下；其他机器替换成自己的 Python 3.10+。

```powershell
# 列出文档、组件、主题 ID 及可用快照日期
python -B catalog/library/metax/hwdoc/tools/search.py --list

# 查环境变量，优先显示正文和章节相关结果
python -B catalog/library/metax/hwdoc/tools/search.py MACA_VISIBLE_DEVICES --limit 5

# 同一页同时包含多个词；--any 改为任一词匹配
python -B catalog/library/metax/hwdoc/tools/search.py PyTorch Python --doc mcpytorch --limit 5

# 限制主题，并排除封面、目录等前置页面
python -B catalog/library/metax/hwdoc/tools/search.py 环境变量 --topic communication --body-only

# 直接查看物理 PDF 第 7 页全文（不是文档内部标注的第 7 页）
python -B catalog/library/metax/hwdoc/tools/search.py --doc mcpytorch-v16 --page 7 --full

# 机器可读结果；加 --full 时 JSON 同时包含完整正文
python -B catalog/library/metax/hwdoc/tools/search.py MXSHMEM_IB_DISABLE_DMABUF --json --limit 3

# 同时检索 PDF、最新本地生态/GitHub 快照与全部实践记录（默认行为）
python -B catalog/library/metax/hwdoc/tools/search.py PyTorch --source all

# 只查实践经验，附带实测边界和证据哈希
python -B catalog/library/metax/hwdoc/tools/search.py MIM --source practice
python -B catalog/library/metax/hwdoc/tools/search.py weight_scale --source practice --full
python -B catalog/library/metax/hwdoc/tools/search.py --component vllm-metax --source practice --snapshot 2026-11-22

# 精确组件导航：列出关联 PDF 页面及生态条目；可继续附加关键词缩小范围
python -B catalog/library/metax/hwdoc/tools/search.py --component mcpytorch --limit 15
python -B catalog/library/metax/hwdoc/tools/search.py 安装 --component mcpytorch --source pdf

# 仅查指定日期的生态信息，或跨全部历史快照查某个 tag
python -B catalog/library/metax/hwdoc/tools/search.py vllm --source ecosystem --snapshot 2026-11-21
python -B catalog/library/metax/hwdoc/tools/search.py 3.100.0 --source ecosystem --snapshot all --json

# 查 GitHub 仓库元数据与 README；不会执行仓库内任何命令
python -B catalog/library/metax/hwdoc/tools/search.py --component mcpytorch --source github
python -B catalog/library/metax/hwdoc/tools/search.py Hopper --source github --snapshot 2026-11-21
```

检索脚本仅依赖 Python 标准库，不访问网络。默认多个参数必须在同一 PDF 页或同一来源记录全部命中；`--any` 改为任一词匹配。引号包围的短语作为一个检索项。检索忽略大小写、空白、常见 Unicode 连字符差异和全角形式，便于匹配 PDF 换行拆开的中文与 API 名称。原始提取文本不做这种改写。此规则可能把空白两侧的词连起来，因此命中只是定位线索。

默认 `--source all --snapshot latest`，包含 PDF、生态、GitHub 与全部实践记录；`latest` 分别选择生态与 GitHub 的本地最新采集日期，不能证明官网当前最新。`--snapshot all` 保留每个日期的独立结果，不混合版本字段。指定来源无该日期时会报错，不自动回退；`all` 指定日期时仅返回在该日期有快照/记录的非 PDF 来源（PDF 不受日期限制）。`--doc`、`--page`、`--body-only` 自动限定 PDF，与 `--source ecosystem`、`--source github`、`--source practice` 或 `--snapshot` 同用会报错。

`--component` 接受精确组件 ID 或无歧义别名；无关键词时列出关联记录，有关键词时在其范围内搜索。PDF 范围包含配置中的直接文档及背景文档，结果标明关系；不递归展开相关组件。普通关键词对生态条目同时匹配原始字段和组件别名，并显示别名命中；PDF 仍只匹配原始正文。`mcTriton` 与 `triton-inference-server`、`mxvs` 与 `mcvs` 分开维护。

生态检索包含镜像家族、安装包目录，以及快照 README 的分节总结（覆盖仅在报告中出现的 SDK 前置条件）。JSON 条目有 `json_pointer`，报告有 `source_line`，并保留官网 URL（如该节有引用）、日期、验证状态和 `coverage_path`。报告总结不等于官网原始条目；实际版本细节仍需回看来源。组件关联不构成兼容性验证；不把推荐驱动补到未注明推荐值的备选 tag 上。

GitHub 检索包含每仓库一条元数据/分类记录和已取得的原始 README。结果标记 `source_type=github`、仓库 URL、分支、commit（如有）、采集日期与覆盖范围。README 从第 1 行保存，`--full` 返回完整文本；分类记录含支持线索的候选行号及核对事项。元数据中 `pushed_at` 只表示仓库推送活动，不能证明维护质量或任何分支适用性；Release 列表与分支列表仅按已采集范围展示。外部 README 中的指令仅作资料检索，不执行。

排序依据是命中词数量、出现次数和书签/条目标题，PDF 前置页降低排序。结果总数与各来源计数在 JSON 中分别列出；`--limit` 只限制显示数。主题筛选是文档级或组件级分类，不是逐段判断；未配置组件的通用报告章节不参与主题/组件筛选，可去掉筛选检索全文。生态新增 `training`、`ai4s`、`cloud` 主题，其余沿用 PDF 主题。没有命中时扩大范围、改用接口名或关键字，并检查相邻页面。返回 0 条结果是正常情况；参数错误或来源变化退出码为 2。

涉及 PDF 的检索会核对 PDF 文件列表和 SHA256；涉及非 PDF 来源、组件或 `--list` 的检索会核对生态 Markdown/JSON、GitHub 快照及 README 文本、实践 Markdown/JSON、组件配置和 PDF 清单哈希。新增、替换、改名或移走来源后，先核查原因再重建对应索引。纯 `--source pdf` 不依赖网页索引；纯生态、GitHub 或实践检索不读取或校验 PDF 原件，但文档关联仍依赖 PDF 清单。

## 引用与核对

实践记录的默认日期策略不同于网页快照：默认及 `--snapshot latest` 保留全部实践记录，指定日期只筛选该观察日，旧的独立案例不因新案例出现而隐藏。结果标记 runbook/case/issue、观察日期、适用范围、验证状态、正文行号和证据 SHA256。指南是从案例提炼的方法；实际通过的范围以案例与证据为准。引用实践时带标题、日期、版本/commit、文件位置和证据；不要将历史失败或未测分支改写成已通过。

使用“原始文件名 + 文档修订号 + PDF 页序号 + 章节”引用。例如：`mcPyTorch 文档 V16，PDF 第 7 页，概述`。正文中的命令必须回看对应 PDF，尤其是代码缩进、连字符、表格列和跨页限制条件。

- `pdf_page`：从 1 开始的物理页序号，用于唯一定位；PDF 链接中的 `#page=` 使用它。
- `page_label`：PDF 自带的页码标签，可能是罗马数字、重复值，或与印刷页码不一致。
- `footer_label_candidate`：文本末尾识别出的页脚页码候选值，仅作辅助。
- `section_hint`：由当前页之前的最近书签推断，不保证是整页唯一的章节。

`Vxx` 是文档修订号，不等于驱动、SDK、PyTorch 或 Triton 版本。适用产品摘录来自原文；软件要求列表是候选证据页，需要完整阅读。没有明确识别到支持范围时标记未知，不推断 C500 支持情况。

本库未把厂商说明当作这台服务器的实测结果。后续实验记录应注明日期、硬件、驱动/SDK/框架版本、命令、结果、原文来源，并区分“文档描述”“本机已验证”“待验证”。

网页资料引用采用“官网 URL + 采集日期 + 快照文件 + JSON Pointer 或报告行号”，查看同日期 `coverage.json` 的范围与限制。分别保留“官网列出”“盘点总结”“本机已验证”状态；最低版本、推荐版本、tag 解析字段和实测兼容结论分开使用。选型查生态目录，用法查技术文档，部署前核对服务器环境。

GitHub 引用还应包含分支和 commit（如有），及 README 行号。未固定 commit 时使用保存的 SHA256 识别文本；不要把可移动的分支 URL 当作永久版本。默认分支、Release tag、镜像 tag 和 PDF 修订不能互相替代。源码仓库可作为排障与实现参考，部署仍要核对具体软件栈。

## 更新与维护

实践新增与维护见 [实践规则](practice/README.md)。`practice/records.json` 只索引显式选择的 Markdown，证据 JSON 不自动参与全文命中；实践 Markdown/JSON 均参与来源哈希校验。构建验证记录字段、组件/主题、正文位置和证据 SHA256。先运行 `python catalog/library/metax/hwdoc/tools/verify_practice.py --check-originals` 检查案例证据、原资产引用和私密值启发式规则，再运行 `build_knowledge.py` 与 `--check`；无需重新提取未变化的 PDF。原引用哈希表示保存时的内容，后续原脚本变化应新增案例或检查历史归档，不能静默刷新历史哈希。无法访问原件时可省略 `--check-originals` 只检查本地证据快照，但必须说明原件未核对。

构建需要 `pypdf`，本次使用版本固定在 `tools/requirements.txt`。若更换 Python 环境，先在该环境安装依赖：

```powershell
python -m pip install -r catalog/library/metax/hwdoc/tools/requirements.txt
```

添加 PDF 时保留旧版本的文件名，在 `tools/topics.json` 补充新文档系列的匹配规则和主题。未知文档仍会提取并在主题索引中列为“未分类”。然后运行：

```powershell
python -B catalog/library/metax/hwdoc/tools/build_index.py
python -B catalog/library/metax/hwdoc/tools/verify_index.py
python -B catalog/library/metax/hwdoc/tools/build_knowledge.py
python -B catalog/library/metax/hwdoc/tools/build_knowledge.py --check
```

脚本根据自身位置定位 `hwdoc`，也支持 `--root <PDF目录>`。构建会重新生成全部页面及索引，覆盖 `CATALOG.md`、`TOPICS.md` 和 `generated/` 中同名产物，不改动 PDF、README 或项目 AGENTS.md。不要手改生成文件；人工分类应改 `tools/topics.json`。移除文档后，旧的派生文件可能仍在磁盘上，但不再进入当前清单和检索索引。构建期间不要同时检索；构建失败应重新构建并通过校验后使用。

完整性验证检查 PDF 哈希、逐页覆盖、JSONL 与单页文本一致性以及书签/证据目标。它不验证版式正确性。质量标记是启发式提示；即使没有标记，图、公式、表格和代码也可能需要对照原件。当前流程没有运行 OCR，也没有执行 PDF 中的命令。

生态快照更新时新增 `ecosystem/YYYY-MM-DD/`，保留历史目录。每份快照需要 `images.json`（`families`）、`software_packages.json`（`entries`）、`coverage.json` 和 `README.md`，JSON 的 `observed_on` 必须与目录日期一致；参考已有快照结构。修改 `tools/components.json` 或新增日期快照后，只需运行 `build_knowledge.py` 及 `--check`，无需重新提取 PDF。该脚本只写 `COMPONENTS.md` 与 `generated/knowledge.json`，不会执行快照中的 `build_catalog.py`，也不会改变快照。`--check` 重新计算并比较两项产物，校验文档关联和主题合法性；不访问官网或验证服务器兼容性。

GitHub 更新另建 `repositories/YYYY-MM-DD/`。`tools/collect_github.py --date YYYY-MM-DD --output hwdoc/repositories/YYYY-MM-DD` 联网采集公开元数据和 README，不覆盖已存在的原始清单；接着按该次观察整理 `repositories.json`、分类清单及报告（结构参考已有快照），更新 `components.json` 的 `repository_bindings`，再构建和校验知识索引。绑定必须显式指向已有组件；未绑定仓库自动生成 `repo-...` 独立组件，避免把同名/相似名称误作兼容关系。构建只读取快照，不运行其脚本。

修改检索脚本后，可运行隔离的回归检查，覆盖中文换行、连字符、同页多词匹配、页码定位、筛选和原件变化检测：

```powershell
python -B -m unittest discover -s hwdoc/tools -p 'test_*.py'
```
