"""Read-only host/container inventory; never starts a model or changes a service."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess


def run(argv, timeout=25):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, errors='replace', timeout=timeout)
        return dict(code=p.returncode, stdout=p.stdout, stderr=p.stderr)
    except Exception as exc:
        return dict(error=repr(exc))


def safe_env(env):
    prefixes = ('VLLM_', 'MACA_', 'MCCL_', 'NCCL_', 'TORCH_', 'TRITON_', 'OMP_', 'MKL_', 'CUDA_',
                'INFEROPTLAB_', 'AIPERF_')
    exact = {'PATH', 'PYTHONPATH', 'LD_LIBRARY_PATH', 'VIRTUAL_ENV', 'CONDA_PREFIX'}
    return {k: v for s in env or [] for k, _, v in [s.partition('=')]
            if (k.startswith(prefixes) or k in exact) and not re.search('TOKEN|SECRET|PASSWORD|API_KEY', k)}


def safe_args(args):
    result = []; redact = False
    for arg in args or []:
        if redact: result.append('<redacted>'); redact=False; continue
        if re.search(r'^--(?:api-key|token|password|secret)(?:=|$)', arg):
            result.append(arg.split('=')[0]+'=<redacted>'); redact='=' not in arg
        else: result.append(arg)
    return result


out = dict(host=socket.gethostname(), captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
           kernel=run(['uname', '-a']), docker_version=run(['docker', 'version', '--format', '{{json .Server}}']),
           gpu=run(['/opt/mxdriver/bin/mx-smi']), cpu=run(['lscpu']))
listed = run(['docker', 'ps', '-a', '--no-trunc', '--format', '{{json .}}'])
rows = [json.loads(line) for line in listed.get('stdout', '').splitlines() if line.strip()]
out['container_index'] = [{k:r[k] for k in ['ID','Names','Image','State','Status']} for r in rows]
selected = [r for r in rows if re.search('glm|inferoptlab|c500-validation',r['Names'],re.I)]
out['containers'] = []
images = set()
for row in selected:
    raw = run(['docker', 'inspect', row['ID']])
    if raw.get('code') != 0: continue
    data = json.loads(raw['stdout'])[0]; config=data['Config']; host=data['HostConfig']; images.add(data['Image'])
    out['containers'].append(dict(id=data['Id'], name=data['Name'], created=data['Created'], state=data['State'],
        image_id=data['Image'], image_ref=config['Image'], entrypoint=safe_args(config.get('Entrypoint')),
        cmd=safe_args(config.get('Cmd')), env=safe_env(config.get('Env')), labels=config.get('Labels'),
        mounts=data.get('Mounts'), working_dir=config.get('WorkingDir'), network=host.get('NetworkMode'),
        ipc=host.get('IpcMode'), shm_size=host.get('ShmSize'), privileged=host.get('Privileged'),
        cpuset=host.get('CpusetCpus'), cpu_quota=host.get('CpuQuota'), memory_limit=host.get('Memory'),
        devices=host.get('Devices'), device_requests=host.get('DeviceRequests')))
out['images'] = []
for image in sorted(images):
    raw=run(['docker','image','inspect',image])
    if raw.get('code') != 0: continue
    d=json.loads(raw['stdout'])[0]
    out['images'].append(dict(id=d['Id'], tags=d.get('RepoTags'), digests=d.get('RepoDigests'),
        created=d['Created'], size=d.get('Size'), labels=d['Config'].get('Labels'),
        env=safe_env(d['Config'].get('Env')), layers=d.get('RootFS',{}).get('Layers')))
out['workspace_dirs'] = {}
for root in ['/home/ubuntu','/home/ubuntu/CJ_workspace','/home/ubuntu/DCC_workspace','/data/heyi/c500-glm5.3']:
    p=Path(root)
    if p.is_dir():
        out['workspace_dirs'][root]=[dict(name=q.name,directory=q.is_dir()) for q in sorted(p.iterdir()) if not q.name.startswith('.')]
out['model_metadata'] = []
model_roots={m['Source'] for c in out['containers'] for m in c['mounts'] if 'GLM' in m['Source'] and Path(m['Source']).is_dir()}
for root in sorted(model_roots):
    p=Path(root); item=dict(path=root, realpath=str(p.resolve()),files=[])
    for q in sorted(p.iterdir()):
        if not q.is_file(): continue
        record=dict(name=q.name,bytes=q.stat().st_size)
        if q.name in ['config.json','tokenizer_config.json','generation_config.json','model.safetensors.index.json']:
            payload=q.read_bytes();record['sha256']=hashlib.sha256(payload).hexdigest();record['content']=json.loads(payload)
        if q.name in ['tokenizer.json','special_tokens_map.json']:record['sha256']=hashlib.sha256(q.read_bytes()).hexdigest()
        item['files'].append(record)
    out['model_metadata'].append(item)
print(json.dumps(out,ensure_ascii=False))
