"""Transfer a bounded diagnostic and launch once despite an unreliable SSH link."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import time

folder=Path(sys.argv[1])
root='/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124'
remote=root+'/'+folder.as_posix()
files=[folder/x for x in ['run_diagnostic.py','check_prefill.py','diagnostic_flashmla.py']]

def ssh(code):
    return subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',
        '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60',
        'python3 -c '+shlex.quote(code)],capture_output=True,text=True,timeout=45)

for attempt in range(12):
    try:
        p=ssh('from pathlib import Path;Path('+repr(remote)+').mkdir(parents=True,exist_ok=True)')
        if p.returncode:
            continue
        p=subprocess.run(['scp','-o','BatchMode=yes','-o','ConnectTimeout=8',
            '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2',
            *[str(x) for x in files],'metax-60:'+remote+'/'],capture_output=True,text=True,timeout=45)
        if p.returncode:
            continue
        expected={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        code=f'''import pathlib,hashlib,json,subprocess,os,sys
p=pathlib.Path({remote!r});r=pathlib.Path({root!r})
for n,h in {expected!r}.items(): assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h
receipt=p/'launch.json'
if receipt.exists():print(receipt.read_text())
else:
 if (r/'experiments/runs/benchmark/.execution.lock').exists():
  print('WAITING_FOR_EXISTING_LEASE');sys.exit(3)
 with receipt.open('x') as f:
  with (p/'controller.log').open('x') as log:
   env=dict(os.environ,PYTHONPATH=str(r/'.host-deps')+':'+str(r),PATH='/opt/mxdriver/bin:/opt/maca/bin:'+os.environ['PATH'])
   child=subprocess.Popen(['python3','-u',str(p/'run_diagnostic.py')],cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  value=dict(pid=child.pid,diagnostic_only=True);json.dump(value,f);print(json.dumps(value))
'''
        p=ssh(code)
        print(p.stdout,p.stderr,flush=True)
        if p.returncode==0:
            break
        if p.returncode==3:
            time.sleep(15)
    except subprocess.TimeoutExpired:
        print('VPN timeout; retry',attempt,flush=True)
else:
    raise SystemExit('upload/launch not confirmed')
