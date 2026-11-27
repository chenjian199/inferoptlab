"""Resume once with user-directed failure skips and restart the waiting extension."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import tarfile

ROOT='/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124'
NAME='glm53-short-output-continue-failures-20261125'
QUEUE='experiments/evidence/glm53-five-layout-extension-20261125'
files=['benchmark/load/checkpoint.py','benchmark/load/runner.py','benchmark/load/cli.py',
       'tools/experiments.py','tools/deployment/metax-vllm/run_scan.py',
       'tools/deployment/metax-vllm/supervise_scan.py',QUEUE+'/queue.py']
archive=Path(__file__).with_name('continue-failures.tar.gz')
with tarfile.open(archive,'w:gz') as tar:
    for name in files:tar.add(name,arcname=name)
sha=hashlib.sha256(archive.read_bytes()).hexdigest()
code=r'''
import json,hashlib,os,pathlib,signal,subprocess,sys,tarfile,time
r=pathlib.Path(ROOT);receipt=r/'experiments/evidence'/(NAME+'.launch.json');q=r/QUEUE
env=dict(os.environ,PYTHONPATH=str(r/'.host-deps')+':'+str(r),PATH='/opt/mxdriver/bin:/opt/maca/bin:'+os.environ['PATH'])
if not receipt.exists():
 old=json.loads((r/'experiments/evidence/glm53-short-output-skip-c128-20261125/state.json').read_text())
 p=pathlib.Path('/proc')/str(old['pid'])/'cmdline'
 assert not p.exists() or b'supervise_scan.py' not in p.read_bytes(),'prior supervisor still active'
 assert old['original_restored'] and not (r/'experiments/runs/benchmark/.execution.lock').exists()
 archive=r/'experiments/evidence/continue-failures.tar.gz'
 assert hashlib.sha256(archive.read_bytes()).hexdigest()==SHA
 with tarfile.open(archive) as tar:
  assert sorted(tar.getnames())==sorted(FILES)
  for member in tar.getmembers():
   target=r/member.name
   assert member.isfile() and target.resolve().is_relative_to(r.resolve())
   tmp=target.with_suffix(target.suffix+'.continue-update')
   tmp.write_bytes(tar.extractfile(member).read());os.replace(tmp,target)
 sys.path[:0]=[str(r/'.host-deps'),str(r)]
 from tools.specs import read
 from benchmark.load.checkpoint import load
 b=pathlib.Path(old['batch']);load(b,read(b/'resolved.yaml'))
 previous=json.loads((r/'experiments/evidence/glm53-short-output-skip-c128-20261125.launch.json').read_text())
 command=previous['command'];command[command.index('--state-dir')+1]=str(r/'experiments/evidence'/NAME)
 command+=['--skip-failed-configurations','--max-stalled-attempts','1']
 with receipt.open('x') as f:
  with (r/'experiments/evidence'/(NAME+'.log')).open('x') as log:
   child=subprocess.Popen(command,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  json.dump(dict(pid=child.pid,command=command,batch=str(b),code_sha256=SHA,policy='skip_failed_configurations'),f,indent=2)
launched=json.loads(receipt.read_text())
state=r/'experiments/evidence'/NAME/'state.json'
for attempt in range(30):
 if state.exists():break
 time.sleep(1)
else:raise SystemExit('New supervisor state not visible; inspect receipt before another launch')
new=json.loads(state.read_text())
assert new.get('batch')==launched['batch']
queue_receipt=q/'launch-continue-failures.json'
if not queue_receipt.exists():
 oldq=json.loads((q/'queue-state.json').read_text());p=pathlib.Path('/proc')/str(oldq['pid'])/'cmdline'
 if p.exists() and b'glm53-five-layout-extension-20261125/queue.py' in p.read_bytes():
  assert oldq['status']=='waiting_for_prior_scan' and not oldq.get('child_pid'),'queue already started a child'
  os.kill(oldq['pid'],signal.SIGTERM)
 cfg=json.loads((q/'queue-config.json').read_text());cfg['after_state']='experiments/evidence/'+NAME+'/state.json'
 (q/'queue-config.json').write_text(json.dumps(cfg,indent=2))
 with queue_receipt.open('x') as f:
  with (q/'queue-continue-failures.log').open('x') as log:
   child=subprocess.Popen(['python3','-u',str(q/'queue.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  json.dump(dict(pid=child.pid,prior_queue_pid=oldq['pid'],after_state=cfg['after_state'],policy='skip_failed_configurations'),f,indent=2)
print(json.dumps(dict(supervisor=launched,queue=json.loads(queue_receipt.read_text()))))
'''
code='ROOT='+repr(ROOT)+'\nNAME='+repr(NAME)+'\nQUEUE='+repr(QUEUE)+'\nFILES='+repr(files)+'\nSHA='+repr(sha)+'\n'+code
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(12):
    try:
        p=subprocess.run(['scp',*opts,str(archive),f'metax-60:{ROOT}/experiments/evidence/continue-failures.tar.gz'],capture_output=True,text=True,encoding='utf-8',timeout=45)
        if p.returncode:
            print('Transfer retry',attempt,p.stderr,flush=True);continue
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],capture_output=True,text=True,encoding='utf-8',timeout=55)
        print(p.stdout,p.stderr,flush=True)
        if p.returncode==0:
            Path(__file__).with_name('continue-failures-launch.json').write_text(p.stdout,encoding='utf-8');break
        if p.returncode!=255:raise SystemExit(p.returncode)
    except subprocess.TimeoutExpired:
        print('VPN timeout; retry idempotent continuation',attempt,flush=True)
else:raise SystemExit('Continuation launch not confirmed')
