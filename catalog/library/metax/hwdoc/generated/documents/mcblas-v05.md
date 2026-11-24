# 沐曦通用GPU_mcBLAS API参考

文档 ID：`mcblas-v05`；文档修订：V05；发布日期：2026-03-27。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf)

SHA256：`89e54674efde34906958f75828231bc53e3e7a72986e741a8e220f52761b9c13`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 8 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=8)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 8 页（标签 1）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=8) · [逐页文本](../../generated/text/mcblas-v05/page-0008.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 简介 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=8) | 1 | [文本](../../generated/text/mcblas-v05/page-0008.txt) |
| 2 | 适用产品 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=8) | 1 | [文本](../../generated/text/mcblas-v05/page-0008.txt) |
| 2 | 安装mcBLAS | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=8) | 1 | [文本](../../generated/text/mcblas-v05/page-0008.txt) |
| 2 | Hello mcBLAS | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=9) | 2 | [文本](../../generated/text/mcblas-v05/page-0009.txt) |
| 2 | 数据布局 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=12) | 5 | [文本](../../generated/text/mcblas-v05/page-0012.txt) |
| 1 | 使用mcBLAS API | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 2 | mcBLAS数据类型 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcblasHandle_t | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcblas_int | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcblas_stride | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcblas_half | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcComplex | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcDoubleComplex | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=13) | 6 | [文本](../../generated/text/mcblas-v05/page-0013.txt) |
| 3 | mcblasStatus_t | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=14) | 7 | [文本](../../generated/text/mcblas-v05/page-0014.txt) |
| 3 | macaDataType_t | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=14) | 7 | [文本](../../generated/text/mcblas-v05/page-0014.txt) |
| 3 | mcblasOperation_t | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=15) | 8 | [文本](../../generated/text/mcblas-v05/page-0015.txt) |
| 3 | mcblasFillMode_t | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=15) | 8 | [文本](../../generated/text/mcblas-v05/page-0015.txt) |
| 3 | mcblasDiagType_t | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=15) | 8 | [文本](../../generated/text/mcblas-v05/page-0015.txt) |
| 3 | mcblasSideMode_t | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=15) | 8 | [文本](../../generated/text/mcblas-v05/page-0015.txt) |
| 3 | mcblasPointerMode_t | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=16) | 9 | [文本](../../generated/text/mcblas-v05/page-0016.txt) |
| 3 | mcblasAtomicsMode_t | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=16) | 9 | [文本](../../generated/text/mcblas-v05/page-0016.txt) |
| 3 | mcblasGemmAlgo_t | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=16) | 9 | [文本](../../generated/text/mcblas-v05/page-0016.txt) |
| 3 | mcblasMath_t | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=17) | 10 | [文本](../../generated/text/mcblas-v05/page-0017.txt) |
| 3 | mcblasComputeType_t | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=17) | 10 | [文本](../../generated/text/mcblas-v05/page-0017.txt) |
| 2 | mcBLAS辅助函数 | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=18) | 11 | [文本](../../generated/text/mcblas-v05/page-0018.txt) |
| 3 | mcblasCreate() | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=18) | 11 | [文本](../../generated/text/mcblas-v05/page-0018.txt) |
| 3 | mcblasDestroy() | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=19) | 12 | [文本](../../generated/text/mcblas-v05/page-0019.txt) |
| 3 | mcblasGetVersion() | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=19) | 12 | [文本](../../generated/text/mcblas-v05/page-0019.txt) |
| 3 | mcblasGetProperty() | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=19) | 12 | [文本](../../generated/text/mcblas-v05/page-0019.txt) |
| 3 | mcblasGetStatusName() | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=20) | 13 | [文本](../../generated/text/mcblas-v05/page-0020.txt) |
| 3 | mcblasGetStatusString() | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=20) | 13 | [文本](../../generated/text/mcblas-v05/page-0020.txt) |
| 3 | mcblasSetStream() | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=20) | 13 | [文本](../../generated/text/mcblas-v05/page-0020.txt) |
| 3 | mcblasSetWorkspace() | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=21) | 14 | [文本](../../generated/text/mcblas-v05/page-0021.txt) |
| 3 | mcblasGetStream() | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=21) | 14 | [文本](../../generated/text/mcblas-v05/page-0021.txt) |
| 3 | mcblasGetPointerMode() | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=22) | 15 | [文本](../../generated/text/mcblas-v05/page-0022.txt) |
| 3 | mcblasSetPointerMode() | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=22) | 15 | [文本](../../generated/text/mcblas-v05/page-0022.txt) |
| 3 | mcblasSetVector() | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=22) | 15 | [文本](../../generated/text/mcblas-v05/page-0022.txt) |
| 3 | mcblasGetVector() | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=23) | 16 | [文本](../../generated/text/mcblas-v05/page-0023.txt) |
| 3 | mcblasSetMatrix() | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=23) | 16 | [文本](../../generated/text/mcblas-v05/page-0023.txt) |
| 3 | mcblasGetMatrix() | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=24) | 17 | [文本](../../generated/text/mcblas-v05/page-0024.txt) |
| 3 | mcblasSetVectorAsync() | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=24) | 17 | [文本](../../generated/text/mcblas-v05/page-0024.txt) |
| 3 | mcblasGetVectorAsync() | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=24) | 17 | [文本](../../generated/text/mcblas-v05/page-0024.txt) |
| 3 | mcblasSetMatrixAsync() | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=25) | 18 | [文本](../../generated/text/mcblas-v05/page-0025.txt) |
| 3 | mcblasGetMatrixAsync() | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=25) | 18 | [文本](../../generated/text/mcblas-v05/page-0025.txt) |
| 3 | mcblasSetAtomicsMode() | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=26) | 19 | [文本](../../generated/text/mcblas-v05/page-0026.txt) |
| 3 | mcblasGetAtomicsMode() | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=26) | 19 | [文本](../../generated/text/mcblas-v05/page-0026.txt) |
| 3 | mcblasSetMathMode() | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=26) | 19 | [文本](../../generated/text/mcblas-v05/page-0026.txt) |
| 3 | mcblasGetMathMode() | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=27) | 20 | [文本](../../generated/text/mcblas-v05/page-0027.txt) |
| 3 | mcblasSetSmCountTarget() | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=27) | 20 | [文本](../../generated/text/mcblas-v05/page-0027.txt) |
| 3 | mcblasGetSmCountTarget() | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=27) | 20 | [文本](../../generated/text/mcblas-v05/page-0027.txt) |
| 3 | mcblasLoggerConfigure() | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=27) | 20 | [文本](../../generated/text/mcblas-v05/page-0027.txt) |
| 3 | mcblasGetLoggerCallback() | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=28) | 21 | [文本](../../generated/text/mcblas-v05/page-0028.txt) |
| 3 | mcblasSetLoggerCallback() | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=28) | 21 | [文本](../../generated/text/mcblas-v05/page-0028.txt) |
| 2 | mcBLAS Level-1函数 | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=29) | 22 | [文本](../../generated/text/mcblas-v05/page-0029.txt) |
| 3 | mcblasI<t>amax() | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=29) | 22 | [文本](../../generated/text/mcblas-v05/page-0029.txt) |
| 3 | mcblasI<t>amin() | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=30) | 23 | [文本](../../generated/text/mcblas-v05/page-0030.txt) |
| 3 | mcblas<t>asum() | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=31) | 24 | [文本](../../generated/text/mcblas-v05/page-0031.txt) |
| 3 | mcblas<t>axpy() | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=31) | 24 | [文本](../../generated/text/mcblas-v05/page-0031.txt) |
| 3 | mcblas<t>copy() | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=32) | 25 | [文本](../../generated/text/mcblas-v05/page-0032.txt) |
| 3 | mcblas<t>dot() | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=33) | 26 | [文本](../../generated/text/mcblas-v05/page-0033.txt) |
| 3 | mcblas<t>nrm2() | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=34) | 27 | [文本](../../generated/text/mcblas-v05/page-0034.txt) |
| 3 | mcblas<t>rot() | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=35) | 28 | [文本](../../generated/text/mcblas-v05/page-0035.txt) |
| 3 | mcblas<t>rotg() | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=36) | 29 | [文本](../../generated/text/mcblas-v05/page-0036.txt) |
| 3 | mcblas<t>rotm() | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=38) | 31 | [文本](../../generated/text/mcblas-v05/page-0038.txt) |
| 3 | mcblas<t>rotmg() | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=39) | 32 | [文本](../../generated/text/mcblas-v05/page-0039.txt) |
| 3 | mcblas<t>scal() | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=40) | 33 | [文本](../../generated/text/mcblas-v05/page-0040.txt) |
| 3 | mcblas<t>swap() | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=41) | 34 | [文本](../../generated/text/mcblas-v05/page-0041.txt) |
| 2 | mcBLAS Level-2函数 | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=42) | 35 | [文本](../../generated/text/mcblas-v05/page-0042.txt) |
| 3 | mcblas<t>gbmv() | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=42) | 35 | [文本](../../generated/text/mcblas-v05/page-0042.txt) |
| 3 | mcblas<t>gemv() | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=44) | 37 | [文本](../../generated/text/mcblas-v05/page-0044.txt) |
| 3 | mcblas<t>ger() | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=45) | 38 | [文本](../../generated/text/mcblas-v05/page-0045.txt) |
| 3 | mcblas<t>sbmv() | [47](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=47) | 40 | [文本](../../generated/text/mcblas-v05/page-0047.txt) |
| 3 | mcblas<t>spmv() | [48](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=48) | 41 | [文本](../../generated/text/mcblas-v05/page-0048.txt) |
| 3 | mcblas<t>spr() | [49](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=49) | 42 | [文本](../../generated/text/mcblas-v05/page-0049.txt) |
| 3 | mcblas<t>spr2() | [50](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=50) | 43 | [文本](../../generated/text/mcblas-v05/page-0050.txt) |
| 3 | mcblas<t>symv() | [51](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=51) | 44 | [文本](../../generated/text/mcblas-v05/page-0051.txt) |
| 3 | mcblas<t>syr() | [53](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=53) | 46 | [文本](../../generated/text/mcblas-v05/page-0053.txt) |
| 3 | mcblas<t>syr2() | [54](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=54) | 47 | [文本](../../generated/text/mcblas-v05/page-0054.txt) |
| 3 | mcblas<t>tbmv() | [55](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=55) | 48 | [文本](../../generated/text/mcblas-v05/page-0055.txt) |
| 3 | mcblas<t>tbsv() | [57](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=57) | 50 | [文本](../../generated/text/mcblas-v05/page-0057.txt) |
| 3 | mcblas<t>tpmv() | [58](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=58) | 51 | [文本](../../generated/text/mcblas-v05/page-0058.txt) |
| 3 | mcblas<t>tpsv() | [60](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=60) | 53 | [文本](../../generated/text/mcblas-v05/page-0060.txt) |
| 3 | mcblas<t>trmv() | [62](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=62) | 55 | [文本](../../generated/text/mcblas-v05/page-0062.txt) |
| 3 | mcblas<t>trsv() | [63](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=63) | 56 | [文本](../../generated/text/mcblas-v05/page-0063.txt) |
| 3 | mcblas<t>hemv() | [65](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=65) | 58 | [文本](../../generated/text/mcblas-v05/page-0065.txt) |
| 3 | mcblas<t>hbmv() | [66](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=66) | 59 | [文本](../../generated/text/mcblas-v05/page-0066.txt) |
| 3 | mcblas<t>hpmv() | [68](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=68) | 61 | [文本](../../generated/text/mcblas-v05/page-0068.txt) |
| 3 | mcblas<t>her() | [69](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=69) | 62 | [文本](../../generated/text/mcblas-v05/page-0069.txt) |
| 3 | mcblas<t>her2() | [70](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=70) | 63 | [文本](../../generated/text/mcblas-v05/page-0070.txt) |
| 3 | mcblas<t>hpr() | [71](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=71) | 64 | [文本](../../generated/text/mcblas-v05/page-0071.txt) |
| 3 | mcblas<t>hpr2() | [73](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=73) | 66 | [文本](../../generated/text/mcblas-v05/page-0073.txt) |
| 3 | mcblas<t>gemvBatched() | [74](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=74) | 67 | [文本](../../generated/text/mcblas-v05/page-0074.txt) |
| 3 | mcblas<t>gemvStridedBatched() | [77](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=77) | 70 | [文本](../../generated/text/mcblas-v05/page-0077.txt) |
| 2 | mcBLAS Level-3函数 | [81](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=81) | 74 | [文本](../../generated/text/mcblas-v05/page-0081.txt) |
| 3 | mcblas<t>gemm() | [81](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=81) | 74 | [文本](../../generated/text/mcblas-v05/page-0081.txt) |
| 3 | mcblas<t>gemm3m() | [83](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=83) | 76 | [文本](../../generated/text/mcblas-v05/page-0083.txt) |
| 3 | mcblas<t>gemmBatched() | [85](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=85) | 78 | [文本](../../generated/text/mcblas-v05/page-0085.txt) |
| 3 | mcblas<t>gemmStridedBatched() | [88](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=88) | 81 | [文本](../../generated/text/mcblas-v05/page-0088.txt) |
| 3 | mcblas<t>symm() | [92](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=92) | 85 | [文本](../../generated/text/mcblas-v05/page-0092.txt) |
| 3 | mcblas<t>syrk() | [94](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=94) | 87 | [文本](../../generated/text/mcblas-v05/page-0094.txt) |
| 3 | mcblas<t>syr2k() | [96](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=96) | 89 | [文本](../../generated/text/mcblas-v05/page-0096.txt) |
| 3 | mcblas<t>syrkx() | [98](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=98) | 91 | [文本](../../generated/text/mcblas-v05/page-0098.txt) |
| 3 | mcblas<t>trmm() | [100](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=100) | 93 | [文本](../../generated/text/mcblas-v05/page-0100.txt) |
| 3 | mcblas<t>trsm() | [102](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=102) | 95 | [文本](../../generated/text/mcblas-v05/page-0102.txt) |
| 3 | mcblas<t>trsmBatched() | [105](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=105) | 98 | [文本](../../generated/text/mcblas-v05/page-0105.txt) |
| 3 | mcblas<t>hemm() | [108](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=108) | 101 | [文本](../../generated/text/mcblas-v05/page-0108.txt) |
| 3 | mcblas<t>herk() | [110](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=110) | 103 | [文本](../../generated/text/mcblas-v05/page-0110.txt) |
| 3 | mcblas<t>her2k() | [111](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=111) | 104 | [文本](../../generated/text/mcblas-v05/page-0111.txt) |
| 3 | mcblas<t>herkx() | [113](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=113) | 106 | [文本](../../generated/text/mcblas-v05/page-0113.txt) |
| 2 | BLAS-Like扩展函数 | [115](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=115) | 108 | [文本](../../generated/text/mcblas-v05/page-0115.txt) |
| 3 | mcblas<t>geam() | [115](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=115) | 108 | [文本](../../generated/text/mcblas-v05/page-0115.txt) |
| 3 | mcblas<t>dgmm() | [118](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=118) | 111 | [文本](../../generated/text/mcblas-v05/page-0118.txt) |
| 3 | mcblas<t>getrfBatched() | [120](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=120) | 113 | [文本](../../generated/text/mcblas-v05/page-0120.txt) |
| 3 | mcblas<t>getrsBatched() | [122](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=122) | 115 | [文本](../../generated/text/mcblas-v05/page-0122.txt) |
| 3 | mcblas<t>getriBatched() | [125](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=125) | 118 | [文本](../../generated/text/mcblas-v05/page-0125.txt) |
| 3 | mcblas<t>matinvBatched() | [127](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=127) | 120 | [文本](../../generated/text/mcblas-v05/page-0127.txt) |
| 3 | mcblas<t>geqrfBatched() | [129](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=129) | 122 | [文本](../../generated/text/mcblas-v05/page-0129.txt) |
| 3 | mcblas<t>gelsBatched() | [130](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=130) | 123 | [文本](../../generated/text/mcblas-v05/page-0130.txt) |
| 3 | mcblas<t>tpttr() | [133](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=133) | 126 | [文本](../../generated/text/mcblas-v05/page-0133.txt) |
| 3 | mcblas<t>trttp() | [134](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=134) | 127 | [文本](../../generated/text/mcblas-v05/page-0134.txt) |
| 3 | mcblas<t>gemmEx() | [136](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=136) | 129 | [文本](../../generated/text/mcblas-v05/page-0136.txt) |
| 3 | mcblasGemmEx() | [139](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=139) | 132 | [文本](../../generated/text/mcblas-v05/page-0139.txt) |
| 3 | mcblasGemmBatchedEx() | [142](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=142) | 135 | [文本](../../generated/text/mcblas-v05/page-0142.txt) |
| 3 | mcblasGemmStridedBatchedEx() | [147](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=147) | 140 | [文本](../../generated/text/mcblas-v05/page-0147.txt) |
| 3 | mcblasCsyrkEx() | [152](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=152) | 145 | [文本](../../generated/text/mcblas-v05/page-0152.txt) |
| 3 | mcblasCsyrk3mEx() | [154](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=154) | 147 | [文本](../../generated/text/mcblas-v05/page-0154.txt) |
| 3 | mcblasCherkEx() | [156](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=156) | 149 | [文本](../../generated/text/mcblas-v05/page-0156.txt) |
| 3 | mcblasCherk3mEx() | [158](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=158) | 151 | [文本](../../generated/text/mcblas-v05/page-0158.txt) |
| 3 | mcblasNrm2Ex() | [160](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=160) | 153 | [文本](../../generated/text/mcblas-v05/page-0160.txt) |
| 3 | mcblasAxpyEx() | [162](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=162) | 155 | [文本](../../generated/text/mcblas-v05/page-0162.txt) |
| 3 | mcblasDotEx() | [163](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=163) | 156 | [文本](../../generated/text/mcblas-v05/page-0163.txt) |
| 3 | mcblasRotEx() | [165](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=165) | 158 | [文本](../../generated/text/mcblas-v05/page-0165.txt) |
| 3 | mcblasScalEx() | [166](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_mcBLAS%20API%E5%8F%82%E8%80%83_CN_V05.pdf#page=166) | 159 | [文本](../../generated/text/mcblas-v05/page-0166.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/mcblas-v05/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/mcblas-v05/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/mcblas-v05/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/mcblas-v05/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/mcblas-v05/page-0005.txt)
- [PDF 6 / 标签 iv](../../generated/text/mcblas-v05/page-0006.txt)
- [PDF 7 / 标签 v](../../generated/text/mcblas-v05/page-0007.txt)
- [PDF 8 / 标签 1](../../generated/text/mcblas-v05/page-0008.txt)
- [PDF 9 / 标签 2](../../generated/text/mcblas-v05/page-0009.txt)
- [PDF 10 / 标签 3](../../generated/text/mcblas-v05/page-0010.txt)
- [PDF 11 / 标签 4](../../generated/text/mcblas-v05/page-0011.txt)
- [PDF 12 / 标签 5](../../generated/text/mcblas-v05/page-0012.txt)
- [PDF 13 / 标签 6](../../generated/text/mcblas-v05/page-0013.txt)
- [PDF 14 / 标签 7](../../generated/text/mcblas-v05/page-0014.txt)
- [PDF 15 / 标签 8](../../generated/text/mcblas-v05/page-0015.txt)
- [PDF 16 / 标签 9](../../generated/text/mcblas-v05/page-0016.txt)
- [PDF 17 / 标签 10](../../generated/text/mcblas-v05/page-0017.txt)
- [PDF 18 / 标签 11](../../generated/text/mcblas-v05/page-0018.txt)
- [PDF 19 / 标签 12](../../generated/text/mcblas-v05/page-0019.txt)
- [PDF 20 / 标签 13](../../generated/text/mcblas-v05/page-0020.txt)
- [PDF 21 / 标签 14](../../generated/text/mcblas-v05/page-0021.txt)
- [PDF 22 / 标签 15](../../generated/text/mcblas-v05/page-0022.txt)
- [PDF 23 / 标签 16](../../generated/text/mcblas-v05/page-0023.txt)
- [PDF 24 / 标签 17](../../generated/text/mcblas-v05/page-0024.txt)
- [PDF 25 / 标签 18](../../generated/text/mcblas-v05/page-0025.txt)
- [PDF 26 / 标签 19](../../generated/text/mcblas-v05/page-0026.txt)
- [PDF 27 / 标签 20](../../generated/text/mcblas-v05/page-0027.txt)
- [PDF 28 / 标签 21](../../generated/text/mcblas-v05/page-0028.txt)
- [PDF 29 / 标签 22](../../generated/text/mcblas-v05/page-0029.txt)
- [PDF 30 / 标签 23](../../generated/text/mcblas-v05/page-0030.txt)
- [PDF 31 / 标签 24](../../generated/text/mcblas-v05/page-0031.txt)
- [PDF 32 / 标签 25](../../generated/text/mcblas-v05/page-0032.txt)
- [PDF 33 / 标签 26](../../generated/text/mcblas-v05/page-0033.txt)
- [PDF 34 / 标签 27](../../generated/text/mcblas-v05/page-0034.txt)
- [PDF 35 / 标签 28](../../generated/text/mcblas-v05/page-0035.txt)
- [PDF 36 / 标签 29](../../generated/text/mcblas-v05/page-0036.txt)
- [PDF 37 / 标签 30](../../generated/text/mcblas-v05/page-0037.txt)
- [PDF 38 / 标签 31](../../generated/text/mcblas-v05/page-0038.txt)
- [PDF 39 / 标签 32](../../generated/text/mcblas-v05/page-0039.txt)
- [PDF 40 / 标签 33](../../generated/text/mcblas-v05/page-0040.txt)
- [PDF 41 / 标签 34](../../generated/text/mcblas-v05/page-0041.txt)
- [PDF 42 / 标签 35](../../generated/text/mcblas-v05/page-0042.txt)
- [PDF 43 / 标签 36](../../generated/text/mcblas-v05/page-0043.txt)
- [PDF 44 / 标签 37](../../generated/text/mcblas-v05/page-0044.txt)
- [PDF 45 / 标签 38](../../generated/text/mcblas-v05/page-0045.txt)
- [PDF 46 / 标签 39](../../generated/text/mcblas-v05/page-0046.txt)
- [PDF 47 / 标签 40](../../generated/text/mcblas-v05/page-0047.txt)
- [PDF 48 / 标签 41](../../generated/text/mcblas-v05/page-0048.txt)
- [PDF 49 / 标签 42](../../generated/text/mcblas-v05/page-0049.txt)
- [PDF 50 / 标签 43](../../generated/text/mcblas-v05/page-0050.txt)
- [PDF 51 / 标签 44](../../generated/text/mcblas-v05/page-0051.txt)
- [PDF 52 / 标签 45](../../generated/text/mcblas-v05/page-0052.txt)
- [PDF 53 / 标签 46](../../generated/text/mcblas-v05/page-0053.txt)
- [PDF 54 / 标签 47](../../generated/text/mcblas-v05/page-0054.txt)
- [PDF 55 / 标签 48](../../generated/text/mcblas-v05/page-0055.txt)
- [PDF 56 / 标签 49](../../generated/text/mcblas-v05/page-0056.txt)
- [PDF 57 / 标签 50](../../generated/text/mcblas-v05/page-0057.txt)
- [PDF 58 / 标签 51](../../generated/text/mcblas-v05/page-0058.txt)
- [PDF 59 / 标签 52](../../generated/text/mcblas-v05/page-0059.txt)
- [PDF 60 / 标签 53](../../generated/text/mcblas-v05/page-0060.txt)
- [PDF 61 / 标签 54](../../generated/text/mcblas-v05/page-0061.txt)
- [PDF 62 / 标签 55](../../generated/text/mcblas-v05/page-0062.txt)
- [PDF 63 / 标签 56](../../generated/text/mcblas-v05/page-0063.txt)
- [PDF 64 / 标签 57](../../generated/text/mcblas-v05/page-0064.txt)
- [PDF 65 / 标签 58](../../generated/text/mcblas-v05/page-0065.txt)
- [PDF 66 / 标签 59](../../generated/text/mcblas-v05/page-0066.txt)
- [PDF 67 / 标签 60](../../generated/text/mcblas-v05/page-0067.txt)
- [PDF 68 / 标签 61](../../generated/text/mcblas-v05/page-0068.txt)
- [PDF 69 / 标签 62](../../generated/text/mcblas-v05/page-0069.txt)
- [PDF 70 / 标签 63](../../generated/text/mcblas-v05/page-0070.txt)
- [PDF 71 / 标签 64](../../generated/text/mcblas-v05/page-0071.txt)
- [PDF 72 / 标签 65](../../generated/text/mcblas-v05/page-0072.txt)
- [PDF 73 / 标签 66](../../generated/text/mcblas-v05/page-0073.txt)
- [PDF 74 / 标签 67](../../generated/text/mcblas-v05/page-0074.txt)
- [PDF 75 / 标签 68](../../generated/text/mcblas-v05/page-0075.txt)
- [PDF 76 / 标签 69](../../generated/text/mcblas-v05/page-0076.txt)
- [PDF 77 / 标签 70](../../generated/text/mcblas-v05/page-0077.txt)
- [PDF 78 / 标签 71](../../generated/text/mcblas-v05/page-0078.txt)
- [PDF 79 / 标签 72](../../generated/text/mcblas-v05/page-0079.txt)
- [PDF 80 / 标签 73](../../generated/text/mcblas-v05/page-0080.txt)
- [PDF 81 / 标签 74](../../generated/text/mcblas-v05/page-0081.txt)
- [PDF 82 / 标签 75](../../generated/text/mcblas-v05/page-0082.txt)
- [PDF 83 / 标签 76](../../generated/text/mcblas-v05/page-0083.txt)
- [PDF 84 / 标签 77](../../generated/text/mcblas-v05/page-0084.txt)
- [PDF 85 / 标签 78](../../generated/text/mcblas-v05/page-0085.txt)
- [PDF 86 / 标签 79](../../generated/text/mcblas-v05/page-0086.txt)
- [PDF 87 / 标签 80](../../generated/text/mcblas-v05/page-0087.txt)
- [PDF 88 / 标签 81](../../generated/text/mcblas-v05/page-0088.txt)
- [PDF 89 / 标签 82](../../generated/text/mcblas-v05/page-0089.txt)
- [PDF 90 / 标签 83](../../generated/text/mcblas-v05/page-0090.txt)
- [PDF 91 / 标签 84](../../generated/text/mcblas-v05/page-0091.txt)
- [PDF 92 / 标签 85](../../generated/text/mcblas-v05/page-0092.txt)
- [PDF 93 / 标签 86](../../generated/text/mcblas-v05/page-0093.txt)
- [PDF 94 / 标签 87](../../generated/text/mcblas-v05/page-0094.txt)
- [PDF 95 / 标签 88](../../generated/text/mcblas-v05/page-0095.txt)
- [PDF 96 / 标签 89](../../generated/text/mcblas-v05/page-0096.txt)
- [PDF 97 / 标签 90](../../generated/text/mcblas-v05/page-0097.txt)
- [PDF 98 / 标签 91](../../generated/text/mcblas-v05/page-0098.txt)
- [PDF 99 / 标签 92](../../generated/text/mcblas-v05/page-0099.txt)
- [PDF 100 / 标签 93](../../generated/text/mcblas-v05/page-0100.txt)
- [PDF 101 / 标签 94](../../generated/text/mcblas-v05/page-0101.txt)
- [PDF 102 / 标签 95](../../generated/text/mcblas-v05/page-0102.txt)
- [PDF 103 / 标签 96](../../generated/text/mcblas-v05/page-0103.txt)
- [PDF 104 / 标签 97](../../generated/text/mcblas-v05/page-0104.txt)
- [PDF 105 / 标签 98](../../generated/text/mcblas-v05/page-0105.txt)
- [PDF 106 / 标签 99](../../generated/text/mcblas-v05/page-0106.txt)
- [PDF 107 / 标签 100](../../generated/text/mcblas-v05/page-0107.txt)
- [PDF 108 / 标签 101](../../generated/text/mcblas-v05/page-0108.txt)
- [PDF 109 / 标签 102](../../generated/text/mcblas-v05/page-0109.txt)
- [PDF 110 / 标签 103](../../generated/text/mcblas-v05/page-0110.txt)
- [PDF 111 / 标签 104](../../generated/text/mcblas-v05/page-0111.txt)
- [PDF 112 / 标签 105](../../generated/text/mcblas-v05/page-0112.txt)
- [PDF 113 / 标签 106](../../generated/text/mcblas-v05/page-0113.txt)
- [PDF 114 / 标签 107](../../generated/text/mcblas-v05/page-0114.txt)
- [PDF 115 / 标签 108](../../generated/text/mcblas-v05/page-0115.txt)
- [PDF 116 / 标签 109](../../generated/text/mcblas-v05/page-0116.txt)
- [PDF 117 / 标签 110](../../generated/text/mcblas-v05/page-0117.txt)
- [PDF 118 / 标签 111](../../generated/text/mcblas-v05/page-0118.txt)
- [PDF 119 / 标签 112](../../generated/text/mcblas-v05/page-0119.txt)
- [PDF 120 / 标签 113](../../generated/text/mcblas-v05/page-0120.txt)
- [PDF 121 / 标签 114](../../generated/text/mcblas-v05/page-0121.txt)
- [PDF 122 / 标签 115](../../generated/text/mcblas-v05/page-0122.txt)
- [PDF 123 / 标签 116](../../generated/text/mcblas-v05/page-0123.txt)
- [PDF 124 / 标签 117](../../generated/text/mcblas-v05/page-0124.txt)
- [PDF 125 / 标签 118](../../generated/text/mcblas-v05/page-0125.txt)
- [PDF 126 / 标签 119](../../generated/text/mcblas-v05/page-0126.txt)
- [PDF 127 / 标签 120](../../generated/text/mcblas-v05/page-0127.txt)
- [PDF 128 / 标签 121](../../generated/text/mcblas-v05/page-0128.txt)
- [PDF 129 / 标签 122](../../generated/text/mcblas-v05/page-0129.txt)
- [PDF 130 / 标签 123](../../generated/text/mcblas-v05/page-0130.txt)
- [PDF 131 / 标签 124](../../generated/text/mcblas-v05/page-0131.txt)
- [PDF 132 / 标签 125](../../generated/text/mcblas-v05/page-0132.txt)
- [PDF 133 / 标签 126](../../generated/text/mcblas-v05/page-0133.txt)
- [PDF 134 / 标签 127](../../generated/text/mcblas-v05/page-0134.txt)
- [PDF 135 / 标签 128](../../generated/text/mcblas-v05/page-0135.txt)
- [PDF 136 / 标签 129](../../generated/text/mcblas-v05/page-0136.txt)
- [PDF 137 / 标签 130](../../generated/text/mcblas-v05/page-0137.txt)
- [PDF 138 / 标签 131](../../generated/text/mcblas-v05/page-0138.txt)
- [PDF 139 / 标签 132](../../generated/text/mcblas-v05/page-0139.txt)
- [PDF 140 / 标签 133](../../generated/text/mcblas-v05/page-0140.txt)
- [PDF 141 / 标签 134](../../generated/text/mcblas-v05/page-0141.txt)
- [PDF 142 / 标签 135](../../generated/text/mcblas-v05/page-0142.txt)
- [PDF 143 / 标签 136](../../generated/text/mcblas-v05/page-0143.txt)
- [PDF 144 / 标签 137](../../generated/text/mcblas-v05/page-0144.txt)
- [PDF 145 / 标签 138](../../generated/text/mcblas-v05/page-0145.txt)
- [PDF 146 / 标签 139](../../generated/text/mcblas-v05/page-0146.txt)
- [PDF 147 / 标签 140](../../generated/text/mcblas-v05/page-0147.txt)
- [PDF 148 / 标签 141](../../generated/text/mcblas-v05/page-0148.txt)
- [PDF 149 / 标签 142](../../generated/text/mcblas-v05/page-0149.txt)
- [PDF 150 / 标签 143](../../generated/text/mcblas-v05/page-0150.txt)
- [PDF 151 / 标签 144](../../generated/text/mcblas-v05/page-0151.txt)
- [PDF 152 / 标签 145](../../generated/text/mcblas-v05/page-0152.txt)
- [PDF 153 / 标签 146](../../generated/text/mcblas-v05/page-0153.txt)
- [PDF 154 / 标签 147](../../generated/text/mcblas-v05/page-0154.txt)
- [PDF 155 / 标签 148](../../generated/text/mcblas-v05/page-0155.txt)
- [PDF 156 / 标签 149](../../generated/text/mcblas-v05/page-0156.txt)
- [PDF 157 / 标签 150](../../generated/text/mcblas-v05/page-0157.txt)
- [PDF 158 / 标签 151](../../generated/text/mcblas-v05/page-0158.txt)
- [PDF 159 / 标签 152](../../generated/text/mcblas-v05/page-0159.txt)
- [PDF 160 / 标签 153](../../generated/text/mcblas-v05/page-0160.txt)
- [PDF 161 / 标签 154](../../generated/text/mcblas-v05/page-0161.txt)
- [PDF 162 / 标签 155](../../generated/text/mcblas-v05/page-0162.txt)
- [PDF 163 / 标签 156](../../generated/text/mcblas-v05/page-0163.txt)
- [PDF 164 / 标签 157](../../generated/text/mcblas-v05/page-0164.txt)
- [PDF 165 / 标签 158](../../generated/text/mcblas-v05/page-0165.txt)
- [PDF 166 / 标签 159](../../generated/text/mcblas-v05/page-0166.txt)
- [PDF 167 / 标签 160](../../generated/text/mcblas-v05/page-0167.txt)
