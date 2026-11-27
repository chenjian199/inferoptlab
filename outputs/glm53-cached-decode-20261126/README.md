# GLM Flash 缓存续接 Decode 测试

计划：[cached-decode.yaml](../../recipes/plans/benchmark/glm53-vllm/cached-decode.yaml)。
实现与口径：[CACHED-DECODE.md](../../benchmark/load/CACHED-DECODE.md)。

快速查看：[本轮性能简版（TTFT、TPOT、E2E、输出与请求吞吐量）](quick-read.md)。
简版合并同配置的重复测量，延迟 P95 从原始请求重新计算；快照时间与排除项见表内说明。

| 项目 | 设置 |
|---|---|
| 部署 | TP8/DP1/EP8、TP1/DP8/EP8 |
| 原始上下文 | 4096、16384、65536 token |
| D 新生成输出 | 20、50 token；不包括 P 生成的 seed |
| 并发 | 1、2、4、8、16、32、64、128 |
| 请求数 | 并发 × 4；每槽四次顺序请求 |
| 重复 | 3；共 288 个计划性能点 |
| 数据 | 各并发槽独立上下文，固定 DP 路由 |
| 有效性 | 原上下文全命中、每步 query=1、零抢占、路由正确、输出数正确 |
| 容量不足 | 保留证据，单独标记，不混入有效性能表 |

这里的 100% 是 **L 个原始上下文 token 全部命中**。HTTP 输入是 L+1，额外的一个是
P 产生的 seed，D 从它开始计算。不能把接口的 L/(L+1) 命中率写成 100%，
也不能把这项模拟写成真实 PD 网络传输测试。

## 已归档的初步证据

- [当前扫描性能表](scan-r3/README.md)：本地下载快照，按点保留均值、p50、p95、p99；远端继续执行时需重新下载更新。
- r3 已通过 DP8 的全部 8 个 rank 路由、缓存和 KDA/FlashMLA Decode 路径验证，并开始产出通过逐请求验证的性能点。

- [三种长度的缓存证据](preflight-evidence/proof-tp8/results.json)：TP8+EP，4K/16K/64K 各重放三次，9/9 的原始上下文全命中。
- [AIPerf 实跑验证](preflight-evidence/observed-proof-4k-c2-1795667946786800114/validation.json)：4K→20，C=2，共 8 请求，全部通过接口 token 数与逐请求调度验证。
  每请求 20 次单 token 计算，零抢占。该预检观察了 KDA 路径；正式矩阵增加 FlashMLA 路径验证。
- 该预检 TPOT 均值 153.181 ms，p95 153.530 ms，输出吞吐 12.406 token/s。
  这是单个流程验证点，不是两种部署的完整比较结果。
- [重复性检查](preflight-evidence/repeatability/summary.json)：冷请求本身也存在逐 token 差异；未宣称数值精度验收通过。
- [完整初步证据压缩包](preflight-evidence.tar.gz)。

## 启动问题记录

1. DP8 初次启动在 MLA 临时缓冲申请 4.25 GiB 时 OOM。请求分块由 4096 改为 1024 后通过启动内存检查。
2. 随后预热触发原生 MHA gather 的维度限制：仅支持 320/576，而此模型缓存维度为 512。
   r3 使用当前镜像原有的 `sparse_mla_force_mqa: true` 后，已通过全 rank 预热和 Decode 路径验证；通过独立 RuntimeSpec 记录。
3. AIPerf 的 payload-bytes 格式会丢失逐请求请求头。已改用保留头部的 conversation 格式，并关闭 mmap 缓存复用；实跑验证请求 ID 和路由证据。

运行中的快照来自 [scan-status.json](scan-status.json)，它记录采集时的状态，**不是实时页面**。
本机更新状态：

```powershell
python outputs/glm53-cached-decode-20261126/poll_scan.py --attempt r3
python outputs/glm53-cached-decode-20261126/collect_scan.py --attempt r3
```

当前远端输出目录：
`/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3`。
该目录的 `state.json` 是执行状态，`README.md` 是逐点更新的性能表。
旧的普通 Prefill+Decode 扫描保持停止，旧数据的计时口径没有改写。

本地后台采集程序 `watch_scan.py` 每 60 秒检查状态，每新增 6 个有效测点或扫描结束时下载结果。
VPN 不通时标记 `observation_unavailable` 并重试，不据此终止远端任务。
[monitor-r3.json](monitor-r3.json) 是最近一次检查；进程信息在 `monitor-r3-launch.json`。
该采集程序只观察和下载：若服务/扫描失败，会标记 `needs_attention`，保留故障证据；不自动改配方或跳过验证。
本机休眠或关闭会影响自动下载，但不会终止远端扫描。
