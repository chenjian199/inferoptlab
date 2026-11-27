import json
from pathlib import Path
import shlex
import subprocess
import argparse

parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='r3');parser.add_argument('--compact',action='store_true');args=parser.parse_args()
assert args.attempt.isalnum()

OUT=Path(__file__).resolve().parent
code=r'''
import collections,json,pathlib,subprocess
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
out=root/('experiments/runs/glm53-cached-decode-20261126-'+ATTEMPT)
state=json.loads((out/'state.json').read_text()) if (out/'state.json').exists() else {}
result={'state':state}
if state.get('deployment'):
 dep=out/state['deployment']
 prefix='routes-' if state.get('status')=='qualifying_routes' else (state.get('group','')+'-')
 candidates=sorted(dep.glob(prefix+'*'),key=lambda p:p.name.rsplit('-',1)[-1]) if prefix!='-' else []
 if candidates:
  group=candidates[-1]
  result['group_progress']={'folder':group.name,'slots_filled':len(list(group.glob('fill-*.json'))),
   'residency_audited':len(list(group.glob('residency-*.json'))),'decode_qualified':(group/'qualification.json').exists()}
client=subprocess.run(['docker','inspect','inferoptlab-cached-decode-scan-20261126-'+ATTEMPT],capture_output=True,text=True)
result['controller']=json.loads(client.stdout)[0]['State'] if client.returncode==0 else client.stderr
logs=subprocess.run(['docker','logs','--tail','12','inferoptlab-cached-decode-scan-20261126-'+ATTEMPT],capture_output=True,text=True)
result['controller_log']=logs.stdout+logs.stderr
if state.get('server_attempt'):
 launch=pathlib.Path(state['server_attempt'])/'launch.json'
 if launch.exists():
  cid=json.loads(launch.read_text())['container_id']
  logs=subprocess.run(['docker','logs',cid],capture_output=True,text=True)
  if logs.returncode and (launch.parent/'server.log').exists():logs.stdout=(launch.parent/'server.log').read_text()
  lines=(logs.stdout+logs.stderr).splitlines()
  result['server_log']='\n'.join(lines[-10:])
  selected=set()
  for i,line in enumerate(lines):
   if any(s in line for s in ['Error:','AssertionError','Exception:']):selected.update(range(max(0,i-4),min(len(lines),i+4)))
  result['server_errors']='\n'.join(lines[i] for i in sorted(selected))[-14000:]
print(json.dumps(result))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60','python3 -c '+shlex.quote('ATTEMPT='+repr(args.attempt)+'\n'+code)],capture_output=True,timeout=35)
if r.returncode:raise SystemExit(r.stderr.decode(errors='replace'))
data=json.loads(r.stdout);(OUT/'scan-status.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
state=data['state'];points=state.pop('points',[])
from collections import Counter
if args.compact:
 print(json.dumps(dict(status=state.get('status'),deployment=state.get('deployment'),
  group=state.get('group'),point=state.get('point'),updated_at=state.get('updated_at'),
  counts=dict(Counter(p['status'] for p in points)),controller_running=data['controller'].get('Running'),
  group_progress=data.get('group_progress'),
  error=state.get('error'),server_errors=data.get('server_errors')),ensure_ascii=False))
else:
 print(json.dumps(dict(**data,counts=dict(Counter(p['status'] for p in points)),last_points=points[-3:]),ensure_ascii=False,indent=2))
