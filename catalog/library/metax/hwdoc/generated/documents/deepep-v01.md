# 沐曦通用GPU_DeepEP多机通信内存注册环境变量配置说明

文档 ID：`deepep-v01`；文档修订：V01；发布日期：2026-11-13。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf)

SHA256：`04ecd9ea7a268dc14c88f283869f64e17479a5da63dadef5cc4b93b07732fbf0`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 5 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=5)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 6 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=6) · [逐页文本](../../generated/text/deepep-v01/page-0006.txt)
- [PDF 第 7 页（标签 3）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=7) · [逐页文本](../../generated/text/deepep-v01/page-0007.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [5](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=5) | 1 | [文本](../../generated/text/deepep-v01/page-0005.txt) |
| 2 | 适用场景 | [5](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=5) | 1 | [文本](../../generated/text/deepep-v01/page-0005.txt) |
| 2 | 适用产品 | [5](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=5) | 1 | [文本](../../generated/text/deepep-v01/page-0005.txt) |
| 1 | 配置说明 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=6) | 2 | [文本](../../generated/text/deepep-v01/page-0006.txt) |
| 2 | 不同 MXMACA SDK Release版本的支持情况 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=6) | 2 | [文本](../../generated/text/deepep-v01/page-0006.txt) |
| 3 | MXMACA SDK Release版本 ＜ 3.8.3 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=6) | 2 | [文本](../../generated/text/deepep-v01/page-0006.txt) |
| 3 | 3.8.3 ≤ MXMACA SDK Release版本 ≤ 3.10.0 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=6) | 2 | [文本](../../generated/text/deepep-v01/page-0006.txt) |
| 3 | MXMACA SDK Release版本 ≥ 3.10.1 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=7) | 3 | [文本](../../generated/text/deepep-v01/page-0007.txt) |
| 2 | 客户使用建议 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_DeepEP%E5%A4%9A%E6%9C%BA%E9%80%9A%E4%BF%A1%E5%86%85%E5%AD%98%E6%B3%A8%E5%86%8C%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F%E9%85%8D%E7%BD%AE%E8%AF%B4%E6%98%8E_CN_V01.pdf#page=7) | 3 | [文本](../../generated/text/deepep-v01/page-0007.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/deepep-v01/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/deepep-v01/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/deepep-v01/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/deepep-v01/page-0004.txt)
- [PDF 5 / 标签 1](../../generated/text/deepep-v01/page-0005.txt)
- [PDF 6 / 标签 2](../../generated/text/deepep-v01/page-0006.txt)
- [PDF 7 / 标签 3](../../generated/text/deepep-v01/page-0007.txt)
