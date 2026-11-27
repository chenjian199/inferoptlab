"""Replace the completed owned preflight with an observed preflight."""
import json
from pathlib import Path
import shlex
import subprocess

out=Path(__file__).resolve().parent
code='''
import json,pathlib,subprocess
root=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
out=root/'experiments/evidence/glm53-cached-decode-20261126'
receipt=out/'observed-launch.json'
if receipt.exists():print(receipt.read_text());raise SystemExit()
old=json.loads((out/'preflight-launch.json').read_text())
info=json.loads(subprocess.check_output(['docker','inspect',old['id']]))[0]
assert info['Config']['Labels']['io.inferoptlab.role']=='cached-decode-preflight'
log=subprocess.run(['docker','logs',old['id']],capture_output=True)
(out/'preflight-server.log').write_bytes(log.stdout+log.stderr)
subprocess.run(['docker','stop','--time','20',old['id']],check=True,stdout=subprocess.DEVNULL)
observations=out/'observations-tp8';observations.mkdir(exist_ok=True)
cmd=old['command'];cmd[cmd.index('--name')+1]='inferoptlab-cached-decode-tp8-observed'
i=cmd.index('--entrypoint')
cmd[i:i]=['-v',str(out/'hooks')+':/inferoptlab-observers:ro','-v',str(observations)+':/inferoptlab-observations',
 '-e','PYTHONPATH=/inferoptlab-observers','-e','INFEROPTLAB_DECODE_OBSERVATIONS=/inferoptlab-observations']
cid=subprocess.check_output(cmd,text=True).strip()
data=dict(id=cid,command=cmd);receipt.write_text(json.dumps(data,indent=2));print(json.dumps(data))
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -c '+shlex.quote(code)],capture_output=True,timeout=60)
if r.returncode:raise SystemExit(r.stderr.decode(errors='replace'))
value=json.loads(r.stdout);(out/'observed-launch.json').write_text(json.dumps(value,indent=2),encoding='utf-8')
print(value['id'])
