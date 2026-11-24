"""Resolve common dependencies while the private SDK/wheels are still downloading."""
import importlib.metadata as md
import json
import os
import subprocess
import sys
from pathlib import Path

assert Path('/.dockerenv').exists() and os.environ.get('GLM53_ISOLATED_ENV') == '1'
before = {d.metadata['Name']:d.version for d in md.distributions() if d.metadata['Name']}
private = {k:v for k,v in before.items() if '+metax' in v or '+maca' in v}
lock = Path('/work/evidence/bootstrap_private_constraints.txt')
lock.write_text(''.join(f'{name}=={version}\n' for name,version in private.items()))
env = os.environ.copy()
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:
    env.pop(key,None)
subprocess.run([sys.executable,'-m','pip','install','--index-url',
    'https://pypi.tuna.tsinghua.edu.cn/simple','--timeout','60','--retries','8',
    '--find-links','/wheelhouse/public','-c',str(lock),
    '-r','/work/src/vllm-metax/requirements/common.txt',
    '-r','/work/evidence/build_public.txt'],env=env,check=True)
assert all(md.version(name)==version for name,version in private.items())
Path('/work/evidence/public_preparation.json').write_text(json.dumps({
    'private_versions_preserved':private,'completed':True},indent=2))
print('PUBLIC_PREPARATION_READY',flush=True)
