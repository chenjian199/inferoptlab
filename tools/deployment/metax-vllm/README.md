# vLLM-MetaX 构建与验证工具

为 InferOptLab 提供 vLLM 与 MetaX 插件的源码构建、容器封装和部署验证入口。工具记录源码提交、依赖哈希、运行参数及原始验证结果，供后续实验追溯。

所有命令均从 **inferoptlab 仓库根目录**执行。本文使用首版已验证的基础镜像、源码提交和依赖组合；仓库位置、模型目录及结果目录可按环境调整。构建不依赖特定 SSH 别名，但需要取得下述基础镜像。

## 功能与范围

- 下载固定提交的源码归档，校验 SDK 与 native wheel，生成构建上下文。
- 将 vLLM 和 MetaX 插件构建为 wheel，安装到镜像内的独立 Python 环境。
- 保存依赖锁、源码快照、补丁及构建证据。
- 提供设备通信检查、示例服务启动、响应检查及 AIPerf 冒烟测试。

当前构建配置针对 MetaX 软件栈，使用预编译的 Torch、Triton 和 mcoplib。`serve.py`、`check_gpu.py` 是 GLM-5.3-Flash-W8A8 八设备示例，启动参数固定为 TP8；尚不支持通过命令行切换任意模型或设备数量。其他部署方式应使用相应的部署配方和启动入口。

## 环境要求

| 阶段 | 要求 |
| --- | --- |
| 准备构建上下文 | Linux x86_64、Python 3.10+、tar；可访问 GitHub、MetaX 软件仓库 |
| 构建镜像 | Docker Engine、Buildx/BuildKit，启用 containerd image store；首版为 Docker 29.1.3、Buildx 0.39.1、BuildKit 0.26.2 |
| 基础镜像 | Debian/Ubuntu 系环境，具备 dpkg、patch、编译工具和 `/opt/conda/bin/python3`（Python 3.12）；具备 MACA 环境及 `/opt/maca` 符号链接 |
| 运行服务 | 与容器软件栈匹配的宿主驱动、设备访问权限及模型文件 |
| AIPerf 客户端 | Docker、上述基础镜像、本地 tokenizer 文件及可达的 HTTP 服务；Python 3.12 由容器提供 |

基础镜像通过 `BASE_IMAGE` 显式传入。当前 Dockerfile 使用 MACA、Conda 的既定容器路径，不能直接将任意 Ubuntu 或 CUDA 镜像作为替代。脚本仅在容器中安装用户态 SDK，宿主驱动由运行环境提供。首版运行验证使用八张 C500、宿主驱动 3.9.35；更换运行环境后应重新执行设备与模型检查。

## 版本配置

以下为首版实际构建并通过验证的配置：

| 组件 | 固定版本或身份 |
| --- | --- |
| 基础镜像 ID | `sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad` |
| vLLM 源码 | v0.32.0，`5df63a7203cdb9328d824a27b682e77c7b9928be` |
| MetaX 插件源码 | v0.32.0-dev，`0962c8735ffe4795800030680311410848512b82` |
| MACA 用户态 SDK | 3.9.0.29 |
| Python | 3.12 |
| Torch | `2.10.0+metax3.9.0.8` |
| Triton | `3.6.0+metax3.9.0.8` |
| mcoplib | `0.4.14+gf3794c4.maca3.9.0.31.torch2.10` |
| 服务端 Transformers | 首版安装结果为 5.19.0，见下述依赖锁说明 |
| AIPerf / 客户端 Transformers | 0.12.0 / 5.24.0 |

基础镜像原有标签为：

```text
172.17.0.57:5000/infer/deepseek-v4-flash-0731-w8a8:sglang0.5.14-maca.ai3.8.2.121-torch2.10-py312-ubuntu22.04-amd64-mim4.0.1
```

这是已有的 DeepSeek/SGLang 环境镜像，不是已确认未经修改的官方基础镜像。本文复用它的系统环境，在新 venv 中构建 vLLM。该标签来自内部仓库，不保证其他机器可以拉取；缺少镜像时，需要从有权限的仓库获取，或从已有机器通过 `docker save` / `docker load` 转移，再核对上述 ID。仅有 ID 不能从公网自动下载镜像。

首版在公开依赖齐备的 0.32 分支上完成验证。版本选择原因及检查日期见[版本选择记录](../../../experiments/evidence/metax-60-vllm-source-build/20261124/version-selection.json)，不能将该配置理解为自动跟随上游最新版本。

