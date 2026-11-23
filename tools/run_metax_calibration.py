"""Run bounded GPU0 microbenchmarks in an existing MACA container after idle checks.

Host mx-smi is used because containers may lack a working management interface.
The container and its services are not restarted or changed. Results are diagnostic;
the advisory lock prevents concurrent invocations of this tool only.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='metax')
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--container')
    target.add_argument('--image', help='Create and remove an isolated container from a local image ID')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.host.startswith('-') or (args.container or args.image).startswith('-'):
        parser.error('host/container cannot start with a dash')
    if args.out.exists():
        parser.error('output exists; use a new file for every attempt')
    probe = (Path(__file__).parent / 'hardware/probes/torch_bench.py').read_bytes()
    remote = '''import base64,fcntl,json,subprocess,re,datetime,uuid
container = CONTAINER
image = IMAGE
probe = base64.b64decode(PROBE)
lock = open('/tmp/inferoptlab-c500-calibration.lock', 'a')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
def smi():
 p=subprocess.run(['mx-smi','--show-process'],capture_output=True,text=True,timeout=15)
 if p.returncode:raise RuntimeError('host mx-smi failed')
 return p.stdout
before=smi()
result={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'gpu_before':before,'container':container,'image_id':image}
if re.search(r'\\|\\s+\\d+\\s+\\d+\\s+\\S+',before):
 result.update(status='blocked',reason='Existing GPU process; no benchmark started')
else:
 name='inferoptlab-calibration-'+uuid.uuid4().hex
 cmd=(['docker','run','--pull=never','--rm','--init','-i','--name',name,'--network','none','--device','/dev/dri','--device','/dev/mxcd','--group-add','video','-e','MACA_VISIBLE_DEVICES=0','-e','INFEROPTLAB_HOST_GPU_PREFLIGHT='+before,'--entrypoint','python3',image,'-','0'] if image else ['docker','exec','-i','-e','INFEROPTLAB_HOST_GPU_PREFLIGHT='+before,container,'timeout','-k','5','140','python3','-','0'])
 try:
  try:p=subprocess.run(cmd,input=probe,capture_output=True,timeout=150)
  except subprocess.TimeoutExpired as exc:p=subprocess.CompletedProcess(cmd,124,exc.stdout or b'',exc.stderr or b'calibration timed out')
 finally:
  if image:subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20)
 result.update(returncode=p.returncode,stdout=p.stdout.decode(errors='replace'),stderr=p.stderr.decode(errors='replace'),gpu_after=smi())
 if p.returncode==0:
  result['result']=json.loads(result['stdout'][result['stdout'].index('{'):]);result['status']=result['result']['status']
 else:result['status']='failed'
print(json.dumps(result,indent=2))
'''.replace('CONTAINER', repr(args.container)).replace('IMAGE', repr(args.image)).replace('PROBE', repr(base64.b64encode(probe).decode()))
    p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                        '-o', 'ConnectTimeout=10', args.host, 'python3 -'],
                       input=remote.encode(), capture_output=True, timeout=200)
    if p.returncode:
        raise SystemExit(p.stderr.decode(errors='replace'))
    result = json.loads(p.stdout)
    result['probe_sha256'] = hashlib.sha256(probe).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=2, allow_nan=False)
        f.write('\n')
    args.out.with_suffix('.probe.py').write_bytes(probe)
    print(result['status'])
    for row in result.get('result', {}).get('measurements', []):
        print(row['name'], row['value'], row['unit'])
    if result['status'] != 'measured':
        print(result.get('reason', result.get('stderr', '')))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
