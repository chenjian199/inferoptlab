"""Independent read-only checks of the requested matrix and completed artifacts."""
import json
import argparse
from pathlib import Path
import shlex
import subprocess

REMOTE=r'''
import json,pathlib,sys,itertools,hashlib,math,datetime
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
sys.path[:0]=[str(r/'.host-deps'),str(r)]
from tools.specs import Catalog
from benchmark.load.cli import load_snapshot
from benchmark.load.planner import embedded_catalog,scenario_parts
stage_path={'original':'glm53-short-output-continue-failures-20261125/state.json',
            'additional':'glm53-five-layout-extension-20261125/scan/state.json'}[STAGE]
layouts={'original':{'glm53-vllm-decode-tp2-dp4-ep8':(2,4,8,1),'glm53-vllm-decode-tp4-dp2-ep8':(4,2,8,1)},
         'additional':{'glm53-vllm-decode-tp8':(8,1,1,1),'glm53-vllm-decode-tp8-ep8':(8,1,8,1),'glm53-vllm-decode-tp1-dp8-ep8':(1,8,8,1)}}[STAGE]
point_count=len(layouts)*3*2*8*3
state_path=r/'experiments/evidence'/stage_path
if not state_path.exists() or not json.loads(state_path.read_text()).get('batch'):
 print(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=STAGE,status='not_started',matrix_points=point_count,audited_completed=0,accounted_points=0,batch_complete=False)))
 raise SystemExit(0)
s=json.loads(state_path.read_text())
b=pathlib.Path(s['batch']);state=json.loads((b/'batch.json').read_text())
c=Catalog(r);c.load();snapshot=load_snapshot(c,b/'resolved.yaml');c=embedded_catalog(c,snapshot)
expected=set(itertools.product(layouts,[4096,16384,65536],[20,50],[1,2,4,8,16,32,64,128],[1,2,3]))
actual=[];trials={};audited=[]
for t in snapshot['trials']:
 scene,case,w,protocol=scenario_parts(c,t['scenario_ref'])
 dep=c.get(t['deployment_ref']);parallel=dep['parallelism']
 assert (parallel['tp'],parallel['dp'],parallel['ep'],parallel['pp'])==layouts[dep['id']]
 assert w['requests'].get('count_multiplier')==4 and 'min_count' not in w['requests']
 assert protocol['scope']=='decode' and protocol['method']=='full_request'
 value=(t['deployment_ref']['id'],w['input']['tokens'],w['output']['tokens'],t['concurrency'],t['repetition'])
 actual.append(value);trials[(t['id'],t['repetition'])]=(t,w)
assert len(actual)==point_count and set(actual)==expected,'matrix differs from requested points'
assert len(trials)==point_count and len(state['runs'])==point_count
assert len({(x['trial_id'],x['repetition']) for x in state['runs']})==point_count
from benchmark.load.checkpoint import load,exclusions,terminal
load(b,snapshot)
selected,fingerprint=exclusions(b,snapshot)
expected_skips={('glm53-vllm-decode-tp2-dp4-ep8',4096,50,128,i) for i in (1,2,3)} if STAGE=='original' else set()
actual_skips=set()
for identity in selected:
 t,w=trials[identity]
 actual_skips.add((t['deployment_ref']['id'],w['input']['tokens'],w['output']['tokens'],t['concurrency'],t['repetition']))
assert actual_skips==expected_skips
assert sum(x['status']=='skipped_by_user' for x in state['runs'])==len(expected_skips)
for row in state['runs']:
 if row['status']!='completed':continue
 t,w=trials[(row['trial_id'],row['repetition'])];p=b/row['directory'];n=4*t['concurrency']
 record=json.loads((p/'run.json').read_text());summary=json.loads((p/'summary.json').read_text())
 assert record['status']=='completed' and not record['environment_issues']
 assert summary['validity']=='valid' and summary['counts']==dict(planned=n,observed=n,succeeded=n,failed=0,missing=0)
 raw=(p/'raw/aiperf/profile_export.jsonl').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==summary['raw_sha256']
 native=[json.loads(x) for x in raw.splitlines() if x.strip()]
 assert len(native)==n
 ids=record['dataset_manifest']['files']['requests.jsonl']['session_ids']
 assert set(x['metadata']['conversation_id'] for x in native)==set(ids)
 for x in native:
  assert not x.get('error')
  assert x['metrics']['input_sequence_length']['value']==w['input']['tokens']
  assert x['metrics']['output_sequence_length']['value']==w['output']['tokens']
 records=[json.loads(x) for x in (p/'requests.jsonl').read_text().splitlines() if x.strip()]
 assert len(records)==n and all(x['status']=='success' for x in records)
 measured=[(x['e2e_latency']-x['ttft'])/(x['output_tokens']-1) for x in records]
 decode=json.loads((p/'decode.json').read_text())
 assert decode['eligible_for_performance_comparison'] and decode['tpot_ms']['count']==n
 assert math.isclose(decode['tpot_ms']['mean'],sum(measured)/n,rel_tol=1e-10)
 commands=json.loads((p/'commands.json').read_text());a=commands['aiperf']
 assert int(a[a.index('--request-count')+1])==n and int(a[a.index('--concurrency')+1])==t['concurrency']
 assert 'max_tokens:'+str(w['output']['tokens']) in a and 'min_tokens:'+str(w['output']['tokens']) in a
 warm=json.loads((p/'warmup-summary.json').read_text())
 assert warm['validity']=='valid' and warm['counts']['succeeded']==max(4,t['concurrency']) and warm['counts']['failed']==0
 audited.append(dict(directory=row['directory'],deployment=row['deployment'],input=w['input']['tokens'],output=w['output']['tokens'],concurrency=t['concurrency'],repetition=t['repetition'],requests=n,raw_sha256=summary['raw_sha256']))
from collections import Counter
accounted=sum(terminal(row,state) for row in state['runs'])
print(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=STAGE,snapshot_sha256=snapshot['content_sha256'],batch=str(b),matrix_points=point_count,user_excluded=len(expected_skips),exclusions_sha256=fingerprint,status_counts=dict(Counter(x['status'] for x in state['runs'])),accounted_points=accounted,audited_completed=len(audited),audited_requests=sum(x['requests'] for x in audited),batch_complete=accounted==point_count and state['status'] in {'completed','completed_with_skips','finished_with_failures'},runs=audited)))
'''

