import json,os,subprocess
from pathlib import Path
root=Path('/home/ubuntu/CJ_workspace/inferoptlab-profiler-20261126')
receipt=root/'launch-r2.json'
if receipt.exists():print(receipt.read_text());raise SystemExit()
active=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).strip()
if active:raise RuntimeError('New active containers appeared: '+active)
client=Path('/home/ubuntu/CJ_workspace/inferoptlab-client-20261124')
model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
cache='/home/ubuntu/CJ_workspace/inferoptlab-scan-cache'
image='sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad'
cmd=['docker','run','-d','--pull=never','--name','inferoptlab-decode-profiler-20261126-r2','--label','io.inferoptlab.role=decode-profiler-controller','--network=host','--user',f'{os.getuid()}:{os.getgid()}','--group-add',str(os.stat('/var/run/docker.sock').st_gid),'--workdir',str(root)]
for source,target,ro in [(str(root),str(root),False),(str(client),'/work',False),(model,model,True),(cache,cache,False),('/var/run/docker.sock','/var/run/docker.sock',False),('/usr/bin/docker','/usr/bin/docker',True)]:
 cmd+=['--mount',f'type=bind,source={source},target={target}'+(',readonly' if ro else '')]
for k,v in dict(HOME='/work',PYTHONPATH=str(root),PATH='/work/venv/bin:/opt/conda/bin:/usr/local/bin:/usr/bin:/bin').items():cmd+=['-e',k+'='+v]
cmd+=['--entrypoint','/work/venv/bin/python',image,'-u','-m','benchmark.breakdown.cached_decode_profile','recipes/plans/breakdown/glm53-cached-decode-profiler.yaml','--out','experiments/runs/glm53-tp2-dp4-ep8-profiler-r2']
cid=subprocess.check_output(cmd,text=True).strip();data=dict(id=cid,command=cmd,root=str(root));receipt.write_text(json.dumps(data,indent=2));print(json.dumps(data))
