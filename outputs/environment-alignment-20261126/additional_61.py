import json,hashlib
from pathlib import Path
paths=['/home/ubuntu/LYQ_workspace/inferoptlab/benchmark/load/cached_decode.py', '/home/ubuntu/LYQ_workspace/inferoptlab/benchmark/load/aiperf_hooks/sitecustomize.py', '/home/ubuntu/LYQ_workspace/inferoptlab/tools/deployment/metax-vllm/observers/sitecustomize.py']
roots=[]
for root in roots:
 for pattern in ['aiperf-*.dist-info/METADATA','transformers-*.dist-info/METADATA']:
  paths += [str(p) for p in Path(root).glob(pattern)]
out=[]
for name in paths:
 p=Path(name)
 if p.is_file():
  b=p.read_bytes();out.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),text=b.decode('utf-8',errors='replace')))
print(json.dumps(out))
