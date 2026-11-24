"""Compare the actual deployment INT8 linear kernels with CPU arithmetic."""
import json
from pathlib import Path

import torch
from vllm.plugins import load_general_plugins


def main():
    load_general_plugins()
    from vllm import _custom_ops as ops
    from vllm_metax.model_executor.layers.quantization import _python_api_ops

    torch.set_num_threads(4)
    rng = torch.Generator().manual_seed(20261122)
    cases = []
    for m, k, n in [(1, 4096, 512), (33, 4096, 512), (17, 512, 4096)]:
        x = torch.randn((m, k), generator=rng, dtype=torch.bfloat16)
        w = torch.randint(-16, 17, (n, k), generator=rng, dtype=torch.int8)
        ws = (torch.rand((n, 1), generator=rng) * 0.03 + 0.001).float()
        q, scale, zero = ops.scaled_int8_quant(x.cuda())
        assert zero is None
        cpu_q, cpu_scale = q.cpu(), scale.cpu()
        ref_scale = x.float().abs().amax(1, keepdim=True) / 127
        assert torch.allclose(cpu_scale, ref_scale, rtol=1e-6, atol=1e-8)
        ref_q = (x.float() / ref_scale).round().clamp(-128, 127).to(torch.int8)
        q_error = int((ref_q.to(torch.int16) - cpu_q.to(torch.int16)).abs().max())
        assert q_error <= 1
        actual = _python_api_ops.cutlass_scaled_mm(
            q, w.cuda().t(), scale_a=scale, scale_b=ws.cuda(),
            out_dtype=torch.bfloat16, bias=None).cpu()
        ref = ((cpu_q.float() @ w.float().t()) * cpu_scale * ws.t()).to(torch.bfloat16)
        diff = (actual.float() - ref.float()).abs()
        assert torch.isfinite(actual).all()
        assert torch.allclose(actual.float(), ref.float(), rtol=0.01, atol=0.02), float(diff.max())
        cases.append(dict(m=m, k=k, n=n, max_abs_error=float(diff.max()),
                          relative_l2=float(torch.linalg.vector_norm(diff) /
                                            torch.linalg.vector_norm(ref.float())),
                          max_quantized_integer_difference=q_error))
    report = {'passed': True, 'cases': cases, 'rtol': 0.01, 'atol': 0.02}
    Path('/work/evidence/int8_linear.json').write_text(json.dumps(report, indent=2))
    print('INT8_LINEAR_PASS', json.dumps(cases), flush=True)


if __name__ == '__main__':
    main()
