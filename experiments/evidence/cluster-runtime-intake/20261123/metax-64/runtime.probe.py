"""CPU-only package and model-visibility audit; no existing container is changed."""
import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid


def packages():
    result = {'python': sys.version, 'executable': sys.executable, 'packages': {}, 'executables': {}}
    for name in ('vllm', 'sglang', 'aiperf', 'torch', 'transformers', 'triton'):
        try:
            result['packages'][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result['packages'][name] = None
        result['executables'][name] = shutil.which(name)
    return result


def audit(model_paths, image_filter=None):
    result = dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), host_packages=packages(), models=[], images=[])
    for location in model_paths:
        root = Path(location)
        entry = dict(path=location, exists=root.is_dir(), config_sha256=None, weight_files=[], errors=[])
        try:
            entry['config_sha256'] = hashlib.sha256((root/'config.json').read_bytes()).hexdigest()
            index = root/'model.safetensors.index.json'
            names = sorted(set(json.loads(index.read_text())['weight_map'].values())) if index.is_file() else sorted(p.name for p in root.glob('*.safetensors'))
            for name in names:
                if Path(name).name != name:
                    raise ValueError('shard index contains a non-basename')
                p = root/name
                with p.open('rb') as stream:
                    header = stream.read(8)
                entry['weight_files'].append(dict(name=name, size_bytes=p.stat().st_size, readable_header=len(header)==8))
            entry['tokenizer_readable'] = all((root/n).is_file() for n in ('tokenizer.json', 'tokenizer_config.json'))
        except Exception as exc:
            entry['errors'].append(str(exc))
        result['models'].append(entry)
    proc = subprocess.run(['docker','images','--no-trunc','--format','{{json .}}'], capture_output=True, text=True, timeout=30)
    result['docker_images_returncode'] = proc.returncode
    result['docker_images_stderr'] = proc.stderr
    images = {}
    for line in proc.stdout.splitlines():
        row = json.loads(line)
        images.setdefault(row['ID'], []).append(row['Repository']+':'+row['Tag'])
    source = '''import sys, shutil, importlib.metadata, json
r = dict(python=sys.version, executable=sys.executable, packages={}, executables={})
for name in ('vllm', 'sglang', 'aiperf', 'torch', 'transformers', 'triton'):
 try: r['packages'][name] = importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError: r['packages'][name] = None
 r['executables'][name] = shutil.which(name)
print(json.dumps(r))
'''
    for image, tags in images.items():
        if image_filter and image not in image_filter:
            continue
        name = 'inferoptlab-runtime-audit-'+uuid.uuid4().hex
        entry = dict(image_id=image, tags=tags)
        try:
            p = subprocess.run(['docker','run','--pull=never','--rm','-i','--network','none','--name',name,
                                '--entrypoint','python3',image,'-'],input=source,capture_output=True,text=True,timeout=45)
            entry.update(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
            if p.returncode == 0:
                entry['runtime'] = json.loads(p.stdout)
        except Exception as exc:
            entry['error'] = str(exc)
        finally:
            subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=15)
        result['images'].append(entry)
    return result

print(json.dumps(audit(['/mnt/ufs1/models/models/Qwen/Qwen3-0.6B', '/mnt/ufs1/models/models/metax-tech/GLM-5.3-Flash-W8A8', '/mnt/ufs1/models/models/metax-tech/GLM-5.3-W4A8', '/mnt/ufs1/models/models/metax-tech/GLM-5.3-W8A8'],None),indent=2))
