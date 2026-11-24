"""Explicit one-layer runtime injection, local to this experimental worker."""
from pathlib import Path
import json
from worker_provenance import Provenance

TARGET='language_model.model.layers.0.mlp.gate_up_proj'


class OneLayerKernel:
    def __init__(self,old,owner):
        self.old=old;self.owner=owner
        self.stats={'calls':0,'replaced':0,'fallback':0,'shape_counts':{},'max_abs':0.0,'max_bf16_ulp':0.0,'changed_elements':0,'elements':0,'reference_checks':[]}
        self.captured=set()

    def apply_weights(self,layer,x,bias=None):
        import torch
        from vllm import _custom_ops as ops
        from vllm_metax.model_executor.layers.quantization import _python_api_ops as original
        from gemm_kernel import gemm,supported,difference
        s=self.stats;s['calls']+=1
        wq,ws,ins,izp,adj=self.old._get_layer_params(layer)
        if adj is not None or x.ndim!=2:
            s['fallback']+=1;return self.old.apply_weights(layer,x,bias)
        aq,sa,zp=ops.scaled_int8_quant(x.contiguous(),ins,izp,symmetric=True)
        if zp is not None or not supported(aq,wq,sa,ws,x.dtype,bias):
            s['fallback']+=1;return self.old.apply_weights(layer,x,bias)
        # Retain original GEMM as a shadow validator; returned tensor is candidate.
        expected=original.cutlass_scaled_mm(aq,wq,sa,ws,x.dtype,bias)
        actual,integer=gemm(aq,wq,sa,ws,x.dtype,bias)
        d=difference(actual,expected)
        if not d['finite'] or d['max_bf16_ulp']>1:
            self.save_failure({'kind':'original_gemm_mismatch','difference':d,'shape':[aq.shape[0],wq.shape[1],aq.shape[1]]})
            raise AssertionError(('Original GEMM contract failed',d))
        s['replaced']+=1
        key=','.join(map(str,[aq.shape[0],wq.shape[1],aq.shape[1]]))
        s['shape_counts'][key]=s['shape_counts'].get(key,0)+1
        s['max_abs']=max(s['max_abs'],d['max_abs']);s['max_bf16_ulp']=max(s['max_bf16_ulp'],d['max_bf16_ulp'])
        s['changed_elements']+=d['changed'];s['elements']+=d['elements']
        mode='decode' if aq.shape[0]==1 else 'prefill'
        if mode not in self.captured:
            # Independent CPU integer reference on saved rows/columns of real inputs.
            nr=min(4,aq.shape[0]);nc=min(8,wq.shape[1])
            ac=aq[:nr].cpu();bc=wq[:,:nc].cpu();ic=integer[:nr,:nc].cpu()
            sac=sa.reshape(-1)[:nr if sa.numel()>1 else 1].cpu().reshape(-1,1)
            sbc=ws.reshape(-1)[:nc if ws.numel()>1 else 1].cpu().reshape(1,-1)
            exact=ac.long()@bc.long()
            assert torch.equal(ic.long(),exact),'Real-input integer reference mismatch'
            ref32=((exact.float()*sac)*sbc).to(torch.bfloat16)
            ref64=((exact.double()*sac.double())*sbc.double()).to(torch.bfloat16)
            yc=actual[:nr,:nc].cpu();d32=difference(yc,ref32);d64=difference(yc,ref64)
            assert d32['exact'] and d64['finite'] and d64['max_bf16_ulp']<=1
            path=Path('/experiment/evidence/real_inputs')/f'rank{self.owner.rank}_{mode}.pt';path.parent.mkdir(exist_ok=True)
            assert not path.exists()
            torch.save({'a':ac,'b':bc,'scale_a':sac,'scale_b':sbc,'accumulator':ic,'candidate':yc,'original':expected[:nr,:nc].cpu()},path)
            s['reference_checks'].append({'mode':mode,'path':str(path),'int32_exact':True,'fp32':d32,'fp64':d64})
            self.captured.add(mode)
        return actual

    def save_failure(self,value):
        Path(f'/experiment/evidence/replacement_failure_rank{self.owner.rank}.json').write_text(json.dumps(value,indent=2))


class Replacement(Provenance):
    def target_info(self):
        import torch
        modules=dict(self.get_model().named_modules())
        assert TARGET in modules,(TARGET,list(modules)[:10])
        layer=modules[TARGET]
        scheme=getattr(layer,'scheme',None);kernel=getattr(scheme,'kernel',None)
        info={'rank':self.rank,'target':TARGET,'layer_class':type(layer).__module__+'.'+type(layer).__name__,
            'scheme':type(scheme).__name__,'kernel':type(kernel).__module__+'.'+type(kernel).__name__,
            'weight_shape':list(layer.weight.shape),'weight_stride':list(layer.weight.stride()),'weight_dtype':str(layer.weight.dtype),
            'bias':getattr(layer,'bias',None) is not None,'device':str(layer.weight.device)}
        assert layer.weight.dtype==torch.int8 and type(kernel).__name__=='MctlassScaledMMLinearKernel',info
        info['scheme_aliases']=[name for name,module in modules.items() if getattr(module,'scheme',None) is scheme]
        assert info['scheme_aliases']==[TARGET],info
        self._gemm_layer=layer;self._original_kernel=kernel
        return info

    def install_gemm(self):
        assert not hasattr(self,'_gemm_proxy')
        self._gemm_proxy=OneLayerKernel(self._original_kernel,self)
        self._gemm_layer.scheme.kernel=self._gemm_proxy
        return {'rank':self.rank,'installed':True,'target':TARGET}

    def gemm_stats(self):
        return {'rank':self.rank,**self._gemm_proxy.stats}

    def restore_gemm(self):
        self._gemm_layer.scheme.kernel=self._original_kernel
        assert self._gemm_layer.scheme.kernel is self._original_kernel
        return {'rank':self.rank,'restored':True}
