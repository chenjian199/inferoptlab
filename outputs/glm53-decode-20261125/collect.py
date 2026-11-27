import base64
import gzip
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
REMOTE = r'''
import pathlib,json,datetime,sys,hashlib,gzip,base64
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
sys.path[:0]=[str(r/'.host-deps'),str(r)]
import yaml
result=dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),host='metax-60',root=str(r),batches=[])
for name in ['batch-20261125T070618Z-42e96aad','batch-20261125T060155Z-3fd3a8a0']:
 p=r/'experiments/runs/benchmark'/name
 state=json.loads((p/'batch.json').read_text())
 batch=dict(name=name,state=state,snapshot=yaml.safe_load((p/'resolved.yaml').read_text()),runs=[])
 for entry in state['runs']:
  if not entry.get('directory'): continue
  q=p/entry['directory']; item=dict(entry=entry,path=str(q),files={},hashes={})
  for n in ['run.json','resolved.yaml','summary.json','decode.json','sla.json','requests.jsonl','environment.json','commands.json','raw/aiperf/profile_export_aiperf.json']:
   f=q/n
   if f.exists():
    data=f.read_bytes();item['files'][n]=data.decode();item['hashes'][n]=hashlib.sha256(data).hexdigest()
  raw=q/'raw/aiperf/profile_export.jsonl'
  if raw.exists():item['native_raw_sha256']=hashlib.sha256(raw.read_bytes()).hexdigest()
  for n in ['logs/aiperf.log','logs/warmup.log','logs/server.log']:
   f=q/n
   if f.exists(): item['files'][n]=f.read_text(errors='replace')[-16000:]
  batch['runs'].append(item)
 result['batches'].append(batch)
controller=r/'experiments/evidence/glm53-decode-preflight/20261125/direct-performance-fourfold/state.json'
result['controller']=json.loads(controller.read_text())
print(base64.b64encode(gzip.compress(json.dumps(result,ensure_ascii=False).encode())).decode())
'''
for attempt in range(3):
    response = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
                               '-o', 'ConnectionAttempts=2', 'metax-60', 'python3 -'],
                              input=REMOTE, text=True, capture_output=True, timeout=75)
    if response.returncode == 0:
        break
    print(response.stderr.strip())
response.check_returncode()
data = json.loads(gzip.decompress(base64.b64decode(response.stdout)))
(OUT / 'source-snapshot.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('Captured', data['captured_at'])
for batch in data['batches']:
    print(batch['name'], batch['state']['status'])
    for run in batch['runs']:
        d = json.loads(run['files']['run.json'])
        print(run['entry']['concurrency'], d['status'], d.get('error'))
        if d['status'] == 'failed':
            print(run['files'].get('logs/warmup.log', '')[-2500:])
print('Controller:', data['controller'])
