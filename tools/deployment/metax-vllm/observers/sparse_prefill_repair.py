"""Opt-in C500 BF16 512/512 sparse-prefill address-width repair."""
import torch
import _inferoptlab_flashmla_offset64 as native


def prefill(q, kv, indices, sm_scale, d_v=512, indices_all_valid_per_q=None,
            attn_sink=None, topk_length=None, out=None):
    if q.dtype != torch.bfloat16 or kv.dtype != torch.bfloat16 or q.shape[-1] != 512 or d_v != 512 or kv.shape[1] != 1:
        raise ValueError('offset64 kernel requires C500 BF16 NoPE 512/512 with one KV head')
    if attn_sink is not None:
        raise ValueError('offset64 kernel does not implement attention sinks')
    if topk_length is not None:
        columns = torch.arange(indices.shape[-1], device=indices.device)
        indices = indices.masked_fill(columns.view(1, 1, -1) >= topk_length.view(-1, 1, 1), -1)
    flags = torch.zeros((q.shape[0], 1), device=q.device, dtype=torch.bool)
    result = native.prefill(q, kv, indices, sm_scale, d_v, flags)
    if out is not None:
        out.copy_(result[0])
        return out, result[1], result[2]
    return result
