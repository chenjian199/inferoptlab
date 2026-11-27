"""Read-only observation of this scan; connection loss never triggers a restart."""
import argparse
import json
from pathlib import Path
import shlex
import subprocess
import time

REMOTE = r'''
import json,pathlib,subprocess,datetime
from collections import Counter
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
additional=r/'experiments/evidence/glm53-five-layout-extension-20261125/scan/state.json'
stage='additional' if additional.exists() else 'original'
state_path=additional if stage=='additional' else r/'experiments/evidence/glm53-short-output-continue-failures-20261125/state.json'
s=json.loads(state_path.read_text())
b=pathlib.Path(s['batch']) if s.get('batch') else None
v=json.loads((b/'batch.json').read_text()) if b else dict(status=s['status'],runs=[])
proc=pathlib.Path('/proc')/str(s['pid'])/'cmdline'
cmd=proc.read_bytes().replace(b'\0',b' ').decode() if proc.exists() else ''
result=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage=stage,supervisor_status=s['status'],supervisor_live='supervise_scan.py' in cmd,supervisor_pid=s['pid'],heartbeat=s['updated_at'],batch=str(b) if b else None,batch_status=v['status'],counts=dict(Counter(x['status'] for x in v['runs'])),current=v.get('current_trial'),preparing_fixture=v.get('preparing_fixture'),completed=[],failures=[])
for row in v['runs']:
 if row['status']=='completed':
  d=json.loads((b/row['directory']/'decode.json').read_text())
  result['completed'].append(dict(row,tpot_mean_ms=d['tpot_ms']['mean'],requests=d['counts']))
 elif row['status'] in ['failed','invalid','interrupted','completed_with_errors','unverified']:
  p=b/row['directory']/'run.json'
  result['failures'].append(dict(row,error=json.loads(p.read_text()).get('error')))
 if result['current'] and row.get('directory')==result['current']['directory']:
  result['current'].update({k:row[k] for k in ['deployment','scenario','concurrency','repetition']})
result['completed']=result['completed'][-3:]
result['containers']=subprocess.run(['docker','ps','--format','{{.ID}} {{.Names}} {{.Status}}'],capture_output=True,text=True,timeout=15).stdout.splitlines()
q=r/'experiments/evidence/glm53-five-layout-extension-20261125/queue-state.json'
if q.exists():
 queue=json.loads(q.read_text());p=pathlib.Path('/proc')/str(queue['pid'])/'cmdline'
 queue['process_live']=p.exists() and b'glm53-five-layout-extension-20261125/queue.py' in p.read_bytes()
 result['extension_queue']=queue
print(json.dumps(result))
'''


def poll(compact=False):
    for _ in range(4):
        try:
            result = subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',
                         '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2',
                         'metax-60','python3 -c '+shlex.quote(REMOTE)],
                         text=True,encoding='utf-8',capture_output=True,timeout=40)
        except subprocess.TimeoutExpired:
            continue
        if result.returncode == 0:
            value = json.loads(result.stdout)
            out = Path(__file__).parent
            (out/'last-poll.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
            with (out/'polls.jsonl').open('a',encoding='utf-8') as stream:
                stream.write(json.dumps(value)+'\n')
            report=value
            if compact:
                report={k:value.get(k) for k in ['at','stage','supervisor_status','supervisor_live','counts','current','preparing_fixture','extension_queue']}
                report['latest_completed']=value['completed'][-1:] if value['completed'] else []
            print(json.dumps(report),flush=True)
            return value
    print('OBSERVATION_UNAVAILABLE: SSH retries exhausted; remote execution status is unknown',flush=True)
    return None


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--checks',type=int,default=1)
    parser.add_argument('--interval',type=int,default=45)
    parser.add_argument('--compact',action='store_true')
    args=parser.parse_args()
    for i in range(args.checks):
        value=poll(args.compact)
        if value and (any(not row.get('failure_evidence') for row in value['failures'])
                      or value['supervisor_status'] in ['needs_repair','completed','completed_with_skips','finished_with_failures']):
            break
        if i+1 < args.checks:
            time.sleep(args.interval)
