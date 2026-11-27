from pathlib import Path
import subprocess
import tarfile

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
names=['benchmark/load/cached_decode.py','benchmark/load/adapters/vllm.py','benchmark/load/aiperf_hooks/sitecustomize.py',
    'tools/deployment/metax-vllm/observers/sitecustomize.py','tools/specs.py','schemas/definitions/cached-decode.json',
    'recipes/runtimes/metax60-vllm-glm53-cached-decode.yaml',
    'recipes/plans/benchmark/glm53-vllm/cached-decode.yaml','outputs/glm53-cached-decode-20261126/prove_observed.py']
for folder in ['recipes/deployments/glm53-flash/c500/vllm/cached-decode','recipes/workloads/glm53-vllm/cached-decode']:
    names.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).glob('*.yaml'))
archive=OUT/'code.tar'
with tarfile.open(archive,'w') as tar:
    for name in names:tar.add(ROOT/name,arcname=name)
remote='/home/ubuntu/CJ_workspace/inferoptlab-scan-20261124'
subprocess.run(['scp','-o','BatchMode=yes','-o','ConnectTimeout=8',str(archive),'metax-60:'+remote+'/experiments/evidence/glm53-cached-decode-20261126/code.tar'],check=True,timeout=45)
subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=8','metax-60','tar -xf '+remote+'/experiments/evidence/glm53-cached-decode-20261126/code.tar -C '+remote],check=True,timeout=30)
