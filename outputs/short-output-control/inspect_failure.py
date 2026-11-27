"""Capture the latest failed point and its shared serving-log failure context."""
import json
from pathlib import Path
import shlex
import subprocess

code=r'''
import json,pathlib,datetime
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
s=json.loads((r/'experiments/evidence/glm53-short-output-continue-failures-20261125/state.json').read_text())
b=pathlib.Path(s['batch']);state=json.loads((b/'batch.json').read_text())
result=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),failures=[],server_errors=[])
for row in state['runs']:
 if row['status']!='failed':continue
 p=b/row['directory'];item=dict(ledger=row,record=json.loads((p/'run.json').read_text()))
 if (p/'warmup-summary.json').exists():item['warmup']=json.loads((p/'warmup-summary.json').read_text())
 raw=p/'raw/warmup/profile_export.jsonl'
 if raw.exists():
  native=[json.loads(x) for x in raw.read_text().splitlines() if x.strip()]
  item['request_errors']=[dict(id=x.get('metadata',{}).get('conversation_id'),error=x.get('error')) for x in native if x.get('error')][:8]
 item['warmup_log_tail']=(p/'logs/warmup.log').read_text(errors='replace')[-3500:]
 result['failures'].append(item)
for log in b.glob('run-*/logs/server.log'):
 if log.stat().st_size==0:continue
 with log.open('rb') as f:
  f.seek(max(0,log.stat().st_size-400000));lines=f.read().decode(errors='replace').splitlines()
 hits=[i for i,line in enumerate(lines) if any(x in line for x in ['Xnack','ATU','RuntimeError','FATAL','Error while','Traceback'])]
 if hits:
  primary=[i for i,line in enumerate(lines) if any(x in line for x in ['Xnack','ATU','sparse_attn_global','illegal memory access'])]
  selected=list(dict.fromkeys(primary[:12]+hits[-3:]))
  result['server_errors'].append(dict(path=str(log),contexts=['\n'.join(lines[max(0,i-2):i+9]) for i in selected]))
print(json.dumps(result))
'''
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(6):
    try:
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],capture_output=True,text=True,encoding='utf-8',timeout=45)
        if p.returncode:
            print('Retry',attempt,p.stderr,flush=True);continue
        v=json.loads(p.stdout)
        Path(__file__).with_name('latest-failure.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
        for row in v['failures']:
            row['record']={k:row['record'].get(k) for k in ['id','status','error','created_at','finished_at']}
            row['warmup']={k:row.get('warmup',{}).get(k) for k in ['counts','validity','issues']}
            row['warmup']['issues']=row['warmup'].get('issues',[])[:4]
            row.pop('warmup_log_tail',None)
        print(json.dumps(v),flush=True);break
    except subprocess.TimeoutExpired:print('VPN timeout; retry observation',flush=True)
else:raise SystemExit('Failure observation unavailable')
