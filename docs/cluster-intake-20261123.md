# 2026-11-23 集群清点与小模型流程验证

## 四台新节点：文件可用，运行环境尚未齐备

已免密登录 `metax-60 / 61 / 64 / 65`，分别创建 `/home/ubuntu/CJ_workspace`。四台节点都在运行现有 `dsv41-anhui` SGLang 服务；本次只采集清单、读取权重元数据，并启动不映射 GPU 的临时镜像检查容器，没有停止现有服务或执行 GPU 性能测试。

| 项目 | 四台节点的实际观测 |
|---|---|
| GPU | 每台 8 × MetaX C500，单卡 64 GiB，共 32 卡 |
| CPU | 每台双路 Intel Xeon Gold 6530，128 逻辑 CPU |
| 主存 | 每台 Linux 可见约 755.45 GiB |
| 系统 | Ubuntu 22.04.4，内核 5.15.0-112-generic |
| 驱动 / MACA / mx-smi | 3.9.35 / 3.8.3.17 / 2.3.4 |
| PCIe 当前链路 | 32 GT/s × 16；这是链路属性，不是实测传输带宽 |
| GPU 可用性 | 采集时均被已有服务占用；健康认证未执行 |

硬件证据位于 `experiments/evidence/metax-four-node-inventory/1.0.0/`，对应每台 host 和每张卡的配方位于 `recipes/hardware/metax-four-node-inventory-*.yaml`。这里记录了真实的序号、板卡序列号、BDF、NUMA、CPU 亲和性、显存和链路；没有把原 `metax` 的硬件性能测量复制到新集群。

新驱动未返回 `vram driver reserved`，规约现支持 `driver_reserved_bytes: null`，明确表示未知，不填零。

## 模型文件

以下路径在四台节点均可访问，配置哈希一致。逐一检查索引所列权重文件、文件长度及头部可读性；在共享路径上另完成一次所有 safetensors 头部与索引核对。未计算全部数百 GiB 权重 payload 的哈希，也未启动 GLM 验证加载。

| 模型 | 共享目录（相对于 `/mnt/ufs1/models/models/`） | 权重文件 | 文件总大小 | 配方 |
|---|---|---:|---:|---|
| Qwen3-0.6B | `Qwen/Qwen3-0.6B` | 1 | 1.40 GiB | `cluster-qwen3-06b` |
| GLM-5.3-Flash-W8A8 | `metax-tech/GLM-5.3-Flash-W8A8` | 47 | 305.91 GiB | `cluster-glm53-flash-w8a8` |
| GLM-5.3-W4A8 | `metax-tech/GLM-5.3-W4A8` | 80 | 361.95 GiB | `cluster-glm53-w4a8` |
| GLM-5.3-W8A8 | `metax-tech/GLM-5.3-W8A8` | 80 | 703.95 GiB | `cluster-glm53-w8a8` |

Flash 是 45 层、hidden 4096、288 专家/top-8，包含 34 层线性注意力与 11 层稀疏注意力；完整版是 78 层、hidden 6144、256 专家/top-8。W4A8 实际是 Linear W8A8 与 FusedMoE W4A8 混合分组，不能将所有权重都理解为 4 bit。完整版 W8A8 的权重文件已超过单节点 512 GiB 显存，部署还需要额外考虑 KV cache 与运行时开销。

新配方按家族与具体模型归档在 `recipes/models/<family>/<model>/`，详见 [模型目录](../recipes/models/README.md)；元数据与采集脚本位于 `experiments/evidence/model-intake/`。模型导入入口为 `python -m tools.import_inspected_model`，必须提供 `--family` 和 `--model` 归档参数，支持此次实际出现的 dense 非量化、无索引单文件、混合量化及 MoE 模型。LLMC 的 YAML 包含 Python 对象标签，导入器只读取 JSON 配置，不执行这些标签。

## 镜像和工具

检查范围为每台宿主机默认 Python/PATH，以及每台 12 个唯一 Docker 镜像的默认 `python3` 环境。此范围之外的其他虚拟环境不作“已安装/未安装”的推断。

| 组件 | 四台新节点 | 原 `metax` |
|---|---|---|
| SGLang | 已找到，且现有服务在运行；新镜像元数据为 `0.5.14+detached.bde79bde7.maca3.8.2.121` | 本次流程选择 vLLM |
| vLLM | 检查范围内未找到包/CLI | 已找到 `0.32.0+empty` MetaX 构建 |
| AIPerf | 检查范围内未找到包/CLI | 工具镜像已有 0.13.0，项目协议固定 0.12.0，另建隔离环境 |
| GLM 加载资格 | 未验证 | 本次仅验证 Qwen 小模型 |

四台都有镜像 ID `sha256:91b2504601a1d2bdc2f4b057127258311df95d1d9c7f7aa2b270c60e5d4848e3`，SGLang 模块定位到 `/src/python/sglang/__init__.py`；Torch 为 `2.10.0+metax3.8.2.2`、Transformers 为 `5.12.0`。镜像存在不等于能够加载所有 GLM-5.3 变体；尤其模型配置标注 Transformers 5.16.1，仍需逐模型验证对应实现和量化 loader。

旧镜像 `sha256:641be9b5d27dfbc85b582dc8b2871edb28ec39b7aac60b10b8d7ecce2c6b7b0e` 同时存在 SGLang `0.5.12+maca3.8.2.7` 与 `0.3.1+mx.dev.0.5.19.2ad2ac45f4.maca0` 元数据，遍历顺序不同会给出不同的 `metadata.version()` 结果。后续不能用这一返回值单独锁定版本。

