"""Prepare a separate amd64 CPU benchmark client using the existing Python image."""
from pathlib import Path
import json, subprocess

work=Path('/home/ubuntu/CJ_workspace/inferoptlab-client-20261124')
work.mkdir(exist_ok=False)
image='sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad'
source='''from pathlib import Path
import subprocess, json
root=Path('/work')
subprocess.run(['python3','-m','venv',str(root/'venv')],check=True,timeout=30)
python=str(root/'venv/bin/python')
with (root/'install.log').open('w') as stream:
 result=subprocess.run([python,'-m','pip','install','--disable-pip-version-check','--index-url','https://pypi.org/simple','aiperf==0.12.0','PyYAML>=6.0.2,<7','jsonschema>=4.23,<5','referencing>=0.35,<1'],stdout=stream,stderr=subprocess.STDOUT,timeout=240)
 result.check_returncode()
p=subprocess.run([python,'-m','pip','freeze'],capture_output=True,text=True,check=True)
(root/'requirements.lock.txt').write_text(p.stdout)
for name,args in [('version',['/work/venv/bin/aiperf','--version']),('help',['/work/venv/bin/aiperf','profile','--help'])]:
 p=subprocess.run(args,capture_output=True,text=True,timeout=40)
 (root/(name+'.json')).write_text(json.dumps(dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr),indent=2))
 p.check_returncode()
print(json.dumps({'status':'ready','python':python,'aiperf_version':'0.12.0'}))
'''
args=['docker','run','--pull=never','--rm','-i','--name','inferoptlab-client-install-20261124',
      '--user','1000:1000','--mount',f'type=bind,source={work},target=/work',
      '-e','HOME=/work','--entrypoint','python3',image,'-']
try:
    p=subprocess.run(args,input=source,text=True,capture_output=True,timeout=330)
    result={'image':image,'workdir':str(work),'argv':args,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    (work/'prepare.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result))
finally:
    subprocess.run(['docker','rm','-f','inferoptlab-client-install-20261124'],capture_output=True,timeout=30)
