"""User-requested stop: disable both schedulers, then interrupt only the owned client."""
import json
from pathlib import Path
import shlex
import subprocess

remote=r'''
import datetime,json,os,pathlib,signal,subprocess,time
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
dest=r/'experiments/evidence/glm53-collectives-20261126';dest.mkdir(exist_ok=True)
receipt=dest/'pause-scan.json'
s=json.loads((r/'experiments/evidence/glm53-short-output-continue-failures-20261125/state.json').read_text())
q=json.loads((r/'experiments/evidence/glm53-five-layout-extension-20261125/queue-state.json').read_text())
if not receipt.exists():
 assert q['status']=='waiting_for_prior_scan' and not q.get('child_pid')
 before=json.loads((pathlib.Path(s['batch'])/'batch.json').read_text())
 receipt.write_text(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='User stopped performance scan to measure collective bandwidth',supervisor=s,queue=q,batch_before=before,restore_original_service=False),indent=2))
for state,expected in [(q,'glm53-five-layout-extension-20261125/queue.py'),(s,'supervise_scan.py')]:
 p=pathlib.Path('/proc')/str(state['pid'])/'cmdline'
 if p.exists():
  command=p.read_bytes().replace(b'\0',b' ').decode()
  if command:
   assert expected in command,(state['pid'],command)
   os.kill(state['pid'],signal.SIGTERM)
name=s['attempts'][-1]['client_name']
p=subprocess.run(['docker','inspect',name],capture_output=True,text=True)
if p.returncode==0:
 info=json.loads(p.stdout)[0]
 assert info['Config'].get('Labels',{}).get('io.inferoptlab.role')=='benchmark-client'
 if info['State']['Running']:
  subprocess.run(['docker','kill','--signal=INT',info['Id']],check=True,capture_output=True,text=True,timeout=20)
value=json.loads(receipt.read_text());value['stop_signals_sent_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt.write_text(json.dumps(value,indent=2))
print(json.dumps(dict(receipt=str(receipt),supervisor_pid=s['pid'],queue_pid=q['pid'],client=name,status='stop_signals_sent')))
'''
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(6):
    try:
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(remote)],capture_output=True,text=True,encoding='utf-8',timeout=45)
        if p.returncode==0:
            print(p.stdout);Path(__file__).with_name('pause-for-collectives.json').write_text(p.stdout,encoding='utf-8');break
        print(p.stderr,flush=True)
        if p.returncode!=255:raise SystemExit(p.returncode)
    except subprocess.TimeoutExpired:print('Reconnect to verify idempotent stop',flush=True)
else:raise SystemExit('Stop not yet confirmed')
