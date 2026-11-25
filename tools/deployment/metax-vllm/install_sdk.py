"""Install only userspace SDK packages inside a Docker build stage."""
import json
import os
import re
import subprocess
from pathlib import Path

assert os.environ.get('INFEROPTLAB_BUILD_CONTAINER') == '1' and Path('/opt/build-scripts').is_dir(), 'Dedicated Docker build only'
packages = sorted(Path('/inputs/sdk').glob('*.deb'))
assert packages
records = []
for package in packages:
    name = subprocess.check_output(['dpkg-deb', '-f', str(package), 'Package'], text=True).strip()
    assert not any(word in name for word in ['driver', 'firmware', 'dkms'])
    controls = Path('/tmp/sdk-controls') / name
    controls.mkdir(parents=True, exist_ok=True)
    subprocess.run(['dpkg-deb', '-e', str(package), str(controls)], check=True)
    for script in controls.iterdir():
        if script.name in ('preinst', 'postinst', 'prerm', 'postrm'):
            assert not re.search(r'\b(modprobe|insmod|depmod|dkms|systemctl|service)\b|/dev/|/sys/', script.read_text()), script
    records.append(name)
subprocess.run(['dpkg', '-i', *map(str, packages)], check=True)
sdk = Path('/opt/maca-3.9.0')
assert sdk.is_dir(), list(Path('/opt').glob('maca*'))
link = Path('/opt/maca')
assert link.is_symlink()
link.unlink()
link.symlink_to(sdk)
Path('/etc/ld.so.conf.d/maca.conf').write_text('/opt/maca/lib\n/opt/maca/mxgpu_llvm/lib\n')
subprocess.run(['ldconfig'], check=True)
assert '3.9.0.29' in (sdk / 'Version.txt').read_text()
Path('/opt/build-evidence/sdk-install.json').write_text(json.dumps({'packages': records, 'version': '3.9.0.29', 'host_modified': False}, indent=2))
