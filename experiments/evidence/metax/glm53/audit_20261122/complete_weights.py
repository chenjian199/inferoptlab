"""Resume official model files and verify every SHA256; contains no credentials."""
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import requests
import sys

ROOT = Path('/models/GLM_Series/GLM-5.3-Flash-W8A8')
OUT = Path('/workspace/audit_20261122')
API = 'https://modelscope.cn/api/v1/models/metax-tech/GLM-5.3-Flash-W8A8'
REV = '6df7a9b0309e530094e29b2a6ced3e21bed6c16d'
lock = threading.Lock()
results = []

def log(event, **kw):
    with lock:
        print(json.dumps(dict(time=dt.datetime.now(dt.timezone.utc).isoformat(), event=event, **kw)), flush=True)

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def process(item):
    name, size, expected = item['Path'], item['Size'], item['Sha256']
    dest = ROOT / name
    if not dest.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Unsafe repository path')
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size == size and sha(dest) == expected:
        log('verified_existing', file=name, size=size)
        return dict(file=name, size=size, sha256=expected, status='verified_existing')
    if dest.exists():
        backup = dest.with_name(dest.name + '.before_repair_' + str(time.time_ns()))
        dest.rename(backup)
        log('preserved_mismatch', file=name, backup=backup.name)
    part = dest.with_name(dest.name + '.incomplete')
    for attempt in range(20):
        try:
            offset = part.stat().st_size if part.exists() else 0
            if offset > size:
                part.rename(part.with_name(part.name + '.oversize_' + str(time.time_ns())))
                offset = 0
            if offset < size:
                headers = {'Range': f'bytes={offset}-'} if offset else {}
                with requests.get(API+'/repo', params={'Revision':REV,'FilePath':name}, headers=headers, stream=True, timeout=(30,90)) as r:
                    r.raise_for_status()
                    if offset and (r.status_code != 206 or not r.headers.get('Content-Range','').startswith(f'bytes {offset}-')):
                        raise RuntimeError('Server did not honor resume range')
                    log('download_started', file=name, offset=offset, size=size, attempt=attempt)
                    last=time.monotonic()
                    with part.open('ab' if offset else 'wb') as f:
                        for b in r.iter_content(4*1024*1024):
                            if b:
                                f.write(b)
                                offset += len(b)
                            if offset > size: raise RuntimeError('Download exceeds manifest size')
                            if time.monotonic()-last > 60:
                                log('progress',file=name,bytes=offset,size=size)
                                last=time.monotonic()
            if part.stat().st_size != size: raise RuntimeError('Size mismatch')
            if sha(part) != expected:
                part.rename(part.with_name(part.name+'.badsha_'+str(time.time_ns())))
                raise RuntimeError('SHA256 mismatch; preserved corrupt partial')
            os.replace(part,dest)
            log('verified_download',file=name,size=size)
            return dict(file=name,size=size,sha256=expected,status='verified_download')
        except Exception as exc:
            log('retry',file=name,attempt=attempt,error=str(exc).split('?')[0])
            if attempt == 19: raise
            time.sleep(min(5*(attempt+1),30))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    r=requests.get(API+'/repo/files',params={'Revision':REV,'Recursive':'true'},timeout=60)
    r.raise_for_status()
    manifest=r.json()
    if manifest.get('Code') != 200: raise RuntimeError('Manifest request failed')
    (OUT/'model_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    files=[x for x in manifest['Data']['Files'] if x['Type']=='blob']
    total_files=len(files)
    if '--retry-failed' in sys.argv:
        prior=json.loads((OUT/'weight_verification.json').read_text())
        assert prior['revision']==REV
        (OUT/('verification_before_retry_'+str(time.time_ns())+'.json')).write_text(json.dumps(prior,indent=2))
        good={x['file']:x for x in prior['verified']}
        retained=[]
        pending=[]
        for item in files:
            p=ROOT/item['Path']
            if item['Path'] in good and p.exists() and p.stat().st_size==item['Size']:
                retained.append(good[item['Path']])
            else:pending.append(item)
        results.extend(retained)
        files=pending
    log('manifest',revision=REV,count=len(files),bytes=sum(x['Size'] for x in files))
    # Start missing files first while also checking existing content.
    files.sort(key=lambda x:(ROOT/x['Path']).exists())
    failures=[]
    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        futures={pool.submit(process,x):x['Path'] for x in files}
        for future in cf.as_completed(futures):
            try:results.append(future.result())
            except Exception as exc:failures.append(dict(file=futures[future],error=str(exc).split('?')[0]))
    report=dict(revision=REV,total_files=total_files,verified=results,failures=failures,complete=len(results)==total_files and not failures)
    (OUT/'weight_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    log('finished',complete=report['complete'],verified=len(results),failures=failures)
    if failures:raise SystemExit(1)

if __name__=='__main__':main()
