# 沐曦通用GPU_mxcc编译器用户指南

文档 ID：`mxcc-v06`；文档修订：V06；发布日期：2026-03-27。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf)

SHA256：`6fceba6f92b1b4274a5c2dd106d76320947a0b4ef0cdaffd36af5497fdffb6dd`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 6 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=6)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 9 页（标签 4）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=9) · [逐页文本](../../generated/text/mxcc-v06/page-0009.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=6) | 1 | [文本](../../generated/text/mxcc-v06/page-0006.txt) |
| 2 | 适用产品 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=6) | 1 | [文本](../../generated/text/mxcc-v06/page-0006.txt) |
| 1 | mxcc的使用 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=7) | 2 | [文本](../../generated/text/mxcc-v06/page-0007.txt) |
| 2 | 支持的输入文件类型 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=7) | 2 | [文本](../../generated/text/mxcc-v06/page-0007.txt) |
| 1 | 使用前准备 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=8) | 3 | [文本](../../generated/text/mxcc-v06/page-0008.txt) |
| 1 | 支持的选项 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=9) | 4 | [文本](../../generated/text/mxcc-v06/page-0009.txt) |
| 2 | File和Path说明 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=9) | 4 | [文本](../../generated/text/mxcc-v06/page-0009.txt) |
| 2 | 指定编译阶段的选项 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=11) | 6 | [文本](../../generated/text/mxcc-v06/page-0011.txt) |
| 2 | 指定编译器/链接器行为的选项 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=12) | 7 | [文本](../../generated/text/mxcc-v06/page-0012.txt) |
| 2 | 传递特定阶段选项的选项 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=14) | 9 | [文本](../../generated/text/mxcc-v06/page-0014.txt) |
| 2 | 指导编译器驱动程序的选项 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=14) | 9 | [文本](../../generated/text/mxcc-v06/page-0014.txt) |
| 2 | 调整GPU代码生成的选项 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=15) | 10 | [文本](../../generated/text/mxcc-v06/page-0015.txt) |
| 2 | 通用工具选项 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=16) | 11 | [文本](../../generated/text/mxcc-v06/page-0016.txt) |
| 2 | 设备链接器选项 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=16) | 11 | [文本](../../generated/text/mxcc-v06/page-0016.txt) |
| 1 | 示例 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=18) | 13 | [文本](../../generated/text/mxcc-v06/page-0018.txt) |
| 2 | 编译包含设备和主机函数的源文件 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=18) | 13 | [文本](../../generated/text/mxcc-v06/page-0018.txt) |
| 2 | 编译C/C++源文件 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=18) | 13 | [文本](../../generated/text/mxcc-v06/page-0018.txt) |
| 2 | 编译并单独链接 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=18) | 13 | [文本](../../generated/text/mxcc-v06/page-0018.txt) |
| 2 | 编译设备函数定义在其他文件中的源文件 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=18) | 13 | [文本](../../generated/text/mxcc-v06/page-0018.txt) |
| 2 | 编译设备函数定义在其他文件中的源文件并单独链接 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=19) | 14 | [文本](../../generated/text/mxcc-v06/page-0019.txt) |
| 2 | 编译设备和主机函数有自定义设备库的源文件 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=19) | 14 | [文本](../../generated/text/mxcc-v06/page-0019.txt) |
| 1 | 附录 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=20) | 15 | [文本](../../generated/text/mxcc-v06/page-0020.txt) |
| 2 | 术语/缩略语 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxcc%E7%BC%96%E8%AF%91%E5%99%A8%E7%94%A8%E6%88%B7%E6%8C%87%E5%8D%97_CN_V06.pdf#page=20) | 15 | [文本](../../generated/text/mxcc-v06/page-0020.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mxcc-v06/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mxcc-v06/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mxcc-v06/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mxcc-v06/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/mxcc-v06/page-0005.txt)
- [PDF 6 / 标签 1](../../generated/text/mxcc-v06/page-0006.txt)
- [PDF 7 / 标签 2](../../generated/text/mxcc-v06/page-0007.txt)
- [PDF 8 / 标签 3](../../generated/text/mxcc-v06/page-0008.txt)
- [PDF 9 / 标签 4](../../generated/text/mxcc-v06/page-0009.txt)
- [PDF 10 / 标签 5](../../generated/text/mxcc-v06/page-0010.txt)
- [PDF 11 / 标签 6](../../generated/text/mxcc-v06/page-0011.txt)
- [PDF 12 / 标签 7](../../generated/text/mxcc-v06/page-0012.txt)
- [PDF 13 / 标签 8](../../generated/text/mxcc-v06/page-0013.txt)
- [PDF 14 / 标签 9](../../generated/text/mxcc-v06/page-0014.txt)
- [PDF 15 / 标签 10](../../generated/text/mxcc-v06/page-0015.txt)
- [PDF 16 / 标签 11](../../generated/text/mxcc-v06/page-0016.txt)
- [PDF 17 / 标签 12](../../generated/text/mxcc-v06/page-0017.txt)
- [PDF 18 / 标签 13](../../generated/text/mxcc-v06/page-0018.txt)
- [PDF 19 / 标签 14](../../generated/text/mxcc-v06/page-0019.txt)
- [PDF 20 / 标签 15](../../generated/text/mxcc-v06/page-0020.txt)
