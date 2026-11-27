import json,subprocess
from pathlib import Path
root=Path('/home/ubuntu/CJ_workspace/inferoptlab-profiler-20261126')
run=root/'experiments/runs/glm53-tp2-dp4-ep8-profiler-r1'
state=json.loads((run/'state.json').read_text()) if (run/'state.json').exists() else {}
print(json.dumps({k:v for k,v in state.items() if k!='points'}))
for p in state.get('points',[]):print(json.dumps(dict(scenario=p['scenario'],status=p['status'],traces=p.get('traces'))))
launch=run/'server/launch.json'
if launch.exists():
 cid=json.loads(launch.read_text())['container_id']
 p=subprocess.run(['docker','logs','--tail','12',cid],capture_output=True,text=True)
 print(p.stdout+p.stderr)
for p in sorted(run.glob('l*/qualification.json')):
 q=json.loads(p.read_text());print('qualification',p.parent.name,q['valid'])
print('traces',len(list((run/'server/observations/profiles').glob('*.gz'))))
