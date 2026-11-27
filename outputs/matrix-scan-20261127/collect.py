"""Download only matrix status, capacities and summary tables."""
import json
from pathlib import Path
import subprocess

script=r'''
import json,subprocess
from pathlib import Path
root=Path('/home/ubuntu/CJ_workspace/inferoptlab-matrix-20261127')
r=root/'experiments/runs/glm53-matrix'
files={}
for name in ['state.json','README.md','summary.csv','matrix.yaml','expanded-deployments.json','environment.json']:
 if (r/name).exists():files[name]=(r/name).read_text(encoding='utf-8')
for p in r.glob('*/capacity-l*.json'):files[str(p.relative_to(r))]=p.read_text()
if (root/'host-inventory.json').exists():files['host-inventory.json']=(root/'host-inventory.json').read_text()
p=subprocess.run(['docker','logs','--tail','15','inferoptlab-matrix-20261127'],capture_output=True,text=True)
files['controller-tail.log']=p.stdout+p.stderr
print(json.dumps(files))
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -'],input=script.encode(),capture_output=True,timeout=60)
if p.returncode:raise SystemExit(p.stderr.decode(errors='replace'))
files=json.loads(p.stdout);out=Path(__file__).resolve().parent/'collected'
for name,content in files.items():
 dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content,encoding='utf-8')
state=json.loads(files.get('state.json','{}'))
print(json.dumps({k:v for k,v in state.items() if k not in ('deployments','points')},ensure_ascii=False,indent=2))
print('Completed:',sum(p['status']=='completed' for p in state.get('points',[])))
