# C500 GLM Sparse Prefill 非法访存修复

此目录提供已验证二进制、固定源码构建、安装和内核验证入口。所有示例从`tools/deployment/metax-vllm`目录执行。共享时可发送旁边的`sparse-prefill-fix.zip`，解压后保留目录结构。

## 修复内容

Sparse Prefill读取KV缓存时，原实现先以32位整数计算`topk_sparse_idx * row_stride`，再赋给64位变量。行跨度512时，索引4194304开始溢出。补丁将乘法两端先转成`int64_t`。

本实现采用C500 BF16 NoPE 512/512专用扩展，包含公开源码所需的NoPE适配。安装适配器负责`topk_length`掩码和调用方提供的输出缓冲区。原始差异见`../patches/sparse-prefill-offset64.patch`。

2026-11-27核查时，MetaX官方仓库最新提交仍为`b246af19465084b1a97d4de480c3ea0c1b356e4c`，源码保留原表达式，本目录交付项目本地修复。[官方源码](https://github.com/MetaX-MACA/FlashMLA/blob/b246af19465084b1a97d4de480c3ea0c1b356e4c/csrc/utils/utils.h)

## 已验证环境

| 项目 | 配置 |
|---|---|
| 设备 | MetaX C500 |
| 系统/Python | Linux x86_64、CPython 3.12 |
| PyTorch | `2.10.0+metax3.9.0.8` |
| MACA用户态SDK | 3.9.0.29 |
| 宿主驱动 | 3.9.35 |
| vLLM / MetaX插件 | 0.32.0 / 0.32.0-dev |
| 模型 | GLM-5.3-Flash-W8A8 |
| 内核输入 | BF16、Q/K维度512、V维度512、单KV head、无attention sink |
| 原始服务镜像ID | `sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b` |

二进制适配上述Python与运行库ABI。其他版本请在目标服务镜像中重新构建并验证。

## 使用已编译二进制

在运行vLLM的Linux容器或Python环境中执行。`python`应指向vLLM worker使用的解释器。

```bash
python sparse-prefill-fix/install.py \
  --binary sparse-prefill-fix/bin/_inferoptlab_flashmla_offset64.cpython-312-x86_64-linux-gnu.so \
  --sha256 f3e1869d90e1d656d7af32379cc7116257da454023f77511347aa5fc481972c2

python sparse-prefill-fix/verify.py
python sparse-prefill-fix/verify.py --boundary 4194816
```

内核验证需要一张可用C500。边界测试会分配约4GiB KV张量，请在空闲测试设备执行。可通过`MACA_VISIBLE_DEVICES`指定设备。

安装后为服务进程设置环境变量，并重新启动vLLM，使新worker加载修复。

```bash
export INFEROPTLAB_SPARSE_PREFILL_OFFSET64=1
# 在同一个环境中执行现有的vLLM启动命令。
```

Docker部署可使用下面的派生镜像，以已验证服务镜像作为`BASE_IMAGE`。Docker构建上下文为当前`metax-vllm`目录。

```dockerfile
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
COPY sparse-prefill-fix /opt/inferoptlab-fix/sparse-prefill-fix
COPY observers/sparse_prefill_repair.py /opt/inferoptlab-fix/observers/sparse_prefill_repair.py
RUN python3 /opt/inferoptlab-fix/sparse-prefill-fix/install.py \
    --binary /opt/inferoptlab-fix/sparse-prefill-fix/bin/_inferoptlab_flashmla_offset64.cpython-312-x86_64-linux-gnu.so \
    --sha256 f3e1869d90e1d656d7af32379cc7116257da454023f77511347aa5fc481972c2
ENV INFEROPTLAB_SPARSE_PREFILL_OFFSET64=1
```

安装器在解释器的site-packages写入扩展、适配器和`.pth`启动钩子，服务每个Python worker启动时自动生效。无需依赖InferOptLab的观测目录。关闭修复可将环境变量设为`0`并重启服务。

## 从固定源码构建

在包含MACA SDK/cu-bridge、C++编译工具、ninja和目标PyTorch的Linux开发镜像内执行。构建阶段使用CPU。

```bash
python sparse-prefill-fix/build.py --work-dir /tmp/flashmla-offset64-build
```

脚本从GitHub下载`source.json`指定提交，校验归档SHA256，生成64位寻址和NoPE适配源码，然后编译扩展。工作目录需未含`build-source`，以保留每次构建的独立记录。

离线构建可传入相同归档。

```bash
python sparse-prefill-fix/build.py \
  --work-dir /tmp/flashmla-offset64-build \
  --archive /path/to/FlashMLA.tar.gz
```

产物在工作目录的`build-source/`，`build-manifest.json`记录二进制SHA256。用该路径和SHA256调用安装器，再执行上述内核验证。重新构建的二进制哈希可能因工具链不同而变化。

## 已完成的验证

- 4组query/head/topk形状，与当前已安装内核及PyTorch FP32参考比较，最大绝对误差0.00791，满足测试使用的BF16容差。
- 索引4194816、元素偏移2147745792的边界测试通过，全1参考输出的最大绝对误差为0。
- TP8图模式4K/C32全部预热成功，128/512输出各32条请求均通过缓存命中、路由、单token Decode和无抢占检查。

记录见`verification.json`。该记录描述已完成的内核及模型回归，其他环境和完整性能矩阵需要在目标机器验证。
