"""Run diagnostic requests in the independent Linux AIPerf client container."""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client-root', type=Path, required=True,
                        help='Directory containing venv/ and a staged project/.')
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--run', required=True, help='New artifact directory name below client-root/experiments/.')
    parser.add_argument('--image', default='sha256:43af58b15b63b6095611b257590466632433d6786d66386839e1c5b8027d30ad')
    parser.add_argument('--url', default='http://127.0.0.1:18081')
    args = parser.parse_args()
    if not args.run or Path(args.run).name != args.run or args.run in {'.', '..'}:
        parser.error('--run must be a single directory name')
    client = args.client_root.resolve(strict=True)
    model = args.model.resolve(strict=True)
    for required in ['venv/bin/python', 'project/tools/deployment/metax-vllm/smoke_client.py']:
        if not (client / required).is_file():
            parser.error(f'Missing client prerequisite: {client / required}')
    output = client / 'experiments' / args.run
    if output.exists():
        parser.error(f'Artifacts already exist: {output}; choose a new --run')
    records = client / 'launches' / args.run
    records.mkdir(parents=True, exist_ok=False)
    # AIPerf 0.12 treats any nonempty offline variable (including "0") as true
    # and passes absolute local paths to snapshot_download. Empty both here;
    # tokenizer files still come from the read-only /model mount.
    command = ['docker', 'run', '--rm', '--pull=never', '--network=host',
               '--user', f'{os.getuid()}:{os.getgid()}',
               '--mount', f'type=bind,source={client},target=/work',
               '--mount', f'type=bind,source={model},target=/model,readonly',
               '--workdir', '/work/project', '-e', 'HF_HUB_OFFLINE=', '-e', 'TRANSFORMERS_OFFLINE=',
               '-e', 'HOME=/work', '-e', 'PYTHONPATH=/work/project',
               '-e', 'PATH=/work/venv/bin:/opt/conda/bin:/usr/local/bin:/usr/bin:/bin',
               '--entrypoint', '/work/venv/bin/python', args.image,
               '-u', 'tools/deployment/metax-vllm/smoke_client.py', '--tokenizer', '/model',
               '--url', args.url, '--output', '/work/experiments/' + args.run]
    record = {'command': command, 'artifacts': str(output), 'exit': None}
    start = time.monotonic()
    try:
        with (records / 'client.log').open('wb') as stream:
            result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT)
        record['exit'] = result.returncode
    finally:
        record['elapsed_s'] = time.monotonic() - start
        (records / 'launch.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, indent=2))
    raise SystemExit(record['exit'])


if __name__ == '__main__':
    main()
