PAYLOAD = {'host': {'id': 'metax-64', 'ssh': 'metax-64', 'backend': 'metax', 'image': 'sha256:91b2504601a1d2bdc2f4b057127258311df95d1d9c7f7aa2b270c60e5d4848e3', 'devices': 'all', 'max_devices': 8}, 'protocol': {'gemm_shapes': [[4096, 4096, 4096]], 'dtypes': ['float16', 'bfloat16', 'float32'], 'copy_sizes_mib': [256], 'warmup_iterations': 10, 'iterations_per_sample': 20, 'repeats': 5, 'max_allocation_mib': 1024, 'timeout_seconds': 150}, 'mode': 'inspect', 'inventory_code': '"""Read-only Linux probe. Send to `ssh HOST python3 -`; writes JSON to stdout.\n\nReads metadata and safetensors headers, never model weight payloads. No imports\nof remote model code, GPU allocations, resets, or service modifications.\n"""\nimport collections\nimport datetime\nimport hashlib\nimport json\nimport math\nimport pathlib\nimport platform\nimport struct\nimport subprocess\nimport sys\n\n\ndef sha(data):\n    return hashlib.sha256(data).hexdigest()\n\n\ndef command(args, timeout=20):\n    try:\n        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)\n        return {"argv": args, "returncode": p.returncode,\n                "stdout": p.stdout, "stderr": p.stderr}\n    except (OSError, subprocess.TimeoutExpired) as exc:\n        return {"argv": args, "error": str(exc)}\n\n\ndef model(directory):\n    root = pathlib.Path(directory)\n    result = {"path": str(root), "files": {}, "errors": [],\n              "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}\n    for name in ("config.json", "generation_config.json", "quantize_config.json",\n                 "quant_config.json", "tokenizer_config.json", "special_tokens_map.json",\n                 "tokenizer.json", "tokenizer.model", "vocab.json", "merges.txt",\n                 "chat_template.jinja", "model.safetensors.index.json",\n                 "quant_model_weights.safetensors.index.json", "quant_model_description.json",\n                 "processor_config.json", "README.md", "llmc_qconfig.yaml",\n                 "DeepSeek-V4_best_practice.yaml", "DeepSeek-V4.1-Flash_best_practice.yaml",\n                 "optional/quarot.safetensors"):\n        p = root / name\n        if not p.is_file():\n            continue\n        data = p.read_bytes()\n        item = {"size_bytes": len(data), "sha256": sha(data)}\n        if name == "quant_model_description.json":\n            desc = json.loads(data)\n            counts, examples = collections.Counter(), {}\n            for k, v in desc.items():\n                label = v if isinstance(v, str) else json.dumps(v, sort_keys=True)\n                counts[label] += 1\n                if len(examples.setdefault(label, [])) < 3:\n                    examples[label].append(k)\n            item["summary"] = {"counts": dict(counts), "examples": examples}\n        elif name.endswith(".json") and name not in ("tokenizer.json", "vocab.json"):\n            item["content"] = json.loads(data)\n        elif name.endswith((".jinja", ".md", ".yaml")):\n            item["content"] = data.decode()\n        result["files"][name] = item\n    index_name = next((n for n in ("model.safetensors.index.json", "quant_model_weights.safetensors.index.json")\n                       if n in result["files"]), None)\n    index = result["files"].get(index_name, {}).get("content", {})\n    weight_map = index.get("weight_map", {})\n    shard_names = sorted(set(weight_map.values())) or sorted(p.name for p in root.glob("*.safetensors"))\n    stats, samples, shards, scale_dtypes = {}, {}, [], set()\n    actual_map = {}\n    for name in shard_names:\n        p = root / name\n        if pathlib.PurePosixPath(name).name != name:\n            result["errors"].append("non-basename shard: " + name)\n            continue\n        if not p.is_file():\n            result["errors"].append("missing shard: " + name)\n            continue\n        with p.open("rb") as f:\n            prefix = f.read(8)\n            length = struct.unpack("<Q", prefix)[0]\n            if not 0 < length <= 64 * 1024 * 1024:\n                raise ValueError("invalid safetensors header size")\n            header_bytes = f.read(length)\n        header = json.loads(header_bytes)\n        size = p.stat().st_size\n        shards.append({"name": name, "size_bytes": size,\n                       "header_sha256": sha(prefix + header_bytes)})\n        for tensor_name, tensor in header.items():\n            if tensor_name == "__metadata__":\n                continue\n            if tensor_name in actual_map:\n                result["errors"].append("duplicate tensor: " + tensor_name)\n            actual_map[tensor_name] = name\n            dtype, shape = tensor["dtype"], tensor["shape"]\n            if \'scale\' in tensor_name:\n                scale_dtypes.add(dtype)\n            lo, hi = tensor["data_offsets"]\n            if not 0 <= lo <= hi <= size - 8 - length:\n                result["errors"].append("invalid tensor offsets: " + tensor_name)\n            stat = stats.setdefault(dtype, {"tensor_count": 0, "elements": 0, "storage_bytes": 0})\n            stat["tensor_count"] += 1\n            stat["elements"] += math.prod(shape)\n            stat["storage_bytes"] += hi - lo\n            if len(samples.setdefault(dtype, [])) < 5:\n                samples[dtype].append({"name": tensor_name, "shape": shape})\n    if weight_map and actual_map != weight_map:\n        result["errors"].append("index/header tensor map mismatch")\n    result["weights"] = {"shards": shards, "dtype_summary": stats, "tensor_samples": samples,\n                         "index_file": index_name,\n                         "scale_tensor_dtypes": sorted(scale_dtypes),\n                         "unindexed_safetensors": sorted(p.name for p in root.glob("*.safetensors") if p.name not in shard_names),\n                         "index_metadata": index.get("metadata", {}),\n                         "index_matches_headers": bool(weight_map) and actual_map == weight_map,\n                         "verification_scope": "index_and_all_shard_headers; payload bytes not hashed"}\n    # Preserve the full index file hash, without duplicating its enormous tensor map.\n    if index_name:\n        result["files"][index_name].pop("content", None)\n    return result\n\n\ndef inventory():\n    result = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),\n              "hostname": platform.node(), "kernel": platform.release()}\n    commands = {\n        "gpu": ["mx-smi", "-j"], "summary": ["mx-smi"],\n        "pcie": ["mx-smi", "--show-pcie"], "memory": ["mx-smi", "--show-memory"],\n        "hwinfo": ["mx-smi", "--show-hwinfo"], "ecc": ["mx-smi", "--count-ecc"],\n        "topology_help": ["mx-smi", "topo", "-h"],\n        "topology": ["mx-smi", "topo", "-m"],\n        "processes": ["mx-smi", "--show-process"],\n        "cpu": ["lscpu", "-J"], "nics": ["ip", "-j", "link"],\n        "containers": ["docker", "ps", "--format", "{{.Names}}"],\n    }\n    result["commands"] = {name: command(args) for name, args in commands.items()}\n    result["meminfo"] = pathlib.Path("/proc/meminfo").read_text()\n    result["os_release"] = pathlib.Path("/etc/os-release").read_text()\n    result["pci"] = []\n    for p in sorted(pathlib.Path("/sys/bus/pci/devices").iterdir()):\n        if (p / "vendor").read_text().strip() != "0x9999":\n            continue\n        item = {"address": p.name}\n        for name in ("vendor", "device", "subsystem_vendor", "subsystem_device", "numa_node",\n                     "local_cpulist", "current_link_speed", "current_link_width",\n                     "max_link_speed", "max_link_width"):\n            try:\n                item[name] = (p / name).read_text().strip()\n            except OSError:\n                item[name] = None\n        result["pci"].append(item)\n    result["containers"] = []\n    for name in result["commands"]["containers"].get("stdout", "").splitlines():\n        inspect = command(["docker", "inspect", name])\n        if inspect.get("returncode") != 0:\n            continue\n        doc = json.loads(inspect["stdout"])[0]\n        result["containers"].append({"name": name, "image_id": doc["Image"],\n            "image_label": doc["Config"]["Image"], "state": doc["State"], "mounts": doc["Mounts"]})\n    return result\n\n\nif __name__ == "__main__":\n    output = model(sys.argv[2]) if len(sys.argv) > 1 and sys.argv[1] == "model" else inventory()\n    print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))\n', 'benchmark_code': '"""Bounded single-device calibration, intended for an idle MACA PyTorch runtime.\n\nRun through a separate Python process; never stops another process. Refuses to\nbenchmark when mx-smi reports another GPU process. Event timing excludes Python\ndispatch; bandwidth is copy read+write traffic, not PCIe transfer bandwidth.\n"""\nimport datetime\nimport importlib.metadata\nimport json\nimport os\nimport re\nimport statistics\nimport subprocess\nimport sys\n\n\ndef active_gpu_pids(text):\n    """Fail closed when management output cannot establish device occupancy."""\n    attached = re.search(r\'Attached GPUs\\s+:\\s+(\\d+)\', text)\n    if not attached or int(attached[1]) < 1 or \'Process:\' not in text or \'End of Log\' not in text:\n        raise RuntimeError(\'incomplete GPU process inventory\')\n    pids = re.findall(r"\\|\\s+\\d+\\s+(\\d+)\\s+\\S+", text)\n    if not pids and \'no process found\' not in text:\n        raise RuntimeError(\'unrecognized GPU process table\')\n    return sorted(set(pids))\n\n\ndef smi():\n    if os.environ.get(\'INFEROPTLAB_HOST_GPU_PREFLIGHT\'):\n        return os.environ[\'INFEROPTLAB_HOST_GPU_PREFLIGHT\']\n    p = subprocess.run(["mx-smi", "--show-process"], capture_output=True, text=True, timeout=15)\n    if p.returncode:\n        raise RuntimeError("mx-smi failed: " + p.stderr)\n    return p.stdout\n\n\ndef main():\n    before = smi()\n    active = active_gpu_pids(before)\n    protocol = json.loads(os.environ.get(\'INFEROPTLAB_PROTOCOL\', \'{}\'))\n    shapes = protocol.get(\'gemm_shapes\', [[4096, 4096, 4096]])\n    dtypes = protocol.get(\'dtypes\', [\'float16\', \'bfloat16\', \'float32\'])\n    warmup = protocol.get(\'warmup_iterations\', 10)\n    iterations = protocol.get(\'iterations_per_sample\', 20)\n    repeats = protocol.get(\'repeats\', 5)\n    copy_sizes = protocol.get(\'copy_sizes_mib\', [256])\n    result = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),\n              "hostname": os.uname().nodename, "status": "blocked", "gpu_before": before,\n              "isolation": "exclusive_preflight_only", "measurements": []}\n    if active:\n        result["reason"] = "GPU processes already present: " + ",".join(active)\n        print(json.dumps(result, indent=2))\n        return 2\n    import torch\n    torch.set_num_threads(1)\n    visible_count = torch.cuda.device_count()\n    if os.environ.get(\'MACA_VISIBLE_DEVICES\') and visible_count != 1:\n        raise RuntimeError(\'MACA device isolation failed: expected exactly one visible GPU\')\n    device = int(sys.argv[1]) if len(sys.argv) > 1 else 0\n    torch.cuda.set_device(device)\n    prop = torch.cuda.get_device_properties(device)\n    result.update(device_index=device, device_name=prop.name, memory_bytes=prop.total_memory, visible_device_count=visible_count,\n                  torch_version=torch.__version__, timer="torch.cuda.Event.elapsed_time",\n                  warmup_iterations=warmup, iterations_per_sample=iterations, repeats=repeats,\n                  physical_ordinal=os.environ.get(\'MACA_VISIBLE_DEVICES\', str(device)), protocol=protocol)\n    result[\'packages\'] = {}\n    for name in (\'torch\', \'triton\', \'mcoplib\', \'mctlassEx\'):\n        try:\n            result[\'packages\'][name] = importlib.metadata.version(name)\n        except importlib.metadata.PackageNotFoundError:\n            pass\n    torch.manual_seed(20261123)\n\n    def measure(name, operation, count, unit, details, verify):\n        for _ in range(warmup):\n            operation()\n        torch.cuda.synchronize()\n        samples = []\n        for _ in range(repeats):\n            begin, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)\n            begin.record()\n            for _ in range(iterations):\n                operation()\n            end.record()\n            end.synchronize()\n            samples.append(begin.elapsed_time(end) / iterations)\n        if not verify():\n            raise RuntimeError("output correctness failed: " + name)\n        median = statistics.median(samples)\n        result["measurements"].append(dict(name=name, samples_ms=samples,\n            statistic="median", value=count / (median / 1000), unit=unit,\n            correctness="passed", **details))\n\n    limit = protocol.get(\'max_allocation_mib\', 1024) * 1024**2\n    for dtype_name in dtypes:\n        dtype = getattr(torch, dtype_name)\n        for m, n, k in shapes:\n            needed = (m*k + k*n + m*n) * torch.empty((), dtype=dtype).element_size() + m*n\n            if needed > limit:\n                raise RuntimeError(\'GEMM allocation exceeds configured budget\')\n            a = torch.full((m, k), 0.125, device="cuda", dtype=dtype)\n            b = torch.full((k, n), 0.125, device="cuda", dtype=dtype)\n            out = torch.empty((m, n), device="cuda", dtype=dtype)\n            torch.backends.cuda.matmul.allow_tf32 = False\n            measure(f"gemm_{dtype_name}_{m}x{n}x{k}", lambda: torch.mm(a, b, out=out),\n                    2 * m*n*k / 1e12, "TFLOPS", {"shape_mnk": [m,n,k], "dtype": str(dtype),\n                    "formula": "2*M*N*K/(median_ms/1000)/1e12", "allow_tf32": False},\n                    lambda: bool(torch.all(out == k/64).item()))\n            del a, b, out\n            torch.cuda.empty_cache()\n    for mib in copy_sizes:\n        size = mib * 1024**2\n        if size * 2 + size//4 > limit:\n            raise RuntimeError(\'copy allocation exceeds configured budget\')\n        a = torch.ones(size // 4, dtype=torch.float32, device="cuda")\n        b = torch.empty_like(a)\n        measure(f"device_copy_{mib}mib", lambda: b.copy_(a), 2 * size / 1e9, "GB/s",\n                {"payload_bytes": size, "dtype": "torch.float32",\n                 "formula": "2*payload_bytes/(median_ms/1000)/1e9"},\n                lambda: bool(torch.all(b == 1).item()))\n        del a, b\n        torch.cuda.empty_cache()\n    result["status"] = "measured"\n    if not os.environ.get(\'INFEROPTLAB_HOST_GPU_PREFLIGHT\'):\n        result["gpu_after"] = smi()\n    print(json.dumps(result, indent=2, allow_nan=False))\n    return 0\n\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'}
"""Standalone remote worker; controller supplies PAYLOAD before this source."""
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import traceback
import uuid


