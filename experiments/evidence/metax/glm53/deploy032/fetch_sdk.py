"""Range-validated resumable SDK download from the official signed object URL."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import requests

root = Path('/home/metax/glm53-vllm032/downloads')
root.mkdir(exist_ok=True)
url = json.loads(sys.stdin.readline())['url']
name = 'maca-sdk-3.9.0.29-deb-x86_64.tar.xz'
total = 6392534772
chunk_size = 128 * 1024 * 1024
parts = root / (name + '.parts')
parts.mkdir(exist_ok=True)
lock = threading.Lock()
state = {'started': time.time(), 'total': total, 'parts': {}, 'complete': False}


def progress(i, **values):
    with lock:
        state['parts'].setdefault(str(i), {}).update(values)
        state['updated'] = time.time()
        tmp = root / 'sdk_progress.tmp'
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(root / 'sdk_progress.json')


def fetch(i):
    base = i * chunk_size
    end = min(total, base + chunk_size) - 1
    size = end - base + 1
    path = parts / f'{i:04d}'
    s = requests.Session()
    s.trust_env = False
    for attempt in range(1, 9):
        have = path.stat().st_size if path.exists() else 0
        assert have <= size
        if have == size:
            progress(i, current=have, size=size, complete=True)
            return
        start = base + have
        progress(i, current=have, size=size, complete=False, attempt=attempt)
        try:
            with s.get(url, headers={'Range': f'bytes={start}-{end}'}, stream=True,
                       timeout=(20, 60)) as r:
                r.raise_for_status()
                assert r.status_code == 206, 'Server did not honor Range'
                assert r.headers.get('Content-Range') == f'bytes {start}-{end}/{total}'
                last = time.monotonic()
                with path.open('ab') as out:
                    for b in r.iter_content(1024 * 1024):
                        assert out.tell() + len(b) <= size
                        out.write(b)
                        if time.monotonic() - last > 5:
                            out.flush()
                            progress(i, current=out.tell())
                            last = time.monotonic()
                    out.flush()
                    os.fsync(out.fileno())
            if path.stat().st_size == size:
                progress(i, current=size, complete=True)
                print('PART_READY', i, flush=True)
                return
        except requests.RequestException as exc:
            progress(i, error_type=type(exc).__name__)
            time.sleep(min(attempt * 2, 10))
    raise RuntimeError(f'Part {i} exhausted retries')


with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(fetch, range((total + chunk_size - 1) // chunk_size)))
temporary = root / (name + '.part')
sha = hashlib.sha256()
md5 = hashlib.md5()
with temporary.open('wb') as out:
    for i in range((total + chunk_size - 1) // chunk_size):
        with (parts / f'{i:04d}').open('rb') as f:
            for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
                sha.update(b)
                md5.update(b)
                out.write(b)
assert temporary.stat().st_size == total
temporary.replace(root / name)
state.update(complete=True, sha256=sha.hexdigest(), md5=md5.hexdigest())
progress('summary', complete=True)
print('SDK_READY', sha.hexdigest(), flush=True)
