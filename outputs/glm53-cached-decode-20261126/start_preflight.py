"""Start only an owned cache-qualification server, never the old scan."""
import json
from pathlib import Path
import shlex
import subprocess
import sys

import yaml

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
sys.path.insert(0,str(ROOT))
from benchmark.load.adapters.vllm import server_arguments

dep=yaml.safe_load((ROOT/'recipes/deployments/glm53-flash/c500/vllm/decode/tp8-ep8.yaml').read_text(encoding='utf-8'))
runtime=yaml.safe_load((ROOT/'recipes/runtimes/metax60-vllm-glm53-source.yaml').read_text(encoding='utf-8'))
dep['prefix_cache']=True
dep['backend_options'].update({'--mamba-block-size':256,'--prefix-match-unit':16})
server=server_arguments(dep,runtime)
(OUT/'preflight-deployment.yaml').write_text(yaml.safe_dump(dep,sort_keys=False),encoding='utf-8')
remote='''
import datetime,json,pathlib,subprocess
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
out=root/'experiments/evidence/glm53-cached-decode-20261126'
out.mkdir(parents=True,exist_ok=True)
receipt=out/'preflight-launch.json'
if receipt.exists():print(receipt.read_text());raise SystemExit(0)
idle=subprocess.check_output(['/opt/mxdriver/bin/mx-smi','--show-process'],text=True)
assert 'no process found' in idle.lower()
assert not (root/'experiments/runs/benchmark/.execution.lock').exists()
model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
image=CONFIG['image'];name='inferoptlab-cached-decode-tp8-preflight'
cmd=['docker','run','-d','--pull=never','--name',name,'--label','io.inferoptlab.role=cached-decode-preflight',
 '--network=host','--shm-size=32g','--ulimit','memlock=-1:-1','--ulimit','stack=67108864:67108864',
 '--device=/dev/mxcd','--device=/dev/dri','-v',model+':'+model+':ro','-v',str(root)+':/workspace']
env=CONFIG['env'];env.update({'VLLM_SERVER_DEV_MODE':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'})
for k,v in env.items():cmd+=['-e',k+'='+str(v)]
for source,target in [('cache','/root/.cache'),('triton','/root/.triton')]:
 p=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-cache')/image.split(':')[1]/source
 assert p.is_dir();cmd+=['-v',str(p)+':'+target]
cmd+=['--entrypoint','/opt/vllm-env/bin/python',image,'-m','vllm.entrypoints.openai.api_server',*CONFIG['server']]
cid=subprocess.check_output(cmd,text=True).strip()
result=dict(name=name,id=cid,command=cmd,created_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
receipt.write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''
config=dict(image=runtime['container_digest'],env=runtime['execution_profile']['environment'],server=server)
remote='CONFIG='+repr(config)+'\n'+remote
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60','python3 -c '+shlex.quote(remote)],capture_output=True,timeout=60)
if r.returncode:raise SystemExit(r.stderr.decode(errors='replace'))
d=json.loads(r.stdout);(OUT/'preflight-launch.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps({k:d[k] for k in ['name','id','created_at']}))
