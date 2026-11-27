"""Offline arithmetic for the draft single-file matrix; no GPU probing or launch.

Callers must supply resolved block-pool sizes and a justified per-slot peak
including retained prefixes, state copies, warmup and output growth. A token
capacity printed at max_model_len is not a substitute for that accounting.
"""
from __future__ import annotations


def _integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return value


def rank_limit(*, pools, max_num_seqs, max_num_batched_tokens):
    """Return independent residency and scheduling budgets for a DP engine.

    pools: independent pools after taking TP-worker constraints into account.
    Each has total_blocks, reserved_blocks (including the null block), and
    blocks_per_slot (sum across groups drawing from that same pool).
    The latter must be a safe bound, not an average from a single request.
    """
    if not pools:
        raise ValueError('resolved KV pool accounting is required')
    bounds = []
    for pool in pools:
        total = _integer(pool['total_blocks'], 'total_blocks')
        reserved = _integer(pool['reserved_blocks'], 'reserved_blocks')
        cost = _integer(pool['blocks_per_slot'], 'blocks_per_slot', 1)
        if reserved > total:
            raise ValueError('reserved_blocks exceeds total_blocks')
        bounds.append((total - reserved) // cost)
    kv_limit = min(bounds)
    scheduling_limit = min(
        _integer(max_num_seqs, 'max_num_seqs', 1),
        _integer(max_num_batched_tokens, 'max_num_batched_tokens', 1))
    # Queueing does not remove a warmed prefix. Do not clip resident/client
    # concurrency to the number of sequences that can be scheduled at once.
    return dict(kv_limit=kv_limit, scheduling_limit=scheduling_limit)


def glm_slot_blocks(input_tokens, output_tokens, attention_block_tokens,
                    *, mamba_groups=4, retained_state_blocks_per_group=1,
                    attention_copy_blocks=1):
    """Conservative arithmetic for the archived GLM layout, not a measured peak.

    One full-attention group, four align-mode Mamba groups (2 active blocks
    each, no speculative/prefill checkpoint extras), one circular-buffer group.
    Reserve a separate original-prefix state per Mamba group and one partial
    attention page copy. Validate the actual layout before applying this model.
    """
    length = _integer(input_tokens, 'input_tokens', 1)
    output = _integer(output_tokens, 'output_tokens', 1)
    block = _integer(attention_block_tokens, 'attention_block_tokens', 1)
    groups = _integer(mamba_groups, 'mamba_groups', 1)
    retained = _integer(retained_state_blocks_per_group, 'retained_state_blocks_per_group')
    copies = _integer(attention_copy_blocks, 'attention_copy_blocks')
    attention = (length + 1 + output + block - 1) // block
    running = attention + 2 * groups + 1
    return dict(attention_blocks=attention, runtime_model_blocks=running,
                retained_prefix_blocks=groups * retained,
                attention_copy_blocks=copies,
                reserved_slot_blocks=running + groups * retained + copies,
                status='conservative_model_not_measured_peak')


def concurrency_points(preset, per_rank_limits, request_multiplier=4):
    """Clip each requested point to the slot%DP bound, then deduplicate.

    For rank r with q slots, the first infeasible slot index is DP*q+r.
    That index equals the largest feasible total request count for that rank.
    This handles unequal rank capacities without assuming free load balancing.
    """
    if not preset or not per_rank_limits:
        raise ValueError('preset and all DP rank limits must be nonempty')
    multiplier = _integer(request_multiplier, 'request_multiplier', 1)
    desired = [_integer(c, 'concurrency', 1) for c in preset]
    limits = [_integer(q, 'per_rank_limit') for q in per_rank_limits]
    dp = len(limits)
    cap = min(dp * q + rank for rank, q in enumerate(limits))
    mapping = [dict(requested=c, effective=min(c, cap)) for c in desired]
    effective = sorted({row['effective'] for row in mapping if row['effective'] > 0})
    return dict(capacity_limit=cap, mapping=mapping,
                points=[dict(concurrency=c, requests=c * multiplier,
                             slots_per_rank=[c // dp + int(r < c % dp) for r in range(dp)])
                        for c in effective])
