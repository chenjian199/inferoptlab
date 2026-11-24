# 卡6热复位与故障复发记录

观察日期：2026-11-23，以下时间为北京时间（Asia/Shanghai）。**一次获授权的GPU热复位短暂恢复了设备和链路，但默认路径八卡通信检查中相同故障复发。未启动模型，32/32/4对照仍待恢复后执行。**

## 实际执行和结果

1. 复查无GPU进程、所有容器停止、metax驱动引用数0；持有项目GPU资源锁。
2. 14:45:41，以root执行一次`mx-smi -r -i 0000:5b:00.0 -y`。工具报告处理GPU4/5/6/7，返回0。未做第二次复位。
3. 等待90秒后，14:47:11八卡均Available，GPU4～7的12个MetaXLink端口全部up、32GT/s、x16，AER计数清零。服务器boot_id未变，驱动仍3.10.14。该阶段没有新不可纠正错误；复位过程中驱动自动重新初始化设备，不是安装/升级/人工卸载重载驱动。
4. 创建独立容器`glm53-gemm-recovery-v1`，固定镜像`9bbf20dbcaaf`，只读旧源码/权重，独立缓存与结果。执行有120秒外部上限的八卡检查：每卡8×8矩阵乘，再做长度1/16/1024的all-reduce；不禁用P2P。
5. **14:49:38**，GPU6与GPU7的metalk4宽度再次从x16降为x4；**14:49:48**，GPU6再次报告EID0x2119、status0x00100000、AER[20]Unsupported Request，active status变0。
6. 各rank日志报告首个1元素ALLREDUCE超过45秒超时，外部进程退出124。长度16/1024测试未通过；没有成功通信结果。按测试源码顺序，各rank到达all-reduce意味着前置本地计算断言已通过，但没有单独保存每卡计算回执，不能替代完整验收。
7. 14:51:43停止本次容器后，无GPU进程、驱动引用数0；卡6仍Not Available，卡6/7的port4仍down/x4，卡6计数CE=1、UE=1。

初次`mx-smi`汇总命令返回4，但正文各卡均Available；不能单凭该返回码认定复位失败。真正失败证据是后续新AER事件、设备状态回退及collective超时。复位会清零错误计数，初次0计数不等于长期无故障。

## 已保留的环境与实测边界

- 本轮没有服务器重启、驱动/固件安装升级、ACS参数变更、MetaXLink手工开关或第二次热复位。
- 原dcc、glm53-vllm032、glm53-heval-v1、glm53-repeat-v1、glm53-gemm-v1的身份、镜像、挂载和运行状态保持；新容器已停止。
- 旧基线65文件、重复性实验135文件、GEMM原型69文件哈希检查通过。原153/164精度结果未变。
- 本轮没有加载模型或注入GEMM候选，无新HumanEval分数。`pilot/`内32/32/4程序及评分流程只准备好，未执行。
- 故障定位到卡6—卡7的port4路径及其错误事件。尚不能区分连接器/板卡/链路信号质量、固件、驱动、PCIe路径等具体原因；不能认定是模型或自编GEMM导致。

## 下一步，需另行授权

已达到[预先约定的停止条件](RECOVERY_PLAN.md)：单次复位后故障复发，不继续反复复位或强行跑推理。厂商Warm Reset指南建议复位后设备/拓扑仍异常时冷重启（来源、版本与访问限制见RECOVERY_PLAN）。

优先安排有BMC或现场开机保障的冷重启，再复查链路和最小通信；冷重启也不能保证修复物理故障。若用户选择先普通操作系统重启，可授权一次`sudo systemctl reboot`，SSH将断开，恢复连接后重新核对boot_id、驱动、容器、GPU与链路；普通重启不等于断电冷启动，可能不能清除故障。两种重启都尚未执行。

本机有`/dev/ipmi0`，但未安装`ipmitool`；本轮未安装工具或尝试裸IPMI控制，没有已核实的BMC远程电源入口。不要通过SSH直接关机后假定能自行开机。dcc策略为unless-stopped，其余相关容器为no；重启前后仍需复查实际状态。

若冷重启后同一端口再次降宽/报UE，建议交维护方检查卡6—卡7互联路径并提交本次复发证据；在确认硬件/驱动方案前，不盲目降级驱动或修改ACS。

## 证据定位

- `evidence/preflight.json`：只读盘点、原容器、型号与版本。
- `evidence/warm_reset_result.json`：命令、时间、返回码、90秒后状态及驱动初始化事件；仅实验目录保存，不整份导入知识库。
- `evidence/recovery_summary.json`：热复位后的初次恢复状态，非最终成功结论。
- `evidence/recurrence_kernel.json`：人工限定为新MetaXLink/AER/状态事件的5行摘录。
- `pilot/evidence/communication_process.json`与`communication.log`：命令、退出124及各rank超时。
- `evidence/after_recurrence.json`、`preserved_after.json`、`reboot_preparation.json`：最终状态、环境保持和重启前置盘点。

根因未闭环，恢复未完成；后续新尝试使用新的结果目录，不覆盖上述证据。
