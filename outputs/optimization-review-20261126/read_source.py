"""Read selected installed source files from the frozen image, without GPU access."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAGE = 'sha256:9d82e3b3cc52430770a02b00d8c763b62e9c8bc64c4be871d9be25148e4fdf8b'
probe = r'''
import hashlib,json
from pathlib import Path
root=Path('/opt/vllm-env/lib/python3.12/site-packages')
patterns=[
 'vllm/model_executor/custom_op.py',
 'vllm_metax/platform.py',
 'vllm_metax/model_executor/kernels/mhc/*.py',
 'vllm_metax/model_executor/layers/fused_moe/*align*.py',
 'vllm_metax/model_executor/layers/fused_moe/fused_moe.py',
 'vllm_metax/model_executor/layers/fused_moe/experts/triton_moe.py',
 'vllm_metax/model_executor/layers/fused_moe/config.py',
 'vllm_metax/patch/**/layernorm*.py',
 'vllm_metax/patch/**/rms*.py',
 'vllm/third_party/flash_linear_attention/ops/kda/*.py',
 'vllm_metax/models/glm5next/common/kda.py',
 'vllm_metax/models/glm5next/common/model.py',
 'vllm_metax/model_executor/layers/fused_moe/all2all_utils.py',
 'vllm_metax/model_executor/layers/fused_moe/experts/fused_batched_moe.py',
 'vllm_metax/model_executor/kernels/linear/scaled_mm/*.py',
 'vllm_metax/model_executor/kernels/linear/*.py',
 'vllm_metax/**/layernorm_gated*.py',
 'vllm/model_executor/layers/mamba/ops/scatter_states.py',
 'vllm/v1/utils.py',
 'vllm/model_executor/layers/fused_moe/moe_align_block_size.py',
]
files={}
for package in ['vllm_metax','vllm','fla','mcoplib']:
 for p in (root/package).rglob('*.py'):
  b=p.read_bytes()
  if any(s in b for s in [b'FusedRMSNormGated',b'def rms_norm_gated',b'fused_rms_norm_gated',b'MctlassScaledMMLinearKernel',b'def maybe_override_stage_block_size_m']):
   files[str(p.relative_to(root))]={'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode()}
for pattern in patterns:
 for p in root.glob(pattern):
  b=p.read_bytes();files[str(p.relative_to(root))]={'sha256':hashlib.sha256(b).hexdigest(),'text':b.decode()}
print(json.dumps(files))
'''
remote = "import subprocess,sys\np=subprocess.run(" + repr(['docker','run','--rm','-i','--network=none','--entrypoint','python3',IMAGE,'-']) + ",input=" + repr(probe.encode()) + ",capture_output=True)\nsys.stdout.buffer.write(p.stdout)\nsys.stderr.buffer.write(p.stderr)\nsys.exit(p.returncode)\n"
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','python3 -'],input=remote.encode(),capture_output=True,timeout=90)
if p.returncode: raise SystemExit(p.stderr.decode(errors='replace'))
data=json.loads(p.stdout)
manifest=[]
for name,entry in data.items():
 dest=ROOT/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(entry['text'],encoding='utf8',newline='\n')
 manifest.append({'path':name,'sha256':entry['sha256']})
(ROOT/'source-manifest.json').write_text(json.dumps({'image':IMAGE,'files':manifest},indent=2),encoding='utf8')
print('Read',len(manifest),'source files from frozen image; no GPU mounted.')
