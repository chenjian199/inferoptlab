"""Build the pinned C500 BF16 sparse-prefill repair inside a MetaX dev image."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    parser.add_argument('--archive', type=Path, help='Use an existing source archive for offline builds')
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    if (work / 'build-source').exists():
        parser.error('work directory already contains build-source; choose a fresh directory')
    receipt = json.loads((package / 'source.json').read_text())
    archive = work / 'FlashMLA.tar.gz'
    if args.archive:
        if args.archive.resolve() != archive:
            shutil.copyfile(args.archive, archive)
    elif not archive.exists():
        url = f'https://codeload.github.com/MetaX-MACA/FlashMLA/tar.gz/{receipt["commit"]}'
        with urllib.request.urlopen(url, timeout=60) as response, archive.open('wb') as output:
            shutil.copyfileobj(response, output)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != receipt['archive_sha256']:
        raise ValueError('FlashMLA archive SHA256 does not match source.json')
    shutil.copyfile(package / 'source.json', work / 'source.json')
    subprocess.run([sys.executable, str(package / 'prepare_source.py'), str(work)], check=True)
    source = work / 'build-source'
    shutil.copyfile(package / 'setup_offset64.py', source / 'setup_offset64.py')
    env = dict(os.environ, MAX_JOBS='4', TORCH_CUDA_ARCH_LIST='8.0', CUCC_TARGETS='xcore1000')
    subprocess.run([sys.executable, 'setup_offset64.py', 'build_ext', '--inplace'], cwd=source, env=env, check=True)
    binaries = list(source.glob('_inferoptlab_flashmla_offset64*.so'))
    if len(binaries) != 1:
        raise RuntimeError('expected one compiled extension')
    binary = binaries[0]
    manifest = dict(source=receipt, python=sys.version, binary=str(binary),
                    sha256=hashlib.sha256(binary.read_bytes()).hexdigest())
    (work / 'build-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
