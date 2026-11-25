# SPDX-License-Identifier: Apache-2.0
# 2026 - Modified by MetaX Integrated Circuits (Shanghai) Co., Ltd. All Rights Reserved.
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
# -----------------------------------------------------------------------------
# Note: mcoplib 0.4.14 exposes the seven-argument alignment ABI. vLLM 0.32
#       always passes an eighth, optional scatter_idx output. Adapt only the
#       legacy schema and only calls that do not request this output.
# Affected versions: vLLM 0.32.0 (5df63a7203), MetaX 0962c873, mcoplib
#       0.4.14+gf3794c4.maca3.9.0.31.torch2.10 (verified 2026-11-22).
# Remove at: The deployed native alignment schema includes scatter_idx.
# -----------------------------------------------------------------------------

import torch
from vllm import _custom_ops as ops  # noqa: F401

from vllm_metax.patch.utils import patch


def moe_align_block_size(
    topk_ids: torch.Tensor,
    num_experts: int,
    block_size: int,
    sorted_token_ids: torch.Tensor,
    experts_ids: torch.Tensor,
    num_tokens_post_pad: torch.Tensor,
    expert_map: torch.Tensor | None = None,
    scatter_idx: torch.Tensor | None = None,
) -> None:
    if scatter_idx is not None:
        raise NotImplementedError(
            "Installed mcoplib alignment ABI does not support scatter_idx"
        )
    torch.ops._moe_C.moe_align_block_size(
        topk_ids,
        num_experts,
        block_size,
        sorted_token_ids,
        experts_ids,
        num_tokens_post_pad,
        expert_map,
    )


# Importing upstream ops loads platform kernels before inspecting the schema.
# Leave the upstream callable unchanged for newer native providers.
_arguments = torch.ops._moe_C.moe_align_block_size.default._schema.arguments
if [a.name for a in _arguments] == [
    "topk_ids",
    "num_experts",
    "block_size",
    "sorted_token_ids",
    "experts_ids",
    "num_tokens_post_pad",
    "maybe_expert_map",
]:
    moe_align_block_size = patch("vllm._custom_ops", "moe_align_block_size")(
        moe_align_block_size
    )
