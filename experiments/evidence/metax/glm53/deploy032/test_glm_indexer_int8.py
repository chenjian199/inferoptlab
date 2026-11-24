"""Check the GLM INT8 prefill scorer against a CPU FP32 reference."""
import json
from pathlib import Path

import torch
from vllm.plugins import load_general_plugins


def main():
    load_general_plugins()
    from vllm_metax.models.glm5next.metax.utils import _mqa_logits_by_dtype

    generator = torch.Generator().manual_seed(20261122)
    results = []
    for m, n, heads in [(1, 128, 64), (17, 257, 32), (65, 513, 64)]:
        q = torch.randint(-127, 128, (m, heads, 128), generator=generator, dtype=torch.int8)
        k = torch.randint(-127, 128, (n, 128), generator=generator, dtype=torch.int8)
        k_scale = torch.rand(n, generator=generator) * 0.02 + 0.001
        # Includes folded per-query/head quantization scales, as in GLM.
        weights = torch.rand((m, heads), generator=generator) * 0.1
        starts = torch.arange(m, dtype=torch.int32) % 5
        ends = torch.arange(m, dtype=torch.int32) % (n // 2) + n // 2
        ref = torch.einsum('mhd,nd->mhn', q.float(), k.float())
        ref = (ref * k_scale[None, None, :]).relu()
        ref = (ref * weights[:, :, None]).sum(1)
        columns = torch.arange(n)[None, :]
        mask = (columns >= starts[:, None]) & (columns < ends[:, None])
        ref[~mask] = float('-inf')
        for clean in [True, False]:
            # Native INT8 provider takes Tensor Q, not the FP4 (values, scales) pair.
            actual = _mqa_logits_by_dtype(q.cuda(), (k.cuda(), k_scale.cuda()),
                                          weights.cuda(), starts.cuda(), ends.cuda(),
                                          clean_logits=clean).cpu()
            assert actual.shape == ref.shape
            error = float((actual[mask] - ref[mask]).abs().max())
            assert torch.allclose(actual[mask], ref[mask], rtol=1e-4, atol=0.005), error
            if clean:
                assert torch.isneginf(actual[~mask]).all()
            results.append(dict(m=m, n=n, heads=heads, clean=clean, max_abs_error=error))
    report = {'passed': True, 'cases': results, 'rtol': 1e-4, 'atol': 0.005,
              'reference': 'CPU FP32 dot, per-key scaling, ReLU, weighted head sum and causal bounds'}
    Path('/work/evidence/glm_indexer_int8.json').write_text(json.dumps(report, indent=2))
    print('GLM_INDEXER_INT8_PASS', json.dumps(results), flush=True)


if __name__ == '__main__':
    main()
