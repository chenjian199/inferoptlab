import fcntl,json,subprocess,time
from pathlib import Path

ROOT=Path('/home/metax/glm53-recovery-20261123/pilot')


def main():
    e=ROOT/'evidence'
    assert json.loads((e/'communication_check.json').read_text())['status']=='passed'
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        commands=[['docker','exec','glm53-gemm-recovery-v1','python3','-u','/experiment/harness/run_model.py']]
        commands += [['python3','-u',str(ROOT/'harness/evaluate_humaneval.py'),'--run',str(ROOT/'runs'/name)] for name in ['baseline32','candidate32','rollback4']]
        record={'status':'running','started_epoch':time.time(),'commands':commands,'steps':[]}
        target=e/'model_process.json';assert not target.exists()
        with (e/'model.log').open('x') as log:
            for cmd in commands:
                p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
                record['current_pid']=p.pid;target.write_text(json.dumps(record,indent=2))
                code=p.wait();record['steps'].append({'command':cmd,'exit_code':code})
                if code:
                    record.update(status='failed',exit_code=code);target.write_text(json.dumps(record,indent=2));raise RuntimeError('Pilot failed')
        record.update(status='complete',exit_code=0,elapsed_seconds=time.time()-record['started_epoch'])
        target.write_text(json.dumps(record,indent=2))


if __name__=='__main__':main()
