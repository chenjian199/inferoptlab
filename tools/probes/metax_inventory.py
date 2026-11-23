"""Compatibility entrypoint; implementation lives under tools.hardware.probes."""
from pathlib import Path
import runpy
import sys

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from tools.hardware.probes.metax import *  # noqa: F401,F403

if __name__ == '__main__':
    runpy.run_path(str(_ROOT / 'tools/hardware/probes/metax.py'), run_name='__main__')
