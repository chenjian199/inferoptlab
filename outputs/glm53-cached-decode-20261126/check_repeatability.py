"""Separate cold-run variation from cached-state restoration differences."""
import json
from pathlib import Path
import time
import urllib.request

OUT=Path('/workspace/experiments/evidence/glm53-cached-decode-20261126/repeatability')
OUT.mkdir(parents=True,exist_ok=True)
BASE=OUT.parent/'proof-tp8'
def call(path,payload):
    req=urllib.request.Request('http://127.0.0.1:18082'+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=600) as r:return json.load(r)
rows=[]
for length in [4096,16384]:
    context=json.loads((BASE/f'{length}-context.json').read_text())['token_ids']
    seed=json.loads((BASE/f'{length}-cold.json').read_text())['response']['choices'][0]['token_ids'][0]
    for rep in range(3):
        assert call('/reset_prefix_cache',{})['success']
        for mode in ['cold','cached']:
            payload=dict(model='glm53-flash',prompt=context+[seed],max_tokens=20,min_tokens=20,ignore_eos=True,
                temperature=0,return_token_ids=True,logprobs=5,request_id=f'control-{length}-{rep}-{mode}')
            r=call('/v1/completions',payload)
            (OUT/f'{length}-{rep}-{mode}.json').write_text(json.dumps(r,ensure_ascii=False))
            choice=r['choices'][0]
            rows.append(dict(length=length,rep=rep,mode=mode,usage=r['usage'],tokens=choice['token_ids'],text=choice['text']))
            (OUT/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
            print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
