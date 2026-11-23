"""Sequential hosts/devices, hashed artifacts and bounded remote execution."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

from tools.specs import SpecError
from tools.specs import read
from .config import validate

HERE = Path(__file__).resolve().parent


def write_json(path, doc):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(doc, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def ssh(host, script, timeout):
    try:
        p = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                            '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=15',
                            '-o', 'ServerAliveCountMax=3', host, 'python3 -'],
                           input=script, capture_output=True, timeout=timeout)
        if p.returncode:
            return dict(status='failed', error='SSH worker failed', returncode=p.returncode,
                        stdout=p.stdout.decode(errors='replace'), stderr=p.stderr.decode(errors='replace'))
        try:
            result = json.loads(p.stdout)
            if not isinstance(result, dict) or 'status' not in result:
                raise ValueError('worker did not return a result object with status')
        except ValueError as exc:
            return dict(status='failed', error=str(exc), stdout=p.stdout.decode(errors='replace'),
                        stderr=p.stderr.decode(errors='replace'))
        result['ssh_stderr'] = p.stderr.decode(errors='replace')
        return result
    except subprocess.TimeoutExpired as exc:
        return dict(status='failed', error='SSH worker exceeded its deadline',
                    stdout=(exc.stdout or b'').decode(errors='replace'), stderr=(exc.stderr or b'').decode(errors='replace'))
    except OSError as exc:
        return dict(status='failed', error=str(exc))


def execute(plan, out, mode='run', transport=ssh):
    validate(plan)
    if mode not in ('inspect', 'run'):
        raise SpecError('execution mode must be inspect or run')
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / 'plan.json', plan)
    for name, source in [('inventory.py', HERE/'probes/metax.py'), ('benchmark.py', HERE/'probes/torch_bench.py'),
                         ('worker.py', HERE/'remote.py')]:
        (out/name).write_bytes(source.read_bytes())
    manifest = dict(format_version=1, mode=mode, status='running',
                    captured_at=datetime.now(timezone.utc).isoformat(), hosts=[], files={})
    interrupted = False
    try:
        for host in plan['hosts']:
            folder = out / host['id']
            folder.mkdir()
            payload = dict(host=host, protocol=plan['protocol'], mode=mode,
                           inventory_code=(out/'inventory.py').read_text(encoding='utf-8'),
                           benchmark_code=(out/'benchmark.py').read_text(encoding='utf-8'))
            script = ('PAYLOAD = ' + repr(payload) + '\n').encode() + (out/'worker.py').read_bytes()
            # Bound "all" by the declared host device limit. Worker enforces it too.
            count = host['max_devices'] if host['devices'] == 'all' else len(host['devices'])
            timeout = 300 + count * (plan['protocol']['timeout_seconds'] + 90)
            (folder/'worker.py').write_bytes(script)
            result = transport(host['ssh'], script, timeout)
            result.update(ssh_host=host['ssh'], node_id=host['id'],
                          worker_sha256=hashlib.sha256(script).hexdigest())
            write_json(folder/'result.json', result)
            manifest['hosts'].append(dict(id=host['id'], path=f'{host["id"]}/result.json', status=result['status']))
    except KeyboardInterrupt:
        interrupted = True
        manifest['error'] = 'controller interrupted; current remote test retains its own timeout and cleanup'
    finally:
        good = 'inspected' if mode == 'inspect' else 'measured'
        manifest['status'] = 'complete' if not interrupted and len(manifest['hosts']) == len(plan['hosts']) and all(
            h['status'] == good for h in manifest['hosts']) else 'incomplete'
        for path in sorted(out.rglob('*')):
            if path.is_file():
                manifest['files'][path.relative_to(out).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        write_json(out/'manifest.json', manifest)
    return manifest


def verify(out):
    out = Path(out).resolve()
    manifest = read(out/'manifest.json')
    if manifest.get('format_version') != 1 or manifest.get('mode') not in ('inspect', 'run'):
        raise SpecError('unsupported artifact format/mode')
    if not {'plan.json', 'worker.py', 'inventory.py', 'benchmark.py'} <= set(manifest['files']):
        raise SpecError('manifest omits plan or executed probes')
    for name, expected in manifest['files'].items():
        if Path(name).is_absolute() or '\\' in name or '..' in Path(name).parts or Path(name).as_posix() != name:
            raise SpecError(f'artifact path must be a normalized relative path: {name}')
        path = (out/name).resolve()
        if not path.is_relative_to(out) or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SpecError(f'artifact missing, changed, or outside run: {name}')
    plan = validate(read(out/'plan.json'))
    expected_ids = [h['id'] for h in plan['hosts']]
    actual_ids = [h['id'] for h in manifest['hosts']]
    if len(actual_ids) != len(set(actual_ids)) or not set(actual_ids) <= set(expected_ids):
        raise SpecError('manifest host IDs differ from plan')
    for host in manifest['hosts']:
        if host['path'] != f'{host["id"]}/result.json' or host['path'] not in manifest['files']:
            raise SpecError('unhashed or unexpected host artifact')
        worker = f'{host["id"]}/worker.py'
        if worker not in manifest['files']:
            raise SpecError('executed worker is not hashed')
        result = read(out/host['path'])
        if (result['node_id'] != host['id'] or result['status'] != host['status'] or
                result['worker_sha256'] != manifest['files'][worker]):
            raise SpecError('host result identity/status/worker digest differs from manifest')
    if manifest['status'] == 'complete':
        good = 'inspected' if manifest['mode'] == 'inspect' else 'measured'
        if actual_ids != expected_ids or any(h['status'] != good for h in manifest['hosts']):
            raise SpecError('complete manifest has missing or unsuccessful hosts')
    return manifest, plan
