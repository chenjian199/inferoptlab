import json
from pathlib import Path
import shlex
import subprocess
import sys

name=sys.argv[1] if len(sys.argv)>1 else 'glm53-sparse-prefill-diagnosis-r2-20261125'
code=f'''import pathlib,json,subprocess
d=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124/experiments/evidence')/{name!r}
s=json.loads((d/'state.json').read_text());p=pathlib.Path('/proc')/str(s['pid'])/'cmdline'
v=dict(state=s,live=p.exists() and b'run_diagnostic.py' in p.read_bytes(),controller=(d/'controller.log').read_text()[-1200:])
v['diagnostic_calls']=[json.loads(p.read_text()) for p in (d/'evidence').glob('last-*.json')]
v['invalid']=[json.loads(p.read_text()) for p in (d/'evidence').glob('invalid-*.json')]
v['containers']=subprocess.run(['docker','ps','--format','{{{{.Names}}}} {{{{.Status}}}}'],capture_output=True,text=True).stdout
if 'server_name' in s:
 p=subprocess.run(['docker','logs','--tail','12',s['server_name']],capture_output=True,text=True);v['server_tail']=p.stdout+p.stderr
print(json.dumps(v))
'''
for _ in range(4):
    try:
        p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8',
          '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2','metax-60',
          'python3 -c '+shlex.quote(code)],capture_output=True,text=True,timeout=40)
        if p.returncode==0:
            value=json.loads(p.stdout)
            (Path(__file__).parent/(name+'-status.json')).write_text(p.stdout,encoding='utf-8')
            print(json.dumps(value),flush=True)
            break
        print(p.stderr,flush=True)
    except subprocess.TimeoutExpired:
        print('SSH observation timeout; retry',flush=True)
