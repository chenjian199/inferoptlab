# GLM-5.3-Flash-W8A8 在八卡 C500 上的独立部署

观察日期：2026-11-22，Asia/Shanghai。本次完成独立 vLLM-MetaX 0.32.0-dev 环境中的真实权重 TP8 文本生成，并冻结依赖镜像与配套源码、脚本。原 `dcc`、宿主机驱动/SDK、旧源码和标准模型权重保留。

**验收范围：V2 runner、4096 上下文、单序列、同步调度、eager。** 这是功能 smoke 验收，不是性能或全框架兼容性认证。MIM 鉴权成功，原 MIM 镜像未完整下载；本次成功环境由缓存基础镜像和官方 SDK/wheel 重建。

结构化入口：[case.json](case.json) · [问题与补丁](issues.md) · [资产与证据来源](artifacts.json) · [运行摘要](evidence/deployment-summary.json)。原操作材料仍位于项目 `glmf/deploy032/` 和 `glmf/audit_20261122/`。

## 环境和权重

| 项目 | 本次实际状态 |
|---|---|
| 硬件与系统 | 8×C500 64 GiB，Ubuntu 22.04.5，宿主驱动 3.8.30 |
| 独立目录与容器 | `/home/metax/glm53-vllm032`，容器 `glm53-vllm032` |
| 基础路线 | 已缓存的不可变 0.28 基底，新容器内安装 SDK 3.9.0.29 |
| 上游源码 | vLLM v0.32.0，commit `5df63a7203cdb9328d824a27b682e77c7b9928be`，干净源码 |
| 插件源码 | vLLM-MetaX v0.32.0-dev，commit `0962c8735ffe4795800030680311410848512b82`，加本案例三项修复 |
| Torch / Triton | `2.10.0+metax3.9.0.8` / `3.6.0+metax3.9.0.8` |
| mcoplib | `0.4.14+gf3794c4.maca3.9.0.31.torch2.10` |
| Python / Transformers / compressed-tensors | 3.12 / 5.17.0 / 0.17.0 |
| 实际导入 | `/work/src/vllm/vllm/__init__.py`，`/work/src/vllm-metax/vllm_metax/__init__.py` |
| 实际平台 | `MxsmlMacaPlatform` |
| 权重 | ModelScope `metax-tech/GLM-5.3-Flash-W8A8`，revision `6df7a9b0309e530094e29b2a6ced3e21bed6c16d` |

权重文件 59/59 校验，47 个 safetensors 分片；标准目录只读挂载到 `/models/GLM-5.3-Flash-W8A8`。量化为对称 per-channel INT8 权重与动态 per-token INT8 激活，另有 BF16 保留模块，不能称为全部张量 INT8。原 `metadata.total_size=[]` 异常未改写，加载按 weight_map；[哈希校验](evidence/weight-summary.json) 通过，但[结构检查](evidence/structure-summary.json) 保留 `complete=false` 和 `index total_size mismatch`，同时 `tensor_data_and_mapping_valid=true`。文件哈希与张量映射通过，不代表原索引元数据完全无误。

依赖最低驱动声明与实测结论分别保留于摘要。本机 3.8.30 驱动实际通过八卡计算、MCCL 和该配置的 TP8 推理，不外推到其他镜像/SDK。完整包清单在资产清单登记，不将名字中含 maca3.9.0.31 的 wheel 等同于容器 SDK 版本。

## MIM 与代理的实际结果

已有 MIM 凭据最终通过鉴权 HTTP 200 和 manifest HTTP 200。先前过期 bearer、匿名 token 无目标 pull 权限、配置凭据 401 都作为历史排查事实保留；本库不记录登录秘密，也不猜测手机账号对应的通用登录用户名。

目标大层下载继续超时/EOF，被测 Range 请求返回 200，未实现有效分段续传。Mihomo v1.19.34 使用认证回环代理，订阅由用户在服务器不回显输入；无认证代理/控制器分别返回 407/401。没有改全局代理、Docker daemon 或重启 Docker。代理建立不等于大镜像下载成功。

