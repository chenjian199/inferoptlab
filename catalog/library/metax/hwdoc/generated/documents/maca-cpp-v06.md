# 沐曦通用GPU_MXMACA C++编程指南

文档 ID：`maca-cpp-v06`；文档修订：V06；发布日期：2026-03-27。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf)

SHA256：`030f0ca6e3c9c4a245b61a0d15a1c3469d411292f3aa728954c943843639168f`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 9 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=9)

> 本文档适用于沐曦MXC500系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及MXC600系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

未自动定位到候选页，请检索全文。

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=9) | 1 | [文本](../../generated/text/maca-cpp-v06/page-0009.txt) |
| 2 | 适用产品 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=9) | 1 | [文本](../../generated/text/maca-cpp-v06/page-0009.txt) |
| 1 | C++ 语言扩展 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=10) | 2 | [文本](../../generated/text/maca-cpp-v06/page-0010.txt) |
| 2 | 函数执行空间标识符 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=10) | 2 | [文本](../../generated/text/maca-cpp-v06/page-0010.txt) |
| 3 | __global__ | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=10) | 2 | [文本](../../generated/text/maca-cpp-v06/page-0010.txt) |
| 3 | __device__ | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=10) | 2 | [文本](../../generated/text/maca-cpp-v06/page-0010.txt) |
| 3 | __host__ | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=10) | 2 | [文本](../../generated/text/maca-cpp-v06/page-0010.txt) |
| 3 | 未定义的行为 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=11) | 3 | [文本](../../generated/text/maca-cpp-v06/page-0011.txt) |
| 3 | __noinline__与__forceinline__ | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=11) | 3 | [文本](../../generated/text/maca-cpp-v06/page-0011.txt) |
| 2 | 变量存储空间标识符 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=11) | 3 | [文本](../../generated/text/maca-cpp-v06/page-0011.txt) |
| 3 | __device__ | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=12) | 4 | [文本](../../generated/text/maca-cpp-v06/page-0012.txt) |
| 3 | __constant__ | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=12) | 4 | [文本](../../generated/text/maca-cpp-v06/page-0012.txt) |
| 3 | __shared__ | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=12) | 4 | [文本](../../generated/text/maca-cpp-v06/page-0012.txt) |
| 3 | __managed__ | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=13) | 5 | [文本](../../generated/text/maca-cpp-v06/page-0013.txt) |
| 2 | 内置类型 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=13) | 5 | [文本](../../generated/text/maca-cpp-v06/page-0013.txt) |
| 3 | maca_bfloat16 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=13) | 5 | [文本](../../generated/text/maca-cpp-v06/page-0013.txt) |
| 4 | maca_bfloat162 与 maca_bfloat16 关系 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=14) | 6 | [文本](../../generated/text/maca-cpp-v06/page-0014.txt) |
| 3 | Half-precision floating-point format（半精度浮点格式） | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=14) | 6 | [文本](../../generated/text/maca-cpp-v06/page-0014.txt) |
| 4 | IEEE 754 - 2008 半精度二进制浮点格式：binary16 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=14) | 6 | [文本](../../generated/text/maca-cpp-v06/page-0014.txt) |
| 4 | 指数编码 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=14) | 6 | [文本](../../generated/text/maca-cpp-v06/page-0014.txt) |
| 4 | 半精度示例 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=15) | 7 | [文本](../../generated/text/maca-cpp-v06/page-0015.txt) |
| 4 | half2 与 half 关系 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=15) | 7 | [文本](../../generated/text/maca-cpp-v06/page-0015.txt) |
| 2 | 内置向量类型 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=15) | 7 | [文本](../../generated/text/maca-cpp-v06/page-0015.txt) |
| 3 | char，short，int，long，longlong，float，double | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=15) | 7 | [文本](../../generated/text/maca-cpp-v06/page-0015.txt) |
| 3 | dim3 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 2 | 内置变量 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 3 | gridDim | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 3 | blockIdx | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 3 | blockDim | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 3 | threadIdx | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 3 | warpSize | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 2 | Memory Fence函数 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=17) | 9 | [文本](../../generated/text/maca-cpp-v06/page-0017.txt) |
| 2 | 同步函数 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=20) | 12 | [文本](../../generated/text/maca-cpp-v06/page-0020.txt) |
| 2 | 数学函数 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=21) | 13 | [文本](../../generated/text/maca-cpp-v06/page-0021.txt) |
| 3 | 半精度（half）算术函数 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=21) | 13 | [文本](../../generated/text/maca-cpp-v06/page-0021.txt) |
| 3 | half2算术函数 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=26) | 18 | [文本](../../generated/text/maca-cpp-v06/page-0026.txt) |
| 3 | half比较函数 | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=30) | 22 | [文本](../../generated/text/maca-cpp-v06/page-0030.txt) |
| 3 | half2比较函数 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=37) | 29 | [文本](../../generated/text/maca-cpp-v06/page-0037.txt) |
| 3 | 半精度转换与数据移动函数 | [47](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=47) | 39 | [文本](../../generated/text/maca-cpp-v06/page-0047.txt) |
| 3 | half数学函数 | [76](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=76) | 68 | [文本](../../generated/text/maca-cpp-v06/page-0076.txt) |
| 3 | half2数学函数 | [80](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=80) | 72 | [文本](../../generated/text/maca-cpp-v06/page-0080.txt) |
| 3 | Bfloat16算术函数 | [84](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=84) | 76 | [文本](../../generated/text/maca-cpp-v06/page-0084.txt) |
| 3 | Bfloat162算术函数 | [88](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=88) | 80 | [文本](../../generated/text/maca-cpp-v06/page-0088.txt) |
| 3 | Bfloat16比较函数 | [93](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=93) | 85 | [文本](../../generated/text/maca-cpp-v06/page-0093.txt) |
| 3 | Bfloat162比较函数 | [99](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=99) | 91 | [文本](../../generated/text/maca-cpp-v06/page-0099.txt) |
| 3 | Bfloat16精度转换与数据移动函数 | [110](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=110) | 102 | [文本](../../generated/text/maca-cpp-v06/page-0110.txt) |
| 3 | Bfloat16数学函数 | [139](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=139) | 131 | [文本](../../generated/text/maca-cpp-v06/page-0139.txt) |
| 3 | Bfloat162数学函数 | [143](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=143) | 135 | [文本](../../generated/text/maca-cpp-v06/page-0143.txt) |
| 3 | 单精度数学函数 | [147](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=147) | 139 | [文本](../../generated/text/maca-cpp-v06/page-0147.txt) |
| 3 | 双精度数学函数 | [169](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=169) | 161 | [文本](../../generated/text/maca-cpp-v06/page-0169.txt) |
| 3 | 整数型度数学函数 | [193](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=193) | 185 | [文本](../../generated/text/maca-cpp-v06/page-0193.txt) |
| 3 | 单精度intrinsic | [204](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=204) | 196 | [文本](../../generated/text/maca-cpp-v06/page-0204.txt) |
| 3 | 双精度intrinsic | [214](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=214) | 206 | [文本](../../generated/text/maca-cpp-v06/page-0214.txt) |
| 3 | 整数型intrinsic | [220](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=220) | 212 | [文本](../../generated/text/maca-cpp-v06/page-0220.txt) |
| 3 | 类型转换intrinsic | [225](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=225) | 217 | [文本](../../generated/text/maca-cpp-v06/page-0225.txt) |
| 3 | SIMD intrinsic | [240](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=240) | 232 | [文本](../../generated/text/maca-cpp-v06/page-0240.txt) |
| 2 | Texture函数 | [259](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=259) | 251 | [文本](../../generated/text/maca-cpp-v06/page-0259.txt) |
| 3 | Texture Object API | [259](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=259) | 251 | [文本](../../generated/text/maca-cpp-v06/page-0259.txt) |
| 4 | tex1Dfetch() | [259](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=259) | 251 | [文本](../../generated/text/maca-cpp-v06/page-0259.txt) |
| 4 | tex1D() | [259](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=259) | 251 | [文本](../../generated/text/maca-cpp-v06/page-0259.txt) |
| 3 | Texture Reference API | [260](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=260) | 252 | [文本](../../generated/text/maca-cpp-v06/page-0260.txt) |
| 4 | tex1Dfetch() | [260](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=260) | 252 | [文本](../../generated/text/maca-cpp-v06/page-0260.txt) |
| 4 | tex1D() | [261](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=261) | 253 | [文本](../../generated/text/maca-cpp-v06/page-0261.txt) |
| 2 | 只读数据缓存区加载函数 | [262](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=262) | 254 | [文本](../../generated/text/maca-cpp-v06/page-0262.txt) |
| 2 | 使用缓存提示的加载函数 | [262](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=262) | 254 | [文本](../../generated/text/maca-cpp-v06/page-0262.txt) |
| 2 | 使用缓存提示的存储函数 | [262](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=262) | 254 | [文本](../../generated/text/maca-cpp-v06/page-0262.txt) |
| 2 | 时间函数 | [263](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=263) | 255 | [文本](../../generated/text/maca-cpp-v06/page-0263.txt) |
| 2 | Atomic函数 | [263](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=263) | 255 | [文本](../../generated/text/maca-cpp-v06/page-0263.txt) |
| 3 | 算术函数 | [264](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=264) | 256 | [文本](../../generated/text/maca-cpp-v06/page-0264.txt) |
| 4 | atomicAdd() | [264](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=264) | 256 | [文本](../../generated/text/maca-cpp-v06/page-0264.txt) |
| 4 | atomicSub() | [264](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=264) | 256 | [文本](../../generated/text/maca-cpp-v06/page-0264.txt) |
| 4 | atomicExch() | [264](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=264) | 256 | [文本](../../generated/text/maca-cpp-v06/page-0264.txt) |
| 4 | atomicMin() | [265](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=265) | 257 | [文本](../../generated/text/maca-cpp-v06/page-0265.txt) |
| 4 | atomicMax() | [265](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=265) | 257 | [文本](../../generated/text/maca-cpp-v06/page-0265.txt) |
| 4 | atomicInc() | [265](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=265) | 257 | [文本](../../generated/text/maca-cpp-v06/page-0265.txt) |
| 4 | atomicDec() | [265](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=265) | 257 | [文本](../../generated/text/maca-cpp-v06/page-0265.txt) |
| 4 | atomicCAS() | [266](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=266) | 258 | [文本](../../generated/text/maca-cpp-v06/page-0266.txt) |
| 3 | 位运算函数 | [266](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=266) | 258 | [文本](../../generated/text/maca-cpp-v06/page-0266.txt) |
| 4 | atomicAnd() | [266](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=266) | 258 | [文本](../../generated/text/maca-cpp-v06/page-0266.txt) |
| 4 | atomicOr() | [266](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=266) | 258 | [文本](../../generated/text/maca-cpp-v06/page-0266.txt) |
| 4 | atomicXor() | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 2 | 地址空间谓词函数 | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 3 | __isGlobal() | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 3 | __isShared() | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 3 | __isLocal() | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 2 | 地址空间转换函数 | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 3 | __cvta_generic_to_global() | [267](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=267) | 259 | [文本](../../generated/text/maca-cpp-v06/page-0267.txt) |
| 3 | __cvta_generic_to_shared() | [268](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=268) | 260 | [文本](../../generated/text/maca-cpp-v06/page-0268.txt) |
| 3 | __cvta_generic_to_constant() | [268](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=268) | 260 | [文本](../../generated/text/maca-cpp-v06/page-0268.txt) |
| 3 | __cvta_generic_to_local() | [268](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=268) | 260 | [文本](../../generated/text/maca-cpp-v06/page-0268.txt) |
| 3 | __cvta_global_to_generic() | [268](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=268) | 260 | [文本](../../generated/text/maca-cpp-v06/page-0268.txt) |
| 3 | __cvta_shared_to_generic() | [268](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=268) | 260 | [文本](../../generated/text/maca-cpp-v06/page-0268.txt) |
| 3 | __cvta_constant_to_generic() | [268](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=268) | 260 | [文本](../../generated/text/maca-cpp-v06/page-0268.txt) |
| 3 | __cvta_local_to_generic() | [269](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=269) | 261 | [文本](../../generated/text/maca-cpp-v06/page-0269.txt) |
| 2 | Alloca函数 | [269](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=269) | 261 | [文本](../../generated/text/maca-cpp-v06/page-0269.txt) |
| 3 | alloca() | [269](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=269) | 261 | [文本](../../generated/text/maca-cpp-v06/page-0269.txt) |
| 2 | 编译器内置函数 | [269](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=269) | 261 | [文本](../../generated/text/maca-cpp-v06/page-0269.txt) |
| 3 | __builtin_assume_aligned() | [269](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=269) | 261 | [文本](../../generated/text/maca-cpp-v06/page-0269.txt) |
| 3 | __builtin_assume() | [270](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=270) | 262 | [文本](../../generated/text/maca-cpp-v06/page-0270.txt) |
| 3 | __assume() | [270](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=270) | 262 | [文本](../../generated/text/maca-cpp-v06/page-0270.txt) |
| 3 | __builtin_expect() | [270](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=270) | 262 | [文本](../../generated/text/maca-cpp-v06/page-0270.txt) |
| 3 | __builtin_unreachable() | [271](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=271) | 263 | [文本](../../generated/text/maca-cpp-v06/page-0271.txt) |
| 3 | __builtin_mxc_byte_perm | [271](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=271) | 263 | [文本](../../generated/text/maca-cpp-v06/page-0271.txt) |
| 3 | __builtin_mxc_load_global_async | [272](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=272) | 264 | [文本](../../generated/text/maca-cpp-v06/page-0272.txt) |
| 3 | __builtin_mxc_arrive | [273](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=273) | 265 | [文本](../../generated/text/maca-cpp-v06/page-0273.txt) |
| 3 | __builtin_mxc_arrive_gvmcnt | [274](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=274) | 266 | [文本](../../generated/text/maca-cpp-v06/page-0274.txt) |
| 3 | __builtin_mxc_arrive_bsmcnt | [274](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=274) | 266 | [文本](../../generated/text/maca-cpp-v06/page-0274.txt) |
| 3 | __builtin_mxc_barrier | [275](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=275) | 267 | [文本](../../generated/text/maca-cpp-v06/page-0275.txt) |
| 3 | __builtin_mxc_barrier_inst | [276](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=276) | 268 | [文本](../../generated/text/maca-cpp-v06/page-0276.txt) |
| 3 | __builtin_mxc_ldg_*_predicator | [276](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=276) | 268 | [文本](../../generated/text/maca-cpp-v06/page-0276.txt) |
| 3 | __builtin_mxc_stg_*_predicator | [278](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=278) | 270 | [文本](../../generated/text/maca-cpp-v06/page-0278.txt) |
| 2 | Warp Vote函数 | [279](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=279) | 271 | [文本](../../generated/text/maca-cpp-v06/page-0279.txt) |
| 2 | Warp Match函数 | [280](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=280) | 272 | [文本](../../generated/text/maca-cpp-v06/page-0280.txt) |
| 3 | 提要 | [280](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=280) | 272 | [文本](../../generated/text/maca-cpp-v06/page-0280.txt) |
| 3 | 描述 | [280](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=280) | 272 | [文本](../../generated/text/maca-cpp-v06/page-0280.txt) |
| 2 | Warp Reduce函数 | [281](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=281) | 273 | [文本](../../generated/text/maca-cpp-v06/page-0281.txt) |
| 3 | 提要 | [281](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=281) | 273 | [文本](../../generated/text/maca-cpp-v06/page-0281.txt) |
| 3 | 描述 | [281](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=281) | 273 | [文本](../../generated/text/maca-cpp-v06/page-0281.txt) |
| 2 | Warp Shuffle函数 | [282](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=282) | 274 | [文本](../../generated/text/maca-cpp-v06/page-0282.txt) |
| 3 | 提要 | [282](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=282) | 274 | [文本](../../generated/text/maca-cpp-v06/page-0282.txt) |
| 3 | 描述 | [282](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=282) | 274 | [文本](../../generated/text/maca-cpp-v06/page-0282.txt) |
| 3 | 例子 | [283](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=283) | 275 | [文本](../../generated/text/maca-cpp-v06/page-0283.txt) |
| 2 | Nanosleep函数 | [284](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=284) | 276 | [文本](../../generated/text/maca-cpp-v06/page-0284.txt) |
| 3 | 提要 | [284](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=284) | 276 | [文本](../../generated/text/maca-cpp-v06/page-0284.txt) |
| 3 | 描述 | [284](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=284) | 276 | [文本](../../generated/text/maca-cpp-v06/page-0284.txt) |
| 3 | 例子 | [284](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=284) | 276 | [文本](../../generated/text/maca-cpp-v06/page-0284.txt) |
| 2 | Warp matrix函数 | [284](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=284) | 276 | [文本](../../generated/text/maca-cpp-v06/page-0284.txt) |
| 3 | 描述 | [285](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=285) | 277 | [文本](../../generated/text/maca-cpp-v06/page-0285.txt) |
| 3 | 其他浮点类型 | [286](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=286) | 278 | [文本](../../generated/text/maca-cpp-v06/page-0286.txt) |
| 3 | 双精度类型 | [287](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=287) | 279 | [文本](../../generated/text/maca-cpp-v06/page-0287.txt) |
| 3 | 元素类型和矩阵形状 | [287](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=287) | 279 | [文本](../../generated/text/maca-cpp-v06/page-0287.txt) |
| 3 | 示例 | [288](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=288) | 280 | [文本](../../generated/text/maca-cpp-v06/page-0288.txt) |
| 2 | Asynchronous Data Copies | [288](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=288) | 280 | [文本](../../generated/text/maca-cpp-v06/page-0288.txt) |
| 3 | memcpy_async API | [288](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=288) | 280 | [文本](../../generated/text/maca-cpp-v06/page-0288.txt) |
| 3 | 没有memcpy_async | [289](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=289) | 281 | [文本](../../generated/text/maca-cpp-v06/page-0289.txt) |
| 3 | 有memcpy_async | [290](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=290) | 282 | [文本](../../generated/text/maca-cpp-v06/page-0290.txt) |
| 2 | Assert函数 | [291](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=291) | 283 | [文本](../../generated/text/maca-cpp-v06/page-0291.txt) |
| 2 | Trap函数 | [291](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=291) | 283 | [文本](../../generated/text/maca-cpp-v06/page-0291.txt) |
| 2 | Breakpoint函数 | [291](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=291) | 283 | [文本](../../generated/text/maca-cpp-v06/page-0291.txt) |
| 2 | 格式化输出 | [292](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=292) | 284 | [文本](../../generated/text/maca-cpp-v06/page-0292.txt) |
| 3 | Format Specifiers | [292](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=292) | 284 | [文本](../../generated/text/maca-cpp-v06/page-0292.txt) |
| 3 | 限制 | [292](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=292) | 284 | [文本](../../generated/text/maca-cpp-v06/page-0292.txt) |
| 3 | 例子 | [292](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=292) | 284 | [文本](../../generated/text/maca-cpp-v06/page-0292.txt) |
| 2 | 动态Global内存操作 | [293](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=293) | 285 | [文本](../../generated/text/maca-cpp-v06/page-0293.txt) |
| 3 | 堆内存分配 | [294](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=294) | 286 | [文本](../../generated/text/maca-cpp-v06/page-0294.txt) |
| 3 | 与host内存交互的api | [294](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=294) | 286 | [文本](../../generated/text/maca-cpp-v06/page-0294.txt) |
| 3 | 例子 | [294](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=294) | 286 | [文本](../../generated/text/maca-cpp-v06/page-0294.txt) |
| 4 | Per Thread 分配 | [294](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=294) | 286 | [文本](../../generated/text/maca-cpp-v06/page-0294.txt) |
| 4 | Per Thread block 分配 | [295](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=295) | 287 | [文本](../../generated/text/maca-cpp-v06/page-0295.txt) |
| 2 | 执行配置 | [296](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=296) | 288 | [文本](../../generated/text/maca-cpp-v06/page-0296.txt) |
| 2 | Launch Bounds（启动边界） | [296](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=296) | 288 | [文本](../../generated/text/maca-cpp-v06/page-0296.txt) |
| 2 | #pragma unroll | [297](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=297) | 289 | [文本](../../generated/text/maca-cpp-v06/page-0297.txt) |
| 2 | 关于内联汇编 | [298](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=298) | 290 | [文本](../../generated/text/maca-cpp-v06/page-0298.txt) |
| 1 | Cooperative Groups | [299](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=299) | 291 | [文本](../../generated/text/maca-cpp-v06/page-0299.txt) |
| 2 | 介绍 | [299](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=299) | 291 | [文本](../../generated/text/maca-cpp-v06/page-0299.txt) |
| 2 | 编程模型概念 | [299](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=299) | 291 | [文本](../../generated/text/maca-cpp-v06/page-0299.txt) |
| 3 | 组示例 | [300](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=300) | 292 | [文本](../../generated/text/maca-cpp-v06/page-0300.txt) |
| 2 | 组类型 | [300](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=300) | 292 | [文本](../../generated/text/maca-cpp-v06/page-0300.txt) |
| 3 | 隐式组 | [300](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=300) | 292 | [文本](../../generated/text/maca-cpp-v06/page-0300.txt) |
| 4 | Thread Block Group | [301](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=301) | 293 | [文本](../../generated/text/maca-cpp-v06/page-0301.txt) |
| 4 | Grid Group | [302](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=302) | 294 | [文本](../../generated/text/maca-cpp-v06/page-0302.txt) |
| 4 | Multi Grid Group | [302](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=302) | 294 | [文本](../../generated/text/maca-cpp-v06/page-0302.txt) |
| 3 | 显式组 | [303](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=303) | 295 | [文本](../../generated/text/maca-cpp-v06/page-0303.txt) |
| 4 | Thread Block Tile | [303](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=303) | 295 | [文本](../../generated/text/maca-cpp-v06/page-0303.txt) |
| 5 | Warp-Synchronous代码模型 | [304](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=304) | 296 | [文本](../../generated/text/maca-cpp-v06/page-0304.txt) |
| 5 | Single thread分组 | [304](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=304) | 296 | [文本](../../generated/text/maca-cpp-v06/page-0304.txt) |
| 4 | Coalesced Groups | [305](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=305) | 297 | [文本](../../generated/text/maca-cpp-v06/page-0305.txt) |
| 5 | Discovery Pattern | [306](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=306) | 298 | [文本](../../generated/text/maca-cpp-v06/page-0306.txt) |
| 2 | 组分割 | [306](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=306) | 298 | [文本](../../generated/text/maca-cpp-v06/page-0306.txt) |
| 3 | tiled_partition | [306](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=306) | 298 | [文本](../../generated/text/maca-cpp-v06/page-0306.txt) |
| 3 | labeled_partition | [307](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=307) | 299 | [文本](../../generated/text/maca-cpp-v06/page-0307.txt) |
| 3 | binary_partition | [307](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=307) | 299 | [文本](../../generated/text/maca-cpp-v06/page-0307.txt) |
| 2 | 组操作集合 | [308](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=308) | 300 | [文本](../../generated/text/maca-cpp-v06/page-0308.txt) |
| 3 | 同步 | [308](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=308) | 300 | [文本](../../generated/text/maca-cpp-v06/page-0308.txt) |
| 4 | sync | [308](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=308) | 300 | [文本](../../generated/text/maca-cpp-v06/page-0308.txt) |
| 3 | 数据移动 | [308](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=308) | 300 | [文本](../../generated/text/maca-cpp-v06/page-0308.txt) |
| 4 | memcpy_async | [308](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=308) | 300 | [文本](../../generated/text/maca-cpp-v06/page-0308.txt) |
| 2 | Grid 同步 | [310](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=310) | 302 | [文本](../../generated/text/maca-cpp-v06/page-0310.txt) |
| 2 | 多设备同步 | [311](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=311) | 303 | [文本](../../generated/text/maca-cpp-v06/page-0311.txt) |
| 1 | C++ 语言支持 | [313](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=313) | 305 | [文本](../../generated/text/maca-cpp-v06/page-0313.txt) |
| 2 | C++98 支持状态 | [313](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=313) | 305 | [文本](../../generated/text/maca-cpp-v06/page-0313.txt) |
| 2 | C++11支持状态 | [313](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=313) | 305 | [文本](../../generated/text/maca-cpp-v06/page-0313.txt) |
| 2 | C++14支持状态 | [313](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=313) | 305 | [文本](../../generated/text/maca-cpp-v06/page-0313.txt) |
| 2 | C++17以及之后标准支持状态 | [313](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20C%2B%2B%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V06.pdf#page=313) | 305 | [文本](../../generated/text/maca-cpp-v06/page-0313.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/maca-cpp-v06/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/maca-cpp-v06/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/maca-cpp-v06/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/maca-cpp-v06/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/maca-cpp-v06/page-0005.txt)
- [PDF 6 / 标签 iv](../../generated/text/maca-cpp-v06/page-0006.txt)
- [PDF 7 / 标签 v](../../generated/text/maca-cpp-v06/page-0007.txt)
- [PDF 8 / 标签 vi](../../generated/text/maca-cpp-v06/page-0008.txt)
- [PDF 9 / 标签 1](../../generated/text/maca-cpp-v06/page-0009.txt)
- [PDF 10 / 标签 2](../../generated/text/maca-cpp-v06/page-0010.txt)
- [PDF 11 / 标签 3](../../generated/text/maca-cpp-v06/page-0011.txt)
- [PDF 12 / 标签 4](../../generated/text/maca-cpp-v06/page-0012.txt)
- [PDF 13 / 标签 5](../../generated/text/maca-cpp-v06/page-0013.txt)
- [PDF 14 / 标签 6](../../generated/text/maca-cpp-v06/page-0014.txt)
- [PDF 15 / 标签 7](../../generated/text/maca-cpp-v06/page-0015.txt)
- [PDF 16 / 标签 8](../../generated/text/maca-cpp-v06/page-0016.txt)
- [PDF 17 / 标签 9](../../generated/text/maca-cpp-v06/page-0017.txt)
- [PDF 18 / 标签 10](../../generated/text/maca-cpp-v06/page-0018.txt)
- [PDF 19 / 标签 11](../../generated/text/maca-cpp-v06/page-0019.txt)
- [PDF 20 / 标签 12](../../generated/text/maca-cpp-v06/page-0020.txt)
- [PDF 21 / 标签 13](../../generated/text/maca-cpp-v06/page-0021.txt)
- [PDF 22 / 标签 14](../../generated/text/maca-cpp-v06/page-0022.txt)
- [PDF 23 / 标签 15](../../generated/text/maca-cpp-v06/page-0023.txt)
- [PDF 24 / 标签 16](../../generated/text/maca-cpp-v06/page-0024.txt)
- [PDF 25 / 标签 17](../../generated/text/maca-cpp-v06/page-0025.txt)
- [PDF 26 / 标签 18](../../generated/text/maca-cpp-v06/page-0026.txt)
- [PDF 27 / 标签 19](../../generated/text/maca-cpp-v06/page-0027.txt)
- [PDF 28 / 标签 20](../../generated/text/maca-cpp-v06/page-0028.txt)
- [PDF 29 / 标签 21](../../generated/text/maca-cpp-v06/page-0029.txt)
- [PDF 30 / 标签 22](../../generated/text/maca-cpp-v06/page-0030.txt)
- [PDF 31 / 标签 23](../../generated/text/maca-cpp-v06/page-0031.txt)
- [PDF 32 / 标签 24](../../generated/text/maca-cpp-v06/page-0032.txt)
- [PDF 33 / 标签 25](../../generated/text/maca-cpp-v06/page-0033.txt)
- [PDF 34 / 标签 26](../../generated/text/maca-cpp-v06/page-0034.txt)
- [PDF 35 / 标签 27](../../generated/text/maca-cpp-v06/page-0035.txt)
- [PDF 36 / 标签 28](../../generated/text/maca-cpp-v06/page-0036.txt)
- [PDF 37 / 标签 29](../../generated/text/maca-cpp-v06/page-0037.txt)
- [PDF 38 / 标签 30](../../generated/text/maca-cpp-v06/page-0038.txt)
- [PDF 39 / 标签 31](../../generated/text/maca-cpp-v06/page-0039.txt)
- [PDF 40 / 标签 32](../../generated/text/maca-cpp-v06/page-0040.txt)
- [PDF 41 / 标签 33](../../generated/text/maca-cpp-v06/page-0041.txt)
- [PDF 42 / 标签 34](../../generated/text/maca-cpp-v06/page-0042.txt)
- [PDF 43 / 标签 35](../../generated/text/maca-cpp-v06/page-0043.txt)
- [PDF 44 / 标签 36](../../generated/text/maca-cpp-v06/page-0044.txt)
- [PDF 45 / 标签 37](../../generated/text/maca-cpp-v06/page-0045.txt)
- [PDF 46 / 标签 38](../../generated/text/maca-cpp-v06/page-0046.txt)
- [PDF 47 / 标签 39](../../generated/text/maca-cpp-v06/page-0047.txt)
- [PDF 48 / 标签 40](../../generated/text/maca-cpp-v06/page-0048.txt)
- [PDF 49 / 标签 41](../../generated/text/maca-cpp-v06/page-0049.txt)
- [PDF 50 / 标签 42](../../generated/text/maca-cpp-v06/page-0050.txt)
- [PDF 51 / 标签 43](../../generated/text/maca-cpp-v06/page-0051.txt)
- [PDF 52 / 标签 44](../../generated/text/maca-cpp-v06/page-0052.txt)
- [PDF 53 / 标签 45](../../generated/text/maca-cpp-v06/page-0053.txt)
- [PDF 54 / 标签 46](../../generated/text/maca-cpp-v06/page-0054.txt)
- [PDF 55 / 标签 47](../../generated/text/maca-cpp-v06/page-0055.txt)
- [PDF 56 / 标签 48](../../generated/text/maca-cpp-v06/page-0056.txt)
- [PDF 57 / 标签 49](../../generated/text/maca-cpp-v06/page-0057.txt)
- [PDF 58 / 标签 50](../../generated/text/maca-cpp-v06/page-0058.txt)
- [PDF 59 / 标签 51](../../generated/text/maca-cpp-v06/page-0059.txt)
- [PDF 60 / 标签 52](../../generated/text/maca-cpp-v06/page-0060.txt)
- [PDF 61 / 标签 53](../../generated/text/maca-cpp-v06/page-0061.txt)
- [PDF 62 / 标签 54](../../generated/text/maca-cpp-v06/page-0062.txt)
- [PDF 63 / 标签 55](../../generated/text/maca-cpp-v06/page-0063.txt)
- [PDF 64 / 标签 56](../../generated/text/maca-cpp-v06/page-0064.txt)
- [PDF 65 / 标签 57](../../generated/text/maca-cpp-v06/page-0065.txt)
- [PDF 66 / 标签 58](../../generated/text/maca-cpp-v06/page-0066.txt)
- [PDF 67 / 标签 59](../../generated/text/maca-cpp-v06/page-0067.txt)
- [PDF 68 / 标签 60](../../generated/text/maca-cpp-v06/page-0068.txt)
- [PDF 69 / 标签 61](../../generated/text/maca-cpp-v06/page-0069.txt)
- [PDF 70 / 标签 62](../../generated/text/maca-cpp-v06/page-0070.txt)
- [PDF 71 / 标签 63](../../generated/text/maca-cpp-v06/page-0071.txt)
- [PDF 72 / 标签 64](../../generated/text/maca-cpp-v06/page-0072.txt)
- [PDF 73 / 标签 65](../../generated/text/maca-cpp-v06/page-0073.txt)
- [PDF 74 / 标签 66](../../generated/text/maca-cpp-v06/page-0074.txt)
- [PDF 75 / 标签 67](../../generated/text/maca-cpp-v06/page-0075.txt)
- [PDF 76 / 标签 68](../../generated/text/maca-cpp-v06/page-0076.txt)
- [PDF 77 / 标签 69](../../generated/text/maca-cpp-v06/page-0077.txt)
- [PDF 78 / 标签 70](../../generated/text/maca-cpp-v06/page-0078.txt)
- [PDF 79 / 标签 71](../../generated/text/maca-cpp-v06/page-0079.txt)
- [PDF 80 / 标签 72](../../generated/text/maca-cpp-v06/page-0080.txt)
- [PDF 81 / 标签 73](../../generated/text/maca-cpp-v06/page-0081.txt)
- [PDF 82 / 标签 74](../../generated/text/maca-cpp-v06/page-0082.txt)
- [PDF 83 / 标签 75](../../generated/text/maca-cpp-v06/page-0083.txt)
- [PDF 84 / 标签 76](../../generated/text/maca-cpp-v06/page-0084.txt)
- [PDF 85 / 标签 77](../../generated/text/maca-cpp-v06/page-0085.txt)
- [PDF 86 / 标签 78](../../generated/text/maca-cpp-v06/page-0086.txt)
- [PDF 87 / 标签 79](../../generated/text/maca-cpp-v06/page-0087.txt)
- [PDF 88 / 标签 80](../../generated/text/maca-cpp-v06/page-0088.txt)
- [PDF 89 / 标签 81](../../generated/text/maca-cpp-v06/page-0089.txt)
- [PDF 90 / 标签 82](../../generated/text/maca-cpp-v06/page-0090.txt)
- [PDF 91 / 标签 83](../../generated/text/maca-cpp-v06/page-0091.txt)
- [PDF 92 / 标签 84](../../generated/text/maca-cpp-v06/page-0092.txt)
- [PDF 93 / 标签 85](../../generated/text/maca-cpp-v06/page-0093.txt)
- [PDF 94 / 标签 86](../../generated/text/maca-cpp-v06/page-0094.txt)
- [PDF 95 / 标签 87](../../generated/text/maca-cpp-v06/page-0095.txt)
- [PDF 96 / 标签 88](../../generated/text/maca-cpp-v06/page-0096.txt)
- [PDF 97 / 标签 89](../../generated/text/maca-cpp-v06/page-0097.txt)
- [PDF 98 / 标签 90](../../generated/text/maca-cpp-v06/page-0098.txt)
- [PDF 99 / 标签 91](../../generated/text/maca-cpp-v06/page-0099.txt)
- [PDF 100 / 标签 92](../../generated/text/maca-cpp-v06/page-0100.txt)
- [PDF 101 / 标签 93](../../generated/text/maca-cpp-v06/page-0101.txt)
- [PDF 102 / 标签 94](../../generated/text/maca-cpp-v06/page-0102.txt)
- [PDF 103 / 标签 95](../../generated/text/maca-cpp-v06/page-0103.txt)
- [PDF 104 / 标签 96](../../generated/text/maca-cpp-v06/page-0104.txt)
- [PDF 105 / 标签 97](../../generated/text/maca-cpp-v06/page-0105.txt)
- [PDF 106 / 标签 98](../../generated/text/maca-cpp-v06/page-0106.txt)
- [PDF 107 / 标签 99](../../generated/text/maca-cpp-v06/page-0107.txt)
- [PDF 108 / 标签 100](../../generated/text/maca-cpp-v06/page-0108.txt)
- [PDF 109 / 标签 101](../../generated/text/maca-cpp-v06/page-0109.txt)
- [PDF 110 / 标签 102](../../generated/text/maca-cpp-v06/page-0110.txt)
- [PDF 111 / 标签 103](../../generated/text/maca-cpp-v06/page-0111.txt)
- [PDF 112 / 标签 104](../../generated/text/maca-cpp-v06/page-0112.txt)
- [PDF 113 / 标签 105](../../generated/text/maca-cpp-v06/page-0113.txt)
- [PDF 114 / 标签 106](../../generated/text/maca-cpp-v06/page-0114.txt)
- [PDF 115 / 标签 107](../../generated/text/maca-cpp-v06/page-0115.txt)
- [PDF 116 / 标签 108](../../generated/text/maca-cpp-v06/page-0116.txt)
- [PDF 117 / 标签 109](../../generated/text/maca-cpp-v06/page-0117.txt)
- [PDF 118 / 标签 110](../../generated/text/maca-cpp-v06/page-0118.txt)
- [PDF 119 / 标签 111](../../generated/text/maca-cpp-v06/page-0119.txt)
- [PDF 120 / 标签 112](../../generated/text/maca-cpp-v06/page-0120.txt)
- [PDF 121 / 标签 113](../../generated/text/maca-cpp-v06/page-0121.txt)
- [PDF 122 / 标签 114](../../generated/text/maca-cpp-v06/page-0122.txt)
- [PDF 123 / 标签 115](../../generated/text/maca-cpp-v06/page-0123.txt)
- [PDF 124 / 标签 116](../../generated/text/maca-cpp-v06/page-0124.txt)
- [PDF 125 / 标签 117](../../generated/text/maca-cpp-v06/page-0125.txt)
- [PDF 126 / 标签 118](../../generated/text/maca-cpp-v06/page-0126.txt)
- [PDF 127 / 标签 119](../../generated/text/maca-cpp-v06/page-0127.txt)
- [PDF 128 / 标签 120](../../generated/text/maca-cpp-v06/page-0128.txt)
- [PDF 129 / 标签 121](../../generated/text/maca-cpp-v06/page-0129.txt)
- [PDF 130 / 标签 122](../../generated/text/maca-cpp-v06/page-0130.txt)
- [PDF 131 / 标签 123](../../generated/text/maca-cpp-v06/page-0131.txt)
- [PDF 132 / 标签 124](../../generated/text/maca-cpp-v06/page-0132.txt)
- [PDF 133 / 标签 125](../../generated/text/maca-cpp-v06/page-0133.txt)
- [PDF 134 / 标签 126](../../generated/text/maca-cpp-v06/page-0134.txt)
- [PDF 135 / 标签 127](../../generated/text/maca-cpp-v06/page-0135.txt)
- [PDF 136 / 标签 128](../../generated/text/maca-cpp-v06/page-0136.txt)
- [PDF 137 / 标签 129](../../generated/text/maca-cpp-v06/page-0137.txt)
- [PDF 138 / 标签 130](../../generated/text/maca-cpp-v06/page-0138.txt)
- [PDF 139 / 标签 131](../../generated/text/maca-cpp-v06/page-0139.txt)
- [PDF 140 / 标签 132](../../generated/text/maca-cpp-v06/page-0140.txt)
- [PDF 141 / 标签 133](../../generated/text/maca-cpp-v06/page-0141.txt)
- [PDF 142 / 标签 134](../../generated/text/maca-cpp-v06/page-0142.txt)
- [PDF 143 / 标签 135](../../generated/text/maca-cpp-v06/page-0143.txt)
- [PDF 144 / 标签 136](../../generated/text/maca-cpp-v06/page-0144.txt)
- [PDF 145 / 标签 137](../../generated/text/maca-cpp-v06/page-0145.txt)
- [PDF 146 / 标签 138](../../generated/text/maca-cpp-v06/page-0146.txt)
- [PDF 147 / 标签 139](../../generated/text/maca-cpp-v06/page-0147.txt)
- [PDF 148 / 标签 140](../../generated/text/maca-cpp-v06/page-0148.txt)
- [PDF 149 / 标签 141](../../generated/text/maca-cpp-v06/page-0149.txt)
- [PDF 150 / 标签 142](../../generated/text/maca-cpp-v06/page-0150.txt)
- [PDF 151 / 标签 143](../../generated/text/maca-cpp-v06/page-0151.txt)
- [PDF 152 / 标签 144](../../generated/text/maca-cpp-v06/page-0152.txt)
- [PDF 153 / 标签 145](../../generated/text/maca-cpp-v06/page-0153.txt)
- [PDF 154 / 标签 146](../../generated/text/maca-cpp-v06/page-0154.txt)
- [PDF 155 / 标签 147](../../generated/text/maca-cpp-v06/page-0155.txt)
- [PDF 156 / 标签 148](../../generated/text/maca-cpp-v06/page-0156.txt)
- [PDF 157 / 标签 149](../../generated/text/maca-cpp-v06/page-0157.txt)
- [PDF 158 / 标签 150](../../generated/text/maca-cpp-v06/page-0158.txt)
- [PDF 159 / 标签 151](../../generated/text/maca-cpp-v06/page-0159.txt)
- [PDF 160 / 标签 152](../../generated/text/maca-cpp-v06/page-0160.txt)
- [PDF 161 / 标签 153](../../generated/text/maca-cpp-v06/page-0161.txt)
- [PDF 162 / 标签 154](../../generated/text/maca-cpp-v06/page-0162.txt)
- [PDF 163 / 标签 155](../../generated/text/maca-cpp-v06/page-0163.txt)
- [PDF 164 / 标签 156](../../generated/text/maca-cpp-v06/page-0164.txt)
- [PDF 165 / 标签 157](../../generated/text/maca-cpp-v06/page-0165.txt)
- [PDF 166 / 标签 158](../../generated/text/maca-cpp-v06/page-0166.txt)
- [PDF 167 / 标签 159](../../generated/text/maca-cpp-v06/page-0167.txt)
- [PDF 168 / 标签 160](../../generated/text/maca-cpp-v06/page-0168.txt)
- [PDF 169 / 标签 161](../../generated/text/maca-cpp-v06/page-0169.txt)
- [PDF 170 / 标签 162](../../generated/text/maca-cpp-v06/page-0170.txt)
- [PDF 171 / 标签 163](../../generated/text/maca-cpp-v06/page-0171.txt)
- [PDF 172 / 标签 164](../../generated/text/maca-cpp-v06/page-0172.txt)
- [PDF 173 / 标签 165](../../generated/text/maca-cpp-v06/page-0173.txt)
- [PDF 174 / 标签 166](../../generated/text/maca-cpp-v06/page-0174.txt)
- [PDF 175 / 标签 167](../../generated/text/maca-cpp-v06/page-0175.txt)
- [PDF 176 / 标签 168](../../generated/text/maca-cpp-v06/page-0176.txt)
- [PDF 177 / 标签 169](../../generated/text/maca-cpp-v06/page-0177.txt)
- [PDF 178 / 标签 170](../../generated/text/maca-cpp-v06/page-0178.txt)
- [PDF 179 / 标签 171](../../generated/text/maca-cpp-v06/page-0179.txt)
- [PDF 180 / 标签 172](../../generated/text/maca-cpp-v06/page-0180.txt)
- [PDF 181 / 标签 173](../../generated/text/maca-cpp-v06/page-0181.txt)
- [PDF 182 / 标签 174](../../generated/text/maca-cpp-v06/page-0182.txt)
- [PDF 183 / 标签 175](../../generated/text/maca-cpp-v06/page-0183.txt)
- [PDF 184 / 标签 176](../../generated/text/maca-cpp-v06/page-0184.txt)
- [PDF 185 / 标签 177](../../generated/text/maca-cpp-v06/page-0185.txt)
- [PDF 186 / 标签 178](../../generated/text/maca-cpp-v06/page-0186.txt)
- [PDF 187 / 标签 179](../../generated/text/maca-cpp-v06/page-0187.txt)
- [PDF 188 / 标签 180](../../generated/text/maca-cpp-v06/page-0188.txt)
- [PDF 189 / 标签 181](../../generated/text/maca-cpp-v06/page-0189.txt)
- [PDF 190 / 标签 182](../../generated/text/maca-cpp-v06/page-0190.txt)
- [PDF 191 / 标签 183](../../generated/text/maca-cpp-v06/page-0191.txt)
- [PDF 192 / 标签 184](../../generated/text/maca-cpp-v06/page-0192.txt)
- [PDF 193 / 标签 185](../../generated/text/maca-cpp-v06/page-0193.txt)
- [PDF 194 / 标签 186](../../generated/text/maca-cpp-v06/page-0194.txt)
- [PDF 195 / 标签 187](../../generated/text/maca-cpp-v06/page-0195.txt)
- [PDF 196 / 标签 188](../../generated/text/maca-cpp-v06/page-0196.txt)
- [PDF 197 / 标签 189](../../generated/text/maca-cpp-v06/page-0197.txt)
- [PDF 198 / 标签 190](../../generated/text/maca-cpp-v06/page-0198.txt)
- [PDF 199 / 标签 191](../../generated/text/maca-cpp-v06/page-0199.txt)
- [PDF 200 / 标签 192](../../generated/text/maca-cpp-v06/page-0200.txt)
- [PDF 201 / 标签 193](../../generated/text/maca-cpp-v06/page-0201.txt)
- [PDF 202 / 标签 194](../../generated/text/maca-cpp-v06/page-0202.txt)
- [PDF 203 / 标签 195](../../generated/text/maca-cpp-v06/page-0203.txt)
- [PDF 204 / 标签 196](../../generated/text/maca-cpp-v06/page-0204.txt)
- [PDF 205 / 标签 197](../../generated/text/maca-cpp-v06/page-0205.txt)
- [PDF 206 / 标签 198](../../generated/text/maca-cpp-v06/page-0206.txt)
- [PDF 207 / 标签 199](../../generated/text/maca-cpp-v06/page-0207.txt)
- [PDF 208 / 标签 200](../../generated/text/maca-cpp-v06/page-0208.txt)
- [PDF 209 / 标签 201](../../generated/text/maca-cpp-v06/page-0209.txt)
- [PDF 210 / 标签 202](../../generated/text/maca-cpp-v06/page-0210.txt)
- [PDF 211 / 标签 203](../../generated/text/maca-cpp-v06/page-0211.txt)
- [PDF 212 / 标签 204](../../generated/text/maca-cpp-v06/page-0212.txt)
- [PDF 213 / 标签 205](../../generated/text/maca-cpp-v06/page-0213.txt)
- [PDF 214 / 标签 206](../../generated/text/maca-cpp-v06/page-0214.txt)
- [PDF 215 / 标签 207](../../generated/text/maca-cpp-v06/page-0215.txt)
- [PDF 216 / 标签 208](../../generated/text/maca-cpp-v06/page-0216.txt)
- [PDF 217 / 标签 209](../../generated/text/maca-cpp-v06/page-0217.txt)
- [PDF 218 / 标签 210](../../generated/text/maca-cpp-v06/page-0218.txt)
- [PDF 219 / 标签 211](../../generated/text/maca-cpp-v06/page-0219.txt)
- [PDF 220 / 标签 212](../../generated/text/maca-cpp-v06/page-0220.txt)
- [PDF 221 / 标签 213](../../generated/text/maca-cpp-v06/page-0221.txt)
- [PDF 222 / 标签 214](../../generated/text/maca-cpp-v06/page-0222.txt)
- [PDF 223 / 标签 215](../../generated/text/maca-cpp-v06/page-0223.txt)
- [PDF 224 / 标签 216](../../generated/text/maca-cpp-v06/page-0224.txt)
- [PDF 225 / 标签 217](../../generated/text/maca-cpp-v06/page-0225.txt)
- [PDF 226 / 标签 218](../../generated/text/maca-cpp-v06/page-0226.txt)
- [PDF 227 / 标签 219](../../generated/text/maca-cpp-v06/page-0227.txt)
- [PDF 228 / 标签 220](../../generated/text/maca-cpp-v06/page-0228.txt)
- [PDF 229 / 标签 221](../../generated/text/maca-cpp-v06/page-0229.txt)
- [PDF 230 / 标签 222](../../generated/text/maca-cpp-v06/page-0230.txt)
- [PDF 231 / 标签 223](../../generated/text/maca-cpp-v06/page-0231.txt)
- [PDF 232 / 标签 224](../../generated/text/maca-cpp-v06/page-0232.txt)
- [PDF 233 / 标签 225](../../generated/text/maca-cpp-v06/page-0233.txt)
- [PDF 234 / 标签 226](../../generated/text/maca-cpp-v06/page-0234.txt)
- [PDF 235 / 标签 227](../../generated/text/maca-cpp-v06/page-0235.txt)
- [PDF 236 / 标签 228](../../generated/text/maca-cpp-v06/page-0236.txt)
- [PDF 237 / 标签 229](../../generated/text/maca-cpp-v06/page-0237.txt)
- [PDF 238 / 标签 230](../../generated/text/maca-cpp-v06/page-0238.txt)
- [PDF 239 / 标签 231](../../generated/text/maca-cpp-v06/page-0239.txt)
- [PDF 240 / 标签 232](../../generated/text/maca-cpp-v06/page-0240.txt)
- [PDF 241 / 标签 233](../../generated/text/maca-cpp-v06/page-0241.txt)
- [PDF 242 / 标签 234](../../generated/text/maca-cpp-v06/page-0242.txt)
- [PDF 243 / 标签 235](../../generated/text/maca-cpp-v06/page-0243.txt)
- [PDF 244 / 标签 236](../../generated/text/maca-cpp-v06/page-0244.txt)
- [PDF 245 / 标签 237](../../generated/text/maca-cpp-v06/page-0245.txt)
- [PDF 246 / 标签 238](../../generated/text/maca-cpp-v06/page-0246.txt)
- [PDF 247 / 标签 239](../../generated/text/maca-cpp-v06/page-0247.txt)
- [PDF 248 / 标签 240](../../generated/text/maca-cpp-v06/page-0248.txt)
- [PDF 249 / 标签 241](../../generated/text/maca-cpp-v06/page-0249.txt)
- [PDF 250 / 标签 242](../../generated/text/maca-cpp-v06/page-0250.txt)
- [PDF 251 / 标签 243](../../generated/text/maca-cpp-v06/page-0251.txt)
- [PDF 252 / 标签 244](../../generated/text/maca-cpp-v06/page-0252.txt)
- [PDF 253 / 标签 245](../../generated/text/maca-cpp-v06/page-0253.txt)
- [PDF 254 / 标签 246](../../generated/text/maca-cpp-v06/page-0254.txt)
- [PDF 255 / 标签 247](../../generated/text/maca-cpp-v06/page-0255.txt)
- [PDF 256 / 标签 248](../../generated/text/maca-cpp-v06/page-0256.txt)
- [PDF 257 / 标签 249](../../generated/text/maca-cpp-v06/page-0257.txt)
- [PDF 258 / 标签 250](../../generated/text/maca-cpp-v06/page-0258.txt)
- [PDF 259 / 标签 251](../../generated/text/maca-cpp-v06/page-0259.txt)
- [PDF 260 / 标签 252](../../generated/text/maca-cpp-v06/page-0260.txt)
- [PDF 261 / 标签 253](../../generated/text/maca-cpp-v06/page-0261.txt)
- [PDF 262 / 标签 254](../../generated/text/maca-cpp-v06/page-0262.txt)
- [PDF 263 / 标签 255](../../generated/text/maca-cpp-v06/page-0263.txt)
- [PDF 264 / 标签 256](../../generated/text/maca-cpp-v06/page-0264.txt)
- [PDF 265 / 标签 257](../../generated/text/maca-cpp-v06/page-0265.txt)
- [PDF 266 / 标签 258](../../generated/text/maca-cpp-v06/page-0266.txt)
- [PDF 267 / 标签 259](../../generated/text/maca-cpp-v06/page-0267.txt)
- [PDF 268 / 标签 260](../../generated/text/maca-cpp-v06/page-0268.txt)
- [PDF 269 / 标签 261](../../generated/text/maca-cpp-v06/page-0269.txt)
- [PDF 270 / 标签 262](../../generated/text/maca-cpp-v06/page-0270.txt)
- [PDF 271 / 标签 263](../../generated/text/maca-cpp-v06/page-0271.txt)
- [PDF 272 / 标签 264](../../generated/text/maca-cpp-v06/page-0272.txt)
- [PDF 273 / 标签 265](../../generated/text/maca-cpp-v06/page-0273.txt)
- [PDF 274 / 标签 266](../../generated/text/maca-cpp-v06/page-0274.txt)
- [PDF 275 / 标签 267](../../generated/text/maca-cpp-v06/page-0275.txt)
- [PDF 276 / 标签 268](../../generated/text/maca-cpp-v06/page-0276.txt)
- [PDF 277 / 标签 269](../../generated/text/maca-cpp-v06/page-0277.txt)
- [PDF 278 / 标签 270](../../generated/text/maca-cpp-v06/page-0278.txt)
- [PDF 279 / 标签 271](../../generated/text/maca-cpp-v06/page-0279.txt)
- [PDF 280 / 标签 272](../../generated/text/maca-cpp-v06/page-0280.txt)
- [PDF 281 / 标签 273](../../generated/text/maca-cpp-v06/page-0281.txt)
- [PDF 282 / 标签 274](../../generated/text/maca-cpp-v06/page-0282.txt)
- [PDF 283 / 标签 275](../../generated/text/maca-cpp-v06/page-0283.txt)
- [PDF 284 / 标签 276](../../generated/text/maca-cpp-v06/page-0284.txt)
- [PDF 285 / 标签 277](../../generated/text/maca-cpp-v06/page-0285.txt)
- [PDF 286 / 标签 278](../../generated/text/maca-cpp-v06/page-0286.txt)
- [PDF 287 / 标签 279](../../generated/text/maca-cpp-v06/page-0287.txt)
- [PDF 288 / 标签 280](../../generated/text/maca-cpp-v06/page-0288.txt)
- [PDF 289 / 标签 281](../../generated/text/maca-cpp-v06/page-0289.txt)
- [PDF 290 / 标签 282](../../generated/text/maca-cpp-v06/page-0290.txt)
- [PDF 291 / 标签 283](../../generated/text/maca-cpp-v06/page-0291.txt)
- [PDF 292 / 标签 284](../../generated/text/maca-cpp-v06/page-0292.txt)
- [PDF 293 / 标签 285](../../generated/text/maca-cpp-v06/page-0293.txt)
- [PDF 294 / 标签 286](../../generated/text/maca-cpp-v06/page-0294.txt)
- [PDF 295 / 标签 287](../../generated/text/maca-cpp-v06/page-0295.txt)
- [PDF 296 / 标签 288](../../generated/text/maca-cpp-v06/page-0296.txt)
- [PDF 297 / 标签 289](../../generated/text/maca-cpp-v06/page-0297.txt)
- [PDF 298 / 标签 290](../../generated/text/maca-cpp-v06/page-0298.txt)
- [PDF 299 / 标签 291](../../generated/text/maca-cpp-v06/page-0299.txt)
- [PDF 300 / 标签 292](../../generated/text/maca-cpp-v06/page-0300.txt)
- [PDF 301 / 标签 293](../../generated/text/maca-cpp-v06/page-0301.txt)
- [PDF 302 / 标签 294](../../generated/text/maca-cpp-v06/page-0302.txt)
- [PDF 303 / 标签 295](../../generated/text/maca-cpp-v06/page-0303.txt)
- [PDF 304 / 标签 296](../../generated/text/maca-cpp-v06/page-0304.txt)
- [PDF 305 / 标签 297](../../generated/text/maca-cpp-v06/page-0305.txt)
- [PDF 306 / 标签 298](../../generated/text/maca-cpp-v06/page-0306.txt)
- [PDF 307 / 标签 299](../../generated/text/maca-cpp-v06/page-0307.txt)
- [PDF 308 / 标签 300](../../generated/text/maca-cpp-v06/page-0308.txt)
- [PDF 309 / 标签 301](../../generated/text/maca-cpp-v06/page-0309.txt)
- [PDF 310 / 标签 302](../../generated/text/maca-cpp-v06/page-0310.txt)
- [PDF 311 / 标签 303](../../generated/text/maca-cpp-v06/page-0311.txt)
- [PDF 312 / 标签 304](../../generated/text/maca-cpp-v06/page-0312.txt)
- [PDF 313 / 标签 305](../../generated/text/maca-cpp-v06/page-0313.txt)
