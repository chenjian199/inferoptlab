import json,os,pathlib,subprocess,sys
r=pathlib.Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
out=r/'experiments/evidence/glm53-short-output-supervised-20261125'
launch=out.with_suffix('.launch.json')
if launch.exists():
 print(launch.read_text());sys.exit(0)
assert not (r/'experiments/runs/benchmark/.execution.lock').exists(),'active benchmark lease'
for proc in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try: cmd=proc.read_bytes().split(bytes([0]))
 except (FileNotFoundError,PermissionError):continue
 assert not any(x.endswith(b'/prepare-short-output.py') for x in cmd),'fixture preparation still active'
env=dict(os.environ,PYTHONPATH=str(r/'.host-deps')+':'+str(r),PATH='/opt/mxdriver/bin:/opt/maca/bin:'+os.environ['PATH'])
command=['python3','-u',str(r/'tools/deployment/metax-vllm/supervise_scan.py'),'--plan',str(r/'recipes/plans/benchmark/glm53-vllm/decode-scan.yaml'),'--qualification',str(r/'experiments/evidence/glm53-decode-preflight/20261125/live-r3/startup/qualification.json'),'--client-root',str(r.parent/'inferoptlab-client-20261124'),'--client-image','sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad','--state-dir',str(out),'--interval','60','--restore-service','inferoptlab-glm53-vllm-r1','--service-label','glm53-source-reproduction']
with launch.open('x') as receipt:
 with out.with_suffix('.log').open('x') as log:
  child=subprocess.Popen(command,cwd=r,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 value=dict(pid=child.pid,command=command,log=str(out.with_suffix('.log')))
 json.dump(value,receipt,indent=2)
 print(json.dumps(value))
