# 硬件发现与性能校准

本模块把实机测试固定为 **计划 → 探测 → 测试 → 报告 → YAML 配方**。新机器复用同一套协议，只修改 SSH 别名、本机镜像 ID、设备范围及测试矩阵。当前已在 MetaX C500 / MACA 上验证；其他厂商需要实现采集和执行适配，不能直接把 `backend` 改成厂商名。

四台新集群的只读发现计划见 [plans/metax-four-nodes.yaml](plans/metax-four-nodes.yaml)，实际清点结果见 [集群记录](../../docs/cluster-intake-20261123.md)。MACA 管理命令未提供的驱动预留显存使用 `null`，不会按零导出。`probes/runtime.py` 可在 Linux 上额外检查模型文件、镜像包版本候选和模块位置；该探针不加载模型、不分配 GPU，不把镜像存在视为推理兼容性已通过。

## 快速开始

在仓库根目录运行。控制端依赖 Python、OpenSSH，以及 `schemas/requirements.txt`；控制端不需要安装 PyTorch。远端需要 Linux、Python 3、`mx-smi`、Docker 使用权限，以及已经存在且包含 MACA PyTorch 的镜像。SSH alias 和主机指纹应已配置。

复制 [plans/metax.yaml](plans/metax.yaml) 为新计划，修改 `id`、`version`、`hosts`。示例的镜像 ID 只代表 metax 已验证的本地镜像。新机器用 `docker image inspect --format '{{.Id}}' <本机镜像>` 获取自己的完整 ID。工具不拉取镜像、不安装远端软件。

```powershell
python -m pip install -r schemas/requirements.txt

# 离线校验并查看执行参数
python -m tools.hardware plan tools/hardware/plans/my-cluster.yaml

# 只采集设备、拓扑和环境；占用中的机器也可探测
python -m tools.hardware inspect tools/hardware/plans/my-cluster.yaml --out runs/hardware/my-cluster-inspect

# 真正执行 GPU 微基准；输出目录必须不存在
python -m tools.hardware run tools/hardware/plans/my-cluster.yaml --out runs/hardware/my-cluster-run1

# 校验文件哈希并显示每张卡的结果
python -m tools.hardware report runs/hardware/my-cluster-run1

# 导出到 schemas，自动生成来源、设备、主机、运行环境及实测配方
python -m tools.hardware export runs/hardware/my-cluster-run1 --out schemas
python tools/specs.py validate
```

需要先查看生成物时，将导出目标设为 `--out runs/hardware/my-cluster-review`；它同样生成 `recipes/` 和 `evidence/`。导出目标必须位于仓库内，保证来源路径可解析。检查后可从原始 run 再导出到 `schemas`。不要直接移动暂存 YAML：其中的来源路径指向暂存证据。

每次正式录入使用新的计划 `version` 或 `id`，已有文件和 `(id, version)` 不会被覆盖。同一观察的 inspect 与 run 任选一个导出，或给它们分配不同版本。重复性能观测保留为不同版本；旧证据和旧配方保持可追溯。

## 测试计划

计划结构由 [hardware-test.json](../../schemas/definitions/hardware-test.json) 校验，示例也纳入 `tools/specs.py validate`。参数之外的未知字段会报错。

| 参数 | 含义 |
|---|---|
| `hosts[]` | 多台机器；按列表依次执行，不同时争抢资源 |
| `hosts[].id` / `ssh` | 稳定节点标识 / 已配置的 SSH alias，分别唯一 |
| `backend` / `image` | 首版为 `metax` / 远端已有完整 Docker image ID |
| `devices` | 物理 GPU ordinal 列表，或 `all`；不是容器内 ordinal |
| `max_devices` | 本次允许测试的最大设备数；`all` 超限也拒绝执行 |
| `gemm_shapes` | `[M, N, K]` 列表，dtype 与 shape 做笛卡尔积；维度须为 64 的倍数 |
| `dtypes` | `float16`、`bfloat16`、`float32` 的子集 |
| `copy_sizes_mib` | 设备内复制的单侧缓冲区大小，MiB = 2²⁰ bytes |
| `warmup_iterations` | 每个测项预热次数 |
| `iterations_per_sample` | 每个计时组的循环次数，输出折算为单次毫秒 |
| `repeats` | 每个测项计时组数，至少 3 组；默认 5 组 |
| `max_allocation_mib` | 测项张量及正确性检查缓冲区预算，不包括运行时上下文/库工作区 |
| `timeout_seconds` | 每张卡整个测试进程的超时，包括容器启动及 PyTorch 初始化 |