def run(payload):
    inv = {'__name__': '_inventory'}
    bench = {'__name__': '_benchmark'}
    exec(compile(payload['inventory_code'], 'inventory.py', 'exec'), inv)
    exec(compile(payload['benchmark_code'], 'benchmark.py', 'exec'), bench)
    result = dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  node_id=payload['host']['id'], hostname=os.uname().nodename,
                  status='failed', attempts=[], inventory=None)
    try:
        inventory = inv['inventory']()
        result['inventory'] = inventory
        process = inventory['commands']['processes']
        if process.get('returncode') != 0:
            raise RuntimeError('mx-smi process inventory failed')
        bench['active_gpu_pids'](process['stdout'])  # malformed output is an error even for inspect
        gpu_command = inventory['commands']['gpu']
        if gpu_command.get('returncode') != 0:
            raise RuntimeError('GPU identity inventory failed')
        text = gpu_command['stdout']
        gpu = json.loads(text[text.index('{'):])
        indices = sorted(v['device_id'] for v in gpu.values() if isinstance(v, dict) and 'device_id' in v)
        selected = indices if payload['host']['devices'] == 'all' else payload['host']['devices']
        if not selected or not set(selected) <= set(indices):
            raise RuntimeError('requested GPU indices are absent from the inventory')
        if len(selected) > payload['host']['max_devices']:
            raise RuntimeError('selected GPUs exceed max_devices')
        result['selected_devices'] = selected
        if payload['mode'] == 'inspect':
            result['status'] = 'inspected'
            return result
        image = payload['host']['image']
        p = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', image],
                           capture_output=True, text=True, timeout=20)
        if p.returncode or p.stdout.strip() != image:
            raise RuntimeError('local image ID missing or mismatched; images are never downloaded')
        result['image_id'] = image
        with open('/tmp/inferoptlab-c500-calibration.lock', 'a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                result.update(status='blocked', error='another calibration holds the host lock')
                return result
            for ordinal in selected:
                attempt = dict(ordinal=ordinal, status='failed', captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
                result['attempts'].append(attempt)
                before = inv['command'](['mx-smi', '--show-process'])
                attempt['before'] = before
                if before.get('returncode') != 0:
                    attempt['error'] = 'process preflight failed'
                    break
                if bench['active_gpu_pids'](before['stdout']):
                    attempt.update(status='blocked', error='GPU process already present on host')
                    break
                name = 'inferoptlab-hardware-' + uuid.uuid4().hex
                cmd = ['docker', 'run', '--pull=never', '--rm', '--init', '-i', '--name', name,
                       '--network', 'none', '--device', '/dev/dri', '--device', '/dev/mxcd',
                       '--group-add', 'video', '-e', f'MACA_VISIBLE_DEVICES={ordinal}',
                       '-e', 'INFEROPTLAB_HOST_GPU_PREFLIGHT=' + before['stdout'],
                       '-e', 'INFEROPTLAB_PROTOCOL=' + json.dumps(payload['protocol']),
                       '--entrypoint', 'python3', image, '-', '0']
                attempt['container_name'] = name
                try:
                    p = subprocess.run(cmd, input=payload['benchmark_code'].encode(), capture_output=True,
                                       timeout=payload['protocol']['timeout_seconds'])
                    attempt.update(returncode=p.returncode, stdout=p.stdout.decode(errors='replace'),
                                   stderr=p.stderr.decode(errors='replace'))
                    if p.returncode == 0:
                        text = attempt['stdout']
                        measured = json.loads(text[text.index('{'):])
                        if measured['status'] != 'measured' or int(measured['physical_ordinal']) != ordinal:
                            raise RuntimeError('measurement device/status mismatch')
                        attempt.update(status='measured', result=measured)
                except subprocess.TimeoutExpired as exc:
                    attempt.update(status='timeout', error='device test exceeded its deadline',
                                   stdout=(exc.stdout or b'').decode(errors='replace'),
                                   stderr=(exc.stderr or b'').decode(errors='replace'))
                finally:
                    cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, text=True, timeout=20)
                    # --rm normally already removed this owned container.
                    attempt['cleanup'] = dict(returncode=cleanup.returncode, stderr=cleanup.stderr)
                    if cleanup.returncode and 'No such container' not in cleanup.stderr:
                        attempt.update(status='cleanup_failed', error='owned container cleanup could not be confirmed')
                after = inv['command'](['mx-smi', '--show-process'])
                attempt['after'] = after
                if after.get('returncode') != 0 or bench['active_gpu_pids'](after.get('stdout', '')):
                    attempt.update(status='contended', error='GPU process state was not idle after the test')
                if attempt['status'] != 'measured':
                    break
        result['status'] = 'measured' if len(result['attempts']) == len(selected) and all(
            a['status'] == 'measured' for a in result['attempts']) else 'incomplete'
    except Exception as exc:
        result.update(status='failed', error=str(exc), traceback=traceback.format_exc())
    return result


if __name__ == '__main__':
    print(json.dumps(run(PAYLOAD), indent=2, allow_nan=False))
