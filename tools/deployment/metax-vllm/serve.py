"""Launch an isolated eight-C500 GLM service and verify HTTP readiness."""
import argparse
import hashlib
import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--name', default='inferoptlab-glm53-vllm')
    parser.add_argument('--port', type=int, default=18081)
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--cache-dir', type=Path, help='Persist JIT caches for this exact image/GPU environment.')
    args = parser.parse_args()
    model = args.model.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', args.port))
    existing = subprocess.run(['docker', 'container', 'inspect', args.name], capture_output=True)
    if existing.returncode == 0:
        raise SystemExit('Container name already exists; choose a new name.')
    before = subprocess.check_output(['mx-smi'], text=True)
    (output / 'gpu-before.txt').write_text(before)
    if 'no process found' not in before.lower():
        raise SystemExit('GPUs have active processes; free the intended GPUs before running this check.')
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', args.image], text=True))[0]
    command = ['docker', 'run', '-d', '--pull=never', '--name', args.name,
               '--label', 'io.inferoptlab.task=glm53-source-reproduction',
               '--network=host', '--shm-size=32g', '--device=/dev/mxcd', '--device=/dev/dri',
               '--ulimit', 'memlock=-1:-1', '--ulimit', 'stack=67108864:67108864',
               '--mount', f'type=bind,source={model},target=/model,readonly',
               '-e', 'MACA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7', '-e', 'HF_HUB_OFFLINE=1',
               '-e', 'TRANSFORMERS_OFFLINE=1', '-e', 'VLLM_SERVER_DEV_MODE=1',
               image['Id'], '--model', '/model', '--tokenizer', '/model', '--reasoning-parser', 'glm47',
               '--served-model-name', 'glm53-flash', '--host', '127.0.0.1', '--port', str(args.port),
               '--tensor-parallel-size', '8', '--pipeline-parallel-size', '1',
               '--dtype', 'bfloat16', '--quantization', 'compressed-tensors', '--load-format', 'safetensors',
               '--max-model-len', '4096', '--max-num-seqs', '1', '--max-num-batched-tokens', '4096',
               '--gpu-memory-utilization', '0.9', '--enforce-eager', '--no-enable-prefix-caching',
               '--no-async-scheduling', '--disable-custom-all-reduce', '--enable-chunked-prefill',
               '--limit-mm-per-prompt', '{"image":0,"video":0}',
               '--attention-config', '{"indexer_kv_dtype":"auto"}']
    if args.cache_dir:
        cache = args.cache_dir.resolve()
        for name, target in [('root-cache', '/root/.cache'), ('triton', '/root/.triton')]:
            path = cache / name
            path.mkdir(parents=True, exist_ok=True)
            at = command.index(image['Id'])
            command[at:at] = ['--mount', f'type=bind,source={path},target={target}']
    config_bytes = (model / 'config.json').read_bytes()
    record = {'image_id': image['Id'], 'command': command, 'ready': False, 'port': args.port,
              'model_path': str(model), 'config_sha256': hashlib.sha256(config_bytes).hexdigest(),
              'model_config': json.loads(config_bytes)}
    (output / 'launch.json').write_text(json.dumps(record, indent=2))
    subprocess.run(command, check=True)
    deadline = time.monotonic() + args.timeout
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        while time.monotonic() < deadline:
            state = json.loads(subprocess.check_output(['docker', 'inspect', args.name], text=True))[0]['State']
            if not state['Running']:
                raise RuntimeError(f'Server exited: {state}')
            try:
                with opener.open(f'http://127.0.0.1:{args.port}/health', timeout=3) as response:
                    if response.status == 200:
                        record['ready'] = True
                        break
            except OSError:
                pass
            time.sleep(5)
        if not record['ready']:
            raise TimeoutError('Model service did not become ready within the startup budget.')
        (output / 'models.json').write_bytes(opener.open(f'http://127.0.0.1:{args.port}/v1/models', timeout=10).read())
        print('HTTP_READY', args.name, args.port, flush=True)
    except BaseException as exc:
        record['error'] = str(exc)
        subprocess.run(['docker', 'stop', '--time', '20', args.name], check=False)
        raise
    finally:
        logs = subprocess.run(['docker', 'logs', args.name], capture_output=True)
        (output / 'server.log').write_bytes(logs.stdout + logs.stderr)
        (output / 'launch.json').write_text(json.dumps(record, indent=2))

if __name__ == '__main__':
    main()
