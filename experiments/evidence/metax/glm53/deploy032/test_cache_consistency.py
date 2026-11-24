"""Check cached next-token distributions against fresh full-prefill distributions."""
import json,os,time
from pathlib import Path
os.environ.setdefault('USE_PRECOMPILED_KERNEL','1')
os.environ.setdefault('HF_HUB_OFFLINE','1')
os.environ.setdefault('TRANSFORMERS_OFFLINE','1')
def main():
    from transformers import AutoTokenizer
    from vllm import LLM,SamplingParams
    model='/models/GLM-5.3-Flash-W8A8'
    tok=AutoTokenizer.from_pretrained(model,local_files_only=True)
    prompt=tok.encode(tok.apply_chat_template([{'role':'user','content':'请用中文简短介绍你自己。'}],tokenize=False,add_generation_prompt=True,reasoning_effort='low'),add_special_tokens=False)
    assert isinstance(prompt,list) and all(isinstance(x,int) for x in prompt)
    settings=dict(model=model,tensor_parallel_size=8,distributed_executor_backend='mp',dtype='bfloat16',quantization='compressed-tensors',load_format='safetensors',max_model_len=4096,max_num_seqs=1,max_num_batched_tokens=4096,gpu_memory_utilization=.9,enforce_eager=True,enable_prefix_caching=False,async_scheduling=False,attention_config={'indexer_kv_dtype':'auto'},limit_mm_per_prompt={'image':0,'video':0},trust_remote_code=False,worker_extension_cls='worker_provenance.Provenance')
    llm=LLM(**settings)
    print(llm.collective_rpc('start_layer_trace',args=('cached',)),flush=True)
    pair=llm.generate([{'prompt_token_ids':prompt}],SamplingParams(temperature=0,max_tokens=2),use_tqdm=False)[0].outputs[0]
    print(llm.collective_rpc('stop_layer_trace'),flush=True)
    print(llm.collective_rpc('start_layer_trace',args=('prefill',)),flush=True)
    llm.generate([{'prompt_token_ids':prompt+[int(pair.token_ids[0])]}],SamplingParams(temperature=0,max_tokens=1),use_tqdm=False)
    print(llm.collective_rpc('stop_layer_trace'),flush=True)
    import torch
    cached=torch.load('/work/evidence/layer_trace_cached.pt',weights_only=True)
    fresh=torch.load('/work/evidence/layer_trace_prefill.pt',weights_only=True)
    differences=[]
    for name,entries in cached.items():
        if len(entries)<2 or name not in fresh:continue
        row=dict(module=name,cached_shapes=[v['shape'] for v in entries[-1]],fresh_shapes=[v['shape'] for v in fresh[name][-1]],errors=[])
        for c,f in zip(entries[-1],fresh[name][-1],strict=True):
            x,y=c['last'],f['last']
            if not x.numel():
                row['errors'].append(dict(relative_l2=0.0,max_abs=0.0,empty=True))
                continue
            row['errors'].append(dict(relative_l2=float((x-y).norm()/y.norm().clamp_min(1e-8)),max_abs=float((x-y).abs().max())))
        differences.append(row)
    Path('/work/evidence/layer_trace_comparison.json').write_text(json.dumps(differences,indent=2))
    print('LAYER_DIFFERENCES',json.dumps(differences[:12]),flush=True)
    if os.environ.get('GLM53_TRACE_ONLY') == '1':
        print('TRACE_COMPLETE',flush=True)
        return
    out=llm.generate([{'prompt_token_ids':prompt}],SamplingParams(temperature=0,max_tokens=32,logprobs=10),use_tqdm=False)[0].outputs[0]
    print('CACHED',out.text,flush=True)
    comparisons=[]
    for step in [0,1,2,4,8,16,31]:
        if step>=len(out.token_ids):continue
        fresh=llm.generate([{'prompt_token_ids':prompt+list(out.token_ids[:step])}],SamplingParams(temperature=0,max_tokens=1,logprobs=10),use_tqdm=False)[0].outputs[0]
        cached_lp={int(k):v.logprob for k,v in out.logprobs[step].items()}
        fresh_lp={int(k):v.logprob for k,v in fresh.logprobs[0].items()}
        overlap=sorted(set(cached_lp)&set(fresh_lp))
        item=dict(step=step,cached_token=int(out.token_ids[step]),fresh_token=int(fresh.token_ids[0]),cached_text=tok.decode([out.token_ids[step]]),fresh_text=fresh.text,max_common_logprob_delta=max([abs(cached_lp[k]-fresh_lp[k]) for k in overlap],default=None),cached_logprobs=cached_lp,fresh_logprobs=fresh_lp)
        comparisons.append(item);print(json.dumps(item,ensure_ascii=False),flush=True)
    report=dict(settings=settings,runner=os.environ.get('VLLM_USE_V2_MODEL_RUNNER'),cached_text=out.text,cached_token_ids=list(out.token_ids),comparisons=comparisons)
    Path('/work/evidence/cache_consistency.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

