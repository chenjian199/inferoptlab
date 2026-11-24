# MetaX 独立推理环境的构建与溯源

本指南提炼自[GLM 八卡案例](../cases/2026-11-22-glm53-w8a8-tp8/README.md)。已验证的软件组合是 C500、宿主驱动 3.8.30、容器 SDK 3.9.0.29、固定 commit 的 vLLM-MetaX 0.32.0-dev 及三项局部修复；不是任意 0.32 镜像的兼容性声明。

## 保留原环境并固定输入

创建独立容器、源码目录、wheelhouse、脚本和证据目录；原 `dcc` 容器、旧源码、宿主驱动/SDK 与标准模型权重保持原状。权重只读挂载，部署前检查磁盘、共享内存、设备节点及资源占用。用 image ID/digest 固定基底，tag 仅作名称。

本例从缓存的 0.28 基底重建，仅升级新容器用户态。官方 SDK 压缩包经 SHA256 和压缩完整性校验，检查包清单后安装；27 个私有 wheel 与来源哈希比对。最低驱动要求、网站推荐驱动、镜像 tag 字段和本机运行结果分别记录，不能互换。具体哈希、版本与证据在案例 `case.json` 和 `artifacts.json`。

## 依赖与源码构建

固定上游 vLLM commit `5df63a7203cdb9328d824a27b682e77c7b9928be` 与 MetaX commit `0962c8735ffe4795800030680311410848512b82`，在 MetaX 独立目录应用已登记修复。依赖为 Torch `2.10.0+metax3.9.0.8`、Triton `3.6.0+metax3.9.0.8`、mcoplib `0.4.14+gf3794c4.maca3.9.0.31.torch2.10`、Transformers `5.17.0`、compressed-tensors `0.17.0`。

上游以 editable、`VLLM_TARGET_DEVICE=empty`、`--no-deps --no-build-isolation` 构建；插件使用 `USE_PRECOMPILED_KERNEL=1`。这些开关依赖预先安装的配套包，不应复制成绕过依赖校验的通用命令。cu-bridge 编译工具来自 MACA SDK，并设置 `CUCC_PATH`、`CUCC_CMAKE_ENTRY=2`、`CUBRIDGE_HOME`、对应 `CUDA_HOME`；本例没有安装 NVIDIA Toolkit。完整操作入口保留在 `glmf/deploy032/` 原脚本，资产清单记录哈希。

旧基础镜像中的冲突附加包仅在新容器移除，保留完整包清单并运行 `pip check`。包管理器版本通过不代表实际源码或 native 扩展正确。

## 证明实际加载路径

同时记录 distribution 版本、Python `__file__`、git commit/工作区补丁、native 扩展路径和实际共享库。每个推理 worker 都验证来源，避免主进程正确而子进程使用旧安装。

本例实际导入 `/work/src/vllm/vllm/__init__.py` 和 `/work/src/vllm-metax/vllm_metax/__init__.py`，平台为 `MxsmlMacaPlatform`。上游包显示 `0.32.0+empty`，插件包显示 `0.32.0+g0962c8.d20261122.maca3.9.0.29.torch2.10.0`；commit 和源文件证据才解释这些字符串代表的构建。mcoplib 的版本号也不能代替具体算子 schema 检查。

## 恢复已有基线

恢复案例中匹配的源码和脚本归档到记录的 bind mount 路径，先核对 SHA256、模型权重和本机 image ID，再使用原 `create_bootstrap.sh`，将 `GLM53_IMAGE` 指向 `glm53-vllm032:verified-20261122`。脚本中的容器名称和目录是本例固定值；同名容器已存在时脚本会复用它，设置变量不会替换已有容器。要开展新实验，先审查并改用新的任务名和目录。

依赖镜像不包含 editable 源码挂载、完整模型和所有脚本；镜像单独存在不能保证复现。先完成[分层验收](inference-validation-and-freeze.md)，再扩展并发、上下文和算子优化实验。
