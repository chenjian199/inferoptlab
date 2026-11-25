# metax-60 的 GLM-5.3-Flash-W8A8 启动检查

后续已通过源码构建的 vLLM-MetaX 镜像跑通八卡 GLM 服务与 AIPerf 流程，见[源码构建与复现结果](metax-60-glm53-vllm-source-build-20261124.md)。本文保留此前 SGLang 镜像检查的历史结果，下面的空闲状态和启动失败不代表当前机器状态。

2026-11-24 通过 `ssh metax-60` 实际检查 `ubuntu@172.17.0.60`（`gpu-node-060`）。模型文件已具备，8 张 C500 在检查前后均无 GPU 进程；现有 SGLang 镜像尚未完成该模型的权重加载。已执行两次独立启动检查，没有生成 GLM 性能结果。

## 已确认的条件

| 项目 | 本次实际结果 |
|---|---|
| 登录和目录 | 免密登录成功；用户 ubuntu；`/home/ubuntu/CJ_workspace` 可写 |
| GPU | 8 × C500，每卡 65536 MiB；开始和结束时均为 `no process found` |
| 驱动与宿主 MACA | 3.9.35 / 3.8.3.17；容器内 Torch 为 `2.10.0+metax3.8.2.2` |
| 主存 | 总量约 755 GiB，初始可用约 730 GiB |
| 本地磁盘 | `/home/ubuntu` 所在卷初始剩余约 272 GiB |
| 权重目录 | `/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8` |
| 权重检查 | 索引列出的 47 个分片均存在、可读文件头，合计 305.91 GiB；tokenizer 可读；未重新计算全部 payload 哈希 |
| 模型配置 | `glm5_next` / `Glm5NextForConditionalGeneration`，text 为 `glm5_next_text` |
| 服务状态 | 检查前无运行中的 Docker 容器；两次启动检查均未达到 HTTP ready |

模型配方见 [cluster-glm53-flash-w8a8](../recipes/models/glm/glm-5.3-flash/cluster-glm53-flash-w8a8.yaml)。旧硬件配方记录的是此前占用状态，本次空闲状态单独保留在新证据中。

## 实际启动发现的问题

检查了基础镜像 `sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad` 和新增镜像 `sha256:e636eb63ab7408be62ce15e3dd25fb2ffb38649074fb2fb5852c42a8c8e1047d`。它们的 SGLang 包版本元数据相同，但实际导入源码不同：前者从 site-packages 导入，未检索到目标架构实现；后者从 `/src/python` 导入，含 GLM-5.3 实现。因此不能仅凭 `pip show sglang` 判断兼容性。

新增镜像通过了启动帮助、SGLang 自带 `Glm5NextConfig` 解析、C500 设备识别和 `sglang.srt.models.glm5_next` 模块导入。直接使用 Transformers 5.12 的 `AutoConfig` 不认识 `glm5_next`，但 SGLang 自带配置类可以解析它；不能把这项直接 AutoConfig 检查失败单独当作服务必然不可启动的结论。

两次启动使用相同的模型目录和新增镜像：TP8、PP1、EP1、DP1、4096 上下文、并发上限 1、chunk 4096、显存比例 0.85、BF16 计算、compressed-tensors、关闭 prefix cache/CUDA Graph/custom all-reduce。它们是加载检查配置，不是性能最优配置。模型目录只读挂载；未启用旧机器故障排查时的 `MCCL_P2P_DISABLE=1`。

### 第一次：镜像继承了 DeepSeek 专用加载器

默认环境包括：

```text
SGLANG_C500_DSV41_MIXED_LOAD=1
SGLANG_C500_DSV41_PRECISION_REFERENCE=1
```

`loader.py` 因第一个开关调用 `/work/c500_model.py`，其实现仅接受 `deepseek_v41`，实际报错：

```text
ValueError: C500 mixed loader only supports deepseek_v41
```

该次日志与完整启动 argv 在 [startup/](../experiments/evidence/metax-60-glm-readiness/20261124/startup/)。远端目录为 `/home/ubuntu/CJ_workspace/glm53-flash-preflight-20261124T043546Z`。

### 第二次：关闭专用开关后，GLM 量化加载仍失败

仅将两个开关改为 `0`，重新创建独立容器后进入通用权重加载路径，实际报错：

```text
glm5_next.py:1789 -> linear.py:478 -> parameter.py:69
ValueError: Unsupported copy between dtypes:
target.dtype=torch.int8, loaded_weight.dtype=torch.bfloat16
```

这确认了目标参数的预期精度与读入 tensor 不一致。GLM 权重包含 BF16 非量化模块；接下来需定位具体 tensor，核对模块名称映射、compressed-tensors 分组及 ignore 列表。当前日志没有给出冲突 tensor 名称，不能直接认定是哪一个模块，也不能把 BF16 强转 INT8 当作已经修复。

该次日志与完整启动 argv 在 [startup-glm/](../experiments/evidence/metax-60-glm-readiness/20261124/startup-glm/)。远端目录为 `/home/ubuntu/CJ_workspace/glm53-flash-preflight-20261124T043845Z`。父进程退出码为 0，但子进程报错、HTTP 未就绪，所以记录为 `startup_failed`，不以容器退出码认定成功。

两次测试容器均已停止、删除；日志和结果保留，GPU 进程清单恢复为空。已有停止的业务容器未更改，宿主驱动和模型文件未更改。

