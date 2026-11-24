# 资料与方法库

`catalog/` 保存可复用资料的入口、来源索引和方法整理，适合收录这批 C500 材料。它与另外两个目录分工：`recipes/` 保存当前实验要用的配置，`experiments/` 保存每次运行的完整证据与结果。

```text
catalog/
  mechanisms/              # 从现象到控制实验的机制卡
  library/
    metax/
      collection.yaml      # 资料集合、固定来源哈希、人工选定的方法/报告
      index.yaml           # 可重建的文档导航索引
      README.md            # 本项目的使用与方法映射
      hwdoc/               # 原始 PDF、逐页索引、生态快照、实践资料和检索工具
      methods/             # 精度回归、HumanEval 与算子优化方法
```

第一批资料见 [MetaX / C500 入口](library/metax/README.md)：16 份 PDF、899 页，既有检索还覆盖 138 条生态记录、130 条 GitHub 记录、16 条实践记录。条目数不是独立文件数。保留原资料中的日期、文档修订、适用范围、原页与来源哈希。

```powershell
python -m catalog verify metax
python -m catalog index metax
python -m catalog search metax weight_scale --source practice --limit 5
python -m catalog search metax --component mcprofiler --limit 5
python -m catalog search metax --doc mctracer-v08 --page 7 --full
```

检索使用资料库中的本地检索引擎，不联网、不执行文档中的部署命令。`verify` 检查入口固定文件、PDF、知识索引来源，以及接收清单中全部文件的当前位置、大小与哈希。索引改变后先核对更新来源，更新相应清单并保留收到时的摘要；不要直接刷新哈希来掩盖历史材料被改动。

资料已经按用途入库：PDF、生态快照和实践库位于 `library/metax/hwdoc/`，可复用方法位于 `library/metax/methods/`；历史实验及其脚本快照位于 `experiments/evidence/metax/glm53/`，HumanEval 数据集位于 `experiments/datasets/humaneval/`，接收清单和搬迁核验记录位于 `experiments/evidence/metax/intake/`。原包目录已移除，所有当前引用直接使用真实位置。当前 CLI 接入 `metax` 集合。

文档修订号不等于运行库版本；官网列出不等于安装成功；历史测量不等于新机器上的有效基线。经过重算的历史结果也保留原观察日期。新的运行结果先进入 `experiments/`，经过审阅后再提炼为带证据链接的实践案例。
