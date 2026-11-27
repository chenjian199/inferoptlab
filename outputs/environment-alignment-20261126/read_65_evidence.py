import json,hashlib
from pathlib import Path
paths=['/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/README.md', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795680151385883427/server-info.json', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795680151385883427/launch.json', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/4k/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/routes-1795680156847139122/qualification.json', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/README.md', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795679721046534175/server-info.json', '/home/ubuntu/DCC_workspace/inferoptlab/experiments/evidence/glm53-tp4-dp2-ep1-graph-cacheddecode-latest-20261126/full/glm53-vllm-cached-decode-tp4-dp2-ep1-graph/server-1795679721046534175/launch.json']
out=[]
for name in paths:
 p=Path(name)
 if p.is_file():
  b=p.read_bytes();out.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),text=b.decode('utf-8',errors='replace')))
print(json.dumps(out))
