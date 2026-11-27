"""Transfer and idempotently queue the additional three deployment layouts."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import tarfile

ROOT='/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124'
DIRECTORY='experiments/evidence/glm53-five-layout-extension-20261125'
files=['tools/deployment/metax-vllm/supervise_scan.py',
       'recipes/studies/glm53-vllm-decode-five-layouts.yaml',
       'recipes/plans/benchmark/glm53-vllm/decode-five-layouts.yaml',
       'recipes/plans/benchmark/glm53-vllm/decode-additional-layouts.yaml',
       *['recipes/deployments/glm53-flash/c500/vllm/decode/'+n+'.yaml'
         for n in ['tp8','tp8-ep8','tp1-dp8-ep8']],
       DIRECTORY+'/queue.py',DIRECTORY+'/queue-config.json']
archive=Path(__file__).with_name('five-layout-extension.tar.gz')
with tarfile.open(archive,'w:gz') as tar:
    for name in files:tar.add(name,arcname=name)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
expected=json.loads(Path('outputs/short-output-control/completed-audit.json').read_text())['snapshot_sha256']
code=r'''
import hashlib,json,os,pathlib,subprocess,sys,tarfile
r=pathlib.Path(ROOT);out=r/DIRECTORY
receipt=out/'launch.json'
if receipt.exists():print(receipt.read_text());sys.exit(0)
archive=r/'experiments/evidence/five-layout-extension.tar.gz'
assert hashlib.sha256(archive.read_bytes()).hexdigest()==SHA
with tarfile.open(archive) as tar:
 assert sorted(tar.getnames())==sorted(FILES)
 for member in tar.getmembers():
  assert member.isfile()
  target=r/member.name
  assert target.resolve().is_relative_to(r.resolve())
  target.parent.mkdir(parents=True,exist_ok=True)
  tmp=target.with_suffix(target.suffix+'.extension-update')
  tmp.write_bytes(tar.extractfile(member).read())
  os.replace(tmp,target)
sys.path[:0]=[str(r/'.host-deps'),str(r)]
from tools.specs import Catalog,write
from benchmark.load.cli import load_snapshot
c=Catalog(r);c.load()
cfg=json.loads((out/'queue-config.json').read_text())
old=load_snapshot(c,r/cfg['prior_batch']/'resolved.yaml')
assert old['content_sha256']==EXPECTED
snapshot=load_snapshot(c,r/cfg['plan'])
assert not snapshot['execution_issues'] and len(snapshot['trials'])==432
assert snapshot['content_sha256']=='94f66a352832e5b2f5df01af04760da3c8247bc7e0827d3b7da9a1b928d515c9'
all_points=load_snapshot(c,r/'recipes/plans/benchmark/glm53-vllm/decode-five-layouts.yaml')
assert not all_points['execution_issues'] and len(all_points['trials'])==720
write(out/'resolved.yaml',snapshot)
env=dict(os.environ,PYTHONPATH=str(r/'.host-deps')+':'+str(r),PATH='/opt/mxdriver/bin:/opt/maca/bin:'+os.environ['PATH'])
with receipt.open('x') as f:
 with (out/'queue.log').open('x') as log:
  child=subprocess.Popen(['python3','-u',str(out/'queue.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 value=dict(pid=child.pid,code_sha256=SHA,plan_sha256=snapshot['content_sha256'],added_points=432,full_points=720,waits_for=cfg['prior_batch'])
 json.dump(value,f,indent=2);print(json.dumps(value))
'''
code='ROOT='+repr(ROOT)+'\nDIRECTORY='+repr(DIRECTORY)+'\nFILES='+repr(files)+'\nSHA='+repr(sha)+'\nEXPECTED='+repr(expected)+'\n'+code
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(12):
    try:
        p=subprocess.run(['scp',*opts,str(archive),f'metax-60:{ROOT}/experiments/evidence/five-layout-extension.tar.gz'],capture_output=True,text=True,encoding='utf-8',timeout=45)
        if p.returncode:
            print('Transfer retry',attempt,p.stderr,flush=True);continue
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],capture_output=True,text=True,encoding='utf-8',timeout=55)
        print(p.stdout,p.stderr,flush=True)
        if p.returncode==0:
            Path(DIRECTORY,'launch.json').write_text(p.stdout,encoding='utf-8');break
        if p.returncode!=255:raise SystemExit(p.returncode)
    except subprocess.TimeoutExpired:
        print('VPN timeout; retry idempotent launch',attempt,flush=True)
else:raise SystemExit('Queue launch not confirmed')
