# Cached Decode 扫描

更新时间：2026-11-26T06:41:24.650323+00:00；状态：preparing

每槽独立上下文；原始上下文 L 全部命中，线上的请求为 L+1（额外一个 P 端生成的 seed）。
输出是 D 端新生成的 token，seed 不计入输出。未测量 P→D 传输；客户端时延包含调度、排队及流式传输。

| 部署 | 上下文 | 输出 | 并发 | 重复 | 请求数 | TPOT均值 ms | p50 | p95 | p99 | 首D token ms | 输出 tokens/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 1 | 1 | 4 | 165.332 | 164.951 | 166.948 | 167.205 | 300.653 | 5.807 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 1 | 2 | 4 | 170.515 | 170.580 | 176.077 | 176.110 | 305.539 | 5.638 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 1 | 3 | 4 | 163.550 | 163.115 | 165.842 | 166.112 | 297.387 | 5.871 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 1 | 1 | 4 | 160.983 | 160.044 | 163.496 | 163.977 | 295.398 | 6.108 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 1 | 2 | 4 | 159.862 | 159.708 | 160.413 | 160.505 | 299.165 | 6.147 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 1 | 3 | 4 | 158.542 | 158.417 | 159.400 | 159.485 | 290.573 | 6.202 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 2 | 1 | 8 | 160.092 | 160.074 | 160.629 | 160.669 | 293.650 | 11.986 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 2 | 2 | 8 | 159.469 | 159.553 | 159.721 | 159.749 | 306.811 | 11.981 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 2 | 3 | 8 | 160.688 | 160.795 | 161.395 | 161.419 | 294.979 | 11.940 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 2 | 1 | 8 | 159.265 | 159.071 | 159.870 | 159.885 | 292.528 | 12.347 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 2 | 2 | 8 | 159.398 | 159.412 | 159.579 | 159.587 | 293.595 | 12.336 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 2 | 3 | 8 | 159.471 | 159.488 | 159.624 | 159.639 | 294.285 | 12.329 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 4 | 1 | 16 | 162.466 | 162.548 | 163.174 | 163.188 | 309.426 | 23.334 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 4 | 2 | 16 | 163.015 | 163.055 | 163.373 | 163.374 | 312.203 | 23.247 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 4 | 3 | 16 | 163.102 | 162.478 | 165.019 | 165.020 | 312.970 | 23.232 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 4 | 1 | 16 | 162.781 | 162.676 | 163.221 | 163.226 | 314.411 | 24.028 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 4 | 2 | 16 | 162.515 | 162.358 | 163.127 | 163.134 | 325.911 | 24.033 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 4 | 3 | 16 | 160.347 | 160.346 | 160.489 | 160.504 | 321.833 | 24.357 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 8 | 1 | 32 | 160.732 | 160.656 | 161.625 | 161.679 | 333.475 | 46.996 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 8 | 2 | 32 | 164.022 | 163.983 | 164.725 | 164.845 | 341.927 | 46.038 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 8 | 3 | 32 | 163.738 | 163.681 | 164.759 | 164.822 | 340.507 | 46.126 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 8 | 1 | 32 | 160.066 | 160.072 | 160.542 | 160.577 | 328.539 | 48.844 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 8 | 2 | 32 | 161.645 | 160.755 | 165.262 | 165.269 | 331.959 | 48.367 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 8 | 3 | 32 | 163.477 | 163.758 | 165.516 | 165.575 | 340.647 | 47.797 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 16 | 1 | 64 | 166.096 | 165.966 | 166.967 | 167.344 | 368.033 | 90.531 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 16 | 2 | 64 | 165.844 | 166.229 | 167.262 | 167.815 | 368.402 | 90.648 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 20 | 16 | 3 | 64 | 169.452 | 169.652 | 175.163 | 175.352 | 374.593 | 88.767 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 16 | 1 | 64 | 163.000 | 162.934 | 163.309 | 164.536 | 378.037 | 95.511 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 16 | 2 | 64 | 164.807 | 164.420 | 166.355 | 166.547 | 366.497 | 94.640 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 4096 | 50 | 16 | 3 | 64 | 164.495 | 164.329 | 165.544 | 165.843 | 366.595 | 94.810 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 1 | 1 | 4 | 168.093 | 168.053 | 168.607 | 168.636 | 311.396 | 5.700 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 1 | 2 | 4 | 170.655 | 172.190 | 174.852 | 174.868 | 328.575 | 5.595 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 1 | 3 | 4 | 161.862 | 161.683 | 162.853 | 162.950 | 301.931 | 5.915 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 1 | 1 | 4 | 158.557 | 158.227 | 159.475 | 159.644 | 314.534 | 6.182 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 1 | 2 | 4 | 157.921 | 157.984 | 158.085 | 158.085 | 297.481 | 6.219 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 1 | 3 | 4 | 159.156 | 159.329 | 159.569 | 159.587 | 312.186 | 6.162 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 2 | 1 | 8 | 161.403 | 161.448 | 161.889 | 161.984 | 319.913 | 11.798 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 2 | 2 | 8 | 161.967 | 161.755 | 163.607 | 163.772 | 320.234 | 11.760 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 2 | 3 | 8 | 161.188 | 161.264 | 161.521 | 161.609 | 312.921 | 11.838 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 2 | 1 | 8 | 161.661 | 161.473 | 162.503 | 162.541 | 313.368 | 12.137 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 2 | 2 | 8 | 162.582 | 162.202 | 164.349 | 164.395 | 313.055 | 12.073 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 2 | 3 | 8 | 161.956 | 161.694 | 163.001 | 163.037 | 313.043 | 12.118 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 4 | 1 | 16 | 161.449 | 161.743 | 162.243 | 162.279 | 335.778 | 23.275 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 4 | 2 | 16 | 161.711 | 161.230 | 163.479 | 163.638 | 345.668 | 23.175 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 4 | 3 | 16 | 164.083 | 164.273 | 165.676 | 166.023 | 346.661 | 22.867 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 4 | 1 | 16 | 164.572 | 164.599 | 165.584 | 165.648 | 333.055 | 23.719 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 4 | 2 | 16 | 165.519 | 165.559 | 166.450 | 166.483 | 333.702 | 23.587 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 4 | 3 | 16 | 162.180 | 162.091 | 166.144 | 166.251 | 330.131 | 24.067 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 8 | 1 | 32 | 159.119 | 159.170 | 160.534 | 160.737 | 356.507 | 47.078 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 8 | 2 | 32 | 160.012 | 159.848 | 162.192 | 162.450 | 355.072 | 46.857 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 20 | 8 | 3 | 32 | 159.277 | 159.005 | 161.421 | 161.711 | 370.322 | 46.844 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 8 | 1 | 32 | 161.905 | 162.121 | 164.715 | 164.737 | 366.604 | 48.082 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 8 | 2 | 32 | 160.016 | 159.984 | 160.353 | 160.450 | 354.889 | 48.690 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 16384 | 50 | 8 | 3 | 32 | 161.573 | 162.016 | 162.355 | 162.422 | 368.237 | 48.166 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 1 | 1 | 4 | 159.660 | 159.056 | 164.071 | 164.363 | 337.295 | 5.916 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 1 | 2 | 4 | 155.948 | 155.838 | 156.291 | 156.348 | 333.675 | 6.050 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 1 | 3 | 4 | 172.048 | 172.037 | 172.478 | 172.517 | 348.761 | 5.511 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 1 | 1 | 4 | 156.780 | 156.744 | 157.096 | 157.116 | 344.893 | 6.222 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 1 | 2 | 4 | 156.628 | 156.620 | 156.728 | 156.739 | 332.551 | 6.237 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 1 | 3 | 4 | 156.808 | 156.642 | 157.266 | 157.350 | 331.903 | 6.230 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 2 | 1 | 8 | 159.952 | 159.144 | 163.164 | 163.271 | 362.749 | 11.659 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 2 | 2 | 8 | 159.167 | 158.876 | 160.375 | 160.512 | 361.612 | 11.781 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 2 | 3 | 8 | 158.887 | 158.864 | 160.471 | 160.779 | 360.300 | 11.805 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 2 | 1 | 8 | 161.029 | 160.970 | 161.511 | 161.537 | 359.000 | 12.079 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 2 | 2 | 8 | 159.906 | 159.844 | 160.485 | 160.558 | 370.234 | 12.171 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 2 | 3 | 8 | 158.915 | 158.999 | 159.712 | 159.743 | 360.653 | 12.228 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 4 | 1 | 16 | 159.646 | 159.451 | 162.532 | 162.567 | 400.147 | 23.167 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 4 | 2 | 16 | 158.115 | 158.180 | 161.051 | 162.103 | 401.367 | 23.357 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 4 | 3 | 16 | 161.285 | 161.322 | 163.352 | 163.589 | 404.939 | 22.926 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 4 | 1 | 16 | 162.950 | 162.504 | 164.463 | 164.813 | 389.724 | 23.796 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 4 | 2 | 16 | 159.153 | 159.148 | 160.509 | 160.540 | 404.386 | 24.322 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 4 | 3 | 16 | 158.676 | 158.783 | 160.621 | 161.037 | 429.217 | 24.318 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 8 | 1 | 32 | 159.460 | 158.576 | 164.105 | 164.289 | 468.257 | 45.468 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 8 | 2 | 32 | 160.457 | 159.156 | 166.394 | 167.914 | 508.691 | 44.767 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 20 | 8 | 3 | 32 | 161.757 | 157.496 | 178.387 | 181.417 | 534.551 | 44.135 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 8 | 1 | 32 | 165.291 | 163.993 | 173.895 | 175.616 | 530.658 | 46.261 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 8 | 2 | 32 | 161.061 | 160.342 | 163.936 | 165.557 | 504.256 | 47.544 |
| glm53-vllm-cached-decode-tp1-dp8-ep8 | 65536 | 50 | 8 | 3 | 32 | 163.153 | 162.349 | 166.991 | 169.001 | 510.690 | 46.934 |