测试全部卡时设置 `devices: all`。测试多节点时在 `hosts` 追加相同字段；每个节点可以有不同的镜像和设备数量。首版为每节点导出独立的单节点 `HardwareSpec`，保留异构 CPU/显存/驱动事实；不会把节点间网络推断成已测拓扑，也不汇总成“集群峰值”。不同 SSH alias 若实际指向同一台主机，需在计划中去重。

## 指标与固定口径

| 分类 | 当前输出 | 证据与边界 |
|---|---|---|
| 身份与容量 | 型号、板卡/芯片序列号、PCI BDF、物理显存、驱动预留、已用显存 | `mx-smi`；物理显存与 PyTorch 可见容量分别保存 |
| 主机环境 | CPU sockets/cores/threads、NUMA、DRAM、OS/kernel、驱动/MACA、网卡名 | `lscpu`、`/proc`、`/sys`、`ip`；包含虚拟接口，未测速 |
| 拓扑 | GPU NUMA/CPU 亲和、协商 PCIe 速率/宽度、卡对连接类型 | `MX1`/`SYS` 等是拓扑类型，不是带宽值 |
| GEMM | 每 dtype/shape 的 samples、median、TFLOPS | `torch.mm`；FP32 禁用 TF32；`2*M*N*K/(median_ms/1000)/1e12` |
| 设备内复制 | 每缓冲区大小的 samples、median、GB/s | `copy_`；读+写流量 `2*payload_bytes/(median_ms/1000)/1e9` |

计时用 GPU Event，预热和输出检查不计入样本，最后一个 Event 同步后读取时长；结果保留每组单次耗时，不只留一个平均值。GEMM 使用 0.125 常量输入，检查输出是否为 `K/64`；复制检查所有输出为 1。这是执行正确性冒烟检查，不代替复杂输入的数值精度或模型质量验收。

同一缓冲区重复复制可能受缓存影响，特别是小缓冲区；结果是该 shape/size/runtime 下的有效速率，不直接称为 HBM 峰值。没有测得的 INT8 算力、H2D/D2H、P2P、AllReduce/AllToAll、跨节点网络、稳定功耗及模型 tokens/s 不填入配方。集群通信测试后续需独立协议，包含 rank 映射、消息大小、MCCL/NCCL 参数和算法/总线带宽口径。

## 执行与失败处理

1. 采集全部设备的只读 inventory；检查目标 ordinal 和 `max_devices`。
2. 验证本机镜像 ID，取得主机协作锁。每张卡开始前重新读取全机 GPU 进程列表；任何 GPU 已有进程就停止本次节点测试。空闲判定无法解析时也停止。
3. 每张卡使用独立的临时容器。`MACA_VISIBLE_DEVICES` 指向物理 ordinal，检查运行时仅能看到一张卡，再测试逻辑 GPU 0。容器禁用网络，只映射必要设备，结束或超时只清理本次创建的容器。
4. 测试后重新读取进程列表。占用变化、超时、输出错误、清理异常均记录为未完成；当前节点不再继续测试剩余卡，其他节点仍可独立完成。
5. 本地保存成功及失败记录，退出码 `0` 表示本次操作成功，`2` 表示运行未完成或校验失败。失败运行可以 `report`，不能 `export` 为完整测量。

