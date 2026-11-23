"""Read-only Linux probe. Send to `ssh HOST python3 -`; writes JSON to stdout.

Reads metadata and safetensors headers, never model weight payloads. No imports
of remote model code, GPU allocations, resets, or service modifications.
"""
import collections
import datetime
import hashlib
import json
import math
import pathlib
import platform
import struct
import subprocess
import sys


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(args, timeout=20):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return {"argv": args, "returncode": p.returncode,
                "stdout": p.stdout, "stderr": p.stderr}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"argv": args, "error": str(exc)}


def model(directory):
    root = pathlib.Path(directory)
    result = {"path": str(root), "files": {}, "errors": [],
              "captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for name in ("config.json", "generation_config.json", "quantize_config.json",
                 "quant_config.json", "tokenizer_config.json", "special_tokens_map.json",
                 "tokenizer.json", "tokenizer.model", "vocab.json", "merges.txt",
                 "chat_template.jinja", "model.safetensors.index.json",
                 "quant_model_weights.safetensors.index.json", "quant_model_description.json",
                 "processor_config.json", "README.md", "llmc_qconfig.yaml",
                 "DeepSeek-V4_best_practice.yaml", "DeepSeek-V4.1-Flash_best_practice.yaml",
                 "optional/quarot.safetensors"):
        p = root / name
        if not p.is_file():
            continue
        data = p.read_bytes()
        item = {"size_bytes": len(data), "sha256": sha(data)}
        if name == "quant_model_description.json":
            desc = json.loads(data)
            counts, examples = collections.Counter(), {}
            for k, v in desc.items():
                label = v if isinstance(v, str) else json.dumps(v, sort_keys=True)
                counts[label] += 1
                if len(examples.setdefault(label, [])) < 3:
                    examples[label].append(k)
            item["summary"] = {"counts": dict(counts), "examples": examples}
        elif name.endswith(".json") and name not in ("tokenizer.json", "vocab.json"):
            item["content"] = json.loads(data)
        elif name.endswith((".jinja", ".md", ".yaml")):
            item["content"] = data.decode()
        result["files"][name] = item
    index_name = next((n for n in ("model.safetensors.index.json", "quant_model_weights.safetensors.index.json")
                       if n in result["files"]), None)
    index = result["files"].get(index_name, {}).get("content", {})
    weight_map = index.get("weight_map", {})
    shard_names = sorted(set(weight_map.values())) or sorted(p.name for p in root.glob("*.safetensors"))
    stats, samples, shards, scale_dtypes = {}, {}, [], set()
    actual_map = {}
    for name in shard_names:
        p = root / name
        if pathlib.PurePosixPath(name).name != name:
            result["errors"].append("non-basename shard: " + name)
            continue
        if not p.is_file():
            result["errors"].append("missing shard: " + name)
            continue
        with p.open("rb") as f:
            prefix = f.read(8)
            length = struct.unpack("<Q", prefix)[0]
            if not 0 < length <= 64 * 1024 * 1024:
                raise ValueError("invalid safetensors header size")
            header_bytes = f.read(length)
        header = json.loads(header_bytes)
        size = p.stat().st_size
        shards.append({"name": name, "size_bytes": size,
                       "header_sha256": sha(prefix + header_bytes)})
        for tensor_name, tensor in header.items():
            if tensor_name == "__metadata__":
                continue
            if tensor_name in actual_map:
                result["errors"].append("duplicate tensor: " + tensor_name)
            actual_map[tensor_name] = name
            dtype, shape = tensor["dtype"], tensor["shape"]
            if 'scale' in tensor_name:
                scale_dtypes.add(dtype)
            lo, hi = tensor["data_offsets"]
            if not 0 <= lo <= hi <= size - 8 - length:
                result["errors"].append("invalid tensor offsets: " + tensor_name)
            stat = stats.setdefault(dtype, {"tensor_count": 0, "elements": 0, "storage_bytes": 0})
            stat["tensor_count"] += 1
            stat["elements"] += math.prod(shape)
            stat["storage_bytes"] += hi - lo
            if len(samples.setdefault(dtype, [])) < 5:
                samples[dtype].append({"name": tensor_name, "shape": shape})
    if weight_map and actual_map != weight_map:
        result["errors"].append("index/header tensor map mismatch")
    result["weights"] = {"shards": shards, "dtype_summary": stats, "tensor_samples": samples,
                         "index_file": index_name,
                         "scale_tensor_dtypes": sorted(scale_dtypes),
                         "unindexed_safetensors": sorted(p.name for p in root.glob("*.safetensors") if p.name not in shard_names),
                         "index_metadata": index.get("metadata", {}),
                         "index_matches_headers": bool(weight_map) and actual_map == weight_map,
                         "verification_scope": "index_and_all_shard_headers; payload bytes not hashed"}
    # Preserve the full index file hash, without duplicating its enormous tensor map.
    if index_name:
        result["files"][index_name].pop("content", None)
    return result


def inventory():
    result = {"captured_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "hostname": platform.node(), "kernel": platform.release()}
    commands = {
        "gpu": ["mx-smi", "-j"], "summary": ["mx-smi"],
        "pcie": ["mx-smi", "--show-pcie"], "memory": ["mx-smi", "--show-memory"],
        "hwinfo": ["mx-smi", "--show-hwinfo"], "ecc": ["mx-smi", "--count-ecc"],
        "topology_help": ["mx-smi", "topo", "-h"],
        "cpu": ["lscpu", "-J"], "nics": ["ip", "-j", "link"],
        "containers": ["docker", "ps", "--format", "{{.Names}}"],
    }
    result["commands"] = {name: command(args) for name, args in commands.items()}
    result["meminfo"] = pathlib.Path("/proc/meminfo").read_text()
    result["os_release"] = pathlib.Path("/etc/os-release").read_text()
    result["pci"] = []
    for p in sorted(pathlib.Path("/sys/bus/pci/devices").iterdir()):
        if (p / "vendor").read_text().strip() != "0x9999":
            continue
        item = {"address": p.name}
        for name in ("vendor", "device", "subsystem_vendor", "subsystem_device", "numa_node",
                     "local_cpulist", "current_link_speed", "current_link_width",
                     "max_link_speed", "max_link_width"):
            try:
                item[name] = (p / name).read_text().strip()
            except OSError:
                item[name] = None
        result["pci"].append(item)
    result["containers"] = []
    for name in result["commands"]["containers"].get("stdout", "").splitlines():
        inspect = command(["docker", "inspect", name])
        if inspect.get("returncode") != 0:
            continue
        doc = json.loads(inspect["stdout"])[0]
        result["containers"].append({"name": name, "image_id": doc["Image"],
            "image_label": doc["Config"]["Image"], "state": doc["State"], "mounts": doc["Mounts"]})
    return result


if __name__ == "__main__":
    output = model(sys.argv[2]) if len(sys.argv) > 1 and sys.argv[1] == "model" else inventory()
    print(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False))
