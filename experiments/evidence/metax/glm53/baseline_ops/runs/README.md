# 运行结果

`_template/` 只有格式模板，不是一次运行，不参与统计。后续为每次实验新建 `<Asia-Shanghai时间戳>_<配置摘要>/`，如 `YYYYMMDDTHHMMSS+0800_<hash>/`，禁止覆盖已有目录。

每轮保存 manifest、environment、correctness.jsonl、performance.jsonl、operator_coverage 和 report。JSONL 模板是空文件；运行器须校验状态、预期 ID 和行数，不能因为文件存在就判断完成。

真实结果目录默认不提交；完成后按哈希归档必要数据和报告。`run.status=complete` 只在预期任务均有有效结果、产物清单完整时写入；单题模型失败仍是有效评分，但基础设施故障、缺失任务和未执行阶段必须如实列出。

HumanEval v1 使用 `canonical_v1`、`20261123_humaneval_v1_smoke32`、`20261123_humaneval_v1_full164`。模型运行各含 `generation_manifest.json`、`generations.jsonl`、`correctness.jsonl`、`score_summary.json`；公共环境/输入/脚本证据位于 `../evidence/humaneval_v1/`，不重复拷贝到每个 run。canonical 只有评分结果。未运行 performance 或 operator capture，因此不创建对应的假结果文件。
