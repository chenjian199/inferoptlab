"""Read cache and routing implementation from the exact serving image."""
import json
from pathlib import Path
import shlex
import subprocess

OUT=Path(__file__).resolve().parent
IMAGE='sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b'
code='''
import json,pathlib
files={}
for root in [pathlib.Path('/opt/src/vllm'),pathlib.Path('/opt/src/vllm-metax')]:
 for p in root.rglob('*.py'):
  s=str(p)
  if '/build/' in s:continue
  if any(k in s for k in ['kv_cache_manager.py','kv_cache_utils.py','single_type_kv_cache_manager.py','hybrid_kv_cache_coordinator.py','config/cache.py','core/sched/scheduler.py','engine/core_client.py','entrypoints/openai/completion','entrypoints/openai/chat_completion','entrypoints/openai/engine/protocol.py','v1/attention/backends/','v1/worker/gpu/model_runner.py']):
   files[str(p.relative_to('/opt/src'))]=p.read_text()
print(json.dumps(files))
'''
cmd=['docker','run','--rm','--network=none','--entrypoint','python3',IMAGE,'-c',code]
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60',shlex.join(cmd)],capture_output=True,timeout=100)
if r.returncode:raise SystemExit(r.stderr.decode(errors='replace'))
files=json.loads(r.stdout)
for name,content in files.items():
 p=OUT/'source'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
print(json.dumps(dict(files=len(files),bytes=len(r.stdout))))
