# 独立 GEMM 优化实验

这个实验不依赖 vLLM，用多版 FP32 kernel 验证“基线—优化—正确性—性能分析”闭环：

- `gemm_naive`：每个线程计算一个输出元素，直接反复读取全局内存。
- `gemm_tiled`：使用 16×16 共享内存分块，复用 A、B 数据。
- `gemm_tiled_2x`：在共享内存分块基础上，每线程用两个独立寄存器累加器
  计算同一行的两个输出，复用 A，并摊薄 workgroup 和同步开销。
- `gemm_tiled_4x/8x`：继续增加寄存器分块，用于寻找标量 FMA 路径的收益拐点。
- `mctlass_gemm`：通过 SDK 的 Grouped GEMM 入口调用 C500 FP32
  `16×16×4` MMA 指令，使用 `128×128×32` tile 和双级流水。

## 编译和运行

```bash
make
./gemm_demo --m 1024 --n 1024 --k 1024 --warmup 5 --iters 20 --kernel both

# 对比共享内存基线和 2x 寄存器分块版本
./gemm_demo --m 1024 --n 1024 --k 1024 --warmup 10 --iters 100 --kernel compare2

# MMA 版本；不传参数时为 1024³，也可传入 M N K
./mctlass_gemm
./mctlass_gemm 4096 4096 4096
```

输出包含平均耗时、GFLOPS、误差和加速比。先以 `VERIFY ... status=PASS` 作为优化有效的前提。

单独运行某个 kernel，便于 mcProfiler 采集：

```bash
./gemm_demo --m 1024 --n 1024 --k 1024 --warmup 2 --iters 5 --kernel naive
./gemm_demo --m 1024 --n 1024 --k 1024 --warmup 2 --iters 5 --kernel tiled
./gemm_demo --m 1024 --n 1024 --k 1024 --warmup 2 --iters 5 --kernel tiled2
```

MetaX C500、MACA 3.8.2.6 的实测结果：

| 版本/shape | 平均耗时 | FP32 性能 |
|---|---:|---:|
| naive，1024³ | 1.269 ms | 1.69 TFLOPS |
| tiled，1024³ | 0.799 ms | 2.69 TFLOPS |
| tiled 2x，1024³ | 0.609 ms | 3.53 TFLOPS |
| tiled 4x，1024³ | 0.534 ms | 4.02 TFLOPS |
| mctlass MMA，1024³ | 0.150 ms | 14.36 TFLOPS |
| mctlass MMA，2048³ | 0.749 ms | 22.95 TFLOPS |
| mctlass MMA，4096³ | 4.803 ms | 28.61 TFLOPS |
| PyTorch/mcBLAS，4096³ | 4.754 ms | 28.91 TFLOPS |

4096³ 下 MMA 版本重复三次为 28.612、28.615、28.616 TFLOPS，均通过
64 点独立 FP64 参考校验，达到同尺寸厂商库实测 roofline 的约 99.0%。
1024³ 的利用率较低属于小矩阵并行度和固定开销问题，应按 shape dispatch。

## mcProfiler 示例

在 `mcProfiler-ubuntu18.04` 目录执行；本地模式不要另外启动 `profiler_server`：

```bash
./mcProfiler perf_exec \
  --cmdline './gemm_demo --m 1024 --n 1024 --k 1024 --warmup 2 --iters 5 --kernel tiled' \
  --cwd '/workspace/gemm-opt-demo' \
  --casename 'gemm_tiled_total_cycles' \
  --metrics 'Total Cycles' \
  --per-kernel \
  --kernelnames 'gemm_tiled' \
  --counts 5 \
  --output '/workspace/gemm-opt-demo/profile'
```

第一轮先分别比较 `Total Cycles`、全局内存流量、共享内存效率和 Occupancy。不要一次全选所有指标，以免采集轮次过多并放大干扰。

MMA 版本的全指标报告位于：

```text
/workspace/linux-perf-kit-3.8.1.3/mcProfiler-ubuntu18.04/output20261116110341/report.pdf
```

报告显示 MMA Duty 83.20%、MTE Duty 4.94%、共享内存访问效率 100%、
bank conflict 0，说明它已从访存受限转为 MMA 计算受限。
