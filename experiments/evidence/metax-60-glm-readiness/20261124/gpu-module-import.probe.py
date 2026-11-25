import json, importlib, traceback
import torch
r={'device_count':torch.cuda.device_count(),'torch':torch.__version__}
try:
 r['device_name']=torch.cuda.get_device_name(0)
 r['capability']=torch.cuda.get_device_capability(0)
 m=importlib.import_module('sglang.srt.models.glm5_next')
 r['module']=m.__file__
 r['status']='passed'
except Exception:
 r['status']='failed';r['error']=traceback.format_exc()
print(json.dumps(r,indent=2))
