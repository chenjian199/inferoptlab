"""Validate and inspect the official SDK archive inside the isolated container."""
import json
import os
import re
import subprocess
import tarfile
from pathlib import Path

assert Path('/.dockerenv').exists()
assert os.environ.get('GLM53_ISOLATED_ENV') == '1'
archive = Path('/install/maca-sdk-3.9.0.29-deb-x86_64.tar.xz')
assert archive.stat().st_size == 6392534772
subprocess.run(['xz', '-t', str(archive)], check=True)
stage = Path('/opt/glm53-sdk-stage')
stage.mkdir(exist_ok=True)
with tarfile.open(archive, 'r:xz') as tar:
    tar.extractall(stage, filter='data')
sdk = stage/'maca-sdk-3.9.0.29'
records = []
controls = Path('/work/evidence/sdk_package_controls')
controls.mkdir(exist_ok=True)
for deb in sorted((sdk/'deb').glob('*.deb')):
    info = subprocess.check_output(['dpkg-deb', '-f', str(deb)], text=True)
    name = re.search(r'^Package: (.+)$', info, re.M).group(1)
    destination = controls/name
    destination.mkdir(exist_ok=True)
    subprocess.run(['dpkg-deb', '-e', str(deb), str(destination)], check=True)
    relevant = {}
    for f in destination.iterdir():
        if f.name in ['preinst','postinst','prerm','postrm']:
            matches = [line for line in f.read_text(errors='replace').splitlines()
                       if re.search(r'\b(modprobe|insmod|depmod|dkms|systemctl|service)\b|/dev/|/sys/', line)]
            if matches:
                relevant[f.name] = matches
    records.append({'file': deb.name, 'metadata': info, 'system_actions': relevant})
report = {'archive': str(archive), 'xz_integrity': 'pass', 'sdk': str(sdk), 'packages': records}
Path('/work/evidence/sdk_stage.json').write_text(json.dumps(report, indent=2))
print('SDK_STAGE_READY', len(records), flush=True)
for item in records:
    if item['system_actions']:
        print(json.dumps(item), flush=True)
