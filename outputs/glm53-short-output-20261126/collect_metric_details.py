"""Read-only copy of completed-point server metrics for the Markdown snapshot."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
receipt = json.loads((ROOT / 'experiments/evidence/glm53-short-output-collected-20261125/latest.json').read_text())
raw = (ROOT / receipt['path']).read_bytes()
assert hashlib.sha256(raw).hexdigest() == receipt['sha256']
source = json.loads(gzip.decompress(raw))
runs = [r['ledger_entry']['directory'] for r in source['runs'] if r['ledger_entry']['status'] == 'completed']
remote = r'''
import base64,datetime,gzip,hashlib,json,pathlib,sys
request=json.load(sys.stdin);b=pathlib.Path(request['batch']);files={};missing=[]
for run in request['runs']:
 p=b/run
 assert p.resolve().is_relative_to(b.resolve())
 assert json.loads((p/'run.json').read_text())['status']=='completed'
 for phase in ['aiperf','warmup']:
  for name in ['server_metrics_export.json','gpu_telemetry_export.jsonl']:
   f=p/'raw'/phase/name;key=str(f.relative_to(b))
   if not f.exists():missing.append(key);continue
   raw=f.read_bytes();files[key]=dict(sha256=hashlib.sha256(raw).hexdigest(),text=raw.decode())
out=dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=request['source_sha256'],files=files,missing=missing)
print(base64.b64encode(gzip.compress(json.dumps(out).encode())).decode())
'''
for attempt in range(6):
    try:
        p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', '-o', 'ServerAliveInterval=5', '-o', 'ServerAliveCountMax=2', 'metax-60', 'python3 -c ' + shlex.quote(remote)], input=json.dumps(dict(batch=source['batch'],runs=runs,source_sha256=receipt['sha256'])), capture_output=True, text=True, encoding='utf-8', timeout=60)
        if p.returncode:
            print('Read-only retry', attempt, p.stderr, flush=True)
            continue
        compressed = base64.b64decode(p.stdout)
        data = json.loads(gzip.decompress(compressed))
        assert data['source_sha256'] == receipt['sha256']
        for item in data['files'].values():
            assert hashlib.sha256(item['text'].encode()).hexdigest() == item['sha256']
        dest = OUT / 'metric-details.json.gz'
        dest.write_bytes(compressed)
        (OUT / 'markdown-source.json').write_text(json.dumps(dict(core=receipt,details=dict(path=str(dest.relative_to(ROOT)),sha256=hashlib.sha256(compressed).hexdigest(),files=len(data['files']),missing=len(data['missing']))),indent=2),encoding='utf-8')
        print(json.dumps(dict(path=str(dest),bytes=len(compressed),files=len(data['files']),missing=len(data['missing']))))
        break
    except subprocess.TimeoutExpired:
        print('Read-only transfer timed out; retrying', flush=True)
else:
    raise SystemExit('Metrics collection not confirmed')
