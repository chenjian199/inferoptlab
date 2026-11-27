"""One synchronous C32 warmup reproduction; never a performance score."""
import json,time
from pathlib import Path
from benchmark.load import capacity_scan as cs,cached_decode as cd,dataset
from benchmark.load.adapters import vllm,sglang
from benchmark.common.io import json_write,utc_now
from tools.specs import read
root=Path.cwd();out=root/'diagnostic';out.mkdir(exist_ok=True)
matrix=read(root/'benchmark-matrix.yaml');row=cs.expand(matrix)[0]
dep,runtime=cs.deployment_specs(matrix,row,'/home/ubuntu/CJ_workspace/inferoptlab-scan-cache')
runtime['execution_profile']['environment']['CUDA_LAUNCH_BLOCKING']='1'
obs=out/'observations';server=vllm.Deployment(dep,runtime,out/'server.log',observation=dict(hooks=root/'tools/deployment/metax-vllm/observers',records=obs))
state=dict(diagnostic_only=True,status='starting',started_at=utc_now())
def save(**kw):
 state.update(kw);json_write(out/'state.json',state);print(json.dumps(state),flush=True)
try:
 command=server.launch();json_write(out/'launch.json',dict(command=command,container_id=server.container_id));save(container_id=server.container_id)
 sglang.wait_ready(dep['serving'],time.monotonic()+900,server)
 json_write(out/'server-info.json',cd.api(dep['serving']['url'],'/server_info?config_format=json'))
 tokenizer=dataset.load_tokenizer(matrix['target']['tokenizer_path'])
 prep=out/'c32';prep.mkdir(exist_ok=True);save(status='warming_c32')
 slots=cd.prepare_slots(tokenizer,dep['serving'],4096,32,1,matrix['requests']['seed'],prep,300)
 q=cd.qualify_slots(slots,dep['serving'],4096,obs,prep,300,output=2)
 save(status='passed' if q['valid'] else 'qualification_failed')
except Exception as exc:save(status='failed',error=repr(exc))
finally:
 server.close();save(container_id=None,finished_at=utc_now())