def audit(stage):
    for attempt in range(4):
        try:
            result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',
                       '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2',
                       'metax-60','python3 -c '+shlex.quote('STAGE='+repr(stage)+'\n'+REMOTE)],
                       capture_output=True,text=True,encoding='utf-8',timeout=60)
        except subprocess.TimeoutExpired:
            continue
        if result.returncode==0:
            value=json.loads(result.stdout)
            filename='completed-audit.json' if stage=='original' else 'additional-completed-audit.json'
            (Path(__file__).parent/filename).write_text(json.dumps(value,indent=2),encoding='utf-8')
            print(json.dumps({k:v for k,v in value.items() if k!='runs'}))
            return value
        print(result.stderr,flush=True)
        if result.returncode!=255:
            raise SystemExit(result.returncode)
    else:
        raise SystemExit('audit observation unavailable; no completion claim')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=['original','additional','all'],default='original')
    args=parser.parse_args()
    if args.stage!='all':audit(args.stage)
    else:
        stages=[audit(stage) for stage in ['original','additional']]
        report=dict(scope='five_layout_campaign',matrix_points=sum(s['matrix_points'] for s in stages),
                    completed=sum(s['audited_completed'] for s in stages),
                    accounted=sum(s['accounted_points'] for s in stages),
                    campaign_complete=all(s['batch_complete'] for s in stages),
                    stages=[{k:v for k,v in s.items() if k!='runs'} for s in stages])
        assert report['matrix_points']==720
        (Path(__file__).parent/'campaign-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report))
