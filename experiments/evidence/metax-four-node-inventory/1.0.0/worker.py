"""Standalone remote worker; controller supplies PAYLOAD before this source."""
import datetime
import fcntl
import hashlib
import json
import os
import subprocess
import traceback
import uuid


def run(payload):
    inv = {'__name__': '_inventory'}
    bench = {'__name__': '_benchmark'}
    exec(compile(payload['inventory_code'], 'inventory.py', 'exec'), inv)
    exec(compile(payload['benchmark_code'], 'benchmark.py', 'exec'), bench)
    result = dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  node_id=payload['host']['id'], hostname=os.uname().nodename,
                  status='failed', attempts=[], inventory=None)
    try:
        inventory = inv['inventory']()
        result['inventory'] = inventory
        process = inventory['commands']['processes']
        if process.get('returncode') != 0:
            raise RuntimeError('mx-smi process inventory failed')
        bench['active_gpu_pids'](process['stdout'])  # malformed output is an error even for inspect
        gpu_command = inventory['commands']['gpu']
        if gpu_command.get('returncode') != 0:
            raise RuntimeError('GPU identity inventory failed')
        text = gpu_command['stdout']
        gpu = json.loads(text[text.index('{'):])
        indices = sorted(v['device_id'] for v in gpu.values() if isinstance(v, dict) and 'device_id' in v)
        selected = indices if payload['host']['devices'] == 'all' else payload['host']['devices']
        if not selected or not set(selected) <= set(indices):
            raise RuntimeError('requested GPU indices are absent from the inventory')
        if len(selected) > payload['host']['max_devices']:
            raise RuntimeError('selected GPUs exceed max_devices')
        result['selected_devices'] = selected
        if payload['mode'] == 'inspect':
            result['status'] = 'inspected'
            return result
        image = payload['host']['image']
        p = subprocess.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', image],
                           capture_output=True, text=True, timeout=20)
        if p.returncode or p.stdout.strip() != image:
            raise RuntimeError('local image ID missing or mismatched; images are never downloaded')
        result['image_id'] = image
        with open('/tmp/inferoptlab-c500-calibration.lock', 'a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                result.update(status='blocked', error='another calibration holds the host lock')
                return result
            for ordinal in selected:
                attempt = dict(ordinal=ordinal, status='failed', captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
                result['attempts'].append(attempt)
                before = inv['command'](['mx-smi', '--show-process'])
                attempt['before'] = before
                if before.get('returncode') != 0:
                    attempt['error'] = 'process preflight failed'
                    break
                if bench['active_gpu_pids'](before['stdout']):
                    attempt.update(status='blocked', error='GPU process already present on host')
                    break
                name = 'inferoptlab-hardware-' + uuid.uuid4().hex
                cmd = ['docker', 'run', '--pull=never', '--rm', '--init', '-i', '--name', name,
                       '--network', 'none', '--device', '/dev/dri', '--device', '/dev/mxcd',
                       '--group-add', 'video', '-e', f'MACA_VISIBLE_DEVICES={ordinal}',
                       '-e', 'INFEROPTLAB_HOST_GPU_PREFLIGHT=' + before['stdout'],
                       '-e', 'INFEROPTLAB_PROTOCOL=' + json.dumps(payload['protocol']),
                       '--entrypoint', 'python3', image, '-', '0']
                attempt['container_name'] = name
                try:
                    p = subprocess.run(cmd, input=payload['benchmark_code'].encode(), capture_output=True,
                                       timeout=payload['protocol']['timeout_seconds'])
                    attempt.update(returncode=p.returncode, stdout=p.stdout.decode(errors='replace'),
                                   stderr=p.stderr.decode(errors='replace'))
                    if p.returncode == 0:
                        text = attempt['stdout']
                        measured = json.loads(text[text.index('{'):])
                        if measured['status'] != 'measured' or int(measured['physical_ordinal']) != ordinal:
                            raise RuntimeError('measurement device/status mismatch')
                        attempt.update(status='measured', result=measured)
                except subprocess.TimeoutExpired as exc:
                    attempt.update(status='timeout', error='device test exceeded its deadline',
                                   stdout=(exc.stdout or b'').decode(errors='replace'),
                                   stderr=(exc.stderr or b'').decode(errors='replace'))
                finally:
                    cleanup = subprocess.run(['docker', 'rm', '-f', name], capture_output=True, text=True, timeout=20)
                    # --rm normally already removed this owned container.
                    attempt['cleanup'] = dict(returncode=cleanup.returncode, stderr=cleanup.stderr)
                    if cleanup.returncode and 'No such container' not in cleanup.stderr:
                        attempt.update(status='cleanup_failed', error='owned container cleanup could not be confirmed')
                after = inv['command'](['mx-smi', '--show-process'])
                attempt['after'] = after
                if after.get('returncode') != 0 or bench['active_gpu_pids'](after.get('stdout', '')):
                    attempt.update(status='contended', error='GPU process state was not idle after the test')
                if attempt['status'] != 'measured':
                    break
        result['status'] = 'measured' if len(result['attempts']) == len(selected) and all(
            a['status'] == 'measured' for a in result['attempts']) else 'incomplete'
    except Exception as exc:
        result.update(status='failed', error=str(exc), traceback=traceback.format_exc())
    return result


if __name__ == '__main__':
    print(json.dumps(run(PAYLOAD), indent=2, allow_nan=False))
