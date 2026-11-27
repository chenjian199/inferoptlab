"""Run inside the owned qualification container; preserve every API response."""
import json
from pathlib import Path
import random
import sys
import time
import urllib.request

sys.path.insert(0, '/workspace')
from benchmark.load.dataset import load_tokenizer, prompt

OUT=Path('/workspace/experiments/evidence/glm53-cached-decode-20261126/proof-tp8')
OUT.mkdir(parents=True,exist_ok=True)
URL='http://127.0.0.1:18082'

def call(path, payload=None, timeout=600):
    request=urllib.request.Request(URL+path, data=None if payload is None else json.dumps(payload).encode(),
        headers={'Content-Type':'application/json','X-data-parallel-rank':'0'})
    with urllib.request.urlopen(request,timeout=timeout) as r:
        body=r.read()
        return json.loads(body) if body else None

def save(name, data):
    (OUT/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))

def run():
    for _ in range(120):
        try: call('/health',timeout=3);break
        except Exception:time.sleep(10)
    else:raise RuntimeError('server did not become healthy')
    save('server-info',call('/server_info'))
    model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
    tokenizer=load_tokenizer(model)
    results=[]
    for length in [4096,16384,65536]:
        text=prompt(tokenizer,random.Random(20261125),length)
        ids=tokenizer.apply_chat_template([dict(role='user',content=text)],tokenize=True,add_generation_prompt=True,return_dict=True)['input_ids']
        assert len(ids)==length
        save(str(length)+'-context',dict(token_ids=ids))
        reset=call('/reset_prefix_cache',{})
        assert reset['success'] is True,reset
        def request(tag, tokens, n):
            payload=dict(model='glm53-flash',prompt=tokens,max_tokens=n,min_tokens=n,
                ignore_eos=True,temperature=0,return_token_ids=True,request_id='cacheproof-'+tag)
            start=time.perf_counter();r=call('/v1/completions',payload)
            save(tag,dict(elapsed_s=time.perf_counter()-start,response=r))
            return r
        cold=request(str(length)+'-cold',ids,21)
        seed=cold['choices'][0]['token_ids'][0]
        request(str(length)+'-fill-boundary',ids+[seed],1)
        for repeat in range(3):
            r=request(str(length)+f'-replay-{repeat}',ids+[seed],20)
            usage=r['usage'];cache=usage.get('prompt_tokens_details',{}).get('cached_tokens')
            passed=cache==length and usage['prompt_tokens']==length+1 and usage['completion_tokens']==20
            equal=r['choices'][0]['token_ids']==cold['choices'][0]['token_ids'][1:]
            results.append(dict(context_tokens=length,seed_token=seed,replay=repeat,usage=usage,
                full_original_context_hit=passed,continuation_equals_cold=equal))
            save('results',results);print(json.dumps(results[-1]),flush=True)
            assert passed,'original context not fully cached'
    save('status',dict(status='cache_counts_passed',numerical_equivalence=all(r['continuation_equals_cold'] for r in results),results=results))

if __name__=='__main__':
    try:run()
    except Exception as exc:
        save('status',dict(status='failed',error=repr(exc)));raise
