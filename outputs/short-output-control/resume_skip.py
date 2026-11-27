"""Resume the archived scan after the user's explicit single-config exclusion."""
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import tarfile

ROOT = '/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124'
NAME = 'glm53-short-output-skip-c128-20261125'
FILES = ['benchmark/load/checkpoint.py', 'benchmark/load/runner.py',
         'benchmark/load/cli.py', 'tools/experiments.py',
         'tools/deployment/metax-vllm/supervise_scan.py']
opts = ['-o','BatchMode=yes','-o','ConnectTimeout=8',
        '-o','ServerAliveInterval=5','-o','ServerAliveCountMax=2']
archive = Path(__file__).with_name('skip-resume-code.tar.gz')
with tarfile.open(archive, 'w:gz') as tar:
    for name in FILES:
        tar.add(name, arcname=name)
fingerprint = hashlib.sha256(archive.read_bytes()).hexdigest()

code = r'''
import hashlib,json,os,pathlib,subprocess,sys,tarfile,datetime
r=pathlib.Path(ROOT)
sys.path[:0]=[str(r/'.host-deps'),str(r)]
receipt=r/'experiments/evidence'/ (NAME+'.launch.json')
if receipt.exists():
 print(receipt.read_text());sys.exit(0)
assert not (r/'experiments/runs/benchmark/.execution.lock').exists(), 'existing execution lease'
old=r/'experiments/evidence/glm53-short-output-supervised-20261125'
s=json.loads((old/'state.json').read_text())
p=pathlib.Path('/proc')/str(s['pid'])/'cmdline'
assert not p.exists() or b'supervise_scan.py' not in p.read_bytes(), 'old supervisor still active'
containers=subprocess.run(['docker','ps','--filter','label=io.inferoptlab.role=benchmark-client','--format','{{.Names}}'],capture_output=True,text=True,check=True).stdout
assert not containers.strip(),containers
build=subprocess.run(['docker','ps','--filter','label=io.inferoptlab.role=flashmla-offset64-build','--format','{{.Names}}'],capture_output=True,text=True,check=True).stdout
assert not build.strip(), 'experimental build still active: '+build
archive=r/'experiments/evidence'/ (NAME+'.code.tar.gz')
assert hashlib.sha256(archive.read_bytes()).hexdigest()==FINGERPRINT
with tarfile.open(archive) as tar:
 assert sorted(tar.getnames())==sorted(FILES)
 for member in tar.getmembers():
  assert member.isfile()
  dest=r/member.name
  assert dest.resolve().is_relative_to(r.resolve())
  tmp=dest.with_suffix(dest.suffix+'.skip-update')
  tmp.write_bytes(tar.extractfile(member).read());os.replace(tmp,dest)
from tools.specs import read
from benchmark.load.checkpoint import load,exclusions
b=pathlib.Path(s['batch']);snapshot=read(b/'resolved.yaml')
state=load(b,snapshot)
selected=[dict(trial_id=t['id'],repetition=t['repetition']) for t in snapshot['trials']
 if t['deployment_ref']['id']=='glm53-vllm-decode-tp2-dp4-ep8'
 and t['scenario_ref']['id']=='glm53-vllm-decode-4k-50' and t['concurrency']==128]
assert len(selected)==3 and {x['repetition'] for x in selected}=={1,2,3},selected
path=b/'exclusions.json'
requested_at=json.loads(path.read_text())['requested_at'] if path.exists() else datetime.datetime.now(datetime.timezone.utc).isoformat()
directive=dict(plan_sha256=snapshot['content_sha256'],requested_by='user',
 requested_at=requested_at,
 reason='User requested skipping the failing TP2/DP4/EP8, input 4096, output 50, concurrency 128 configuration and continuing other points; all three repetitions excluded.',
 trials=selected)
if path.exists():assert json.loads(path.read_text())==directive
else:
 with path.open('x') as f:json.dump(directive,f,indent=2)
exclusions(b,snapshot)
old_launch=json.loads((r/'experiments/evidence/glm53-short-output-supervised-20261125.launch.json').read_text())
command=old_launch['command']
command[command.index('--plan')+1]=str(b/'resolved.yaml')
command[command.index('--state-dir')+1]=str(r/'experiments/evidence'/NAME)
command+=['--resume',str(b)]
env=dict(os.environ,PYTHONPATH=str(r/'.host-deps')+':'+str(r),PATH='/opt/mxdriver/bin:/opt/maca/bin:'+os.environ['PATH'])
logpath=r/'experiments/evidence'/(NAME+'.log')
with receipt.open('x') as f:
 with logpath.open('x') as log:
  child=subprocess.Popen(command,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 value=dict(pid=child.pid,command=command,log=str(logpath),excluded=selected,
            completed_before=sum(e['status']=='completed' for e in state['runs']),
            code_sha256=FINGERPRINT,launched_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
 json.dump(value,f,indent=2);print(json.dumps(value))
'''
code = 'ROOT='+repr(ROOT)+'\nNAME='+repr(NAME)+'\nFILES='+repr(FILES)+'\nFINGERPRINT='+repr(fingerprint)+'\n'+code
for attempt in range(12):
    try:
        result = subprocess.run(['scp',*opts,str(archive),f'metax-60:{ROOT}/experiments/evidence/{NAME}.code.tar.gz'],
                                capture_output=True,text=True,encoding='utf-8',timeout=45)
        if result.returncode:
            print('VPN transfer retry', attempt, result.stderr, flush=True);continue
        result = subprocess.run(['ssh',*opts,'metax-60','python3 -c '+shlex.quote(code)],
                                capture_output=True,text=True,encoding='utf-8',timeout=45)
        print(result.stdout,result.stderr,flush=True)
        if result.returncode==0:
            Path(__file__).with_name('skip-resume-launch.json').write_text(result.stdout,encoding='utf-8')
            break
        if result.returncode!=255:
            raise SystemExit(result.returncode)
    except subprocess.TimeoutExpired:
        print('VPN observation timeout; retry idempotent launch',attempt,flush=True)
else:
    raise SystemExit('Remote launch not confirmed')
