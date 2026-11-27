PATHS=['/data/glm53/work/evidence/native_installed_versions.json', '/data/glm53/work/evidence/native_wheel_manifest.json', '/data/glm53/work/evidence/packages_after_build.json', '/data/glm53/work/evidence/packages_before_build.json', '/data/glm53/work/evidence/sdk_sha256.txt', '/data/glm53/work/scripts/check_gpu8.py', '/data/glm53/work/scripts/infer_smoke.py', '/data/glm53/work/scripts/install_frameworks.py', '/data/glm53/work/scripts/install_native.py', '/data/glm53/work/scripts/install_sdk.py', '/data/glm53/work/scripts/stage_sdk.py', '/data/glm53/work/scripts/worker_provenance.py', '/home/ubuntu/LYQ_workspace/cached-decode-061-progress/README.md', '/home/ubuntu/LYQ_workspace/cached-decode-061-results/TP8.md', '/home/ubuntu/LYQ_workspace/cached-decode-061-results/state.json', '/home/ubuntu/LYQ_workspace/cached-decode-061-validation/off/qualification.json', '/home/ubuntu/LYQ_workspace/cached-decode-061-validation/on/qualification.json', '/home/ubuntu/LYQ_workspace/cached-decode-061-validation/summary.json']
import json,hashlib
from pathlib import Path
rows=[]
for name in PATHS:
 p=Path(name)
 if not p.is_file():continue
 b=p.read_bytes();text=b.decode('utf-8',errors='replace')
 if len(b)>2000000:text=text[:150000]+'\n[TRUNCATED]\n'+text[-100000:]
 rows.append(dict(path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),text=text,truncated=len(b)>2000000))
print(json.dumps(rows,ensure_ascii=False))
