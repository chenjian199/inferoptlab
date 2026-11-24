import concurrent.futures as cf
import json
from pathlib import Path
import time
import requests
import sys

ROOT=Path(__file__).resolve().parent
if '--details' in sys.argv:
    jobs=[
      ('vLLM-metax','ae1df26a5177d8c3b90f4fc89bf08b3c4949aed8','requirements/maca_private.txt','vllm029-deps.txt'),
      ('vLLM-metax','ae1df26a5177d8c3b90f4fc89bf08b3c4949aed8','vllm_metax/models/__init__.py','vllm029-models.txt'),
      ('vLLM-metax','0962c8735ffe4795800030680311410848512b82','requirements/maca_private.txt','vllm032-deps.txt'),
      ('vLLM-metax','0962c8735ffe4795800030680311410848512b82','vllm_metax/models/__init__.py','vllm032-models.txt'),
      ('sglang','cea8f950303ae0635af66f021d1e9fb48fd06d5b','python/sglang/srt/models/glm5_next.py','sglang0521-glm.txt'),
      ('sglang','cea8f950303ae0635af66f021d1e9fb48fd06d5b','python/pyproject.toml','sglang0521-deps.txt'),
      ('sglang','bcbd6c8d1daf156c916a8fdce202c36fee71cf37','python/sglang/srt/models/glm5_next.py','sglang0522-glm.txt'),
      ('sglang','cea8f950303ae0635af66f021d1e9fb48fd06d5b','python/sglang/srt/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_int8.py','sglang0521-int8.txt'),
      ('sglang','cea8f950303ae0635af66f021d1e9fb48fd06d5b','python/sglang/srt/layers/quantization/compressed_tensors/schemes/compressed_tensors_w8a8_int8_moe.py','sglang0521-int8moe.txt'),
    ]
    def fetch(j):
        repo,rev,path,name=j
        url=f'https://raw.githubusercontent.com/MetaX-MACA/{repo}/{rev}/{path}'
        r=requests.get(url,timeout=45);r.raise_for_status()
        (ROOT/name).write_text(r.text,encoding='utf-8')
        return dict(file=name,url=url,lines=len(r.text.splitlines()))
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for x in pool.map(fetch,jobs):print(json.dumps(x),flush=True)
    raise SystemExit(0)
def get(url, name):
    r=requests.get(url,timeout=45);r.raise_for_status()
    data=r.json()
    (ROOT/name).write_text(json.dumps(data,indent=2),encoding='utf-8')
    return data

def tree(repo,rev,name):
    d=get(f'https://api.github.com/repos/MetaX-MACA/{repo}/git/trees/{rev}?recursive=1',name+'.json')
    matches=[x['path'] for x in d['tree'] if any(k in x['path'].lower() for k in ['glm5','glm_5','glm_next','glmnext','maca','metax'])]
    print(json.dumps({'tree':name,'truncated':d.get('truncated'),'matches':matches[:110]}),flush=True)
    return d

jobs=[('vLLM-metax','ae1df26a5177d8c3b90f4fc89bf08b3c4949aed8','vllm029-tree'),('sglang','cea8f950303ae0635af66f021d1e9fb48fd06d5b','sglang0521-tree'),('sglang','bcbd6c8d1daf156c916a8fdce202c36fee71cf37','sglang0522-tree')]
with cf.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(lambda a:tree(*a),jobs))
d=get('https://api.github.com/repos/MetaX-MACA/vLLM-metax/compare/v0.28.0...v0.29.0','vllm028-029-compare.json')
print('COMPARE',d.get('status'),d.get('ahead_by'),[(x['sha'][:10],x['commit']['message'].splitlines()[0]) for x in d.get('commits',[])],flush=True)
url='https://modelscope.cn/api/v1/models/metax-tech/GLM-5.3-Flash-W8A8/repo'
start=time.monotonic(); n=0
try:
    with requests.get(url,params={'Revision':'6df7a9b0309e530094e29b2a6ced3e21bed6c16d','FilePath':'model-language_model-layers-00021.safetensors'},headers={'Range':'bytes=0-16777215'},stream=True,timeout=(20,30)) as r:
        r.raise_for_status()
        for b in r.iter_content(1024*1024):
            n+=len(b)
            if n>=16777216:break
        print('LOCAL_RANGE_SPEED',n,time.monotonic()-start,n/(time.monotonic()-start)/1e6,flush=True)
except Exception as exc:print('LOCAL_RANGE_ERROR',type(exc).__name__,flush=True)