## 未纳入有效性能结果的测点

- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c32-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c32-1795670212750093363`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c32-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c32-1795670212750093363`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c32-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c32-1795670212750093363`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c32-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c32-1795670212750093363`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c32-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c32-1795670212750093363`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c32-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c32-1795670212750093363`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c64-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c64-1795670294076320327`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c64-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c64-1795670294076320327`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c64-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c64-1795670294076320327`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c64-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c64-1795670294076320327`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c64-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c64-1795670294076320327`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c64-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c64-1795670294076320327`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c128-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c128-1795670454261118483`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c128-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c128-1795670454261118483`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o20-c128-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c128-1795670454261118483`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c128-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c128-1795670454261118483`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c128-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c128-1795670454261118483`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l4096-o50-c128-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l4096-c128-1795670454261118483`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c16-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c16-1795671661770373633`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c16-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c16-1795671661770373633`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c16-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c16-1795671661770373633`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c16-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c16-1795671661770373633`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c16-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c16-1795671661770373633`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c16-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c16-1795671661770373633`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c32-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c32-1795671795073534832`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c32-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c32-1795671795073534832`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c32-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c32-1795671795073534832`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c32-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c32-1795671795073534832`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c32-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c32-1795671795073534832`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c32-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c32-1795671795073534832`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c64-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c64-1795672052200066472`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c64-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c64-1795672052200066472`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c64-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c64-1795672052200066472`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c64-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c64-1795672052200066472`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c64-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c64-1795672052200066472`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c64-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c64-1795672052200066472`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c128-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c128-1795672557833461432`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c128-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c128-1795672557833461432`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o20-c128-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c128-1795672557833461432`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c128-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c128-1795672557833461432`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c128-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c128-1795672557833461432`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l16384-o50-c128-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l16384-c128-1795672557833461432`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l65536-o20-c16-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l65536-c16-1795674798418696719`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l65536-o20-c16-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l65536-c16-1795674798418696719`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l65536-o20-c16-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l65536-c16-1795674798418696719`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l65536-o50-c16-r1: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l65536-c16-1795674798418696719`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l65536-o50-c16-r2: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l65536-c16-1795674798418696719`
- glm53-vllm-cached-decode-tp1-dp8-ep8 / glm53-vllm-cached-decode-tp1-dp8-ep8-l65536-o50-c16-r3: cache_residency_failed；证据 `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/l65536-c16-1795674798418696719`
