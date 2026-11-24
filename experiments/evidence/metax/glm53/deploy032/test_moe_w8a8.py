"""Check the deployment TritonExperts W8A8 pipeline against CPU QDQ."""
import json
from pathlib import Path
import torch
from vllm.plugins import load_general_plugins

def quant(x):
    scale=x.float().abs().amax(-1,keepdim=True).clamp_min(1e-12)/127
    return (x.float()/scale).round().clamp(-128,127),scale

def main():
    load_general_plugins()
    from vllm.config import VllmConfig,set_current_vllm_config
    from vllm.model_executor.layers.fused_moe.config import FusedMoEConfig,FusedMoEParallelConfig,RoutingMethodType
    from vllm.model_executor.layers.fused_moe.activation import MoEActivation
    from vllm_metax.patch.bugfix.int8_w8a8.int8_moe_config import int8_w8a8_moe_quant_config
    from vllm_metax.model_executor.layers.fused_moe.experts.triton_moe import TritonExperts
    from vllm import _custom_ops as ops
    torch.set_num_threads(4);torch.manual_seed(53)
    pc=FusedMoEParallelConfig(tp_size=1,pcp_size=1,dp_size=1,ep_size=1,tp_rank=0,pcp_rank=0,dp_rank=0,ep_rank=0,sp_size=1,use_ep=False,all2all_backend='allgather_reducescatter',enable_eplb=False)
    cases=[]
    for m,n,k,e,top in [(1,256,4096,288,8),(33,256,512,8,2)]:
        a=torch.randn(m,k,dtype=torch.bfloat16)*.2
        w1=torch.randint(-64,64,(e,2*n,k),dtype=torch.int8)
        w2=torch.randint(-64,64,(e,k,n),dtype=torch.int8)
        s1=torch.rand(e,2*n,1)*.001+.0005;s2=torch.rand(e,k,1)*.001+.0005
        weights,ids=torch.rand(m,e).softmax(-1).topk(top,dim=-1)
        weights=weights/weights.sum(-1,keepdim=True)
        cfg=FusedMoEConfig(num_experts=e,experts_per_token=top,hidden_dim=k,intermediate_size=n,num_local_experts=e,num_logical_experts=e,activation=MoEActivation.SILU,device='cuda',routing_method=next(iter(RoutingMethodType)),moe_parallel_config=pc,in_dtype=torch.bfloat16)
        qc=int8_w8a8_moe_quant_config(s1.cuda(),s2.cuda(),None,None,per_act_token_quant=True)
        with set_current_vllm_config(VllmConfig()):
            expert=TritonExperts(cfg,qc)
            shapes=expert.workspace_shapes(m,2*n,k,top,e,e,None,MoEActivation.SILU)
            wa,wb,out=[torch.empty(s,device='cuda',dtype=torch.bfloat16) for s in shapes]
            qa,sa,_=ops.scaled_int8_quant(a.cuda())
            expert.apply(output=out,hidden_states=qa,w1=w1.cuda(),w2=w2.cuda(),topk_weights=weights.cuda(),topk_ids=ids.int().cuda(),activation=MoEActivation.SILU,global_num_experts=e,expert_map=None,a1q_scale=sa,a2_scale=None,workspace13=wa,workspace2=wb,expert_tokens_meta=None,apply_router_weight_on_input=False)
            actual=out.cpu().float()
        qa,sa=quant(a)
        expected=torch.zeros(m,k)
        for i in range(m):
            for t in range(top):
                eid=int(ids[i,t])
                intermediate=((qa[i]@w1[eid].float().t())*sa[i]*s1[eid,:,0]).bfloat16().float()
                act=(torch.nn.functional.silu(intermediate[:n])*intermediate[n:]).bfloat16()
                qact,sact=quant(act)
                y=((qact@w2[eid].float().t())*sact*s2[eid,:,0]).bfloat16().float()
                expected[i]+=y*weights[i,t]
        err=float((actual-expected).norm()/expected.norm())
        case=dict(m=m,n=n,k=k,experts=e,topk=top,relative_l2=err,max_abs=float((actual-expected).abs().max()),finite=bool(actual.isfinite().all()))
        cases.append(case);print(json.dumps(case),flush=True)
    passed=all(c['finite'] and c['relative_l2']<.04 for c in cases)
    Path('/work/evidence/moe_w8a8_numerics.json').write_text(json.dumps(dict(passed=passed,cases=cases),indent=2))
    assert passed
if __name__=='__main__':main()

