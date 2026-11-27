"""Fetch a read-only scan snapshot, retaining metric and qualification evidence.

Large token fixtures and response echoes remain in the remote experiment folder.
The download manifest lists exactly what was copied and its content hashes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import tarfile

parser = argparse.ArgumentParser()
parser.add_argument('--attempt', default='r3')
args = parser.parse_args()
if not args.attempt.isalnum():
    raise SystemExit('attempt must be alphanumeric')
out = Path(__file__).resolve().parent
code = r'''
import hashlib,json,pathlib,tarfile,time
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
run=root/('experiments/runs/glm53-cached-decode-20261126-'+ATTEMPT)
assert run.is_dir()
archive=run.parent/(run.name+'-metrics.tar.gz')
names={'state.json','snapshot.json','README.md','launch.json','server-info.json',
 'server.log','qualification.json','reset.json','tokenizer.json','command.json',
 'server.json','expected.json','engine-verification.json','profile-verification.json',
 'aiperf.log','profile_export_aiperf.json','profile_export.jsonl'}
paths=[p for p in run.rglob('*') if p.is_file() and
 (p.name in names or p.name.startswith('code-') or p.parent.name=='observations')]
manifest={'captured_at_unix':time.time(),'remote_run':str(run),'files':[]}
# Copy bytes into tar from memory to avoid hashing a different version of a live file.
import io
with tarfile.open(archive,'w:gz') as tar:
 for p in sorted(paths):
  data=p.read_bytes();name=p.relative_to(run).as_posix()
  entry=tarfile.TarInfo(name);entry.size=len(data);tar.addfile(entry,io.BytesIO(data))
  manifest['files'].append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 data=json.dumps(manifest,indent=2).encode()
 entry=tarfile.TarInfo('download-manifest.json');entry.size=len(data);tar.addfile(entry,io.BytesIO(data))
print(archive)
'''
ssh = ['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
       '-o', 'ServerAliveInterval=5', '-o', 'ServerAliveCountMax=2', 'metax-60']
result = subprocess.run(ssh+['python3 -c '+shlex.quote('ATTEMPT='+repr(args.attempt)+'\n'+code)],
                        capture_output=True, check=True, timeout=60)
archive = out/('scan-'+args.attempt+'-metrics.tar.gz')
subprocess.run(['scp','-o','BatchMode=yes','-o','ConnectTimeout=8',
                'metax-60:'+result.stdout.decode().strip(),str(archive)],check=True,timeout=60)
target = out/('scan-'+args.attempt)
target.mkdir(exist_ok=True)
with tarfile.open(archive,'r:gz') as tar:
    for member in tar.getmembers():
        if not (target/member.name).resolve().is_relative_to(target.resolve()):
            raise ValueError('unsafe archive member')
    tar.extractall(target,filter='data')
manifest=json.loads((target/'download-manifest.json').read_text())
for item in manifest['files']:
    if hashlib.sha256((target/item['path']).read_bytes()).hexdigest()!=item['sha256']:
        raise ValueError('download hash mismatch: '+item['path'])
state=json.loads((target/'state.json').read_text())
from collections import Counter
print(json.dumps({'status':state['status'],'points':dict(Counter(p['status'] for p in state['points'])),
                  'files':len(manifest['files']),'bytes':archive.stat().st_size}))
