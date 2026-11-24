# C500 GLM 模型部署与算子替换移交说明

版本：2026-11-23，无镜像移交补充版。接收对象：负责在其他服务器复现环境、部署模型、开展精度评测和算子替换实验的同事。

本次移交包括知识库、Agent 工作规则、部署与评测代码、算子替换原型和历史验证证据。参考模型为 **GLM-5.3-Flash-W8A8**，参考硬件为 **8 张 C500，每卡 64 GiB，TP8**。本次优先采用**小型资料/代码包＋固定源码＋接收方取得安装材料并重建**，不要求发送原推理或评分镜像。接收服务器重建后建立自己的对照基线；镜像导入仅保留为可选历史路线。

**当前交付形态是经过实测的代码与实验材料集合，尚非参数化的一键安装发行包。** 本说明没有执行镜像导出、远程传输或新服务器部署；大文件交付和接收方复现需按下列清单完成。所有“通过”均指明确记录的历史配置，新服务器须重新验收。

**能否只打包本地目录？** 可以将经过筛选和审阅的本地目录作为知识库/实验代码交付包，但它不包含完整框架源码、SDK、wheel或模型权重，单独收到该包不能立即安装。第12节说明无镜像重建的新增要求，第13节给出本地目录盘点和打包范围。

## 1 交付范围与历史实测结果

| 工作 | 历史结果 | 接收方应如何使用 |
|---|---|---|
| 知识库与检索 | 16 份 PDF、899 页文本；软件/镜像及仓库快照；16 条实践记录；统一检索与来源校验 | 作为部署、排障和开发入口，保留版本、日期和证据边界 |
| 独立推理环境 | vLLM-MetaX 0.32.0-dev 配套环境及三项局部修复；真实权重 TP8 文本生成通过 | 恢复匹配镜像、源码、权重和参数，在新服务器重跑 |
| 模型任务精度 | HumanEval 全量 153/164，pass@1=93.29%；canonical 评分器验证164/164通过 | 复现固定协议；分数是历史结果，不是新服务器必然达到的保证或官方榜单分数 |
| 重复性诊断 | 4 个独立生成进程、6轮32题结果一致，均31/32；有固定前缀数值诊断与回归判定代码 | 复用判定方法；历史9题输出分叉的唯一根因仍未闭环 |
| 局部 GEMM 原型 | mcTriton INT8 GEMM，独立56/56组、真实权重分片配合合成激活24/24组通过 | 可复现局部测试，不代表所有层或量化格式支持 |
| 模型内替换 | 仅第一层 gate_up_proj；备用通信下原32题30/32、候选32题31/32、恢复4题4/4；无通过题退化 | 可复用单层接入、检查和恢复流程；尚未完成全量、多独立进程候选验收 |
| 性能优化 | 尚未建立正式整模型性能基线，也未证明候选加速 | 只能声明可替换性与有限范围正确性，后续单独测量性能 |

最新单层试验中八卡候选总调用11936次、零fallback、相对原GEMM最大差异1 BF16 ULP。该原型同时执行原实现作为影子校验，保留INT32中间矩阵，耗时不适合作加速比较。候选多通过一题也不构成精度提升证明。

原服务器最新实测驱动为3.10.14，而最初部署和历史153/164基线使用3.8.30。GPU6—GPU7的MetaXLink port4仍有down/x4异常，最新模型对照在实验容器禁用P2P并关闭自定义all-reduce后完成。**这是一条故障绕行记录，不能作为新服务器默认配置或硬件修复证明。** 参见[最新对照报告](../glm53/reboot_recheck_20261123/REPORT.md)。

## 2 知识库与代码入口

保留下面的相对结构，便于链接、校验工具和同事间共享。示意中的省略项不代表打包时应删除其他文件。

```text
交付根目录/
  AGENTS.md
  移交说明_C500_GLM模型复现.md
  hwdoc/
    README.md / CATALOG.md / TOPICS.md / COMPONENTS.md
    *.pdf
    ecosystem/                 官网镜像与软件目录的日期快照
    repositories/              GitHub元数据、README和哈希
    practice/                  指南、案例、问题与审阅后的证据
    generated/                 索引、逐页文本和来源清单
    tools/                     检索、构建、核验和回归测试
  glmf/
    HANDOFF_BASELINE_OPERATOR_OPTIMIZATION.md
    audit_20261122/             权重、源码、环境和版本审计
    deploy032/                 部署、三项修复、推理与冻结入口
    baseline_ops/              HumanEval数据、生成、评分与历史基线
    repeatability_20261123/     重复性诊断与正式回归规则
    gemm_replace_20261123/      自编GEMM、契约和局部测试
    recovery_20261123/          热复位及故障复发证据
    reboot_recheck_20261123/    已完成的备用通信单层模型对照
```

交接阅读顺序：

1. [AGENTS.md](received-agents.md)：项目工作规则；使用Agent协作时要求它先读取。
2. [知识库使用说明](../../../../catalog/library/metax/hwdoc/README.md)与[实践入口](../../../../catalog/library/metax/hwdoc/practice/README.md)：查询资料和实测经验。
3. [独立环境指南](../../../../catalog/library/metax/hwdoc/practice/runbooks/isolated-metax-environment.md)与[部署案例](../../../../catalog/library/metax/hwdoc/practice/cases/2026-11-22-glm53-w8a8-tp8/README.md)：理解环境与修复。
4. [HumanEval复现说明](../../../../catalog/library/metax/methods/humaneval.md)：生成和隔离评分协议。
5. [回归判定规则](../../../../catalog/library/metax/methods/regression-policy.md)、[GEMM原型](../glm53/gemm_replace_20261123/README.md)与[最新模型对照](../glm53/reboot_recheck_20261123/REPORT.md)：开展替换。

