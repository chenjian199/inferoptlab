# 沐曦通用GPU_mxvs测试工具套件使用手册

文档 ID：`mxvs-v26`；文档修订：V26；发布日期：2026-10-30。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf)

SHA256：`f14e664d429c6568ce5723a3a83c7a9164c2fcb33fd59137fb49c1128ab63ce2`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 11 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=11)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 12 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=12) · [逐页文本](../../generated/text/mxvs-v26/page-0012.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=11) | 1 | [文本](../../generated/text/mxvs-v26/page-0011.txt) |
| 2 | 适用产品 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=11) | 1 | [文本](../../generated/text/mxvs-v26/page-0011.txt) |
| 1 | 工具部署 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=12) | 2 | [文本](../../generated/text/mxvs-v26/page-0012.txt) |
| 1 | 日志存放 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=13) | 3 | [文本](../../generated/text/mxvs-v26/page-0013.txt) |
| 1 | 设备信息显示 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=14) | 4 | [文本](../../generated/text/mxvs-v26/page-0014.txt) |
| 1 | 显卡工作状态显示 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=15) | 5 | [文本](../../generated/text/mxvs-v26/page-0015.txt) |
| 1 | PCIe验收测试工具 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=16) | 6 | [文本](../../generated/text/mxvs-v26/page-0016.txt) |
| 2 | PCIe实时速率查询 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=16) | 6 | [文本](../../generated/text/mxvs-v26/page-0016.txt) |
| 2 | PCIe单向带宽测试 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=16) | 6 | [文本](../../generated/text/mxvs-v26/page-0016.txt) |
| 2 | PCIe双向带宽测试 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=18) | 8 | [文本](../../generated/text/mxvs-v26/page-0018.txt) |
| 2 | PCIe眼图特性测试 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=19) | 9 | [文本](../../generated/text/mxvs-v26/page-0019.txt) |
| 1 | Memory验收测试工具 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=20) | 10 | [文本](../../generated/text/mxvs-v26/page-0020.txt) |
| 2 | Memory实时带宽查询 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=20) | 10 | [文本](../../generated/text/mxvs-v26/page-0020.txt) |
| 2 | Memory带宽测试 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=21) | 11 | [文本](../../generated/text/mxvs-v26/page-0021.txt) |
| 1 | MetaXLink验收测试工具 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=22) | 12 | [文本](../../generated/text/mxvs-v26/page-0022.txt) |
| 2 | MetaXLink实时带宽查询 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=22) | 12 | [文本](../../generated/text/mxvs-v26/page-0022.txt) |
| 2 | MetaXLink带宽测试 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=23) | 13 | [文本](../../generated/text/mxvs-v26/page-0023.txt) |
| 2 | MetaXLink眼图特性测试 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=24) | 14 | [文本](../../generated/text/mxvs-v26/page-0024.txt) |
| 1 | P2P验收测试工具 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=26) | 16 | [文本](../../generated/text/mxvs-v26/page-0026.txt) |
| 2 | P2P带宽测试 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=26) | 16 | [文本](../../generated/text/mxvs-v26/page-0026.txt) |
| 1 | 算力测试工具 | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=28) | 18 | [文本](../../generated/text/mxvs-v26/page-0028.txt) |
| 2 | 算力测试 | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=28) | 18 | [文本](../../generated/text/mxvs-v26/page-0028.txt) |
| 2 | 软切分算力测试示例(C588不支持) | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=29) | 19 | [文本](../../generated/text/mxvs-v26/page-0029.txt) |
| 1 | 压力测试 | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=30) | 20 | [文本](../../generated/text/mxvs-v26/page-0030.txt) |
| 2 | XCORE压力测试 | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=30) | 20 | [文本](../../generated/text/mxvs-v26/page-0030.txt) |
| 2 | MetaXLink压力测试 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=32) | 22 | [文本](../../generated/text/mxvs-v26/page-0032.txt) |
| 2 | ETH压力测试 | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=33) | 23 | [文本](../../generated/text/mxvs-v26/page-0033.txt) |
| 1 | ETH验收测试工具 | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=34) | 24 | [文本](../../generated/text/mxvs-v26/page-0034.txt) |
| 2 | ETH眼图特性测试 | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=34) | 24 | [文本](../../generated/text/mxvs-v26/page-0034.txt) |
| 1 | 光模块验收测试工具（仅适用C500X） | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=35) | 25 | [文本](../../generated/text/mxvs-v26/page-0035.txt) |
| 2 | 单机MetaXLink带宽测试 | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=35) | 25 | [文本](../../generated/text/mxvs-v26/page-0035.txt) |
| 2 | 跨机MetaXLink带宽测试 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=36) | 26 | [文本](../../generated/text/mxvs-v26/page-0036.txt) |
| 1 | 附录 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=38) | 28 | [文本](../../generated/text/mxvs-v26/page-0038.txt) |
| 2 | 术语/缩略语 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mxvs%E6%B5%8B%E8%AF%95%E5%B7%A5%E5%85%B7%E5%A5%97%E4%BB%B6%E4%BD%BF%E7%94%A8%E6%89%8B%E5%86%8C_CN_V26.pdf#page=38) | 28 | [文本](../../generated/text/mxvs-v26/page-0038.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mxvs-v26/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mxvs-v26/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mxvs-v26/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mxvs-v26/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/mxvs-v26/page-0005.txt)
- [PDF 6 / 标签 iv](../../generated/text/mxvs-v26/page-0006.txt)
- [PDF 7 / 标签 iv](../../generated/text/mxvs-v26/page-0007.txt)
- [PDF 8 / 标签 v](../../generated/text/mxvs-v26/page-0008.txt)
- [PDF 9 / 标签 vi](../../generated/text/mxvs-v26/page-0009.txt)
- [PDF 10 / 标签 vii](../../generated/text/mxvs-v26/page-0010.txt)
- [PDF 11 / 标签 1](../../generated/text/mxvs-v26/page-0011.txt)
- [PDF 12 / 标签 2](../../generated/text/mxvs-v26/page-0012.txt)
- [PDF 13 / 标签 3](../../generated/text/mxvs-v26/page-0013.txt)
- [PDF 14 / 标签 4](../../generated/text/mxvs-v26/page-0014.txt)
- [PDF 15 / 标签 5](../../generated/text/mxvs-v26/page-0015.txt)
- [PDF 16 / 标签 6](../../generated/text/mxvs-v26/page-0016.txt)
- [PDF 17 / 标签 7](../../generated/text/mxvs-v26/page-0017.txt)
- [PDF 18 / 标签 8](../../generated/text/mxvs-v26/page-0018.txt)
- [PDF 19 / 标签 9](../../generated/text/mxvs-v26/page-0019.txt)
- [PDF 20 / 标签 10](../../generated/text/mxvs-v26/page-0020.txt)
- [PDF 21 / 标签 11](../../generated/text/mxvs-v26/page-0021.txt)
- [PDF 22 / 标签 12](../../generated/text/mxvs-v26/page-0022.txt)
- [PDF 23 / 标签 13](../../generated/text/mxvs-v26/page-0023.txt)
- [PDF 24 / 标签 14](../../generated/text/mxvs-v26/page-0024.txt)
- [PDF 25 / 标签 15](../../generated/text/mxvs-v26/page-0025.txt)
- [PDF 26 / 标签 16](../../generated/text/mxvs-v26/page-0026.txt)
- [PDF 27 / 标签 17](../../generated/text/mxvs-v26/page-0027.txt)
- [PDF 28 / 标签 18](../../generated/text/mxvs-v26/page-0028.txt)
- [PDF 29 / 标签 19](../../generated/text/mxvs-v26/page-0029.txt)
- [PDF 30 / 标签 20](../../generated/text/mxvs-v26/page-0030.txt)
- [PDF 31 / 标签 21](../../generated/text/mxvs-v26/page-0031.txt)
- [PDF 32 / 标签 22](../../generated/text/mxvs-v26/page-0032.txt)
- [PDF 33 / 标签 23](../../generated/text/mxvs-v26/page-0033.txt)
- [PDF 34 / 标签 24](../../generated/text/mxvs-v26/page-0034.txt)
- [PDF 35 / 标签 25](../../generated/text/mxvs-v26/page-0035.txt)
- [PDF 36 / 标签 26](../../generated/text/mxvs-v26/page-0036.txt)
- [PDF 37 / 标签 27](../../generated/text/mxvs-v26/page-0037.txt)
- [PDF 38 / 标签 28](../../generated/text/mxvs-v26/page-0038.txt)
