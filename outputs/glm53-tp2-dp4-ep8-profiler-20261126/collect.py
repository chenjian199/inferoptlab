"""Fetch immutable completed profiler evidence and check the archive checksum."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import time

parser=argparse.ArgumentParser()
parser.add_argument('--attempt',default='r2',choices=['r1','r2'])
args=parser.parse_args()
out=Path(__file__).resolve().parent
remote='/home/ubuntu/CJ_workspace/inferoptlab-profiler-20261126'
code='ATTEMPT='+repr(args.attempt)+'\n'+'''
import hashlib,json,tarfile
from pathlib import Path
r=Path('/home/ubuntu/CJ_workspace/inferoptlab-profiler-20261126')
run=r/'experiments/runs'/('glm53-tp2-dp4-ep8-profiler-'+ATTEMPT)
state=json.loads((run/'state.json').read_text())
if state['status'] not in ['completed','failed','finished_with_exclusions']:raise RuntimeError('capture is still active')
archive=r/('profile-'+ATTEMPT+'.tar.gz')
with tarfile.open(archive,'w:gz',compresslevel=1) as tar:
 tar.add(run,arcname='run-'+ATTEMPT)
h=hashlib.sha256()
with archive.open('rb') as f:
 for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
print(json.dumps(dict(archive=str(archive),bytes=archive.stat().st_size,sha256=h.hexdigest(),status=state['status'])))
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -'],input=code.encode(),capture_output=True,timeout=120)
if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace'))
receipt=json.loads(p.stdout);(out/('collection-'+args.attempt+'.json')).write_text(json.dumps(receipt,indent=2))
archive=out/('profile-'+args.attempt+'.tar.gz')
for attempt in range(3):
    p=subprocess.run(['scp','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60:'+receipt['archive'],str(archive)],capture_output=True,timeout=240)
    if not p.returncode:break
    if attempt==2:raise RuntimeError(p.stderr.decode(errors='replace'))
    time.sleep(2)
h=hashlib.sha256()
with archive.open('rb') as f:
    for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
assert h.hexdigest()==receipt['sha256']
with tarfile.open(archive) as tar:
    for item in tar:
        target=(out/item.name).resolve()
        if not target.is_relative_to(out.resolve()):raise ValueError('unsafe archive path')
        if item.isdir():target.mkdir(parents=True,exist_ok=True)
        elif item.isfile():
            target.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(item) as src,target.open('wb') as dst:
                for block in iter(lambda:src.read(1024*1024),b''):dst.write(block)
        else:raise ValueError('archive contains a link or special file')
print(json.dumps(receipt))