`AGENTS.md`是共享工作约定，不是自动执行程序；核心要求包括先查资料、保留版本和实测边界、禁止覆盖历史实验、记录哈希、保护原环境及不保存凭据。文档中的命令是复现参考，由接收方按其服务器权限和作业安排执行。

知识检索在交付根目录运行，Linux将原Windows Python路径替换为`python3`：

```bash
python3 -B hwdoc/tools/search.py --component vllm-metax --source practice
python3 -B hwdoc/tools/search.py weight_scale --source practice --full
python3 -B hwdoc/tools/search.py --component mctriton
python3 -B hwdoc/tools/build_knowledge.py --check
python3 -B hwdoc/tools/verify_practice.py --check-originals
python3 -B -m unittest discover -s hwdoc/tools -p 'test_*.py'
```

纯检索使用Python标准库；PDF重建另需`hwdoc/tools/requirements.txt`中的依赖。`--check-originals`需交付其引用的原始本地文件；缺少原件时报告缺项，不能改旧清单使其通过。索引变化应先核查原因，再运行`build_knowledge.py`和`--check`。实践日期互不替代，`latest`不会隐藏旧独立案例。

## 3 移交前的大文件与资产清单

知识库中的文件路径不等于大文件已经包含在交付包。移交人和接收人应共同填写交付清单，至少登记“文件/来源、版本、字节数、SHA256、交付位置、接收校验结果”。模型和第三方软件按各自许可及单位分发规则交付，保留LICENSE和NOTICE。

| 资产 | 参考标识 | 交付要求 |
|---|---|---|
| 本地资料和代码 | 上述项目目录，含执行源码快照及必要历史证据 | 审阅后按白名单打包；记录每文件SHA256，保持相对结构 |
| 推理依赖镜像 | `glm53-vllm032:verified-20261122` | 本次不发送，保留ID作历史参考；接收方重建新镜像并记录自己的ID |
| 评分镜像 | 历史评分使用原0.28基底image ID，见下文 | 本次不发送；接收方构建/取得小型CPU Python评分环境，修改评分器引用并重验 |
| 匹配源码 | 原commit＋修复，或`sources-20261122.tar.gz` | 完整源码不在本地项目；接收方能取得精确版本时可自行获取，否则另交Git bundle/源码归档。无需发送完整推理镜像 |
| 部署脚本归档 | `deployment-scripts-20261122.tar.gz` | 保留历史哈希；可用本地相应脚本代替另传归档，但须对照执行版本。后续HumanEval/GEMM工具从项目目录交付 |
| GLM W8A8权重 | revision `6df7a9b0309e530094e29b2a6ced3e21bed6c16d`，59文件/47分片 | 约328.5 GB原始文件；完整包含tokenizer、模板、配置和索引，或按revision重新下载并校验 |
| HumanEval数据 | `openai/openai_humaneval` revision `7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544` | 原始数据、准备后输入、固定32题ID、164题ID和评分测试；生成与评分材料分离 |
| 重建安装材料 | SDK3.9.0.29、27个已核验私有wheel、公共依赖、固定源码及补丁 | 本路线必需；由接收方从可访问渠道按版本/哈希取得，或另行提供安装材料，不要求经原服务器传输 |

已知不可变标识：

```text
推理镜像 ID
sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285

历史评分/原0.28基底镜像 ID
sha256:96bbee871d4ea038b123276eacd65f77825b093b9255157938e0b1628e121f0b

源码归档 SHA256
da769ed300e32876f2bd358a1c537a8618f7fdbc8f56830eacfec57f6d1ab592

早期部署脚本归档 SHA256
d62bdbf93b61785422931fdde5b5cc4da960829645f729ddae38e094bc61d83f

SDK3.9.0.29压缩包 SHA256
6737f26cec90fda2916c11615805bcd5fe9f0c9a1f267818bb9cebdec73a3bc4
```

源码和脚本归档原位置为`/home/metax/glm53-vllm032/baseline/`。这些是已有记录，正式交付前应重新确认可读并校验。详见[资产清单](../../../../catalog/library/metax/hwdoc/practice/cases/2026-11-22-glm53-w8a8-tp8/artifacts.json)。

以下为可选镜像导出/接收参考，**本次无镜像方案跳过整个命令块**。目录和文件名由移交双方指定；以下尚未执行：

```bash
# 发送方：在空的交付目录执行，先检查磁盘和镜像身份
docker image inspect glm53-vllm032:verified-20261122
docker save -o inference-image.tar glm53-vllm032:verified-20261122
docker save -o scoring-image.tar sha256:96bbee871d4ea038b123276eacd65f77825b093b9255157938e0b1628e121f0b
sha256sum inference-image.tar scoring-image.tar > images.sha256

# 接收方：传输校验通过后加载，再检查image ID
sha256sum -c images.sha256
docker load -i inference-image.tar
docker load -i scoring-image.tar
docker image inspect glm53-vllm032:verified-20261122 --format '{{.Id}}'
docker image inspect sha256:96bbee871d4ea038b123276eacd65f77825b093b9255157938e0b1628e121f0b --format '{{.Id}}'
```

采用`docker save/load`保留镜像配置；不要用容器文件系统的`export/import`代替。镜像ID、registry digest和导出tar的SHA256是不同对象，分别核对。镜像不包含宿主驱动、只读模型挂载和外置源码；只交镜像无法完整复现。

