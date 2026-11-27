# 实际源码落点与优化可行性

## 1 代码版本与证据层次

本次重新从60固定镜像提取27个安装源码文件，清单及完整SHA256见[source-manifest](source-manifest.json)。源码位于镜像 `/opt/vllm-env/lib/python3.12/site-packages/`，本地保存在 `outputs/optimization-review-20261126/source/`。通信与indexer的其它文件复用同镜像的[通信分析源码快照](../outputs/collectives-20261126/source/)。

上游固定提交：[vLLM 5df63a7](https://github.com/vllm-project/vllm/tree/5df63a7203cdb9328d824a27b682e77c7b9928be)、[MetaX 0962c87](https://github.com/MetaX-MACA/vLLM-metax/tree/0962c8735ffe4795800030680311410848512b82)。当前安装包包含本地修补，所以本次源码判断以镜像提取内容为准，公开链接用于查原始项目。完整构建定义见[构建目录](../tools/deployment/metax-vllm/README.md)。

以下区分三件事：源码中存在入口、实际trace命中了相应类别、修改后端到端更快。前两项在不同方向上已有证据，第三项尚未验证。

## 2 KDA 门控归一化存在清晰的回退路径

调用链及当前安装文件行号：

```text
MacaPlatformBase._enum = PlatformEnum.OOT                 platform.py:127
Glm5NextLinearAttention.__init__ -> FusedRMSNormGated      common/kda.py:316
Glm5NextLinearAttention.forward -> self.o_norm(out, g2)    common/kda.py:500
CustomOp.dispatch_forward -> forward_oot                 custom_op.py:202
CustomOp.forward_oot -> forward_native                   custom_op.py:167
FusedRMSNormGated.forward_native                         ops/kda.py:484
  cast -> pow -> mean -> add eps -> rsqrt -> mul weight
  -> sigmoid(g) -> mul -> cast
```

[平台定义](../outputs/optimization-review-20261126/source/vllm_metax/platform.py)、[KDA模型](../outputs/optimization-review-20261126/source/vllm_metax/models/glm5next/common/kda.py)、[CustomOp分派](../outputs/optimization-review-20261126/source/vllm/model_executor/custom_op.py)、[实际FusedRMSNormGated实现](../outputs/optimization-review-20261126/source/vllm/third_party/flash_linear_attention/ops/kda.py)。该类有 `forward_cuda`，但没有覆盖 `forward_oot`。`device_type="cuda"` 不会改变 OOT 枚举分支。

F的日志显示 `compilation_config.mode=NONE`、`custom_ops=['all']`，同时图重放真实发生。这说明**图重放开启，并不意味着native碎片链已经被Inductor融合**。4K/32步/单卡中，recurrent、mean、pow、rsqrt、sigmoid各1088次，即34次/步，与KDA层数吻合。你的TP8分析中十个候选基础核约7.52%的预算因此有了更强的源码解释；仍需要在worker记录绑定方法与张量shape，把每一个通用核准确映射到这条链。

**可实施方向**：以MetaX局部注册/覆盖补 `forward_oot`，先验证既有Triton gated norm在当前MACA上的正确性；无法直接使用时再做窄范围mcTriton实现。保留FP32归一化累加、sigmoid gate、eps、stride和BF16回写语义。不要全局修改所有OOT CustomOp，也不把整个模型切到compile作为该问题的替代修复。[005](005-kda-gated-norm.md)

## 3 mHC 已经融合，值得做的是平台与shape重调

模型 `hc_fused_post_pre` 已调用融合实现，trace也出现 `mhc_pre_big_fuse_with_norm_tilelang_kernel`、`mhc_fused_tilelang_kernel`。[模型入口](../outputs/optimization-review-20261126/source/vllm_metax/models/glm5next/common/model.py)约559–687行；[TileLang实现](../outputs/optimization-review-20261126/source/vllm_metax/model_executor/kernels/mhc/tilelang_kernels.py)56–119行。

源码的调度说明引用GB300、hidden 5120/7168的经验；当前模型hidden为4096、C500，函数仍使用128 threads，按token<16分配tile_n=2、否则6，n_splits初值8，最多覆盖32 tokens。这个差异是调优依据，不是默认配置一定低效的证明。

TP8/EP关4K/C1两个主核合计约15.43%；F的DP0/TP0整个mHC类约85.266/852.702=10.00%。若将该类别减少20%，只是对应累计kernel预算约2%的减少，不是可承诺的2% TPOT提升。保持Sinkhorn迭代数、eps、归约精度，扫描tile/split/thread/小M布局，先验证dispatch、warmup和capture使用同一个配置来源。[004](004-mhc-small-batch.md)

## 4 EP 准备操作有真实成本，也有必要的正确性语义

[TritonExperts.apply](../outputs/optimization-review-20261126/source/vllm_metax/model_executor/layers/fused_moe/experts/triton_moe.py)374–428行经过 `_prepare_expert_assignment`。后者默认 `ignore_invalid_experts=False`，进入[moe_align_block_size](../outputs/optimization-review-20261126/source/vllm/model_executor/layers/fused_moe/moe_align_block_size.py)164–165行的 `expert_ids = expert_map[expert_ids]`。这是EP额外index/cast的候选来源；需要关联具体trace，不能把全部copy都归给它。

同一Experts文件638–639行：只要有expert_map或SPLIT_K>1，`intermediate_cache3.zero_()` 就会执行。非本地专家可能不写对应输出，后续reduce需要这些位置为零。正确改法是让计算/归并明确屏蔽无效项，或在有效写入路径中合并初始化；直接删除会读到上轮残留。现有原生alignment还有七参数ABI适配，[补丁](../tools/deployment/metax-vllm/patches/moe_align_legacy_abi.py)明确不支持scatter_idx，不能把上游新API直接套上。

F的实测通信为AG/RS：DP0/TP0 4K/32步collective约197.060ms，其中RS约98.885ms。TP8表中的EP差分则主要呈现AllReduce增时；两种形态的组、分片和prepare路径不同，不能把TP8的归因直接搬到TP2/DP4。

**额外发现**：F每卡32步还有2688个独立 `gpu_memset` 事件，每次524288B，4K合计95.502ms、逻辑写入1.3125GiB（42MiB/步）。其84次/步与两次×42个MoE层的次数相符，值得核查mctlass工作区初始化；次数一致尚未证明调用归属。这不是EP链路字节量，也不是原表BF16 FillFunctor的同一统计项。[003](003-ep-prepare-and-collectives.md)、[007](007-moe-kernel-selection.md)

## 5 MoE 调优应先证明配置真正控制内核

F日志确有 `H=4096,E=36,N=2048,device_name=MXC500,dtype=int8_w8a8.json` 缺失告警。但[utils.py](../outputs/optimization-review-20261126/source/vllm_metax/model_executor/layers/fused_moe/utils.py)93行起 `maybe_override_stage_block_size_m` 调用 `cutlass_moe_mm_w8a8_get_kernel_m`，随后覆盖两个stage的BLOCK_SIZE_M。

[fused_moe.py](../outputs/optimization-review-20261126/source/vllm_metax/model_executor/layers/fused_moe/fused_moe.py)986行分支实际调用 `mctlass_ops.cutlass_moe_mm_w8a8`。类名叫TritonExperts，并不证明最终GEMM是Triton；新trace的 `MacaGemmMoe` 也支持实际进入原生实现。

因此第一步是记录实际后端、选中kernel和参数覆盖结果；第二步才决定调原生内核选择、工作区，或对照mcTriton。不能只让告警消失就报“优化完成”。F的MoE GEMM约98.112ms/32步、11.51%的kernel预算；TP8/C8该子类约14.55%，不同负载应分开调。[007](007-moe-kernel-selection.md)

## 6 BF16 GEMV 与 W8A8 GEMM 必须分开

KDA构造时显式暂置 `vllm_config.quant_config=None`，保留BF16投影，并且q/k/v/b/f_a/g_a已经合并成一个投影。不能因为模型名称含W8A8就默认所有层为INT8，也不能提出重复的“合并六投影”任务。

[INT8 linear注册](../outputs/optimization-review-20261126/source/vllm_metax/registry/linear_kernels/int8.py)中的 `MctlassScaledMMLinearKernel.apply_weights` 走 `scaled_int8_quant → cutlass_scaled_mm[_azp]`。它和trace中的BF16 `b16gemvt*`不是同一个优化入口。先采shape/module/stride、校验是否存在重复读写，再按目标shape选择库算法或实现小M kernel。

已有[单层替换原型](../experiments/evidence/metax/glm53/gemm_replace_20261123/README.md)验证56组设备测试、24组真实权重分片测试；它保留双算与同步以验证数值，不能拿这个原型直接测速度，更不能用INT8原型覆盖BF16 KDA。[006](006-dense-gemv.md)

## 7 通信与DP形态不能只看名字

[MetaX prepare/finalize](../outputs/optimization-review-20261126/source/vllm_metax/model_executor/layers/fused_moe/all2all_utils.py)50–67行：DP>1且EP关闭仍用naive AG/RS。[AllGather/RS manager](../outputs/collectives-20261126/source/vllm/vllm/distributed/device_communicators/all2all.py)76–86行按sequence parallel选择EP或DP组。因此EP关闭不是通信关闭。

MetaX已有DeepEP low-latency入口，当前安装deep_ep为MetaX 1.0.0变体，不等于最新NVIDIA上游。插件检查package、hidden size、quant格式，并明确拒绝NVFP4/UE8M0。INT8 batched expert代码声明支持相应量化键，但这还不足以证明完整GLM/graph链路可跑通。AG/RS换DeepEP应覆盖prepare、expert compute、combine整体，路由的有效token、padding、quant scales都要一致。[008](008-deepep-candidate.md)

[通信实测](../outputs/collectives-20261126/README.md)中EP8/8KiB的两次A2A约0.1321ms、AG+RS约0.1088ms，大消息256MiB时AG/RS优势更明显。它们的输入语义与真实top-k dispatch不同，既不能证明DeepEP更快，也不能证明所有A2A实现都更慢。Decode优先关注小消息延迟、rank到达偏差、实际布局与工作区成本。

## 8 把GPU内存操作补回时间线

原热点表的kernel sum/union没有包括单独分类的memcpy和memset。本次重新解析三个DP0/TP0原始trace，按同一GPU合并三类事件区间：

| 输入 | kernel sum ms | 全部已记录GPU活动union ms | 首末已记录GPU活动跨度 ms | 跨度内未覆盖 ms |
|---|---:|---:|---:|---:|
| 4K | 852.702 | 985.592 | 1239.081 | 253.490 |
| 16K | 871.125 | 1002.973 | 1276.583 | 273.610 |
| 64K | 871.439 | 1003.685 | 1271.730 | 268.045 |

4K的D2D类memcpy累计37.962ms，另有少量H2D/D2H。union是区间并集，不能直接相加各类duration替代；“未覆盖”仅表示trace没有记录这三类设备活动，不能直接称CPU瓶颈或可消除开销。需先看同步、事件依赖、DP协调、采集器干扰和流式发送时间线。[010](010-dp-scheduling-gaps.md)

## 9 其它芯片哪些方法可以借鉴

公开资料于2026-11-26核查。下列是方法参考，不提供C500收益承诺。

| 来源 | 可借鉴的方法 | 在本项目的落点与限制 |
|---|---|---|
| [AMD GLM5.2/5.3跟踪任务](https://github.com/vllm-project/vllm/issues/57230) | 区分MoE调优、投影、indexer和共享专家，分别验收 | 同模型家族有参考价值；其MXFP4/AttnFP8与当前W8A8不同，收益不复制 |
| [AITER GLM5.3配置问题](https://github.com/ROCm/aiter/issues/5156) | 同时核实shape覆盖、tuner和实际运行内核 | 发帖者报告调优候选反而慢于已有ASM；支持007先测生效路径再调优，而非“有告警就重写配置” |
| [AITER EP调优键问题](https://github.com/ROCm/aiter/issues/3999) | 对照真实top-k及dummy/shared expert语义检查查表键 | 只是AMD的历史报告，不说明MetaX有相同bug；可借鉴记录lookup key的方法 |
| [FlashInfer gated norm](https://docs.flashinfer.ai/generated/flashinfer.norm.rmsnorm_sigmoid_gate.html) | 用单核融合归一化、权重和sigmoid gate | 该实现有SM和head dim约束；C500应先验证当前已有Triton实现，不能直接安装CUDA二进制代替 |
| [DeepEP](https://github.com/deepseek-ai/DeepEP) | 专家dispatch/combine与分组GEMM布局协同，减少非必要中间格式 | 当前上游要求NVIDIA Hopper及更新硬件、CUDA/NCCL/NVLink；与已装MetaX 1.0包的API和硬件不同 |
| [DeepGEMM](https://github.com/deepseek-ai/DeepGEMM) | 分组GEMM、小M与布局专门化的思路 | 不等于本机W8A8支持；优先研究MetaX自己的batched实现与选择约束 |
| [vLLM图模式设计](https://docs.vllm.ai/en/latest/design/cuda_graphs/) | 将graph replay、torch.compile、形状dispatch分别验证 | 当前F已真实重放32步，不再把“开启graph”当成尚未实现的优化；优先修实际OOT回退 |

共享专家融合暂不列首批实现任务：当前模型 `_fused_shared_experts_tuned` 明确限制gfx950/TP4或8/DP1/EP关，C500不是改一个环境变量就能享受。需要新的W8A8权重/scale布局和路由正确性设计。MTP会改变执行协议并依赖接受率，也暂不混入单token Decode基线。
