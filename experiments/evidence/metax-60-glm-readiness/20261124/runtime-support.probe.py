"""CPU-only local image audit; no GPU mapping, network or checkpoint payload read."""
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import traceback

result = {'packages': {}, 'module_origins': {}}
for name in ('torch', 'transformers', 'sglang', 'vllm', 'aiperf'):
    result['packages'][name] = [d.version for d in metadata.distributions()
                                if (d.metadata.get('Name') or '').lower() == name]
    try:
        spec = importlib.util.find_spec(name)
        result['module_origins'][name] = spec.origin if spec else None
    except Exception as exc:
        result['module_origins'][name] = str(exc)

config_path = Path('/model/config.json')
if config_path.exists():
    config = json.loads(config_path.read_text())
    text = config.get('text_config', config)
    result['model'] = {key: config.get(key) for key in ('model_type', 'architectures', 'transformers_version', 'auto_map')}
    result['model']['text_model_type'] = text.get('model_type')
    result['model']['config_sha256'] = hashlib.sha256(config_path.read_bytes()).hexdigest()
    try:
        from transformers import AutoConfig
        loaded = AutoConfig.from_pretrained('/model', local_files_only=True, trust_remote_code=False)
        result['autoconfig'] = {'status': 'passed', 'class': type(loaded).__name__}
    except Exception:
        result['autoconfig'] = {'status': 'failed', 'error': traceback.format_exc()}
    needles = set(config.get('architectures', []) + [text.get('model_type', ''), config.get('model_type', '')]) - {''}
    matches = []
    for package in ('sglang', 'vllm', 'transformers'):
        origin = result['module_origins'].get(package)
        if not origin or not Path(origin).is_file():
            continue
        base = Path(origin).parent
        for path in base.rglob('*.py'):
            contents = path.read_text(errors='replace')
            found = sorted(n for n in needles if n in contents)
            if found:
                matches.append({'package': package, 'path': str(path), 'terms': found})
    result['model_implementation_matches'] = matches
if result['packages']['aiperf']:
    for args in (['aiperf', '--version'], ['aiperf', 'profile', '--help']):
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=30)
            result[' '.join(args)] = {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
        except Exception as exc:
            result[' '.join(args)] = {'error': str(exc)}
print(json.dumps(result, indent=2))