交付排除项：Docker登录配置、MIM/API凭据、SSH私钥和密码、Mihomo私密配置及订阅、签名下载URL、未经审阅的原始日志和完整环境转储。新的下载服务器由接收方配置自己的账号/代理；本次原MIM镜像并未拉取完成，不把其名称当作可直接取得的成功交付物。

## 4 新服务器环境准备

先记录接收服务器的型号、CPU架构、OS/kernel、GPU型号/显存/卡序、驱动、互联拓扑、Docker、磁盘/内存和现有作业。原实测宿主内存约1 TiB，这不是已证明的最低要求；磁盘需容纳权重、镜像导出与解包、源码、缓存和结果，不仅预留模型文件大小。

优先使用同类8×C500/64 GiB、x86_64 Linux。其他卡型、卡数、显存或架构属于新适配任务，不能直接承诺TP8方案可用。驱动选择由新服务器维护方结合厂商支持范围确定；历史3.8.30/3.10.14结果不是建议照搬升级或降级。

健康检查顺序：设备枚举和状态 → 单卡小计算 → 八卡最小collective → 完整模型。每一步记录时间、命令、退出码和每rank结果。出现链路down、不可纠正错误或设备不可用时先处理设备问题，不用不断重跑模型判断“是否偶尔成功”。热复位、驱动修改和主机重启按新服务器维护流程操作。

创建新的任务目录和容器。参考[历史容器创建参数](../glm53/baseline_ops/evidence/humaneval_v1/create_container.json)：设备`/dev/dri`和`/dev/mxcd`、video组、private IPC、64 GiB shm、memlock、主机网络和hostname映射均需在目标机核对。主机锁要放在所有GPU实验共享的路径，容器不同不代表GPU资源隔离。

建议保留容器内路径，以减少框架editable路径变化；只改宿主挂载源：

| 容器路径 | 接收服务器上的内容/权限 |
|---|---|
| `/work/src/vllm`、`/work/src/vllm-metax` | 匹配源码归档展开目录；基线只读 |
| `/models/GLM-5.3-Flash-W8A8` | 完整已校验权重；只读 |
| `/work/scripts` | 部署smoke需要的脚本 |
| `/experiment/harness`、`/experiment/configs`、`/experiment/data` | 精度/算子实验脚本、配置、生成输入；尽量只读 |
| `/work/evidence`、`/experiment/evidence` | 指向本次新证据目录，按实际脚本需求映射 |
| `/experiment/runs`、`/experiment/cache` | 本次独立结果和缓存；可写 |

评分测试与canonical solution保存在宿主评分目录，不挂进模型生成容器。评分器由具备Docker权限的宿主进程启动CPU沙箱；不向模型容器或评分沙箱挂Docker socket。

## 5 镜像恢复与源码构建两条路线

### 可选路线 恢复冻结镜像

导入推理/评分镜像，校验归档后将源码恢复到新的宿主目录，挂载到原容器内路径。检查tar目录层级、符号链接和文件权限，避免多套一层目录。旧编译产物只能在兼容硬件与依赖下使用；若加载失败，应记录错误并重建对应产物，不把缺少库或符号问题误判为模型问题。

启动后检查实际`__file__`、distribution版本、MetaX平台、native库路径和pip依赖；完整环境以[包清单](../glm53/deploy032/evidence/environment_packages.json)和[运行来源](../glm53/deploy032/evidence/framework_runtime.json)为参照。归档展开源码没有`.git`时，使用归档哈希及逐文件比对证明来源，不把失败的git命令输出当commit。

### 本次优先路线 从固定源码和安装材料重建

适用于本次不传输大镜像的交付方式，所有安装都限定在新环境。历史成功环境从已有0.28厂商镜像升级，并非从干净OS基底验证过的完整构建配方；去掉该基底后需补齐第12节的系统依赖和构建验证。核心版本如下：

| 项目 | 参考版本 |
|---|---|
| MACA SDK | 3.9.0.29 |
| Python / Torch | 3.12 / `2.10.0+metax3.9.0.8` |
| mcTriton | `3.6.0+metax3.9.0.8` |
| mcoplib | `0.4.14+gf3794c4.maca3.9.0.31.torch2.10` |
| mctlassEx | `0.1.1+metax3.9.0.8torch2.10` |
| Transformers / compressed-tensors | 5.17.0 / 0.17.0 |
| vLLM | commit `5df63a7203cdb9328d824a27b682e77c7b9928be` |
| vLLM-MetaX | commit `0962c8735ffe4795800030680311410848512b82` 加三项修复 |

顺序为固定源码和依赖材料 → 校验/暂存SDK → 容器用户态SDK安装 → 配套wheel → 上游和插件构建 → 导入与计算验证。参考`deploy032/stage_sdk.py`、`install_sdk.py`、`install_native.py`、`install_frameworks.py`，先读代码的环境断言和路径约束，再在迁移副本修改。

上游构建采用editable、`VLLM_TARGET_DEVICE=empty`、`--no-deps --no-build-isolation`；插件使用`USE_PRECOMPILED_KERNEL=1`。这些设置依赖已安装的配套包，不能当作跳过依赖准备的捷径。cu-bridge来自MACA SDK，核对`CUCC_PATH`、`CUBRIDGE_HOME`、`CUDA_HOME`和PATH；不要因目录名带CUDA就自行安装NVIDIA Toolkit。

重建注意：

