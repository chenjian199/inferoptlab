# 卡6恢复预检查与执行边界

日期：2026-11-23。本文件为执行前方案；当时仅完成只读检查。用户随后明确授权一次热复位，实际执行及故障复发见[结果报告](REPORT.md)。不以本方案的执行前状态替代实际结果。

## 当前证据

服务器实际型号H3C R5330 G7，裸机；驱动3.10.14，mx-smi2.3.4。GPU4～7 VBIOS均1.24.3.0，构成一个MetaXLink互联组。所有容器停止、GPU进程为空、metax驱动引用数0。

GPU6的不可用原因由当前mx-smi明确报告为MetaXLink port4 AER UE，建议warm reset或reboot。GPU6与GPU7的port4都down、宽度x4；GPU6该口CE=5、UE=1。两卡主PCIe链路仍32 GT/s x16、ECC计数0。故障定位到该互联路径，但硬件、固件、驱动等具体根因仍未确定。

## 可审阅的恢复动作

若允许尝试热复位，先持有`/home/metax/.glm53-c500-tp8.lock`并重新检查驱动引用数与GPU进程；以root执行一次：

```sh
mx-smi -r -i 0000:5b:00.0 -y
```

指定GPU6，驱动会处理互联组（预期GPU4～7）。不是单卡隔离复位。命令选项已由本机`mx-smi --help`确认；凭据仅交互提供，不写脚本/记录。等待至少90秒期间不向GPU发其他操作，之后检查可用状态、MetaXLink端口、AER新错误、boot_id与驱动版本，再做每卡小计算和8卡通信测试。

热复位设计上不重启主机、不安装或卸载驱动。但查到的厂商适配表仅列H3C R5300 G6，未能确认R5330 G7已验证；厂商还说明未经验证的机型可能丢卡或因AER直接重启。因此不能承诺本机热复位不会触发主机重启。鉴于用户要求重启前先告知，执行前需要明确这一风险及是否允许尝试。

若命令失败、链路未恢复或出现新错误，停止继续复位/推理，先报告；不自动reboot、冷启动、卸载/重载驱动、改ACS、升级VBIOS。恢复不是根因闭环。

## 恢复后的验证

保留`glmf/gemm_replace_20261123`及旧基线归档，复制冻结源码与协议到新的实验根目录、独立容器/缓存/结果目录。先每卡基础计算、默认通信路径最小all-reduce，通过后运行原32题→候选32题→恢复4题。评估目标层8卡实际命中、局部容差、零意外fallback、隔离评分、逐题退化、token差异与恢复一致性；新驱动必须使用同期原实现对照。尚未恢复前不启动模型。

## 外部依据与覆盖

2026-11-23查询厂商网页（搜索返回正文；直接打开部分页面被验证页阻挡，未取得完整新版适配矩阵）。引用为外部资料，不等于本机兼容认证：

- [Warm Reset指南2.32.0.x](https://developer.metax-tech.com/api/client/document/preview/331/C500_WarmResetGuide_CN.html)，§2/3/4.2/7：版本前置、已验证机型、空闲条件/90秒等待、未经验证机型风险。
- [Warm Reset指南3.5.3.x物理机场景](https://developer.metax-tech.com/api/client/document/preview/1000/split_files/物理机场景.html)，§4.1/4.2：互联组自动复位、root权限、恢复后检查与失败处理。
- [mx-smi手册3.8.3.x](https://developer.metax-tech.com/api/client/document/preview/GPU%20运维/mx-smi使用手册/曦云C500系列/3.8.3.x/split_files/命令介绍.html)：热复位失败后的重启建议；不反复复位同一互联组。

本机命令和原始结果保存`evidence/preflight.json`；不包含密钥、订阅地址或完整环境转储。
