import importlib.util
import json
import os
from pathlib import Path
import subprocess

OUT=Path('/workspace/audit_20261122')
repos=['/workspace/vLLM-metax','/workspace/glm/vLLM-metax']
def run(cmd):
    p=subprocess.run(cmd,text=True,capture_output=True,timeout=30)
    return dict(code=p.returncode,stdout=p.stdout,stderr=p.stderr)
data={'repos':{},'resolution':{},'package_files':{},'pip_check':run(['python','-B','-m','pip','check'])}
for p in repos:
    data['repos'][p]={}
    for key,args in [('head',['rev-parse','HEAD']),('branch',['branch','--show-current']),('status',['status','--short'])]:
        data['repos'][p][key]=run(['git','-c','safe.directory='+p,'-C',p]+args)
for cwd in ['/workspace']+repos:
    data['resolution'][cwd]=run(['docker']) if False else run(['python','-B','-c',"import os,importlib.util,pathlib; os.chdir("+repr(cwd)+"); s=importlib.util.find_spec('vllm_metax'); print(s.origin); print(pathlib.Path(s.origin).resolve())"])
site=Path('/opt/conda/lib/python3.12/site-packages')
for p in site.glob('*vllm*pth'):
    data['package_files'][str(p)]=p.read_text()
for p in site.glob('__editable__*vllm*.py'):
    data['package_files'][str(p)]=p.read_text()
for p in [site/'vllm_metax',Path('/workspace/vLLM-metax/vllm_metax')]:
    data['package_files'][str(p)]={'realpath':str(p.resolve()),'symlink':p.is_symlink()}
(OUT/'environment_diagnostics.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
