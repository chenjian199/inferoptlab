"""Regression checks for GLM INT8 scale ownership and BF16 FP8 fallback."""
import json
from pathlib import Path
import torch
from vllm.plugins import load_general_plugins

def main():
    load_general_plugins()
    from vllm_metax.models.glm5next.common.model import _try_load_fp8_attn_proj
    results=[]
    prefix='layers.3.self_attn'
    mapping={'q_a_proj':'fused_qkv_a_proj','kv_a_proj_with_mqa':'fused_qkv_a_proj','q_b_proj':'q_b_proj','o_proj':'o_proj'}
    for source,target in mapping.items():
        params={f'{prefix}.{target}.weight':torch.zeros((128,128),dtype=torch.int8),
                f'{prefix}.{target}.weight_scale':torch.full((128,1),float('nan'))}
        for name,tensor in [('weight',torch.ones((128,128),dtype=torch.int8)),('weight_scale',torch.ones((128,1)))]:
            buf={};loaded=set()
            handled=_try_load_fp8_attn_proj(f'{prefix}.{source}.{name}',tensor,buf,params,loaded,0)
            assert not handled and not buf and not loaded,(source,name,buf)
            results.append(dict(source=source,tensor=name,normal_loader_retains_ownership=True))
    for scale_name in ['weight_scale','weight_scale_inv']:
        for scale_first in [False,True]:
            param=torch.nn.Parameter(torch.zeros((128,128),dtype=torch.bfloat16),requires_grad=False)
            param.weight_loader=lambda dest,value:dest.data.copy_(value)
            params={f'{prefix}.q_b_proj.weight':param}
            weight=(torch.ones((128,128))*2).to(torch.float8_e4m3fn)
            scale=torch.tensor([[.25]])
            pairs=[('weight',weight),(scale_name,scale)]
            if scale_first:pairs.reverse()
            buf={};loaded=set()
            for name,tensor in pairs:
                assert _try_load_fp8_attn_proj(f'{prefix}.q_b_proj.{name}',tensor,buf,params,loaded,0)
            assert torch.equal(param,torch.full_like(param,.5))
            assert f'{prefix}.q_b_proj.weight' in loaded
            results.append(dict(fp8_scale=scale_name,scale_first=scale_first,dequantization_preserved=True))
    report=dict(passed=True,cases=results)
    Path('/work/evidence/glm_mla_scale_loader.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()

