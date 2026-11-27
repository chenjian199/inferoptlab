# 006 按真实模块和 shape 优化 BF16 GEMV 与 INT8 dense linear

状态：proposed，待确认。优先级：P2。类型：算子选择与局部kernel。前置：001。

## 证据与边界

TP8/EP关4K/C1的GEMV子集占16.45%，C8仅0.61%；新TP2/DP4/EP8每DP一条请求时gemm类约238.546ms/32步，占27.98%，其中有明显BF16 GEMV。该gemm类不是单个模块，不把整个类别都算成某个候选的收益。

当前KDA投影显式保持BF16；其六路输入投影已经合并。W8A8 dense linear则通过 `MctlassScaledMMLinearKernel.apply_weights → scaled_int8_quant → cutlass_scaled_mm[_azp]`。两条路径需分别处理。[源码分析](source-review.md)

## 最小计划

- [ ] 抓一次不计分的shape/module映射，记录M/N/K、输入/权重dtype与stride、bias、quant scale、layout、调用频次；图内缺CPU调用时做独立单层replay，不能用kernel模板名猜矩阵尺寸。
- [ ] BF16线优先比较现有库算法、小M GEMV tile/并行度与权重读取布局；不把改成INT8算作同精度kernel优化。
- [ ] INT8线先比较真实scale/zero-point契约下的现有mctlassEx与候选；复用[单层原型](../experiments/evidence/metax/glm53/gemm_replace_20261123/README.md)的对象级替换、输入冻结和恢复方法。
- [ ] 性能版关闭双算、同步对比和INT32结果抓取；正确性版单独保留。原型的历史局部通过不是新环境模型精度或性能证明。
- [ ] 对M=1/2/4与目标吞吐batch分开验收；确认是否可以避免重复contiguous或中间量化访问。预转置/packing只在加载时做，并验证对显存与cache容量的影响。

## 验收与否决

每个候选只覆盖已测shape allowlist；同权重/精度下局部变快，目标模块确实被命中，模型回归与端到端达到共同流程要求。不因一个GEMV快就全局替换全部linear。

原生GEMM底层若只提供二进制，能改的是接入、布局、算法选择或新实现；不能声称已经修改未获得源码的内部调度。若需厂商接口才能继续，提交具体shape/trace/最小复现，不泛泛申请“更快的GEMM”。
