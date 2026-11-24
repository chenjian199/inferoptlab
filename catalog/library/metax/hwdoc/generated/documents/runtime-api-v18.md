# 沐曦通用GPU_运行时API编程指南

文档 ID：`runtime-api-v18`；文档修订：V18；发布日期：2026-10-30。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf)

SHA256：`fff0305698ce390261781c45706df7ee1c34bf07f3409acb975e75c689a2a5f0`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 10 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=10)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

未自动定位到候选页，请检索全文。

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=10) | 1 | [文本](../../generated/text/runtime-api-v18/page-0010.txt) |
| 2 | 适用产品 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=10) | 1 | [文本](../../generated/text/runtime-api-v18/page-0010.txt) |
| 1 | 编程模型 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=11) | 2 | [文本](../../generated/text/runtime-api-v18/page-0011.txt) |
| 2 | 程序结构 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=11) | 2 | [文本](../../generated/text/runtime-api-v18/page-0011.txt) |
| 2 | 执行模型 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=12) | 3 | [文本](../../generated/text/runtime-api-v18/page-0012.txt) |
| 2 | 内存层次模型 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=13) | 4 | [文本](../../generated/text/runtime-api-v18/page-0013.txt) |
| 2 | 核函数 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=14) | 5 | [文本](../../generated/text/runtime-api-v18/page-0014.txt) |
| 2 | 动态并行 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=15) | 6 | [文本](../../generated/text/runtime-api-v18/page-0015.txt) |
| 2 | 图编程 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=15) | 6 | [文本](../../generated/text/runtime-api-v18/page-0015.txt) |
| 2 | MPS多进程服务 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=16) | 7 | [文本](../../generated/text/runtime-api-v18/page-0016.txt) |
| 1 | 编程接口 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=17) | 8 | [文本](../../generated/text/runtime-api-v18/page-0017.txt) |
| 2 | 设备管理 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=17) | 8 | [文本](../../generated/text/runtime-api-v18/page-0017.txt) |
| 3 | 查询设备信息 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=17) | 8 | [文本](../../generated/text/runtime-api-v18/page-0017.txt) |
| 4 | 查询设备计算能力 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=19) | 10 | [文本](../../generated/text/runtime-api-v18/page-0019.txt) |
| 3 | 选择运行设备 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=19) | 10 | [文本](../../generated/text/runtime-api-v18/page-0019.txt) |
| 3 | 初始化设备 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=20) | 11 | [文本](../../generated/text/runtime-api-v18/page-0020.txt) |
| 2 | 内存管理 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=20) | 11 | [文本](../../generated/text/runtime-api-v18/page-0020.txt) |
| 3 | 内存申请与释放 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=20) | 11 | [文本](../../generated/text/runtime-api-v18/page-0020.txt) |
| 3 | 内存拷贝 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=20) | 11 | [文本](../../generated/text/runtime-api-v18/page-0020.txt) |
| 2 | 流和事件 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=21) | 12 | [文本](../../generated/text/runtime-api-v18/page-0021.txt) |
| 3 | 流 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=21) | 12 | [文本](../../generated/text/runtime-api-v18/page-0021.txt) |
| 4 | 代码示例 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=22) | 13 | [文本](../../generated/text/runtime-api-v18/page-0022.txt) |
| 4 | 流管理函数 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=22) | 13 | [文本](../../generated/text/runtime-api-v18/page-0022.txt) |
| 3 | 事件 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=23) | 14 | [文本](../../generated/text/runtime-api-v18/page-0023.txt) |
| 4 | 代码示例 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=23) | 14 | [文本](../../generated/text/runtime-api-v18/page-0023.txt) |
| 4 | 事件管理函数 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=23) | 14 | [文本](../../generated/text/runtime-api-v18/page-0023.txt) |
| 3 | 操作并发 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=24) | 15 | [文本](../../generated/text/runtime-api-v18/page-0024.txt) |
| 4 | 使用异步流进行并发 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=24) | 15 | [文本](../../generated/text/runtime-api-v18/page-0024.txt) |
| 4 | 设置流之间依赖 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=24) | 15 | [文本](../../generated/text/runtime-api-v18/page-0024.txt) |
| 3 | 流回调 | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=25) | 16 | [文本](../../generated/text/runtime-api-v18/page-0025.txt) |
| 2 | 同步 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=26) | 17 | [文本](../../generated/text/runtime-api-v18/page-0026.txt) |
| 3 | 系统级同步 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=26) | 17 | [文本](../../generated/text/runtime-api-v18/page-0026.txt) |
| 3 | 线程块级/线程束级同步 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=26) | 17 | [文本](../../generated/text/runtime-api-v18/page-0026.txt) |
| 3 | 用户细粒度并行同步 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=26) | 17 | [文本](../../generated/text/runtime-api-v18/page-0026.txt) |
| 4 | 协作组API | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=28) | 19 | [文本](../../generated/text/runtime-api-v18/page-0028.txt) |
| 4 | 线程组集体操作 | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=28) | 19 | [文本](../../generated/text/runtime-api-v18/page-0028.txt) |
| 4 | 协作组示例 | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=29) | 20 | [文本](../../generated/text/runtime-api-v18/page-0029.txt) |
| 2 | 流序内存分配 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=31) | 22 | [文本](../../generated/text/runtime-api-v18/page-0031.txt) |
| 3 | 基本接口 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=31) | 22 | [文本](../../generated/text/runtime-api-v18/page-0031.txt) |
| 3 | 内存池和内存池数据结构 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=32) | 23 | [文本](../../generated/text/runtime-api-v18/page-0032.txt) |
| 3 | 默认内存池 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=32) | 23 | [文本](../../generated/text/runtime-api-v18/page-0032.txt) |
| 3 | 显式内存池 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=32) | 23 | [文本](../../generated/text/runtime-api-v18/page-0032.txt) |
| 3 | 物理页面缓存行为 | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=33) | 24 | [文本](../../generated/text/runtime-api-v18/page-0033.txt) |
| 3 | 多GPU的设备可访问性支持 | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=34) | 25 | [文本](../../generated/text/runtime-api-v18/page-0034.txt) |
| 3 | IPC内存池 | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=35) | 26 | [文本](../../generated/text/runtime-api-v18/page-0035.txt) |
| 4 | 创建和共享IPC内存池 | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=35) | 26 | [文本](../../generated/text/runtime-api-v18/page-0035.txt) |
| 4 | 在导入进程中设置访问权限 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=36) | 27 | [文本](../../generated/text/runtime-api-v18/page-0036.txt) |
| 4 | 从导出的IPC内存池创建和共享分配 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=36) | 27 | [文本](../../generated/text/runtime-api-v18/page-0036.txt) |
| 4 | IPC导出内存池限制 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=38) | 29 | [文本](../../generated/text/runtime-api-v18/page-0038.txt) |
| 4 | IPC导入内存池限制 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=38) | 29 | [文本](../../generated/text/runtime-api-v18/page-0038.txt) |
| 2 | 多设备系统编程 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=38) | 29 | [文本](../../generated/text/runtime-api-v18/page-0038.txt) |
| 3 | 多设备管理 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=38) | 29 | [文本](../../generated/text/runtime-api-v18/page-0038.txt) |
| 3 | 点对点通信 | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=39) | 30 | [文本](../../generated/text/runtime-api-v18/page-0039.txt) |
| 4 | 点对点访问 | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=39) | 30 | [文本](../../generated/text/runtime-api-v18/page-0039.txt) |
| 4 | 点对点内存复制 | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=40) | 31 | [文本](../../generated/text/runtime-api-v18/page-0040.txt) |
| 3 | 多GPU设备间的同步 | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=40) | 31 | [文本](../../generated/text/runtime-api-v18/page-0040.txt) |
| 2 | 动态并行 | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=40) | 31 | [文本](../../generated/text/runtime-api-v18/page-0040.txt) |
| 3 | 核函数 | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=41) | 32 | [文本](../../generated/text/runtime-api-v18/page-0041.txt) |
| 4 | 异步启动 | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=41) | 32 | [文本](../../generated/text/runtime-api-v18/page-0041.txt) |
| 4 | 启动环境配置 | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=41) | 32 | [文本](../../generated/text/runtime-api-v18/page-0041.txt) |
| 4 | 用设备端运行时API启动 | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=41) | 32 | [文本](../../generated/text/runtime-api-v18/page-0041.txt) |
| 3 | 内存管理 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=42) | 33 | [文本](../../generated/text/runtime-api-v18/page-0042.txt) |
| 4 | 内存声明和使用 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=42) | 33 | [文本](../../generated/text/runtime-api-v18/page-0042.txt) |
| 4 | 全局内存 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=42) | 33 | [文本](../../generated/text/runtime-api-v18/page-0042.txt) |
| 4 | 零拷贝内存 | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=43) | 34 | [文本](../../generated/text/runtime-api-v18/page-0043.txt) |
| 4 | 常量内存 | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=43) | 34 | [文本](../../generated/text/runtime-api-v18/page-0043.txt) |
| 4 | 共享内存和私有内存 | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=44) | 35 | [文本](../../generated/text/runtime-api-v18/page-0044.txt) |
| 4 | 私有内存 | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=44) | 35 | [文本](../../generated/text/runtime-api-v18/page-0044.txt) |
| 3 | 设备管理 | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=44) | 35 | [文本](../../generated/text/runtime-api-v18/page-0044.txt) |
| 3 | 流和事件 | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=45) | 36 | [文本](../../generated/text/runtime-api-v18/page-0045.txt) |
| 4 | 排序和并发 | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=45) | 36 | [文本](../../generated/text/runtime-api-v18/page-0045.txt) |
| 4 | 同步 | [46](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=46) | 37 | [文本](../../generated/text/runtime-api-v18/page-0046.txt) |
| 3 | API附加说明 | [46](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=46) | 37 | [文本](../../generated/text/runtime-api-v18/page-0046.txt) |
| 3 | 代码示例 | [47](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=47) | 38 | [文本](../../generated/text/runtime-api-v18/page-0047.txt) |
| 3 | 性能分析 | [47](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=47) | 38 | [文本](../../generated/text/runtime-api-v18/page-0047.txt) |
| 3 | 限制和注意事项 | [48](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=48) | 39 | [文本](../../generated/text/runtime-api-v18/page-0048.txt) |
| 4 | 内存限制 | [48](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=48) | 39 | [文本](../../generated/text/runtime-api-v18/page-0048.txt) |
| 4 | API错误和启动失败 | [49](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=49) | 40 | [文本](../../generated/text/runtime-api-v18/page-0049.txt) |
| 2 | 图编程接口 | [49](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=49) | 40 | [文本](../../generated/text/runtime-api-v18/page-0049.txt) |
| 3 | 显式图编程接口 | [49](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=49) | 40 | [文本](../../generated/text/runtime-api-v18/page-0049.txt) |
| 3 | 流捕获图编程接口 | [50](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=50) | 41 | [文本](../../generated/text/runtime-api-v18/page-0050.txt) |
| 3 | 实例化图更新 | [50](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=50) | 41 | [文本](../../generated/text/runtime-api-v18/page-0050.txt) |
| 4 | 整图更新 | [51](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=51) | 42 | [文本](../../generated/text/runtime-api-v18/page-0051.txt) |
| 4 | 单个节点更新 | [52](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=52) | 43 | [文本](../../generated/text/runtime-api-v18/page-0052.txt) |
| 4 | 启用或禁用节点（Individual Node Enable） | [52](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=52) | 43 | [文本](../../generated/text/runtime-api-v18/page-0052.txt) |
| 4 | 实例化图更新的限制 | [53](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=53) | 44 | [文本](../../generated/text/runtime-api-v18/page-0053.txt) |
| 3 | 图编程的注意事项 | [53](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=53) | 44 | [文本](../../generated/text/runtime-api-v18/page-0053.txt) |
| 4 | 图编程的调试接口 | [54](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=54) | 45 | [文本](../../generated/text/runtime-api-v18/page-0054.txt) |
| 2 | MPS多进程服务 | [56](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=56) | 47 | [文本](../../generated/text/runtime-api-v18/page-0056.txt) |
| 3 | MPS多进程服务控制 | [56](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=56) | 47 | [文本](../../generated/text/runtime-api-v18/page-0056.txt) |
| 4 | MPS多进程服务行为说明 | [56](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=56) | 47 | [文本](../../generated/text/runtime-api-v18/page-0056.txt) |
| 4 | MPS多进程服务使用限制 | [57](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=57) | 48 | [文本](../../generated/text/runtime-api-v18/page-0057.txt) |
| 1 | 编译和调试 | [58](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=58) | 49 | [文本](../../generated/text/runtime-api-v18/page-0058.txt) |
| 2 | 离线编译和静态运行 | [58](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=58) | 49 | [文本](../../generated/text/runtime-api-v18/page-0058.txt) |
| 3 | Makefile编译和示例 | [58](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=58) | 49 | [文本](../../generated/text/runtime-api-v18/page-0058.txt) |
| 4 | CMake编译和示例 | [61](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=61) | 52 | [文本](../../generated/text/runtime-api-v18/page-0061.txt) |
| 2 | 运行时编译和动态加载 | [62](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=62) | 53 | [文本](../../generated/text/runtime-api-v18/page-0062.txt) |
| 2 | 代码托管（Binary Cache） | [65](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=65) | 56 | [文本](../../generated/text/runtime-api-v18/page-0065.txt) |
| 3 | 更改Binary Cache 文件支持Size | [67](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=67) | 58 | [文本](../../generated/text/runtime-api-v18/page-0067.txt) |
| 3 | 自定义Cache文件路径 | [67](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=67) | 58 | [文本](../../generated/text/runtime-api-v18/page-0067.txt) |
| 3 | 关闭Binary Cache功能 | [67](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=67) | 58 | [文本](../../generated/text/runtime-api-v18/page-0067.txt) |
| 2 | 环境变量 | [68](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=68) | 59 | [文本](../../generated/text/runtime-api-v18/page-0068.txt) |
| 2 | 主机代码调试信息 | [74](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=74) | 65 | [文本](../../generated/text/runtime-api-v18/page-0074.txt) |
| 2 | 设备代码调试信息 | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=75) | 66 | [文本](../../generated/text/runtime-api-v18/page-0075.txt) |
| 3 | 使用GPU printf | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=75) | 66 | [文本](../../generated/text/runtime-api-v18/page-0075.txt) |
| 3 | 使用GPU Trap Handler | [76](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=76) | 67 | [文本](../../generated/text/runtime-api-v18/page-0076.txt) |
| 1 | 附录 | [79](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=79) | 70 | [文本](../../generated/text/runtime-api-v18/page-0079.txt) |
| 2 | 术语/缩略语 | [79](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_%E8%BF%90%E8%A1%8C%E6%97%B6API%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V18.pdf#page=79) | 70 | [文本](../../generated/text/runtime-api-v18/page-0079.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/runtime-api-v18/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/runtime-api-v18/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/runtime-api-v18/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/runtime-api-v18/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/runtime-api-v18/page-0005.txt)
- [PDF 6 / 标签 iv](../../generated/text/runtime-api-v18/page-0006.txt)
- [PDF 7 / 标签 v](../../generated/text/runtime-api-v18/page-0007.txt)
- [PDF 8 / 标签 vi](../../generated/text/runtime-api-v18/page-0008.txt)
- [PDF 9 / 标签 vii](../../generated/text/runtime-api-v18/page-0009.txt)
- [PDF 10 / 标签 1](../../generated/text/runtime-api-v18/page-0010.txt)
- [PDF 11 / 标签 2](../../generated/text/runtime-api-v18/page-0011.txt)
- [PDF 12 / 标签 3](../../generated/text/runtime-api-v18/page-0012.txt)
- [PDF 13 / 标签 4](../../generated/text/runtime-api-v18/page-0013.txt)
- [PDF 14 / 标签 5](../../generated/text/runtime-api-v18/page-0014.txt)
- [PDF 15 / 标签 6](../../generated/text/runtime-api-v18/page-0015.txt)
- [PDF 16 / 标签 7](../../generated/text/runtime-api-v18/page-0016.txt)
- [PDF 17 / 标签 8](../../generated/text/runtime-api-v18/page-0017.txt)
- [PDF 18 / 标签 9](../../generated/text/runtime-api-v18/page-0018.txt)
- [PDF 19 / 标签 10](../../generated/text/runtime-api-v18/page-0019.txt)
- [PDF 20 / 标签 11](../../generated/text/runtime-api-v18/page-0020.txt)
- [PDF 21 / 标签 12](../../generated/text/runtime-api-v18/page-0021.txt)
- [PDF 22 / 标签 13](../../generated/text/runtime-api-v18/page-0022.txt)
- [PDF 23 / 标签 14](../../generated/text/runtime-api-v18/page-0023.txt)
- [PDF 24 / 标签 15](../../generated/text/runtime-api-v18/page-0024.txt)
- [PDF 25 / 标签 16](../../generated/text/runtime-api-v18/page-0025.txt)
- [PDF 26 / 标签 17](../../generated/text/runtime-api-v18/page-0026.txt)
- [PDF 27 / 标签 18](../../generated/text/runtime-api-v18/page-0027.txt)
- [PDF 28 / 标签 19](../../generated/text/runtime-api-v18/page-0028.txt)
- [PDF 29 / 标签 20](../../generated/text/runtime-api-v18/page-0029.txt)
- [PDF 30 / 标签 21](../../generated/text/runtime-api-v18/page-0030.txt)
- [PDF 31 / 标签 22](../../generated/text/runtime-api-v18/page-0031.txt)
- [PDF 32 / 标签 23](../../generated/text/runtime-api-v18/page-0032.txt)
- [PDF 33 / 标签 24](../../generated/text/runtime-api-v18/page-0033.txt)
- [PDF 34 / 标签 25](../../generated/text/runtime-api-v18/page-0034.txt)
- [PDF 35 / 标签 26](../../generated/text/runtime-api-v18/page-0035.txt)
- [PDF 36 / 标签 27](../../generated/text/runtime-api-v18/page-0036.txt)
- [PDF 37 / 标签 28](../../generated/text/runtime-api-v18/page-0037.txt)
- [PDF 38 / 标签 29](../../generated/text/runtime-api-v18/page-0038.txt)
- [PDF 39 / 标签 30](../../generated/text/runtime-api-v18/page-0039.txt)
- [PDF 40 / 标签 31](../../generated/text/runtime-api-v18/page-0040.txt)
- [PDF 41 / 标签 32](../../generated/text/runtime-api-v18/page-0041.txt)
- [PDF 42 / 标签 33](../../generated/text/runtime-api-v18/page-0042.txt)
- [PDF 43 / 标签 34](../../generated/text/runtime-api-v18/page-0043.txt)
- [PDF 44 / 标签 35](../../generated/text/runtime-api-v18/page-0044.txt)
- [PDF 45 / 标签 36](../../generated/text/runtime-api-v18/page-0045.txt)
- [PDF 46 / 标签 37](../../generated/text/runtime-api-v18/page-0046.txt)
- [PDF 47 / 标签 38](../../generated/text/runtime-api-v18/page-0047.txt)
- [PDF 48 / 标签 39](../../generated/text/runtime-api-v18/page-0048.txt)
- [PDF 49 / 标签 40](../../generated/text/runtime-api-v18/page-0049.txt)
- [PDF 50 / 标签 41](../../generated/text/runtime-api-v18/page-0050.txt)
- [PDF 51 / 标签 42](../../generated/text/runtime-api-v18/page-0051.txt)
- [PDF 52 / 标签 43](../../generated/text/runtime-api-v18/page-0052.txt)
- [PDF 53 / 标签 44](../../generated/text/runtime-api-v18/page-0053.txt)
- [PDF 54 / 标签 45](../../generated/text/runtime-api-v18/page-0054.txt)
- [PDF 55 / 标签 46](../../generated/text/runtime-api-v18/page-0055.txt)
- [PDF 56 / 标签 47](../../generated/text/runtime-api-v18/page-0056.txt)
- [PDF 57 / 标签 48](../../generated/text/runtime-api-v18/page-0057.txt)
- [PDF 58 / 标签 49](../../generated/text/runtime-api-v18/page-0058.txt)
- [PDF 59 / 标签 50](../../generated/text/runtime-api-v18/page-0059.txt)
- [PDF 60 / 标签 51](../../generated/text/runtime-api-v18/page-0060.txt)
- [PDF 61 / 标签 52](../../generated/text/runtime-api-v18/page-0061.txt)
- [PDF 62 / 标签 53](../../generated/text/runtime-api-v18/page-0062.txt)
- [PDF 63 / 标签 54](../../generated/text/runtime-api-v18/page-0063.txt)
- [PDF 64 / 标签 55](../../generated/text/runtime-api-v18/page-0064.txt)
- [PDF 65 / 标签 56](../../generated/text/runtime-api-v18/page-0065.txt)
- [PDF 66 / 标签 57](../../generated/text/runtime-api-v18/page-0066.txt)
- [PDF 67 / 标签 58](../../generated/text/runtime-api-v18/page-0067.txt)
- [PDF 68 / 标签 59](../../generated/text/runtime-api-v18/page-0068.txt)
- [PDF 69 / 标签 60](../../generated/text/runtime-api-v18/page-0069.txt)
- [PDF 70 / 标签 61](../../generated/text/runtime-api-v18/page-0070.txt)
- [PDF 71 / 标签 62](../../generated/text/runtime-api-v18/page-0071.txt)
- [PDF 72 / 标签 63](../../generated/text/runtime-api-v18/page-0072.txt)
- [PDF 73 / 标签 64](../../generated/text/runtime-api-v18/page-0073.txt)
- [PDF 74 / 标签 65](../../generated/text/runtime-api-v18/page-0074.txt)
- [PDF 75 / 标签 66](../../generated/text/runtime-api-v18/page-0075.txt)
- [PDF 76 / 标签 67](../../generated/text/runtime-api-v18/page-0076.txt)
- [PDF 77 / 标签 68](../../generated/text/runtime-api-v18/page-0077.txt)
- [PDF 78 / 标签 69](../../generated/text/runtime-api-v18/page-0078.txt)
- [PDF 79 / 标签 70](../../generated/text/runtime-api-v18/page-0079.txt)
