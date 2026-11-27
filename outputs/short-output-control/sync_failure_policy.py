"""Atomically publish tested failure policy for future child processes only."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

root='/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124'
files=['benchmark/load/checkpoint.py','benchmark/load/qualification.py','benchmark/load/runner.py',
       'tools/deployment/metax-vllm/supervise_scan.py','recipes/plans/benchmark/glm53-vllm/DECODE.md']
payload={name:Path(name).read_text(encoding='utf-8') for name in files}
transfer=Path(__file__).with_name('failure-policy-code.json')
transfer.write_text(json.dumps(payload,ensure_ascii=True),encoding='utf-8')
fingerprint=hashlib.sha256(transfer.read_bytes()).hexdigest()
remote_payload=root+'/experiments/evidence/failure-policy-code-upload.json'
code='ROOT='+repr(root)+'\nTRANSFER='+repr(remote_payload)+'\nSHA='+repr(fingerprint)+'\n'+r'''
import pathlib,hashlib,json,os,datetime
data=pathlib.Path(TRANSFER).read_bytes();assert hashlib.sha256(data).hexdigest()==SHA
PAYLOAD=json.loads(data)
r=pathlib.Path(ROOT);result={}
for name,source in PAYLOAD.items():
 p=r/name
 assert p.resolve().is_relative_to(r.resolve())
 if p.suffix=='.py':compile(source,name,'exec')
 data=source.encode('utf-8');temp=p.with_suffix(p.suffix+'.policy-update')
 temp.write_bytes(data);os.replace(temp,p)
 result[name]=hashlib.sha256(p.read_bytes()).hexdigest()
receipt=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=result,
             action='Future process code updated; no running process restarted')
(r/'experiments/evidence/glm53-five-layout-extension-20261125/failure-policy-code.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
'''
opts=['-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
for attempt in range(6):
    try:
        transfer_result=subprocess.run(['scp',*opts,str(transfer),'metax-60:'+remote_payload],capture_output=True,text=True,encoding='utf-8',timeout=45)
        if transfer_result.returncode:
            print(transfer_result.stderr,flush=True);continue
        p=subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],
                         capture_output=True,text=True,encoding='utf-8',timeout=50)
        if p.returncode==0:
            receipt=json.loads(p.stdout)
            assert receipt['files']=={k:hashlib.sha256(v.encode('utf-8')).hexdigest() for k,v in payload.items()}
            Path(__file__).with_name('failure-policy-sync.json').write_text(p.stdout,encoding='utf-8')
            print(p.stdout);break
        print(p.stderr,flush=True)
        if p.returncode!=255:raise SystemExit(p.returncode)
    except subprocess.TimeoutExpired:print('VPN timeout; retry publish',attempt,flush=True)
else:raise SystemExit('Remote publication not confirmed')
