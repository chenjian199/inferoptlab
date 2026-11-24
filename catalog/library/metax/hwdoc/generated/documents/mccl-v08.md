# 沐曦通用GPU_MCCL编程指南

文档 ID：`mccl-v08`；文档修订：V08；发布日期：2026-06-26。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf)

SHA256：`7a95ac3ce4f68b0fb11baabb7fa08794cd5f5081c9ec3e888eefaaa03ab8c8b2`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 8 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦索® X206；以
> 及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

未自动定位到候选页，请检索全文。

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8) | 1 | [文本](../../generated/text/mccl-v08/page-0008.txt) |
| 2 | 适用产品 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8) | 1 | [文本](../../generated/text/mccl-v08/page-0008.txt) |
| 1 | 简介 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=9) | 2 | [文本](../../generated/text/mccl-v08/page-0009.txt) |
| 2 | 系统架构 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=9) | 2 | [文本](../../generated/text/mccl-v08/page-0009.txt) |
| 1 | 编程模型 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 4 | [文本](../../generated/text/mccl-v08/page-0011.txt) |
| 2 | 通讯器管理 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 4 | [文本](../../generated/text/mccl-v08/page-0011.txt) |
| 3 | mcclGetVersion | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 4 | [文本](../../generated/text/mccl-v08/page-0011.txt) |
| 3 | mcclGetUniqueId | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 4 | [文本](../../generated/text/mccl-v08/page-0011.txt) |
| 3 | mcclCommInitRank | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 4 | [文本](../../generated/text/mccl-v08/page-0011.txt) |
| 3 | mcclCommInitAll | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 4 | [文本](../../generated/text/mccl-v08/page-0011.txt) |
| 3 | mcclCommDestroy | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 5 | [文本](../../generated/text/mccl-v08/page-0012.txt) |
| 3 | mcclCommAbort | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 5 | [文本](../../generated/text/mccl-v08/page-0012.txt) |
| 3 | mcclGetErrorString | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 5 | [文本](../../generated/text/mccl-v08/page-0012.txt) |
| 3 | mcclCommGetAsyncError | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 5 | [文本](../../generated/text/mccl-v08/page-0012.txt) |
| 3 | mcclCommCount | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 5 | [文本](../../generated/text/mccl-v08/page-0012.txt) |
| 3 | mcclCommMcDevice | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 5 | [文本](../../generated/text/mccl-v08/page-0012.txt) |
| 3 | mcclCommUserRank | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=13) | 6 | [文本](../../generated/text/mccl-v08/page-0013.txt) |
| 3 | 示例 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=13) | 6 | [文本](../../generated/text/mccl-v08/page-0013.txt) |
| 4 | 单进程 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=13) | 6 | [文本](../../generated/text/mccl-v08/page-0013.txt) |
| 4 | 多进程 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=13) | 6 | [文本](../../generated/text/mccl-v08/page-0013.txt) |
| 2 | 集合通讯 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=14) | 7 | [文本](../../generated/text/mccl-v08/page-0014.txt) |
| 3 | mcclAllReduce | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=14) | 7 | [文本](../../generated/text/mccl-v08/page-0014.txt) |
| 3 | mcclBroadcast | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=14) | 7 | [文本](../../generated/text/mccl-v08/page-0014.txt) |
| 3 | mcclReduce | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=14) | 7 | [文本](../../generated/text/mccl-v08/page-0014.txt) |
| 3 | mcclAllGather | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=15) | 8 | [文本](../../generated/text/mccl-v08/page-0015.txt) |
| 3 | mcclReduceScatter | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=15) | 8 | [文本](../../generated/text/mccl-v08/page-0015.txt) |
| 3 | mcclAllToAll | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=15) | 8 | [文本](../../generated/text/mccl-v08/page-0015.txt) |
| 3 | mcclAllToAllv | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=15) | 8 | [文本](../../generated/text/mccl-v08/page-0015.txt) |
| 3 | mcclAllToAlld | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=16) | 9 | [文本](../../generated/text/mccl-v08/page-0016.txt) |
| 3 | 示例 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=16) | 9 | [文本](../../generated/text/mccl-v08/page-0016.txt) |
| 2 | 组调用 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=17) | 10 | [文本](../../generated/text/mccl-v08/page-0017.txt) |
| 3 | mcclGroupStart | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=18) | 11 | [文本](../../generated/text/mccl-v08/page-0018.txt) |
| 3 | mcclGroupEnd | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=18) | 11 | [文本](../../generated/text/mccl-v08/page-0018.txt) |
| 3 | 示例 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=18) | 11 | [文本](../../generated/text/mccl-v08/page-0018.txt) |
| 2 | 点对点通讯 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=18) | 11 | [文本](../../generated/text/mccl-v08/page-0018.txt) |
| 3 | mcclSend | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=18) | 11 | [文本](../../generated/text/mccl-v08/page-0018.txt) |
| 3 | mcclRecv | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=19) | 12 | [文本](../../generated/text/mccl-v08/page-0019.txt) |
| 3 | 示例 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=19) | 12 | [文本](../../generated/text/mccl-v08/page-0019.txt) |
| 2 | 数据类型 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=19) | 12 | [文本](../../generated/text/mccl-v08/page-0019.txt) |
| 2 | 返回值类型 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=20) | 13 | [文本](../../generated/text/mccl-v08/page-0020.txt) |
| 2 | 归约操作类型 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=20) | 13 | [文本](../../generated/text/mccl-v08/page-0020.txt) |
| 1 | 环境变量 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=21) | 14 | [文本](../../generated/text/mccl-v08/page-0021.txt) |
| 2 | 推荐环境变量 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=21) | 14 | [文本](../../generated/text/mccl-v08/page-0021.txt) |
| 3 | 多机环境 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=21) | 14 | [文本](../../generated/text/mccl-v08/page-0021.txt) |
| 3 | 极致性能 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=21) | 14 | [文本](../../generated/text/mccl-v08/page-0021.txt) |
| 3 | Arm服务器 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=22) | 15 | [文本](../../generated/text/mccl-v08/page-0022.txt) |
| 3 | 异构集群 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=22) | 15 | [文本](../../generated/text/mccl-v08/page-0022.txt) |
| 3 | 虚拟化场景 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=22) | 15 | [文本](../../generated/text/mccl-v08/page-0022.txt) |
| 3 | C500X机型 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 3 | 阡视服务器 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 3 | 大模型通信日志 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 2 | 环境变量说明 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 3 | 功能相关 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 4 | MCCL_DISABLE_OPTIC_LINK | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 4 | MCCL_FAST_WRITE_BACK | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=23) | 16 | [文本](../../generated/text/mccl-v08/page-0023.txt) |
| 4 | MCCL_EARLY_WRITE_BACK | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=24) | 17 | [文本](../../generated/text/mccl-v08/page-0024.txt) |
| 4 | MCCL_GROUP_WRITE_BACK | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=24) | 17 | [文本](../../generated/text/mccl-v08/page-0024.txt) |
| 4 | MCCL_DISABLE_MULTI_NODE_FABRIC | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=24) | 17 | [文本](../../generated/text/mccl-v08/page-0024.txt) |
| 4 | MCCL_BUFFSIZE | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=24) | 17 | [文本](../../generated/text/mccl-v08/page-0024.txt) |
| 4 | MCCL_DISABLE_CACHEABLE_BUFFER | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=25) | 18 | [文本](../../generated/text/mccl-v08/page-0025.txt) |
| 4 | MCCL_THRESHOLD_TO_USE_CACHEABLE_BUFFER | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=25) | 18 | [文本](../../generated/text/mccl-v08/page-0025.txt) |
| 4 | MCCL_THRESHOLD_TO_USE_CACHEABLE_BUFFER_P2P | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=25) | 18 | [文本](../../generated/text/mccl-v08/page-0025.txt) |
| 4 | MCCL_PCIE_BUFFER_MODE | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=25) | 18 | [文本](../../generated/text/mccl-v08/page-0025.txt) |
| 4 | MCCL_TUNING_MODEL | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=26) | 19 | [文本](../../generated/text/mccl-v08/page-0026.txt) |
| 4 | MCCL_PROTO | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=26) | 19 | [文本](../../generated/text/mccl-v08/page-0026.txt) |
| 4 | MCCL_ALGO | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=26) | 19 | [文本](../../generated/text/mccl-v08/page-0026.txt) |
| 4 | MCCL_DMABUF_ENABLE | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=26) | 19 | [文本](../../generated/text/mccl-v08/page-0026.txt) |
| 4 | MCCL_EXT_CCL_ENABLE | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=27) | 20 | [文本](../../generated/text/mccl-v08/page-0027.txt) |
| 4 | MCCL_HC_PLUGIN | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=27) | 20 | [文本](../../generated/text/mccl-v08/page-0027.txt) |
| 4 | MCCL_RINGS | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=27) | 20 | [文本](../../generated/text/mccl-v08/page-0027.txt) |
| 3 | 性能相关 | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=27) | 20 | [文本](../../generated/text/mccl-v08/page-0027.txt) |
| 4 | MCCL_ENABLE_FC | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=27) | 20 | [文本](../../generated/text/mccl-v08/page-0027.txt) |
| 4 | MCCL_ENABLE_FC8_OAM | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=28) | 21 | [文本](../../generated/text/mccl-v08/page-0028.txt) |
| 4 | MCCL_FC_BYTE_LIMIT | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=28) | 21 | [文本](../../generated/text/mccl-v08/page-0028.txt) |
| 4 | MCCL_FC_MAX_BLOCKS | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=28) | 21 | [文本](../../generated/text/mccl-v08/page-0028.txt) |
| 4 | MCCL_FC_DISABLE_REMOTE_READ | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=28) | 21 | [文本](../../generated/text/mccl-v08/page-0028.txt) |
| 4 | MCCL_FC_BYTE_LIMIT_DRAGONFLY | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=28) | 21 | [文本](../../generated/text/mccl-v08/page-0028.txt) |
| 4 | MCCL_FC_MTLK_BLOCKS | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=29) | 22 | [文本](../../generated/text/mccl-v08/page-0029.txt) |
| 4 | MCCL_LIMIT_RING_LL_THREADTHRESHOLDS | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=29) | 22 | [文本](../../generated/text/mccl-v08/page-0029.txt) |
| 4 | MCCL_CROSS_NIC | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=29) | 22 | [文本](../../generated/text/mccl-v08/page-0029.txt) |
| 4 | MCCL_MIN_NCHANNELS | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=29) | 22 | [文本](../../generated/text/mccl-v08/page-0029.txt) |
| 4 | MCCL_MAX_NCHANNELS | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=30) | 23 | [文本](../../generated/text/mccl-v08/page-0030.txt) |
| 4 | MCCL_RING_TP8_MODE | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=30) | 23 | [文本](../../generated/text/mccl-v08/page-0030.txt) |
| 4 | MCCL_NET_DISABLE_INTRA | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=31) | 24 | [文本](../../generated/text/mccl-v08/page-0031.txt) |
| 4 | MCCL_PXN_DISABLE | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=31) | 24 | [文本](../../generated/text/mccl-v08/page-0031.txt) |
| 4 | MCCL_MIN_P2P_NCHANNELS | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=31) | 24 | [文本](../../generated/text/mccl-v08/page-0031.txt) |
| 4 | MCCL_MAX_P2P_NCHANNELS | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=31) | 24 | [文本](../../generated/text/mccl-v08/page-0031.txt) |
| 4 | MCCL_P2P_NCHANNELS | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=31) | 24 | [文本](../../generated/text/mccl-v08/page-0031.txt) |
| 4 | MCCL_TUNING_FILE | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=32) | 25 | [文本](../../generated/text/mccl-v08/page-0032.txt) |
| 4 | MCCL_TOPO_FILE | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=32) | 25 | [文本](../../generated/text/mccl-v08/page-0032.txt) |
| 4 | MCCL_TOPO_DUMP_FILE | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=32) | 25 | [文本](../../generated/text/mccl-v08/page-0032.txt) |
| 4 | MCCL_P2P_DISABLE | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=32) | 25 | [文本](../../generated/text/mccl-v08/page-0032.txt) |
| 4 | MCCL_P2P_LEVEL | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=32) | 25 | [文本](../../generated/text/mccl-v08/page-0032.txt) |
| 4 | MCCL_DF16_RINGS | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=33) | 26 | [文本](../../generated/text/mccl-v08/page-0033.txt) |
| 4 | MCCL_IGNORE_CPU_AFFINITY | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=33) | 26 | [文本](../../generated/text/mccl-v08/page-0033.txt) |
| 4 | MCCL_RUNTIME_CONNECT | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=34) | 27 | [文本](../../generated/text/mccl-v08/page-0034.txt) |
| 4 | MCCL_HFC_EP4_KERNEL_LIMIT | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=34) | 27 | [文本](../../generated/text/mccl-v08/page-0034.txt) |
| 4 | MCCL_HFC_EP8_KERNEL_LIMIT | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=34) | 27 | [文本](../../generated/text/mccl-v08/page-0034.txt) |
| 3 | 网络相关 | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=34) | 27 | [文本](../../generated/text/mccl-v08/page-0034.txt) |
| 4 | MCCL_SHM_DISABLE | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=34) | 27 | [文本](../../generated/text/mccl-v08/page-0034.txt) |
| 4 | MCCL_IB_GID_INDEX | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=35) | 28 | [文本](../../generated/text/mccl-v08/page-0035.txt) |
| 4 | MCCL_IB_DISABLE | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=35) | 28 | [文本](../../generated/text/mccl-v08/page-0035.txt) |
| 4 | MCCL_SOCKET_FAMILY | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=35) | 28 | [文本](../../generated/text/mccl-v08/page-0035.txt) |
| 4 | MCCL_SOCKET_IFNAME | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=35) | 28 | [文本](../../generated/text/mccl-v08/page-0035.txt) |
| 4 | MCCL_IB_HCA | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=35) | 28 | [文本](../../generated/text/mccl-v08/page-0035.txt) |
| 4 | MCCL_NET_GDR_LEVEL | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=36) | 29 | [文本](../../generated/text/mccl-v08/page-0036.txt) |
| 3 | 调试相关 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=36) | 29 | [文本](../../generated/text/mccl-v08/page-0036.txt) |
| 4 | MCCL_DEBUG | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=36) | 29 | [文本](../../generated/text/mccl-v08/page-0036.txt) |
| 4 | MCCL_DEBUG_SUBSYS | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=37) | 30 | [文本](../../generated/text/mccl-v08/page-0037.txt) |
| 4 | MCCL_DEBUG_FILE | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=37) | 30 | [文本](../../generated/text/mccl-v08/page-0037.txt) |
| 3 | UMD相关 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=38) | 31 | [文本](../../generated/text/mccl-v08/page-0038.txt) |
| 4 | MACA_EXT_CPU_THREAD_POLICY | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=38) | 31 | [文本](../../generated/text/mccl-v08/page-0038.txt) |
| 4 | MACA_LAUNCH_BLOCKING | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=38) | 31 | [文本](../../generated/text/mccl-v08/page-0038.txt) |
| 4 | MACA_VISIBLE_DEVICES | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=38) | 31 | [文本](../../generated/text/mccl-v08/page-0038.txt) |
| 4 | MACA_DEVICE_ORDER | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=39) | 32 | [文本](../../generated/text/mccl-v08/page-0039.txt) |
| 4 | MXLOG_LEVEL | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=39) | 32 | [文本](../../generated/text/mccl-v08/page-0039.txt) |
| 4 | MACA_EXT_MPS_MODE | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=40) | 33 | [文本](../../generated/text/mccl-v08/page-0040.txt) |
| 4 | MACA_EXT_DIRECT_DISPATCH | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=40) | 33 | [文本](../../generated/text/mccl-v08/page-0040.txt) |
| 3 | 工具相关 | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=40) | 33 | [文本](../../generated/text/mccl-v08/page-0040.txt) |
| 4 | MX_TRACER_ENABLED_MCPTI | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=40) | 33 | [文本](../../generated/text/mccl-v08/page-0040.txt) |
| 4 | MCCL_OPTIMIZATION_A2A | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=41) | 34 | [文本](../../generated/text/mccl-v08/page-0041.txt) |
| 4 | P2P_MODE | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=41) | 34 | [文本](../../generated/text/mccl-v08/page-0041.txt) |
| 1 | 附录 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=42) | 35 | [文本](../../generated/text/mccl-v08/page-0042.txt) |
| 2 | 调试信息 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=42) | 35 | [文本](../../generated/text/mccl-v08/page-0042.txt) |
| 3 | 共享内存 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=42) | 35 | [文本](../../generated/text/mccl-v08/page-0042.txt) |
| 2 | 术语/缩略语 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MCCL%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V08.pdf#page=42) | 35 | [文本](../../generated/text/mccl-v08/page-0042.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mccl-v08/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mccl-v08/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mccl-v08/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mccl-v08/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/mccl-v08/page-0005.txt)
- [PDF 6 / 标签 iv](../../generated/text/mccl-v08/page-0006.txt)
- [PDF 7 / 标签 v](../../generated/text/mccl-v08/page-0007.txt)
- [PDF 8 / 标签 1](../../generated/text/mccl-v08/page-0008.txt)
- [PDF 9 / 标签 2](../../generated/text/mccl-v08/page-0009.txt)
- [PDF 10 / 标签 3](../../generated/text/mccl-v08/page-0010.txt)
- [PDF 11 / 标签 4](../../generated/text/mccl-v08/page-0011.txt)
- [PDF 12 / 标签 5](../../generated/text/mccl-v08/page-0012.txt)
- [PDF 13 / 标签 6](../../generated/text/mccl-v08/page-0013.txt)
- [PDF 14 / 标签 7](../../generated/text/mccl-v08/page-0014.txt)
- [PDF 15 / 标签 8](../../generated/text/mccl-v08/page-0015.txt)
- [PDF 16 / 标签 9](../../generated/text/mccl-v08/page-0016.txt)
- [PDF 17 / 标签 10](../../generated/text/mccl-v08/page-0017.txt)
- [PDF 18 / 标签 11](../../generated/text/mccl-v08/page-0018.txt)
- [PDF 19 / 标签 12](../../generated/text/mccl-v08/page-0019.txt)
- [PDF 20 / 标签 13](../../generated/text/mccl-v08/page-0020.txt)
- [PDF 21 / 标签 14](../../generated/text/mccl-v08/page-0021.txt)
- [PDF 22 / 标签 15](../../generated/text/mccl-v08/page-0022.txt)
- [PDF 23 / 标签 16](../../generated/text/mccl-v08/page-0023.txt)
- [PDF 24 / 标签 17](../../generated/text/mccl-v08/page-0024.txt)
- [PDF 25 / 标签 18](../../generated/text/mccl-v08/page-0025.txt)
- [PDF 26 / 标签 19](../../generated/text/mccl-v08/page-0026.txt)
- [PDF 27 / 标签 20](../../generated/text/mccl-v08/page-0027.txt)
- [PDF 28 / 标签 21](../../generated/text/mccl-v08/page-0028.txt)
- [PDF 29 / 标签 22](../../generated/text/mccl-v08/page-0029.txt)
- [PDF 30 / 标签 23](../../generated/text/mccl-v08/page-0030.txt)
- [PDF 31 / 标签 24](../../generated/text/mccl-v08/page-0031.txt)
- [PDF 32 / 标签 25](../../generated/text/mccl-v08/page-0032.txt)
- [PDF 33 / 标签 26](../../generated/text/mccl-v08/page-0033.txt)
- [PDF 34 / 标签 27](../../generated/text/mccl-v08/page-0034.txt)
- [PDF 35 / 标签 28](../../generated/text/mccl-v08/page-0035.txt)
- [PDF 36 / 标签 29](../../generated/text/mccl-v08/page-0036.txt)
- [PDF 37 / 标签 30](../../generated/text/mccl-v08/page-0037.txt)
- [PDF 38 / 标签 31](../../generated/text/mccl-v08/page-0038.txt)
- [PDF 39 / 标签 32](../../generated/text/mccl-v08/page-0039.txt)
- [PDF 40 / 标签 33](../../generated/text/mccl-v08/page-0040.txt)
- [PDF 41 / 标签 34](../../generated/text/mccl-v08/page-0041.txt)
- [PDF 42 / 标签 35](../../generated/text/mccl-v08/page-0042.txt)
