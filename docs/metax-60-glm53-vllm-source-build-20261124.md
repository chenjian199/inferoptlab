# metax-60：GLM-5.3-Flash-W8A8 源码构建与流程复现

2026-11-24 已在 `ubuntu@172.17.0.60` 完成源码下载、独立 vLLM 镜像构建、八卡检查、GLM 加载和 AIPerf 流式请求验证。交付时容器 `inferoptlab-glm53-vllm-r1` 正在运行，占用本机 8 张 C500；本机 `http://127.0.0.1:18081/health` 返回 200。宿主驱动和模型文件未修改。

本次完成的是部署与测试流程验证，尚未形成正式性能基线或精度验收。完整证据在 [20261124/](../experiments/evidence/metax-60-vllm-source-build/20261124/)，机器可读汇总在 [qualification.json](../experiments/evidence/metax-60-vllm-source-build/20261124/qualification.json)。

## 交付位置

| 内容 | 位置 |
| --- | --- |
| 构建、检查、启动、客户端入口 | [tools/deployment/metax-vllm/](../tools/deployment/metax-vllm/README.md) |
| 实际运行环境配方 | [metax60-vllm-glm53-source.yaml](../recipes/runtimes/metax60-vllm-glm53-source.yaml) |
| 实际八卡部署配方 | [metax60-tp8-smoke.yaml](../recipes/deployments/glm53-flash/c500/vllm/metax60-tp8-smoke.yaml) |
| 证据来源登记 | [source-metax60-glm53-source-build.yaml](../recipes/sources/source-metax60-glm53-source-build.yaml) |
| 远端源码、依赖、构建日志 | `/home/ubuntu/CJ_workspace/glm53-vllm-build-20261124` |
| 独立客户端与本项目代码快照 | `/home/ubuntu/CJ_workspace/inferoptlab-client-20261124` |
| 成功的远端 AIPerf 运行 | 上述客户端目录下 `experiments/glm53-vllm-source-20261124-r2/` |
| 权重只读挂载来源 | `/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8` |

镜像名：

```text
inferoptlab/vllm-metax:0.32.0-glm53-c500-20261124
```

本机 Docker 记录的不可变镜像 ID：

```text
sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b
```

Docker 报告镜像大小约 35.29 GB；完成时宿主 `/home` 所在文件系统还剩约 137 GiB。没有向镜像仓库推送。

## “最新版本”的实际边界

检查时上游最新正式版为 vLLM 0.34.0，MetaX master 为 `fb69a4ed938c9353469514db2e9253109a98f594`，插件声明 0.33.0；但该 master 所需的 Torch `2.13.0+metax3.10.1.3`、mcoplib `0.4.16` 尚未出现在公开 MACA Python 索引中。因此这次使用公开依赖齐备、包含目标 GLM 实现的 `v0.32.0-dev` 分支，不能把交付镜像称为上游最新版本。

| 组件 | 实际版本 |
| --- | --- |
| vLLM 源码 | v0.32.0，`5df63a7203cdb9328d824a27b682e77c7b9928be` |
| MetaX 插件源码 | `0962c8735ffe4795800030680311410848512b82`，另加下述三项显式修复 |
| 安装后的 vLLM / 插件 | `0.32.0+empty` / `0.32.0+g0962c873.maca3.9.0.29.torch2.10.0` |
| MACA SDK / 宿主驱动 | 容器 3.9.0.29 / 宿主 3.9.35 |
| Torch / Triton | `2.10.0+metax3.9.0.8` / `3.6.0+metax3.9.0.8` |
| mcoplib | `0.4.14+gf3794c4.maca3.9.0.31.torch2.10` |
| 服务端 Transformers | 5.19.0 |
| 客户端 | AIPerf 0.12.0，Transformers 5.24.0，无 Torch |

