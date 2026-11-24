"""Bounded single-device calibration, intended for an idle MACA PyTorch runtime.

Run through a separate Python process; never stops another process. Refuses to
benchmark when mx-smi reports another GPU process. Event timing excludes Python
dispatch; bandwidth is copy read+write traffic, not PCIe transfer bandwidth.
"""
import datetime
import hashlib
import importlib.metadata
import json
import os
import re
import statistics
import subprocess
import sys
import time


def smi():
    if os.environ.get('INFEROPTLAB_HOST_GPU_PREFLIGHT'):
        return os.environ['INFEROPTLAB_HOST_GPU_PREFLIGHT']
    p = subprocess.run(["mx-smi", "--show-process"], capture_output=True, text=True, timeout=15)
    if p.returncode:
        raise RuntimeError("mx-smi failed: " + p.stderr)
    return p.stdout


def main():
    before = smi()
    active = re.findall(r"\|\s+\d+\s+(\d+)\s+\S+", before)
    result = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "hostname": os.uname().nodename, "status": "blocked", "gpu_before": before,
              "isolation": "exclusive_preflight_only", "measurements": []}
    if active:
        result["reason"] = "GPU processes already present: " + ",".join(active)
        print(json.dumps(result, indent=2))
        return 2
    import torch
    torch.set_num_threads(1)
    device = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    torch.cuda.set_device(device)
    prop = torch.cuda.get_device_properties(device)
    result.update(device_index=device, device_name=prop.name, memory_bytes=prop.total_memory,
                  torch_version=torch.__version__, timer="torch.cuda.Event.elapsed_time",
                  warmup_iterations=10, iterations_per_sample=20, repeats=5)
    torch.manual_seed(20261123)

    def measure(name, operation, count, unit, details, verify):
        for _ in range(10):
            operation()
        torch.cuda.synchronize()
        samples = []
        for _ in range(5):
            begin, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            begin.record()
            for _ in range(20):
                operation()
            end.record()
            end.synchronize()
            samples.append(begin.elapsed_time(end) / 20)
        if not verify():
            raise RuntimeError("output correctness failed: " + name)
        median = statistics.median(samples)
        result["measurements"].append(dict(name=name, samples_ms=samples,
            statistic="median", value=count / (median / 1000), unit=unit,
            correctness="passed", **details))

    # Each case has bounded allocation (< 600 MiB); no model load or collectives.
    for dtype in (torch.float16, torch.bfloat16, torch.float32):
        n = 4096
        a = torch.full((n, n), 0.125, device="cuda", dtype=dtype)
        b = torch.full_like(a, 0.125)
        out = torch.empty_like(a)
        torch.backends.cuda.matmul.allow_tf32 = False
        measure("gemm_" + str(dtype).split(".")[-1], lambda: torch.mm(a, b, out=out),
                2 * n ** 3 / 1e12, "TFLOPS", {"shape_mnk": [n,n,n], "dtype": str(dtype),
                "formula": "2*M*N*K/(median_ms/1000)/1e12", "allow_tf32": False},
                lambda: bool(torch.all(out == 64).item()))
        del a, b, out
    size = 256 * 1024 * 1024
    a = torch.ones(size // 4, dtype=torch.float32, device="cuda")
    b = torch.empty_like(a)
    measure("device_copy", lambda: b.copy_(a), 2 * size / 1e9, "GB/s",
            {"payload_bytes": size, "dtype": "torch.float32",
             "formula": "2*payload_bytes/(median_ms/1000)/1e9"},
            lambda: bool(torch.all(b == 1).item()))
    result["status"] = "measured"
    if not os.environ.get('INFEROPTLAB_HOST_GPU_PREFLIGHT'):
        result["gpu_after"] = smi()
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
