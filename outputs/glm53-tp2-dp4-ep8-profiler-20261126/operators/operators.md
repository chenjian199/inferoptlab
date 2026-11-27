# torch.profiler Decode 算子采样

按 worker/device 独立统计。GPU kernel 时长求和不等于墙钟时间；CPU 算子为包含子调用的总时长，不能与 GPU 时长相加。
图重放可能保留 GPU kernel 名称但不重新产生每个 Python/ATen 调用；缺失 CPU 调用不表示该算子未执行。
family_hint 仅按名称归类。完整名称、调用次数、均值、P95、最大值和总时长保存在各 trace 的 JSON 中；过长的模板名称在表内缩写并附名称哈希。

## l16384-o200-c4_dp0_pp0_tp0_dcp0_ep0_rank0.1795684751027658828.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp0_pp0_tp0_dcp0_ep0_rank0.1795684751027658828.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 0 | 871.125 | 869.455 | 1276.372 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 100.437 | 74.730 | 123.730 | 173.471 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.824 | 61.022 | 69.800 | 387.328 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 65.590 | 48.802 | 90.569 | 124.689 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 55.973 | 17.849 | 32.173 | 50.580 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.873 | 14.887 | 15.310 | 15.950 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.138 | 14.796 | 15.160 | 15.710 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 38.291 | 28.490 | 21.437 | 1844.100 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 36.634 | 27.258 | 48.248 | 65.530 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.844 | 25.926 | 26.730 | 27.460 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 30.957 | 28.454 | 29.840 | 31.530 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 16.639 | 519.970 | 1308.022 | 6950.698 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.297 | 10.637 | 10.880 | 11.360 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.240 | 12.169 | 12.480 | 12.950 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.630 | 35.880 | 36.150 | 36.310 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.545 | 8.590 | 8.770 | 9.060 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.904 | 8.113 | 8.380 | 8.680 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.631 | 4.885 | 5.120 | 5.460 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.281 | 3.279 | 3.422 | 4.670 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.756 | 3.209 | 3.420 | 6.270 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.022 | 6.265 | 8.610 | 13.340 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 20.814 | 18.068 |
| `aten::to` | 640 | 16.899 | 26.405 |
| `aten::_to_copy` | 448 | 16.030 | 35.781 |
| `vllm::all_gather` | 32 | 9.190 | 287.200 |
| `aten::slice` | 2624 | 8.513 | 3.244 |
| `c10d::_allgather_base_` | 32 | 5.979 | 186.858 |
| `aten::fill_` | 704 | 5.512 | 7.829 |
| `aten::index` | 128 | 5.410 | 42.262 |
| `record_param_comms` | 32 | 5.223 | 163.215 |
| `aten::select` | 1472 | 4.213 | 2.862 |

## l16384-o200-c4_dp0_pp0_tp1_dcp0_ep1_rank1.1795684750997061885.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp0_pp0_tp1_dcp0_ep1_rank1.1795684750997061885.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 1 | 857.481 | 855.895 | 1268.658 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.804 | 61.008 | 69.810 | 387.328 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 83.331 | 62.002 | 116.873 | 176.180 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 76.272 | 56.750 | 91.088 | 131.311 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.410 | 17.988 | 32.380 | 50.080 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.863 | 14.883 | 15.340 | 15.850 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.117 | 14.788 | 15.141 | 15.555 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 42.043 | 31.282 | 48.675 | 68.090 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 37.896 | 28.196 | 20.837 | 1844.462 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.750 | 25.856 | 26.720 | 27.320 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.125 | 28.608 | 30.170 | 32.050 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.301 | 10.640 | 10.890 | 11.150 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.257 | 12.185 | 12.480 | 12.940 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.630 | 35.881 | 36.180 | 36.450 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.541 | 8.587 | 8.800 | 9.060 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.930 | 8.133 | 8.400 | 8.680 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.538 | 4.843 | 5.190 | 5.490 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.266 | 3.274 | 3.410 | 4.590 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.747 | 3.206 | 3.420 | 6.720 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.086 | 6.310 | 8.573 | 12.709 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 8.925 | 25.354 | 27.289 | 28.330 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 17.314 | 15.913 |
| `aten::to` | 544 | 11.578 | 21.283 |
| `aten::_to_copy` | 384 | 10.973 | 28.576 |
| `aten::slice` | 2624 | 9.250 | 3.525 |
| `vllm::all_gather` | 32 | 8.583 | 268.205 |
| `aten::fill_` | 704 | 6.561 | 9.319 |
| `aten::arange` | 64 | 6.090 | 95.152 |
| `c10d::_allgather_base_` | 32 | 5.594 | 174.825 |
| `aten::index` | 128 | 5.055 | 39.491 |
| `record_param_comms` | 32 | 4.922 | 153.826 |

## l16384-o200-c4_dp1_pp0_tp0_dcp0_ep2_rank0.1795684751003495251.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp1_pp0_tp0_dcp0_ep2_rank0.1795684751003495251.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 2 | 883.192 | 881.611 | 1276.325 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.863 | 61.048 | 69.800 | 386.816 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 84.611 | 62.954 | 89.343 | 121.511 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 69.501 | 51.712 | 110.564 | 155.389 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.567 | 18.038 | 32.660 | 50.970 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 46.119 | 34.315 | 47.924 | 64.780 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 44.538 | 33.138 | 21.435 | 2923.301 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.865 | 14.884 | 15.330 | 15.740 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.199 | 14.817 | 15.157 | 15.620 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.819 | 25.907 | 26.890 | 27.740 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.325 | 28.791 | 30.396 | 32.360 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 23.653 | 739.156 | 1230.764 | 7774.554 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.306 | 10.645 | 10.910 | 11.260 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.253 | 12.181 | 12.466 | 12.820 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.626 | 35.868 | 36.105 | 36.430 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.559 | 8.600 | 8.830 | 9.060 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.908 | 8.116 | 8.410 | 8.760 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.505 | 4.828 | 5.090 | 5.360 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.267 | 3.274 | 3.440 | 4.520 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.755 | 3.209 | 3.420 | 5.990 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.216 | 6.400 | 8.990 | 12.960 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 18.404 | 15.976 |
| `aten::to` | 640 | 14.474 | 22.615 |
| `aten::_to_copy` | 448 | 13.701 | 30.582 |
| `vllm::all_gather` | 32 | 8.085 | 252.648 |
| `aten::slice` | 2624 | 7.807 | 2.975 |
| `c10d::_allgather_base_` | 32 | 5.098 | 159.302 |
| `aten::index` | 128 | 4.891 | 38.213 |
| `aten::fill_` | 704 | 4.819 | 6.846 |
| `record_param_comms` | 32 | 4.438 | 138.676 |
| `aten::select` | 1472 | 3.926 | 2.667 |

