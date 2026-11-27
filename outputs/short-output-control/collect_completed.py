"""Copy terminal point evidence without touching a live test or its growing logs."""
import base64
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage', choices=['original', 'additional'], default='original')
args = parser.parse_args()
state_file = {
    'original': 'experiments/evidence/glm53-short-output-continue-failures-20261125/state.json',
    'additional': 'experiments/evidence/glm53-five-layout-extension-20261125/scan/state.json',
}[args.stage]
target=Path('experiments/evidence') / ('glm53-short-output-collected-20261125' if args.stage=='original' else 'glm53-additional-output-collected-20261125')

def collections_of(value):
    return [value['files'],*[row['files'] for row in value['runs']+value.get('historical_runs',[])]]

cache={}
if (target/'latest.json').exists():
    previous=json.loads((target/'latest.json').read_text(encoding='utf-8'))
    payload=Path(previous['path']).read_bytes()
    assert hashlib.sha256(payload).hexdigest()==previous['sha256'],'local base archive hash mismatch'
    base=json.loads(gzip.decompress(payload))
    assert base.get('stage','original')==args.stage
    for collection in collections_of(base):
        for item in collection.values():
            assert hashlib.sha256(item['text'].encode('utf-8')).hexdigest()==item['sha256']
            cache[item['sha256']]=item['text']

REMOTE=r'''
import base64,gzip,hashlib,json,pathlib,datetime,sys
known=set(json.load(sys.stdin))
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
s=json.loads((r/STATE_FILE).read_text())
b=pathlib.Path(s['batch']);ledger=json.loads((b/'batch.json').read_text())
result=dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),host='metax-60',batch=str(b),
 scope='terminal point core evidence; fixtures and shared live server logs remain in the remote archive',
 stage=STAGE,ledger=ledger,files={},runs=[],historical_runs=[])
def capture(path):
 raw=path.read_bytes()
 sha=hashlib.sha256(raw).hexdigest()
 return dict(sha256=sha,cached=True) if sha in known else dict(sha256=sha,text=raw.decode('utf-8'))
for name in ['resolved.yaml','exclusions.json','qualification.json']:
 if (b/name).exists():result['files'][name]=capture(b/name)
names=['run.json','resolved.yaml','summary.json','decode.json','sla.json','requests.jsonl',
 'warmup-summary.json','environment.json','commands.json',
 'raw/aiperf/profile_export.jsonl','raw/aiperf/profile_export_aiperf.json',
 'raw/warmup/profile_export.jsonl','raw/warmup/profile_export_aiperf.json']
for entry in ledger['runs']:
 if not entry.get('directory') or entry['status'] not in {'completed','failed','invalid','unverified','completed_with_errors','skipped_by_user'}:continue
 p=b/entry['directory'];record=json.loads((p/'run.json').read_text())
 if record['status'] not in {'completed','failed','invalid','unverified','completed_with_errors'}:continue
 item=dict(ledger_entry=entry,files={})
 for name in names:
  if (p/name).exists():item['files'][name]=capture(p/name)
 if entry['status']=='completed':
  summary=json.loads((p/'summary.json').read_text())
  assert record['status']=='completed' and summary['validity']=='valid'
  assert item['files']['raw/aiperf/profile_export.jsonl']['sha256']==summary['raw_sha256']
 result['runs'].append(item)
captured={item['ledger_entry']['directory'] for item in result['runs']}
for entry in ledger['runs']:
 for attempt in entry.get('attempts',[]):
  directory=attempt.get('directory')
  if not directory or directory in captured:continue
  p=b/directory
  assert p.resolve().is_relative_to(b.resolve())
  record=json.loads((p/'run.json').read_text())
  if record['status'] not in {'completed','failed','invalid','unverified','completed_with_errors','interrupted'}:continue
  item=dict(ledger_entry=attempt,files={})
  for name in names:
   if (p/name).exists():item['files'][name]=capture(p/name)
  result['historical_runs'].append(item);captured.add(directory)
payload=gzip.compress(json.dumps(result,ensure_ascii=False).encode('utf-8'))
print(base64.b64encode(payload).decode('ascii'))
'''
REMOTE='STATE_FILE='+repr(state_file)+'\nSTAGE='+repr(args.stage)+'\n'+REMOTE

opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(6):
    try:
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(REMOTE)],
                         input=json.dumps(list(cache)),capture_output=True,text=True,encoding='utf-8',timeout=60)
        if p.returncode:
            print('Read-only collection retry',attempt,p.stderr,flush=True);continue
        compressed=base64.b64decode(p.stdout,validate=False)
        transferred_bytes=len(compressed)
        value=json.loads(gzip.decompress(compressed))
        assert value['stage']==args.stage
        count=0;reused=0
        for collection in collections_of(value):
            for name,item in collection.items():
                if item.pop('cached',False):
                    item['text']=cache[item['sha256']]
                    reused+=1
                assert hashlib.sha256(item['text'].encode('utf-8')).hexdigest()==item['sha256'],name
                count+=1
        # Every persisted archive is self-contained; transport references never remain.
        compressed=gzip.compress(json.dumps(value,ensure_ascii=False).encode('utf-8'))
        target.mkdir(exist_ok=True)
        stamp=value['captured_at'].replace(':','').replace('-','').replace('+0000','Z')
        archive=target/(stamp+'.json.gz')
        with archive.open('xb') as stream:stream.write(compressed)
        receipt=dict(stage=args.stage,captured_at=value['captured_at'],batch=value['batch'],path=str(archive),
                     sha256=hashlib.sha256(compressed).hexdigest(),bytes=len(compressed),verified_files=count,
                     completed_points=sum(row['ledger_entry']['status']=='completed' for row in value['runs']),
                     retained_failed_points=sum(row['ledger_entry']['status']!='completed' for row in value['runs']),
                     historical_attempts=len(value['historical_runs']),
                     transferred_bytes=transferred_bytes,reused_files=reused)
        (target/'latest.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
        print(json.dumps(receipt),flush=True);break
    except subprocess.TimeoutExpired:
        print('Observation timeout; live run unchanged',flush=True)
else:
    raise SystemExit('Collection not confirmed; remote evidence remains authoritative')
