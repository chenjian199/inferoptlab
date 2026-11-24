# 沐曦通用GPU_mcProfiler使用手册

文档 ID：`mcprofiler-v06`；文档修订：V06；发布日期：2026-03-27。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf)

SHA256：`22c9fa76c4f27e328b151bad16f105b11d81df4fc501075baec5794c29b5c66e`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 6 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=6)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 6 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=6) · [逐页文本](../../generated/text/mcprofiler-v06/page-0006.txt)
- [PDF 第 7 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=7) · [逐页文本](../../generated/text/mcprofiler-v06/page-0007.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=6) | 1 | [文本](../../generated/text/mcprofiler-v06/page-0006.txt) |
| 2 | 适用产品 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=6) | 1 | [文本](../../generated/text/mcprofiler-v06/page-0006.txt) |
| 1 | mcProfiler | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=7) | 2 | [文本](../../generated/text/mcprofiler-v06/page-0007.txt) |
| 2 | 安装 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=7) | 2 | [文本](../../generated/text/mcprofiler-v06/page-0007.txt) |
| 2 | 使用 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=7) | 2 | [文本](../../generated/text/mcprofiler-v06/page-0007.txt) |
| 3 | 前置要求 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=7) | 2 | [文本](../../generated/text/mcprofiler-v06/page-0007.txt) |
| 3 | 创建度量任务 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=8) | 3 | [文本](../../generated/text/mcprofiler-v06/page-0008.txt) |
| 3 | 执行度量任务 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=9) | 4 | [文本](../../generated/text/mcprofiler-v06/page-0009.txt) |
| 3 | 分析度量结果 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=9) | 4 | [文本](../../generated/text/mcprofiler-v06/page-0009.txt) |
| 2 | 卸载 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcProfiler%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V06.pdf#page=10) | 5 | [文本](../../generated/text/mcprofiler-v06/page-0010.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mcprofiler-v06/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mcprofiler-v06/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mcprofiler-v06/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mcprofiler-v06/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/mcprofiler-v06/page-0005.txt)
- [PDF 6 / 标签 1](../../generated/text/mcprofiler-v06/page-0006.txt)
- [PDF 7 / 标签 2](../../generated/text/mcprofiler-v06/page-0007.txt)
- [PDF 8 / 标签 3](../../generated/text/mcprofiler-v06/page-0008.txt)
- [PDF 9 / 标签 4](../../generated/text/mcprofiler-v06/page-0009.txt)
- [PDF 10 / 标签 5](../../generated/text/mcprofiler-v06/page-0010.txt)
