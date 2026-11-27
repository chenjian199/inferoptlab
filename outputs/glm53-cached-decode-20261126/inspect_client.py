import json
from pathlib import Path
import shlex
import subprocess

code='''
import json,pathlib
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-client-20261124/venv/lib/python3.12/site-packages/aiperf')
selected={}
for p in root.rglob('*.py'):
 t=p.read_text()
 if any(s in t for s in ['raw_payload','request_headers','extra_headers','input_type']):selected[str(p.relative_to(root))]=t
print(json.dumps(selected))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -c '+shlex.quote(code)],capture_output=True,check=True,timeout=30)
out=Path(__file__).resolve().parent/'source/aiperf'
files=json.loads(r.stdout)
for n,t in files.items():
 p=out/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,encoding='utf-8')
print(len(files))
