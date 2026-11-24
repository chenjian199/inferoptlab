"""Task-scoped remote launcher; preserves existing containers and serializes TP8."""
import fcntl
import json
from pathlib import Path
import subprocess
import time

ROOT=Path('/home/metax/glm53-baseline-ops')
NAME='glm53-heval-v1'
LABEL='20261123_humaneval_v1'


def main():
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        info=json.loads(subprocess.check_output(['docker','inspect',NAME]))[0]
        assert info['Config']['Labels']['com.codex.task']=='glm53-baseline-ops'
        assert info['State']['Running']
        commands=[['docker','exec',NAME,'python3','/experiment/harness/check_frozen_baseline.py'],
                  ['docker','exec',NAME,'python3','-u','/experiment/harness/generate_humaneval.py','--label',LABEL]]
        for index,cmd in enumerate(commands):
            started=time.time()
            status=dict(command=cmd,status='running',started_epoch=started)
            output=ROOT/'evidence'/('preflight_process.json' if index==0 else 'generation_process.json')
            output.write_text(json.dumps(status,indent=2))
            with (ROOT/'evidence'/('preflight.log' if index==0 else 'generation.log')).open('x') as log:
                process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
                status['pid']=process.pid;output.write_text(json.dumps(status,indent=2))
                code=process.wait()
            status.update(status='complete' if code==0 else 'failed',exit_code=code,elapsed_seconds=time.time()-started)
            output.write_text(json.dumps(status,indent=2))
            if code:raise RuntimeError('Task process failed: '+str(code))


if __name__=='__main__':main()
