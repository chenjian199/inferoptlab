# Adapted from deepseek-ai/FlashMLA(https://github.com/deepseek-ai/FlashMLA)
from typing import Optional, Tuple, Callable, Dict
import torch

import flash_mla_cuda as flash_mla
from functools import wraps
import warnings
import numpy as np
import dataclasses

@dataclasses.dataclass
class FlashMLASchedMeta:
    """
    A class that stores the tile scheduler metadata of FlashMLA
    """

    @dataclasses.dataclass
    class Config:
        b: int
        s_q: int
        h_q: int
        page_block_size: int
        h_k: int

        causal: bool
        is_fp8_kvcache: bool
        topk: Optional[int]

        extra_page_block_size: Optional[int]
        extra_topk: Optional[int]

    have_initialized: bool = False

    config: Optional[Config] = None

    tile_scheduler_metadata: Optional[torch.Tensor] = None   # (num_sm_parts, TileSchedulerMetaDataSize), dtype torch.int32.
    num_splits: Optional[torch.Tensor] = None                # (1), dtype torch.int32.

def get_mla_metadata(
    *args,
    **kwargs
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Returns an empty instance of FlashMLASchedMeta. The actual scheduling metadata will be generated during the first invocation of flash_mla_with_kvcache.

    # NOTE:
    The FlashMLA `get_mla_metadata` interface has been updated in this version.
    Its overall functionality and calling semantics remain unchanged, but the
    type definitions and state management requirements for `metadata` and
    `num_splits` have changed.

    During a single inference pass, `metadata` is reused across all MLA layers.
    Therefore, callers are responsible for maintaining the lifetime and state of
    both `metadata` and `num_splits` properly.

    If these variables are reused across layers, cached, passed asynchronously, or
    shared by reference in other execution paths, callers should create copies as
    needed to avoid reference conflicts, state corruption, or runtime errors.

    Please review the usage of `get_mla_metadata` after upgrading and adjust the
    handling of `metadata` and `num_splits` according to the updated type
    definitions.

    Arguments:
        This function does not need any arguments, but we keep *args and **kwargs to be compatible with the old interface.

    Return:
        A tuple. Due to historical reasons, we return a tuple of (FlashMLASchedMeta, None) now. Only the first element is useful.
    """
    return FlashMLASchedMeta(), None


def flash_mla_with_kvcache(
    q: torch.Tensor,
    k_cache: torch.Tensor,
    block_table: Optional[torch.Tensor],
    cache_seqlens: Optional[torch.Tensor],
    head_dim_v: int,
    tile_scheduler_metadata: FlashMLASchedMeta,
    num_splits: None = None,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    is_fp8_kvcache: bool = False,
    indices: Optional[torch.Tensor] = None,
    attn_sink: Optional[torch.Tensor] = None,
    extra_k_cache: Optional[torch.Tensor] = None,
    extra_indices_in_kvcache: Optional[torch.Tensor] = None,
    topk_length: Optional[torch.Tensor] = None,
    extra_topk_length: Optional[torch.Tensor] = None,
    cp_world_size=1,
    cp_rank=0,
    cp_tot_seqlen_k=None,
    indices_all_valid_per_q: Optional[torch.tensor] = None,
    out: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Arguments:
        q: (batch_size, seq_len_q, num_heads_q, head_dim).
        k_cache: (num_blocks, page_block_size, num_heads_k, head_dim).
                Different modes (including fp8/bf16, and sparsity) has different KV cache layouts. See comments below for details.
                The KV cache must be contiguously valid for sparse attention on sm100. Here "contiguously valid" means that every byte,
                from the very beginning of the KV cache, till the last byte in the KV cache, is valid memory address to visit (i.e. won't IMA).
                In other words, the KV cache could be a slice of a larger array, but cannot be a list of disjoint memory blocks.
        block_table: (batch_size, max_num_blocks_per_seq), torch.int32. Can be None when sparse attention is used.
        cache_seqlens: (batch_size), torch.int32. Can be None when sparse attention is used.
        head_dim_v: Head_dim of v. Must be 512
        tile_scheduler_metadata:
                FlashMLASchedMeta, return by get_mla_metadata. You may reuse the same sched_meta across different invocations,
                but only when the tensor shapes and the values of cache_seqlens, topk_length, and extra_topk_length remain the same.
        num_splits: must be "None" (to be compatible with the old interface).
        softmax_scale: float. The scaling of QK^T before applying softmax. Default to 1 / sqrt(head_dim).
        causal: bool. Whether to apply causal attention mask. Only valid for dense attention.
        is_fp8_kvcache: bool. Whether the k_cache and v_cache are in fp8 format. Do not support fp8 kvcahce right now.
        indices: (batch_size, seq_len_q, topk). KV indices when sparse attention is enabled.
                    Pay attention that indices_in_kvcache[i][j][k] = (the index of the page block where token t resides) * block_size + (the offset of token t among the page block),
                    where t is the k-th token of the j-th q-sequence in the i-th batch.
        attn_sink: Optional[torch.Tensor], (num_heads_q, ), torch.float32. If presented, the final output will be scaled by exp(lse) / (exp(lse) + exp(attn_sink)). Have no affect on the returned softmax_lse. +inf will cause the result to become 0.
        extra_k_cache and extra_indices_in_kvcache: If provided, will attend to these extra tokens in addition to those in k_cache and indices_in_kvcache. Their format requirements are the same as k_cache and indices_in_kvcache respectively.
        topk_length/extra_topk_length: (batch_size, ), torch.int32. If provided, only the leftmost topk_length indices will be processed. Useful when the actual topk for different queries are different so that we can save some computation, compared to masking.
        indices_all_valid_per_q: [batch_size, seq_len_q, 1], bool. A scalar boolean tensor indicating wheter all entries in indices for every query token are valid.
        out: Optional pre-allocated output tensor with shape (batch_size, seq_len_q, num_heads_q, head_dim_v), same dtype as q, and contiguous. If provided, the result will be written into this buffer to avoid allocation. For dense attention, only num_heads_k == 1 (MLA) is supported.

        - descale_q: (batch_size),
        torch.float32. Descaling factors for Q, used for fp8 quantization.
        - descale_k: (batch_size),
        torch.float32. Descaling factors for K, used for fp8 quantization.

        For DeepSeek V3, DeepSeek V3.1, and DeepSeek V3.2:
        head_dim should be 576 while head_dim_v should be 512.
        In FP8+sparse mode, each token's KV cache is 656 Bytes, structured as:
            - The shape of the tensor `k_cache` is (num_blocks, page_block_size, num_heads_k, head_dim), and num_heads_k must be 1.
            - First 512 bytes: The "quantized NoPE" part, containing 512 float8_e4m3 values.
            - Next 16 bytes: Scale factors, containing 4 float32 values. The first float32 is the scale for the first 128 float8_e4m3 values, the second for the next 128, and so on.
            - Last 128 bytes: The "RoPE" part, containing 64 bfloat16 values. This part is not quantized for accuracy.

        For DeepSeek MODEL1:
        head_dim should be 512 while head_dim_v is also 512.
        In FP8+sparse mode, every block can be divided into two parts. The first parts stores NoPE0, RoPE0, NoPE1, RoPE1, ... while the second part stores scale factors: 7xue8m0, 1Bpad, 7xue8m0, 1Bpad, ...

    Return:
        out: (batch_size, seq_len_q, num_heads_q, head_dim_v).
        softmax_lse: (batch_size, num_heads_q, seq_len_q), torch.float32.
    """
    sched_meta = tile_scheduler_metadata
    indices_in_kvcache = indices
    assert isinstance(sched_meta, FlashMLASchedMeta), "tile_scheduler_metadata must be of type FlashMLASchedMeta"
    assert num_splits is None, "num_splits must be None"

    if indices_all_valid_per_q is None:
        indices_all_valid_per_q = torch.full((q.shape[0], q.shape[1], 1), False, dtype=torch.bool, device=q.device)

    topk = indices_in_kvcache.shape[-1] if indices_in_kvcache is not None else None
    extra_k_page_block_size = extra_k_cache.shape[1] if extra_k_cache is not None else None
    extra_topk = extra_indices_in_kvcache.shape[-1] if extra_indices_in_kvcache is not None else None
    if softmax_scale is None:
        softmax_scale = q.shape[-1] ** (-0.5)

    if not sched_meta.have_initialized:
        # Sanity check. We only perform sanity check during the first invocation to save CPU time.
        if indices_in_kvcache is not None:
            assert not causal, "causal must be False when indices_in_kvcache is not None (i.e. sparse attention is enabled)"

        # Initialize the tile scheduler metadata during the first invocation.
        sched_meta.have_initialized = True
        sched_meta.config = FlashMLASchedMeta.Config(
            q.shape[0],
            q.shape[1],
            q.shape[2],
            k_cache.shape[1],
            k_cache.shape[2],

            causal,
            is_fp8_kvcache,
            topk,

            extra_k_page_block_size,
            extra_topk,
        )
    else:
        # Check whether the input arguments are consistent with sched_meta
        helper_msg = " Your input arguments are inconsistent with sched_meta. Please make sure the input arguments are consistent across different invocations of flash_mla_with_kvcache on the same sched_meta."
        assert sched_meta.config is not None
        assert sched_meta.config.b == q.shape[0], "sched_meta.config.b must be equal to batch_size." + helper_msg
        assert sched_meta.config.s_q == q.shape[1], "sched_meta.config.s_q must be equal to seq_len_q." + helper_msg
        assert sched_meta.config.h_q == q.shape[2], "sched_meta.config.h_q must be equal to num_heads_q." + helper_msg
        assert sched_meta.config.page_block_size == k_cache.shape[1], "sched_meta.config.page_block_size must be equal to page_block_size." + helper_msg
        assert sched_meta.config.h_k == k_cache.shape[2], "sched_meta.config.h_k must be equal to num_heads_k." + helper_msg
        assert sched_meta.config.causal == causal, "sched_meta.config.causal must be equal to causal." + helper_msg
        assert sched_meta.config.is_fp8_kvcache == is_fp8_kvcache, "sched_meta.config.is_fp8_kvcache must be equal to is_fp8_kvcache." + helper_msg
        assert sched_meta.config.topk == topk, "sched_meta.config.topk must be equal to the last dim of indices_in_kvcache." + helper_msg
        assert sched_meta.config.extra_page_block_size == extra_k_page_block_size, "sched_meta.config.extra_page_block_size must be equal to the page_block_size of extra_k_cache." + helper_msg
        assert sched_meta.config.extra_topk == extra_topk, "sched_meta.config.extra_topk must be equal to the last dim of extra_indices_in_kvcache." + helper_msg

    if (q.dtype == torch.float8_e4m3fn):
        s_q = q.shape[1]
        assert cp_world_size == 1 or s_q == 1, "fp8 mla decode not support dcp + mtp"
        if indices is None:
            assert False, "please use flash_mla_with_kvcache_fp8 api for dense fp8 mla"
        else:
            #sparse fp8 MLA
            out, lse = decode_fp8_torch(q, k_cache, cache_seqlens, block_table, 512, causal, indices)
    else:
        if topk is not None:
            # Sparse Attention
            assert not causal, "causal must be False when sparse attention is enabled"
            # assert is_fp8_kvcache ==False, "is_fp8_kv_cache must be False when sparse attention is enabled"
            out, lse, new_tile_scheduler_metadata, new_num_splits = flash_mla.sparse_decode_fwd(
                q, k_cache, indices_in_kvcache, topk_length, attn_sink,
                sched_meta.tile_scheduler_metadata, sched_meta.num_splits,
                extra_k_cache, extra_indices_in_kvcache, extra_topk_length,
                head_dim_v, softmax_scale, indices_all_valid_per_q, out, is_fp8_kvcache
            )
        else:
            # Dense Attention
            assert indices_in_kvcache is None, "indices_in_kvcache must be None when dense attention is used."
            assert attn_sink is None, "attn_sink must be None when dense attention is used."
            assert extra_k_cache is None, "extra_k_cache must be None when dense attention is used."
            assert extra_indices_in_kvcache is None, "extra_indices_in_kvcache must be None when dense attention is used."
            assert topk_length is None, "topk_length must be None when dense attention is used."
            assert extra_topk_length is None, "extra_topk_length must be None when dense attention is used."
            assert block_table is not None and cache_seqlens is not None, "block_table and cache_seqlens must be provided when dense attention is used."
            out, lse, new_tile_scheduler_metadata, new_num_splits = flash_mla.dense_decode_fwd(
                q, k_cache, head_dim_v,
                cache_seqlens, block_table,
                softmax_scale, causal,
                sched_meta.tile_scheduler_metadata, sched_meta.num_splits,
                cp_world_size, cp_rank, cp_tot_seqlen_k, out
            )
        if (not is_fp8_kvcache):
            sched_meta.tile_scheduler_metadata = new_tile_scheduler_metadata
            sched_meta.num_splits = new_num_splits

    return out, lse
#ifndef __MLA_OPEN_SOURCE__
def get_mla_metadata_dense_fp8(
    cache_seqlens: torch.Tensor,
    num_q_tokens_per_head_k: int,
    num_heads_k: int,
) -> Tuple[torch.Tensor, torch.Tensor]:
    return flash_mla.get_mla_metadata(
        cache_seqlens, num_q_tokens_per_head_k, num_heads_k, None, False, None
    )

def flash_mla_with_kvcache_fp8(
    q: torch.Tensor,
    k_cache: torch.Tensor,
    block_table: torch.Tensor,
    cache_seqlens: torch.Tensor,
    head_dim_v: int,
    tile_scheduler_metadata: torch.Tensor,
    num_splits: torch.Tensor,
    softmax_scale: Optional[float] = None,
    causal: bool = False,
    descale_q: Optional[torch.Tensor] = None,
    descale_k: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    Arguments:
        q: (batch_size, seq_len_q, num_heads_q, head_dim).
        k_cache: (num_blocks, page_block_size, num_heads_k, head_dim).
                Different modes (including fp8/bf16, and sparsity) has different KV cache layouts. See comments below for details.
                The KV cache must be contiguously valid for sparse attention on sm100. Here "contiguously valid" means that every byte,
                from the very beginning of the KV cache, till the last byte in the KV cache, is valid memory address to visit (i.e. won't IMA).
                In other words, the KV cache could be a slice of a larger array, but cannot be a list of disjoint memory blocks.
        block_table: (batch_size, max_num_blocks_per_seq), torch.int32. Can be None when sparse attention is used.
        cache_seqlens: (batch_size), torch.int32. Can be None when sparse attention is used.
        head_dim_v: Head_dim of v. Must be 512
        tile_scheduler_metadata:
                FlashMLASchedMeta, return by get_mla_metadata. You may reuse the same sched_meta across different invocations,
                but only when the tensor shapes and the values of cache_seqlens, topk_length, and extra_topk_length remain the same.
        num_splits: must be "None" (to be compatible with the old interface).
        softmax_scale: float. The scaling of QK^T before applying softmax. Default to 1 / sqrt(head_dim).
        causal: bool. Whether to apply causal attention mask. Only valid for dense attention.
        descale_q: (batch_size), torch.float32. Descaling factors for Q, used for fp8 quantization.
        descale_k: (batch_size), torch.float32. Descaling factors for K, used for fp8 quantization.

    Return:
        out: (batch_size, seq_len_q, num_heads_q, head_dim_v).
        softmax_lse: (batch_size, num_heads_q, seq_len_q), torch.float32.
    """
    if softmax_scale is None:
        softmax_scale = q.shape[-1] ** (-0.5)
    out, softmax_lse = flash_mla.fwd_kvcache_mla_fp8(
        q,
        k_cache,
        head_dim_v,
        cache_seqlens,
        block_table,
        softmax_scale,
        causal,
        tile_scheduler_metadata,
        num_splits,
        descale_q,
        descale_k,
    )
    return out, softmax_lse
#endif

def flash_mla_sparse_fwd(
    q: torch.Tensor,
    kv: torch.Tensor,
    indices: torch.Tensor,
    sm_scale: float,
    d_v: int = 512,
    indices_all_valid_per_q: Optional[torch.tensor] = None,
    attn_sink: Optional[torch.Tensor] = None,
    topk_length: Optional[torch.Tensor] = None,
    out: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Sparse attention prefill kernel

    Args:
        q: [s_q, h_q, d_qk], bfloat16
        kv: [s_kv, h_kv, d_qk], bfloat16
        indices: [s_q, h_kv, topk], int32. Invalid indices should be set to -1 or numbers >= s_kv
        sm_scale: float
        d_v: The dimension of value vectors. Can only be 512
        attn_sink: optional, [h_q], float32.
            If attn_sink is provided, when computing output, output will be additionally multiplied by exp(lse) / (exp(lse) + exp(attn_sink)).
            +-inf in attn_sink will be handled normally (i.e., -inf has no effect, +inf will make corresponding output all zeros).
            This argument has no effect on lse and max_logits.
        topk_length: optional, [s_q], int32. If provided, the i-th q token will only attend to k tokens specified by indices[i, :, :topk_length[i]], ignoring later k/v tokens (even if provided in indices).
            In extremely rare cases (topk_length provided, there is a valid topk index between topk_length[i] ~ s_kv, and that topk index points to a k token containing NaN), operator output will contain NaN, so please avoid this situation.
        indices_all_valid_per_q: [s_q, 1], bool. A scalar boolean tensor indicating wheter all entries for every query token in indices are valid.
        out: optional pre-allocated output tensor with shape [s_q, h_q, d_v], bfloat16, contiguous on the last dim. If provided, the result will be written into this buffer to avoid allocation.

    Returns:
        (output, max_logits, lse)
        About the definition of output, max_logits and lse, please refer to README.md
        - output: [s_q, h_q, d_v], bfloat16
        - max_logits:  [s_q, h_q], float
        - lse: [s_q, h_q], float, 2-based log-sum-exp
    """
    if (q.dtype == torch.float8_e4m3fn and kv.dtype == torch.float8_e4m3fn):
        results = sparse_prefill_fp8_torch(
            q, kv, indices, sm_scale, d_v
        )
    else:
        if indices_all_valid_per_q is None:
            indices_all_valid_per_q = torch.full((q.shape[0], 1), False, dtype=torch.bool, device=q.device)
        results = flash_mla.sparse_prefill_fwd(
            q, kv, indices, sm_scale, d_v, attn_sink, topk_length, indices_all_valid_per_q, out
        )
    return results

def flash_mla_sparse_bwd(
    q: torch.Tensor,
    kv: torch.Tensor,
    out: torch.Tensor,
    dout: torch.Tensor,
    lse: torch.Tensor,
    indices: torch.Tensor,
    sm_scale: float,
    attn_sink: Optional[torch.Tensor] = None,
    topk_length: Optional[torch.Tensor] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Sparse attention prefill kernel

    Args:
        q:         [S, H, D] bf16
        kv:        [S_kv, 1, D] bf16
        o:         [S, H, D] bf16 (forward output)
        do:        [S, H, D] bf16 (grad of output)
        lse:       [S, H] fp32 (log-sum-exp from forward)
        indices: [S, topk] int32
        sm_scale:  float or None
        attn_sink: [H] fp32

    Returns:
        dq:         [S, H, D] bf16
        dkv:        [S_kv, 1, D] bf16
        d_attn_sink: [H] fp32
    """
    results = flash_mla.sparse_bwd(
        q, kv, out, dout, lse, indices, sm_scale, attn_sink, topk_length
    )
    return results


#ifndef __MLA_OPEN_SOURCE__
import enum
class FP8KVCacheLayout(enum.Enum):
    V32_FP8Sparse = 1
    MODEL1_FP8Sparse = 2

    def get_meta(self) -> Tuple[int, int, int, int, int]:
        # Return: (d, d_nope, d_rope, tile_size, num_tiles)
        return {
            FP8KVCacheLayout.V32_FP8Sparse: (576, 512, 64, 128, 4),
            FP8KVCacheLayout.MODEL1_FP8Sparse: (512, 448, 64, 64, 7)
        }[self]

def dequantize_k_cache(
    quant_k_cache: torch.Tensor,    # (num_blocks, block_size, 1, bytes_per_token)
    kvcache_layout: FP8KVCacheLayout = FP8KVCacheLayout.MODEL1_FP8Sparse,
) -> torch.Tensor:
    """
    De-quantize the k-cache
    """
    d, d_nope, d_rope, tile_size, num_tiles = kvcache_layout.get_meta()
    num_blocks, block_size, h_k, _ = quant_k_cache.shape
    assert h_k == 1
    result = torch.empty((num_blocks, block_size, d), dtype=torch.bfloat16, device=quant_k_cache.device)

    if kvcache_layout == FP8KVCacheLayout.V32_FP8Sparse:
        quant_k_cache = quant_k_cache.view(num_blocks, block_size, -1)

        input_nope = quant_k_cache[..., :d_nope]
        input_scale = quant_k_cache[..., d_nope:d_nope + num_tiles*4].view(torch.float32)
        input_rope = quant_k_cache[..., d_nope + num_tiles*4:].view(torch.bfloat16)
        result[..., d_nope:] = input_rope

        for tile_idx in range(0, num_tiles):
            cur_nope = input_nope[..., tile_idx*tile_size:(tile_idx+1)*tile_size].to(torch.float32)
            cur_scales = input_scale[..., tile_idx].unsqueeze(-1)
            result[..., tile_idx*tile_size:(tile_idx+1)*tile_size] = cur_nope * cur_scales

    elif kvcache_layout == FP8KVCacheLayout.MODEL1_FP8Sparse:
        quant_k_cache = quant_k_cache.view(num_blocks, -1)  # [num_blocks, ...]
        input_nope_rope = quant_k_cache[:, :block_size*(d_nope+2*d_rope)].view(num_blocks, block_size, d_nope + 2*d_rope)
        input_nope = input_nope_rope[:, :, :d_nope]
        input_rope = input_nope_rope[:, :, d_nope:].view(torch.bfloat16)
        input_scale = quant_k_cache[:, block_size*(d_nope+2*d_rope):].view(num_blocks, block_size, 8)[:, :, :7].view(torch.float8_e8m0fnu)   # [num_blocks, block_size, num_tiles]

        result[..., d_nope:] = input_rope
        for tile_idx in range(0, num_tiles):
            cur_nope = input_nope[..., tile_idx*tile_size:(tile_idx+1)*tile_size].to(torch.bfloat16)
            cur_scales = input_scale[:, :, tile_idx].to(torch.bfloat16).unsqueeze(-1)
            result[..., tile_idx*tile_size: (tile_idx+1)*tile_size] = cur_nope * cur_scales

    else:
        raise NotImplementedError(f"Unsupported kvcache_layout: {kvcache_layout}")

    result = result.view(num_blocks, block_size, 1, d)
    return result

def sparse_decode_fwd_fp8_torch(
    q: torch.Tensor,
    k_cache: torch.Tensor,
    head_dim_v: int,
    softmax_scale: Optional[float] = None,
    indices: Optional[torch.Tensor] = None,
    attn_sink: Optional[torch.Tensor] = None,
    extra_k_cache: Optional[torch.Tensor] = None,
    extra_indices_in_kvcache: Optional[torch.Tensor] = None,
    topk_length: Optional[torch.Tensor] = None,
    extra_topk_length: Optional[torch.Tensor] = None,
):
    b, s_q, h_q, d_qk = q.shape
    d_v = head_dim_v
    def process_kv_scope(indices_in_kvcache: torch.Tensor, blocked_k: torch.Tensor, topk_length: Optional[torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor]:
        assert indices_in_kvcache is not None
        topk = indices_in_kvcache.size(-1)
        indices_in_kv_cache_fixed = torch.clamp_min(indices_in_kvcache, 0) # Otherwise torch.index_select will complain
        gathered_kv = blocked_k.view(-1, d_qk).index_select(0, indices_in_kv_cache_fixed.view(-1)).view(b, s_q, topk, d_qk)  # [b, s_q, topk, d]
        invalid_mask = indices_in_kvcache == -1
        if topk_length is not None:
            invalid_mask |= torch.arange(0, topk).view(1, 1, topk).broadcast_to(b, s_q, topk) >= topk_length.view(b, 1, 1)
        return gathered_kv, invalid_mask
    k_cache = dequantize_k_cache(k_cache)
    gathered_kv, invalid_mask = process_kv_scope(indices, k_cache, topk_length)
    if extra_k_cache is not None:
        extra_k_cache = dequantize_k_cache(extra_k_cache)
        gathered_kv1, invalid_mask1 = process_kv_scope(extra_indices_in_kvcache, extra_k_cache, extra_topk_length)
        gathered_kv = torch.cat([gathered_kv, gathered_kv1], dim=2)  # [b, s_q, topk+extra_topk, d]
        invalid_mask = torch.cat([invalid_mask, invalid_mask1], dim=2)   # [b, s_q, topk+extra_topk]

    gathered_kv = gathered_kv.view(b*s_q, -1, d_qk).float()
    gathered_kv[torch.isnan(gathered_kv)] = 0.0
    q = q.float().view(b*s_q, h_q, d_qk)
    attn_weight = q @ gathered_kv.transpose(-1, -2)  # [t.b*t.s_q, t.h_q, topk+extra_topk]
    attn_weight *= softmax_scale
    attn_weight[invalid_mask.view(b*s_q, 1, -1).broadcast_to(b*s_q, h_q, invalid_mask.size(-1))] = float("-inf")
    lse = attn_weight.logsumexp(dim=-1)  # [t.b*t.s_q, t.h_q]
    attn_weight = torch.exp(attn_weight - lse.unsqueeze(-1))
    output = attn_weight @ gathered_kv[..., :d_v]    # [t.b*t.s_q, t.h_q, t.dv]
    output = output.view(b, s_q, h_q, d_v)
    lse = lse.view(b, s_q, h_q)

    # Attention sink
    if attn_sink is not None:
        output *= (1.0 / (1.0 + torch.exp(attn_sink.view(1, 1, h_q) - lse))).unsqueeze(-1)

    # Correct for q tokens which has no attendable k
    lonely_q_mask = (lse == float("-inf"))
    output[lonely_q_mask.unsqueeze(-1).broadcast_to(b, s_q, h_q, d_v)] = 0.0
    lse[lonely_q_mask] = float("+inf")

    return output.to(torch.bfloat16), lse.transpose(1, 2)

def decode_fp8_torch(
    q: torch.Tensor,    # [batch_size, s_q, h_q, d]
    blocked_k: torch.Tensor,    # [?, block_size, h_kv, d]
    cache_seqlens: torch.Tensor,    # [batch_size]
    block_table: torch.Tensor,      # [batch_size, ?]
    dv: int,
    is_causal: bool,
    indices: Optional[torch.Tensor] = None   # [batch_size, s_q, topk]
) -> Tuple[torch.Tensor, torch.Tensor]:
    """
    A reference implementation in PyTorch
    """
    import math
    def get_topk_attn_mask(s_q: int, s_k: int, indices: torch.Tensor):
        mask = torch.zeros(s_q, s_k, dtype=torch.bool)
        for i in range(s_q):
            cur_indices = indices[i]
            valid_indices = cur_indices[cur_indices != -1]
            mask[i, valid_indices] = True
        return mask

    def scaled_dot_product_attention(
        batch_idx: int,
        query: torch.Tensor,    # [h_q, s_q, d]
        kv: torch.Tensor,      # [h_kv, s_k, d]
        dv: int,
        is_causal,
        indices: Optional[torch.Tensor],  # [s_q, topk]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        h_q = query.size(0)
        h_kv = kv.size(0)
        s_q = query.shape[-2]
        s_k = kv.shape[-2]
        query = query.float()
        kv = kv.float()
        if h_kv != 1:
            kv = kv.repeat_interleave(h_q // h_kv, dim=0)
        kv[np.isnan(kv)] = 0.0
        attn_weight = query @ kv.transpose(-2, -1) # [h_q, s_q, s_k]
        if (is_causal and query.size(1) > 1) or indices is not None:
            mask = torch.ones(s_q, s_k, dtype=torch.bool)
            if is_causal:
                assert indices is None
                mask = mask.tril(diagonal=s_k - s_q)
            if indices is not None:
                mask &= get_topk_attn_mask(s_q, s_k, indices)
            attn_bias = torch.zeros(s_q, s_k, dtype=torch.float)
            attn_bias.masked_fill_(mask.logical_not(), float("-inf"))
            attn_weight += attn_bias.to(q.dtype)
        attn_weight /= math.sqrt(query.size(-1))
        lse = attn_weight.logsumexp(dim=-1) # [h_q, s_q]
        attn_weight = torch.softmax(attn_weight, dim=-1, dtype=torch.float32)
        output = attn_weight @ kv[..., :dv]    # [h_q, s_q, dv]
        # Correct for q tokens which has no attendable k
        lonely_q_mask = (lse == float("-inf"))
        output[lonely_q_mask.unsqueeze(-1).broadcast_to(h_q, s_q, dv)] = 0.0
        lse[lonely_q_mask] = float("+inf")

        return output, lse

    b, s_q, h_q, d = q.size()
    block_size = blocked_k.size(1)
    h_kv = blocked_k.size(2)
    cache_seqlens_cpu = cache_seqlens.cpu()
    out_ref = torch.empty(b, s_q, h_q, dv, dtype=torch.float32)
    lse_ref = torch.empty(b, h_q, s_q, dtype=torch.float32)
    for i in range(b):
        cur_len = cache_seqlens_cpu[i].item()
        cur_num_blocks = cdiv(cur_len, block_size)
        cur_block_indices = block_table[i][0: cur_num_blocks]
        cur_kv = blocked_k[cur_block_indices].view(-1, h_kv, d)[:cur_len, ...]
        cur_out, cur_lse = scaled_dot_product_attention(
            i,
            q[i].transpose(0, 1),
            cur_kv.transpose(0, 1),
            dv,
            is_causal,
            indices[i] if indices is not None else None
        )
        out_ref[i] = cur_out.transpose(0, 1)
        lse_ref[i] = cur_lse
    out_ref = out_ref.to(torch.bfloat16)
    return out_ref, lse_ref


def sparse_prefill_fp8_torch(q, kv, indices, sm_scale, d_v):
    import math
    def log2sumexp2(a: torch.Tensor, dim: int) -> torch.Tensor:
        return torch.logsumexp(a * math.log(2), dim=dim) * math.log2(math.e)

    assert len(q.shape) == len(kv.shape) == 3 # b == 1
    s_q, _, d_qk = q.shape
    s_kv, _, _ = kv.shape

    indices = indices[:, 0, :] # [s_q, topk]
    invalid_indices_mask = (indices < 0) | (indices >= s_kv)
    qs = q[:, :, :].float()  # [s_q, h_q, d_qk]
    kvs = kv[:, 0, :].float()  # [s_kv, d_qk]
    _, topk = indices.shape

    kvs = torch.index_select(kvs, 0, indices.masked_fill(invalid_indices_mask, 0).flatten()).view(s_q, topk, d_qk)  # [s_q, topk, d_qk]
    attn_score = qs @ kvs.transpose(1, 2)    # [s_q, h_q, topk]
    attn_score.masked_fill_(invalid_indices_mask.unsqueeze(1), float('-inf'))
    attn_score *= sm_scale * math.log2(math.e)
    max_logits = torch.max(attn_score, dim=-1)[0]   # [s_q, h_q]
    lse = log2sumexp2(attn_score, dim=-1)   # [s_q, h_q]
    attn_score = torch.exp2(attn_score - lse.unsqueeze(-1))   # [s_q, h_q, topk]
    lse = lse / math.log2(math.e)
    result = attn_score @ kvs[:, :, :d_v]

    return (result, max_logits, lse)
#endif