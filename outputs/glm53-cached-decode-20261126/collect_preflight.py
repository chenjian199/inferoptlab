import json
from pathlib import Path
import shlex
import subprocess
import tarfile

OUT=Path(__file__).resolve().parent
code='''
import pathlib,tarfile
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
evidence=root/'experiments/evidence/glm53-cached-decode-20261126'
archive=evidence/'preflight-evidence.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
 for name in ['proof-tp8','repeatability','observations-tp8','observed-proof-4k-c2-1795667946786800114',
  'preflight-launch.json','observed-launch.json','preflight-server.log','observed-server.log']:
  p=evidence/name
  if p.exists():tar.add(p,arcname=name)
 failed=root/'experiments/runs/glm53-cached-decode-20261126'
 if failed.exists():tar.add(failed,arcname='dp8-startup-oom')
print(str(archive))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -c '+shlex.quote(code)],capture_output=True,check=True,timeout=45)
archive=OUT/'preflight-evidence.tar.gz'
subprocess.run(['scp','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60:'+r.stdout.decode().strip(),str(archive)],check=True,timeout=45)
target=OUT/'preflight-evidence';target.mkdir(exist_ok=True)
with tarfile.open(archive,'r:gz') as tar:
 for m in tar.getmembers():
  if not (target/m.name).resolve().is_relative_to(target.resolve()):raise ValueError('unsafe archive path')
 tar.extractall(target,filter='data')
print(archive.stat().st_size)
