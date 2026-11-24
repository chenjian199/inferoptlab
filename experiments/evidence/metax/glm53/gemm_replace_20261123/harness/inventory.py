import hashlib,importlib.metadata as md,json,subprocess
from pathlib import Path
import torch,triton
from vllm.plugins import load_general_plugins
load_general_plugins()
import mcoplib
from vllm_metax.model_executor.layers.quantization import _python_api_ops

r=Path('/experiment/evidence'); files=[]
for base,patterns in [('/opt/maca/lib',['*blas*','*mctlass*']),('/opt/maca/include',['*blas*','*mctlass*']),('/opt/maca/mxgpu_llvm/bin',['mxcc','clang++']),('/opt/conda/lib/python3.12/site-packages',['*mctlass*'])]:
 for pattern in patterns:
  for p in Path(base).glob(pattern):files.append({'path':str(p),'resolved':str(p.resolve()),'is_dir':p.is_dir()})
ops=[]
for p in Path(mcoplib.__file__).parent.glob('*'):
 if any(s in p.name.lower() for s in ['mctlass','gemm','cutlass']):
  ops.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None})
maps=sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines() if '/' in line and any(k in line.lower() for k in ['mcblas','mctlass','mcoplib'])})
report={'versions':{n:md.version(n) for n in ['torch','triton','mcoplib','vllm','vllm-metax']},'torch_file':torch.__file__,'triton_file':triton.__file__,'mcoplib_file':mcoplib.__file__,'device_count':torch.cuda.device_count(),'files':files,'ops':ops,'loaded_libraries':maps,'dispatch':torch._C._dispatch_dump('vllm::mctlassEx_w8a8_scaled_mm_azp')}
for path in ['/opt/maca/mxgpu_llvm/bin/mxcc','/opt/maca/bin/mxcc']:
 if Path(path).exists():
  p=subprocess.run([path,'--version'],capture_output=True,text=True);report['compiler']={'path':path,'exit_code':p.returncode,'output':p.stdout+p.stderr};break
(r/'stack_inventory.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
