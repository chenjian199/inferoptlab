"""Resume large official vendor wheels with independently validated byte ranges."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import urlsplit, unquote
import zipfile
import requests

assert Path('/.dockerenv').exists() and os.environ.get('GLM53_ISOLATED_ENV') == '1'
job = json.loads(sys.stdin.readline())
url = job['url']
assert urlsplit(url).hostname == 'repos.metax-tech.com' and urlsplit(url).scheme == 'https'
name = unquote(urlsplit(url).path.rsplit('/',1)[1])
assert name.endswith('.whl') and '/' not in name
root = Path('/wheelhouse')
session = requests.Session(); session.trust_env = False
with session.get(url, headers={'Range':'bytes=0-0'}, stream=True, timeout=(20,60)) as response:
    assert response.status_code == 206
    match = re.fullmatch(r'bytes 0-0/(\d+)',response.headers.get('Content-Range',''))
    assert match
    total = int(match.group(1))
size = 32*1024*1024
parts = root/'.resume'/name
parts.mkdir(parents=True,exist_ok=True)
if job.get('partial'):
    partial = Path(job['partial'])
    assert str(partial).startswith('/tmp/pip-unpack-')
    if partial.exists():
        with partial.open('rb') as stream:
            for i in range((total+size-1)//size):
                block = stream.read(size)
                if not block:break
                p=parts/f'{i:04d}'
                if not p.exists() or p.stat().st_size < len(block):p.write_bytes(block)

state={'file':name,'total':total,'parts':{},'started':time.time(),'complete':False}
lock=threading.Lock()
progress=Path('/work/evidence')/(job['name']+'_resume.json')
def update(i,**values):
    with lock:
        state['parts'].setdefault(str(i),{}).update(values)
        tmp=progress.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2));tmp.replace(progress)

def fetch(i):
    start=i*size;end=min(total,start+size)-1;length=end-start+1
    p=parts/f'{i:04d}'
    s=requests.Session();s.trust_env=False
    for attempt in range(1,9):
        have=p.stat().st_size if p.exists() else 0
        assert have<=length
        if have==length:update(i,bytes=have,complete=True);return
        try:
            with s.get(url,headers={'Range':f'bytes={start+have}-{end}'},stream=True,timeout=(20,45)) as res:
                assert res.status_code==206
                assert res.headers.get('Content-Range')==f'bytes {start+have}-{end}/{total}'
                with p.open('ab') as out:
                    for block in res.iter_content(1024*1024):
                        assert out.tell()+len(block)<=length
                        out.write(block)
                    out.flush();os.fsync(out.fileno())
            update(i,bytes=p.stat().st_size,attempt=attempt)
        except requests.RequestException as exc:
            update(i,error=type(exc).__name__,attempt=attempt)
            time.sleep(2)
    if p.stat().st_size!=length:raise RuntimeError(f'Incomplete part {i}')
    update(i,bytes=length,complete=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    list(pool.map(fetch,range((total+size-1)//size)))
destination=root/('.'+name+'.part')
sha=hashlib.sha256()
with destination.open('wb') as out:
    for i in range((total+size-1)//size):
        block=(parts/f'{i:04d}').read_bytes();sha.update(block);out.write(block)
assert destination.stat().st_size==total
with zipfile.ZipFile(destination) as wheel:assert wheel.testzip() is None
destination.replace(root/name)
state.update(complete=True,sha256=sha.hexdigest(),zip_crc='pass')
update('summary',complete=True)
print('VENDOR_WHEEL_READY',name,sha.hexdigest(),flush=True)
