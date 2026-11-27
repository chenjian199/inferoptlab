"""Detached, bounded microbenchmark campaign; never restarts the model scan."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

ROOT=Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
OUT=ROOT/'experiments/evidence/glm53-collectives-20261126'
NAME='inferoptlab-collectives-20261126'
PROBE='/workspace/tools/hardware/probes/collective_bandwidth.py'
GROUPS=[[0,1,2,3,4,5,6,7],[0,2,4,6],[0,4],[0,1,2,3],[4,5,6,7],[0,1]]
OPS=['all_to_all','all_gather','reduce_scatter','all_gather_reduce_scatter','all_to_all_roundtrip','all_reduce']
SIZES=[8192*2**i for i in range(16)]
state=dict(pid=os.getpid(),status='running',started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),jobs=[],groups=GROUPS,sizes=SIZES,operations=OPS)
def save():
    state['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    tmp=OUT/'bandwidth-state.tmp';tmp.write_text(json.dumps(state,indent=2));tmp.replace(OUT/'bandwidth-state.json')

assert not (OUT/'bandwidth-state.json').exists()
assert not (ROOT/'experiments/runs/benchmark/.execution.lock').exists()
idle=subprocess.run(['/opt/mxdriver/bin/mx-smi','--show-process'],capture_output=True,text=True,check=True)
(OUT/'gpu-before.txt').write_text(idle.stdout)
assert 'no process found' in idle.stdout.lower(),idle.stdout
save()
try:
    for devices in GROUPS:
        for op in OPS:
            tag='gpu'+''.join(map(str,devices))+'-'+op
            job=dict(id=tag,devices=devices,operation=op,status='running',started_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            state['jobs'].append(job);state['current']=tag;save()
            cmd=['docker','exec','-e','MACA_VISIBLE_DEVICES='+','.join(map(str,devices)),'-e','OMP_NUM_THREADS=1','-e','NCCL_DEBUG=WARN',NAME,
                 '/opt/vllm-env/bin/python','-m','torch.distributed.run','--standalone','--nproc_per_node='+str(len(devices)),PROBE,
                 '--operation',op,'--physical-devices',','.join(map(str,devices)),'--sizes',*map(str,SIZES),
                 '--out','/workspace/experiments/evidence/glm53-collectives-20261126/'+tag+'.jsonl']
            job['command']=cmd;save()
            with (OUT/(tag+'.log')).open('x') as log:
                process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
                job['pid']=process.pid;save()
                try:code=process.wait(timeout=240)
                except subprocess.TimeoutExpired:
                    subprocess.run(['docker','stop','--time','10',NAME],capture_output=True,timeout=25)
                    process.wait(timeout=20)
                    job.update(status='timed_out');save();raise RuntimeError('Timed out; owned container stopped; no retries')
            job.update(returncode=code,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
            if code!=0:
                job['status']='failed';save()
                # Failed communicators are isolated in the exited torchrun job.
                # Proceed only after no worker remains in this container.
                top=subprocess.run(['docker','top',NAME,'-eo','args'],capture_output=True,text=True,check=True).stdout
                if 'collective_bandwidth.py' in top:raise RuntimeError('Worker remains after failure')
                continue
            rows=[json.loads(x) for x in (OUT/(tag+'.jsonl')).read_text().splitlines() if x.strip()]
            assert len(rows)==len(SIZES) and all(x['correctness']=='passed' and len(x['samples_ms'])==5 for x in rows)
            job.update(status='completed',points=len(rows),sha256=hashlib.sha256((OUT/(tag+'.jsonl')).read_bytes()).hexdigest());save()
    state['status']='completed' if all(j['status']=='completed' for j in state['jobs']) else 'completed_with_failures'
except BaseException as exc:
    state.update(status='stopped',error=repr(exc));raise
finally:
    state['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();state['current']=None;save()
    subprocess.run(['docker','stop','--time','10',NAME],capture_output=True,timeout=25)
    after=subprocess.run(['/opt/mxdriver/bin/mx-smi','--show-process'],capture_output=True,text=True)
    (OUT/'gpu-after.txt').write_text(after.stdout+after.stderr)
