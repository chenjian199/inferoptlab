"""Inspect packages and source fingerprints without importing torch/vLLM."""
import hashlib
import importlib.metadata as md
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

def run(argv,timeout=20):
    try:
        p=subprocess.run(argv,capture_output=True,text=True,errors='replace',timeout=timeout)
        return dict(code=p.returncode,stdout=p.stdout[:100000],stderr=p.stderr[:3000])
    except Exception as e:return dict(error=repr(e))

out=dict(python=sys.version,executable=sys.executable,packages=[],sources=[],processes=[])
for dist in md.distributions():
    name=dist.metadata.get('Name','')
    if any(x in name.lower() for x in ['vllm','torch','triton','aiperf','transformers','sglang','flash','maca','metax','compressed','mccl']):
        row=dict(name=name,version=dist.version,location=str(dist.locate_file('')))
        url=dist.read_text('direct_url.json')
        if url:row['direct_url']=json.loads(url)
        out['packages'].append(row)
for module in ['vllm','vllm_metax','torch','aiperf','triton']:
    try:
        spec=importlib.util.find_spec(module)
        if not spec or not spec.origin:continue
        p=Path(spec.origin).parent
        row=dict(module=module,path=str(p),files={})
        if module in ['vllm','vllm_metax']:
            row['git_head']=run(['git','-C',str(p.parent),'rev-parse','HEAD'])
            row['git_status']=run(['git','-C',str(p.parent),'status','--short','--untracked-files=no'])
            selected=['__init__.py','version.py','v1/core/sched/scheduler.py','v1/worker/gpu_model_runner.py',
                      'v1/attention/backends/mla/flashmla_sparse.py','model_executor/models/glm5_next.py',
                      'v1/worker/gpu/model_runner.py','model_executor/layers/attention/mla_attention.py']
            for rel in selected:
                f=p/rel
                if f.is_file():row['files'][rel]=dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())
        if module=='torch' and (p/'version.py').is_file():row['version_file']=(p/'version.py').read_text()
        out['sources'].append(row)
    except Exception as e:out['sources'].append(dict(module=module,error=repr(e)))
out['maca_packages']=run(['dpkg-query','-W','-f=${Package}\t${Version}\n','maca*'])
out['version_files']={}
for name in ['/opt/maca/version','/opt/maca/version.txt','/opt/maca/include/maca_version.h','/opt/maca/include/mccl.h']:
    p=Path(name)
    if p.is_file():out['version_files'][name]=p.read_text(errors='replace')[:10000]
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():continue
    try:
        args=(proc/'cmdline').read_bytes().decode(errors='replace').split('\0')
        if not any('vllm' in x or 'aiperf' in x or 'cached_decode' in x for x in args):continue
        if args and args[-1]=='':args.pop()
        env=(proc/'environ').read_bytes().decode(errors='replace').split('\0')
        safe={k:v for s in env for k,_,v in [s.partition('=')] if k.startswith(('VLLM_','MACA_','MCCL_','NCCL_','OMP_','INFEROPTLAB_'))
              and not re.search('TOKEN|KEY|SECRET|PASSWORD',k)}
        out['processes'].append(dict(pid=int(proc.name),args=args,env=safe))
    except (OSError,PermissionError):pass
print(json.dumps(out))
