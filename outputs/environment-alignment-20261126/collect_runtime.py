from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parent
probe=(root/'probe_runtime.py').read_text()
def collect(host):
    inv=json.loads((root/f'{host}-inventory.json').read_text(encoding='utf-8'))
    candidates=[c for c in inv['containers'] if c['state']['Running']]
    plan=[dict(id=c['id'],name=c['name'],python=(c['entrypoint'][0] if c['entrypoint'] and 'python' in c['entrypoint'][0]
                                              else ('/work/venv/bin/python' if 'cached64' in c['name'] else 'python3'))) for c in candidates]
    remote='''
import json,subprocess
results=[]
for c in PLAN:
 try:
  p=subprocess.run(['docker','exec','-i',c['id'],c['python'],'-'],input=PROBE,text=True,capture_output=True,timeout=75)
  if p.returncode:results.append(dict(container=c,code=p.returncode,error=p.stderr));continue
  results.append(dict(container=c,data=json.loads(p.stdout)))
 except Exception as e:results.append(dict(container=c,error=repr(e)))
print(json.dumps(results))
'''
    code='PLAN='+repr(plan)+'\nPROBE='+repr(probe)+'\n'+remote
    p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2',
                      'metax-'+host,'python3 -'],input=code.encode(),capture_output=True,timeout=240)
    if p.returncode:return dict(host=host,error=p.stderr.decode(errors='replace'))
    d=json.loads(p.stdout);(root/f'{host}-runtime.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    return dict(host=host,results=[dict(container=r['container']['name'],error=r.get('error'),
                 packages=[(p['name'],p['version']) for p in r.get('data',{}).get('packages',[])]) for r in d])
with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(collect,['60','61','64','65']):print(json.dumps(result),flush=True)
