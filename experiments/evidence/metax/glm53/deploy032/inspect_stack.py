"""Record package/native identities in the isolated container, without loading a model."""
import importlib.metadata as md
import json
import os
import platform
import sys
from pathlib import Path

out = Path('/work/evidence')
out.mkdir(exist_ok=True)
packages = {d.metadata['Name']: d.version for d in md.distributions() if d.metadata['Name']}
report = {'python': sys.version, 'executable': sys.executable,
          'platform': platform.platform(), 'packages': packages,
          'env': {k: os.environ.get(k) for k in ['MACA_PATH', 'LD_LIBRARY_PATH',
                  'CUDA_PATH', 'USE_PRECOMPILED_KERNEL', 'PYTHONPATH']}}
for p in ['/opt/maca/Version.txt', '/opt/mxdriver/version']:
    if Path(p).is_file():
        report[p] = Path(p).read_text()
import torch
report['torch_file'] = torch.__file__
report['torch_version'] = torch.__version__
report['gpu_available'] = torch.cuda.is_available()
report['gpu_count'] = torch.cuda.device_count()
report['gpu_names'] = [torch.cuda.get_device_name(i) for i in range(report['gpu_count'])]
report['native_maps'] = sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                              if any(key in line for key in ['mcruntime', 'mccl', 'mxdriver', 'mcoplib'])})
(out/'base_stack.json').write_text(json.dumps(report, indent=2))
keys = ['torch','triton','vllm','vllm_metax','vllm-metax','mcoplib','transformers','compressed-tensors','mctlassEx']
print(json.dumps({**{k:v for k,v in report.items() if k != 'packages'},
                  'packages': {k:v for k,v in packages.items() if k in keys}}, indent=2), flush=True)
assert report['gpu_available'] and report['gpu_count'] == 8
