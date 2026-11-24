# 数据与来源

首轮选型见 [SELECTION.md](SELECTION.md)，来源记录见 `source_catalog.json`。HumanEval 已下载并固定为 Hugging Face 官方数据集 `openai/openai_humaneval` 的 `test` split，revision 为 `7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544`；[manifest](manifest.json) 状态为 `prepared`，包含原文件及派生文件 SHA256、164 个唯一 ID 和固定的 32 题子集。许可依据固定 revision 的 README 中 MIT 声明；没有另行取得独立 LICENSE 文件。

`raw/` 保存从已核对来源取得的原始文件与许可；`prepared/` 保存冻结后的生成输入、评分材料、token manifest 和 smoke IDs。二者分离，生成接口不能读取 canonical_solution 和隐藏 test。公开 prompt 中自带的示例保留。

`../harness/prepare_dataset.py` 完成下载与准备。原始 parquet SHA256 为 `2f2871a15fbc95b6c683043359f4ed8e144c5a1c4f24f25f66bc51f598dfcfb6`。生成文件严格只含 `task_id/prompt`；评分文件包含 canonical solution、原始 test 和 entry point，放在远程主机单独目录，不挂载进推理容器。实际 tokenizer 文件、chat template 哈希及每题完整输入 token IDs 见 `../evidence/humaneval_v1/prompt_manifest.json`。

本目录已按当前仓库结构入库，保留已接收的原始数据、许可说明、固定 task IDs、准备后的输入与评分材料；它是 `experiments/datasets/` 默认忽略规则的明确例外。未来大型数据集仍使用位置加 SHA256 引用，不能只保存随机 seed 而不保存选中的 ID。历史准备脚本保存在 `experiments/evidence/metax/glm53/baseline_ops/harness/`，当前离线核验入口见 `benchmark/accuracy/README.md`。
