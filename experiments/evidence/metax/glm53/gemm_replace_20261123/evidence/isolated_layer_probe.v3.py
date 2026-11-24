"""Real checkpoint TP8 slices, replayed sequentially on healthy GPU 0.

Exercises the installed vLLM quantization scheme/kernel injection and rollback.
Synthetic activations; no claim of full-model, multi-GPU or HumanEval validation.
"""
import hashlib,json,types
from pathlib import Path
import torch
from safetensors import safe_open
from vllm.plugins import load_general_plugins
load_general_plugins()
import vllm_metax.registry.linear_kernels.int8
from vllm.model_executor.layers.quantization.compressed_tensors.schemes.compressed_tensors_w8a8_int8 import CompressedTensorsW8A8Int8
from replacement_worker import OneLayerKernel
from gemm_kernel import difference


def digest(t):return hashlib.sha256(t.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()


def main():
    torch.set_num_threads(1);torch.cuda.set_device(0)
    from vllm.distributed.parallel_state import init_distributed_environment,initialize_model_parallel,destroy_model_parallel,destroy_distributed_environment
    init_distributed_environment(world_size=1,rank=0,distributed_init_method='file:///experiment/evidence/isolated_tp1_rendezvous',local_rank=0,backend='gloo')
    initialize_model_parallel(tensor_model_parallel_size=1,pipeline_model_parallel_size=1,backend='gloo')
    root=Path('/models/GLM-5.3-Flash-W8A8')
    file=root/'model-language_model-layers-00000.safetensors'
    results=[]
    with safe_open(str(file),framework='pt',device='cpu') as tensors,torch.no_grad():
        prefix='model.language_model.layers.0.mlp.'
        shape=tensors.get_slice(prefix+'gate_proj.weight').get_shape();n,k=shape;assert n%8==0;part=n//8
        for rank in range(8):
            a,b=rank*part,(rank+1)*part
            weights=torch.cat([tensors.get_slice(prefix+key+'.weight')[a:b] for key in ['gate_proj','up_proj']],dim=0)
            scales=torch.cat([tensors.get_slice(prefix+key+'.weight_scale')[a:b] for key in ['gate_proj','up_proj']],dim=0)
            assert weights.dtype==torch.int8 and scales.numel()==2*part
            layer=torch.nn.Module();scheme=CompressedTensorsW8A8Int8('channel',False,True)
            with torch.device('cuda:0'):
                scheme.create_weights(layer,[part,part],k,torch.bfloat16,lambda *args:None)
            layer.weight.copy_(weights);layer.weight_scale.copy_(scales.reshape(2*part,1))
            scheme.process_weights_after_loading(layer)
            old=scheme.kernel;assert type(old).__name__=='MctlassScaledMMLinearKernel'
            proxy=OneLayerKernel(old,types.SimpleNamespace(rank='isolated_slice'+str(rank)))
            cases=[];torch.manual_seed(73+rank)
            for m in [1,17,173]:
                x=torch.randn((m,k*(2 if m==17 else 1)),device='cuda',dtype=torch.bfloat16)*0.5
                if m==17:x=x[:,::2]
                baseline=scheme.apply_weights(layer,x,None)
                scheme.kernel=proxy;candidate=scheme.apply_weights(layer,x,None)
                scheme.kernel=old;restored=scheme.apply_weights(layer,x,None)
                d=difference(candidate,baseline);assert d['finite'] and d['max_bf16_ulp']<=1
                assert torch.equal(restored,baseline)
                cases.append({'shape':[m,2*part,k],'input_stride':list(x.stride()),'comparison':d,'rollback_exact':True})
            assert proxy.stats['replaced']==3 and proxy.stats['fallback']==0
            results.append({'checkpoint_slice':rank,'device':0,'gate_up_rows_per_projection':[a,b],'weight_sha256':digest(weights),
                'scale_sha256':digest(scales),'scheme':type(scheme).__name__,'original_kernel':type(old).__module__+'.'+type(old).__name__,
                'processed_weight_shape':list(layer.weight.shape),'processed_weight_stride':list(layer.weight.stride()),'cases':cases,'stats':proxy.stats})
            print(json.dumps({'slice':rank,'cases':len(cases),'passed':True}),flush=True)
    report={'status':'passed','checkpoint':str(file),'unsharded_projection_shape':shape,'tp8_slices':8,'device_used':0,'cases':24,
        'scope':'Actual frozen checkpoint weights/scales and installed vLLM CompressedTensorsW8A8Int8/Mctlass kernel; synthetic activations. TP8 partitions replayed sequentially on GPU0, not distributed model inference.',
        'results':results}
    with Path('/experiment/evidence/isolated_layer_result.json').open('x') as f:json.dump(report,f,indent=2)
    destroy_model_parallel();destroy_distributed_environment()


if __name__=='__main__':
    from vllm.config import VllmConfig,set_current_vllm_config
    with set_current_vllm_config(VllmConfig()):
        main()
