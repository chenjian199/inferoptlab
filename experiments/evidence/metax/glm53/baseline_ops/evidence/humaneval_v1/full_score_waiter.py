import json,time,subprocess,hashlib
from pathlib import Path
root=Path('/home/metax/glm53-baseline-ops')
deadline=time.monotonic()+7200
while True:
 p=json.loads((root/'evidence/generation_process.json').read_text())
 if p['status']=='failed':raise RuntimeError('generation failed')
 if p['status']=='complete':
  assert p['exit_code']==0
  break
 if time.monotonic()>deadline:raise TimeoutError('generation deadline')
 time.sleep(3)
run=root/'runs/20261123_humaneval_v1_full164'
m=json.loads((run/'generation_manifest.json').read_text())
assert m['status']=='complete' and m['completed_tasks']==m['expected_tasks']==164
frozen=json.loads((root/'configs/protocol-v1.frozen.json').read_text())
for name in ['evaluate_humaneval.py','code_adapter.py']:
 assert hashlib.sha256((root/'harness'/name).read_bytes()).hexdigest()==frozen['harness_sha256'][name]
cmd=['python3','-u',str(root/'harness/evaluate_humaneval.py'),'--run',str(run)]
status={'command':cmd,'status':'running','started_epoch':time.time()}
record=root/'evidence/full_score_process.json'
with (root/'evidence/full_score.log').open('x') as log:
 p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
 status['pid']=p.pid;record.write_text(json.dumps(status,indent=2))
 code=p.wait()
status.update(status='complete' if code==0 else 'failed',exit_code=code,elapsed_seconds=time.time()-status['started_epoch'])
record.write_text(json.dumps(status,indent=2))
