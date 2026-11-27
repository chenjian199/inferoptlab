import json
import os
from pathlib import Path
import subprocess
import time

from benchmark.load import cached_decode as c

ROOT=Path('/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124')
OUT=ROOT/'experiments/evidence/glm53-cached-decode-20261126'
directory=OUT/('observed-proof-4k-c2-'+str(time.time_ns()))
directory.mkdir(exist_ok=True)
serving=dict(url='http://127.0.0.1:18082',served_model='glm53-flash',
    tokenizer_path='/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8')
try:
    for _ in range(100):
        try:c.api(serving['url'],'/health',timeout=3);break
        except Exception:time.sleep(10)
    tokenizer=c.dataset.load_tokenizer(serving['tokenizer_path'])
    slots=c.prepare_slots(tokenizer,serving,4096,2,1,20261125,directory,900)
    qualified=c.qualify_slots(slots,serving,4096,OUT/'observations-tp8',directory,900)
    print(json.dumps({k:v for k,v in qualified.items() if k not in ['attention','engine']}),flush=True)
    # This first observer instance predates the MLA hook. It qualifies the
    # scheduler and KDA path only; production still requires both builders.
    assert qualified['engine']['valid'],qualified['engine']['issues']
    assert all(r['valid'] for r in qualified['cache'])
    assert qualified['attention'] and all(r['num_prefills']==0 for r in qualified['attention'])
    fixture,expected=c.make_fixture(slots,20,4,serving['served_model'],directory.name)
    c.json_write(directory/'inputs.json',fixture)
    cmd=c.profile_command('/work/venv/bin/aiperf',serving,directory/'inputs.json',directory/'aiperf',2,8,900)
    env=os.environ.copy();env['PYTHONPATH']=str(ROOT/'benchmark/load/aiperf_hooks')+os.pathsep+str(ROOT)
    env['AIPERF_DATASET_MMAP_CACHE_ENABLED']='false'
    c.json_write(directory/'command.json',dict(argv=cmd,pythonpath=env['PYTHONPATH']))
    with (directory/'aiperf.log').open('w') as log:
        result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=1200)
    assert result.returncode==0,result.returncode
    profile=c.validate_profile(directory/'aiperf',expected,slots,4096,20)
    engine=c.scheduler_evidence(c.observations(OUT/'observations-tp8','scheduler'),expected,4096,20)
    c.json_write(directory/'validation.json',dict(profile=profile,engine=engine))
    assert profile['valid'] and engine['valid'],[profile['issues'],engine['issues']]
    c.json_write(directory/'status.json',dict(status='passed'))
except Exception as exc:
    c.json_write(directory/'status.json',dict(status='failed',error=repr(exc)))
    raise
