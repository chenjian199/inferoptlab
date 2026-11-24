# GLM-5.3-Flash-W8A8 greedy 重复性排查

观察日期：2026-11-23（Asia/Shanghai）。状态：本轮排查、独立进程验证和规则落地已完成；历史9题分叉的唯一根因仍未复现，不宣称已修复模型或算子。

## 已完成的独立进程结果

| 对照 | 样本 | token 全等 | 原始 HumanEval 测试 |
|---|---:|---:|---:|
| A、B、C 三次全新引擎，同一 smoke32 顺序 | 各32题 | 任意两轮32/32 | 各31/32 |
| A 同进程再执行 | 32题 | 32/32 | 31/32 |
| B 同进程倒序执行 | 32题 | 32/32 | 31/32 |
| C 历史9题，开启 top-5 logprobs，两遍 | 各9题 | 9/9 | 各8/9 |
| 原版生成脚本，第四个独立 plain 引擎 | 32题 | 与A为32/32 | 31/32 |

五轮 plain32 的唯一失败均为 HumanEval/37 的解析失败；没有补缩进、修复答案、重采样或更换评分规则。本轮观测到31个稳定通过题、1个稳定失败题；这是本轮32题集合的观测，不是完整164题的稳定性声明。

证据：`repeatability_summary.json`、`runs/*/{generation_manifest,score_summary}.json`、`runs/*/{generations,correctness}.jsonl`、`evidence/process_{a,b,c}.json` 和对应 `environment.json` / `final_workers.json`。

原版 runner 对照保留历史导入、tokenizer、预检和 SamplingParams 复用流程，仅限制到 smoke32 并给新输出目录设置评分所需所有权。输入 manifest 与 settings 完全一致，输出与A逐 token 一致；与历史 smoke/full 交集分别仅25/32、23/32一致。故本轮没有证据支持“新 runner 导致历史差异”的解释。证据：`evidence/legacy_control.diff`、`legacy_inputs_sha256.json`、`legacy_control_process.json`、`legacy_comparison.json`。

## 历史分歧和本轮输出的关系

历史 smoke32 与 full164 交集的9个分歧题为 HumanEval/10、37、89、94、123、144、148、156、162。首个输出 token 分歧位置（从0开始）依次为8、0、0、64、1、2、52、4、1。共同输入和第一处分歧由 `evidence/historical_divergences.json` 与 `data/divergence_probes.json` 固定。

本轮 A 与历史 smoke32 只有25/32逐 token 一致；不同题为10、72、94、104、117、123、148。72、104、117不在原先9题内，因此后续不能只把9题列为“允许变化”的白名单。两轮31/32的功能成绩相同，也不意味着输出相同。

原始153/164基线继续作为不可覆盖的历史参考，不能用新生成替换 gold，也不能把“总分至少153”作为候选算子通过条件。

## 已核实的配置与排除项

- A/B/C 使用显式 `temperature=0, top_p=1, seed=0, max_tokens=1024`，解析后的 `top_k=0`、sampling type 为 GREEDY。模型默认 sampling config 虽显示 temperature=1，但不是这批请求的实际参数；部署版本的 `update_from_generation_config` 只补 EOS/停止 ID，不覆盖显式温度。
- 八卡 TP=8，V2 GPUModelRunner，eager，max_num_seqs=1，max_model_len=max_num_batched_tokens=4096，关闭 prefix caching 和 async scheduling。生成输入直接使用冻结 token manifest。请求并发及顺序已在同序/倒序对照中控制。
- 固定镜像 `sha256:9bbf20dbcaaf52b794b887f0311a6dcbff6d23bb0a78b72fb0f442f8aab0f285`。上游源码 commit `5df63a7203cdb9328d824a27b682e77c7b9928be`，MetaX commit `0962c8735ffe4795800030680311410848512b82` 加既有适配补丁。源码挂载只读；9,334个文件和8个符号链接与冻结源码 archive 一致。
- 实际 worker 依赖为 torch `2.10.0+metax3.9.0.8`、Triton `3.6.0+metax3.9.0.8`、mcoplib `0.4.14+gf3794c4.maca3.9.0.31.torch2.10`。不是根据镜像 tag 猜测依赖。新旧容器的依赖目录没有 docker writable-layer 改动；mcoplib gumbel 源文件哈希一致。
- 新目录复制了原实验可读编译缓存，未写原缓存。未能复制的 root-only modelinfos JSON 在新环境重建后，SHA256 与旧文件相同。但推理日志仍出现新 shape 的 JIT 编译，不能声称缓存执行状态完全一致或已全面预热。

