"""Independent CPU reference for GLM KDA prefill and decode on C500."""
import json, traceback
from pathlib import Path
import torch
from vllm.plugins import load_general_plugins

def reference(q,k,v,g,beta,a,bias,initial):
    q,k,v,g,beta=[x.float() for x in (q,k,v,g,beta)]
    q=q/torch.sqrt(q.square().sum(-1,keepdim=True)+1e-6)
    k=k/torch.sqrt(k.square().sum(-1,keepdim=True)+1e-6)
    h=initial.clone().float()
    out=[]
    for t in range(q.shape[1]):
        gate=-5*torch.sigmoid(a.exp()[:,None]*(g[0,t]+bias))
        h=h*gate.exp()[:,None,:]
        delta=v[0,t]-(h*k[0,t,:,None,:]).sum(-1)
        h=h+(delta*beta[0,t,:,None])[:,:,None]*k[0,t,:,None,:]
        out.append((h*q[0,t,:,None,:]).sum(-1)*q.shape[-1]**-.5)
    return torch.stack(out)[None],h[None]

def errors(actual,ref):
    x=actual.cpu().float();y=ref.float()
    return dict(max_abs=float((x-y).abs().max()),relative_l2=float((x-y).norm()/y.norm().clamp_min(1e-8)),finite=bool(x.isfinite().all()))

def main():
    load_general_plugins()
    from vllm.models.glm5next.nvidia.ops.third_party.kda import chunk_kda_with_fused_gate,fused_recurrent_kda
    torch.set_num_threads(4);torch.manual_seed(53)
    cases=[]
    for length in [1,20,65,129]:
        heads,dim=8,128
        q,k,v,g=[torch.randn(1,length,heads,dim,dtype=torch.bfloat16) for _ in range(4)]
        beta_raw=torch.randn(1,length,heads,dtype=torch.bfloat16)
        beta=beta_raw.float().sigmoid()
        a=torch.randn(heads)*.3-1
        bias=torch.randn(heads,dim)*.2-1
        initial=torch.randn(heads,dim,dim)*.05
        expected,state=reference(q,k,v,g,beta,a,bias,initial)
        cu=torch.tensor([0,length],dtype=torch.int32,device='cuda')
        # Exact same gate/beta transforms as the production prefill.
        actual,final=chunk_kda_with_fused_gate(q=q.cuda(),k=k.cuda(),v=v.cuda(),raw_g=g.cuda(),beta=beta.cuda(),
            A_log=a.cuda(),g_bias=bias.cuda(),initial_state=initial[None].cuda(),output_final_state=True,
            use_qk_l2norm_in_kernel=True,cu_seqlens=cu,safe_gate=True,lower_bound=-5.)
        case=dict(length=length,kind='chunk',output=errors(actual,expected),state=errors(final,state),state_transposed=errors(final.transpose(-1,-2),state))
        print(json.dumps(case),flush=True);cases.append(case)
        # Sequence length one with padded state block stride and nonzero state index.
        slots=torch.zeros((4,heads*dim*dim+256),device='cuda')
        cache=slots[:,:heads*dim*dim].view(4,heads,dim,dim)
        cache[2].copy_(initial)
        seq=torch.tensor([0,1],dtype=torch.int32,device='cuda')
        idx=torch.tensor([2],dtype=torch.int32,device='cuda')
        expected1,state1=reference(q[:,:1],k[:,:1],v[:,:1],g[:,:1],beta[:,:1],a,bias,initial)
        actual,final=fused_recurrent_kda(q=q[:,:1].cuda(),k=k[:,:1].cuda(),v=v[:,:1].cuda(),g=g[:,:1].cuda(),
            beta=beta_raw[:,:1].cuda(),initial_state=cache,use_qk_l2norm_in_kernel=True,
            cu_seqlens=seq,ssm_state_indices=idx,sigmoid_beta=True,a_log=a.cuda(),g_bias=bias.cuda(),
            compute_gate=True,lower_bound=-5.)
        case=dict(length=1,kind='recurrent',source_length=length,output=errors(actual,expected1),state=errors(cache[2:3],state1))
        print(json.dumps(case),flush=True);cases.append(case)
    passed=all(c['output']['finite'] and c['output']['relative_l2']<.03 and c['state']['relative_l2']<.03 for c in cases)
    Path('/work/evidence/kda_numerics.json').write_text(json.dumps(dict(passed=passed,cases=cases),indent=2))
    assert passed, 'KDA numerical reference mismatch'
if __name__=='__main__':main()

