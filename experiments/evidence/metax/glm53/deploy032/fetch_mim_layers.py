"""Download immutable official image blobs; token is received only on stdin.

Completed blobs are SHA256-verified. Resume requires a correct 206 response;
when the server ignores Range, re-read and verify the retained prefix before
appending new bytes. This fallback preserves work but retransmits the prefix.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
import urllib.parse

import requests

ROOT = Path(__file__).resolve().parent / 'image_download'
ROOT.mkdir(exist_ok=True)
META = json.loads((ROOT.parent / 'mim_base_manifest.json').read_text())
HOST = 'https://mxcr.metax-tech.com'
REPO = 'mim-pub/vllm/model-free'
INPUT = json.loads(sys.stdin.readline())
TOKEN = INPUT['token']
PROXY = None
if INPUT.get('proxy_config'):
    cfg = json.loads(Path(INPUT['proxy_config']).read_text())
    user, password = cfg['authentication'][0].split(':', 1)
    PROXY = ('http://' + urllib.parse.quote(user, safe='') + ':' +
             urllib.parse.quote(password, safe='') + '@127.0.0.1:17890')
LOCK = threading.Lock()
STATE = {'started': time.time(), 'complete': False, 'blobs': {}}


def session():
    s = requests.Session()
    s.trust_env = False
    if PROXY:
        s.proxies.update(http=PROXY, https=PROXY)
    s.headers.update(Authorization='Bearer ' + TOKEN, **{'Accept-Encoding': 'identity'})
    return s


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def update(key, **values):
    with LOCK:
        STATE['blobs'].setdefault(key, {}).update(values)
        STATE['updated'] = time.time()
        temp = ROOT / 'progress.tmp'
        temp.write_text(json.dumps(STATE, indent=2))
        temp.replace(ROOT / 'progress.json')


def fetch(desc):
    key = desc['digest'].split(':')[1]
    total = desc['size']
    final = ROOT / key
    part = ROOT / (key + '.part')
    if final.exists() and final.stat().st_size == total and digest_file(final) == key:
        update(key, status='verified', size=total, current=total)
        return
    s = session()
    for attempt in range(1, 9):
        offset = part.stat().st_size if part.exists() else 0
        if offset == total:
            if digest_file(part) != key:
                raise RuntimeError('SHA256 mismatch: ' + key)
            part.replace(final)
            update(key, status='verified', current=total, size=total)
            return
        if offset > total:
            raise RuntimeError('Oversized checkpoint: ' + key)
        update(key, status='downloading', current=offset, size=total, attempt=attempt)
        try:
            headers = {'Range': f'bytes={offset}-'} if offset else {}
            with s.get(f'{HOST}/v2/{REPO}/blobs/sha256:{key}', headers=headers,
                       stream=True, timeout=(20, 90)) as r:
                r.raise_for_status()
                if r.status_code == 206:
                    expected = f'bytes {offset}-{total - 1}/{total}'
                    if r.headers.get('Content-Range') != expected:
                        raise RuntimeError('Invalid Content-Range')
                    skip = 0
                elif r.status_code == 200:
                    skip = offset
                else:
                    raise RuntimeError('Unexpected HTTP status')
                update(key, response=r.status_code, retransmit_prefix_bytes=skip)
                prefix_hash = hashlib.sha256()
                old_hash = digest_file(part) if skip else None
                position = 0
                last = time.monotonic()
                with part.open('ab') as out:
                    for chunk in r.iter_content(1024 * 1024):
                        if not chunk:
                            continue
                        if position < skip:
                            n = min(len(chunk), skip - position)
                            prefix_hash.update(chunk[:n])
                            position += n
                            chunk = chunk[n:]
                            if position == skip and prefix_hash.hexdigest() != old_hash:
                                raise RuntimeError('Retained prefix mismatch')
                        if chunk:
                            if out.tell() + len(chunk) > total:
                                raise RuntimeError('Oversized response')
                            out.write(chunk)
                            position += len(chunk)
                        if time.monotonic() - last >= 5:
                            out.flush()
                            update(key, current=out.tell(), response_bytes=position)
                            last = time.monotonic()
                    out.flush()
                    os.fsync(out.fileno())
            if part.stat().st_size != total:
                raise RuntimeError('Short response')
            if digest_file(part) != key:
                raise RuntimeError('SHA256 mismatch')
            part.replace(final)
            update(key, status='verified', current=total)
            print('VERIFIED', key[:12], total, flush=True)
            return
        except (requests.RequestException, OSError, RuntimeError) as exc:
            # Never print URLs, headers, or tokens.
            update(key, status='retry_wait', error_type=type(exc).__name__,
                   current=part.stat().st_size if part.exists() else 0)
            print('RETRY', key[:12], attempt, type(exc).__name__, flush=True)
            if isinstance(exc, requests.HTTPError) and exc.response.status_code in (401, 403):
                raise RuntimeError('Fresh authorized token required') from None
            if 'mismatch' in str(exc).lower() or 'oversized' in str(exc).lower():
                raise RuntimeError(str(exc)) from None
            time.sleep(min(attempt * 5, 30))
    raise RuntimeError('Transfer attempts exhausted: ' + key)


with session() as s:
    r = s.get(f"{HOST}/v2/{REPO}/manifests/{META['manifest_digest']}", timeout=30)
    r.raise_for_status()
    assert 'sha256:' + hashlib.sha256(r.content).hexdigest() == META['manifest_digest']
    (ROOT / 'manifest.raw.json').write_bytes(r.content)
    manifest = r.json()
descriptors = {d['digest']: d for d in [manifest['config'], *manifest['layers']]}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(fetch, sorted(descriptors.values(), key=lambda d: -d['size'])))
STATE['complete'] = True
update('summary', verified_count=len(descriptors))
print('ALL_BLOBS_VERIFIED', len(descriptors), flush=True)
