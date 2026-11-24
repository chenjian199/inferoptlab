# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Actual GPU ABI checks against independently grouped CPU routes."""

import importlib
import json
from pathlib import Path

import torch
from vllm.plugins import load_general_plugins


def main():
    load_general_plugins()
    from vllm import _custom_ops as ops
    from vllm.model_executor.layers.fused_moe.moe_align_block_size import (
        moe_align_block_size,
    )
    from vllm_metax.patch.bugfix import moe_align_legacy_abi as bridge

    assert ops.moe_align_block_size is bridge.moe_align_block_size
    before = ops.moe_align_block_size
    load_general_plugins()
    importlib.import_module("vllm_metax.patch.bugfix.moe_align_legacy_abi")
    assert ops.moe_align_block_size is before
    generator = torch.Generator().manual_seed(20261122)
    cases = []
    for dtype in [torch.int32, torch.int64]:
        for rows, experts, topk, block in [(1, 4, 2, 16), (33, 4, 2, 16),
                                          (257, 288, 8, 32), (4096, 288, 8, 32)]:
            ids = torch.randint(experts, (rows, topk), generator=generator, dtype=dtype)
            for mapped, ignore in [(False, False), (True, False), (True, True)]:
                mapping = torch.arange(experts, dtype=torch.int32)
                mapping[1::2] = -1
                mapping[::2] = torch.arange((experts + 1) // 2, dtype=torch.int32)
                flat = ids.flatten().tolist()
                expected = {}
                expected_padded = 0
                for expert in range(experts):
                    routes = [i for i, e in enumerate(flat) if e == expert]
                    local = int(mapping[expert]) if mapped else expert
                    if ignore and local < 0:
                        continue
                    expected_padded += (len(routes) + block - 1) // block * block
                    expected.setdefault(local, []).extend(routes)
                sorted_ids, expert_ids, count = moe_align_block_size(
                    ids.cuda(), block, experts,
                    mapping.cuda() if mapped else None,
                    pad_sorted_ids=True, ignore_invalid_experts=ignore,
                )
                n = count.item()
                assert n == expected_padded, (rows, mapped, ignore, n, expected_padded)
                routed = sorted_ids[:n].cpu().tolist()
                blocks = expert_ids[:n // block].cpu().tolist()
                actual = {}
                for index, expert in enumerate(blocks):
                    bucket = actual.setdefault(expert, [])
                    for route in routed[index * block:(index + 1) * block]:
                        assert 0 <= route <= len(flat), route
                        if route < len(flat):
                            bucket.append(route)
                for expert in set(expected) | set(actual):
                    assert sorted(actual.get(expert, [])) == sorted(expected.get(expert, []))
                cases.append(dict(dtype=str(dtype), rows=rows, experts=experts,
                                  mapped=mapped, ignore_invalid=ignore, padded=n))
    try:
        moe_align_block_size(torch.tensor([[0, 1]], device="cuda"), 16, 4,
                             return_scatter_idx=True)
    except NotImplementedError as error:
        assert "scatter_idx" in str(error)
    else:
        raise AssertionError("Legacy provider must reject scatter output")
    # Adjacent reduction ABI must execute too; integers keep the BF16 sum exact.
    x = torch.randint(-2, 3, (33, 8, 128), generator=generator).to(torch.bfloat16)
    output = torch.empty((33, 128), dtype=torch.bfloat16, device="cuda")
    ops.moe_sum(x.cuda(), output)
    assert torch.equal(output.cpu(), x.float().sum(1).to(torch.bfloat16))
    report = dict(passed=True, alignment_cases=cases, scatter_guard=True,
                  moe_sum_exact=True, wrapper_module=before.__module__,
                  native_schema=str(torch.ops._moe_C.moe_align_block_size.default._schema))
    Path("/work/evidence/moe_alignment_compat.json").write_text(json.dumps(report, indent=2))
    print("MOE_COMPAT_PASS", len(cases), flush=True)


if __name__ == "__main__":
    main()