- `prepare_sources.sh`中的MetaX克隆源是原服务器本地路径，新服务器没有该目录。需交付对应Git仓库/源码，或取得包含精确commit的仓库；不能任意换成当前最新分支。
- 源码归档适合镜像恢复；`install_frameworks.py`检查Git HEAD，直接对无`.git`归档执行会失败。重建时取得真实checkout，或明确改为等价的可审计来源校验，不伪造HEAD。
- `install_native.py`虽从本地wheel安装，但校验步骤会访问厂商索引；`install_frameworks.py`也会下载公共依赖。离线复现须补齐wheel及已核验manifest，并调整网络校验步骤，不能仅复制27个私有wheel就承诺完全离线重建。
- SDK安装器要求已有特定基底布局和`/opt/maca`链接。干净Ubuntu镜像不一定满足；使用已验证基底或单独适配并复验。

恢复[tracked修复patch](../glm53/deploy032/evidence/vllm-metax_deployment.patch)和[新增ABI模块](../glm53/deploy032/moe_align_legacy_abi.py)。三项修复分别保护旧MoE ABI、INT8 indexer Tensor契约和MLA scale加载所有权；diff不含新增模块，二者缺一不可。目标源码若已含等价修复，应核对后测试，不能重复套patch。

## 6 迁移脚本时必须修改的内容

在新副本中逐项改写，保留历史执行源码和哈希。禁止对整个项目盲目全局替换。

| 项目 | 典型位置 | 接收方动作 |
|---|---|---|
| 宿主根目录、源码及权重路径 | `deploy032/*.sh`，容器创建JSON，各launcher的`ROOT` | 改宿主路径和bind mount源，尽量保留容器内路径 |
| 容器名、label、run label | `run_generation_host.py`、`launch_model.py`、Docker label检查 | 使用本次唯一名称，断言与启动命令同步修改 |
| 八卡锁路径 | 各host launcher | 所有实验使用共同锁；不要每容器各建一把互不相干的锁 |
| 镜像引用 | 创建命令、评分器的`IMAGE` | 核对推理和评分两个image ID；替换评分镜像后重验canonical及沙箱 |
| UID/GID | 模型实验`run_model.py`中`os.chown(...,1000,1000)`等 | 改为接收方实际属主；限制到新输出目录，不递归改旧环境权限 |
| 运行编号与输出目录 | `runs/`、证据文件、授权gate文件名 | 每次新建，拒绝覆盖，禁止复用历史成功gate |
| 通信设置 | 最新pilot的`MCCL_P2P_DISABLE=1`、`disable_custom_all_reduce=True` | 两项成对审查；健康服务器选择明确的默认/备用配置，B0与候选一致 |
| 输入/配置哈希 | `inputs_sha256.json`、执行manifest、模型计划 | 保存迁移diff并生成新manifest；历史manifest保持不变 |

`baseline_ops/configs/humaneval_regression.frozen.json`包含历史草案与实际冻结字段；不能把内嵌`null`或`sandbox not_implemented`当作最终状态。实际生成配置从[protocol-v1.executed.json](../glm53/baseline_ops/evidence/humaneval_v1/protocol-v1.executed.json)恢复到新实验的`configs/protocol-v1.json`，评分限制以冻结文件顶层`scoring`和执行代码为准。

## 7 模型部署验收

先检查59文件哈希、47分片和weight_map，保留权重revision与tokenizer/template哈希。原`metadata.total_size=[]`是已知元数据问题：结构检查的`complete=false`不能被隐去；文件哈希及张量映射通过。接收方若修改原模型文件，就必须形成新的模型版本和证据。

起步配置明确固定：TP8、mp、V2 runner、BF16非量化部分、compressed-tensors W8A8、safetensors、max_model_len=4096、max_num_seqs=1、同步调度、eager、prefix cache关闭；indexer配置auto，检查实际解析INT8。图像/视频输入关闭。

先重跑八卡小计算/通信，再在新容器做真实权重smoke。原入口[run_inference.sh](../glm53/deploy032/run_inference.sh)设置了V2/单序列/同步；直接运行[infer_smoke.py](../glm53/deploy032/infer_smoke.py)会使用不同的默认序列数，必须显式传递环境设置，并将输出位置指向新目录。

验收要求：8个worker的实际来源一致、确实使用INT8量化路径、每rank的33个MLA INT8 scale有限且为正、中文回答正常、算术回答2、长前缀查找返回“青松”、进程退出0。历史smoke采用temperature=1/top_p=0.95，不以其随机采样的逐token全等作为迁移成功标准。通过后保存新服务器部署记录，再开展任务精度测试。

## 8 HumanEval精度测试复现

### 数据与目录准备

复用固定revision及同一32题ID选择规则，完整集为164题。`prepare_dataset.py`需要联网及`pyarrow`；也可以接收已校验的原始/准备后数据。生成容器仅获得`task_id`和`prompt`，canonical及测试只提供给评分器。

新host实验根目录至少准备：`harness/`、`configs/`、`data/`、`scoring/`、`evidence/`、`runs/`、`cache/`。生成侧`data/prompts.jsonl`和`data/selection.json`分别由准备后prompts和固定`all/smoke32`列表产生；主机`scoring/scoring.jsonl`保存原始测试及canonical。逐项与dataset manifest和历史输入哈希比对。参考[数据manifest](../../../datasets/humaneval/manifest.json)及历史prompt manifest，不用临时改题集来凑通过率。

### 执行顺序

