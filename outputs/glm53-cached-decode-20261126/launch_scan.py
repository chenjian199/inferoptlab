"""Launch the durable new scan on metax-60; the old scan remains stopped."""
import json
from pathlib import Path
import shlex
import subprocess
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('--attempt',default='r2')
args=parser.parse_args()
assert args.attempt.isalnum()

code='''
import json,os,pathlib,subprocess
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
evidence=root/'experiments/evidence/glm53-cached-decode-20261126'
receipt=evidence/('scan-launch-'+ATTEMPT+'.json')
if receipt.exists():print(receipt.read_text());raise SystemExit()
proof=json.loads((evidence/'observed-proof-4k-c2-1795667946786800114/status.json').read_text())
assert proof['status']=='passed'
old=json.loads((evidence/'observed-launch.json').read_text())
info=json.loads(subprocess.check_output(['docker','inspect',old['id']]))[0]
assert info['Config']['Labels']['io.inferoptlab.role']=='cached-decode-preflight'
logs=subprocess.run(['docker','logs',old['id']],capture_output=True)
(evidence/'observed-server.log').write_bytes(logs.stdout+logs.stderr)
subprocess.run(['docker','stop','--time','20',old['id']],check=True,stdout=subprocess.DEVNULL)
assert not (root/'experiments/runs/benchmark/.execution.lock').exists()
client=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-client-20261124')
model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
cache='/home/ubuntu/CJ_workspace/inferoptlab-scan-cache'
image='sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad'
cmd=['docker','run','-d','--pull=never','--name','inferoptlab-cached-decode-scan-20261126-'+ATTEMPT,
 '--label','io.inferoptlab.role=cached-decode-controller','--network=host','--user',f'{os.getuid()}:{os.getgid()}',
 '--group-add',str(os.stat('/var/run/docker.sock').st_gid),'--workdir',str(root)]
for source,target,ro in [(str(root),str(root),False),(str(client),'/work',False),(model,model,True),(cache,cache,False),
 ('/var/run/docker.sock','/var/run/docker.sock',False),('/usr/bin/docker','/usr/bin/docker',True)]:
 cmd+=['--mount',f'type=bind,source={source},target={target}'+(',readonly' if ro else '')]
for k,v in dict(HOME='/work',PYTHONPATH=str(root),PATH='/work/venv/bin:/opt/conda/bin:/usr/local/bin:/usr/bin:/bin').items():cmd+=['-e',k+'='+v]
cmd+=['--entrypoint','/work/venv/bin/python',image,'-u','-m','benchmark.load.cached_decode',
 'recipes/plans/benchmark/glm53-vllm/cached-decode.yaml','--out','experiments/runs/glm53-cached-decode-20261126-'+ATTEMPT]
cid=subprocess.check_output(cmd,text=True).strip()
data=dict(id=cid,command=cmd,output=str(root/('experiments/runs/glm53-cached-decode-20261126-'+ATTEMPT)))
receipt.write_text(json.dumps(data,indent=2));print(json.dumps(data))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -c '+shlex.quote('ATTEMPT='+repr(args.attempt)+'\n'+code)],capture_output=True,timeout=60)
if r.returncode:raise SystemExit(r.stderr.decode(errors='replace'))
data=json.loads(r.stdout);(Path(__file__).resolve().parent/('scan-launch-'+args.attempt+'.json')).write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(dict(id=data['id'],output=data['output'])))
