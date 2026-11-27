# 四机环境证据明细

本文件由 `build_comparison.py` 从本地采集快照生成。时间及历史/当前区分见 [分析报告](README.md)。

## 服务端实际配置

| 参数 | 60 EP on | 61 EP on | 61 EP off | 64 EP off | 65 EP off |
|---|---|---|---|---|---|
| model.max_model_len | `73728` | `73728` | `73728` | `16896` | `65557` |
| model.enforce_eager | `True` | `False` | `False` | `True` | `False` |
| model.dtype | `torch.bfloat16` | `torch.bfloat16` | `torch.bfloat16` | `torch.bfloat16` | `torch.bfloat16` |
| model.quantization | `compressed-tensors` | `compressed-tensors` | `compressed-tensors` | `compressed-tensors` | `compressed-tensors` |
| parallel.tensor_parallel_size | `1` | `8` | `8` | `1` | `4` |
| parallel.pipeline_parallel_size | `1` | `1` | `1` | `1` | `1` |
| parallel.data_parallel_size | `8` | `1` | `1` | `8` | `2` |
| parallel.enable_expert_parallel | `True` | `True` | `False` | `False` | `False` |
| parallel.all2all_backend | `allgather_reducescatter` | `allgather_reducescatter` | `allgather_reducescatter` | `allgather_reducescatter` | `allgather_reducescatter` |
| parallel.disable_custom_all_reduce | `True` | `True` | `True` | `True` | `True` |
| parallel._api_process_count | `1` | `1` | `1` | `1` | `2` |
| scheduler.max_num_batched_tokens | `1024` | `4096` | `4096` | `2048` | `4096` |
| scheduler.max_num_seqs | `16` | `128` | `128` | `16` | `64` |
| scheduler.enable_chunked_prefill | `True` | `True` | `True` | `True` | `True` |
| scheduler.async_scheduling | `False` | `False` | `False` | `False` | `False` |
| scheduler.stream_interval | `1` | `1` | `1` | `1` | `1` |
| cache.enable_prefix_caching | `True` | `True` | `True` | `True` | `True` |
| cache.gpu_memory_utilization | `0.9` | `0.9` | `0.9` | `0.915` | `0.9` |
| cache.block_size | `4352` | `640` | `640` | `4352` | `1152` |
| cache.mamba_block_size | `256` | `256` | `256` | `256` | `16` |
| cache.prefix_match_unit | `16` | `16` | `16` | `16` | `None` |
| cache.mamba_cache_mode | `align` | `align` | `align` | `align` | `align` |
| cache.num_gpu_blocks | `232` | `2343` | `2320` | `152` | `2154` |
| cache.kv_cache_size_tokens | `82235` | `1381957` | `1368391` | `24694` | `1069771` |
| compilation.mode | `0` | `0` | `0` | `0` | `0` |
| compilation.cudagraph_mode | `0` | `[2, 1]` | `[2, 1]` | `0` | `[2, 1]` |
| compilation.cudagraph_capture_sizes | `[]` | `[1, 2, 4, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 248, 256]` | `[1, 2, 4, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 248, 256]` | `[]` | `[1, 2, 4, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128]` |
| VLLM_USE_V2_MODEL_RUNNER | True | True | True | not exposed | True |
| 证据 | [server-info.json](files/60/4d88d6e55e-server-info.json) | [server-info.json](files/61/d72c9f19f0-server-info.json) | [server-info.json](files/61/196f3bc276-server-info.json) | [server-info.json](files/64/8f6caa64f8-server-info.json) | [server-info.json](files/65/8b1d1d7888-server-info.json) |

65 列为已有 4K 运行保存的 server-info；与稍后抓到的进程启动参数存在差异，不能当成同一时刻的完整配置。

## 源码与二进制

四机以下 11 个采样源码文件的 SHA-256 完全一致；这不是全源码逐文件一致证明。

