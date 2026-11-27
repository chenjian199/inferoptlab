"""Read the pinned image source without loading a model or using GPUs."""
import json
from pathlib import Path
import shlex
import subprocess

OUT=Path(__file__).resolve().parent
IMAGE='sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b'
code='''
import json
from pathlib import Path
roots=[Path('/opt/src/vllm'),Path('/opt/src/vllm-metax')]
files={}
for root in roots:
 for p in root.rglob('*.py'):
  s=str(p)
  if '/build/' not in s and any(x in s for x in ['fused_moe/all2all_utils.py','ops/sequence_parallel.py','fused_moe/router/grouped_topk_router.py']):
   files[str(p.relative_to('/opt/src'))]=p.read_text()
print(json.dumps(files))
'''
cmd=['docker','run','--rm','--network=none','--entrypoint','/opt/vllm-env/bin/python',IMAGE,'-c',code]
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60',shlex.join(cmd)],capture_output=True,timeout=90)
if r.returncode:raise SystemExit(r.stderr.decode(errors='replace'))
files=json.loads(r.stdout)
for name,content in files.items():
 p=OUT/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
(OUT/'dispatch-source.json').write_bytes(r.stdout)
print(json.dumps({'files':list(files),'bytes':len(r.stdout)}))
