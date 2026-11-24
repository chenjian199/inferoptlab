# 沐曦通用GPU_mcTracer使用手册

文档 ID：`mctracer-v08`；文档修订：V08；发布日期：2026-03-27。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf)

SHA256：`63b792c27a24a5f89d2e599bd5f84791f0c31b815e30d341e4c4cfcc1c21a492`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 6 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=6)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 7 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=7) · [逐页文本](../../generated/text/mctracer-v08/page-0007.txt)
- [PDF 第 9 页（标签 4）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=9) · [逐页文本](../../generated/text/mctracer-v08/page-0009.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=6) | 1 | [文本](../../generated/text/mctracer-v08/page-0006.txt) |
| 2 | 适用产品 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=6) | 1 | [文本](../../generated/text/mctracer-v08/page-0006.txt) |
| 1 | mcTracer | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=7) | 2 | [文本](../../generated/text/mctracer-v08/page-0007.txt) |
| 2 | 安装 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=7) | 2 | [文本](../../generated/text/mctracer-v08/page-0007.txt) |
| 2 | 使用 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=7) | 2 | [文本](../../generated/text/mctracer-v08/page-0007.txt) |
| 2 | 卸载 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=8) | 3 | [文本](../../generated/text/mctracer-v08/page-0008.txt) |
| 1 | mcTracer-Viewer | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=9) | 4 | [文本](../../generated/text/mctracer-v08/page-0009.txt) |
| 2 | 安装 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=9) | 4 | [文本](../../generated/text/mctracer-v08/page-0009.txt) |
| 2 | 使用 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=9) | 4 | [文本](../../generated/text/mctracer-v08/page-0009.txt) |
| 2 | 卸载 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTracer%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V08.pdf#page=9) | 4 | [文本](../../generated/text/mctracer-v08/page-0009.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mctracer-v08/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mctracer-v08/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mctracer-v08/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mctracer-v08/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/mctracer-v08/page-0005.txt)
- [PDF 6 / 标签 1](../../generated/text/mctracer-v08/page-0006.txt)
- [PDF 7 / 标签 2](../../generated/text/mctracer-v08/page-0007.txt)
- [PDF 8 / 标签 3](../../generated/text/mctracer-v08/page-0008.txt)
- [PDF 9 / 标签 4](../../generated/text/mctracer-v08/page-0009.txt)
