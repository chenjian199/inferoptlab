"""Download the pinned MACA SDK and wheels; never install into the host."""
import concurrent.futures
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

root = Path(sys.argv[1]).resolve()
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
base = 'https://repos.metax-tech.com/r/'
index = op.open(base + 'maca-sdk-deb/dists/stable/main/binary-amd64/Packages', timeout=60).read()
(root / 'evidence/sdk-packages.txt').write_bytes(index)
sdk = []
for block in index.decode().split('\n\n'):
    fields = dict(line.split(': ', 1) for line in block.splitlines() if ': ' in line and not line.startswith(' '))
    if fields.get('Version') == '3.9.0.29' and fields.get('Architecture') == 'amd64':
        assert not any(s in fields['Package'] for s in ['driver', 'dkms', 'firmware'])
        sdk.append({'file': Path(fields['Filename']).name, 'bytes': int(fields['Size']),
                    'sha256': fields['SHA256'], 'url': base + 'maca-sdk-deb/' + fields['Filename'], 'kind': 'sdk'})
assert any(x['file'].startswith('maca_sdk_3.9.0_') for x in sdk)
wheels = json.loads((root / 'native-wheels.json').read_text())
for item in wheels:
    name, version = item['file'].split('-', 2)[:2]
    project = re.sub(r'[-_.]+', '-', name).lower()
    item.update(kind='wheelhouse', url=base + f'maca-pypi/packages/{project}/{version}/{item["file"]}')

def download(item):
    destination = root / 'inputs' / item['kind'] / item['file']
    destination.parent.mkdir(parents=True, exist_ok=True)
    def matches(path):
        if not path.exists() or path.stat().st_size != item['bytes']:
            return False
        with path.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(f.read()).hexdigest()
        return digest == item['sha256']
    if matches(destination):
        return item
    temporary = destination.with_suffix(destination.suffix + '.part')
    for attempt in range(4):
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(item['url'], timeout=90) as response, temporary.open('wb') as out:
                while data := response.read(4 * 1024 * 1024):
                    out.write(data)
            assert matches(temporary), f'Checksum mismatch: {temporary.name}'
            temporary.replace(destination)
            print('VERIFIED', item['file'], flush=True)
            return item
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2)

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    manifest = list(pool.map(download, sdk + wheels))
(root / 'evidence/dependencies.json').write_text(json.dumps(manifest, indent=2))
print('DEPENDENCIES_READY', len(manifest), flush=True)