| 文件 | 配置内容 |
| --- | --- |
| [prepare.py](prepare.py) | vLLM 与 MetaX 插件的仓库和固定提交 |
| [fetch_dependencies.py](fetch_dependencies.py) | MACA SDK 版本与下载来源 |
| [native-wheels.json](native-wheels.json) | native wheel 版本、大小及 SHA-256 |
| [build_frameworks.py](build_frameworks.py) | 构建参数、依赖约束和安装检查 |
| [patches/](patches/) | 当前依赖组合所需的源码补丁 |

升级时应同时核对源码、SDK、Torch 和算子包的版本关系，并重新执行验证。仅修改镜像标签不会升级依赖。当前构建包含项目补丁，属于基于官方源码安装机制的定制构建。

`glm-w8a8.patch` 修复 W8A8 scale 加载和 INT8 sparse indexer 入参；`moe_align_legacy_abi.py` 对齐固定 mcoplib 的七参数 MoE alignment ABI。首版补丁哈希见[运行配方](../../../recipes/runtimes/metax60-vllm-glm53-source.yaml)。复现时应保留这些补丁，不能将无补丁源码视作同一个已验证配置。

## 构建镜像

以下命令使用 Bash，按首版已验证的构建方式执行。各步骤在同一会话中运行，任一步失败应先处理错误。基础镜像、源码和依赖保持上述固定配置；构建编号与仓库路径可以调整。

### 1. 设置参数

```bash
# 当前目录为 inferoptlab 仓库根目录。
PROJECT_ROOT="$(pwd -P)"
BUILD_ID="$(date +%Y%m%d-%H%M%S)"
BUILD_DIR="$PROJECT_ROOT/build/metax-vllm/$BUILD_ID"
RESULT_DIR="$PROJECT_ROOT/experiments/runs/deployment/$BUILD_ID"
IMAGE="inferoptlab/vllm-metax:0.32.0-glm53-c500-$BUILD_ID"
BASE_IMAGE_ID="sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad"
BASE_IMAGE="inferoptlab/metax-build-base:20261124"

# 确认固定基础镜像已存在，再建立与 Dockerfile 一致的本地标签。
docker image inspect "$BASE_IMAGE_ID" --format '{{.Id}}'
docker tag "$BASE_IMAGE_ID" "$BASE_IMAGE"
```

`BUILD_DIR` 保存源码、依赖和构建上下文，必须为空或不存在。`RESULT_DIR` 保存部署验证结果。每次重新构建使用新的编号，保留已有产物。

### 2. 准备源码和依赖

```bash
python3 tools/deployment/metax-vllm/prepare.py "$BUILD_DIR"
```

该步骤下载 GitHub 固定提交的源码压缩包并解压，不包含 `.git` 历史。SDK 和 native wheel 下载后执行 SHA-256 校验；补丁在 Docker 构建阶段应用。

源码归档下载地址为：

```text
https://codeload.github.com/vllm-project/vllm/tar.gz/5df63a7203cdb9328d824a27b682e77c7b9928be
https://codeload.github.com/MetaX-MACA/vLLM-metax/tar.gz/0962c8735ffe4795800030680311410848512b82
```

SDK 和 native wheel 来自 `https://repos.metax-tech.com/r/`；首版共下载并校验 60 个 SDK deb 和 27 个 native wheel。公共 Python 依赖使用 `https://pypi.tuna.tsinghua.edu.cn/simple`。源码归档的首版 SHA-256 见[来源记录](../../../experiments/evidence/metax-60-vllm-source-build/20261124/evidence/sources.json)。

`prepare.py` 拒绝覆盖非空目录。若依赖下载中断，可对已生成的构建上下文重新运行下载器，复用通过校验的安装包：

```bash
python3 tools/deployment/metax-vllm/fetch_dependencies.py "$BUILD_DIR"
```

### 3. 构建并载入镜像

```bash
docker buildx build \
  --network=host \
  --progress=plain \
  --build-arg "BASE_IMAGE=$BASE_IMAGE" \
  --output type=image,compression=zstd,compression-level=1 \
  --tag "$IMAGE" \
  "$BUILD_DIR"
```

此处恢复首版使用的 BuildKit image exporter 和 zstd level 1，要求 Docker 使用 containerd image store。构建结果保存在本地，不推送镜像仓库；构建后用 `docker image inspect "$IMAGE"` 确认镜像可用。

构建阶段按以下设置生成 wheel，再正常安装到 `/opt/vllm-env`：

- 上游 vLLM：`VLLM_TARGET_DEVICE=empty`，版本标记为 `0.32.0`。
- MetaX 插件：版本标记为 `0.32.0+g0962c873`，`USE_PRECOMPILED_KERNEL=1`，使用固定 mcoplib。
- 两者均使用 `pip wheel --no-deps --no-build-isolation`；禁用 Rust frontend，构建后执行 `pip check`。