| 文件 | SHA-256 |
|---|---|
| `vllm_metax/models/deepseek_v4/metax/flashmla.py` | `ba6b904ceeacfe3505b499317f75bf735b89eec0719bff1acbf4dbe13a069f9e` |
| `vllm_metax/models/deepseek_v4/sparse_mla.py` | `f5e171a175086567d65da11eaf749bddfdc60dab17877cca5a024a721150184f` |
| `vllm_metax/models/deepseek_v41/metax/flashmla.py` | `6a131b3980da8ff5605d89bc64ee621ca91070aca171ab3ec70fef7a3eacf519` |
| `vllm_metax/models/deepseek_v41/sparse_mla.py` | `29e288b40578ac858550d5dbf6e4a532362c0975dca36c7c5ed836095dac123f` |
| `vllm_metax/models/glm5next/common/model.py` | `77b5576b12fcb3d36d922ecc4f967f47f203514c2401d32bfdc89ad78b5bb5e3` |
| `vllm_metax/models/glm5next/metax/sparse_indexer.py` | `13775d9c88b8a419b0eb2f01af7722df1cd9160abf45c32f62b81273ef51fa6b` |
| `vllm_metax/patch/bugfix/__init__.py` | `3db4d3de1ac846e3867fbb813f132d2c284a093e0a287cc7275768bc35d1209f` |
| `vllm_metax/patch/bugfix/moe_align_legacy_abi.py` | `0a54d539f60406e94c5756dab11840304d7e4f407883006cfc55411f853a071e` |
| `vllm_metax/v1/attention/backends/mla/flashmla.py` | `fb81c32d46d2d4db606805254dc632dbc2c4d5bf5530e22449a3eef1b4a1fae7` |
| `vllm_metax/v1/attention/backends/mla/flashmla_sparse.py` | `4bb6a9de73ddbf7a47e9010a32cc18f0493b358224ed80b5f649a2bf3cc529c5` |
| `vllm_metax/v1/attention/ops/flashmla.py` | `5304ebc327574bf46956137d358d5605e77f23012270cd95f408d75499b398bf` |

各机器完整采样指纹：[60](60-fingerprint_60.json), [61](61-fingerprint_61.json), [64](64-fingerprint_64.json), [65](65-fingerprint_65.json)

## 61 原始性能数据核对

18/18 行与 `outputs/TP8.md` 的 TTFT/TPOT/E2E 均值和 P95、两类吞吐量及请求数在显示精度上完全一致。每行 engine/profile 验证均通过。

| EP | 输入 | 并发 | TTFT ms 平均/P95 | TPOT ms 平均/P95 | E2E ms 平均/P95 | 输出 tok/s | 请求 req/s | 原始数据 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| off | 4096 | 1 | 28.446/34.380 | 18.754/18.776 | 384.768/391.121 | 51.768 | 2.588 | [profile_export_aiperf.json](files/61/24f1bdc4ec-profile_export_aiperf.json) |
| off | 4096 | 2 | 43.354/52.435 | 20.006/20.176 | 423.475/432.563 | 93.595 | 4.680 | [profile_export_aiperf.json](files/61/2487718a12-profile_export_aiperf.json) |
| off | 4096 | 4 | 51.156/66.938 | 21.058/21.434 | 451.260/463.064 | 176.089 | 8.804 | [profile_export_aiperf.json](files/61/96cb11b562-profile_export_aiperf.json) |
| off | 4096 | 8 | 67.619/87.578 | 23.083/23.820 | 506.189/521.133 | 314.480 | 15.724 | [profile_export_aiperf.json](files/61/144043ce21-profile_export_aiperf.json) |
| off | 16384 | 1 | 38.277/42.984 | 18.443/18.530 | 388.687/392.527 | 51.042 | 2.552 | [profile_export_aiperf.json](files/61/ff3b3ca344-profile_export_aiperf.json) |
| off | 16384 | 2 | 51.705/66.716 | 20.023/20.195 | 432.150/445.216 | 91.372 | 4.569 | [profile_export_aiperf.json](files/61/6c48b53347-profile_export_aiperf.json) |
| off | 16384 | 4 | 67.456/92.215 | 21.275/21.903 | 471.671/490.329 | 167.901 | 8.395 | [profile_export_aiperf.json](files/61/5c27cdef3f-profile_export_aiperf.json) |
| off | 65536 | 1 | 89.046/98.624 | 17.231/17.762 | 416.428/424.885 | 47.084 | 2.354 | [profile_export_aiperf.json](files/61/6701e26578-profile_export_aiperf.json) |
| off | 65536 | 2 | 83.644/114.996 | 19.657/19.932 | 457.120/493.707 | 85.425 | 4.271 | [profile_export_aiperf.json](files/61/6495646da6-profile_export_aiperf.json) |
| on | 4096 | 1 | 32.671/37.375 | 23.461/23.496 | 478.422/483.697 | 41.667 | 2.083 | [profile_export_aiperf.json](files/61/3a455e6a74-profile_export_aiperf.json) |
| on | 4096 | 2 | 52.315/62.801 | 25.279/25.404 | 532.618/540.873 | 74.465 | 3.723 | [profile_export_aiperf.json](files/61/088ec084ad-profile_export_aiperf.json) |
| on | 4096 | 4 | 61.344/78.728 | 26.500/26.756 | 564.852/582.769 | 140.796 | 7.040 | [profile_export_aiperf.json](files/61/773f169ff5-profile_export_aiperf.json) |
| on | 4096 | 8 | 77.292/97.513 | 28.031/28.717 | 609.875/629.538 | 261.124 | 13.056 | [profile_export_aiperf.json](files/61/87cf0ffed2-profile_export_aiperf.json) |
| on | 16384 | 1 | 41.966/46.292 | 23.040/23.111 | 479.733/483.476 | 41.422 | 2.071 | [profile_export_aiperf.json](files/61/b30021dc48-profile_export_aiperf.json) |
| on | 16384 | 2 | 58.307/70.821 | 25.109/25.254 | 535.370/545.705 | 73.852 | 3.693 | [profile_export_aiperf.json](files/61/e711d022b1-profile_export_aiperf.json) |
| on | 16384 | 4 | 76.702/103.457 | 26.287/26.995 | 576.157/596.533 | 137.644 | 6.882 | [profile_export_aiperf.json](files/61/07734aab61-profile_export_aiperf.json) |
| on | 65536 | 1 | 80.598/87.591 | 22.204/22.270 | 502.466/506.822 | 39.155 | 1.958 | [profile_export_aiperf.json](files/61/e033b0b547-profile_export_aiperf.json) |
| on | 65536 | 2 | 89.816/115.591 | 24.403/24.593 | 553.476/577.630 | 70.640 | 3.532 | [profile_export_aiperf.json](files/61/20bf7bf120-profile_export_aiperf.json) |

