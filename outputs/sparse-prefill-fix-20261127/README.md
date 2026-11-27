# C500 GLM Sparse Prefill 非法访存修复

2026-11-27 16:51（北京时间）完成原失败场景回归。TP8、图模式、4K输入、32个独立上下文预热成功，随后128和512输出各32条请求全部通过缓存、路由、单token Decode及无抢占检查。证据在[verification.json](verification.json)。完整矩阵进入新轮次，尚未全部测完。

## 原因与修复

MetaX FlashMLA的`copy_b32_sparse`用两个`int`计算`topk_sparse_idx * row_stride`，再赋给`int64_t`。乘法先发生32位溢出，错误结果随后扩展为64位。行跨度512时，索引4194304开始越过有符号32位上限。

既有原始诊断中，索引4129404的调用成功，4302400的调用失败，活动索引范围检查均通过。本轮故障在第30条独立上下文的seed预热出现，驱动记录Sparse Prefill内核ATU地址转换异常。物理缓存索引随槽分配增大，解释了请求输入只有4K仍触发此问题。

修复先将乘法两端转成`int64_t`。源码差异见[补丁](../../tools/deployment/metax-vllm/patches/sparse-prefill-offset64.patch)。部署使用C500 BF16 NoPE 512/512专用扩展，并通过[适配器](../../tools/deployment/metax-vllm/observers/sparse_prefill_repair.py)处理topk_length和输出缓冲区。

## 官方核查

本次GitHub API核查的官方最新提交为`b246af19465084b1a97d4de480c3ea0c1b356e4c`，源码仍保留先做32位乘法的表达式。提交记录保存在[official-commits.json](official-commits.json)。本次采用项目本地修复。[官方源码](https://github.com/MetaX-MACA/FlashMLA/blob/b246af19465084b1a97d4de480c3ea0c1b356e4c/csrc/utils/utils.h)

## 验证范围

- 4组query/head/topk形状，与已安装内核及PyTorch FP32参考比较，最大绝对误差0.00791，满足测试采用的BF16容差。
- 索引4194816、元素偏移2147745792的越界边界测试通过，预期全1输出的最大绝对误差为0。
- 原失败4K/C32图模式模型回归通过，128/512输出均完成。该回归每输出一轮32条请求，正式矩阵仍执行并发×4。
- 31项流程回归测试通过。

## 构建与启用

扩展复用项目此前已编译的候选构建，本轮完成数值和真机验证。固定源码、NoPE适配和构建脚本在`experiments/evidence/glm53-flashmla-offset64-20261125/`。`prepare_build.py`从固定归档生成修复源码，`build.py`在镜像中调用`setup_offset64.py build_ext --inplace`。

已验证二进制为`_inferoptlab_flashmla_offset64.cpython-312-x86_64-linux-gnu.so`，SHA256为`f3e1869d90e1d656d7af32379cc7116257da454023f77511347aa5fc481972c2`。将其安装到observer目录后，设置`INFEROPTLAB_SPARSE_PREFILL_OFFSET64=1`启用。此扩展适用C500 BF16 512/512及无attention sink的当前GLM路径。

根目录矩阵已启用该开关。新轮次启动脚本核对二进制哈希并复制到服务只读挂载目录，运行身份记录包含扩展哈希。新控制器为`inferoptlab-matrix-r2-20261127`，远端结果目录为`/home/ubuntu/CJ_workspace/inferoptlab-matrix-r2-20261127/experiments/runs/glm53-matrix`。

```bash
docker logs -f --tail 30 inferoptlab-matrix-r2-20261127
```