这些检查排除了已核对文件范围内的源码/依赖漂移和显式采样配置差异，不能证明全部运行时状态一致。权重使用同一只读挂载，本轮未重新读取全部约328GB权重计算哈希。

相关证据：`evidence/source_integrity.json`、`dependency_layer_comparison.json`、`model_metadata_cache_comparison.json`、`cache_strategy.json`、`source_review/`。

## 当前归因

**没有复现历史9题分叉，因此不能给出已证明的唯一根因。** 本轮没有发现 greedy 偷换成随机采样、并列最大值择优差异、已核对源码/依赖文件变化，或32题同序/倒序导致的变化。prefill/cached 的路径差异确实存在，但本轮没有造成 argmax 改变，不能拿它解释历史分叉。

历史生成只保存了最终输出，没有当时首处分歧位置的完整 logits、中间状态或逐请求内核选择，无法追溯证明究竟是哪一步数值执行发生变化。本轮复制的是原实验结束后的可读编译缓存，也没有完整重放历史 full164 前面的请求序列；不同预热/编译路径、完整请求历史与未观测运行时状态仍是待验证方向，不能直接写成原因。

若继续做因果定位，下一组应预先固定冷/热**独立**编译缓存与完整历史请求序列两个变量，在首处分歧前采集相同前缀的实际内核与输入/状态，先复现分叉再缩小算子范围。本轮未执行这组实验，也没有验证 C500 的全局确定性模式。算子替换阶段可以使用下面的同期 B0/C 配对标准推进，但不能跳过数值契约或把历史波动当作退化豁免。

## 固定前缀诊断的解释边界

两组108次有效观测已完成，每次采集135个模块位置（45层的 attention、MLP 和 decoder 输出），完整 logits 长度154,880。108/108实际温度为0，全部有限，CPU/GPU argmax 与 sampler 选择一致；没有并列最大值，top-1/top-2间隔为0.125～1.25。该范围是这些诊断位置的观测，不能外推到历史运行或全部 token。

| 比较范围 | 配对数 | logits 全等 | argmax 改变 |
|---|---:|---:|---:|
| 同进程，同路径（三遍两两比较） | 108 | 108 | 0 |
| 跨进程，同路径 | 54 | 54 | 0 |
| 同逻辑前缀，prefill 对 cached | 54 | 12 | 0 |

同路径各已采集模块输出也全部逐值相等。跨路径42组不同的比较覆盖7题；另2题的历史分歧位于第0个输出 token，尚无输出前缀需要 cached decode，其两种探针均实际走首步 prefill，12组全等不能算作两个不同计算内核一致的证明。

跨路径最大 logit 绝对差2.1953125、最大 RMSE 0.39134838587851156；最早变化的已采集模块为 `language_model.model.layers.0.self_attn`。按模型配置与源码，该层是 **linear attention / KDA**，字段名 `self_attn` 不代表传统全注意力。此处未采集该模块的完整输入和内部全部算子，不能断言差异最初就在该模块内部产生，也不能用2.1953125作为候选实现的允许误差。

证据：`evidence/tensor_summary.json`、`tensor_analysis.json`、`diagnostics_d{1,2}/`、`first_layer_source.json`。完整自产张量留在远程，每个文件在 `tensor_analysis.json` 记录路径、大小与SHA256。

