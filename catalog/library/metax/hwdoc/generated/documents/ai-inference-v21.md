# 沐曦通用GPU_AI推理用户手册

文档 ID：`ai-inference-v21`；文档修订：V21；发布日期：2026-07-06。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf)

SHA256：`dccf0337eb99006d63db4b6f37938b250473ddd1ba8971dd78b0cfd9582b041d`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 14 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=14)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260，曦
> 索 ® X206；以及 MXC600 系列产品：曦云 ® C600，曦思 ® N300，曦索 ® X301、X302。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 15 页（标签 3）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=15) · [逐页文本](../../generated/text/ai-inference-v21/page-0015.txt)
- [PDF 第 25 页（标签 13）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=25) · [逐页文本](../../generated/text/ai-inference-v21/page-0025.txt)
- [PDF 第 30 页（标签 18）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=30) · [逐页文本](../../generated/text/ai-inference-v21/page-0030.txt)
- [PDF 第 37 页（标签 25）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=37) · [逐页文本](../../generated/text/ai-inference-v21/page-0037.txt)
- [PDF 第 39 页（标签 27）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=39) · [逐页文本](../../generated/text/ai-inference-v21/page-0039.txt)
- [PDF 第 41 页（标签 29）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=41) · [逐页文本](../../generated/text/ai-inference-v21/page-0041.txt)
- [PDF 第 46 页（标签 34）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=46) · [逐页文本](../../generated/text/ai-inference-v21/page-0046.txt)
- [PDF 第 52 页（标签 40）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=52) · [逐页文本](../../generated/text/ai-inference-v21/page-0052.txt)
- [PDF 第 54 页（标签 42）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=54) · [逐页文本](../../generated/text/ai-inference-v21/page-0054.txt)
- [PDF 第 56 页（标签 44）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=56) · [逐页文本](../../generated/text/ai-inference-v21/page-0056.txt)
- [PDF 第 58 页（标签 46）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=58) · [逐页文本](../../generated/text/ai-inference-v21/page-0058.txt)
- [PDF 第 59 页（标签 47）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=59) · [逐页文本](../../generated/text/ai-inference-v21/page-0059.txt)
- [PDF 第 62 页（标签 50）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=62) · [逐页文本](../../generated/text/ai-inference-v21/page-0062.txt)
- [PDF 第 63 页（标签 51）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=63) · [逐页文本](../../generated/text/ai-inference-v21/page-0063.txt)
- [PDF 第 66 页（标签 54）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=66) · [逐页文本](../../generated/text/ai-inference-v21/page-0066.txt)
- [PDF 第 67 页（标签 55）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=67) · [逐页文本](../../generated/text/ai-inference-v21/page-0067.txt)
- [PDF 第 75 页（标签 63）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=75) · [逐页文本](../../generated/text/ai-inference-v21/page-0075.txt)
- [PDF 第 76 页（标签 64）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=76) · [逐页文本](../../generated/text/ai-inference-v21/page-0076.txt)
- [PDF 第 82 页（标签 70）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) · [逐页文本](../../generated/text/ai-inference-v21/page-0082.txt)
- [PDF 第 87 页（标签 75）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=87) · [逐页文本](../../generated/text/ai-inference-v21/page-0087.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=13) | 1 | [文本](../../generated/text/ai-inference-v21/page-0013.txt) |
| 2 | MacaRT介绍 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=13) | 1 | [文本](../../generated/text/ai-inference-v21/page-0013.txt) |
| 2 | MacaRT功能 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=14) | 2 | [文本](../../generated/text/ai-inference-v21/page-0014.txt) |
| 2 | 适用产品 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=14) | 2 | [文本](../../generated/text/ai-inference-v21/page-0014.txt) |
| 1 | 环境依赖及MacaRT安装 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=15) | 3 | [文本](../../generated/text/ai-inference-v21/page-0015.txt) |
| 2 | 环境依赖 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=15) | 3 | [文本](../../generated/text/ai-inference-v21/page-0015.txt) |
| 2 | 安装MacaRT | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=15) | 3 | [文本](../../generated/text/ai-inference-v21/page-0015.txt) |
| 3 | MacaRT C++ | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=15) | 3 | [文本](../../generated/text/ai-inference-v21/page-0015.txt) |
| 3 | MacaRT Python | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=15) | 3 | [文本](../../generated/text/ai-inference-v21/page-0015.txt) |
| 2 | 使用MacaRT容器镜像 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=16) | 4 | [文本](../../generated/text/ai-inference-v21/page-0016.txt) |
| 1 | MacaRT C++ API | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=17) | 5 | [文本](../../generated/text/ai-inference-v21/page-0017.txt) |
| 2 | 部署ONNX模型 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=17) | 5 | [文本](../../generated/text/ai-inference-v21/page-0017.txt) |
| 3 | 创建Session | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=17) | 5 | [文本](../../generated/text/ai-inference-v21/page-0017.txt) |
| 3 | 获取模型图的输入输出信息 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=17) | 5 | [文本](../../generated/text/ai-inference-v21/page-0017.txt) |
| 3 | 构建模型输入Tensors | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=18) | 6 | [文本](../../generated/text/ai-inference-v21/page-0018.txt) |
| 3 | 获取模型输出Tensors | [18](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=18) | 6 | [文本](../../generated/text/ai-inference-v21/page-0018.txt) |
| 2 | 绑定输入输出设备 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=19) | 7 | [文本](../../generated/text/ai-inference-v21/page-0019.txt) |
| 3 | 绑定输入输出数据到可分页内存上 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=19) | 7 | [文本](../../generated/text/ai-inference-v21/page-0019.txt) |
| 3 | 绑定输入输出数据到固页内存上 | [19](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=19) | 7 | [文本](../../generated/text/ai-inference-v21/page-0019.txt) |
| 3 | 绑定输入输出数据到显存上 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=20) | 8 | [文本](../../generated/text/ai-inference-v21/page-0020.txt) |
| 2 | 动态Batch推理 | [21](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=21) | 9 | [文本](../../generated/text/ai-inference-v21/page-0021.txt) |
| 2 | 提升沐曦通用GPU推理性能 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=22) | 10 | [文本](../../generated/text/ai-inference-v21/page-0022.txt) |
| 3 | 设备ID | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=23) | 11 | [文本](../../generated/text/ai-inference-v21/page-0023.txt) |
| 3 | MacaRT显存管理 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=23) | 11 | [文本](../../generated/text/ai-inference-v21/page-0023.txt) |
| 2 | 自定义算子 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=23) | 11 | [文本](../../generated/text/ai-inference-v21/page-0023.txt) |
| 3 | Domain的定义 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=24) | 12 | [文本](../../generated/text/ai-inference-v21/page-0024.txt) |
| 3 | Kernel输入输出的数据排布 | [24](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=24) | 12 | [文本](../../generated/text/ai-inference-v21/page-0024.txt) |
| 1 | MacaRT Python API | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=25) | 13 | [文本](../../generated/text/ai-inference-v21/page-0025.txt) |
| 2 | 部署ONNX模型 | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=25) | 13 | [文本](../../generated/text/ai-inference-v21/page-0025.txt) |
| 3 | 创建Session | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=25) | 13 | [文本](../../generated/text/ai-inference-v21/page-0025.txt) |
| 3 | 获取模型图的输入输出信息 | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=25) | 13 | [文本](../../generated/text/ai-inference-v21/page-0025.txt) |
| 3 | 构建模型输入字典 | [25](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=25) | 13 | [文本](../../generated/text/ai-inference-v21/page-0025.txt) |
| 3 | 获取模型输出 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=26) | 14 | [文本](../../generated/text/ai-inference-v21/page-0026.txt) |
| 2 | 绑定输入输出设备 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=26) | 14 | [文本](../../generated/text/ai-inference-v21/page-0026.txt) |
| 3 | 绑定输入输出数据到可分页内存上 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=26) | 14 | [文本](../../generated/text/ai-inference-v21/page-0026.txt) |
| 3 | 绑定输入输出数据到固页内存上 | [26](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=26) | 14 | [文本](../../generated/text/ai-inference-v21/page-0026.txt) |
| 3 | 绑定输入输出数据到显存上 | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=27) | 15 | [文本](../../generated/text/ai-inference-v21/page-0027.txt) |
| 2 | 动态Batch推理 | [27](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=27) | 15 | [文本](../../generated/text/ai-inference-v21/page-0027.txt) |
| 2 | 提升沐曦通用GPU推理性能 | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=28) | 16 | [文本](../../generated/text/ai-inference-v21/page-0028.txt) |
| 3 | 设备ID设置 | [28](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=28) | 16 | [文本](../../generated/text/ai-inference-v21/page-0028.txt) |
| 1 | MacaRT工具链 | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=29) | 17 | [文本](../../generated/text/ai-inference-v21/page-0029.txt) |
| 2 | MacaConverter | [29](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=29) | 17 | [文本](../../generated/text/ai-inference-v21/page-0029.txt) |
| 3 | 安装 | [30](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=30) | 18 | [文本](../../generated/text/ai-inference-v21/page-0030.txt) |
| 3 | 功能列表 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=31) | 19 | [文本](../../generated/text/ai-inference-v21/page-0031.txt) |
| 3 | 使用说明 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=31) | 19 | [文本](../../generated/text/ai-inference-v21/page-0031.txt) |
| 4 | Caffe模型转ONNX模型 | [31](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=31) | 19 | [文本](../../generated/text/ai-inference-v21/page-0031.txt) |
| 4 | TensorFlow（H5）模型转ONNX模型 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=32) | 20 | [文本](../../generated/text/ai-inference-v21/page-0032.txt) |
| 4 | TensorFlow（SavedModel）模型转ONNX模型 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=32) | 20 | [文本](../../generated/text/ai-inference-v21/page-0032.txt) |
| 4 | TensorFlow（CheckPoint）模型转ONNX模型 | [32](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=32) | 20 | [文本](../../generated/text/ai-inference-v21/page-0032.txt) |
| 4 | TensorFlow（pb）模型转ONNX模型 | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=33) | 21 | [文本](../../generated/text/ai-inference-v21/page-0033.txt) |
| 4 | PyTorch模型转ONNX模型（输入包含模型定义和权重） | [33](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=33) | 21 | [文本](../../generated/text/ai-inference-v21/page-0033.txt) |
| 4 | PyTorch模型转ONNX模型（输入仅包含权重） | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=34) | 22 | [文本](../../generated/text/ai-inference-v21/page-0034.txt) |
| 4 | PyTorch模型转ONNX模型（输入仅包含权重，且模型定义在Torchvision中） | [34](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=34) | 22 | [文本](../../generated/text/ai-inference-v21/page-0034.txt) |
| 4 | Darknet模型转ONNX模型 | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=35) | 23 | [文本](../../generated/text/ai-inference-v21/page-0035.txt) |
| 4 | PaddlePaddle模型转ONNX模型（输入包含权重和定义） | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=35) | 23 | [文本](../../generated/text/ai-inference-v21/page-0035.txt) |
| 4 | PaddlePaddle模型转ONNX模型（输入仅包含权重） | [35](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=35) | 23 | [文本](../../generated/text/ai-inference-v21/page-0035.txt) |
| 4 | PaddlePaddle模型转ONNX模型（输入仅包含权重，模型在paddle.vision中定义） | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=36) | 24 | [文本](../../generated/text/ai-inference-v21/page-0036.txt) |
| 4 | 动态Batch转换 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=36) | 24 | [文本](../../generated/text/ai-inference-v21/page-0036.txt) |
| 4 | ONNX简化 | [36](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=36) | 24 | [文本](../../generated/text/ai-inference-v21/page-0036.txt) |
| 4 | FP32转FP16 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=37) | 25 | [文本](../../generated/text/ai-inference-v21/page-0037.txt) |
| 4 | 子图提取 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=37) | 25 | [文本](../../generated/text/ai-inference-v21/page-0037.txt) |
| 4 | op_set版本转换 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=37) | 25 | [文本](../../generated/text/ai-inference-v21/page-0037.txt) |
| 4 | Pad融合 | [37](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=37) | 25 | [文本](../../generated/text/ai-inference-v21/page-0037.txt) |
| 4 | Float32转Uint8（仅针对模型的input数据，非所有算子） | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=38) | 26 | [文本](../../generated/text/ai-inference-v21/page-0038.txt) |
| 4 | MatMul+Add融合为Gemm | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=38) | 26 | [文本](../../generated/text/ai-inference-v21/page-0038.txt) |
| 4 | MHA融合 | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=38) | 26 | [文本](../../generated/text/ai-inference-v21/page-0038.txt) |
| 2 | MacaPrecision | [38](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=38) | 26 | [文本](../../generated/text/ai-inference-v21/page-0038.txt) |
| 3 | 安装 | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=39) | 27 | [文本](../../generated/text/ai-inference-v21/page-0039.txt) |
| 3 | 使用说明 | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=39) | 27 | [文本](../../generated/text/ai-inference-v21/page-0039.txt) |
| 4 | 常规模型（FP32/FP16） | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=39) | 27 | [文本](../../generated/text/ai-inference-v21/page-0039.txt) |
| 5 | 全量模式 | [39](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=39) | 27 | [文本](../../generated/text/ai-inference-v21/page-0039.txt) |
| 5 | 指定模式 | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=40) | 28 | [文本](../../generated/text/ai-inference-v21/page-0040.txt) |
| 4 | 量化模型（经过MacaQuantizer量化后的模型） | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=40) | 28 | [文本](../../generated/text/ai-inference-v21/page-0040.txt) |
| 2 | MacaQuantizer | [40](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=40) | 28 | [文本](../../generated/text/ai-inference-v21/page-0040.txt) |
| 3 | 安装 | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=41) | 29 | [文本](../../generated/text/ai-inference-v21/page-0041.txt) |
| 3 | 使用说明 | [41](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=41) | 29 | [文本](../../generated/text/ai-inference-v21/page-0041.txt) |
| 4 | 预处理说明 | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=43) | 31 | [文本](../../generated/text/ai-inference-v21/page-0043.txt) |
| 4 | dataset.txt文本格式说明 | [43](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=43) | 31 | [文本](../../generated/text/ai-inference-v21/page-0043.txt) |
| 3 | 注意事项 | [44](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=44) | 32 | [文本](../../generated/text/ai-inference-v21/page-0044.txt) |
| 1 | MacaRT-LLM | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=45) | 33 | [文本](../../generated/text/ai-inference-v21/page-0045.txt) |
| 2 | MacaRT-LLM介绍 | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=45) | 33 | [文本](../../generated/text/ai-inference-v21/page-0045.txt) |
| 2 | MacaRT-LLM功能 | [45](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=45) | 33 | [文本](../../generated/text/ai-inference-v21/page-0045.txt) |
| 2 | MacaRT-LLM使用流程 | [46](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=46) | 34 | [文本](../../generated/text/ai-inference-v21/page-0046.txt) |
| 3 | 模型转换 | [46](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=46) | 34 | [文本](../../generated/text/ai-inference-v21/page-0046.txt) |
| 4 | 安装 | [46](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=46) | 34 | [文本](../../generated/text/ai-inference-v21/page-0046.txt) |
| 4 | 转换为PMX模型 | [47](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=47) | 35 | [文本](../../generated/text/ai-inference-v21/page-0047.txt) |
| 4 | 模型切分 | [48](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=48) | 36 | [文本](../../generated/text/ai-inference-v21/page-0048.txt) |
| 4 | 模型合并（可选） | [48](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=48) | 36 | [文本](../../generated/text/ai-inference-v21/page-0048.txt) |
| 4 | PMX模型测试 | [49](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=49) | 37 | [文本](../../generated/text/ai-inference-v21/page-0049.txt) |
| 4 | 导出为ONNX模型 | [50](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=50) | 38 | [文本](../../generated/text/ai-inference-v21/page-0050.txt) |
| 3 | 本地模型部署精度验证 | [52](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=52) | 40 | [文本](../../generated/text/ai-inference-v21/page-0052.txt) |
| 3 | 本地模型部署性能测试 | [54](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=54) | 42 | [文本](../../generated/text/ai-inference-v21/page-0054.txt) |
| 3 | 服务化部署 | [56](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=56) | 44 | [文本](../../generated/text/ai-inference-v21/page-0056.txt) |
| 4 | 服务端部署 | [56](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=56) | 44 | [文本](../../generated/text/ai-inference-v21/page-0056.txt) |
| 4 | C++客户端部署 | [58](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=58) | 46 | [文本](../../generated/text/ai-inference-v21/page-0058.txt) |
| 4 | Python客户端部署 | [59](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=59) | 47 | [文本](../../generated/text/ai-inference-v21/page-0059.txt) |
| 4 | 服务端输出性能数据解析 | [59](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=59) | 47 | [文本](../../generated/text/ai-inference-v21/page-0059.txt) |
| 1 | MacaRT-vLLM | [61](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=61) | 49 | [文本](../../generated/text/ai-inference-v21/page-0061.txt) |
| 2 | MacaRT-vLLM介绍 | [61](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=61) | 49 | [文本](../../generated/text/ai-inference-v21/page-0061.txt) |
| 2 | MacaRT-vLLM功能与局限性 | [61](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=61) | 49 | [文本](../../generated/text/ai-inference-v21/page-0061.txt) |
| 2 | MacaRT-vLLM使用流程 | [62](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=62) | 50 | [文本](../../generated/text/ai-inference-v21/page-0062.txt) |
| 3 | 环境准备 | [62](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=62) | 50 | [文本](../../generated/text/ai-inference-v21/page-0062.txt) |
| 4 | 使用vLLM镜像 | [62](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=62) | 50 | [文本](../../generated/text/ai-inference-v21/page-0062.txt) |
| 4 | 安装wheel包 | [62](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=62) | 50 | [文本](../../generated/text/ai-inference-v21/page-0062.txt) |
| 4 | 配置环境变量 | [63](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=63) | 51 | [文本](../../generated/text/ai-inference-v21/page-0063.txt) |
| 3 | 离线推理 | [63](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=63) | 51 | [文本](../../generated/text/ai-inference-v21/page-0063.txt) |
| 3 | 吞吐测试 | [64](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=64) | 52 | [文本](../../generated/text/ai-inference-v21/page-0064.txt) |
| 3 | Server服务 | [64](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=64) | 52 | [文本](../../generated/text/ai-inference-v21/page-0064.txt) |
| 1 | MacaRT-vLLM-metax | [65](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=65) | 53 | [文本](../../generated/text/ai-inference-v21/page-0065.txt) |
| 2 | MacaRT-vLLM-metax介绍 | [65](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=65) | 53 | [文本](../../generated/text/ai-inference-v21/page-0065.txt) |
| 3 | 分支说明 | [65](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=65) | 53 | [文本](../../generated/text/ai-inference-v21/page-0065.txt) |
| 2 | MacaRT-vLLM-metax功能与局限性 | [65](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=65) | 53 | [文本](../../generated/text/ai-inference-v21/page-0065.txt) |
| 2 | MacaRT-vLLM-metax使用流程 | [66](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=66) | 54 | [文本](../../generated/text/ai-inference-v21/page-0066.txt) |
| 3 | 环境准备 | [66](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=66) | 54 | [文本](../../generated/text/ai-inference-v21/page-0066.txt) |
| 4 | 使用vLLM镜像 | [66](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=66) | 54 | [文本](../../generated/text/ai-inference-v21/page-0066.txt) |
| 4 | 安装wheel包 | [67](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=67) | 55 | [文本](../../generated/text/ai-inference-v21/page-0067.txt) |
| 4 | 源代码构建教程 | [67](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=67) | 55 | [文本](../../generated/text/ai-inference-v21/page-0067.txt) |
| 4 | 设置环境变量 | [67](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=67) | 55 | [文本](../../generated/text/ai-inference-v21/page-0067.txt) |
| 4 | 构建vLLM | [68](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=68) | 56 | [文本](../../generated/text/ai-inference-v21/page-0068.txt) |
| 4 | 构建vLLM-metax | [68](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=68) | 56 | [文本](../../generated/text/ai-inference-v21/page-0068.txt) |
| 3 | 离线推理 | [68](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=68) | 56 | [文本](../../generated/text/ai-inference-v21/page-0068.txt) |
| 3 | 吞吐测试 | [69](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=69) | 57 | [文本](../../generated/text/ai-inference-v21/page-0069.txt) |
| 3 | Server服务 | [70](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=70) | 58 | [文本](../../generated/text/ai-inference-v21/page-0070.txt) |
| 1 | MacaRT-ModelZoo | [71](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=71) | 59 | [文本](../../generated/text/ai-inference-v21/page-0071.txt) |
| 2 | MacaRT-ModelZoo介绍 | [71](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=71) | 59 | [文本](../../generated/text/ai-inference-v21/page-0071.txt) |
| 2 | 模型评测条件 | [71](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=71) | 59 | [文本](../../generated/text/ai-inference-v21/page-0071.txt) |
| 2 | 代码目录结构及说明 | [71](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=71) | 59 | [文本](../../generated/text/ai-inference-v21/page-0071.txt) |
| 2 | 源码、模型和数据集 | [72](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=72) | 60 | [文本](../../generated/text/ai-inference-v21/page-0072.txt) |
| 3 | 源码镜像获取 | [72](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=72) | 60 | [文本](../../generated/text/ai-inference-v21/page-0072.txt) |
| 3 | 模型获取 | [72](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=72) | 60 | [文本](../../generated/text/ai-inference-v21/page-0072.txt) |
| 3 | 数据集获取 | [73](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=73) | 61 | [文本](../../generated/text/ai-inference-v21/page-0073.txt) |
| 2 | 模型评测步骤 | [73](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=73) | 61 | [文本](../../generated/text/ai-inference-v21/page-0073.txt) |
| 3 | 启动容器镜像 | [73](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=73) | 61 | [文本](../../generated/text/ai-inference-v21/page-0073.txt) |
| 3 | 建立数据集的关联 | [73](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=73) | 61 | [文本](../../generated/text/ai-inference-v21/page-0073.txt) |
| 3 | 执行模型评测 | [73](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=73) | 61 | [文本](../../generated/text/ai-inference-v21/page-0073.txt) |
| 1 | MacaRT-LMDeploy | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=75) | 63 | [文本](../../generated/text/ai-inference-v21/page-0075.txt) |
| 2 | MacaRT-LMDeploy介绍 | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=75) | 63 | [文本](../../generated/text/ai-inference-v21/page-0075.txt) |
| 2 | MacaRT-LMDeploy功能与局限性 | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=75) | 63 | [文本](../../generated/text/ai-inference-v21/page-0075.txt) |
| 2 | MacaRT-LMDeploy使用流程 | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=75) | 63 | [文本](../../generated/text/ai-inference-v21/page-0075.txt) |
| 3 | 环境准备 | [75](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=75) | 63 | [文本](../../generated/text/ai-inference-v21/page-0075.txt) |
| 4 | 获取vLLM镜像 | [76](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=76) | 64 | [文本](../../generated/text/ai-inference-v21/page-0076.txt) |
| 4 | 安装dlinfer | [76](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=76) | 64 | [文本](../../generated/text/ai-inference-v21/page-0076.txt) |
| 4 | 安装LMDeploy | [76](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=76) | 64 | [文本](../../generated/text/ai-inference-v21/page-0076.txt) |
| 3 | 离线推理 | [77](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=77) | 65 | [文本](../../generated/text/ai-inference-v21/page-0077.txt) |
| 3 | 静态推理性能测试 | [77](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=77) | 65 | [文本](../../generated/text/ai-inference-v21/page-0077.txt) |
| 3 | Server服务动态推理性能测试 | [78](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=78) | 66 | [文本](../../generated/text/ai-inference-v21/page-0078.txt) |
| 1 | Diffusers | [80](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=80) | 68 | [文本](../../generated/text/ai-inference-v21/page-0080.txt) |
| 1 | Transformers | [81](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=81) | 69 | [文本](../../generated/text/ai-inference-v21/page-0081.txt) |
| 1 | MacaRT-SGLang | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 2 | MacaRT-SGLang介绍 | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 2 | MacaRT-SGLang功能 | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 2 | MacaRT-SGLang使用流程 | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 3 | 环境准备 | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 4 | 使用SGLang镜像 | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 4 | 设置环境变量 | [82](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=82) | 70 | [文本](../../generated/text/ai-inference-v21/page-0082.txt) |
| 4 | 启动Server | [83](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=83) | 71 | [文本](../../generated/text/ai-inference-v21/page-0083.txt) |
| 3 | 在线推理 | [83](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=83) | 71 | [文本](../../generated/text/ai-inference-v21/page-0083.txt) |
| 3 | 吞吐测试 | [84](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=84) | 72 | [文本](../../generated/text/ai-inference-v21/page-0084.txt) |
| 3 | 精度测试 | [84](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=84) | 72 | [文本](../../generated/text/ai-inference-v21/page-0084.txt) |
| 4 | MMLU精度测试 | [84](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=84) | 72 | [文本](../../generated/text/ai-inference-v21/page-0084.txt) |
| 4 | C-Eval精度测试 | [84](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=84) | 72 | [文本](../../generated/text/ai-inference-v21/page-0084.txt) |
| 1 | ModelZoo.LLM.SGLang | [86](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=86) | 74 | [文本](../../generated/text/ai-inference-v21/page-0086.txt) |
| 2 | ModelZoo.LLM.SGLang介绍 | [86](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=86) | 74 | [文本](../../generated/text/ai-inference-v21/page-0086.txt) |
| 2 | 模型评测条件 | [86](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=86) | 74 | [文本](../../generated/text/ai-inference-v21/page-0086.txt) |
| 2 | 代码目录结构及说明 | [86](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=86) | 74 | [文本](../../generated/text/ai-inference-v21/page-0086.txt) |
| 2 | 源码、模型和环境准备 | [87](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=87) | 75 | [文本](../../generated/text/ai-inference-v21/page-0087.txt) |
| 3 | 源码镜像获取 | [87](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=87) | 75 | [文本](../../generated/text/ai-inference-v21/page-0087.txt) |
| 3 | 模型获取 | [88](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=88) | 76 | [文本](../../generated/text/ai-inference-v21/page-0088.txt) |
| 3 | 服务器信息配置 | [88](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=88) | 76 | [文本](../../generated/text/ai-inference-v21/page-0088.txt) |
| 3 | 修改模型配置文件 | [89](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=89) | 77 | [文本](../../generated/text/ai-inference-v21/page-0089.txt) |
| 2 | 模型评测步骤 | [90](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=90) | 78 | [文本](../../generated/text/ai-inference-v21/page-0090.txt) |
| 3 | 启动容器镜像 | [90](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=90) | 78 | [文本](../../generated/text/ai-inference-v21/page-0090.txt) |
| 3 | 配置机器信息 | [90](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=90) | 78 | [文本](../../generated/text/ai-inference-v21/page-0090.txt) |
| 3 | 配置任务信息 | [90](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=90) | 78 | [文本](../../generated/text/ai-inference-v21/page-0090.txt) |
| 3 | 执行模型评测 | [91](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=91) | 79 | [文本](../../generated/text/ai-inference-v21/page-0091.txt) |
| 1 | 附录 | [92](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=92) | 80 | [文本](../../generated/text/ai-inference-v21/page-0092.txt) |
| 2 | 术语/缩略语 | [92](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_AI%E6%8E%A8%E7%90%86%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V21.pdf#page=92) | 80 | [文本](../../generated/text/ai-inference-v21/page-0092.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/ai-inference-v21/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/ai-inference-v21/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/ai-inference-v21/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/ai-inference-v21/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/ai-inference-v21/page-0005.txt)
- [PDF 6 / 标签 iv](../../generated/text/ai-inference-v21/page-0006.txt)
- [PDF 7 / 标签 v](../../generated/text/ai-inference-v21/page-0007.txt)
- [PDF 8 / 标签 vi](../../generated/text/ai-inference-v21/page-0008.txt)
- [PDF 9 / 标签 vii](../../generated/text/ai-inference-v21/page-0009.txt)
- [PDF 10 / 标签 vii](../../generated/text/ai-inference-v21/page-0010.txt)
- [PDF 11 / 标签 viii](../../generated/text/ai-inference-v21/page-0011.txt)
- [PDF 12 / 标签 ix](../../generated/text/ai-inference-v21/page-0012.txt)
- [PDF 13 / 标签 1](../../generated/text/ai-inference-v21/page-0013.txt)
- [PDF 14 / 标签 2](../../generated/text/ai-inference-v21/page-0014.txt)
- [PDF 15 / 标签 3](../../generated/text/ai-inference-v21/page-0015.txt)
- [PDF 16 / 标签 4](../../generated/text/ai-inference-v21/page-0016.txt)
- [PDF 17 / 标签 5](../../generated/text/ai-inference-v21/page-0017.txt)
- [PDF 18 / 标签 6](../../generated/text/ai-inference-v21/page-0018.txt)
- [PDF 19 / 标签 7](../../generated/text/ai-inference-v21/page-0019.txt)
- [PDF 20 / 标签 8](../../generated/text/ai-inference-v21/page-0020.txt)
- [PDF 21 / 标签 9](../../generated/text/ai-inference-v21/page-0021.txt)
- [PDF 22 / 标签 10](../../generated/text/ai-inference-v21/page-0022.txt)
- [PDF 23 / 标签 11](../../generated/text/ai-inference-v21/page-0023.txt)
- [PDF 24 / 标签 12](../../generated/text/ai-inference-v21/page-0024.txt)
- [PDF 25 / 标签 13](../../generated/text/ai-inference-v21/page-0025.txt)
- [PDF 26 / 标签 14](../../generated/text/ai-inference-v21/page-0026.txt)
- [PDF 27 / 标签 15](../../generated/text/ai-inference-v21/page-0027.txt)
- [PDF 28 / 标签 16](../../generated/text/ai-inference-v21/page-0028.txt)
- [PDF 29 / 标签 17](../../generated/text/ai-inference-v21/page-0029.txt)
- [PDF 30 / 标签 18](../../generated/text/ai-inference-v21/page-0030.txt)
- [PDF 31 / 标签 19](../../generated/text/ai-inference-v21/page-0031.txt)
- [PDF 32 / 标签 20](../../generated/text/ai-inference-v21/page-0032.txt)
- [PDF 33 / 标签 21](../../generated/text/ai-inference-v21/page-0033.txt)
- [PDF 34 / 标签 22](../../generated/text/ai-inference-v21/page-0034.txt)
- [PDF 35 / 标签 23](../../generated/text/ai-inference-v21/page-0035.txt)
- [PDF 36 / 标签 24](../../generated/text/ai-inference-v21/page-0036.txt)
- [PDF 37 / 标签 25](../../generated/text/ai-inference-v21/page-0037.txt)
- [PDF 38 / 标签 26](../../generated/text/ai-inference-v21/page-0038.txt)
- [PDF 39 / 标签 27](../../generated/text/ai-inference-v21/page-0039.txt)
- [PDF 40 / 标签 28](../../generated/text/ai-inference-v21/page-0040.txt)
- [PDF 41 / 标签 29](../../generated/text/ai-inference-v21/page-0041.txt)
- [PDF 42 / 标签 30](../../generated/text/ai-inference-v21/page-0042.txt)
- [PDF 43 / 标签 31](../../generated/text/ai-inference-v21/page-0043.txt)
- [PDF 44 / 标签 32](../../generated/text/ai-inference-v21/page-0044.txt)
- [PDF 45 / 标签 33](../../generated/text/ai-inference-v21/page-0045.txt)
- [PDF 46 / 标签 34](../../generated/text/ai-inference-v21/page-0046.txt)
- [PDF 47 / 标签 35](../../generated/text/ai-inference-v21/page-0047.txt)
- [PDF 48 / 标签 36](../../generated/text/ai-inference-v21/page-0048.txt)
- [PDF 49 / 标签 37](../../generated/text/ai-inference-v21/page-0049.txt)
- [PDF 50 / 标签 38](../../generated/text/ai-inference-v21/page-0050.txt)
- [PDF 51 / 标签 39](../../generated/text/ai-inference-v21/page-0051.txt)
- [PDF 52 / 标签 40](../../generated/text/ai-inference-v21/page-0052.txt)
- [PDF 53 / 标签 41](../../generated/text/ai-inference-v21/page-0053.txt)
- [PDF 54 / 标签 42](../../generated/text/ai-inference-v21/page-0054.txt)
- [PDF 55 / 标签 43](../../generated/text/ai-inference-v21/page-0055.txt)
- [PDF 56 / 标签 44](../../generated/text/ai-inference-v21/page-0056.txt)
- [PDF 57 / 标签 45](../../generated/text/ai-inference-v21/page-0057.txt)
- [PDF 58 / 标签 46](../../generated/text/ai-inference-v21/page-0058.txt)
- [PDF 59 / 标签 47](../../generated/text/ai-inference-v21/page-0059.txt)
- [PDF 60 / 标签 48](../../generated/text/ai-inference-v21/page-0060.txt)
- [PDF 61 / 标签 49](../../generated/text/ai-inference-v21/page-0061.txt)
- [PDF 62 / 标签 50](../../generated/text/ai-inference-v21/page-0062.txt)
- [PDF 63 / 标签 51](../../generated/text/ai-inference-v21/page-0063.txt)
- [PDF 64 / 标签 52](../../generated/text/ai-inference-v21/page-0064.txt)
- [PDF 65 / 标签 53](../../generated/text/ai-inference-v21/page-0065.txt)
- [PDF 66 / 标签 54](../../generated/text/ai-inference-v21/page-0066.txt)
- [PDF 67 / 标签 55](../../generated/text/ai-inference-v21/page-0067.txt)
- [PDF 68 / 标签 56](../../generated/text/ai-inference-v21/page-0068.txt)
- [PDF 69 / 标签 57](../../generated/text/ai-inference-v21/page-0069.txt)
- [PDF 70 / 标签 58](../../generated/text/ai-inference-v21/page-0070.txt)
- [PDF 71 / 标签 59](../../generated/text/ai-inference-v21/page-0071.txt)
- [PDF 72 / 标签 60](../../generated/text/ai-inference-v21/page-0072.txt)
- [PDF 73 / 标签 61](../../generated/text/ai-inference-v21/page-0073.txt)
- [PDF 74 / 标签 62](../../generated/text/ai-inference-v21/page-0074.txt)
- [PDF 75 / 标签 63](../../generated/text/ai-inference-v21/page-0075.txt)
- [PDF 76 / 标签 64](../../generated/text/ai-inference-v21/page-0076.txt)
- [PDF 77 / 标签 65](../../generated/text/ai-inference-v21/page-0077.txt)
- [PDF 78 / 标签 66](../../generated/text/ai-inference-v21/page-0078.txt)
- [PDF 79 / 标签 67](../../generated/text/ai-inference-v21/page-0079.txt)
- [PDF 80 / 标签 68](../../generated/text/ai-inference-v21/page-0080.txt)
- [PDF 81 / 标签 69](../../generated/text/ai-inference-v21/page-0081.txt)
- [PDF 82 / 标签 70](../../generated/text/ai-inference-v21/page-0082.txt)
- [PDF 83 / 标签 71](../../generated/text/ai-inference-v21/page-0083.txt)
- [PDF 84 / 标签 72](../../generated/text/ai-inference-v21/page-0084.txt)
- [PDF 85 / 标签 73](../../generated/text/ai-inference-v21/page-0085.txt)
- [PDF 86 / 标签 74](../../generated/text/ai-inference-v21/page-0086.txt)
- [PDF 87 / 标签 75](../../generated/text/ai-inference-v21/page-0087.txt)
- [PDF 88 / 标签 76](../../generated/text/ai-inference-v21/page-0088.txt)
- [PDF 89 / 标签 77](../../generated/text/ai-inference-v21/page-0089.txt)
- [PDF 90 / 标签 78](../../generated/text/ai-inference-v21/page-0090.txt)
- [PDF 91 / 标签 79](../../generated/text/ai-inference-v21/page-0091.txt)
- [PDF 92 / 标签 80](../../generated/text/ai-inference-v21/page-0092.txt)
