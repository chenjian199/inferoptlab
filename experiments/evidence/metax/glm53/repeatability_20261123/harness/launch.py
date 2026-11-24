"""Serial independent Python engines under the shared TP8 lock."""
import fcntl
import json
from pathlib import Path
import subprocess
import time

ROOT = Path('/home/metax/glm53-repeatability-20261123')
NAME = 'glm53-repeat-v1'


def save(path, value):
    temp = path.with_suffix('.partial')
    temp.write_text(json.dumps(value, indent=2))
    temp.replace(path)


def main():
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        info = json.loads(subprocess.check_output(['docker','inspect',NAME]))[0]
        assert info['Config']['Labels']['com.codex.task'] == 'glm53-repeatability'
        for process in ['a','b','c']:
            cmd = ['docker','exec',NAME,'python3','-u','/experiment/harness/run_probe.py','--process',process]
            status = dict(status='running', command=cmd, started_epoch=time.time())
            target = ROOT/'evidence'/('process_'+process+'.json')
            assert not target.exists()
            with (ROOT/'evidence'/('process_'+process+'.log')).open('x') as log:
                child = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
                status['pid'] = child.pid; save(target,status)
                code = child.wait()
            status.update(status='complete' if code==0 else 'failed', exit_code=code,
                          elapsed_seconds=time.time()-status['started_epoch'])
            save(target,status)
            if code:
                raise RuntimeError('Generation process failed: '+process)
            folders = sorted((ROOT/'runs').glob('process_'+process+'_*'))
            for folder in folders:
                score_cmd = ['python3','-u',str(ROOT/'harness/evaluate_humaneval.py'),'--run',str(folder)]
                with (folder/'score.log').open('x') as log:
                    scored = subprocess.run(score_cmd, stdout=log, stderr=subprocess.STDOUT)
                if scored.returncode:
                    raise RuntimeError('Scoring failed: '+str(folder))
        save(ROOT/'evidence/launcher_complete.json', dict(status='complete', completed_epoch=time.time()))


if __name__ == '__main__':
    main()
