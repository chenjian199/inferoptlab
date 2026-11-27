"""Read the pinned image's cache code without loading a model or using GPUs."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
IMAGE = 'sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b'
probe = '''
import json
from pathlib import Path
r=Path('/opt/vllm-env/lib/python3.12/site-packages')
names=['vllm/v1/kv_cache_interface.py','vllm/v1/core/kv_cache_utils.py',
 'vllm/v1/core/single_type_kv_cache_manager.py',
 'vllm/model_executor/layers/mamba/abstract.py',
 'vllm/model_executor/layers/mamba/gdn/base.py']
files={n:(r/n).read_text() for n in names if (r/n).exists()}
for p in (r/'vllm_metax').rglob('*.py'):
    text=p.read_text()
    if any(s in text for s in ['MambaSpec', 'max_memory_usage_bytes', 'kv_cache_groups']):
        files[str(p.relative_to(r))]=text
for package in ['vllm/v1/engine', 'vllm/v1/executor', 'vllm/entrypoints']:
    for p in (r/package).rglob('*.py'):
        text=p.read_text()
        if 'num_gpu_blocks' in text or 'kv_cache_config.num_blocks' in text:
            files[str(p.relative_to(r))]=text
print(json.dumps(files))
'''
remote = 'import subprocess,sys\np=subprocess.run(' + repr([
    'docker', 'run', '--rm', '-i', '--network=none', '--entrypoint', 'python3', IMAGE, '-'
]) + ',input=' + repr(probe.encode()) + ',capture_output=True)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)'
p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8',
                    'metax-60', 'python3 -'], input=remote.encode(), capture_output=True, timeout=55)
if p.returncode:
    raise SystemExit(p.stderr.decode(errors='replace'))
data = json.loads(p.stdout)
manifest = []
for name, content in data.items():
    dest = ROOT/'source'/name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding='utf-8', newline='\n')
    manifest.append(dict(path=name, sha256=hashlib.sha256(content.encode()).hexdigest()))
(ROOT/'source-manifest.json').write_text(json.dumps(dict(image=IMAGE, files=manifest), indent=2), encoding='utf-8')
print('read', len(manifest), 'cache source files')
