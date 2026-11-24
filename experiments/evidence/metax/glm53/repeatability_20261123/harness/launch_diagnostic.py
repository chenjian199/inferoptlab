import fcntl
import json
from pathlib import Path
import subprocess
import time

ROOT = Path('/home/metax/glm53-repeatability-20261123')


def main():
    deadline = time.monotonic()+14400
    while not (ROOT/'evidence/launcher_complete.json').exists():
        for file in (ROOT/'evidence').glob('process_?.json'):
            if json.loads(file.read_text())['status']=='failed':
                raise RuntimeError('Earlier process failed; diagnostic not started')
        if time.monotonic()>deadline:
            raise TimeoutError('Plain repeats not completed')
        time.sleep(5)
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        cmd = ['docker','exec','glm53-repeat-v1','python3','-u','/experiment/harness/run_diagnostic.py']
        started = time.time()
        with (ROOT/'evidence/diagnostic.log').open('x') as log:
            p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
            record = {'status':'running','pid':p.pid,'command':cmd,'started_epoch':started}
            (ROOT/'evidence/diagnostic_process.json').write_text(json.dumps(record,indent=2))
            code = p.wait()
        record.update(status='complete' if code==0 else 'failed',exit_code=code,elapsed_seconds=time.time()-started)
        (ROOT/'evidence/diagnostic_process.json').write_text(json.dumps(record,indent=2))
        if code:
            raise RuntimeError('Diagnostic process failed')


if __name__ == '__main__':
    main()
