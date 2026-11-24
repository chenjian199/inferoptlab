"""Verify the distribution file inventory without executing project code."""
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'FILES_SHA256.json').read_text(encoding='utf-8'))
    expected = set()
    errors = []
    for item in manifest['files']:
        relative = item['path']
        parts = PurePosixPath(relative)
        if (parts.is_absolute() or '..' in parts.parts or '\\' in relative
                or ':' in relative or relative == 'FILES_SHA256.json'
                or relative in expected):
            raise ValueError('Unsafe or duplicate manifest path: ' + relative)
        expected.add(relative)
        path = root / relative
        if not path.resolve().is_relative_to(root) or path.is_symlink() or not path.is_file():
            errors.append('Missing or unsafe: ' + relative)
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        if path.stat().st_size != item['bytes'] or digest.hexdigest() != item['sha256']:
            errors.append('Changed: ' + relative)
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    for relative in sorted(actual - expected - {'FILES_SHA256.json'}):
        errors.append('Unexpected: ' + relative)
    if errors:
        print('\n'.join(errors))
        return 1
    print(f'PASS: {len(expected)} files match FILES_SHA256.json; no unexpected files.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