## l16384-o200-c4_dp1_pp0_tp1_dcp0_ep3_rank1.1795684751025546404.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp1_pp0_tp1_dcp0_ep3_rank1.1795684751025546404.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 3 | 863.251 | 861.574 | 1268.634 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.890 | 61.067 | 69.970 | 387.584 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 80.750 | 60.082 | 120.139 | 166.768 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 78.688 | 58.548 | 91.967 | 125.970 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.674 | 18.072 | 32.942 | 50.529 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 44.539 | 33.139 | 21.322 | 2923.121 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 43.899 | 32.663 | 49.459 | 67.360 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.880 | 14.889 | 15.310 | 15.870 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.192 | 14.815 | 15.170 | 15.580 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.316 | 25.533 | 26.260 | 27.000 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.504 | 28.955 | 30.736 | 33.270 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.312 | 10.649 | 10.910 | 11.250 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.259 | 12.187 | 12.540 | 13.010 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.621 | 35.855 | 36.080 | 36.430 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.532 | 8.580 | 8.740 | 9.100 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.998 | 8.183 | 8.420 | 8.660 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.446 | 4.800 | 5.050 | 5.280 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.299 | 3.284 | 3.430 | 4.920 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.764 | 3.212 | 3.440 | 7.200 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.028 | 6.270 | 8.679 | 13.730 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 8.978 | 25.506 | 27.470 | 28.070 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 17.029 | 15.651 |
| `aten::to` | 544 | 10.679 | 19.631 |
| `aten::_to_copy` | 384 | 10.042 | 26.151 |
| `aten::slice` | 2624 | 9.297 | 3.543 |
| `vllm::all_gather` | 32 | 8.359 | 261.211 |
| `aten::fill_` | 704 | 6.853 | 9.735 |
| `aten::arange` | 64 | 5.822 | 90.973 |
| `c10d::_allgather_base_` | 32 | 5.370 | 167.801 |
| `aten::index` | 128 | 4.907 | 38.334 |
| `record_param_comms` | 32 | 4.693 | 146.665 |

## l16384-o200-c4_dp2_pp0_tp0_dcp0_ep4_rank0.1795684750972552415.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp2_pp0_tp0_dcp0_ep4_rank0.1795684750972552415.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 4 | 880.320 | 878.634 | 1276.330 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.879 | 61.059 | 69.890 | 386.816 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 85.481 | 63.602 | 115.335 | 179.071 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 73.521 | 54.703 | 92.371 | 131.170 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.087 | 17.885 | 32.150 | 49.641 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 51.243 | 38.127 | 21.180 | 3205.055 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.902 | 14.896 | 15.360 | 16.140 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.142 | 14.797 | 15.140 | 15.590 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 42.040 | 31.280 | 49.871 | 69.550 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 35.014 | 26.052 | 26.759 | 27.350 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.528 | 28.978 | 30.910 | 33.170 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.288 | 10.631 | 10.890 | 11.190 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 13.796 | 431.128 | 902.396 | 7116.604 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.246 | 12.174 | 12.480 | 12.730 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.611 | 35.827 | 36.080 | 36.330 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.541 | 8.587 | 8.740 | 8.970 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.949 | 8.147 | 8.399 | 8.650 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.469 | 4.811 | 5.060 | 5.490 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.364 | 3.305 | 3.890 | 4.970 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.736 | 3.203 | 3.410 | 5.810 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.075 | 6.302 | 8.780 | 13.300 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 19.028 | 16.517 |
| `aten::to` | 640 | 15.542 | 24.285 |
| `aten::_to_copy` | 448 | 14.776 | 32.983 |
| `vllm::all_gather` | 32 | 8.106 | 253.311 |
| `aten::slice` | 2624 | 7.928 | 3.021 |
| `c10d::_allgather_base_` | 32 | 5.229 | 163.409 |
| `aten::index` | 128 | 5.134 | 40.110 |
| `aten::fill_` | 704 | 4.949 | 7.029 |
| `record_param_comms` | 32 | 4.581 | 143.164 |
| `aten::select` | 1472 | 3.954 | 2.686 |

## l16384-o200-c4_dp2_pp0_tp1_dcp0_ep5_rank1.1795684750994728042.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp2_pp0_tp1_dcp0_ep5_rank1.1795684750994728042.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 5 | 868.574 | 867.029 | 1268.616 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 90.040 | 66.994 | 114.593 | 169.150 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.707 | 60.942 | 69.784 | 387.840 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 69.447 | 51.672 | 92.099 | 120.930 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.821 | 18.119 | 33.193 | 50.791 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 50.918 | 37.885 | 20.729 | 3204.978 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.834 | 14.873 | 15.330 | 15.890 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.137 | 14.795 | 15.160 | 15.600 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 40.210 | 29.918 | 49.659 | 63.810 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.699 | 25.818 | 26.590 | 27.430 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.531 | 28.981 | 30.580 | 33.260 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.275 | 10.621 | 10.890 | 11.130 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.232 | 12.162 | 12.446 | 12.930 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.636 | 35.898 | 36.150 | 36.390 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.489 | 8.548 | 8.720 | 8.880 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.970 | 8.163 | 8.410 | 8.790 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.403 | 4.781 | 5.040 | 5.320 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.341 | 3.298 | 3.863 | 4.920 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.730 | 3.201 | 3.420 | 5.430 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.284 | 6.447 | 8.791 | 11.800 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 8.993 | 25.547 | 27.210 | 27.690 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 15.475 | 14.223 |
| `aten::to` | 544 | 10.327 | 18.983 |
| `aten::_to_copy` | 384 | 9.680 | 25.209 |
| `aten::slice` | 2624 | 8.406 | 3.203 |
| `vllm::all_gather` | 32 | 8.041 | 251.276 |
| `aten::fill_` | 704 | 5.323 | 7.561 |
| `c10d::_allgather_base_` | 32 | 5.202 | 162.574 |
| `aten::index` | 128 | 4.807 | 37.557 |
| `record_param_comms` | 32 | 4.542 | 141.930 |
| `aten::select` | 1472 | 4.091 | 2.779 |

