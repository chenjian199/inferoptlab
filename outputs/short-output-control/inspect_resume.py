"""Read compact progress and synchronize the explicit skip receipt."""
import json
from pathlib import Path
import shlex
import subprocess

code = r'''
import pathlib,json,subprocess
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
name='glm53-short-output-continue-failures-20261125'
session=r/'experiments/evidence'/name
s=json.loads((session/'state.json').read_text())
b=pathlib.Path(s['batch']);v=json.loads((b/'batch.json').read_text())
result=dict(state={k:s.get(k) for k in ['status','pid','updated_at','error','attempts']},
 current=v.get('current_trial'),preparing_fixture=v.get('preparing_fixture'))
log=session/('attempt-%03d'%len(s['attempts']))/'runner.log'
result['runner_tail']=subprocess.run(['tail','-c','2500',str(log)],capture_output=True,text=True).stdout
if v.get('current_trial'):
 run=b/v['current_trial']['directory']
 for f in ['logs/server.log','logs/warmup.log','logs/aiperf.log']:
  if (run/f).exists():result[f]=subprocess.run(['tail','-c','1800',str(run/f)],capture_output=True,text=True).stdout
result['documents']={name+'.launch.json':json.loads((r/'experiments/evidence'/(name+'.launch.json')).read_text()),
 'exclusions.json':json.loads((b/'exclusions.json').read_text())}
print(json.dumps(result))
'''
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(4):
    try:
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],
                         capture_output=True,text=True,encoding='utf-8',timeout=40)
        if p.returncode:
            print('SSH retry',attempt,p.stderr,flush=True);continue
        value=json.loads(p.stdout)
        out=Path('experiments/evidence/glm53-short-output-continue-failures-20261125')
        out.mkdir(exist_ok=True)
        for name,doc in value.pop('documents').items():
            (out/name).write_text(json.dumps(doc,indent=2),encoding='utf-8')
        (out/'last-observation.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
        print(json.dumps(value),flush=True);break
    except subprocess.TimeoutExpired:
        print('Observation timeout; no remote restart',flush=True)
