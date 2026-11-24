"""All-eight-device validation, with exact CPU int64 accumulation reference."""
import json,time
from pathlib import Path
import torch
from gemm_kernel import gemm,difference,supported
from vllm.plugins import load_general_plugins
load_general_plugins()
from vllm_metax.model_executor.layers.quantization import _python_api_ops as original


def main():
    torch.set_num_threads(1);torch.manual_seed(27)
    cases=[(1,1,1),(7,65,31),(17,63,65),(33,129,127),(1,128,128),(16,128,256),(173,256,4096)]
    results=[]
    for device in range(8):
        torch.cuda.set_device(device)
        for index,(m,n,k) in enumerate(cases):
            ac=torch.randint(-128,128,(m,k),dtype=torch.int8)
            bc=torch.randint(-128,128,(n,k),dtype=torch.int8).t()
            if index==0:ac.fill_(-128);bc.fill_(-128)
            if index==1:ac.zero_()
            if index==2:ac.fill_(127);bc.fill_(-128)
            sa=torch.rand((m,1),dtype=torch.float32)*0.01+1e-5
            sb=torch.rand((n,1),dtype=torch.float32)*0.01+1e-5
            if index%2:sa=sa[:1].clone()
            if index%3==0:sb=sb[:1].clone()
            a=ac.to('cuda');b=bc.to('cuda');sag=sa.to('cuda');sbg=sb.to('cuda')
            # Include positive non-unit A stride and both B layouts.
            if index==3:a=torch.stack([a,a],dim=-1)[...,0]
            if index%2:b=b.contiguous()
            y,c=gemm(a,b,sag,sbg)
            ref=ac.long()@bc.long()
            assert torch.equal(c.cpu().long(),ref),(device,index,'int32')
            fp32=((ref.float()*sa.reshape(-1,1))*sb.reshape(1,-1)).to(torch.bfloat16)
            fp64=((ref.double()*sa.double().reshape(-1,1))*sb.double().reshape(1,-1)).to(torch.bfloat16)
            d32=difference(y.cpu(),fp32);d64=difference(y.cpu(),fp64)
            assert d32['finite'] and d32['exact'],(device,index,'fp32',d32)
            assert d64['finite'] and d64['max_bf16_ulp']<=1,(device,index,'fp64',d64)
            old=None
            if k%16==n%16==0 and a.is_contiguous() and b.stride(0)==1:
                old=difference(y,original.cutlass_scaled_mm(a,b,sag,sbg,torch.bfloat16))
                assert old['finite'] and old['max_bf16_ulp']<=1,(device,index,'original',old)
            results.append({'device':device,'shape':[m,n,k],'a_stride':list(a.stride()),'b_stride':list(b.stride()),'int32_exact':True,'fp32':d32,'fp64':d64,'original':old})
        assert not supported(a,b,sag,sbg,torch.bfloat16,torch.zeros(n,device='cuda',dtype=torch.bfloat16))
        assert not supported(a,b,sag,sbg,torch.float16)
        print(json.dumps({'device':device,'cases':len(cases),'passed':True}),flush=True)
    report={'status':'passed','cases':len(results),'devices':8,'results':results,'scope':'Prototype contract only, not arbitrary INT8 formats or full model acceptance'}
    with Path('/experiment/evidence/device_tests.json').open('x') as f:json.dump(report,f,indent=2)


if __name__=='__main__':main()
