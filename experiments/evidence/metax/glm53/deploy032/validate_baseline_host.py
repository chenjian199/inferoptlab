"""Validate the completed baseline image in a fresh, disposable container."""
import json,subprocess,time
from pathlib import Path

ROOT=Path('/home/metax/glm53-vllm032')
def main():
    evidence=ROOT/'evidence'
    deadline=time.monotonic()+1800
    while not (evidence/'frozen_baseline.json').exists():
        if time.monotonic()>deadline:raise TimeoutError('Baseline image was not completed')
        time.sleep(3)
    image=json.loads((evidence/'frozen_baseline.json').read_text())
    assert image['tag']=='glm53-vllm032:verified-20261122'
    cmd=['docker','run','--rm','--init','--name','glm53-vllm032-baseline-check',
         '--network=none','--device=/dev/dri','--device=/dev/mxcd','--group-add','video',
         '--mount',f'type=bind,source={ROOT}/src,target=/work/src,readonly',
         '--mount',f'type=bind,source={ROOT}/scripts,target=/work/scripts,readonly',
         '--mount',f'type=bind,source={ROOT}/evidence,target=/work/evidence',
         '-e','PYTHONDONTWRITEBYTECODE=1','-e','USE_PRECOMPILED_KERNEL=1',
         '-e','MACA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7',
         '--entrypoint','python3',image['image_id'],'/work/scripts/check_frozen_baseline.py']
    started=time.monotonic()
    with (evidence/'frozen_baseline_check.log').open('w') as log:
        p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    result=dict(command=cmd,exit_code=p.returncode,elapsed_seconds=time.monotonic()-started)
    (evidence/'frozen_baseline_check_run.json').write_text(json.dumps(result,indent=2))
    assert p.returncode==0,result
if __name__=='__main__':main()