1. 在主机评分器先执行`--canonical --selftest`，要求164/164及沙箱自检通过。它检查评分环境，不运行模型；若失败，先修复评分器/镜像/资源限制。
2. 在新推理容器启动参数化后的`run_generation_host.py`。它先检查环境，再执行同一已载入模型的smoke32，等待full164 gate。
3. 用`evaluate_humaneval.py --run <新smoke目录>`评分。固定提示词、代码提取、上下文、输出预算和超时；模型错误不补缩进、不按测试修代码、不重新采样挑结果。
4. 由本轮真实评分结果生成新的`authorize_full_<新label>.json`。字段包括当前`protocol_sha256`、`smoke_scoring_complete`和`canonical_passed=164`；必须核对本轮产物后生成，不能复制旧gate或只修改布尔值。原脚本等待最长7200秒，超时后保留失败记录，在新的run目录重新安排流程。
5. 完成full164生成和隔离评分，检查任务集合、缺失/重复、截断、基础设施错误与每题结果。保存逐题输出、原始评分、manifest及汇总。

迁移并核对路径后的命令形态如下；尖括号为待替换值，不是可原样运行的命令：

```text
python3 <新实验根>/harness/evaluate_humaneval.py --run <新实验根>/runs/canonical_v1 --canonical --selftest
python3 <新实验根>/harness/run_generation_host.py
python3 <新实验根>/harness/evaluate_humaneval.py --run <新实验根>/runs/<新label>_smoke32
完成本轮评分检查并生成匹配的full164 gate
python3 <新实验根>/harness/evaluate_humaneval.py --run <新实验根>/runs/<新label>_full164
```

launcher运行期间，评分和gate检查在另一终端进行；它持有GPU锁，评分仅使用CPU沙箱。生成协议为greedy temperature=0、top_p=1、seed=0、max_tokens=1024、ignore_eos=False及固定聊天模板，与部署smoke的随机采样协议分开。

保留原评分隔离：无网络、无GPU、无bind mount、非root、只读根文件系统、资源限制和超时；模型生成代码不在宿主直接执行。参考限制为1 CPU、512 MiB、32 PID、单题CPU8秒/wall10秒、外层45秒。变更评分Python或镜像/限制后，记录新评分协议并重新做canonical及自检。基础设施错误记作无效实验，不能算模型答错后仍给有效全量分数。

历史153/164只作为固定协议参考；新服务器应先生成自己的B0。跨驱动、通信、依赖、tokenizer或模板的结果，不直接视为同条件回归。

## 9 算子提取和替换流程复现

当前已验证对象是`language_model.model.layers.0.mlp.gate_up_proj`，实际为`MergedColumnParallelLinear`及`CompressedTensorsW8A8Int8`，原kernel为`MctlassScaledMMLinearKernel`。实际选中GEMM进入mctlassEx二进制；替换在Python层的单个`scheme.kernel`对象完成，无需改写原动态库。

| 文件/目录 | 作用 |
|---|---|
| [gemm_kernel.py](../glm53/gemm_replace_20261123/harness/gemm_kernel.py) | mcTriton INT8累加与scale epilogue、支持范围及误差度量 |
| `gemm_replace_20261123/configs/contract-v1.json` | 测试前冻结的语义与≤1 BF16 ULP标准 |
| `gemm_replace_20261123/harness/test_device.py` | 八卡独立GEMM与CPU参考测试 |
| `gemm_replace_20261123/harness/isolated_layer_probe.py` | 真实权重8份TP分片配合合成激活的量化层验证 |
| [replacement_worker.py](../glm53/reboot_recheck_20261123/pilot/harness/replacement_worker.py) | 安装/恢复单层对象、命中/fallback统计、影子校验、真实输入采集 |
| [run_model.py](../glm53/reboot_recheck_20261123/pilot/harness/run_model.py) | 原32题→候选32题→恢复4题的模型生成 |
| `reboot_recheck_20261123/pilot/harness/launch_model.py` | 通信前置检查、资源锁、模型生成和隔离评分串联 |

建议按以下顺序逐关通过：

1. **独立算子。** 保留原量化，仅替换GEMM；INT8累加对CPU INT64精确，明确顺序FP32 epilogue精确，FP64/原实现差异在预登记标准内。涵盖尾块、极值、零输入、正非连续stride及scale粒度。
2. **真实权重量化层。** 新结果目录中检查实际权重布局，运行原实现→候选→恢复。历史24组是在GPU0依次处理8份TP分片，不能表述为八卡完整模型测试。成功历史源码快照为`evidence/isolated_layer_probe.v3.py`；维护版有后续路径调整，接手时比对差异。
3. **目标服务器原模型对照。** 用当前驱动和明确通信配置建立本轮baseline32；检查8rank都找到预期层和独立scheme对象。
4. **单层注入。** 每rank保存原kernel，只替换显式目标层。保留原激活量化和scale顺序；输入不受支持时回退并计数。此轮要求目标层实际候选命中、零fallback，不能因回退运行正常就声称替换成功。
5. **真实输入提取。** 采集每rank首个prefill/decode的量化输入、权重选定行列、scale、累加和输出，保留完整K。当前只有有限切片与shape统计，尚非全模型通用算子提取器；扩大覆盖时须补布局、别名、状态、workspace和通信契约。
6. **模型评分和恢复。** 候选32题逐题与同期原32题比对，再恢复原对象跑4题。检查8rank安装/恢复记录、token结果、数值、命中次数及设备状态。出现越界/设备错误立即停止该实验并保留证据。

在健康服务器可选择默认通信，但必须同步调整pilot中的`MCCL_P2P_DISABLE`和`disable_custom_all_reduce`，重跑通信和同期原实现；原服务器备用路径的30/32与31/32不是新服务器的预设答案。

