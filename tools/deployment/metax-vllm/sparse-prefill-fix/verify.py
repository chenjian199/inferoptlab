"""Experimental native correctness checks; never performance or model acceptance.

Run only in an exclusively owned diagnostic container after the benchmark lease
is released. The extension is not installed into the scan runtime by this script.
"""
import argparse
import json
import math

import torch
import _inferoptlab_flashmla_offset64 as candidate
import sys
# The extension directory also contains the downloaded Python package. Compare
# against the installed runtime kernel, not that source archive's older wrapper.
sys.path = [p for p in sys.path if not p.rstrip('/').endswith('build-source')]
from flash_mla.flash_mla_interface import flash_mla_sparse_fwd


def modified(q, kv, indices, lengths):
    positions=torch.arange(indices.shape[-1],device=indices.device)
    masked=indices.masked_fill(positions.view(1,1,-1)>=lengths.view(-1,1,1),-1)
    flags=torch.zeros((q.shape[0],1),device=q.device,dtype=torch.bool)
    return candidate.prefill(q,kv,masked,1/math.sqrt(512),512,flags)


def boundary(index):
    q=torch.zeros((1,64,512),device='cuda',dtype=torch.bfloat16)
    kv=torch.zeros((index+1,1,512),device='cuda',dtype=torch.bfloat16)
    kv[index].fill_(1)
    indices=torch.full((1,1,2048),-1,device='cuda',dtype=torch.int32)
    indices[0,0,0]=index
    lengths=torch.ones(1,device='cuda',dtype=torch.int32)
    print(json.dumps(dict(stage='before_candidate',index=index,element_offset=index*512)),flush=True)
    out,_,lse=modified(q,kv,indices,lengths)
    torch.cuda.synchronize()
    error=(out.float()-1).abs().max().item()
    assert torch.isfinite(out).all().item() and error<0.01
    assert torch.isfinite(lse).all().item()
    print(json.dumps(dict(stage='after_candidate',index=index,max_abs_error=error,passed=True)),flush=True)


def numerical():
    torch.manual_seed(20261125)
    reports=[]
    for queries,heads,topk in [(1,64,16),(3,64,2048),(17,128,2048),(65,64,2048)]:
        kv=torch.randn((4096,1,512),device='cuda',dtype=torch.bfloat16)
        q=torch.randn((queries,heads,512),device='cuda',dtype=torch.bfloat16)
        indices=torch.randint(0,4096,(queries,1,topk),device='cuda',dtype=torch.int32)
        lengths=torch.tensor([min(topk,[1,7,16,17,127,512,2048][i%7]) for i in range(queries)],
                             device='cuda',dtype=torch.int32)
        # Positive indices after topk_length must be masked, not accidentally used.
        reference,_,reference_lse=flash_mla_sparse_fwd(q,kv,indices,1/math.sqrt(512),topk_length=lengths)
        output,_,lse=modified(q,kv,indices,lengths)
        torch.cuda.synchronize()
        assert torch.isfinite(output).all().item() and torch.isfinite(lse).all().item()
        errors=[]
        for i in range(queries):
            selected=kv[indices[i,0,:int(lengths[i])].long(),0].float().cpu()
            scores=q[i].float().cpu() @ selected.T / math.sqrt(512)
            expected=torch.softmax(scores,dim=-1) @ selected
            actual=output[i].float().cpu()
            # BF16 implementation tolerance for this kernel check only.
            assert torch.allclose(actual,expected,atol=0.025,rtol=0.03),(queries,heads,topk,i)
            # This MetaX runtime returns natural-log LSE (zero logits over 16
            # keys produce ln(16)); compare both kernels against that convention.
            expected_lse=torch.logsumexp(scores,dim=-1)
            assert torch.allclose(lse[i].float().cpu(),expected_lse,atol=0.03,rtol=0.01)
            errors.append((actual-expected).abs().max().item())
        assert torch.allclose(output.float(),reference.float(),atol=0.025,rtol=0.03)
        assert torch.allclose(lse,reference_lse,atol=0.03,rtol=0.01)
        report=dict(queries=queries,heads=heads,topk=topk,max_abs_error=max(errors),passed=True)
        reports.append(report);print(json.dumps(report),flush=True)
    print(json.dumps(dict(stage='numerical_complete',cases=len(reports),passed=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--boundary',type=int)
    args=parser.parse_args()
    torch.cuda.set_device(0)
    if args.boundary is not None:
        assert 0<=args.boundary<=2**22+512
        boundary(args.boundary)
    else:
        numerical()
