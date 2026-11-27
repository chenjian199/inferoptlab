"""Collect small status/results from the remote controller, leaving raw requests remote."""
import json
from pathlib import Path
import subprocess

OUT=Path(__file__).resolve().parent
script=r'''
import json,subprocess
from pathlib import Path
r=Path('/home/ubuntu/CJ_workspace/inferoptlab-capacity-20261127/experiments/runs/capacity')
names=['state.json','README.md','effective-points.json','matrix.json','expanded-deployments.json']
files={n:(r/n).read_text() for n in names if (r/n).exists()}
for p in r.rglob('per-rank-capacity.json'):
    files[str(p.relative_to(r))]=p.read_text()
for p in r.rglob('l*-capacity.json'):
    files[str(p.relative_to(r))]=p.read_text()
state=json.loads(files.get('state.json','{}'))
trial=Path(state.get('trial_directory',str(r/'missing')))
if trial.is_relative_to(r) and trial.exists():
    proofs=[]
    for p in sorted(trial.rglob('qualification.json')):
        q=json.loads(p.read_text())
        proofs.append(dict(directory=str(p.parent.relative_to(r)),valid=q['valid'],
            cache_valid=all(x['valid'] for x in q['cache']),
            engine_valid=q['engine']['valid'],attention_valid=q['attention_valid']))
    files['current-proof-summary.json']=json.dumps(proofs,indent=2)
for p in r.glob('*/*/l*-c*/result.json'):
    files[str(p.relative_to(r))]=p.read_text()
p=subprocess.run(['docker','logs','--tail','20','inferoptlab-capacity-20261127'],capture_output=True,text=True)
files['controller-tail.log']=p.stdout+p.stderr
print(json.dumps(files))
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -'],
                 input=script.encode(),capture_output=True,timeout=60)
if p.returncode:raise SystemExit(p.stderr.decode(errors='replace'))
files=json.loads(p.stdout)
for name,text in files.items():
    dest=OUT/'collected'/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(text,encoding='utf-8')
state=json.loads(files.get('state.json','{}'))
print(json.dumps({k:v for k,v in state.items() if k!='deployments'},ensure_ascii=False,indent=2))
print('collected',len(files),'files')
