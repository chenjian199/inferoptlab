import json,hashlib
from pathlib import Path
paths=['/data/c500-operator-reproduction-20261125/inferoptlab-local64-latest-20261126/project/benchmark/load/cached_decode.py', '/data/c500-operator-reproduction-20261125/inferoptlab-local64-latest-20261126/project/benchmark/load/aiperf_hooks/sitecustomize.py', '/data/c500-operator-reproduction-20261125/inferoptlab-local64-latest-20261126/project/tools/deployment/metax-vllm/observers/sitecustomize.py']
roots=['/data/c500-operator-reproduction-20261125/inferoptlab-tools-check-20261125/venv/lib/python3.12/site-packages']
for root in roots:
 for pattern in ['aiperf-*.dist-info/METADATA','transformers-*.dist-info/METADATA']:
  paths += [str(p) for p in Path(root).glob(pattern)]
out=[]
for name in paths:
 p=Path(name)
 if p.is_file():
  b=p.read_bytes();out.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),text=b.decode('utf-8',errors='replace')))
print(json.dumps(out))
