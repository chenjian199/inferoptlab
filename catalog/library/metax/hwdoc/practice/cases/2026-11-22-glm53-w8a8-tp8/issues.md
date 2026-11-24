# GLM 八卡部署问题与适配记录

以下问题观察于 2026-11-22。三项代码修复仅应用于独立 MetaX commit `0962c8735ffe4795800030680311410848512b82`，配套 vLLM commit `5df63a7203cdb9328d824a27b682e77c7b9928be`、mcoplib `0.4.14+gf3794c4.maca3.9.0.31.torch2.10`。原 `dcc` 与旧源码未改。文件位置及 SHA256 见 [artifacts.json](artifacts.json)，验证范围见 [case.json](case.json)。

## MIM 鉴权成功后大层下载仍失败

- 症状与复现：鉴权及目标 manifest 已 HTTP 200，随后 Docker pull 仍超时/EOF；对被测大 blob 发 Range 请求返回 200。
- 根因边界：鉴权问题已解决，剩余故障处于大对象传输链路；尚未证明具体中间网络设备或服务端超时配置。匿名 token 签发成功不能证明 pull 授权。
- 处理：保留完整层和部分文件；不把 200 响应当 206 追加。代理改善部分端点，最终改用缓存基底及完成校验的 SDK/wheel 重建。
- 验证：摘要 `registry_diagnostics`、`transfer_failures` 和 `original_mim_image_available=false`；成功的是独立基线。
- 后续条件：仅在大 blob 完整 digest 校验、镜像完整导入并检查之后才可将原 MIM 镜像状态改为可用，新增日期记录，不覆盖本次失败事实。

## MoE alignment 的 7 与 8 参数 ABI

- 症状：模型加载后 warmup 报 `moe_align_block_size` 参数数量错误。
- 复现入口：`glmf/deploy032/test_moe_alignment_compat.py`；直接检查已加载 native schema，再对齐 CPU 参考输出。
- 根因：固定 mcoplib 提供 7 参数，上游 vLLM 0.32 调用包含第 8 个可选 scatter 输出。
- 修复：新增 `vllm_metax/patch/bugfix/moe_align_legacy_abi.py`，仅在精确旧 schema 时安装桥接，透传前 7 项，拒绝非 None scatter；新 schema 保持上游路径。同步导入与 AUDIT 登记。
- 验证：24 个 GPU/CPU 参考对齐用例、BF16 MoE sum 及不支持 scatter 的拒绝行为；见 [moe_alignment_compat.json](evidence/moe_alignment_compat.json)。这不是新 ABI scatter 支持验收。
- 移除条件：部署的 native provider 实现匹配上游的 scatter schema 后，在无桥接状态运行同类参考及真实模型回归；不得仅凭版本号删除。
- 资产注意：tracked diff 不包含新增模块，必须同时恢复补丁和独立的 `moe_align_legacy_abi.py`，或使用配套完整源码归档。

## INT8 sparse indexer 的 Tensor 契约

- 症状：长 prefill 触发 `tuple.dtype`；纯加载和短路径不能覆盖该问题。
- 复现入口：`glmf/deploy032/test_glm_indexer_int8.py`，含不同形状的 INT8 scorer 与 CPU 参考对比；真实长前缀请求另行覆盖。
- 根因：INT8 分支已经把 Q scale 折入 weights，native scorer 要求 Tensor Q，旧调用仍传 `(q, scale)`。
- 修复：`models/glm5next/metax/sparse_indexer.py` 中仅 `use_int8_cache` 分支传 Q Tensor；其他 dtype 继续 tuple，避免重复乘 Q scale。
- 验证：6 个 GPU/CPU 用例，最大绝对误差 0.000732421875；见 [glm_indexer_int8.json](evidence/glm_indexer_int8.json)，随后长前缀真实生成通过。不是全部 KV dtype、形状和并发路径的认证。
- 移除条件：目标源码已修复同一 native 接口契约，或 provider 契约变更；先检查源代码并在目标版本运行参考用例和长 prefill，再去掉本地改动。

## FP8 兼容加载器吞掉 INT8 scale

- 症状：接口修复后仍重复输出或长前缀回答错误；首次 MLA 层出现 NaN，投影中出现约 1e36 的异常值。独立原语数值检查通过，切换采样或同步单序列未解决。
- 复现入口：`glmf/deploy032/test_glm_mla_scale_loader.py` 与 `test_cache_consistency.py` 的逐层诊断。前者直接验证真实加载函数的参数所有权；后者定位异常层，不能单靠脚本名称推断是 cache 根因。
- 根因：`models/glm5next/common/model.py::_try_load_fp8_attn_proj` 只识别目标 `weight_scale_inv`。INT8 目标使用 `weight_scale`，被 FP8 回退缓存误消费，真实 INT8 scale 未初始化。
- 修复：目标参数存在 `weight_scale_inv` **或** `weight_scale` 时返回 False，由正常量化加载器加载。原生 INT8 构造已正确启用，不是把 BF16 模块强制转换 INT8。
- 验证：[before_after](evidence/glm_mla_scale_before_after.json) 显示误消费和缓存从 True 变 False；[loader](evidence/glm_mla_scale_loader.json) 的 12 个用例覆盖四类投影的权重/scale 所有权，以及 FP8→BF16 回退的两种 scale 名称和两种输入顺序。8 个 worker 每个 33 个 MLA INT8 scale 均有限正值；三项真实生成通过。
- 未验证：这组用例没有覆盖全部量化 checkpoint、模型和框架运行模式；不是全矩阵升级认证。
- 移除条件：目标源码包含等价所有权修复，在移除局部改动后通过上述 loader、FP8 回退与真实 TP8 回归。先保留旧基线以便比较。

## V1 非法显存访问的未闭环状态

- 症状：V1 混合调度尝试发生非法显存访问；最终 MLA scale 修复前的历史失败。
- 处理与验证：仅清理本任务 worker，随后八卡 BF16 恢复测试通过。最终成功路线使用 V2 同步单序列 eager。
- 边界：没有在最终 scale 修复后重测 V1，也未证明 V1 故障与 scale 缺陷是同一根因。不得标记 V1 已修复或已通过。
- 后续：独立资源窗口重跑同配置，记录 native 错误、层级数值与清理状态，再决定问题归属；引用原失败与恢复证据的哈希见资产清单。

## 冻结成功但 image ID 解析失败

- 症状：Docker 29 的 `commit --pause=false` 输出弃用警告后，脚本把多行 stdout 当作 image ID，后续 inspect 失败。
- 根因与处理：commit 本身已成功；按确切 tag 检查 ID、来源和验证标签后确认产物。修复脚本使用 `--no-pause`，只提取唯一 SHA256 行。
- 验证：冻结镜像 ID 与新容器检查记录一致，导入/8 卡发现/pip check 通过；未在新容器重新跑完整模型。
- 关联经验：`docker top -eo args` 在该版本要求 PID 列，改为 `-eo pid,args`。tar 排除开发缓存、先写临时文件并校验，避免权限失败留下看似完整的包。
- 移除条件：未来工具链若输出/参数契约变化，针对新版本验证解析和产物检查；不因一次耗时长或 inspect 失败就重新 commit。
