"""Build vLLM and the C500 plugin from pinned, patched source into wheels."""
import importlib.metadata as md
import json
import os
import subprocess
import sys
from pathlib import Path

assert os.environ.get('INFEROPTLAB_BUILD_CONTAINER') == '1' and Path('/opt/build-scripts').is_dir(), 'Dedicated Docker build only'
root = Path('/opt/src')
plugin = root / 'vllm-metax'
upstream = root / 'vllm'
evidence = Path('/opt/build-evidence')
wheels = sorted(Path('/inputs/wheelhouse').glob('*.whl'))
assert len(wheels) == 27
from packaging.utils import parse_wheel_filename
pins = {str(parse_wheel_filename(w.name)[0]): str(parse_wheel_filename(w.name)[1]) for w in wheels}
constraints = evidence / 'native-constraints.txt'
constraints.write_text(''.join(f'{k}=={v}\n' for k, v in sorted(pins.items())))
extra = evidence / 'maca-public.txt'
extra.write_text('\n'.join(line for line in (plugin / 'requirements/maca.txt').read_text().splitlines() if line.strip() and not line.strip().startswith(('#', '-r'))) + '\n')
env = dict(os.environ)
for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy', 'PYTHONPATH'):
    env.pop(key, None)
def run(args, **kwargs):
    print('RUN', args, flush=True)
    subprocess.run(args, check=True, env=kwargs.pop('env', env), **kwargs)

run([sys.executable, '-m', 'pip', 'install', '--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple',
     '--timeout', '60', '--retries', '4', '-c', str(constraints), *map(str, wheels),
     '-r', str(plugin / 'requirements/common.txt'), '-r', str(plugin / 'requirements/build.txt'), '-r', str(extra)])
assert md.version('torch') == '2.10.0+metax3.9.0.8'
assert md.version('mcoplib') == pins['mcoplib']
run([sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--no-build-isolation', '-w', '/opt/built-wheels', str(upstream)],
    env={**env, 'VLLM_TARGET_DEVICE': 'empty', 'SETUPTOOLS_SCM_PRETEND_VERSION': '0.32.0'})
run([sys.executable, '-m', 'pip', 'install', '--no-deps', *map(str, Path('/opt/built-wheels').glob('vllm-*.whl'))])
run([sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--no-build-isolation', '-w', '/opt/built-wheels', str(plugin)],
    env={**env, 'SETUPTOOLS_SCM_PRETEND_VERSION': '0.32.0+g0962c873'})
run([sys.executable, '-m', 'pip', 'install', '--no-deps', *map(str, Path('/opt/built-wheels').glob('vllm_metax-*.whl'))])
run([sys.executable, '-m', 'pip', 'check'])
assert all(md.version(k) == v for k, v in pins.items())
(evidence / 'requirements.lock.txt').write_text(subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True))
