"""Ship a frozen source/config bundle and start the owned remote capacity controller."""
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
REMOTE = '/home/ubuntu/CJ_workspace/inferoptlab-prefill-fix-20261127'
HOST = 'metax-60'
archive = OUT/'source.tar.gz'
with tarfile.open(archive, 'w:gz') as tar:
    for top in ['benchmark', 'tools', 'contracts']:
        for p in sorted((ROOT/top).rglob('*.py')):
            tar.add(p, arcname=p.relative_to(ROOT).as_posix())
    tar.add(ROOT/'benchmark-matrix.yaml', arcname='benchmark-matrix.yaml')
    tar.add(OUT/'diagnose.py', arcname='diagnose.py')

def ssh(script):
    p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', HOST, 'python3 -'],
                       input=script.encode(), capture_output=True, timeout=60)
    if p.returncode:
        raise RuntimeError(p.stderr.decode(errors='replace'))
    return p.stdout.decode()

print(ssh("from pathlib import Path\np=Path("+repr(REMOTE)+")\np.mkdir(parents=True,exist_ok=True)\nassert not (p/'launch.json').exists(), 'already launched; inspect receipt'\nprint(p)"))
subprocess.run(['scp', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', str(archive),
                HOST+':'+REMOTE+'/source.tar.gz'], check=True, timeout=90)
remote = r'''
import json,os,subprocess,tarfile
from pathlib import Path
root=Path(REMOTE)
with tarfile.open(root/'source.tar.gz','r:gz') as tar:
    for member in tar.getmembers():
        assert member.isfile() and (root/member.name).resolve().is_relative_to(root.resolve())
    tar.extractall(root)
import shutil
compiled=Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/evidence/glm53-flashmla-offset64-20261125/build-source/_inferoptlab_flashmla_offset64.cpython-312-x86_64-linux-gnu.so')
shutil.copy2(compiled,root/'tools/deployment/metax-vllm/observers'/compiled.name)
active=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).strip()
if active:raise RuntimeError('active containers appeared: '+active)
inventory={}
for name,args in [('hardware',['/usr/bin/mx-smi','-j']),('driver',['/usr/bin/mx-smi','--show-hwinfo']),('docker',['docker','version'])]:
 p=subprocess.run(args,capture_output=True,text=True,timeout=15)
 inventory[name]=dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
(root/'host-inventory.json').write_text(json.dumps(inventory,indent=2))
client=Path('/home/ubuntu/CJ_workspace/inferoptlab-client-20261124')
model='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8'
cache='/home/ubuntu/CJ_workspace/inferoptlab-scan-cache'
image='sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad'
cmd=['docker','run','-d','--pull=never','--name','inferoptlab-prefill-fix-20261127',
 '--label','io.inferoptlab.role=matrix-controller','--network=host',
 '--user',f'{os.getuid()}:{os.getgid()}','--group-add',str(os.stat('/var/run/docker.sock').st_gid),
 '--workdir',str(root)]
for source,target,ro in [(str(root),str(root),False),(str(client),'/work',False),
 (model,model,True),(cache,cache,False),('/var/run/docker.sock','/var/run/docker.sock',False),
 ('/usr/bin/docker','/usr/bin/docker',True)]:
 cmd+=['--mount',f'type=bind,source={source},target={target}'+(',readonly' if ro else '')]
for k,v in dict(HOME='/work',PYTHONPATH=str(root),PATH='/work/venv/bin:/opt/conda/bin:/usr/local/bin:/usr/bin:/bin',
 TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1').items():
 cmd+=['-e',k+'='+v]
cmd+=['--entrypoint','/work/venv/bin/python',image,'-u','diagnose.py']
cid=subprocess.check_output(cmd,text=True).strip()
receipt=dict(id=cid,command=cmd,root=str(root))
(root/'launch.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
'''
receipt=json.loads(ssh('REMOTE='+repr(REMOTE)+'\n'+remote))
(OUT/'launch.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('Started', receipt['id'])
