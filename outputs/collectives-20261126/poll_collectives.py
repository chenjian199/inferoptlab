"""Read-only campaign snapshot and integrity-checked evidence download."""
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

OUT=Path(__file__).resolve().parent
code='''
import base64,hashlib,json,pathlib,subprocess
p=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/evidence/glm53-collectives-20261126')
s=json.loads((p/'bandwidth-state.json').read_text())
proc=pathlib.Path('/proc')/str(s['pid'])/'cmdline'
live=proc.exists() and b'run_remote.py' in proc.read_bytes()
files={}
for f in p.iterdir():
 if f.suffix in ['.json','.jsonl','.log','.txt','.py']:
  b=f.read_bytes();files[f.name]={'data':base64.b64encode(b).decode(),'sha256':hashlib.sha256(b).hexdigest()}
print(json.dumps({'state':s,'live':live,'files':files,'containers':subprocess.run(['docker','ps','--format','{{.Names}} {{.Status}}'],capture_output=True,text=True).stdout}))
'''
for attempt in range(4):
 try:
  r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60','python3 -c '+shlex.quote(code)],capture_output=True,timeout=45)
  if r.returncode:continue
  result=json.loads(r.stdout);break
 except (subprocess.TimeoutExpired,json.JSONDecodeError):continue
else:raise SystemExit('OBSERVATION_UNAVAILABLE; no remote mutation')
dest=OUT/'raw';dest.mkdir(exist_ok=True)
for name,item in result['files'].items():
 assert Path(name).name==name
 b=base64.b64decode(item['data']);assert hashlib.sha256(b).hexdigest()==item['sha256']
 (dest/name).write_bytes(b)
(OUT/'last-poll.json').write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2),encoding='utf-8')
s=result['state'];print(json.dumps(dict(status=s['status'],live=result['live'],current=s.get('current'),counts=dict(Counter(j['status'] for j in s['jobs'])),containers=result['containers'],failures=[j['id'] for j in s['jobs'] if j['status'] in ['failed','timed_out']],error=s.get('error'))))
