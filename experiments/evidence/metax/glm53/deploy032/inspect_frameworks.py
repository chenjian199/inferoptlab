"""Validate imported sources, GLM registration and native modules before loading weights."""
import importlib.metadata as md
import inspect
import json
import os
import subprocess
from pathlib import Path

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import torch
import vllm
import vllm_metax
from vllm.plugins import load_general_plugins
load_general_plugins()
from vllm.platforms import current_platform
from vllm.config import ModelConfig
from vllm.model_executor.models import ModelRegistry
import mcoplib
import vllm_metax.cumem_allocator

model = '/models/GLM-5.3-Flash-W8A8'
config = ModelConfig(model=model,tokenizer=model,dtype='bfloat16',
                     quantization='compressed-tensors',max_model_len=4096,
                     trust_remote_code=False)
cls, architecture = ModelRegistry.resolve_model_cls(config.hf_config.architectures,config)
assert vllm.__file__.startswith('/work/src/vllm/')
assert vllm_metax.__file__.startswith('/work/src/vllm-metax/')
assert type(current_platform).__module__.startswith('vllm_metax')
assert cls.__module__.startswith('vllm_metax.models.glm5next')
check = subprocess.run(['python','-m','pip','check'],capture_output=True,text=True)
report = {'vllm_file':vllm.__file__,'plugin_file':vllm_metax.__file__,
          'platform':type(current_platform).__module__+'.'+type(current_platform).__name__,
          'model_class':cls.__module__+'.'+cls.__name__,'model_file':inspect.getfile(cls),
          'architecture':architecture,'quantization':config.quantization,
          'versions':{name:md.version(name) for name in ['vllm','vllm-metax','torch','triton',
                     'transformers','compressed-tensors','mcoplib','mctlassEx','cmake','numba']},
          'native_libraries':sorted({line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines()
                                    if any(key in line for key in ['mcoplib','mcruntime','mccl','cumem_allocator'])}),
          'pip_check_exit':check.returncode,'pip_check':check.stdout+check.stderr}
Path('/work/evidence/framework_runtime.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
