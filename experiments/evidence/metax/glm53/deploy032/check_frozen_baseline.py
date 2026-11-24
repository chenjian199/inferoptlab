"""Check that the frozen dependency image resolves the pinned mounted sources."""
import hashlib,importlib.metadata as md,json,subprocess
from pathlib import Path
import torch
from vllm.plugins import load_general_plugins

def main():
    load_general_plugins()
    import vllm,vllm_metax
    from vllm.platforms import current_platform
    checked=subprocess.run(['python3','-m','pip','check'],capture_output=True,text=True)
    report=dict(versions={n:md.version(n) for n in ['torch','triton','vllm','vllm-metax','mcoplib','transformers','compressed-tensors']},
                vllm_file=vllm.__file__,plugin_file=vllm_metax.__file__,
                platform=type(current_platform).__name__,device_count=torch.cuda.device_count(),
                pip_check_exit=checked.returncode,pip_check=checked.stdout+checked.stderr)
    assert report['device_count']==8
    assert report['vllm_file'].startswith('/work/src/vllm/')
    assert report['plugin_file'].startswith('/work/src/vllm-metax/')
    assert checked.returncode==0,report
    report['passed']=True
    Path('/work/evidence/frozen_baseline_check.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)
if __name__=='__main__':main()