SDK 安装包和下载缓存通过 BuildKit 临时挂载使用；最终镜像保留运行环境、源码、构建产物和证据。

native 依赖固定版本和哈希；公共 Python 依赖在构建时解析，实际安装版本保存为 `requirements.lock.txt`。首版完整安装清单见[依赖锁记录](../../../experiments/evidence/metax-60-vllm-source-build/20261124/evidence/image-build/requirements.lock.txt)。当前脚本不会自动读取该历史清单锁定全部公共依赖，因此复建后应核对清单，不能保证不同日期的环境或镜像逐字节一致。

首版产物标签为 `inferoptlab/vllm-metax:0.32.0-glm53-c500-20261124`，镜像 ID 为 `sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b`。新构建使用独立标签；该 ID 用于识别历史产物，不是新构建必须产生的值。

## 验证部署

以下为仓库自带的 **GLM 八设备示例**。运行前应确认模型、设备数量和驱动满足该示例要求。构建镜像本身不执行 GPU 检查。

### 1. 设置运行参数

```bash
export MODEL_DIR='<absolute-model-directory>'
SERVICE_PORT=18081
SERVICE_URL="http://127.0.0.1:$SERVICE_PORT"
CONTAINER_NAME="inferoptlab-vllm-$BUILD_ID"
mkdir -p "$RESULT_DIR"
```

将 `MODEL_DIR` 替换为实际模型绝对路径。客户端使用 `SERVICE_URL` 连接服务；它必须是客户端可访问的地址。

### 2. 检查设备与通信

```bash
docker run --rm --network=host --shm-size=16g \
  --device=/dev/mxcd --device=/dev/dri \
  --mount "type=bind,source=$BUILD_DIR,target=/work" \
  --mount "type=bind,source=$RESULT_DIR,target=/work/evidence" \
  --entrypoint /opt/vllm-env/bin/torchrun \
  "$IMAGE" \
  --standalone --nproc-per-node=8 /work/scripts/check_gpu.py
```

`check_gpu.py` 检查 BF16 计算、all-reduce 和 all-gather，逐 rank 输出结果。

### 3. 启动示例服务

```bash
python3 tools/deployment/metax-vllm/serve.py \
  --image "$IMAGE" \
  --model "$MODEL_DIR" \
  --name "$CONTAINER_NAME" \
  --port "$SERVICE_PORT" \
  --cache-dir "$RESULT_DIR/cache" \
  --output "$RESULT_DIR/service"
```

启动器检查设备是否空闲，创建独立容器并等待 HTTP 就绪。失败或超时时停止本次容器并保存日志；成功时保持服务运行。模型以只读方式挂载。

示例固定使用 `glm53-flash` 服务名、TP8、4096 上下文、单请求调度、eager 模式和 `glm47` reasoning parser，关闭 prefix cache 与 MTP。服务仅监听回环地址，并启用本机配置回读。这套配置用于验证部署流程，未进行吞吐调优。

首版其余运行设置为 PP1、DP1、EP 关闭、BF16 计算、compressed-tensors W8A8、safetensors 加载、max_num_batched_tokens 4096、显存比例 0.9、chunked prefill 开启、async scheduling 与 custom all-reduce 关闭。环境变量为 `VLLM_USE_V2_MODEL_RUNNER=1`、`USE_PRECOMPILED_KERNEL=1`、`OMP_NUM_THREADS=4`。完整参数由 `serve.py` 与 Dockerfile 提供，启动时记录到 `service/launch.json`。

### 4. 检查 API 响应

```bash
python3 tools/deployment/metax-vllm/check_api.py \
  --url "$SERVICE_URL" \
  --output "$RESULT_DIR/api"
```

检查中文响应、算术和上下文提取，保存请求、响应及判定结果。该检查使用固定服务名和 GLM 采样参数，不替代模型精度评测。

## AIPerf 冒烟测试

在服务保持运行时执行。首版客户端复用上述固定基础镜像的 Python 3.12，在独立 `/work/venv` 中安装 AIPerf 0.12.0 和 Transformers 5.24.0，不向该 venv 安装 Torch。以下步骤保留这一方式，宿主无需额外安装 Python 3.12。

### 1. 准备客户端

客户端目录默认位于仓库下，`project/` 保存执行时的项目代码快照。已有按同一布局准备的客户端时，可指定其目录并跳过安装步骤。