## l16384-o200-c4_dp3_pp0_tp0_dcp0_ep6_rank0.1795684762108641869.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp3_pp0_tp0_dcp0_ep6_rank0.1795684762108641869.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 6 | 1515.054 | 1513.485 | 12317.902 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 669.660 | 20926.883 | 3191.746 | 642616.887 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.755 | 60.975 | 69.700 | 386.304 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 88.721 | 66.013 | 116.818 | 171.830 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 71.510 | 53.207 | 93.110 | 123.030 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.207 | 17.923 | 32.292 | 50.400 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.863 | 14.883 | 15.340 | 15.820 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.108 | 14.785 | 15.140 | 15.450 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 41.624 | 30.970 | 50.591 | 65.120 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.314 | 25.531 | 26.350 | 26.890 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.322 | 28.789 | 30.476 | 32.250 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 29.932 | 22.271 | 22.070 | 810.781 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.311 | 10.648 | 10.900 | 11.150 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.237 | 12.167 | 12.520 | 12.900 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.626 | 35.871 | 36.135 | 36.260 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.525 | 8.575 | 8.740 | 8.990 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.885 | 8.099 | 8.310 | 9.010 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.509 | 4.830 | 5.180 | 7.123 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.287 | 3.280 | 3.480 | 4.690 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.759 | 3.210 | 3.420 | 6.770 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.336 | 6.483 | 8.870 | 11.970 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 18.743 | 16.270 |
| `aten::to` | 640 | 15.005 | 23.446 |
| `aten::_to_copy` | 448 | 13.990 | 31.228 |
| `vllm::all_gather` | 32 | 8.350 | 260.923 |
| `aten::slice` | 2624 | 8.286 | 3.158 |
| `aten::index` | 128 | 5.352 | 41.812 |
| `c10d::_allgather_base_` | 32 | 5.345 | 167.022 |
| `aten::fill_` | 704 | 5.186 | 7.367 |
| `record_param_comms` | 32 | 4.684 | 146.370 |
| `aten::select` | 1472 | 4.180 | 2.840 |

## l16384-o200-c4_dp3_pp0_tp1_dcp0_ep7_rank1.1795684762097773560.pt.trace.json.gz

