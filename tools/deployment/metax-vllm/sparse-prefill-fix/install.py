"""Install the repair into the Python environment that runs vLLM workers."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sysconfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--sha256', required=True, help='SHA256 from build-manifest.json or verified-binary.json')
    args = parser.parse_args()
    binary = args.binary.resolve()
    if hashlib.sha256(binary.read_bytes()).hexdigest() != args.sha256:
        parser.error('extension SHA256 mismatch')
    if binary.name != '_inferoptlab_flashmla_offset64' + sysconfig.get_config_var('EXT_SUFFIX'):
        parser.error('extension filename does not match this Python/platform ABI')
    package = Path(__file__).resolve().parent
    site = Path(sysconfig.get_paths()['platlib'])
    targets = [(binary, site / binary.name),
               (package.parent / 'observers/sparse_prefill_repair.py', site / '_inferoptlab_sparse_prefill_adapter.py'),
               (package / 'startup.py', site / '_inferoptlab_sparse_prefill_startup.py')]
    for source, target in targets:
        if source != target:
            shutil.copyfile(source, target)
    # Enable startup only after all modules have been installed successfully.
    (site / 'inferoptlab_sparse_prefill.pth').write_text('import _inferoptlab_sparse_prefill_startup\n', encoding='utf-8')
    print(json.dumps(dict(installed_to=str(site), sha256=args.sha256,
                         enable='INFEROPTLAB_SPARSE_PREFILL_OFFSET64=1'), indent=2))


if __name__ == '__main__':
    main()
