# 实验配置

- `d0_environment.json`：从历史部署案例提取的参考配置，记录 source path，不能冒充新环境检查。
- `humaneval_regression.json`：已选数据集和待校准评测协议。待数据、模板、解析器及执行环境均固定后才可转为 frozen。
- `performance.json`：独立的稳态性能矩阵草案。
- `thresholds.json`：B0 自重复前保留 null；未设置阈值应中止验收，不能默认为通过。
- `candidate.json`：默认使用 baseline；确认算子契约和覆盖范围后，逐个启用候选。

这些是项目配置数据，不是 vLLM 原生 CLI 参数文件。后续 harness 必须显式转换、校验并保存完整生效配置；不能直接把所有字段传给 vLLM。运行时复制并记录 SHA256，不就地修改历史 run 的配置。