版本选择记录见 [version-selection.json](../experiments/evidence/metax-60-vllm-source-build/20261124/version-selection.json)。安装依据：[MetaX 官方文档](https://vllm-metax.readthedocs.io/en/latest/getting_started/installation/en.html)、[固定提交源码](https://github.com/MetaX-MACA/vLLM-metax/tree/0962c8735ffe4795800030680311410848512b82)、[SDK 仓库](https://repos.metax-tech.com/)。升级到 master 需要先取得匹配的厂商依赖，再重做加载、算子和响应验证。

源码最终直接下载到目标机，避免通过 Windows 中转大文件。vLLM 和插件由源码构建为正常安装的 wheel，Torch、Triton、mcoplib 等底层依赖使用厂商发布的预编译包。共校验 60 个 SDK deb 和 27 个 native wheel 的 SHA-256。容器内创建全新 `/opt/vllm-env`，`pip check` 通过；导入路径为该环境的 site-packages，不依赖宿主 checkout。底层系统复用机器上已有的 MetaX 基础镜像，不要求已有 vLLM 镜像。

## 为跑通 GLM 做的修复

1. W8A8 权重 scale 加载：避免 INT8 scale 被 FP8 回退分支忽略。
2. INT8 sparse indexer：传入该算子实际要求的 Tensor，而不是 FP4 路径的 tuple。
3. MoE alignment：与固定 mcoplib 版本的七参数 ABI 对齐，明确拒绝该接口不支持的 scatter 输出。

补丁位于工具目录的 `patches/`，哈希记录在运行配方与汇总中；原始来源是项目已有 GLM 实测证据。它们只对应这套固定依赖，不能据此声称新版本所有算子接口均已支持。

接口首次检查还暴露了 reasoning 配置问题：GLM-5.3 的 `enable_thinking:false` 无法关闭思考；缺少 reasoning parser 时，思考与最终答案混在 content 中。最终启动加入 `--reasoning-parser glm47`，响应检查使用 checkpoint 的 temperature 1、top_p 0.95，并为思考和最终答案合计预留 1024 tokens。三项检查均获得正常终止的最终答案。最初失败记录保留在 `evidence/api/`，通过记录在 `evidence/api-reasoning/`。

AIPerf 首两次在发请求前失败：其 0.12 离线模式会将本地 `/model` 当仓库名交给 `snapshot_download`，而环境变量字符串 `0` 仍被当作真。客户端最终将 `HF_HUB_OFFLINE`、`TRANSFORMERS_OFFLINE` 设为空，继续读取本地只读 tokenizer；未修改 AIPerf 安装包。失败记录保存在 `client-attempt0/`、`client-attempt1/`。

## 实际服务配置

- TP8、PP1、DP1；未启用 EP，配方记为 EP1。
- BF16 计算、compressed-tensors W8A8、safetensors，加载全部 47 个分片，约 305.91 GiB。
- max_model_len 4096、max_num_seqs 1、max_num_batched_tokens 4096、显存比例 0.9。
- eager、同步调度、chunked prefill；关闭 prefix cache、custom all-reduce、MTP；图像与视频请求限额为 0。
- 服务实际回读的 attention block_size 为 **640**，mamba_block_size 为 **4096**。这些是框架选择的实际值，不能用惯常的 16/32 代替。
- `USE_PRECOMPILED_KERNEL=1`、`VLLM_USE_V2_MODEL_RUNNER=1`、`OMP_NUM_THREADS=4`；完整 argv 和镜像环境版本均有记录。

完整启动命令见 `evidence/service-reasoning/launch.json`；实际配置回读见 `evidence/server-config-reasoning.json`。服务打印的 KV cache 可支持并发数只是容量推算，**不是并发性能实测**。当前 max_num_seqs 为 1，不能直接用此配置开展 1–128 并发性能比较。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| 隔离镜像导入、设备枚举 | 通过，8 张 GPU |
| BF16 矩阵计算、MCCL all-reduce / all-gather | 8/8 ranks 通过 |
| MLA scale 加载回归 | 12 cases 通过 |
| MoE alignment CPU/GPU 对照 | 24 cases 通过 |
| INT8 sparse indexer 对照 | 6 cases 通过 |
| 中文介绍、算术、上下文口令提取 | 3/3 通过，最终答案与 reasoning 分离 |
| AIPerf 流式请求 | 12 个正式请求通过，另有 3 个独立预热请求 |

AIPerf 使用本项目 `benchmark.load.dataset` 生成并验证真实 tokenizer 长度，通过 `benchmark.load.adapters.aiperf` 构造请求。每组并发 1、总请求数为并发 × 4，按服务端 usage 核对输入/输出 tokens，保留请求、响应、数据集及全部原始导出。

| 场景 | 输入 / 输出 tokens | 正式请求数 | 平均 TTFT（ms） | 平均请求延迟（ms） | 输出吞吐（tokens/s） |
| --- | ---: | ---: | ---: | ---: | ---: |
| prefill-smoke | 128 / 1 | 4 | 209.21 | 209.21 | 4.75 |
| short-smoke | 128 / 32 | 4 | 209.17 | 4757.54 | 6.72 |
| long-smoke | 1024 / 32 | 4 | 218.89 | 4743.71 | 6.74 |

这是保守 eager 配置下的小样本流程检查。`prefill-smoke` 是输出 1 token 的端到端代理测试，包含调度、网络和首 token，不能视为纯 prefill kernel 时间。固定长度请求可在思考过程中结束，输出长度包括 reasoning tokens；TTFT 是首次模型输出延迟，不能解释成首次最终答案延迟。没有进行纯 decode 全缓存重放、并发扫描、TP/EP 参数扫描或正式精度数据集评测。GPU 压测遥测未配置；八卡功能检查不能替代持续利用率采样。

## 现在如何访问和复测

在本地 PowerShell 建立转发并保持该终端开启：

```powershell
ssh -N -L 18081:127.0.0.1:18081 metax-60
```

另一个终端查看模型列表：

```powershell
curl.exe http://127.0.0.1:18081/v1/models
```

模型名称为 `glm53-flash`，OpenAI base URL 为 `http://127.0.0.1:18081/v1`。服务只监听远端回环地址；开发配置回读接口仅供本机验证使用。

登录后可查看日志：

```bash
docker logs --tail 80 inferoptlab-glm53-vllm-r1
```

复测命令见[工具说明](../tools/deployment/metax-vllm/README.md)。服务已运行时只执行 API 与客户端检查，无需再次启动服务。

已将客户端入口同步至远端构建目录。服务运行时，以下命令可以直接在 `metax-60` 执行；每次换一个新的 `--run` 名称以保留旧结果：

```bash
python3 /home/ubuntu/CJ_workspace/glm53-vllm-build-20261124/scripts/run_client.py \
  --client-root /home/ubuntu/CJ_workspace/inferoptlab-client-20261124 \
  --model /mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8 \
  --run glm53-vllm-smoke-NEW
```

完成使用后释放 GPU：

```bash
docker stop inferoptlab-glm53-vllm-r1
```

停止后可用 `docker start inferoptlab-glm53-vllm-r1` 恢复同一容器，并等待 `/health` 返回 200。旧的 `inferoptlab-glm53-vllm` 容器为未配置 reasoning parser 的首次尝试，已停止并留存，不应作为最终入口启动。

后续正式测量前还需要冻结目标场景、并发和参数矩阵，完成模型配方中仍未验证的来源/权重与精度约束，再生成正式 BenchmarkPlan。本次新增部署配方使用 `management: external`：先由部署入口启动并检查服务，benchmark 消费该现成服务，不应调用旧 SGLang 启动入口。

## 仓库校验

新增脚本通过 Python 编译检查，新增运行环境与部署配方通过 `validate --sources`。全库 `python tools/specs.py validate` 通过，共 336 份文档。全库加 `--sources` 时仍报告 11 个既有 SourceDocument 附件缺失（历史 PDF、图片和设计文档）；未伪造附件或改写原哈希，因此不能声称全库来源核验通过。本次新增 SourceDocument 及其汇总证据哈希已单独验证。