锁只能协调使用本工具的任务，开始/结束快照不能保证整个窗口都独占，因此配方固定标记 `exclusive_preflight_only`。操作者应在机器预约空闲窗口执行。控制端中断/SSH 异常时保留已有归档；远端进程若仍存活，继续受每卡超时和自身清理逻辑约束。中断后先检查机器状态，再选择新输出目录重跑。

硬件健康默认 `unverified`；读到明确不可用或错误记录时标记 `degraded`。GEMM 成功不会把健康状态提升为 `healthy`，不会清除既有链路故障历史。正式冻结仍需处理健康问题。

## 证据与配方

```text
run/
  plan.json                 # 实际执行的完整计划快照
  inventory.py              # 归档的采集脚本
  benchmark.py              # 归档的性能脚本
  worker.py                 # 归档的远端执行器
  <node>/worker.py           # 含精确参数的实际发送脚本
  <node>/result.json         # inventory、前后进程状态、逐卡结果、stdout/stderr、清理结果
  manifest.json             # 运行状态及上述文件的 SHA-256

schemas/
  evidence/<plan-id>/<version>/   # 完整归档副本
  recipes/sources/               # SourceDocument
  recipes/hardware/              # 逐设备 profile + 每主机 inspected HardwareSpec
  recipes/runtimes/              # 每张已测 GPU 的实际 RuntimeSpec
  recipes/measurements/          # 每张已测 GPU 的 HardwareMeasurement
```

导出检查哈希、完整节点/设备集合、真实执行协议、shape/dtype/重复次数、前后空闲状态、镜像身份及所有引用。`HardwareMeasurement` 的速率会从原始样本和操作数重新计算，校验通过后才写入 YAML。哈希用于发现文件变化，不是独立第三方签名。单独 `inspect` 可以导出 inventory 配方，但不会生成 runtime 或 performance 记录。

## 已验证记录

2026-11-23 在 `63metax` 上完成统一入口实测：GPU0、4096³ GEMM、256 MiB 设备内复制、10 次预热、每组 20 次、5 组。FP16 **225.216 TFLOPS**、BF16 **225.075 TFLOPS**、FP32 **29.298 TFLOPS**，复制 **1373.695 GB/s**。8 张卡均完成 inventory，本次仅 GPU0 执行性能测试。

- [原始运行 manifest](../../schemas/evidence/metax-hardware-baseline/1.0.0/manifest.json)
- [本次主机配方](../../schemas/recipes/hardware/metax-hardware-baseline-metax-host-1.0.0.yaml)
- [本次 GPU0 实测配方](../../schemas/recipes/measurements/metax-hardware-baseline-metax-gpu0-measurement-1.0.0.yaml)

另在物理 GPU1 上完成小规模隔离冒烟测试：运行时仅见 1 张卡，逻辑编号为 0；前后进程检查及容器清理通过。[该记录](../../runs/hardware/metax-isolation-smoke-20261123/manifest.json) 仅验证非零 ordinal 的执行路径，不作为性能基线录入配方。回归结果：79 项测试中 78 项通过，1 项因历史原始附件缺失跳过；213 份规约通过结构、引用和语义校验。

## 代码边界与扩展

`cli.py` 提供入口；`config.py` 校验参数和显存预算；`runner.py` 管理 SSH 和归档；`remote.py` 管理空闲检查、容器与超时；`probes/` 保存可独立发送到远端的脚本；`metax.py` 解析厂商观测；`export.py` 负责配方映射和校验。

新增平台时需要同时增加 inventory probe、标准化解析、远端设备/容器适配及测试；只有真机验证后才扩展 `backend` 枚举。性能 probe 使用 PyTorch 接口，但设备选择、运行时和健康判断并不跨厂商通用。

原来的 `tools/collect_metax.py`、`tools/run_metax_calibration.py` 保留为兼容入口，并复用这里的 probe；新项目使用统一入口。旧证据目录内归档的脚本保持原样，不随代码修改。

```powershell
python -m unittest tests.test_hardware_tools
python -m unittest discover -s tests
```
