# 模型配方

按 `家族/具体模型/配方.yaml` 组织。目录表示归档位置；配方的 `id` 与 `version` 是其他配方引用它的稳定身份。加载器递归读取子目录，无需按物理路径引用模型。

同一模型的量化版本、来源资料和不同机器上的检查结果放在同一目录；Flash、Pro、参数规模不同的模型分别建目录。`metax-`、`cluster-` 前缀保留，用于区分实机来源，不能把同名权重的不同观察合并为一次验证。

| 家族 | 模型目录 | 配方数 |
|---|---|---:|
| DeepSeek | [V4 Flash](deepseek/deepseek-v4-flash/)、[V4 Pro](deepseek/deepseek-v4-pro/)、[V4.1 Flash](deepseek/deepseek-v4.1-flash/) | 5 |
| GLM | [5.2](glm/glm-5.2/)、[5.3](glm/glm-5.3/)、[5.3 Flash](glm/glm-5.3-flash/) | 9 |
| Kimi | [K2.7 Code](kimi/kimi-k2.7-code/)、[K3](kimi/kimi-k3/) | 2 |
| Qwen | [3 0.6B](qwen/qwen3-0.6b/)、[3.8 27B](qwen/qwen3.8-27b/)、[3.8 2.4T A95B](qwen/qwen3.8-2.4t-a95b/) | 4 |

新建配方时，先选择家族与具体模型目录，再使用 [模型模板](../../schemas/templates/models/) 或实机导入器。目录使用小写英文、数字、点和连字符；模型目录不带机器名和量化后缀。新家族或模型直接增加目录，不增加路径兼容层。

```powershell
python -m tools.import_inspected_model experiments/runs/hardware/metax-next-model.json --id metax-glm-next --family glm --model glm-5.3-flash
python tools/specs.py validate recipes/models/glm/glm-5.3-flash/metax-glm-5.3-flash-w8a8.yaml --sources
```

模板只定义创建方式，实际配方保存在这里；元数据、探针和性能结果保存在 `experiments/`。模型目录名不作为架构或加载兼容性的证据。

文本统一使用 UTF-8。若内容已成为连续问号，切换编码无法恢复；应对照来源重写说明，保留未知字段和验证限制，不根据目录名补写事实。
