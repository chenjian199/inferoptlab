# 沐曦通用GPU_MXMACA编译器内建函数编程指南

文档 ID：`builtins-v01`；文档修订：V01；发布日期：2026-08-03。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf)

SHA256：`80dfb3a83381e48e19968b432d4eb24d37c505bd711af14f74889277cffc3835`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

未从“适用产品”书签识别到明确说明，不能据此推断支持或不支持 C500。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

未自动定位到候选页，请检索全文。

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=7) | 1 | [文本](../../generated/text/builtins-v01/page-0007.txt) |
| 1 | 类型定义 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=8) | 2 | [文本](../../generated/text/builtins-v01/page-0008.txt) |
| 1 | 接口介绍 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=9) | 3 | [文本](../../generated/text/builtins-v01/page-0009.txt) |
| 2 | 访存函数 | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=9) | 3 | [文本](../../generated/text/builtins-v01/page-0009.txt) |
| 3 | __builtin_mxc_ldg_*_predicator | [9](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=9) | 3 | [文本](../../generated/text/builtins-v01/page-0009.txt) |
| 3 | __builtin_mxc_stg_*_predicator | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=11) | 5 | [文本](../../generated/text/builtins-v01/page-0011.txt) |
| 3 | __builtin_mxc_ldg_*_predicator_ret | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=13) | 7 | [文本](../../generated/text/builtins-v01/page-0013.txt) |
| 3 | __builtin_mxc_ldg_*_bsm | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=15) | 9 | [文本](../../generated/text/builtins-v01/page-0015.txt) |
| 3 | __builtin_mxc_load_shared_trans_* | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=16) | 10 | [文本](../../generated/text/builtins-v01/page-0016.txt) |
| 3 | __builtin_mxc_arrive | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=16) | 10 | [文本](../../generated/text/builtins-v01/page-0016.txt) |
| 3 | __builtin_mxc_arrive_gvmcnt | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=17) | 11 | [文本](../../generated/text/builtins-v01/page-0017.txt) |
| 3 | __builtin_mxc_arrive_bsmcnt | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=18) | 12 | [文本](../../generated/text/builtins-v01/page-0018.txt) |
| 3 | __builtin_mxc_barrier_ex | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=18) | 12 | [文本](../../generated/text/builtins-v01/page-0018.txt) |
| 3 | __builtin_mxc_barrier_and_wait* | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=19) | 13 | [文本](../../generated/text/builtins-v01/page-0019.txt) |
| 2 | 比较函数 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=21) | 15 | [文本](../../generated/text/builtins-v01/page-0021.txt) |
| 3 | __builtin_mxc_uicmp* | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=21) | 15 | [文本](../../generated/text/builtins-v01/page-0021.txt) |
| 3 | __builtin_mxc_sicmp* | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=22) | 16 | [文本](../../generated/text/builtins-v01/page-0022.txt) |
| 3 | __builtin_mxc_fcmp* | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=22) | 16 | [文本](../../generated/text/builtins-v01/page-0022.txt) |
| 2 | 类型转换函数 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=23) | 17 | [文本](../../generated/text/builtins-v01/page-0023.txt) |
| 3 | __builtin_mxc_cvt_f32totf32 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=23) | 17 | [文本](../../generated/text/builtins-v01/page-0023.txt) |
| 3 | __builtin_mxc_cvt_pk_f32tou8 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=24) | 18 | [文本](../../generated/text/builtins-v01/page-0024.txt) |
| 3 | __builtin_mxc_b*_cast_to_f32 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=24) | 18 | [文本](../../generated/text/builtins-v01/page-0024.txt) |
| 2 | 混洗函数 | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=25) | 19 | [文本](../../generated/text/builtins-v01/page-0025.txt) |
| 3 | __builtin_mxc_mov_shfl | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=25) | 19 | [文本](../../generated/text/builtins-v01/page-0025.txt) |
| 3 | __builtin_mxc_update_shfl | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=27) | 21 | [文本](../../generated/text/builtins-v01/page-0027.txt) |
| 3 | __builtin_mxc_bsm_bpermute | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=28) | 22 | [文本](../../generated/text/builtins-v01/page-0028.txt) |
| 3 | __builtin_mxc_bsm_permute | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=29) | 23 | [文本](../../generated/text/builtins-v01/page-0029.txt) |
| 3 | __builtin_mxc_byte_perm | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=30) | 24 | [文本](../../generated/text/builtins-v01/page-0030.txt) |
| 2 | 浮点乘加函数 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=31) | 25 | [文本](../../generated/text/builtins-v01/page-0031.txt) |
| 3 | __builtin_mxc_pk_fma_f32 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=31) | 25 | [文本](../../generated/text/builtins-v01/page-0031.txt) |
| 3 | __builtin_mxc_pk_fma_bf16 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=31) | 25 | [文本](../../generated/text/builtins-v01/page-0031.txt) |
| 3 | __builtin_mxc_pk_fma_f16 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=32) | 26 | [文本](../../generated/text/builtins-v01/page-0032.txt) |
| 3 | __builtin_mxc_fma_bf16 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=32) | 26 | [文本](../../generated/text/builtins-v01/page-0032.txt) |
| 2 | 矩阵乘加函数 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=32) | 26 | [文本](../../generated/text/builtins-v01/page-0032.txt) |
| 3 | __builtin_mxc_mma_16x16x16f16 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=32) | 26 | [文本](../../generated/text/builtins-v01/page-0032.txt) |
| 3 | __builtin_mxc_mma_16x16x4f32 | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=33) | 27 | [文本](../../generated/text/builtins-v01/page-0033.txt) |
| 3 | __builtin_mxc_mma_16x16x16i8 | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=34) | 28 | [文本](../../generated/text/builtins-v01/page-0034.txt) |
| 3 | __builtin_mxc_mma_16x16x32i8 | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=35) | 29 | [文本](../../generated/text/builtins-v01/page-0035.txt) |
| 3 | __builtin_mxc_mma_16x16x16bf16 | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=35) | 29 | [文本](../../generated/text/builtins-v01/page-0035.txt) |
| 3 | __builtin_mxc_mma_16x16x4f64 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=36) | 30 | [文本](../../generated/text/builtins-v01/page-0036.txt) |
| 3 | __builtin_mxc_mma_16x16x8tf32 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=37) | 31 | [文本](../../generated/text/builtins-v01/page-0037.txt) |
| 2 | 常用计算函数 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=37) | 31 | [文本](../../generated/text/builtins-v01/page-0037.txt) |
| 3 | __builtin_mxc_mad_wide_i32/u32 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=37) | 31 | [文本](../../generated/text/builtins-v01/page-0037.txt) |
| 3 | __builtin_mxc_pk_mul_f32 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=38) | 32 | [文本](../../generated/text/builtins-v01/page-0038.txt) |
| 3 | __builtin_mxc_pk_add_f32 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=38) | 32 | [文本](../../generated/text/builtins-v01/page-0038.txt) |
| 3 | __builtin_mxc_ubfe | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=39) | 33 | [文本](../../generated/text/builtins-v01/page-0039.txt) |
| 3 | __builtin_mxc_sbfe | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=40) | 34 | [文本](../../generated/text/builtins-v01/page-0040.txt) |
| 3 | __builtin_mxc_alignbit | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=40) | 34 | [文本](../../generated/text/builtins-v01/page-0040.txt) |
| 3 | __builtin_mxc_cos* | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=41) | 35 | [文本](../../generated/text/builtins-v01/page-0041.txt) |
| 3 | __builtin_mxc_sin* | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=41) | 35 | [文本](../../generated/text/builtins-v01/page-0041.txt) |
| 3 | __builtin_mxc_rcp* | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=42) | 36 | [文本](../../generated/text/builtins-v01/page-0042.txt) |
| 3 | __builtin_mxc_sqrt* | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=42) | 36 | [文本](../../generated/text/builtins-v01/page-0042.txt) |
| 3 | __builtin_mxc_rsq* | [42](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=42) | 36 | [文本](../../generated/text/builtins-v01/page-0042.txt) |
| 3 | __builtin_mxc_log_clampf | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=43) | 37 | [文本](../../generated/text/builtins-v01/page-0043.txt) |
| 2 | 其他 | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=43) | 37 | [文本](../../generated/text/builtins-v01/page-0043.txt) |
| 3 | __builtin_mxc_get_time | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=43) | 37 | [文本](../../generated/text/builtins-v01/page-0043.txt) |
| 3 | __builtin_mxc_read_xmsk | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=44) | 38 | [文本](../../generated/text/builtins-v01/page-0044.txt) |
| 3 | __builtin_mxc_readfirstlane | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=44) | 38 | [文本](../../generated/text/builtins-v01/page-0044.txt) |
| 3 | __builtin_mxc_readlane | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=44) | 38 | [文本](../../generated/text/builtins-v01/page-0044.txt) |
| 3 | __builtin_mxc_writelane | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=45) | 39 | [文本](../../generated/text/builtins-v01/page-0045.txt) |
| 3 | __builtin_mxc_nop | [46](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%E7%BC%96%E8%AF%91%E5%99%A8%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0%E7%BC%96%E7%A8%8B%E6%8C%87%E5%8D%97_CN_V01.pdf#page=46) | 40 | [文本](../../generated/text/builtins-v01/page-0046.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/builtins-v01/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/builtins-v01/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/builtins-v01/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/builtins-v01/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/builtins-v01/page-0005.txt)
- [PDF 6 / 标签 vi](../../generated/text/builtins-v01/page-0006.txt)
- [PDF 7 / 标签 1](../../generated/text/builtins-v01/page-0007.txt)
- [PDF 8 / 标签 2](../../generated/text/builtins-v01/page-0008.txt)
- [PDF 9 / 标签 3](../../generated/text/builtins-v01/page-0009.txt)
- [PDF 10 / 标签 4](../../generated/text/builtins-v01/page-0010.txt)
- [PDF 11 / 标签 5](../../generated/text/builtins-v01/page-0011.txt)
- [PDF 12 / 标签 6](../../generated/text/builtins-v01/page-0012.txt)
- [PDF 13 / 标签 7](../../generated/text/builtins-v01/page-0013.txt)
- [PDF 14 / 标签 8](../../generated/text/builtins-v01/page-0014.txt)
- [PDF 15 / 标签 9](../../generated/text/builtins-v01/page-0015.txt)
- [PDF 16 / 标签 10](../../generated/text/builtins-v01/page-0016.txt)
- [PDF 17 / 标签 11](../../generated/text/builtins-v01/page-0017.txt)
- [PDF 18 / 标签 12](../../generated/text/builtins-v01/page-0018.txt)
- [PDF 19 / 标签 13](../../generated/text/builtins-v01/page-0019.txt)
- [PDF 20 / 标签 14](../../generated/text/builtins-v01/page-0020.txt)
- [PDF 21 / 标签 15](../../generated/text/builtins-v01/page-0021.txt)
- [PDF 22 / 标签 16](../../generated/text/builtins-v01/page-0022.txt)
- [PDF 23 / 标签 17](../../generated/text/builtins-v01/page-0023.txt)
- [PDF 24 / 标签 18](../../generated/text/builtins-v01/page-0024.txt)
- [PDF 25 / 标签 19](../../generated/text/builtins-v01/page-0025.txt)
- [PDF 26 / 标签 20](../../generated/text/builtins-v01/page-0026.txt)
- [PDF 27 / 标签 21](../../generated/text/builtins-v01/page-0027.txt)
- [PDF 28 / 标签 22](../../generated/text/builtins-v01/page-0028.txt)
- [PDF 29 / 标签 23](../../generated/text/builtins-v01/page-0029.txt)
- [PDF 30 / 标签 24](../../generated/text/builtins-v01/page-0030.txt)
- [PDF 31 / 标签 25](../../generated/text/builtins-v01/page-0031.txt)
- [PDF 32 / 标签 26](../../generated/text/builtins-v01/page-0032.txt)
- [PDF 33 / 标签 27](../../generated/text/builtins-v01/page-0033.txt)
- [PDF 34 / 标签 28](../../generated/text/builtins-v01/page-0034.txt)
- [PDF 35 / 标签 29](../../generated/text/builtins-v01/page-0035.txt)
- [PDF 36 / 标签 30](../../generated/text/builtins-v01/page-0036.txt)
- [PDF 37 / 标签 31](../../generated/text/builtins-v01/page-0037.txt)
- [PDF 38 / 标签 32](../../generated/text/builtins-v01/page-0038.txt)
- [PDF 39 / 标签 33](../../generated/text/builtins-v01/page-0039.txt)
- [PDF 40 / 标签 34](../../generated/text/builtins-v01/page-0040.txt)
- [PDF 41 / 标签 35](../../generated/text/builtins-v01/page-0041.txt)
- [PDF 42 / 标签 36](../../generated/text/builtins-v01/page-0042.txt)
- [PDF 43 / 标签 37](../../generated/text/builtins-v01/page-0043.txt)
- [PDF 44 / 标签 38](../../generated/text/builtins-v01/page-0044.txt)
- [PDF 45 / 标签 39](../../generated/text/builtins-v01/page-0045.txt)
- [PDF 46 / 标签 40](../../generated/text/builtins-v01/page-0046.txt)
