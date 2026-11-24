# 算子实验

真实热点 profile 后，再复制 `_template/` 为稳定的 operator ID。当前没有选定或实现任何候选算子。

每个算子目录后续包含 `contract.json`、`capture.py`、`replay.py`、`reference.py`、`candidate.py`、`test_equivalence.py`、`bench.py` 和 `integration.py`。Python 文件在实现时创建，避免空占位文件被当成已实现工具。

依次验证 B0 捕获→B0 重放、候选与独立参考的局部等价、微基准、8 rank 路径命中和整模型回归。保留 baseline 默认路径与经测试的 fallback，原有三项部署兼容修复属于对照的一部分。