局部和32/32/4通过后，按[REGRESSION_POLICY.md](../../../../catalog/library/metax/methods/regression-policy.md)完成同期B0/候选各3个全新进程的全164题、固定共同前缀数值和局部语义验收。稳定通过题不得退化，其他题改善不能抵消；波动题下降须定位。历史自由生成token差异未闭环，不用“所有输出字符串全等”作为所有浮点替换的统一标准。

正式计时前关闭影子原算子和同步诊断，确认新模式仍通过正确性；保留baseline开关。下一步再建立固定输入/输出长度的模型性能矩阵和真实shape的微基准。当前`baseline_ops/configs/performance.json`仍是草案，不是已测性能结果。

## 10 常见迁移问题

| 现象 | 优先检查 |
|---|---|
| 镜像能启动但import失败 | `/work/src`挂载、editable路径、compiled allocator、native库、CPU/GPU架构和SDK ABI |
| pip版本相同但行为不同 | `__file__`、完整源文件/补丁哈希、实际native库、所有worker加载路径 |
| MoE报参数个数错误 | 旧7参数provider与上游8参数调用；检查schema门控桥接和新增模块是否恢复 |
| 长prefill报tuple.dtype | INT8 sparse indexer Q应为Tensor的修复是否存在 |
| 输出重复、NaN或异常巨值 | 首次异常层、INT8 scale加载所有权；检查每rank MLA scale，不先归因于量化模型质量 |
| 卡不可用或collective卡住 | 硬件、MetaXLink/PCIe、卡序、驱动与通信；原故障发生在候选注入前，不能套用为候选错误 |
| full164一直等待 | 新label对应gate、当前protocol哈希、本轮canonical/smoke评分是否完成 |
| 评分无法写目录 | 新run目录属主和UID/GID；不要全盘递归改权 |
| 评分报infrastructure_error | 评分镜像是否加载、Docker权限/隔离限制/外层超时，不把它算成模型失分 |
| 已有结果导致拒绝运行 | 使用新目录、新run ID；这是防覆盖保护，不能删历史结果绕过 |
| 得分或速度与历史不同 | 先对齐硬件、驱动、通信、输入token、模板/采样、评分协议、诊断开关和实际输出长度 |

MIM和代理的处理方法分别见[登录与下载指南](../../../../catalog/library/metax/hwdoc/practice/runbooks/mim-auth-and-download.md)、[Mihomo指南](../../../../catalog/library/metax/hwdoc/practice/runbooks/mihomo-download-proxy.md)。登录/manifest成功不保证大blob下载成功；端点不返回正确206/Content-Range时不能直接追加部分文件。

## 11 接收验收与回传材料

建议双方按下表逐项签收，未完成项写明负责人及后续动作。以下复选框表示待接收方验证，不表示已有执行结果。

- [ ] 资料/代码包齐全；完整框架源码、SDK/wheel、权重和数据已由接收方下载或另行取得并校验。推理及评分环境在目标侧重建，记录新镜像/依赖身份；原镜像不列为本次必交项。
- [ ] 知识库可检索，索引一致性和资料引用检查通过；Agent已读取本地AGENTS规则。
- [ ] 新服务器硬件/互联健康，驱动与用户态配套已核对，8卡计算和collective通过。
- [ ] 完成路径、容器名、UID/GID、锁、镜像和run ID迁移，保存迁移diff与新manifest。
- [ ] 新容器完整TP8部署smoke通过，每rank来源、量化和scale检查通过。
- [ ] canonical164及评分沙箱自检通过，smoke32和full164生成/评分完成，无缺题或基础设施错误；建立接收方B0。
- [ ] 独立GEMM、真实权重量化层、单层32/32/4对照、真实输入检查及恢复原对象通过。
- [ ] 若要求正式接纳候选，完成全164题多进程及数值回归；若要求性能收益，另完成去诊断开销的性能验收。

回传一个新日期结果目录，至少包含：服务器环境清单、镜像/源码/权重/数据/配置指纹、迁移patch、实际命令、原始逐题结果与汇总、算子契约和覆盖率、数值误差、命中/fallback、回退结果、设备前后状态、退出码及未完成项。大张量和trace以受控存储路径与SHA256引用，报告不包含凭据。

历史目录保持不可变；新经验整理为新的`hwdoc/practice/cases/日期-服务器-主题/`，通过`records.json`登记，核验后构建索引。更新规则、基线、候选和性能结论分别记录。跨服务器结果以接收方同期基线为比较对象，完整保留硬件和运行配置差异。

## 12 无镜像重建的重点补充

### 12.1 网络与材料分发方式

服务器之间不能直连，不妨碍接收方从其允许访问的公共源、厂商源或单位制品库下载材料。先逐项验证新服务器能否访问OS软件源、Git源、SDK/wheel源、模型和数据源，再决定哪些文件需要人工转交。不要将原服务器认证头、临时签名URL或代理订阅当成下载说明。

如果接收方也没有外网，则仍需通过允许的中转介质或内网制品库交付安装材料。源码重建不会消除模型和二进制依赖的体积：历史SDK压缩包为6,392,534,772字节，27个私有wheel合计5,178,857,555字节，模型约328.5 GB；此外还有公共Python包、OS包和构建工具。具体包清单见[native_wheel_manifest.json](../glm53/deploy032/evidence/native_wheel_manifest.json)。这些数值不代表完整离线材料包已经备齐。

建议分为三个部分：

1. **资料与实验代码包**：知识库、规则、脚本、配置、历史证据、材料清单，便于通过普通文件渠道发送。
2. **完整框架源码包**：两套精确源码及三项修复；可由接收方下载，也可单独转交小型源码归档/Git bundle。
3. **接收方材料缓存**：SDK、wheel、OS包、模型及数据，在目标网络内下载并校验。所有接收服务器共享同一份版本/哈希清单，但各自保留安装及验收结果。

