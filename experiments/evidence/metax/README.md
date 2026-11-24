# MetaX 历史实验原件

`glm53/` 保存收到的 GLM 实验、逐题生成/评分、张量样本、环境记录、补丁与当时脚本快照。它们说明当时发生了什么；脚本内的远程路径、运行命令和依赖版本是历史记录，不是当前项目入口，也不由测试发现自动执行。

当前测试入口为 `python -m benchmark load|accuracy|breakdown`，硬件采集入口为 `python -m tools.hardware`。复用某个历史实现前，应把它接入相应适配器并完成当前环境核验。

方法正文已移至 [资料库](../../../catalog/library/metax/README.md)，HumanEval 数据集移至 `experiments/datasets/humaneval/`。原始接收清单和安全审阅记录在 `intake/`；`organized-files.json` 登记每份接收文件的原路径/摘要、当前位置/摘要和改变原因。它是来源记录，不提供旧路径解析。
