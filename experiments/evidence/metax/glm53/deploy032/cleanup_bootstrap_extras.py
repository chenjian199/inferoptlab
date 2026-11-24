"""Remove obsolete optional ABI packages only from the dedicated environment."""
import importlib.metadata as md
import json
import os
import subprocess
import sys
from pathlib import Path

assert Path('/.dockerenv').exists() and os.environ.get('GLM53_ISOLATED_ENV') == '1'
# None occurs in the pinned 0.32 maca/common/private requirements. The old
# xformers/mcpy builds target the 3.8 SDK; the inherited decord wheel is invalid
# for this Python/platform according to the bootstrap pip check.
names = ['xformers','mcpy','decord']
found = {}
for name in names:
    try:found[name] = md.version(name)
    except md.PackageNotFoundError:pass
Path('/work/evidence/removed_bootstrap_extras.json').write_text(json.dumps(found,indent=2))
if found:
    subprocess.run([sys.executable,'-m','pip','uninstall','-y',*found],check=True)
print('BOOTSTRAP_EXTRAS_REMOVED',json.dumps(found),flush=True)
