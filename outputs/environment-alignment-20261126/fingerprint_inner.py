"""Read-only source/native/SDK fingerprints; never imports GPU frameworks."""
import hashlib
import importlib.metadata as md
import importlib.util
import json
from pathlib import Path
import subprocess

out = dict(packages={}, files=[], sources=[])
for dist in md.distributions():
    name = dist.metadata.get('Name', '')
    if any(s in name.lower() for s in ['torch', 'vllm', 'triton', 'flash', 'mcop', 'mctlass', 'deep', 'tile', 'transformers', 'aiperf', 'compressed']):
        out['packages'][name] = dist.version

def add(p, text=False):
    if not p.is_file():
        return
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    row = dict(path=str(p), resolved=str(p.resolve()), bytes=p.stat().st_size, sha256=h.hexdigest())
    if text and p.stat().st_size < 200000:
        row['text'] = p.read_text(errors='replace')
    out['files'].append(row)

for module in ['vllm', 'vllm_metax']:
    spec = importlib.util.find_spec(module)
    if not spec or not spec.origin:
        continue
    base = Path(spec.origin).parent
    for rel in ['models/glm5next/common/model.py','models/glm5next/metax/sparse_indexer.py','patch/bugfix/__init__.py', 'patch/AUDIT.md']:
        add(base/rel, True)
    for pat in ['**/*moe*abi*.py','**/*flashmla*.py','**/*sparse_mla*.py']:
        for p in base.glob(pat):
            add(p, True)
    source = base.parent
    if not (source/'.git').exists():
        source = Path('/opt/src') / module.replace('_', '-')
    if (source/'.git').exists():
        commands = {}
        for name, args in [('head',['rev-parse','HEAD']),('status',['status','--short']),('diff',['diff','--stat'])]:
            p = subprocess.run(['git','-C',str(source),*args],text=True,capture_output=True,timeout=20)
            commands[name] = p.stdout[:30000]
        out['sources'].append(dict(module=module,path=str(source),**commands))

seen=set()
for root in [Path('/opt/vllm-env/lib/python3.12/site-packages'),Path('/opt/conda/lib/python3.12/site-packages')]:
    for pat in ['*flash*mla*.so','flash_mla/**/*.so','*mctlass*.so','*mcop*.so']:
        for p in root.glob(pat):
            if p.resolve() not in seen:
                seen.add(p.resolve());add(p)
for root in [Path('/opt/maca/lib'),Path('/opt/maca-3.9.0.29/lib')]:
    for pat in ['libmccl.so*','libmaca.so*','libmcruntime.so*']:
        for p in root.glob(pat):
            if p.resolve() not in seen:
                seen.add(p.resolve());add(p)
print(json.dumps(out))
