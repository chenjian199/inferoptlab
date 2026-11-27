# 单文件矩阵正式性能扫描

2026-11-27根据用户最新要求启动：取消独立的逐并发容量边界搜索，在每个部署启动后计算预算，直接进行完整性能矩阵扫描。任务状态以远端为准。

配置：[benchmark-matrix.yaml](../../benchmark-matrix.yaml)。入口：[matrix_run.py](../../benchmark/load/matrix_run.py)。48种部署；3种输入、2种输出、12个预设并发，容量裁剪前3456点，每点请求数为实际并发×4。

每个DP引擎的预算为`floor((实际池块数−固定预留)/(解析的运行块需求+4个原始KDA状态块+1个Attention尾页副本))`。此模型只接受已核对的GLM混合缓存布局，其他布局报错。结果是保守计算预算，不是实测物理最大并发。逐请求缓存命中、固定DP路由、query=1及无抢占检查决定成绩是否有效。

不额外发送两种完整输出各4轮的容量资格请求。预热后2-token检查仅确认路由和Decode路径；正式AIPerf请求本身验证完整输出及4轮复用。失败保留记录，重启并重新预热后重试一次，之后继续其他点。精度验收仍未建立，不宣称模型质量已验收。

在60上实时查看：

```bash
docker logs -f --tail 30 inferoptlab-matrix-20261127
```

任务根目录：`/home/ubuntu/CJ_workspace/inferoptlab-matrix-20261127`。原始结果位于其`experiments/runs/glm53-matrix`，主机硬件清单另存于根目录`host-inventory.json`。模型身份保存文件路径、大小和修改时间清单及tokenizer指纹，未额外重算全部权重哈希。

本机拉取轻量结果：

```powershell
python -X utf8 outputs/matrix-scan-20261127/collect.py
```

[当前摘要](collected/README.md)、[完整汇总CSV](collected/summary.csv)、[任务状态](collected/state.json)。这些是最近一次收集的快照。

旧容量预检已停止并保留证据。旧预检TP8的4K/C16曾出现非法访存，属于运行故障，不能归为容量不足或成功性能点。

首个正式请求组曾因AIPerf离线模式把本地tokenizer目录当成Hub仓库ID而失败，未产生计时样本。已在项目的AIPerf适配钩子中修正现存目录解析，并在相同控制器内验证`Tokenizer.from_pretrained`成功。部署和负载参数保持本轮冻结值；客户端钩子的变更前后哈希及身份快照保存在`tokenizer-fix.json`和远端`identity-before-tokenizer-fix.json`，后续子进程使用修正后的钩子。
