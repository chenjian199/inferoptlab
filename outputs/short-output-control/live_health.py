"""Read actual server/client liveness while a measurement is in progress."""
import json
from pathlib import Path
import shlex
import subprocess
import sys

code=r'''
import json,pathlib,subprocess,urllib.request,datetime
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
additional=r/'experiments/evidence/glm53-five-layout-extension-20261125/scan/state.json'
stage='additional' if additional.exists() else 'original'
state_path=additional if stage=='additional' else r/'experiments/evidence/glm53-short-output-continue-failures-20261125/state.json'
s=json.loads(state_path.read_text())
b=pathlib.Path(s['batch']) if s.get('batch') else None
v=json.loads((b/'batch.json').read_text()) if b else {}
out=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),stage=stage,current=v.get('current_trial'))
names=subprocess.run(['docker','ps','--format','{{.Names}}'],capture_output=True,text=True,timeout=20).stdout.splitlines()
out['containers']={}
for name in names:
 if not name.startswith(('inferoptlab-scan-','inferoptlab-client-')):continue
 top=subprocess.run(['docker','top',name,'-eo','pid,etime,time,pcpu,args'],capture_output=True,text=True,timeout=20).stdout
 out['containers'][name]=dict(processes=[l for l in top.splitlines() if any(x in l for x in ['PID','aiperf','benchmark.load','vllm','VLLM'])])
 if name.startswith('inferoptlab-scan-'):
  logs=subprocess.run(['docker','logs','--tail','35',name],capture_output=True,text=True,timeout=20)
  out['containers'][name]['logs']=(logs.stdout+logs.stderr)[-9000:]
try:
 with urllib.request.urlopen('http://127.0.0.1:18082/metrics',timeout=8) as response:metrics=response.read().decode()
 names=('vllm:num_requests_running','vllm:num_requests_waiting','vllm:request_success_total','vllm:generation_tokens_total','vllm:prompt_tokens_total')
 out['metrics']=[l for l in metrics.splitlines() if l.startswith(names)]
except Exception as e:out['metrics_error']=str(e)
if v.get('current_trial'):
 warmup=v['current_trial'].get('phase')=='warmup'
 p=b/v['current_trial']['directory']/('raw/warmup' if warmup else 'raw/aiperf')
 out['artifacts']=[dict(name=str(x.relative_to(p)),size=x.stat().st_size) for x in p.glob('*.jsonl')]
 raw=p/'profile_export.jsonl'
 if raw.exists():
  rows=[];partial=0
  for line in raw.read_text().splitlines():
   if not line.strip():continue
   try:rows.append(json.loads(line))
   except json.JSONDecodeError:partial+=1
  record=json.loads((p.parent.parent/'run.json').read_text())
  out['current_request_progress']=dict(scope='warmup' if warmup else 'scoring',
    planned=record['dataset_manifest']['files']['warmup.jsonl' if warmup else 'requests.jsonl']['count'],
    exported=len(rows),errors=sum(bool(x.get('error')) for x in rows),partial_lines=partial,
    missing_token_counts=sum(any(x.get('metrics',{}).get(k,{}).get('value') is None for k in ['input_sequence_length','output_sequence_length']) for x in rows))
print(json.dumps(out))
'''
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(4):
    try:
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],
                         capture_output=True,text=True,encoding='utf-8',timeout=55)
        if p.returncode:
            print('SSH observation retry',attempt,p.stderr,flush=True);continue
        v=json.loads(p.stdout)
        Path(__file__).with_name('last-live-health.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
        report={k:v.get(k) for k in ['at','stage','current','current_request_progress','metrics_error']} if '--compact' in sys.argv else v
        print(json.dumps(report),flush=True);break
    except subprocess.TimeoutExpired:
        print('Observation timeout; remote job unchanged',flush=True)
else:
    raise SystemExit('LIVE_OBSERVATION_UNAVAILABLE: cached data is not a new observation')
