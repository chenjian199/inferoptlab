"""Numerical checks for native sparse MLA, including GLM's NoPE head size."""
import json
from pathlib import Path

import torch
from vllm.plugins import load_general_plugins


def main():
    load_general_plugins()
    from vllm_metax.v1.attention.ops.flashmla import flash_mla_sparse_fwd

    torch.set_num_threads(4)
    rng = torch.Generator().manual_seed(20261122)
    results = []
    for dim in [512, 576]:
        tokens, heads, keys, selected = 3, 64, 257, 128
        q = torch.randn((tokens, heads, dim), generator=rng).to(torch.bfloat16)
        kv = torch.randn((keys, 1, dim), generator=rng).to(torch.bfloat16)
        indices = torch.stack([torch.randperm(keys, generator=rng)[:selected]
                               for _ in range(tokens)]).int()
        counts = torch.tensor([128, 93, 17], dtype=torch.int32)
        indices[torch.arange(selected)[None, :] >= counts[:, None]] = -1
        expected = []
        scale = dim ** -0.5
        for row in range(tokens):
            chosen = kv[indices[row, :counts[row]], 0].float()
            scores = (q[row].float() @ chosen.t()) * scale
            expected.append(scores.softmax(-1) @ chosen[:, :512])
        expected = torch.stack(expected)
        result = flash_mla_sparse_fwd(q.cuda(), kv.cuda(), indices[:, None].cuda(),
                                      scale, topk_length=counts.cuda())
        actual = result[0].cpu().float()
        assert actual.shape == expected.shape, (actual.shape, expected.shape)
        diff = (actual - expected).abs()
        passed = bool(torch.allclose(actual, expected, rtol=0.02, atol=0.01))
        results.append(dict(head_dim=dim, passed=passed,
                            max_abs_error=float(diff.max()),
                            relative_l2=float(torch.linalg.vector_norm(diff) /
                                              torch.linalg.vector_norm(expected))))
    report = {'passed': all(c['passed'] for c in results), 'cases': results,
              'reference': 'CPU FP32 softmax(QK^T/sqrt(D))V over selected valid keys'}
    Path('/work/evidence/sparse_mla_numerics.json').write_text(json.dumps(report, indent=2))
    print('SPARSE_MLA_RESULT', json.dumps(report), flush=True)
    assert report['passed'], report


if __name__ == '__main__':
    main()
