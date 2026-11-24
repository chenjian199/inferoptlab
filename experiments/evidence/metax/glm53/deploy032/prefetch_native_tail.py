"""Prefetch remaining vendor wheels concurrently, publishing only complete files."""
import concurrent.futures
import json
import os
import subprocess
import sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

assert Path('/.dockerenv').exists() and os.environ.get('GLM53_ISOLATED_ENV') == '1'
lines = Path('/work/src/vllm-metax/requirements/maca_private.txt').read_text().splitlines()
start = next(i for i, line in enumerate(lines) if line.startswith('flash_attn_3=='))
requirements = [line.strip() for line in lines[start:]
                if line.strip() and not line.startswith(('#','-','mcoplib=='))]
env = os.environ.copy()
for key in ['HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy']:
    env.pop(key, None)
root = Path('/wheelhouse')

def fetch(requirement):
    name = canonicalize_name(Requirement(requirement).name)
    stage = root/'.prefetch'/name
    stage.mkdir(parents=True, exist_ok=True)
    log = Path('/work/evidence')/f'prefetch-{name}.log'
    with log.open('w') as out:
        result = subprocess.run([sys.executable,'-m','pip','download','--no-deps',
            '--only-binary=:all:','--progress-bar=off','--timeout','60','--retries','8',
            '--index-url','https://repos.metax-tech.com/r/maca-pypi/simple',
            '--find-links',str(root),'--dest',str(stage),requirement],
            env=env,stdout=out,stderr=out)
    if result.returncode == 0:
        for wheel in stage.glob('*.whl'):
            wheel.replace(root/wheel.name)
    print(json.dumps({'requirement':requirement,'exit':result.returncode}),flush=True)
    return result.returncode

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    codes = list(pool.map(fetch, requirements))
assert all(code == 0 for code in codes), codes
print('NATIVE_TAIL_READY',flush=True)
