"""Apply the isolated client hook fix with an auditable before/after receipt."""
import base64,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
payload=base64.b64encode((root/'benchmark/load/aiperf_hooks/sitecustomize.py').read_bytes()).decode()
script=r'''
import base64,json,hashlib,datetime,subprocess
from pathlib import Path
root=Path('/home/ubuntu/CJ_workspace/inferoptlab-matrix-20261127')
p=root/'benchmark/load/aiperf_hooks/sitecustomize.py'
identity=root/'experiments/runs/glm53-matrix/identity.json'
record=json.loads(identity.read_text())
before=p.read_bytes();after=base64.b64decode(PAYLOAD)
receipt=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(p),
 before=hashlib.sha256(before).hexdigest(),after=hashlib.sha256(after).hexdigest(),
 reason='AIPerf offline resolver incorrectly sends existing local tokenizer path to Hub snapshot_download; no model or workload change')
assert record['code']['benchmark/load/aiperf_hooks/sitecustomize.py']==receipt['before']
backup=identity.with_name('identity-before-tokenizer-fix.json')
assert not backup.exists()
backup.write_bytes(identity.read_bytes())
p.write_bytes(after)
record['code']['benchmark/load/aiperf_hooks/sitecustomize.py']=receipt['after']
identity.write_text(json.dumps(record,indent=2))
(root/'experiments/runs/glm53-matrix/tokenizer-fix.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
'''
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -'],input=('PAYLOAD='+repr(payload)+'\n'+script).encode(),capture_output=True,timeout=60)
print(p.stdout.decode());print(p.stderr.decode());p.check_returncode()
Path(__file__).with_name('tokenizer-fix.json').write_text(p.stdout.decode(),encoding='utf-8')
