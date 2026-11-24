# 沐曦通用GPU_MXMACA Clangd用户手册

文档 ID：`clangd-v03`；文档修订：V03；发布日期：2026-03-27。

[原始 PDF](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf)

SHA256：`f84564a4060d30251dbb164705b0aec56b25f11c02c1c748d5ce6187e44868ad`

文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。

## 适用产品来源

[PDF 第 7 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=7)

> 本文档适用于沐曦 MXC500 系列产品：曦云 ® C500、C500X、C550、C550‑PL、C588，曦思® N260；以
> 及 MXC600 系列产品：曦云 ® C600，曦思 ® N300。

## 软件环境与版本要求的候选来源

候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。

- [PDF 第 7 页（标签 2）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=7) · [逐页文本](../../generated/text/clangd-v03/page-0007.txt)
- [PDF 第 8 页（标签 3）](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=8) · [逐页文本](../../generated/text/clangd-v03/page-0008.txt)

## 完整章节书签

标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。

| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |
|---|---|---:|---|---|
| 1 | 概述 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=6) | 1 | [文本](../../generated/text/clangd-v03/page-0006.txt) |
| 2 | 工作流程 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=6) | 1 | [文本](../../generated/text/clangd-v03/page-0006.txt) |
| 2 | 关键特性 | [6](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=6) | 1 | [文本](../../generated/text/clangd-v03/page-0006.txt) |
| 2 | 支持平台 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=7) | 2 | [文本](../../generated/text/clangd-v03/page-0007.txt) |
| 3 | Clangd工具 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=7) | 2 | [文本](../../generated/text/clangd-v03/page-0007.txt) |
| 3 | Clangd插件 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=7) | 2 | [文本](../../generated/text/clangd-v03/page-0007.txt) |
| 2 | 适用产品 | [7](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=7) | 2 | [文本](../../generated/text/clangd-v03/page-0007.txt) |
| 1 | MXMACA Clangd 安装 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=8) | 3 | [文本](../../generated/text/clangd-v03/page-0008.txt) |
| 2 | 准备文件 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=8) | 3 | [文本](../../generated/text/clangd-v03/page-0008.txt) |
| 2 | 安装Clangd插件 | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=8) | 3 | [文本](../../generated/text/clangd-v03/page-0008.txt) |
| 2 | 禁用VSCode官方C/C++插件（若有） | [8](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=8) | 3 | [文本](../../generated/text/clangd-v03/page-0008.txt) |
| 1 | MXMACA Clangd使用 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=10) | 5 | [文本](../../generated/text/clangd-v03/page-0010.txt) |
| 2 | 为工程生成compile_commands.json文件 | [10](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=10) | 5 | [文本](../../generated/text/clangd-v03/page-0010.txt) |
| 2 | 独立文件或简单工程 | [11](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=11) | 6 | [文本](../../generated/text/clangd-v03/page-0011.txt) |
| 1 | 特性列表 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=12) | 7 | [文本](../../generated/text/clangd-v03/page-0012.txt) |
| 2 | .maca文件识别 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=12) | 7 | [文本](../../generated/text/clangd-v03/page-0012.txt) |
| 2 | 错误和告警诊断 | [12](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=12) | 7 | [文本](../../generated/text/clangd-v03/page-0012.txt) |
| 2 | 代码补全 | [13](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=13) | 8 | [文本](../../generated/text/clangd-v03/page-0013.txt) |
| 2 | 跳转 | [14](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=14) | 9 | [文本](../../generated/text/clangd-v03/page-0014.txt) |
| 2 | 工程导航 | [15](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=15) | 10 | [文本](../../generated/text/clangd-v03/page-0015.txt) |
| 2 | 悬停 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=16) | 11 | [文本](../../generated/text/clangd-v03/page-0016.txt) |
| 2 | 代码规范化 | [16](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=16) | 11 | [文本](../../generated/text/clangd-v03/page-0016.txt) |
| 2 | 代码重构 | [17](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=17) | 12 | [文本](../../generated/text/clangd-v03/page-0017.txt) |
| 2 | 关键字高亮 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=20) | 15 | [文本](../../generated/text/clangd-v03/page-0020.txt) |
| 2 | 源文件与头文件切换 | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=20) | 15 | [文本](../../generated/text/clangd-v03/page-0020.txt) |
| 2 | 显示AST | [20](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=20) | 15 | [文本](../../generated/text/clangd-v03/page-0020.txt) |
| 2 | 显示MXMACA预处理后文件 | [22](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=22) | 17 | [文本](../../generated/text/clangd-v03/page-0022.txt) |
| 1 | 进阶配置 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=23) | 18 | [文本](../../generated/text/clangd-v03/page-0023.txt) |
| 2 | 配置Clangd工具路径 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=23) | 18 | [文本](../../generated/text/clangd-v03/page-0023.txt) |
| 2 | 重启Clangd工具 | [23](../../%E6%B2%90%E6%9B%A6%E9%80%9A%E7%94%A8GPU_MXMACA%20Clangd%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_CN_V03.pdf#page=23) | 18 | [文本](../../generated/text/clangd-v03/page-0023.txt) |

## 全部页面

- [PDF 1 / 标签 1](../../generated/text/clangd-v03/page-0001.txt)
- [PDF 2 / 标签 2](../../generated/text/clangd-v03/page-0002.txt)
- [PDF 3 / 标签 i](../../generated/text/clangd-v03/page-0003.txt)
- [PDF 4 / 标签 ii](../../generated/text/clangd-v03/page-0004.txt)
- [PDF 5 / 标签 iii](../../generated/text/clangd-v03/page-0005.txt)
- [PDF 6 / 标签 1](../../generated/text/clangd-v03/page-0006.txt)
- [PDF 7 / 标签 2](../../generated/text/clangd-v03/page-0007.txt)
- [PDF 8 / 标签 3](../../generated/text/clangd-v03/page-0008.txt)
- [PDF 9 / 标签 4](../../generated/text/clangd-v03/page-0009.txt)
- [PDF 10 / 标签 5](../../generated/text/clangd-v03/page-0010.txt)
- [PDF 11 / 标签 6](../../generated/text/clangd-v03/page-0011.txt)
- [PDF 12 / 标签 7](../../generated/text/clangd-v03/page-0012.txt)
- [PDF 13 / 标签 8](../../generated/text/clangd-v03/page-0013.txt)
- [PDF 14 / 标签 9](../../generated/text/clangd-v03/page-0014.txt)
- [PDF 15 / 标签 10](../../generated/text/clangd-v03/page-0015.txt)
- [PDF 16 / 标签 11](../../generated/text/clangd-v03/page-0016.txt)
- [PDF 17 / 标签 12](../../generated/text/clangd-v03/page-0017.txt)
- [PDF 18 / 标签 13](../../generated/text/clangd-v03/page-0018.txt)
- [PDF 19 / 标签 14](../../generated/text/clangd-v03/page-0019.txt)
- [PDF 20 / 标签 15](../../generated/text/clangd-v03/page-0020.txt)
- [PDF 21 / 标签 16](../../generated/text/clangd-v03/page-0021.txt)
- [PDF 22 / 标签 17](../../generated/text/clangd-v03/page-0022.txt)
- [PDF 23 / 标签 18](../../generated/text/clangd-v03/page-0023.txt)
