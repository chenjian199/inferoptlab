"""Read and fingerprint every indexed safetensors shard, without loading a model.

This establishes a local byte identity, not upstream authenticity or numerical
correctness. Output is exclusive; a failed/interrupted run cannot look complete.
Uses only the Python standard library so it can run on a benchmark host.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import struct


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def signature(path):
    s = path.stat()
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def fingerprint(root, progress=None):
    root = Path(root).resolve(strict=True)
    index_path = root / 'model.safetensors.index.json'
    index_signature = signature(index_path)
    index_bytes = index_path.read_bytes()
    index = json.loads(index_bytes)
    weight_map = index['weight_map']
    if not weight_map or not all(isinstance(k, str) and isinstance(v, str) for k, v in weight_map.items()):
        raise ValueError('invalid or empty weight map')
    names = sorted(set(weight_map.values()))
    paths = []
    for name in names:
        if Path(name).name != name or '/' in name or '\\' in name:
            raise ValueError('shard name must be a basename')
        p = (root / name).resolve(strict=True)
        if not p.is_relative_to(root):
            raise ValueError('shard resolves outside checkpoint directory')
        paths.append(p)
    initial = {name: signature(p) for name, p in zip(names, paths)}
    files, actual = [], {}
    for name, p in zip(names, paths):
        total = initial[name][2]
        h = hashlib.sha256()
        with p.open('rb') as f:
            prefix = f.read(8)
            if len(prefix) != 8:
                raise ValueError('truncated header: ' + name)
            length = struct.unpack('<Q', prefix)[0]
            if not 0 < length <= min(64 * 1024 * 1024, total - 8):
                raise ValueError('invalid header size: ' + name)
            header_bytes = f.read(length)
            header = json.loads(header_bytes)
            h.update(prefix)
            h.update(header_bytes)
            intervals = []
            for tensor, spec in header.items():
                if tensor == '__metadata__':
                    continue
                if tensor in actual:
                    raise ValueError('duplicate tensor: ' + tensor)
                lo, hi = spec['data_offsets']
                if not isinstance(lo, int) or not isinstance(hi, int) or not 0 <= lo <= hi <= total - 8 - length:
                    raise ValueError('invalid tensor offsets: ' + tensor)
                intervals.append((lo, hi))
                actual[tensor] = name
            cursor = 0
            for lo, hi in sorted(intervals):
                if lo != cursor:
                    raise ValueError('payload gap or overlap: ' + name)
                cursor = hi
            if cursor != total - 8 - length:
                raise ValueError('unaccounted payload bytes: ' + name)
            consumed = 8 + length
            for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
                h.update(chunk)
                consumed += len(chunk)
            if consumed != total:
                raise ValueError('file size changed while hashing: ' + name)
        if signature(p) != initial[name]:
            raise ValueError('shard changed while hashing: ' + name)
        item = dict(name=name, size_bytes=total, sha256=h.hexdigest(),
                    header_sha256=hashlib.sha256(prefix + header_bytes).hexdigest())
        files.append(item)
        if progress:
            progress(dict(completed=len(files), total=len(names), file=item))
    if actual != weight_map:
        raise ValueError('index/header tensor map mismatch')
    if signature(index_path) != index_signature or index_path.read_bytes() != index_bytes:
        raise ValueError('index changed while hashing')
    if any(signature(p) != initial[n] for n, p in zip(names, paths)):
        raise ValueError('a shard changed during the full checkpoint pass')
    identity = [dict(name=f['name'], size_bytes=f['size_bytes'], sha256=f['sha256']) for f in files]
    return dict(format_version=1, status='completed', checkpoint_path=str(root),
                captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                verification_scope='all_indexed_payload_bytes_and_index_headers',
                upstream_authenticity_verified=False, numerical_correctness_verified=False,
                weights_sha256=digest(identity),
                weights_digest_algorithm='sha256_canonical_json_sorted_name_size_bytes_sha256',
                index_sha256=hashlib.sha256(index_bytes).hexdigest(),
                shard_count=len(files), tensor_count=len(actual),
                total_file_bytes=sum(f['size_bytes'] for f in files), shards=files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the output before expensive I/O. A failure leaves explicit evidence.
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(dict(status='running'), stream)
    result = dict(status='interrupted')
    try:
        result = fingerprint(args.checkpoint, lambda x: print(json.dumps(x), flush=True))
        result['probe_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    except Exception as exc:
        result = dict(status='failed', error=str(exc))
        raise
    finally:
        temporary = args.out.with_name(args.out.name + '.tmp')
        with temporary.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
        os.replace(temporary, args.out)


if __name__ == '__main__':
    main()