```bash
CLIENT_ROOT="$PROJECT_ROOT/build/aiperf-client"
mkdir -p "$CLIENT_ROOT/project"
cp -R benchmark tools contracts schemas "$CLIENT_ROOT/project/"

docker run --rm --pull=never \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$CLIENT_ROOT,target=/work" \
  -e HOME=/work \
  --entrypoint /opt/conda/bin/python3 \
  "$BASE_IMAGE_ID" -m venv /work/venv

docker run --rm --pull=never \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$CLIENT_ROOT,target=/work" \
  -e HOME=/work \
  --entrypoint /work/venv/bin/python \
  "$BASE_IMAGE_ID" -m pip install \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  -r /work/project/benchmark/requirements.txt 'transformers==5.24.0'
```

### 2. 执行请求与归档

```bash
RUN_ID="glm53-vllm-smoke-$(date +%Y%m%d-%H%M%S)"
python3 tools/deployment/metax-vllm/run_client.py \
  --client-root "$CLIENT_ROOT" \
  --image "$BASE_IMAGE_ID" \
  --model "$MODEL_DIR" \
  --url "$SERVICE_URL" \
  --run "$RUN_ID"

# 仅在客户端命令成功后归档；每次使用新的 RESULT_DIR。
cp -a "$CLIENT_ROOT/experiments/$RUN_ID" "$RESULT_DIR/aiperf"
cp -a "$CLIENT_ROOT/launches/$RUN_ID" "$RESULT_DIR/aiperf-launch"
```

`run_client.py` 在容器中调用 `smoke_client.py`，只读挂载模型，并局部清空离线模式变量，避免 AIPerf 0.12 将本地 tokenizer 路径按远端仓库名解析。服务端环境不受影响。原始结果保留在 `CLIENT_ROOT/experiments/<run-id>/`；外层命令、日志和退出码保留在 `CLIENT_ROOT/launches/<run-id>/`。

| 场景 | 输入 tokens | 输出 tokens | 并发 | 正式请求 | 独立预热 |
| --- | ---: | ---: | ---: | ---: | ---: |
| prefill-smoke | 128 | 1 | 1 | 4 | 1 |
| short-smoke | 128 | 32 | 1 | 4 | 1 |
| long-smoke | 1024 | 32 | 1 | 4 | 1 |

检查实际请求数、服务端 token 计数、TTFT 及导出状态。固定输出长度包含 reasoning tokens；TTFT 表示首次模型输出。单 token 输出场景仍包含调度与 HTTP 开销，不代表纯 prefill kernel 时间。正式性能评测使用 [benchmark/load](../../../benchmark/load/README.md) 的计划与归档流程。

客户端 venv 的容器路径固定为 `/work/venv`，不要直接在宿主激活。单独登录客户端机器时需要重新设置路径和服务地址变量，且该机器须具备基础镜像和可读取的模型 tokenizer。

完成全部验证后停止服务：

```bash
docker stop "$CONTAINER_NAME"
```

## 目录与产物

```text
inferoptlab/
├── tools/deployment/metax-vllm/     # 工具源码、Dockerfile、补丁和依赖清单
├── build/metax-vllm/<build-id>/
│   ├── src/                       # 下载并解压的源码
│   ├── inputs/                    # 源码归档、SDK、native wheels
│   ├── scripts/                   # 构建脚本快照
│   ├── patches/                   # 补丁快照
│   └── evidence/                  # 下载来源与哈希
└── experiments/runs/deployment/<build-id>/
    ├── gpu8/                      # 逐 rank 检查结果
    ├── service/                   # 启动参数、模型配置、服务日志
    ├── api/                       # 请求、响应及校验结果
    ├── aiperf/                    # 数据集、命令、日志、原始指标
    ├── aiperf-launch/             # 客户端外层命令、退出码和日志
    └── cache/                     # 当前环境的 JIT 缓存
```

镜像内 `/opt/built-wheels` 保存构建产物，`/opt/build-evidence` 保存依赖锁与来源记录，`/opt/vllm-env` 为运行环境。构建目录和验证目录默认不纳入 Git；需归档的实验按项目证据管理流程登记。

## 参考

- [MetaX 官方安装说明](https://vllm-metax.readthedocs.io/en/latest/getting_started/installation/en.html)
- [实际构建与验证记录](../../../docs/metax-60-glm53-vllm-source-build-20261124.md)：已验证的镜像、版本组合、设备信息与实测结果。
- [部署配方](../../../recipes/deployments/)：具体模型与运行配置。
- [GLM 扫描计划](../../../recipes/plans/benchmark/glm53-vllm/README.md)：复用 workload、部署和模型规约进行启动资格检查与 AIPerf 扫描；`run_scan.py` 使用独立客户端环境执行现有压测入口。远端应使用完整项目副本，包括结果登记依赖的 `diagnosis/`。
- [实验数据管理](../../../experiments/README.md)：结果归档与基线登记。