最终完成官方 SDK 的校验下载和 27 个配套私有 wheel 的哈希校验，走独立重建路线。原 MIM 镜像与本次依赖镜像分别登记；不存在“原 MIM 镜像拉取完成”的结论。

## 排障路径与三项修复

1. 权重加载后，MoE warmup 遇到上游 8 参数调用与 native 7 参数 schema 不匹配。增加严格 schema 门控桥接，只接受未请求 scatter 的旧 ABI。
2. 长 prefill 出现 `tuple.dtype`，INT8 indexer 的 native scorer 需要 Tensor Q；改 INT8 分支传参，其余分支保持 tuple。
3. 修复接口后仍有重复输出和长前缀答案错误。切换采样和 V2 同步单序列未解决；INT8 linear、稀疏 MLA、KDA、MoE 原语对参考的数值检查通过。
4. 逐层检查发现前三个 KDA 层有限，首个 MLA 层出现 NaN；进一步定位到 fused QKV A 投影及 scale。FP8 兼容加载器吞掉 INT8 `weight_scale`，导致正常 INT8 参数未初始化。修复加载所有权后，8 个 worker 各自 33 个 MLA INT8 scale 均有限且为正，三项真实生成通过。

V1 混合调度尝试曾非法访问显存，恢复后八卡计算通过；最终 scale 修复后未重测 V1。这次没有证明 V1 问题的根因或最终修复状态。具体症状、最小验证入口、补丁范围和移除条件见 [issues.md](issues.md)。

## 真实生成验收

TP=8，mp executor，BF16 非量化部分，compressed-tensors W8A8，safetensors，V2 runner，max_model_len=4096，max_num_seqs=1，max_num_batched_tokens=4096，gpu_memory_utilization=0.9，enforce_eager=True，async_scheduling=False，prefix cache 关闭，图像和视频输入关闭。indexer_kv_dtype 配置为 auto，实际 worker 验证为 INT8。

使用模型聊天模板、reasoning_effort=low，temperature=1、top_p=0.95、seed=0、max_tokens=1024。命令入口是 `bash /home/metax/glm53-vllm032/scripts/run_inference.sh`；此文档整理未再次执行远程推理。

| 请求 | 输入 token | 输出 token | 结果 |
|---|---:|---:|---|
| 中文介绍 | 20 | 272 | 正常中文介绍，stop |
| 算术 | 23 | 3 | `</think>2`，stop |
| 长前缀查找 | 2433 | 20 | 正确返回“青松”，stop |

进程 exit 0。权重加载约 184.47 秒，生成阶段约 57.39 秒，包含初始化/JIT 等影响；不作为性能基准。[生成证据](evidence/inference-summary.json) 保留参数、worker 来源与三项输出；[进程结果](evidence/inference_scale_fixed_run.json) 保留命令和退出码。

## 基线冻结与可复现范围

依赖镜像 `glm53-vllm032:verified-20261122`，image ID `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`。源码和脚本另外归档，远程位置及 SHA256 见 [artifacts.json](artifacts.json)。归档不含模型权重和代理订阅。恢复时必须同时满足对应源目录、编译产物、脚本和权重挂载，镜像不是单文件可运行交付。

一次性无网络新容器验证了实际导入、8 设备发现和 `pip check`，通过 exit 0；[回放检查](evidence/frozen_baseline_check.json) **没有覆盖重新加载完整模型并生成**。完整 TP8 结果属于原独立工作容器。本次完成时工作容器空闲，`dcc` 保留；这些是观察日状态，不是当前在线状态承诺。

## 后续待验证

并发、异步调度、图执行、超过 4K 上下文、多模态、性能基准、SGLang 对照、V1 修复后回归及新容器完整推理均不在本次验收范围。下一步算子优化从固定基线开始，一次改变一个因素，并新增实验记录。不得用这里的 3 个 smoke 请求代替模型质量评测或全框架升级认证。