材料清单每项至少有名称、版本/commit、文件名、架构/ABI、SHA256、字节数、公开或内部稳定来源、认证需求、取得状态与许可说明。临时URL只在本次下载进程私密使用；无法取得历史精确版本时明确列缺，不静默改成最新版。

### 12.2 完整源码和依赖锁定

**当前本地项目主要是实验脚本、补丁和资料，既不是vLLM源码仓库，也不是完整vLLM-MetaX源码仓库。** `hwdoc/repositories/`保存仓库资料快照，不包含可直接编译的完整checkout。本地有commit字符串不代表对方能够从公开远端获取该commit，尤其MetaX原部署克隆自原服务器本地目录。

移交前应二选一验证：接收方能按精确commit检出两套源码；或发送源码归档/Git bundle。使用bundle时，工作区未提交改动和untracked文件不会自动包含，须另带修复patch与`moe_align_legacy_abi.py`。使用完整源码tar时标记其包含哪些修复，并记录归档哈希；不要恢复后又重复套补丁。Git子模块/LFS内容如存在也须明确是否包含。源码归档中的旧编译产物不充当目标机重建成功证据，按依赖和硬件需要重新生成。

不能只固定Torch/Triton/mcoplib三个版本。[environment_packages.json](../glm53/deploy032/evidence/environment_packages.json)可作为已装包核对基准，但它是历史包清单，**不是完整可安装锁文件**：缺少部分OS依赖、下载哈希、构建条件，且包含editable/环境附加包。重建需要额外固定公共运行依赖、构建依赖、Python解释器及ABI、OS/系统库、编译器、CMake/Ninja等；记录安装顺序和软件源。

`install_frameworks.py`目前只对部分私有依赖生成约束，公共依赖仍可能被解析成新的版本。接收方应在新副本中加入经核验的公共约束和wheel来源/哈希，分开处理editable源码，不直接把全部已装包名字原样送给pip。保留`+metax...`等完整版本后缀，普通PyPI的同名Torch/Triton不能替代。pip check通过也只说明声明依赖一致，仍需实际native导入、计算和模型验证。

### 12.3 从干净基底构建还缺哪些条件

现有部署脚本的成功起点是**已经带有大量系统依赖和Python的厂商0.28镜像**。因此不传该镜像后，还需编写并实测一份目标侧构建配方，现阶段项目中没有已验证的通用Dockerfile或完整离线安装包。不要把原基底image ID继续放进新Dockerfile的FROM而误以为已消除镜像依赖。

接收方可以使用目标网络可取得的匹配厂商基础环境，或从选定的Ubuntu 22.04 x86_64基底安装用户态依赖。后一条需补齐Python3.12及开发头文件、构建工具、系统库、SDK安装前置与链接布局，并在空环境重新验证；Ubuntu版本不等于Python版本，不能把系统默认Python直接用于cp312 wheel。宿主驱动由维护方准备，不在应用镜像构建中安装内核驱动。

将旧脚本改造成明确的阶段：系统前置 → 用户态SDK → 私有wheel → 公共/构建依赖 → 固定源码及修复 → native编译 → pip/import/八卡检查。`install_sdk.py`中`/opt/maca`必须已经是符号链接的断言体现旧基底假设；新环境需正确执行SDK初装和验证，不能仅创建一个空链接骗过检查。`stage_sdk.py`还有文件大小与SDK路径约束，必须和实际校验材料一致。

