"""Check historical runner flow in one more fresh engine, after diagnostics."""
import fcntl
import json
from pathlib import Path
import subprocess
import time

ROOT=Path('/home/metax/glm53-repeatability-20261123')


def main():
    deadline=time.monotonic()+20000
    while True:
        p=ROOT/'evidence/diagnostic2_process.json'
        try:
            status=json.loads(p.read_text()) if p.exists() else {}
        except json.JSONDecodeError:
            status={}
        if status.get('status')=='failed':raise RuntimeError('Prior diagnostic failed')
        if status.get('status')=='complete':break
        if time.monotonic()>deadline:raise TimeoutError('Prior diagnostic incomplete')
        time.sleep(5)
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for filename in ['prompt_manifest.json','generation_environment.json','final_worker_provenance.json','frozen_baseline_check.json']:
            assert not (ROOT/'evidence'/filename).exists(),'Refuse evidence overwrite'
        commands=[['docker','exec','glm53-repeat-v1','python3','/experiment/harness/check_frozen_baseline.py'],
            ['docker','exec','glm53-repeat-v1','python3','-u','/experiment/harness/run_legacy_control.py','--label','legacy_control'],
            ['python3','-u',str(ROOT/'harness/evaluate_humaneval.py'),'--run',str(ROOT/'runs/legacy_control_smoke32')]]
        record={'status':'running','started_epoch':time.time(),'commands':commands,'steps':[]}
        target=ROOT/'evidence/legacy_control_process.json'
        target.write_text(json.dumps(record,indent=2))
        with (ROOT/'evidence/legacy_control.log').open('x') as log:
            for cmd in commands:
                child=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
                record['current_pid']=child.pid;target.write_text(json.dumps(record,indent=2))
                code=child.wait();record['steps'].append({'command':cmd,'exit_code':code})
                if code:
                    record.update(status='failed',exit_code=code);target.write_text(json.dumps(record,indent=2))
                    raise RuntimeError('Legacy control failed')
        record.update(status='complete',exit_code=0,elapsed_seconds=time.time()-record['started_epoch'])
        target.write_text(json.dumps(record,indent=2))


if __name__=='__main__':main()