[完整算子表](l16384-o200-c4_dp3_pp0_tp1_dcp0_ep7_rank1.1795684762097773560.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 7 | 844.790 | 843.119 | 12317.592 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.802 | 61.007 | 69.765 | 386.048 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 82.254 | 61.201 | 114.426 | 160.851 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 74.098 | 55.132 | 93.906 | 123.850 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.538 | 18.029 | 32.620 | 50.061 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 43.360 | 32.262 | 51.518 | 66.551 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.849 | 14.878 | 15.321 | 15.920 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.229 | 14.828 | 15.180 | 15.620 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.372 | 25.575 | 26.479 | 27.330 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.384 | 28.846 | 30.561 | 33.061 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 29.606 | 22.028 | 21.898 | 810.433 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.300 | 10.640 | 10.890 | 11.190 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.255 | 12.183 | 12.481 | 13.020 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.635 | 35.896 | 36.175 | 36.320 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.562 | 8.603 | 8.790 | 9.310 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.906 | 8.114 | 8.391 | 8.610 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.454 | 4.804 | 5.060 | 5.450 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.261 | 3.272 | 3.410 | 4.630 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.780 | 3.217 | 3.430 | 5.530 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 8.953 | 25.434 | 27.274 | 27.710 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 8.918 | 6.193 | 8.420 | 12.160 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 17.860 | 16.415 |
| `aten::to` | 544 | 12.303 | 22.616 |
| `aten::_to_copy` | 384 | 11.559 | 30.103 |
| `aten::slice` | 2624 | 10.471 | 3.990 |
| `vllm::all_gather` | 32 | 9.630 | 300.939 |
| `aten::fill_` | 704 | 7.124 | 10.119 |
| `aten::arange` | 64 | 6.863 | 107.235 |
| `c10d::_allgather_base_` | 32 | 6.428 | 200.863 |
| `record_param_comms` | 32 | 5.704 | 178.258 |
| `aten::index` | 128 | 5.424 | 42.373 |

## l4096-o200-c4_dp0_pp0_tp0_dcp0_ep0_rank0.1795684637283592567.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp0_pp0_tp0_dcp0_ep0_rank0.1795684637283592567.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 0 | 852.702 | 851.144 | 1238.875 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 98.885 | 73.575 | 123.226 | 186.820 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.830 | 61.026 | 69.879 | 387.072 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 62.832 | 46.750 | 90.131 | 120.510 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 55.935 | 17.836 | 32.212 | 49.790 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.825 | 14.870 | 15.270 | 15.700 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.081 | 14.776 | 15.160 | 15.750 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 41.522 | 30.895 | 20.515 | 1824.419 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 35.281 | 26.250 | 48.200 | 62.440 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.850 | 25.930 | 26.729 | 27.620 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 30.951 | 28.448 | 29.877 | 32.470 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.281 | 10.626 | 10.890 | 11.180 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.218 | 12.149 | 12.461 | 12.810 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.621 | 35.856 | 36.135 | 36.270 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.530 | 8.579 | 8.750 | 8.990 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.898 | 8.109 | 8.390 | 8.680 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.621 | 4.881 | 5.110 | 5.400 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.291 | 3.282 | 3.433 | 4.690 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.757 | 3.210 | 3.440 | 6.380 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 8.954 | 6.218 | 8.570 | 12.820 |
| `triton_poi_fused_clamp_copy__mul_silu_slice_0` | 1344 | 8.494 | 6.320 | 6.570 | 8.200 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 19.883 | 17.259 |
| `aten::to` | 640 | 15.729 | 24.577 |
| `aten::_to_copy` | 448 | 14.944 | 33.358 |
| `aten::slice` | 2624 | 8.900 | 3.392 |
| `vllm::all_gather` | 32 | 8.294 | 259.185 |
| `aten::fill_` | 704 | 5.421 | 7.701 |
| `c10d::_allgather_base_` | 32 | 5.353 | 167.275 |
| `aten::index` | 128 | 5.117 | 39.978 |
| `record_param_comms` | 32 | 4.671 | 145.979 |
| `aten::select` | 1472 | 4.641 | 3.153 |

## l4096-o200-c4_dp0_pp0_tp1_dcp0_ep1_rank1.1795684637257708388.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp0_pp0_tp1_dcp0_ep1_rank1.1795684637257708388.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 1 | 851.465 | 849.926 | 1238.926 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.812 | 61.013 | 69.736 | 387.072 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 82.323 | 61.253 | 117.574 | 171.922 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 73.203 | 54.467 | 90.517 | 124.821 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.380 | 17.978 | 32.500 | 50.210 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.852 | 14.879 | 15.330 | 15.980 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.130 | 14.793 | 15.150 | 15.500 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 41.107 | 30.585 | 20.160 | 1823.067 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 40.584 | 30.196 | 48.310 | 65.450 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.791 | 25.886 | 26.770 | 27.420 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.114 | 28.597 | 30.310 | 32.170 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.297 | 10.638 | 10.890 | 11.130 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.259 | 12.186 | 12.520 | 12.960 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.628 | 35.874 | 36.140 | 36.261 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.545 | 8.590 | 8.790 | 9.040 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.927 | 8.130 | 8.390 | 8.770 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.545 | 4.846 | 5.181 | 5.550 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.274 | 3.276 | 3.420 | 4.860 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.749 | 3.207 | 3.430 | 7.580 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.223 | 6.405 | 9.001 | 12.810 |
| `triton_poi_fused_clamp_copy__mul_silu_slice_0` | 1344 | 8.489 | 6.316 | 6.500 | 9.690 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 15.262 | 14.027 |
| `aten::to` | 544 | 10.462 | 19.232 |
| `aten::_to_copy` | 384 | 9.844 | 25.636 |
| `aten::slice` | 2624 | 9.817 | 3.741 |
| `vllm::all_gather` | 32 | 8.238 | 257.428 |
| `aten::fill_` | 704 | 5.370 | 7.627 |
| `c10d::_allgather_base_` | 32 | 5.325 | 166.420 |
| `aten::index` | 128 | 4.943 | 38.614 |
| `aten::select` | 1472 | 4.757 | 3.232 |
| `record_param_comms` | 32 | 4.624 | 144.497 |

## l4096-o200-c4_dp1_pp0_tp0_dcp0_ep2_rank0.1795684646837008306.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp1_pp0_tp0_dcp0_ep2_rank0.1795684646837008306.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 2 | 858.513 | 856.820 | 10796.128 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.883 | 61.062 | 69.965 | 387.072 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 81.965 | 60.986 | 88.399 | 125.319 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 69.208 | 51.494 | 109.943 | 173.730 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.569 | 18.039 | 32.612 | 50.520 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 44.632 | 33.208 | 47.228 | 66.379 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.876 | 14.888 | 15.320 | 15.770 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.201 | 14.818 | 15.150 | 15.630 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.825 | 25.912 | 26.930 | 27.440 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.298 | 28.767 | 30.486 | 33.870 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 28.858 | 21.472 | 20.987 | 1295.521 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 22.019 | 688.108 | 1844.233 | 2144.429 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.302 | 10.641 | 10.900 | 11.250 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.258 | 12.186 | 12.460 | 12.730 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.619 | 35.848 | 36.075 | 36.200 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.545 | 8.590 | 8.760 | 9.050 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.908 | 8.116 | 8.410 | 8.740 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.511 | 4.831 | 5.110 | 5.380 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.263 | 3.273 | 3.430 | 4.410 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.765 | 3.212 | 3.420 | 6.180 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.116 | 6.330 | 8.751 | 12.570 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 17.865 | 15.508 |
| `aten::to` | 640 | 13.999 | 21.873 |
| `aten::_to_copy` | 448 | 13.123 | 29.293 |
| `aten::slice` | 2624 | 8.347 | 3.181 |
| `vllm::all_gather` | 32 | 8.172 | 255.390 |
| `c10d::_allgather_base_` | 32 | 5.224 | 163.240 |
| `aten::index` | 128 | 4.965 | 38.791 |
| `aten::fill_` | 704 | 4.938 | 7.014 |
| `record_param_comms` | 32 | 4.537 | 141.791 |
| `aten::select` | 1472 | 4.416 | 3.000 |

## l4096-o200-c4_dp1_pp0_tp1_dcp0_ep3_rank1.1795684646841140874.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp1_pp0_tp1_dcp0_ep3_rank1.1795684646841140874.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 3 | 932.516 | 930.876 | 10795.888 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 93.554 | 2923.562 | 199.825 | 92983.293 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.890 | 61.067 | 69.975 | 387.328 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 78.257 | 58.227 | 118.375 | 163.701 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 77.624 | 57.756 | 92.130 | 123.209 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.714 | 18.085 | 32.970 | 50.440 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 43.108 | 32.075 | 49.627 | 64.550 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.861 | 14.882 | 15.330 | 15.880 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.196 | 14.816 | 15.170 | 15.499 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.291 | 25.514 | 26.210 | 26.770 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.478 | 28.932 | 30.767 | 32.810 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 28.825 | 21.447 | 20.967 | 1294.804 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.298 | 10.638 | 10.900 | 11.130 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.279 | 12.205 | 12.546 | 12.930 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.622 | 35.859 | 36.080 | 36.320 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.528 | 8.577 | 8.731 | 9.091 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.995 | 8.181 | 8.410 | 8.660 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.453 | 4.804 | 5.060 | 5.350 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.296 | 3.283 | 3.430 | 4.570 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.755 | 3.209 | 3.430 | 6.340 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.089 | 6.312 | 8.703 | 13.570 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 17.018 | 15.642 |
| `aten::to` | 544 | 11.830 | 21.747 |
| `aten::_to_copy` | 384 | 11.147 | 29.028 |
| `aten::slice` | 2624 | 10.451 | 3.983 |
| `vllm::all_gather` | 32 | 8.583 | 268.219 |
| `aten::fill_` | 704 | 6.118 | 8.690 |
| `c10d::_allgather_base_` | 32 | 5.575 | 174.228 |
| `aten::select` | 1472 | 5.238 | 3.558 |
| `aten::arange` | 64 | 5.142 | 80.341 |
| `aten::index` | 128 | 5.055 | 39.495 |

## l4096-o200-c4_dp2_pp0_tp0_dcp0_ep4_rank0.1795684637257247910.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp2_pp0_tp0_dcp0_ep4_rank0.1795684637257247910.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 4 | 853.591 | 851.886 | 1238.803 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.887 | 61.064 | 69.905 | 386.560 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 84.074 | 62.555 | 112.442 | 167.580 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 71.394 | 53.121 | 92.009 | 130.630 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.071 | 17.880 | 32.215 | 49.980 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.899 | 14.896 | 15.360 | 15.850 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.138 | 14.796 | 15.150 | 15.540 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 40.876 | 30.414 | 49.384 | 70.180 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 36.611 | 27.240 | 20.509 | 1738.454 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 35.013 | 26.051 | 26.760 | 27.390 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.481 | 28.934 | 30.790 | 32.600 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.285 | 10.628 | 10.890 | 11.160 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.263 | 12.190 | 12.530 | 12.850 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.613 | 35.833 | 36.070 | 36.380 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.544 | 8.589 | 8.750 | 8.940 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.952 | 8.149 | 8.410 | 8.780 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.474 | 4.814 | 5.070 | 5.330 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.370 | 3.307 | 3.890 | 4.850 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.760 | 3.211 | 3.420 | 6.420 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 9.208 | 287.758 | 780.066 | 1096.962 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.115 | 6.330 | 8.730 | 14.240 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 18.719 | 16.249 |
| `aten::to` | 640 | 15.297 | 23.902 |
| `aten::_to_copy` | 448 | 14.514 | 32.398 |
| `aten::slice` | 2624 | 8.891 | 3.388 |
| `vllm::all_gather` | 32 | 8.454 | 264.203 |
| `c10d::_allgather_base_` | 32 | 5.520 | 172.492 |
| `aten::fill_` | 704 | 5.263 | 7.476 |
| `aten::index` | 128 | 5.238 | 40.924 |
| `record_param_comms` | 32 | 4.833 | 151.047 |
| `aten::select` | 1472 | 4.567 | 3.102 |

## l4096-o200-c4_dp2_pp0_tp1_dcp0_ep5_rank1.1795684637255952660.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp2_pp0_tp1_dcp0_ep5_rank1.1795684637255952660.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 5 | 844.216 | 842.568 | 1238.930 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 89.739 | 66.770 | 117.891 | 164.000 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.731 | 60.958 | 69.799 | 386.048 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 66.636 | 49.580 | 91.805 | 100.220 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.819 | 18.118 | 33.123 | 50.730 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.849 | 14.878 | 15.350 | 15.849 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.146 | 14.798 | 15.160 | 15.500 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 38.762 | 28.841 | 49.430 | 55.020 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 36.265 | 26.983 | 19.817 | 1738.967 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.687 | 25.808 | 26.600 | 27.120 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.536 | 28.985 | 30.656 | 32.070 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.289 | 10.632 | 10.909 | 11.190 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.235 | 12.165 | 12.500 | 12.830 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.634 | 35.893 | 36.150 | 36.330 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.490 | 8.549 | 8.720 | 8.930 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.979 | 8.169 | 8.410 | 8.659 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.399 | 4.779 | 5.040 | 5.510 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.332 | 3.295 | 3.500 | 4.650 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.756 | 3.209 | 3.430 | 5.410 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.223 | 6.405 | 8.800 | 12.640 |
| `triton_poi_fused_clamp_copy__mul_silu_slice_0` | 1344 | 8.518 | 6.338 | 6.610 | 8.410 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 16.915 | 15.547 |
| `aten::to` | 544 | 11.476 | 21.096 |
| `aten::_to_copy` | 384 | 10.859 | 28.280 |
| `aten::slice` | 2624 | 9.947 | 3.791 |
| `vllm::all_gather` | 32 | 8.910 | 278.423 |
| `aten::arange` | 64 | 7.260 | 113.436 |
| `aten::fill_` | 704 | 6.019 | 8.549 |
| `c10d::_allgather_base_` | 32 | 5.862 | 183.178 |
| `aten::index` | 128 | 5.561 | 43.446 |
| `record_param_comms` | 32 | 5.144 | 160.749 |

## l4096-o200-c4_dp3_pp0_tp0_dcp0_ep6_rank0.1795684637262139873.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp3_pp0_tp0_dcp0_ep6_rank0.1795684637262139873.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 6 | 855.143 | 853.522 | 1238.816 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.776 | 60.989 | 69.759 | 387.328 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 88.270 | 65.677 | 116.680 | 175.251 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 68.512 | 50.977 | 93.341 | 123.580 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.163 | 17.909 | 32.292 | 50.079 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.842 | 14.876 | 15.340 | 15.870 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.109 | 14.785 | 15.140 | 15.479 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 40.588 | 30.199 | 20.998 | 1947.905 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 39.961 | 29.733 | 50.669 | 65.290 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.332 | 25.545 | 26.370 | 26.870 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.356 | 28.820 | 30.710 | 33.160 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.301 | 10.640 | 10.890 | 11.160 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.260 | 12.187 | 12.520 | 12.880 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.628 | 35.875 | 36.080 | 36.380 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.524 | 8.574 | 8.740 | 9.010 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.881 | 8.096 | 8.300 | 8.540 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.503 | 4.827 | 5.160 | 5.520 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.292 | 3.282 | 3.482 | 4.650 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.749 | 3.207 | 3.420 | 6.260 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.722 | 6.752 | 9.640 | 14.770 |
| `triton_poi_fused_clamp_copy__mul_silu_slice_0` | 1344 | 8.498 | 6.323 | 6.510 | 7.390 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 17.931 | 15.565 |
| `aten::to` | 640 | 14.496 | 22.649 |
| `aten::_to_copy` | 448 | 13.680 | 30.535 |
| `aten::slice` | 2624 | 8.842 | 3.369 |
| `vllm::all_gather` | 32 | 8.181 | 255.654 |
| `aten::fill_` | 704 | 5.389 | 7.654 |
| `c10d::_allgather_base_` | 32 | 5.196 | 162.362 |
| `aten::index` | 128 | 5.016 | 39.185 |
| `record_param_comms` | 32 | 4.521 | 141.274 |
| `aten::select` | 1472 | 4.287 | 2.913 |

## l4096-o200-c4_dp3_pp0_tp1_dcp0_ep7_rank1.1795684637256356723.pt.trace.json.gz

[完整算子表](l4096-o200-c4_dp3_pp0_tp1_dcp0_ep7_rank1.1795684637256356723.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 7 | 853.016 | 851.344 | 1238.913 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.830 | 61.026 | 69.770 | 387.328 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 82.765 | 61.581 | 113.519 | 178.659 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 70.250 | 52.270 | 93.344 | 123.161 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.533 | 18.027 | 32.670 | 50.400 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.830 | 14.872 | 15.320 | 16.070 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.220 | 14.824 | 15.170 | 15.610 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 41.256 | 30.697 | 50.700 | 66.121 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 40.305 | 29.989 | 20.849 | 1947.457 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.382 | 25.582 | 26.500 | 27.190 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.351 | 28.815 | 30.667 | 33.360 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.295 | 10.636 | 10.890 | 11.240 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.257 | 12.185 | 12.480 | 12.770 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.629 | 35.879 | 36.090 | 36.440 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.557 | 8.599 | 8.778 | 9.090 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.904 | 8.113 | 8.350 | 8.600 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.456 | 4.805 | 5.060 | 5.430 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.278 | 3.277 | 3.420 | 4.700 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.793 | 3.221 | 3.430 | 6.420 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 8.778 | 6.096 | 8.082 | 10.960 |
| `triton_poi_fused_clamp_copy__mul_silu_slice_0` | 1344 | 8.508 | 6.330 | 6.560 | 8.340 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 15.200 | 13.970 |
| `aten::to` | 544 | 10.467 | 19.241 |
| `aten::_to_copy` | 384 | 9.825 | 25.587 |
| `aten::slice` | 2624 | 8.773 | 3.343 |
| `vllm::all_gather` | 32 | 8.088 | 252.736 |
| `c10d::_allgather_base_` | 32 | 5.205 | 162.660 |
| `aten::fill_` | 704 | 5.168 | 7.341 |
| `aten::index` | 128 | 4.769 | 37.257 |
| `record_param_comms` | 32 | 4.531 | 141.608 |
| `aten::select` | 1472 | 4.461 | 3.031 |

## l65536-o200-c4_dp0_pp0_tp0_dcp0_ep0_rank0.1795684946051006026.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp0_pp0_tp0_dcp0_ep0_rank0.1795684946051006026.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 0 | 871.440 | 869.817 | 1271.535 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 102.071 | 75.945 | 128.946 | 175.531 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.823 | 61.021 | 69.825 | 386.560 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 65.062 | 48.409 | 90.160 | 121.911 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 55.930 | 17.835 | 32.102 | 50.330 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.886 | 14.891 | 15.311 | 15.780 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.121 | 14.790 | 15.150 | 15.550 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 36.370 | 27.061 | 48.005 | 64.030 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.783 | 25.880 | 26.680 | 27.330 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 34.672 | 25.798 | 21.145 | 1485.111 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 30.977 | 28.471 | 29.830 | 32.720 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 14.617 | 456.782 | 1584.277 | 5220.908 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.295 | 10.636 | 10.890 | 11.150 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.742 | 39.039 | 41.248 | 41.980 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.234 | 12.164 | 12.460 | 12.720 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.628 | 35.875 | 36.145 | 36.310 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.535 | 8.582 | 8.750 | 8.990 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.906 | 8.115 | 8.390 | 8.590 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.630 | 4.885 | 5.120 | 5.480 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.301 | 3.285 | 3.433 | 4.710 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.767 | 3.213 | 3.440 | 5.500 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 19.742 | 17.138 |
| `aten::to` | 640 | 15.889 | 24.826 |
| `aten::_to_copy` | 448 | 15.099 | 33.703 |
| `vllm::all_gather` | 32 | 8.434 | 263.561 |
| `aten::slice` | 2624 | 7.988 | 3.044 |
| `aten::fill_` | 704 | 5.625 | 7.991 |
| `c10d::_allgather_base_` | 32 | 5.459 | 170.588 |
| `aten::index` | 128 | 5.169 | 40.385 |
| `record_param_comms` | 32 | 4.780 | 149.370 |
| `aten::select` | 1472 | 4.170 | 2.833 |

## l65536-o200-c4_dp0_pp0_tp1_dcp0_ep1_rank1.1795684946029325940.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp0_pp0_tp1_dcp0_ep1_rank1.1795684946029325940.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 1 | 860.318 | 858.766 | 1266.322 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.826 | 61.023 | 69.885 | 387.584 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 86.032 | 64.012 | 121.350 | 196.360 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 74.986 | 55.793 | 91.007 | 124.690 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.443 | 17.998 | 32.523 | 51.310 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.874 | 14.887 | 15.330 | 16.001 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.122 | 14.790 | 15.140 | 15.560 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 41.434 | 30.829 | 48.750 | 66.150 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.777 | 25.875 | 26.738 | 27.430 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 34.254 | 25.487 | 20.860 | 1484.103 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.091 | 28.576 | 30.337 | 32.230 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.301 | 10.641 | 10.890 | 11.191 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.742 | 39.041 | 41.280 | 41.860 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.246 | 12.175 | 12.480 | 12.840 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.631 | 35.884 | 36.160 | 36.410 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.539 | 8.585 | 8.790 | 9.000 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.912 | 8.119 | 8.340 | 8.670 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.540 | 4.844 | 5.180 | 5.530 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.274 | 3.276 | 3.422 | 4.880 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.748 | 3.207 | 3.420 | 6.960 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.135 | 6.343 | 8.560 | 15.860 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 16.056 | 14.757 |
| `aten::to` | 544 | 10.696 | 19.661 |
| `aten::_to_copy` | 384 | 10.083 | 26.258 |
| `aten::slice` | 2624 | 9.354 | 3.565 |
| `vllm::all_gather` | 32 | 8.206 | 256.441 |
| `aten::fill_` | 704 | 5.406 | 7.679 |
| `c10d::_allgather_base_` | 32 | 5.302 | 165.693 |
| `aten::index` | 128 | 4.878 | 38.112 |
| `record_param_comms` | 32 | 4.637 | 144.916 |
| `aten::arange` | 64 | 4.585 | 71.636 |

## l65536-o200-c4_dp1_pp0_tp0_dcp0_ep2_rank0.1795684946021590750.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp1_pp0_tp0_dcp0_ep2_rank0.1795684946021590750.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 2 | 875.071 | 873.324 | 1271.492 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.841 | 61.034 | 69.814 | 389.376 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 85.612 | 63.699 | 90.948 | 129.251 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 69.023 | 51.356 | 111.378 | 168.640 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.581 | 18.042 | 32.575 | 50.731 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 46.504 | 34.601 | 48.346 | 68.090 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.873 | 14.887 | 15.340 | 15.850 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.207 | 14.820 | 15.150 | 15.630 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 36.935 | 27.481 | 22.540 | 1371.305 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.795 | 25.889 | 26.890 | 27.550 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.322 | 28.788 | 30.481 | 33.810 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 16.882 | 527.563 | 1234.578 | 4928.418 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.304 | 10.643 | 10.890 | 11.240 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.722 | 38.982 | 41.355 | 41.940 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.258 | 12.186 | 12.496 | 12.910 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.630 | 35.881 | 36.135 | 36.290 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.550 | 8.594 | 8.810 | 9.010 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.907 | 8.116 | 8.410 | 8.760 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.511 | 4.830 | 5.090 | 5.360 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.274 | 3.276 | 3.430 | 4.840 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.779 | 3.217 | 3.420 | 5.990 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 18.429 | 15.997 |
| `aten::to` | 640 | 14.586 | 22.790 |
| `aten::_to_copy` | 448 | 13.803 | 30.810 |
| `vllm::all_gather` | 32 | 8.181 | 255.652 |
| `aten::slice` | 2624 | 8.009 | 3.052 |
| `aten::fill_` | 704 | 5.278 | 7.498 |
| `c10d::_allgather_base_` | 32 | 5.221 | 163.171 |
| `aten::index` | 128 | 4.994 | 39.012 |
| `record_param_comms` | 32 | 4.554 | 142.319 |
| `aten::select` | 1472 | 4.018 | 2.730 |

## l65536-o200-c4_dp1_pp0_tp1_dcp0_ep3_rank1.1795684946064683655.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp1_pp0_tp1_dcp0_ep3_rank1.1795684946064683655.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 3 | 863.162 | 861.491 | 1266.333 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.873 | 61.055 | 69.964 | 386.304 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 80.755 | 60.085 | 93.102 | 126.611 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 78.717 | 58.569 | 117.000 | 182.880 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.676 | 18.073 | 32.895 | 50.459 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 44.945 | 33.441 | 50.212 | 67.350 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.863 | 14.883 | 15.350 | 15.972 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.187 | 14.813 | 15.150 | 15.530 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 36.927 | 27.475 | 22.638 | 1373.042 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.265 | 25.495 | 26.250 | 26.810 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.464 | 28.919 | 30.846 | 32.714 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.309 | 10.647 | 10.910 | 11.150 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.710 | 38.950 | 41.254 | 41.890 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.274 | 12.201 | 12.567 | 13.020 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.624 | 35.863 | 36.087 | 36.354 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.525 | 8.575 | 8.730 | 8.980 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 11.010 | 8.192 | 8.420 | 8.670 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.458 | 4.806 | 5.070 | 5.380 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.311 | 3.288 | 3.430 | 4.790 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.742 | 3.205 | 3.420 | 6.000 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 8.961 | 6.223 | 8.420 | 11.770 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 16.534 | 15.197 |
| `aten::to` | 544 | 11.269 | 20.714 |
| `aten::_to_copy` | 384 | 10.635 | 27.695 |
| `aten::slice` | 2624 | 8.863 | 3.378 |
| `vllm::all_gather` | 32 | 8.411 | 262.839 |
| `aten::fill_` | 704 | 6.369 | 9.047 |
| `aten::arange` | 64 | 5.853 | 91.453 |
| `c10d::_allgather_base_` | 32 | 5.460 | 170.614 |
| `aten::index` | 128 | 4.904 | 38.310 |
| `record_param_comms` | 32 | 4.785 | 149.544 |

## l65536-o200-c4_dp2_pp0_tp0_dcp0_ep4_rank0.1795684946009836578.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp2_pp0_tp0_dcp0_ep4_rank0.1795684946009836578.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 4 | 875.457 | 873.803 | 1271.479 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.894 | 61.069 | 69.890 | 386.560 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 86.418 | 64.299 | 118.129 | 165.121 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 73.728 | 54.857 | 92.761 | 130.270 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.068 | 17.879 | 32.182 | 49.690 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 43.111 | 32.077 | 22.033 | 1499.469 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.917 | 14.902 | 15.360 | 15.970 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.136 | 14.795 | 15.150 | 15.530 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 42.116 | 31.336 | 50.134 | 69.211 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 35.063 | 26.089 | 26.790 | 27.350 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.485 | 28.939 | 30.713 | 32.580 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.282 | 10.626 | 10.880 | 11.150 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.709 | 38.945 | 41.230 | 42.490 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.259 | 12.187 | 12.531 | 12.880 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.614 | 35.835 | 36.070 | 36.330 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.545 | 8.590 | 8.750 | 9.060 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.954 | 8.150 | 8.400 | 8.800 |
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 10.622 | 331.942 | 898.276 | 5025.227 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.474 | 4.813 | 5.060 | 5.350 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.363 | 3.305 | 3.890 | 4.580 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.734 | 3.202 | 3.410 | 5.250 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 17.824 | 15.472 |
| `aten::to` | 640 | 14.181 | 22.158 |
| `aten::_to_copy` | 448 | 13.396 | 29.903 |
| `aten::slice` | 2624 | 8.127 | 3.097 |
| `vllm::all_gather` | 32 | 8.066 | 252.053 |
| `c10d::_allgather_base_` | 32 | 5.180 | 161.884 |
| `aten::fill_` | 704 | 5.154 | 7.321 |
| `aten::index` | 128 | 4.866 | 38.019 |
| `record_param_comms` | 32 | 4.533 | 141.643 |
| `aten::select` | 1472 | 3.997 | 2.715 |

## l65536-o200-c4_dp2_pp0_tp1_dcp0_ep5_rank1.1795684946023067285.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp2_pp0_tp1_dcp0_ep5_rank1.1795684946023067285.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 5 | 865.938 | 864.292 | 1266.318 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.717 | 60.949 | 69.760 | 387.328 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 86.057 | 64.031 | 114.631 | 163.590 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 72.861 | 54.212 | 92.614 | 122.801 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.834 | 18.123 | 33.250 | 51.149 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.853 | 14.880 | 15.340 | 16.040 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 42.744 | 31.804 | 21.575 | 1498.327 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.140 | 14.796 | 15.160 | 15.600 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 41.987 | 31.240 | 50.295 | 65.580 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.705 | 25.822 | 26.560 | 27.300 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.555 | 29.003 | 30.566 | 32.381 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.284 | 10.628 | 10.890 | 11.190 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.714 | 38.960 | 41.255 | 42.080 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.228 | 12.158 | 12.460 | 12.770 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.636 | 35.898 | 36.170 | 36.450 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.491 | 8.550 | 8.720 | 8.908 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.962 | 8.156 | 8.410 | 8.580 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.406 | 4.782 | 5.050 | 5.410 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.336 | 3.296 | 3.555 | 4.240 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.737 | 3.203 | 3.420 | 6.060 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 9.210 | 6.396 | 8.694 | 13.000 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 15.834 | 14.553 |
| `aten::to` | 544 | 10.365 | 19.053 |
| `aten::_to_copy` | 384 | 9.765 | 25.431 |
| `aten::slice` | 2624 | 8.624 | 3.286 |
| `vllm::all_gather` | 32 | 7.952 | 248.489 |
| `aten::fill_` | 704 | 5.447 | 7.737 |
| `c10d::_allgather_base_` | 32 | 5.119 | 159.974 |
| `aten::index` | 128 | 4.806 | 37.547 |
| `aten::arange` | 64 | 4.554 | 71.152 |
| `record_param_comms` | 32 | 4.468 | 139.637 |

## l65536-o200-c4_dp3_pp0_tp0_dcp0_ep6_rank0.1795684957090602872.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp3_pp0_tp0_dcp0_ep6_rank0.1795684957090602872.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 6 | 1342.338 | 1340.627 | 12269.236 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `mcclKernel_AllReduce_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 32 | 485.433 | 15169.777 | 1243.938 | 478259.363 |
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.762 | 60.980 | 69.730 | 386.816 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 89.594 | 66.662 | 118.167 | 206.640 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 71.736 | 53.375 | 92.930 | 122.511 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.213 | 17.925 | 32.302 | 49.990 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.868 | 14.885 | 15.370 | 15.940 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.117 | 14.788 | 15.140 | 15.660 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 41.783 | 31.089 | 50.487 | 65.310 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 34.803 | 25.895 | 22.300 | 1473.689 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.330 | 25.543 | 26.370 | 26.990 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.349 | 28.814 | 30.696 | 32.100 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.305 | 10.643 | 10.890 | 11.160 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.765 | 39.104 | 41.460 | 42.110 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.257 | 12.185 | 12.526 | 12.910 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.629 | 35.879 | 36.140 | 36.441 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.519 | 8.571 | 8.740 | 8.940 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.886 | 8.099 | 8.300 | 8.650 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.519 | 4.834 | 5.180 | 5.580 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.290 | 3.281 | 3.480 | 4.840 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.764 | 3.212 | 3.430 | 7.660 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1152 | 20.708 | 17.976 |
| `aten::to` | 640 | 16.713 | 26.114 |
| `aten::_to_copy` | 448 | 15.640 | 34.911 |
| `aten::slice` | 2624 | 8.454 | 3.222 |
| `vllm::all_gather` | 32 | 8.403 | 262.589 |
| `aten::fill_` | 704 | 5.803 | 8.243 |
| `c10d::_allgather_base_` | 32 | 5.416 | 169.246 |
| `aten::index` | 128 | 5.103 | 39.864 |
| `record_param_comms` | 32 | 4.731 | 147.835 |
| `aten::select` | 1472 | 4.587 | 3.116 |

## l65536-o200-c4_dp3_pp0_tp1_dcp0_ep7_rank1.1795684957080990061.pt.trace.json.gz

[完整算子表](l65536-o200-c4_dp3_pp0_tp1_dcp0_ep7_rank1.1795684957080990061.pt.trace-summary.json)；GPU kernel 调用数：79712。

| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |
|---|---:|---:|---:|
| 7 | 857.769 | 856.078 | 12268.805 |

迭代标注：`{"execute_context_0(0)_generation_1(1)": 32}`。图重放事件：`{"mcGraphLaunch": 32}`。

| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |
|---|---:|---:|---:|---:|---:|
| `void b16gemvt_wave_kernel<64, 2, 8, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long,  … #586a4863c8` | 1472 | 89.788 | 60.997 | 69.845 | 386.048 |
| `mcclKernel_ReduceScatter_HFC8_Sum_mccl_bfloat16(fcinfo)` | 1344 | 83.126 | 61.850 | 116.310 | 170.280 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #82685fe90c` | 1344 | 74.270 | 55.261 | 94.189 | 123.191 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmUniversal<mctlass::gemm::threadblock::MacaMmaMultistage<mctlass::gemm::GemmShape<16, 64, 256> … #f00f87c91f` | 3136 | 56.534 | 18.027 | 32.580 | 49.970 |
| `void mctlass::Kernel<mctlass::gemm::kernel::MacaGemmMoe<mctlass::gemm::threadblock::MacaMoeMmaMultistage<mctlass::gemm::GemmShape<16, 128, 256>,  … #201efafdcf` | 1344 | 43.459 | 32.336 | 51.498 | 66.251 |
| `mhc_pre_big_fuse_with_norm_tilelang_kernel` | 2880 | 42.842 | 14.876 | 15.320 | 15.930 |
| `mhc_fused_tilelang_kernel` | 2848 | 42.237 | 14.830 | 15.180 | 15.601 |
| `mcclkernel_AllGather_HFC8_int8_t(fcinfo)` | 1344 | 34.415 | 25.606 | 21.919 | 1473.455 |
| `mcclKernel_AllGather_RING_LL_Sum_int8_t(mcclKernelComm*, unsigned long, mcclWork*)` | 1344 | 34.339 | 25.550 | 26.420 | 27.090 |
| `void b16gemvt_kernel<64, 8, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, in … #04e8d91f0d` | 1088 | 31.340 | 28.805 | 30.431 | 33.270 |
| `void vllm::moe::single_group_topk::detail::single_group_topk_block_kernel<float, float, int, (vllm::moe::ScoringFunc)1, 384, 8>(float const*, flo … #010f201488` | 1344 | 14.298 | 10.639 | 10.890 | 11.390 |
| `void vllm::topk_impl::topk_2pass_row_kernel<1024, false, false>(float const*, int const*, int const*, int*, int, int, int, int, int, int, unsigned int)` | 352 | 13.727 | 38.998 | 41.294 | 42.082 |
| `fused_recurrent_gated_delta_rule_fwd_kernel` | 1088 | 13.258 | 12.186 | 12.500 | 12.780 |
| `void flash_fwd_splitkv_sparse_mla_kernel<Flash_fwd_kernel_traits<512, 64, 16, 8, true, true, mctlass::bfloat16_t, true, 512, 2, false>, false, tr … #0c9c4cdaa6` | 352 | 12.642 | 35.915 | 36.180 | 36.390 |
| `void b16gemvt_kernel<512, 8, 4, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #5f449323ab` | 1344 | 11.560 | 8.601 | 8.800 | 8.990 |
| `void vllm::moe::moe_align_block_size_kernel<int>(int const*, int*, int*, int*, int*, int, int, int, int, unsigned long, int*, int, int, bool)` | 1344 | 10.907 | 8.116 | 8.390 | 8.650 |
| `void b16gemvt_kernel<64, 16, 8, 4, int, float, __maca_bfloat16, __maca_bfloat16>(int, int, float, long long, __maca_bfloat16 const*, long long, i … #323fd25afc` | 2176 | 10.465 | 4.809 | 5.080 | 5.350 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 512, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3136 | 10.256 | 3.271 | 3.400 | 4.690 |
| `void vllm::dynamic_scaled_int8_quant_kernel_sreg_opt<c10::BFloat16, float, float4, float2, 256, false>(c10::BFloat16 const*, signed char*, float*, int, int, int*)` | 3040 | 9.762 | 3.211 | 3.420 | 5.810 |
| `mcclKernel_ReduceScatter_FC2_LL_Sum_mccl_bfloat16(fcinfo)` | 1440 | 8.991 | 6.244 | 8.420 | 12.000 |

| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |
|---|---:|---:|---:|
| `aten::copy_` | 1088 | 16.585 | 15.243 |
| `aten::to` | 544 | 11.061 | 20.333 |
| `aten::_to_copy` | 384 | 10.426 | 27.152 |
| `aten::slice` | 2624 | 9.670 | 3.685 |
| `vllm::all_gather` | 32 | 8.685 | 271.392 |
| `c10d::_allgather_base_` | 32 | 5.705 | 178.276 |
| `aten::fill_` | 704 | 5.568 | 7.909 |
| `aten::index` | 128 | 5.035 | 39.339 |
| `record_param_comms` | 32 | 5.015 | 156.710 |
| `aten::arange` | 64 | 4.879 | 76.227 |

