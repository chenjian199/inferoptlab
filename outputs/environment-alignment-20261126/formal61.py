import hashlib,json
from pathlib import Path
root=Path('/tmp/lyq-cached061-formal')
names={'state.json','snapshot.json','launch.json','server-info.json','server.log','profile_export_aiperf.json',
       'profile_export.jsonl','engine-verification.json','profile-verification.json','command.json','qualification.json'}
rows=[]
if root.exists():
 for p in root.rglob('*'):
  if not p.is_file():continue
  if p.name not in names and p.name not in {'cached_decode.py','sitecustomize.py'}:continue
  if any(part in {'.git','.venv','venv','__pycache__'} for part in p.relative_to(root).parts):continue
  b=p.read_bytes();text=b.decode('utf-8',errors='replace')
  if len(b)>2000000:text=text[:150000]+'\n[TRUNCATED]\n'+text[-100000:]
  rows.append(dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),text=text,truncated=len(b)>2000000))
print(json.dumps(dict(exists=root.exists(),files=rows)))
