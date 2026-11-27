import subprocess
p=subprocess.run(['docker', 'exec', 'glm53-vllm032', '/tmp/lyq-metax60-client/venv/bin/python', '-c', "import importlib.metadata as m,json; print(json.dumps({k:m.version(k) for k in ['aiperf','transformers']}))"],capture_output=True,text=True)
print(p.stdout)
if p.returncode:raise RuntimeError(p.stderr)
