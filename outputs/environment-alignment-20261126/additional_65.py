import json,hashlib
from pathlib import Path
paths=['/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/state.json', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/state.json', '/home/ubuntu/DCC_workspace/inferoptlab/benchmark/load/cached_decode.py', '/home/ubuntu/DCC_workspace/inferoptlab/benchmark/load/aiperf_hooks/sitecustomize.py', '/home/ubuntu/DCC_workspace/inferoptlab/tools/deployment/metax-vllm/observers/sitecustomize.py']
roots=['/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-20261126/client/venv/lib/python3.12/site-packages']
for root in roots:
 for pattern in ['aiperf-*.dist-info/METADATA','transformers-*.dist-info/METADATA']:
  paths += [str(p) for p in Path(root).glob(pattern)]
out=[]
for name in paths:
 p=Path(name)
 if p.is_file():
  b=p.read_bytes();out.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),text=b.decode('utf-8',errors='replace')))
print(json.dumps(out))
