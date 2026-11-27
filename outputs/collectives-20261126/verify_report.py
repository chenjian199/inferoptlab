"""Final evidence/link audit and portable result bundle."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
v = json.loads((OUT / 'verification.json').read_text())
env = json.loads((OUT / 'environment-verification.json').read_text())
assert 'no process found' in env['gpu_after'].lower()
assert not env['containers_after'].strip()
assert env['probe_sha256'] == hashlib.sha256((ROOT / 'tools/hardware/probes/collective_bandwidth.py').read_bytes()).hexdigest()
assert env['probe_sha256'] == hashlib.sha256((OUT / 'raw/collective_bandwidth.py').read_bytes()).hexdigest()
uuid_verified = all('uuid' in d for m in env['masks'] for d in m['devices'])
if uuid_verified:
    assert len(set(d['uuid'] for d in env['masks'][0]['devices'])) == 8
for mask in env['masks']:
    indices = list(map(int, mask['mask'].split(',')))
    assert len(indices) == mask['count']
    if uuid_verified:
        assert [d['uuid'] for d in mask['devices']] == [env['masks'][0]['devices'][i]['uuid'] for i in indices]
v['device_mask_counts_verified'] = len(env['masks'])
v['device_mask_uuid_mapping_verified'] = uuid_verified
v['gpu_idle_after'] = True
v['probe_sha256'] = env['probe_sha256']
v['image'] = env['image']
v['model_config_sha256'] = env['model_config_sha256']
checked = 0
for p in OUT.glob('*.md'):
    text = p.read_text(encoding='utf-8')
    assert '\ufffd' not in text
    for link in re.findall(r'\]\(([^)]+)\)', text):
        if link.startswith(('https://','http://','#')):
            continue
        assert (p.parent / link.split('#')[0]).exists(), (p, link)
        checked += 1
    blocks = []
    for line in text.splitlines():
        if line.startswith('|'):
            width = line.count('|')
            if blocks: assert width == blocks[-1]
            blocks.append(width)
        else:
            blocks = []
v['markdown_links_verified'] = checked
v['artifacts_sha256'] = {str(p.relative_to(OUT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                         and p.name != 'verification.json' and p.suffix != '.zip'}
(OUT / 'verification.json').write_text(json.dumps(v, indent=2), encoding='utf-8')
archive = OUT / 'C500-collectives-and-phase-analysis.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.suffix != '.zip' and '__pycache__' not in p.parts:
            z.write(p, p.relative_to(OUT))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps(dict(points=v['points'],phase_points=v['phase_points'],links=checked,
                     files=len(v['artifacts_sha256']),bundle_bytes=archive.stat().st_size)))
