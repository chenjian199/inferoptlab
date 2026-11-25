"""Prepare the fixed, reproducible C500 build context on a Linux build host."""
import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

SOURCES = {
    'vllm': ('vllm-project/vllm', '5df63a7203cdb9328d824a27b682e77c7b9928be'),
    'vllm-metax': ('MetaX-MACA/vLLM-metax', '0962c8735ffe4795800030680311410848512b82'),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    root = args.directory.resolve()
    assets = Path(__file__).resolve().parent
    required = ['Dockerfile', 'native-wheels.json', 'fetch_dependencies.py',
                'install_sdk.py', 'build_frameworks.py', 'patches/glm-w8a8.patch',
                'patches/moe_align_legacy_abi.py']
    missing = [name for name in required if not (assets / name).is_file()]
    if missing:
        raise SystemExit(f'Incomplete tool directory {assets}: {missing}. Copy the entire metax-vllm directory.')
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise SystemExit(f'Refusing to overwrite a nonempty build directory: {root}; use a new directory.')
    for directory in ('inputs', 'src', 'scripts', 'evidence', 'logs'):
        (root / directory).mkdir(parents=True, exist_ok=True)
    for source in assets.glob('*.py'):
        shutil.copy2(source, root / 'scripts' / source.name)
    for name in ('Dockerfile', 'native-wheels.json'):
        shutil.copy2(assets / name, root / name)
    shutil.copytree(assets / 'patches', root / 'patches', dirs_exist_ok=True)
    (root / '.dockerignore').write_text('logs\ninputs/*.tar.gz\ninputs/*.txt\ninputs/probe.whl\ninputs/wheelhouse/.resume\ninputs/wheelhouse/public\n')
    manifest = {}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for name, (repo, commit) in SOURCES.items():
        output = root / 'src' / name
        if output.exists() and any(output.iterdir()):
            raise SystemExit(f'Refusing to overwrite an existing checkout: {output}; use a new directory.')
        archive = root / 'inputs' / (name + '.tar.gz')
        with opener.open(f'https://codeload.github.com/{repo}/tar.gz/{commit}', timeout=180) as response, archive.open('wb') as stream:
            while block := response.read(1024 * 1024):
                stream.write(block)
        output.mkdir(exist_ok=True)
        subprocess.run(['tar', '-xzf', str(archive), '--strip-components=1', '-C', str(output)], check=True)
        manifest[name] = {'repository': 'https://github.com/' + repo, 'commit': commit,
                          'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'bytes': archive.stat().st_size}
    (root / 'evidence/sources.json').write_text(json.dumps(manifest, indent=2))
    subprocess.run(['python3', str(assets / 'fetch_dependencies.py'), str(root)], check=True)

if __name__ == '__main__':
    main()
