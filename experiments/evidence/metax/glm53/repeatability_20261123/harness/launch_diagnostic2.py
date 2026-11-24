import fcntl
import json
from pathlib import Path
import subprocess
import time

ROOT = Path('/home/metax/glm53-repeatability-20261123')


def main():
    deadline = time.monotonic()+18000
    while True:
        path = ROOT/'evidence/diagnostic_process.json'
        if path.exists():
            status = json.loads(path.read_text())
            if status['status']=='failed':
                raise RuntimeError('First diagnostic failed')
            if status['status']=='complete':
                break
        if time.monotonic()>deadline:
            raise TimeoutError('First diagnostic not complete')
        time.sleep(5)
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        cmd=['docker','exec','glm53-repeat-v1','python3','-u','/experiment/harness/run_diagnostic.py','--label','d2']
        started=time.time()
        with (ROOT/'evidence/diagnostic2.log').open('x') as log:
            p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
            record={'status':'running','pid':p.pid,'command':cmd,'started_epoch':started}
            (ROOT/'evidence/diagnostic2_process.json').write_text(json.dumps(record,indent=2))
            code=p.wait()
        record.update(status='complete' if code==0 else 'failed',exit_code=code,elapsed_seconds=time.time()-started)
        (ROOT/'evidence/diagnostic2_process.json').write_text(json.dumps(record,indent=2))
        if code:
            raise RuntimeError('Second diagnostic failed')


if __name__=='__main__':
    main()
