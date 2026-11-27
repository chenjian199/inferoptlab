# Cached Decode 扫描

更新时间：2026-11-26T08:26:18.170163+00:00；状态：finished_with_exclusions

每槽独立上下文；原始上下文 L 全部命中，线上的请求为 L+1（额外一个 P 端生成的 seed）。
输出是 D 端新生成的 token，seed 不计入输出。未测量 P→D 传输；客户端时延包含调度、排队及流式传输。

| 部署 | 上下文 | 输出 | 并发 | 重复 | 请求数 | TPOT均值 ms | p50 | p95 | p99 | 首D token ms | 输出 tokens/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 1 | 1 | 4 | 164.240 | 163.808 | 165.761 | 166.003 | 297.804 | 5.847 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 1 | 2 | 4 | 162.446 | 162.133 | 163.468 | 163.628 | 308.867 | 5.887 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 1 | 3 | 4 | 163.567 | 163.397 | 164.246 | 164.354 | 310.374 | 5.848 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 2 | 1 | 8 | 161.807 | 161.820 | 161.913 | 161.920 | 297.416 | 11.857 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 2 | 2 | 8 | 162.408 | 161.553 | 165.445 | 165.445 | 293.782 | 11.830 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 2 | 3 | 8 | 159.509 | 159.288 | 160.811 | 160.812 | 291.149 | 12.035 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 4 | 1 | 16 | 162.300 | 162.286 | 162.892 | 162.895 | 317.904 | 23.302 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 4 | 2 | 16 | 163.680 | 162.592 | 167.720 | 167.727 | 327.172 | 23.063 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 4 | 3 | 16 | 162.628 | 162.526 | 163.350 | 163.351 | 310.010 | 23.309 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 8 | 1 | 32 | 158.466 | 158.204 | 160.115 | 160.278 | 329.108 | 47.663 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 8 | 2 | 32 | 158.199 | 158.198 | 158.946 | 159.010 | 328.153 | 47.748 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 8 | 3 | 32 | 157.872 | 157.829 | 158.448 | 158.507 | 328.418 | 47.836 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 16 | 1 | 64 | 163.205 | 163.074 | 164.447 | 164.450 | 365.386 | 92.042 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 16 | 2 | 64 | 162.943 | 162.872 | 163.607 | 164.407 | 365.658 | 92.169 |
| local64-cached-decode-tp1-dp8-epon-smoke | 4096 | 20 | 16 | 3 | 64 | 162.874 | 163.068 | 164.231 | 164.339 | 364.621 | 92.231 |

## 未纳入有效性能结果的测点

- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c32-r1: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c32-1795681054613013188`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c32-r2: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c32-1795681054613013188`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c32-r3: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c32-1795681054613013188`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c64-r1: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c64-1795681130593885717`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c64-r2: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c64-1795681130593885717`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c64-r3: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c64-1795681130593885717`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c128-r1: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c128-1795681280148867815`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c128-r2: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c128-1795681280148867815`
- local64-cached-decode-tp1-dp8-epon-smoke / local64-cached-decode-tp1-dp8-epon-smoke-l4096-o20-c128-r3: cache_residency_failed；证据 `/work/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/l4096-c128-1795681280148867815`