## 启动命令及日志定位

| 机器 | 远端路径 | 本地证据 |
|---|---|---|
| 60 | `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/snapshot.json` | [snapshot.json](files/60/13a23b2f58-snapshot.json) |
| 60 | `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/server-1795668837263403759/server-info.json` | [server-info.json](files/60/4d88d6e55e-server-info.json) |
| 60 | `/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/server-1795668837263403759/launch.json` | [launch.json](files/60/c55f8ae935-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/state.json` | [state.json](files/61/0acb2150aa-state.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/snapshot.json` | [snapshot.json](files/61/5300a65d42-snapshot.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678275910185444/launch.json` | [launch.json](files/61/8d360ca456-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678275910185444/server.log` | [server.log](files/61/b35339108a-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678275910185444/server-info.json` | [server-info.json](files/61/d72c9f19f0-server-info.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678993553431615/launch.json` | [launch.json](files/61/cb769a38cf-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678993553431615/server.log` | [server.log](files/61/ce078c6fda-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678746416495635/launch.json` | [launch.json](files/61/c3a7dbc51b-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678746416495635/server.log` | [server.log](files/61/c49f3f12f5-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678507175934353/launch.json` | [launch.json](files/61/21239e78ca-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-on/server-1795678507175934353/server.log` | [server.log](files/61/39f91d90e6-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677672009216451/launch.json` | [launch.json](files/61/11c06ac775-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677672009216451/server.log` | [server.log](files/61/6124801fcc-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795678107184327403/launch.json` | [launch.json](files/61/c3278345f4-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795678107184327403/server.log` | [server.log](files/61/c35b5472cd-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677461210839831/launch.json` | [launch.json](files/61/8d5c1e2fb6-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677461210839831/server.log` | [server.log](files/61/41a74e103b-server.log) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677461210839831/server-info.json` | [server-info.json](files/61/196f3bc276-server-info.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677888494752857/launch.json` | [launch.json](files/61/36327f0189-launch.json) |
| 61 | `/tmp/lyq-cached061-formal/experiments/tp8-graph20-formal/glm53-vllm-cached-decode-061-tp8-graph20-ep-off/server-1795677888494752857/server.log` | [server.log](files/61/46d5dbece6-server.log) |
| 64 | `/data/c500-operator-reproduction-20261125/inferoptlab-local64-latest-20261126/project/experiments/runs/cached64-full-4k-epon/local64-cached-decode-tp1-dp8-epon-smoke/server-1795680481793601580/launch.json` | [launch.json](files/64/0263483784-launch.json) |
| 64 | `/data/c500-operator-reproduction-20261125/inferoptlab-local64-latest-20261126/project/experiments/runs/cached64-full-4k-epoff/local64-cached-decode-tp1-dp8-epoff-smoke/server-1795679612852538559/server-info.json` | [server-info.json](files/64/8f6caa64f8-server-info.json) |
| 64 | `/data/c500-operator-reproduction-20261125/inferoptlab-local64-latest-20261126/project/experiments/runs/cached64-full-4k-epoff/local64-cached-decode-tp1-dp8-epoff-smoke/server-1795679612852538559/launch.json` | [launch.json](files/64/ad0daf3801-launch.json) |
| 65 | `/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795680151385883427/server-info.json` | [server-info.json](files/65/8b1d1d7888-server-info.json) |
| 65 | `/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795680151385883427/launch.json` | [launch.json](files/65/f307e65579-launch.json) |
| 65 | `/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795679721046534175/server-info.json` | [server-info.json](files/65/5cf5cbc5e3-server-info.json) |
| 65 | `/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795679721046534175/launch.json` | [launch.json](files/65/0a8bc78f15-launch.json) |
| 65 | `/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/state.json` | [state.json](files/65/868f6568a6-state.json) |
| 65 | `/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/state.json` | [state.json](files/65/a97695cabf-state.json) |