## AIPerf 客户端

`/home/ubuntu/CJ_workspace/aiperf.tar` 已导入，镜像名是 `pagoda-aiperf-runner-ascend:v0.0.1`，实际平台为 `linux/arm64`。在当前 `linux/amd64` 机器上执行 Python 已报 `exec format error`，不能直接用于本机压测。原 tar 和导入的镜像均保留。

压测客户端可独立于模型服务安装。项目固定 `aiperf==0.12.0`；官方提供 [虚拟环境安装方式](https://pypi.org/project/aiperf/0.12.0/)。本机系统 Python 为 3.10.12，默认没有 pip，因此使用已有 amd64 镜像中的 Python 3.12，在独立目录准备客户端，不修改宿主 Python 或推理镜像。安装与 CLI 核验结果保存在 [client 证据](../experiments/evidence/metax-60-glm-readiness/20261124/client/)。

**客户端已安装并通过 CLI 核验，尚未对 GLM 服务发送压测请求。** 新目录为 `/home/ubuntu/CJ_workspace/inferoptlab-client-20261124`，使用上述 amd64 基础镜像中的 Python 3.12 与独立 `/work/venv`。`aiperf --version` 返回 `0.12.0`，`aiperf profile --help` 成功；完整依赖已保存为 `requirements.lock.txt`。虚拟环境依赖容器内 Python 路径，请通过包装脚本运行，而不是直接在宿主激活它。

```bash
ssh metax-60
cd /home/ubuntu/CJ_workspace/inferoptlab-client-20261124
./aiperf.sh --version
./aiperf.sh profile --help
```

`aiperf.sh` 只映射客户端目录和只读模型目录，不映射 GPU；可通过 host network 请求本机服务。模型在客户端容器中的路径为 `/model`，输出可保存在 `/work` 下。

首次通过 PyPI 安装在依赖获取阶段超过 240 秒，复用缓存后又报 `No matching distribution found for narwhals>=1.15.1`。单独检查发现该 PyPI 索引返回 200 但接收内容超时、不完整；清华镜像索引可完整返回。第三次使用 `https://pypi.tuna.tsinghua.edu.cn/simple` 安装成功。三次记录分别保存在 `install.log`、`install-retry.log`、`install-mirror.log`，临时安装容器均已清理。后续复现应使用本次 lock 文件或准备完整 wheelhouse，不能只固定顶层 AIPerf 版本而忽略依赖差异。

## 建议的复现顺序

1. **先选择服务基线。** 以“复现原 metax 已运行的 GLM”为目标时，优先准备同一套 vLLM-MetaX 镜像和源码。原机器仍可访问，镜像 `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285` 存在、为 amd64、约 39.08 GB；配套 `src/vllm` 和 `src/vllm-metax` 分别约 209 MiB 和 130 MiB。它们采用 editable 安装，必须与镜像一起迁移、核对指纹，不能只复制镜像。旧环境为 MACA 3.9、Torch MetaX 3.9、Transformers 5.17；与本节点驱动组合需先独立核验。旧 [运行配方](../recipes/runtimes/metax-vllm-glm53-observed.yaml) 提供实际设置，但其中用于专项分析的 worker 扩展、禁用 P2P 等条件不应不加区分地复制到新基线。
2. **如继续使用当前 SGLang，先解决 loader。** 保持两个 DeepSeek 专用开关关闭，定位 BF16→INT8 冲突 tensor，修复正确的量化例外与名称映射，再核验加载后的 dtype、scale 和输出正确性。这属于框架适配工作，不是继续调整并发或 TP 即可解决的问题。
3. **启动最小 HTTP 服务。** 先明确文本模式与多模态禁用方式，使用 TP8/PP1/DP1、短上下文、单请求、关闭 MTP 和缓存复用，确认 ready、`/v1/models`、非流式与流式生成、实际 token 计数及服务配置回读；EP 需要作为明确配置验证。原 metax 的成功离线 LLM 记录不等同于本节点 HTTP 服务已验证。
4. **接入小规模 AIPerf。** 先并发 1、2、4，每点总请求数为并发的 4 倍，预热独立计数，检查逐请求原始导出、失败计数、实际输入/输出 token 和指标复算。保存新的 model/hardware/runtime/deployment 绑定及客户端 lock 文件。
5. **再展开 P/D 扫描。** 当前 P 计划的输出为 1 token、禁用 prefix cache；并发为 1/2/4/8/16/32/64/128、请求倍率 4、重复 3 次。D 要完成缓存清空、相同请求集填充与重放，并核实逐请求 cache-hit 计数；未满足缓存规约的请求不能作为纯 Decode 结果。当前计划共有 3 个候选部署、2 种长度，先资格验证一个部署，再扩大到完整矩阵。

计划入口为 [Prefill](../recipes/plans/benchmark/glm53-flash-prefill.yaml) 与 [Decode](../recipes/plans/benchmark/glm53-flash-decode.yaml)，方法见 [缓存重放流程](benchmark-cache-replay.md)。这些仍是候选计划；本次失败的 SGLang 启动没有被标记为已验证部署。若服务换成 vLLM，还需验证相应适配器的配置读取与 D 阶段缓存控制接口。

完整检查证据、探针和文件指纹见 [metax-60-glm-readiness/20261124](../experiments/evidence/metax-60-glm-readiness/20261124/)。本次没有进行正式性能测量，也没有把其他机器的硬件实测指标复制到该节点。
