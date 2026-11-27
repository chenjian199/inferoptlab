import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import time

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('hosts',nargs='*',default=['60','61','64','65']);args=parser.parse_args()
code=(root/'probe_inventory.py').read_bytes()
def collect(host):
    for attempt in range(3):
        try:
            result=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5',
                '-o','ServerAliveCountMax=2','metax-'+host,'python3 -'],input=code,capture_output=True,timeout=150)
            if result.returncode:
                raise RuntimeError(result.stderr.decode(errors='replace'))
            data=json.loads(result.stdout)
            (root/f'{host}-inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            return dict(host=host,containers=[dict(name=c['name'],running=c['state']['Running'],image=c['image_id'][:24]) for c in data['containers']],
                        models=[m['path'] for m in data['model_metadata']],workspace_dirs=data['workspace_dirs'])
        except Exception as exc:
            if attempt==2:return dict(host=host,error=repr(exc))
            time.sleep(2)
with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(collect,args.hosts):print(json.dumps(result,ensure_ascii=False),flush=True)
