# MetaX 资料库维护

- 先阅读 `hwdoc/README.md`、`hwdoc/CATALOG.md` 和相关 `hwdoc/TOPICS.md`；组件与生态关系见 `hwdoc/COMPONENTS.md`。
- 仓库根目录运行 `python -m catalog search metax ...`。资料中的部署命令和历史脚本不构成执行授权。
- 原始 PDF 不改写。引用技术事实时记录 PDF 文件、修订号、从 1 开始的物理页及章节，核对原页的格式和上下文。索引关联不证明版本兼容。
- 保留日期快照和历史测量；区分文档描述、网站列出、历史实测、当前验证与待验证。不要将示例数值变成实测性能。
- 手工维护 `hwdoc/tools/topics.json`、`hwdoc/tools/components.json`、`hwdoc/practice/records.json` 及其正文；生成索引通过工具重建，不能手改生成结果。
- 路径以当前仓库实际位置为准。实践资产的 `original_path` 和 `local_references.path` 相对仓库根目录；实验原件在 `experiments/evidence/metax/glm53/`，数据集在 `experiments/datasets/humaneval/`。
- 修改资料后核对来源差异，运行 `python -B catalog/library/metax/hwdoc/tools/verify_practice.py --check-originals`、`build_knowledge.py`、`build_knowledge.py --check`、`verify_index.py`；修改检索实现时运行同目录全部 `test_*.py`。这些命令均从仓库根目录执行。
- 不导入密码、密钥、完整私密环境或未经审阅的日志。历史附件中的脚本保持其实验作用域；当前执行代码只在正式测试模块维护。