D1/D2 在两个额外新进程中，对9个历史共同前缀分别执行 prefill 和强制 cached decode，每种各重复三遍。采集 rank 0 各 decoder layer 及若干子模块最后一个位置的输出、完整 processed logits，以及 trace 覆盖之前的 sampler 选择。

cached 路径通过 V2 trace replay 强制共同前缀，再追加一个占位 token，使目标位置得到实际计算。最终返回的占位 token 不是模型决策；分析使用覆盖之前保存的 greedy 选择。v4 忽略了 input processor 的长度截断，未计算目标位置就停止；失败及源代码摘录保存在 `evidence/failed_diagnostic_v4/`，不纳入正式观测。

同步 hooks、trace replay 和 logprobs 都是附加仪器。prefill 与 cached decode 具有不同的计算路径；它们的差异不能直接认定为同条件随机波动，更不能据此追认历史分叉的唯一原因。首个变化的已采集模块只是定位边界，不等于该模块内部某个算子已被证明有缺陷。

## 后续验收规则

完整规则见 [REGRESSION_POLICY.md](../../../../../catalog/library/metax/methods/regression-policy.md)。功能门槛由 `harness/check_functional_gate.py` 实现，规则测试覆盖稳定题退化不能被改善抵消、波动题下降、不完整重复和原样比较。

1. 冻结输入 token、数据版本、解码/停止条件、TP/调度/顺序、实际源码依赖与评分沙箱。实验不完整或基础设施错误判 `invalid`。
2. 局部算子逐项冻结语义与精度阈值，使用独立高精度参考；整数/索引/mask/舍入/状态契约必须满足。不能用统一“INT8允许1%”容差。
3. 固定共同前缀比较 prefill/cached 的 logits 和中间状态。有限次 B0 自差异是观测值，不是全局误差上界。自由生成分叉之后输入已不同，不能直接逐位置比较 logits。
4. 同期 B0/候选各三个独立进程完整164题，交错执行。稳定通过题任何退化判 `fail`；波动题通过次数下降判 `inconclusive`，不允许总分抵消。32题仅为筛查。
5. 四层均通过后再验收性能收益。本轮 hooks/评分/加载耗时不作为算子优化性能基线。

上游 [vLLM 可重复性说明](https://docs.vllm.ai/en/stable/usage/reproducibility/) 不给默认执行全局确定性保证；[v0.32.0 batch invariance](https://docs.vllm.ai/en/v0.32.0/features/batch_invariance/) 的硬件条件不能直接套用到 C500。本轮未启用该开关，也未声明此 GLM/MetaX 组合支持它。

## 保留与验证

原 `glmf/baseline_ops` 保持不可变，结束后再次通过65个归档文件检查，原结果仍为 smoke32=31/32、full164=153/164。新实验位于独立目录和容器，不向 `dcc`、`glm53-vllm032` 写入源码或配置。三个旧容器的身份、镜像、挂载和运行状态前后逐项一致；只停止了新增 `glm53-repeat-v1`，未删除容器或结果。

结束时 `mx-smi` 显示8卡利用率0%、每卡858MiB、无GPU进程；同时保留原始 exit code=4、MACA unknown 和部分N/A，不把该命令当作通过的设备健康检查。见 `evidence/gpu_after.txt`、`closeout.json`、`preserved_{before,after}.json`。

完整108份诊断张量已在远程归档并逐文件核对：`/home/metax/glm53-repeatability-20261123/archives/diagnostic_tensors_20261123.tar.gz`，302,241,093字节，SHA256 `2c6b7d70ec33898a40dbb404f92a77ec208382b14d51a2cd9e46a1adcafab4bc`。原始失败v4材料单独保留，不混入正式观测归档。完整张量没有下载到本地；本地保存完整分析、张量清单和哈希。

本地审阅材料归档为 `archives/repeatability_20261123_v1.tar.gz`，文件清单见 `artifact_manifest.json`，最终验证见 `verification.json`，归档SHA256及远程复核见 `archive_receipt.json`。7项规则/分析测试通过，真实A/B/C数据自对照通过功能检查；这是检查器自检，不是任何候选算子的验收结果。