构建产生自己的镜像ID、依赖清单、源码哈希和构建日志。即使版本相同，新镜像ID也无需与历史镜像一致；接收标准是材料来源、配置和各层验证，而非强行复现旧image ID。使用基础镜像时固定digest，而不仅写可移动tag，见[Docker构建建议](https://docs.docker.com/build/building/best-practices/)（2026-11-23查阅）。先在一台接收服务器走通，再将经验证的构建配方交给其余同事。

### 12.4 评分环境可以独立精简

当前`evaluate_humaneval.py`通过`python3 -I -S`执行标准库测试，评分沙箱不使用GPU、Torch、MACA或模型。因此没有必要为了评分转交原来的大型GPU基底镜像。可以在接收方选择一个**Linux、Python3.12、含标准库和resource模块**的小型CPU容器环境，例如从[Python官方镜像](https://hub.docker.com/_/python)的匹配slim变体起步（2026-11-23查阅），固定具体补丁版本、架构与digest。这是待验证的替代方案，本轮没有拉取或测试新评分镜像。

迁移时修改所用评分脚本副本的`IMAGE`常量及新协议中的`scoring.image_id`；基线、重复性、GEMM试验目录可能各有评分器副本，不能只改一个文件就认为全局生效。保留原`code_adapter.py`与题目测试；对新评分环境运行canonical164、沙箱自检，再用历史生成文件做离线重评分。若结果变化，先定位Python/依赖/超时差异，记录为新评分协议；canonical全通过是必要条件，但不是所有模型输出评分等价的充分证明。

继续保持无网络、无GPU、无挂载、非root、只读根文件系统、CPU/内存/PID/超时限制。换评分环境不等于允许直接在宿主执行生成代码。目标CPU速度与负载不同可能影响超时，先校准再冻结，不能对失败题临时增加时间以提高分数。

### 12.5 哪些原脚本仍需迁移

除第6节的路径与名称外，还要检查：

- `install_native.py`用`trust_env=False`访问官方包索引，`prepare_dataset.py`显式不使用代理，部分构建命令会清除代理环境。目标机需要代理时应修改新副本的网络配置，不把账号或代理认证写入脚本，也不能假设设置HTTPS_PROXY后所有下载都会生效。
- `check_frozen_baseline.py`、来源验证和launcher可能断言旧镜像、路径或版本。新镜像的身份检查必须改为本次已验证清单，保留拒绝漂移能力，不能整段删除检查。
- 归档完整性工具校验的是历史材料，测试新服务器时另写新run清单。不得将本轮哈希回填到旧artifact manifest，使旧记录看起来仍然原样。
- HumanEval准备数据和模型权重不因未传镜像而可省略；接收方取得后仍需对revision、tokenizer/template和数据manifest校验。

## 13 本地目录盘点与建议打包范围

### 13.1 2026-11-23本地扫描结果

本次扫描时项目共1674个文件，总计约1954.7 MiB（约1.91 GiB）；其中`glmf/deploy032/image_download/`中的三个`.part`下载片段合计约1884.9 MiB。仅排除这三个片段后，其余内容约69.8 MiB，尚未压缩。以后新增文件会改变统计，打包前重新核对。

这些`.part`不构成完整可导入镜像，本次无镜像路线不需要发送。扫描未发现本地SDK压缩包、deb、wheel、模型safetensors或两份指定远程源码/脚本归档。完整框架源码也不在该目录；GitHub README快照、提取的源代码片段和部署patch不能替代完整源码。

本地已包含固定HumanEval准备数据：`prompts.jsonl`、`scoring.jsonl`、`selection.json`，位于`baseline_ops/datasets/prepared/<revision>/`。体积小，可以校验后随包发送；其中scoring数据只交给评分进程，不挂进模型生成容器。`.gitignore`忽略部分数据和runs，**直接按Git跟踪文件打包可能遗漏复现资产**，要按交付清单实际列文件。

### 13.2 资料包的保留和排除规则

建议先生成一个独立的分发副本，再压缩发送，保持原项目不变：

| 内容 | 处理方式 |
|---|---|
| `AGENTS.md`、本移交说明、交接文档 | 保留 |
| `hwdoc/`原PDF、指南、日期快照、索引、工具和配置 | 保留；脱敏发生在分发副本，之后重建其索引 |
| `glmf/`各实验的脚本、配置、报告、执行源码快照、结果与manifest | 审阅后保留；首轮体积小，优先保留核验所需材料，不盲删runs/evidence |
| 固定HumanEval原始/准备数据、历史生成及评分结果 | 保留版本和哈希；生成和评分材料在接收端继续分离 |
| `glmf/deploy032/image_download/*.part`与OCI/tar下载残片 | 不入分发包；原目录保留，不在此次文档工作中删除 |
| `image_download/`的非敏感元数据 | 若历史引用需要可保留；不必连同二进制片段发送 |
| 根目录`tmp/`、`__pycache__`、`.pyc`、开发缓存 | 默认排除；如被清单引用，先明确缺项或保留必要文件 |
| Docker登录配置、SSH私钥、代理私密配置、真实密钥/签名URL、未经审阅日志 | 排除或在分发副本脱敏；不承诺扫描一次就覆盖所有秘密 |
| 大权重、SDK/wheel、完整框架源码 | 当前本地未含；在材料清单单独写接收方下载/另交，不能标成随资料包已交付 |

本次文本启发式扫描发现的额外情况：上游`hwdoc/repositories/2026-11-21/readmes/mcXformer.txt`第13行含Codecov徽章URL的token查询参数，且已进入`generated/knowledge.json`。这是上游公开README内容，不是本次部署的MIM或SSH凭据；但为避免转发不必要的token，建议在**分发副本**去掉该徽章URL的token参数或整个徽章。`test_practice.py`中的假凭据/示例URL用于扫描回归测试，应人工确认后保留，避免误删测试。

对分发副本脱敏时，记录原文件SHA256、变换说明、脱敏后SHA256；更新该副本`repositories.json`中对应README的哈希，并运行`build_knowledge.py`重新生成知识索引和导航，再执行`--check`与回归测试。保留采集日期并附分发处理说明，不能把改过的内容冒充原始快照。不要直接改历史原目录，也不要只改生成索引而让下次构建恢复被移除参数。

### 13.3 发包前的最低检查

1. 使用明确文件清单生成分发副本，核对排除项和缺失的大材料，不把私密配置放进副本。
2. 在副本运行知识库索引校验、实践证据核验和39项现有知识库回归；再执行准备交付的实验离线核验脚本。若裁剪了历史原件，明确列出哪些核验无法执行，不改旧哈希冒充通过。
3. 生成分发文件manifest（相对路径、字节数、SHA256），将manifest自身排除在自哈希列表之外。另记录压缩包SHA256和缺失材料清单，接收方解压后逐文件检查。
4. 给同事的首条说明写明：资料包可直接用于阅读、检索及历史结果审计；运行前须取得完整源码、SDK/wheel和权重，完成基底适配、评分镜像替换及服务器验收。

此前文档整理阶段未制作移交包。2026-11-23已在独立副本中执行清理、脱敏与资料核验，并将该副本用于生成移交压缩包，实际内容和验证结果见根目录《先读我_移交包.md》。本次仍未下载完整源码、制作干净基底Dockerfile、安装新评分镜像或在新服务器验证重建。要交付“拿到即可执行”的重建套件，下一步仍需补齐**完整源码与安装材料清单、公共依赖/OS锁定、目标侧构建配方和一次干净环境演练**。
