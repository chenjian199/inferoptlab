"""Bounded single-device calibration, intended for an idle MACA PyTorch runtime.

Run through a separate Python process; never stops another process. Refuses to
benchmark when mx-smi reports another GPU process. Event timing excludes Python
dispatch; bandwidth is copy read+write traffic, not PCIe transfer bandwidth.
"""
import datetime
import importlib.metadata
import json
import os
import re
import statistics
import subprocess
import sys


def active_gpu_pids(text):
    """Fail closed when management output cannot establish device occupancy."""
    attached = re.search(r'Attached GPUs\s+:\s+(\d+)', text)
    if not attached or int(attached[1]) < 1 or 'Process:' not in text or 'End of Log' not in text:
        raise RuntimeError('incomplete GPU process inventory')
    pids = re.findall(r"\|\s+\d+\s+(\d+)\s+\S+", text)
    if not pids and 'no process found' not in text:
        raise RuntimeError('unrecognized GPU process table')
    return sorted(set(pids))


def smi():
    if os.environ.get('INFEROPTLAB_HOST_GPU_PREFLIGHT'):
        return os.environ['INFEROPTLAB_HOST_GPU_PREFLIGHT']
    p = subprocess.run(["mx-smi", "--show-process"], capture_output=True, text=True, timeout=15)
    if p.returncode:
        raise RuntimeError("mx-smi failed: " + p.stderr)
    return p.stdout


def main():
    before = smi()
    active = active_gpu_pids(before)
    protocol = json.loads(os.environ.get('INFEROPTLAB_PROTOCOL', '{}'))
    shapes = protocol.get('gemm_shapes', [[4096, 4096, 4096]])
    dtypes = protocol.get('dtypes', ['float16', 'bfloat16', 'float32'])
    warmup = protocol.get('warmup_iterations', 10)
    iterations = protocol.get('iterations_per_sample', 20)
    repeats = protocol.get('repeats', 5)
    copy_sizes = protocol.get('copy_sizes_mib', [256])
    result = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "hostname": os.uname().nodename, "status": "blocked", "gpu_before": before,
              "isolation": "exclusive_preflight_only", "measurements": []}
    if active:
        result["reason"] = "GPU processes already present: " + ",".join(active)
        print(json.dumps(result, indent=2))
        return 2
    import torch
    torch.set_num_threads(1)
    visible_count = torch.cuda.device_count()
    if os.environ.get('MACA_VISIBLE_DEVICES') and visible_count != 1:
        raise RuntimeError('MACA device isolation failed: expected exactly one visible GPU')
    device = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    torch.cuda.set_device(device)
    prop = torch.cuda.get_device_properties(device)
    result.update(device_index=device, device_name=prop.name, memory_bytes=prop.total_memory, visible_device_count=visible_count,
                  torch_version=torch.__version__, timer="torch.cuda.Event.elapsed_time",
                  warmup_iterations=warmup, iterations_per_sample=iterations, repeats=repeats,
                  physical_ordinal=os.environ.get('MACA_VISIBLE_DEVICES', str(device)), protocol=protocol)
    result['packages'] = {}
    for name in ('torch', 'triton', 'mcoplib', 'mctlassEx'):
        try:
            result['packages'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            pass
    torch.manual_seed(20261123)

    def measure(name, operation, count, unit, details, verify):
        for _ in range(warmup):
            operation()
        torch.cuda.synchronize()
        samples = []
        for _ in range(repeats):
            begin, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            begin.record()
            for _ in range(iterations):
                operation()
            end.record()
            end.synchronize()
            samples.append(begin.elapsed_time(end) / iterations)
        if not verify():
            raise RuntimeError("output correctness failed: " + name)
        median = statistics.median(samples)
        result["measurements"].append(dict(name=name, samples_ms=samples,
            statistic="median", value=count / (median / 1000), unit=unit,
            correctness="passed", **details))

    limit = protocol.get('max_allocation_mib', 1024) * 1024**2
    for dtype_name in dtypes:
        dtype = getattr(torch, dtype_name)
        for m, n, k in shapes:
            needed = (m*k + k*n + m*n) * torch.empty((), dtype=dtype).element_size() + m*n
            if needed > limit:
                raise RuntimeError('GEMM allocation exceeds configured budget')
            a = torch.full((m, k), 0.125, device="cuda", dtype=dtype)
            b = torch.full((k, n), 0.125, device="cuda", dtype=dtype)
            out = torch.empty((m, n), device="cuda", dtype=dtype)
            torch.backends.cuda.matmul.allow_tf32 = False
            measure(f"gemm_{dtype_name}_{m}x{n}x{k}", lambda: torch.mm(a, b, out=out),
                    2 * m*n*k / 1e12, "TFLOPS", {"shape_mnk": [m,n,k], "dtype": str(dtype),
                    "formula": "2*M*N*K/(median_ms/1000)/1e12", "allow_tf32": False},
                    lambda: bool(torch.all(out == k/64).item()))
            del a, b, out
            torch.cuda.empty_cache()
    for mib in copy_sizes:
        size = mib * 1024**2
        if size * 2 + size//4 > limit:
            raise RuntimeError('copy allocation exceeds configured budget')
        a = torch.ones(size // 4, dtype=torch.float32, device="cuda")
        b = torch.empty_like(a)
        measure(f"device_copy_{mib}mib", lambda: b.copy_(a), 2 * size / 1e9, "GB/s",
                {"payload_bytes": size, "dtype": "torch.float32",
                 "formula": "2*payload_bytes/(median_ms/1000)/1e9"},
                lambda: bool(torch.all(b == 1).item()))
        del a, b
        torch.cuda.empty_cache()
    result["status"] = "measured"
    if not os.environ.get('INFEROPTLAB_HOST_GPU_PREFLIGHT'):
        result["gpu_after"] = smi()
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
