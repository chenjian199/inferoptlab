# 沐曦通用GPU_mcTriton用户指南

文档 ID：`mctriton-v08`；文档修订：V08；发布日期：2026-09-22。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf)

SHA256：`5486a806ac8e48e40514347bac7403c40aee53d59515a9bded39cc17a7daed59`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 5 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=5)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 5 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=5) · [逐页文本](../../generated/text/mctriton-v08/page-0005.txt)
- [PDF 第 6 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=6) · [逐页文本](../../generated/text/mctriton-v08/page-0006.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [5](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=5) | 1 | [文本](../../generated/text/mctriton-v08/page-0005.txt) |
| 2 | 适用产品 | [5](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=5) | 1 | [文本](../../generated/text/mctriton-v08/page-0005.txt) |
| 1 | 快速安装 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=6) | 2 | [文本](../../generated/text/mctriton-v08/page-0006.txt) |
| 2 | 基于pip安装 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=6) | 2 | [文本](../../generated/text/mctriton-v08/page-0006.txt) |
| 3 | 环境准备 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=6) | 2 | [文本](../../generated/text/mctriton-v08/page-0006.txt) |
| 3 | 开始安装 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=6) | 2 | [文本](../../generated/text/mctriton-v08/page-0006.txt) |
| 3 | 验证安装 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=6) | 2 | [文本](../../generated/text/mctriton-v08/page-0006.txt) |
| 3 | 如何卸载 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=7) | 3 | [文本](../../generated/text/mctriton-v08/page-0007.txt) |
| 1 | 功能支持 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8) | 4 | [文本](../../generated/text/mctriton-v08/page-0008.txt) |
| 2 | 基本功能 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8) | 4 | [文本](../../generated/text/mctriton-v08/page-0008.txt) |
| 3 | tl.dot的数据类型支持 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8) | 4 | [文本](../../generated/text/mctriton-v08/page-0008.txt) |
| 2 | 扩展功能 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=8) | 4 | [文本](../../generated/text/mctriton-v08/page-0008.txt) |
| 3 | triton.Config | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=9) | 5 | [文本](../../generated/text/mctriton-v08/page-0009.txt) |
| 4 | pipeline | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=9) | 5 | [文本](../../generated/text/mctriton-v08/page-0009.txt) |
| 4 | scenario | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=9) | 5 | [文本](../../generated/text/mctriton-v08/page-0009.txt) |
| 3 | MCTRITON_LOG_LEVEL | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=11) | 7 | [文本](../../generated/text/mctriton-v08/page-0011.txt) |
| 1 | 开源资源 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcTriton%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V08.pdf#page=12) | 8 | [文本](../../generated/text/mctriton-v08/page-0012.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mctriton-v08/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mctriton-v08/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mctriton-v08/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mctriton-v08/page-0004.txt)
- [PDF 5 / 标签 1](../../generated/text/mctriton-v08/page-0005.txt)
- [PDF 6 / 标签 2](../../generated/text/mctriton-v08/page-0006.txt)
- [PDF 7 / 标签 3](../../generated/text/mctriton-v08/page-0007.txt)
- [PDF 8 / 标签 4](../../generated/text/mctriton-v08/page-0008.txt)
- [PDF 9 / 标签 5](../../generated/text/mctriton-v08/page-0009.txt)
- [PDF 10 / 标签 6](../../generated/text/mctriton-v08/page-0010.txt)
- [PDF 11 / 标签 7](../../generated/text/mctriton-v08/page-0011.txt)
- [PDF 12 / 标签 8](../../generated/text/mctriton-v08/page-0012.txt)
