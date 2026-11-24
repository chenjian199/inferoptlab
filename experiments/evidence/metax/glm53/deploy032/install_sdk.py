"""Apply the official SDK container installation recipe in the isolated container."""
import json
import os
import subprocess
from pathlib import Path

assert Path('/.dockerenv').exists() and os.environ.get('GLM53_ISOLATED_ENV') == '1'
evidence = Path('/work/evidence')
stage = json.loads((evidence/'sdk_stage.json').read_text())
assert stage['xz_integrity'] == 'pass'
assert all(not item['system_actions'] for item in stage['packages'])
assert not any(any(word in item['file'] for word in ['tdriver','firmware','dkms','kernel-module'])
               for item in stage['packages'])
link = Path('/opt/maca')
assert link.is_symlink() and str(link.resolve()).startswith('/opt/maca-')
before = str(link.resolve())
sdk = Path(stage['sdk'])
assert sdk == Path('/opt/glm53-sdk-stage/maca-sdk-3.9.0.29')
subprocess.run(['bash',str(sdk/'mxmaca-sdk-install.sh'),'-f'],cwd=sdk,check=True)
Path('/etc/ld.so.conf.d/maca.conf').write_text('/opt/maca/lib\n/opt/maca/mxgpu_llvm/lib\n')
subprocess.run(['ldconfig'],check=True)
version = (link/'Version.txt').read_text().strip()
assert '3.9.0.29' in version, version
audit = subprocess.run(['dpkg','--audit'],capture_output=True,text=True)
report = {'before_sdk_path':before,'sdk_path':str(link.resolve()),'version':version,
          'dpkg_audit_exit':audit.returncode,'dpkg_audit':audit.stdout+audit.stderr,
          'host_driver_installer_used':False,
          'recipe':'official .layerspec/Dockerfile: mxmaca-sdk-install.sh -f; ldconfig'}
(evidence/'sdk_install.json').write_text(json.dumps(report,indent=2))
print('SDK_INSTALL_READY',json.dumps(report),flush=True)
