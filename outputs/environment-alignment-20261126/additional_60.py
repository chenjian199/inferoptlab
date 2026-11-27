import json,hashlib
from pathlib import Path
paths=['/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/benchmark/load/cached_decode.py', '/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/benchmark/load/aiperf_hooks/sitecustomize.py', '/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/tools/deployment/metax-vllm/observers/sitecustomize.py']
roots=['/home/ubuntu/CJ_workspace/inferoptlab-client-20261124/venv/lib/python3.12/site-packages']
for root in roots:
 for pattern in ['aiperf-*.dist-info/METADATA','transformers-*.dist-info/METADATA']:
  paths += [str(p) for p in Path(root).glob(pattern)]
paths += ['/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/snapshot.json', '/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/server-1795668837263403759/server-info.json', '/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/runs/glm53-cached-decode-20261126-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/server-1795668837263403759/launch.json']
out=[]
for name in paths:
 p=Path(name)
 if p.is_file():
  b=p.read_bytes();out.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),text=b.decode('utf-8',errors='replace')))
print(json.dumps(out))
