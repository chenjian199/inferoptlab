# 48种部署的缓存驻留容量预检

2026-11-27在metax-60启动，随后按用户要求停止，切换为[启动后计算容量的正式扫描](../matrix-scan-20261127/README.md)。本目录保存旧任务启动记录、冻结源码及轻量结果副本，不再继续寻找容量边界。

- 部署：TP8、TP4/DP2、TP2/DP4、TP1/DP8，分别开关EP；max_num_seqs取16/32，max_num_batched_tokens取2048/4096/8192，共48种。
- 输入：4096、16384、65536；输出：128、512。按最大输出512预留，同时验证两种输出各4轮回放。
- 预设并发：1、2、4、8、16、32、48、64、80、96、112、128。
- 每个并发槽独立上下文，固定路由slot%DP；驻留容量不按max_num_seqs截断。
- 通过128仅证明“至少128”；缓存驻留失败与物理容量不足分开记录。此任务不产生正式性能成绩。

## 查看进度

在60机器上执行：

```bash
docker logs -f --tail 30 inferoptlab-capacity-20261127
```

远端任务根目录为`/home/ubuntu/CJ_workspace/inferoptlab-capacity-20261127`，结果位于其`experiments/runs/capacity/`。控制器独立于SSH运行，VPN断开不会结束任务。

本机项目根目录执行以下命令，拉回状态、池规格和已完成的容量结果，不下载请求原始数据：

```powershell
python -X utf8 outputs/capacity-scan-20261127/collect.py
```

查看[结果表](collected/README.md)、[状态](collected/state.json)、[有效测点](collected/effective-points.json)。文件是最近一次收集的快照，不会自行刷新。完整输入长度的一组并发资格检查结束后才进入结果表；检查中的点可查看状态文件里的`trial_directory`及其远端`qualification.json`。

## 结果如何使用

确认当前协议的边界K后，对预设并发数组逐项取`min(c,K)`并去重。所有预设点通过则原样保留。每个实际点请求数为`4×实际并发`。长度超限、启动失败及路由/Decode协议错误保留状态，不能当作容量为零。

完整算法与限制见[CAPACITY.md](../../benchmark/load/CAPACITY.md)。`launch.py`是本次启动记录脚本，已有启动记录时拒绝重复启动；不要为查看状态重复执行它。
