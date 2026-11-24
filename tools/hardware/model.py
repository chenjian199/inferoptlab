"""Read-only checkpoint inspection through the current hardware tool entrypoint."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess

from tools.specs import SpecError
from .runner import HERE, write_json


def inspect_model(host, model, output):
    if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.@-]*', host):
        raise SpecError('invalid SSH host or alias')
    if not PurePosixPath(model).is_absolute() or '\x00' in model:
        raise SpecError('model must be an absolute remote path')
    output = Path(output)
    probe_output = output.with_suffix('.probe.py')
    if output.suffix != '.json' or output.exists() or probe_output.exists():
        raise SpecError('use a new .json observation and probe path')
    script = (HERE/'probes/metax.py').read_bytes()
    try:
        process = subprocess.run(
            ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
             '-o', 'ConnectTimeout=10', host, shlex.join(['python3', '-', 'model', model])],
            input=script, capture_output=True, timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise SpecError('model inspection exceeded its deadline') from exc
    if process.returncode:
        raise SpecError('model inspection failed: ' + process.stderr.decode(errors='replace'))
    result = json.loads(process.stdout)
    if not isinstance(result, dict):
        raise SpecError('model probe must return an object')
    result.update(probe_sha256=hashlib.sha256(script).hexdigest(), ssh_host=host)
    output.parent.mkdir(parents=True, exist_ok=True)
    with probe_output.open('xb') as stream:
        stream.write(script)
    write_json(output, result)
    return output
