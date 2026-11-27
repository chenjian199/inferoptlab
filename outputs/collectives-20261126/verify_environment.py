"""After completion, verify device masks and archive exact image/model identity."""
import json
from pathlib import Path
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
remote = r'''
import hashlib,json,pathlib,subprocess,time
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
out=root/'experiments/evidence/glm53-collectives-20261126'
state=json.loads((out/'bandwidth-state.json').read_text())
assert state['status']=='completed'
name='inferoptlab-collectives-20261126'
container=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
assert container['Config']['Labels']['io.inferoptlab.role']=='collective-bandwidth'
assert not container['State']['Running'],'Wait until the campaign has stopped its container'
proc=pathlib.Path('/proc')/str(state['pid'])/'cmdline'
assert not proc.exists() or b'run_remote.py' not in proc.read_bytes()
idle=subprocess.check_output(['/opt/mxdriver/bin/mx-smi','--show-process'],text=True)
assert 'no process found' in idle.lower()
probe=root/'tools/hardware/probes/collective_bandwidth.py'
config=pathlib.Path('/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8/config.json').read_bytes()
result=dict(image=container['Image'],image_env=container['Config']['Env'],model_config=json.loads(config),
 model_config_sha256=hashlib.sha256(config).hexdigest(),probe_sha256=hashlib.sha256(probe.read_bytes()).hexdigest(),
 topology=subprocess.check_output(['/opt/mxdriver/bin/mx-smi','topo','-m'],text=True),masks=[])
(out/'collective_bandwidth.py').write_bytes(probe.read_bytes())
code="""
import json,os,torch
devices=[]
for i in range(torch.cuda.device_count()):
 p=torch.cuda.get_device_properties(i)
 devices.append(dict(index=i,properties=str(p),**{k:str(getattr(p,k)) for k in ['name','uuid','pci_bus_id','pci_device_id','total_memory'] if hasattr(p,k)}))
try: version=torch.cuda.nccl.version()
except Exception as exc:version=repr(exc)
print(json.dumps(dict(mask=os.environ['MACA_VISIBLE_DEVICES'],count=len(devices),devices=devices,torch=torch.__version__,nccl_api_version=version)))
"""
try:
 subprocess.run(['docker','start',name],check=True,stdout=subprocess.DEVNULL)
 for group in state['groups']:
  mask=','.join(map(str,group))
  text=subprocess.check_output(['docker','exec','-e','MACA_VISIBLE_DEVICES='+mask,name,'/opt/vllm-env/bin/python','-c',code],text=True,timeout=45)
  data=json.loads(text)
  assert data['count']==len(group),(group,data)
  result['masks'].append(data)
finally:
 subprocess.run(['docker','stop','--time','10',name],capture_output=True,timeout=25)
result['gpu_after']=subprocess.check_output(['/opt/mxdriver/bin/mx-smi','--show-process'],text=True)
result['containers_after']=subprocess.check_output(['docker','ps','--format','{{.Names}} {{.Status}}'],text=True)
assert 'no process found' in result['gpu_after'].lower()
(out/'environment-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
'''
r = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5',
                    '-o','ServerAliveCountMax=2','metax-60','python3 -c '+shlex.quote(remote)],
                   capture_output=True,timeout=300)
if r.returncode:
    raise SystemExit(r.stderr.decode(errors='replace'))
data=json.loads(r.stdout)
(OUT/'environment-verification.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
print(json.dumps(dict(image=data['image'],probe=data['probe_sha256'],masks=data['masks'],containers=data['containers_after'])))