逐节点原始检查结果见 `experiments/evidence/cluster-runtime-intake/20261123/<host>/`。可复用探针为 `tools/hardware/probes/runtime.py`：在 Linux 主机执行 `python3 runtime.py --model /absolute/model/path`；默认审计本地全部镜像，可用重复 `--image sha256:...` 限定或 `--skip-images` 只查宿主机与模型。探针保存所有包版本候选和模块来源，区分“包元数据存在”与“模块能够定位”；它不证明模型已成功加载。

## 原 metax 小模型验证

工作目录：`/home/metax/CJ_workspace/inferoptlab-intake-20261123`。

模型为 `/NFS_62/Models/Qwen_Series/Qwen3-0.6B`，部署 GPU0、TP/PP/EP/DP 均为 1，监听 `127.0.0.1:18080`，最大上下文 12288、最大运行请求 4、显存比例 0.15、关闭 prefix cache、单 token 流式返回。服务容器使用 `--enforce-eager`，此配置用于验证流程，不代表调优后的性能。

vLLM 镜像 `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285` 采用 editable 安装，必须同时挂载 `/home/metax/glm53-vllm032:/work:ro`。只有镜像 ID 不足以完整锁定服务代码，Runtime 配方保留相应冻结阻塞项。该节点 `/dev/mxcd` 仅 root 可读写，测试容器采用默认容器用户访问设备，没有修改宿主机设备权限。

计划 `recipes/plans/benchmark/qwen-metax-pipeline-plan.yaml` 包含 4 个 run：128/16、1024/32（并发 1 和 2）、8192/32；每个 run 4 个测量请求、1 个独立预热请求。长短场景是小模型流程资格检查，不替代 GLM 正式场景或 p99 验收。

真实验证已发现并修正两个离线替身测试没有发现的问题：

- Transformers 5 的聊天模板默认返回 `BatchEncoding`，直接求长度会得到字段数。当前实现显式传入 `return_dict=True` 并读取 `input_ids`，回归测试覆盖这一契约。
- AIPerf 0.12 不接受 `--warmup-request-count 0`。安装源码明确规定：不传 warmup count/duration 才是不启用其内建预热。现在省略这两个选项，由我们的独立请求集执行预热；首轮失败批次保留，不计为有效测量。

新增 vLLM external 适配器回读 `/server_info`，核对并行参数、prefix cache、stream interval 与上下文长度。新增 MetaX 实时设备身份与驱动核对。客户端容器 `mx-smi` 显示的 MACA 3.8.2.6 是采集进程用户态库版本，与宿主机安装的 3.9.0.29 分别记录，不能据此推断服务使用哪个运行库。AIPerf 确认从隔离环境 `/job/aiperf012/lib/python3.12/site-packages/aiperf/` 加载 0.12.0，未误用镜像内 0.13.0。未验证的环境不会被标成通过。

成功批次为 `batch-20261123T085945Z-ccf82622`，4/4 run 完成，16/16 测量请求成功，另有 4 个独立预热请求；每个 run 的逐请求指标完整性为 `valid`，环境核对问题列表为空。

| 输入 / 输出 tokens | 并发 | 成功请求 | 平均 TTFT（ms） | 平均 TPOT（ms） | 输出吞吐（tokens/s） |
|---|---:|---:|---:|---:|---:|
| 128 / 16 | 1 | 4/4 | 37.71 | 22.87 | 41.84 |
| 1024 / 32 | 1 | 4/4 | 40.90 | 23.76 | 41.07 |
| 1024 / 32 | 2 | 4/4 | 64.70 | 25.04 | 75.48 |
| 8192 / 32 | 1 | 4/4 | 218.48 | 23.75 | 33.44 |

这些数值只验证 Qwen、单卡、eager 部署下的采集闭环。TPOT 为客户端 `(E2E - TTFT)/(输出 token 数 - 1)`；吞吐窗口是首请求开始至末请求结束。样本量不足以进行尾延迟验收，未采集连续 GPU 功耗/利用率遥测，也没有设置正式 SLA。

归档位置为 [benchmark-qualification/20261123](../experiments/evidence/benchmark-qualification/20261123/)：包含成功批次、首次 CLI 参数失败批次、逐请求原始导出、请求集、服务配置、启动命令、日志、客户端包清单和执行代码快照。下载后校验了 231 个归档文件的 SHA-256；[离线复算记录](../experiments/evidence/benchmark-qualification/20261123/offline-verification.json) 确认四个 run 的原始哈希、计数、状态完全一致，数值在 `1e-12` 绝对/相对误差内一致。Linux Python 3.12 与 Windows Python 3.11 的浮点求和末位存在约 `1e-15` 的差异，不改写原始测量。

测试完成后已删除本次创建的四个服务尝试容器；设备进程检查显示 `no process found`。工作目录、隔离 AIPerf 环境及证据保留，四台新节点的现有服务未改动。

本地验证：280 份规约通过结构、引用和语义校验；85 个单元测试中 84 个通过，1 个因历史原始附件不在本地而明确跳过。Qwen 计划无执行阻塞，但仍有 20 项正式冻结就绪问题，包含模型来源/质量与硬件健康、editable 服务代码等。流程完成不等于正式冻结通过。

## 正式 GLM 测量前仍需完成

1. 明确 Flash-W8A8、完整版 W4A8、完整版 W8A8 中的目标变体，再分配卡数和并行方式。
2. 在新集群准备匹配 MetaX 驱动的 vLLM 镜像（若选择 vLLM），以及固定 AIPerf 版本的采集环境；镜像与实际服务代码一起锁定。已有 SGLang 仍需验证具体 GLM 架构和量化 loader。
3. 释放指定资源后，先验证模型加载、tokenizer 一致性与少量生成，再补充实际部署配方和正式测试计划。新集群的 HBM、GEMM、互联指标需在空闲资源上单独测量。

本次未启动任何 GLM 性能测量；按约定，待用户确认后再进入该阶段。
