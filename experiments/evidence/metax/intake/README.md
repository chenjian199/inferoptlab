# 接收与整理记录

`FILES_SHA256.json`、`TRANSFER_*.json`、移交说明、`received-agents.md` 和 `verify_package.py` 保存收到时的交付记录。清单中的目录和验证命令描述原始分发包，不能在拆分后的仓库直接照搬执行。

当前核验命令为：

```powershell
python -m catalog verify metax
```

`organized-files.json` 逐文件记录收到时的路径、大小、SHA-256，以及当前的位置、大小、SHA-256 和变更原因。它不提供运行时路径别名。原始 PDF、实验 JSON/JSONL、张量、源码快照和压缩归档保留原内容；维护文档修正本地链接，索引通过资料库工具重建。

原包的两个 `.gitignore` 保存为各自目录下的 `gitignore.snapshot`，避免历史忽略规则隐藏已接收的运行与数据集文件。所有接收文件均有当前位置，原包目录已移除。
