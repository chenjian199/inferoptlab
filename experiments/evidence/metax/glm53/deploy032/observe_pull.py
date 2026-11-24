"""Attach a Docker pull client and persist non-secret layer progress."""
import base64
import http.client
import json
import socket
import time
import urllib.parse
from pathlib import Path

root = Path('/home/metax/glm53-vllm032')
manifest = json.loads((root/'evidence/mim_base_manifest.json').read_text())
cfg = json.loads(Path('/home/metax/.docker/config.json').read_text())
user, password = base64.b64decode(cfg['auths']['mxcr.metax-tech.com']['auth']).decode().split(':', 1)
auth = base64.urlsafe_b64encode(json.dumps({'username':user, 'password':password,
                                         'serveraddress':'mxcr.metax-tech.com'}).encode()).decode()

class Docker(http.client.HTTPConnection):
    def __init__(self):
        super().__init__('localhost', timeout=300)
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(300)
        self.sock.connect('/var/run/docker.sock')

c = Docker()
c.request('POST', '/v1.52/images/create?fromImage='+urllib.parse.quote(manifest['image'],safe=''),
          headers={'X-Registry-Auth':auth})
r = c.getresponse()
if r.status != 200:
    raise RuntimeError(f'Docker API status {r.status}: '+r.read().decode()[:1000])
progress = {'started':time.time(), 'layers':{}, 'complete':False}
last = 0
out = root/'evidence/pull_progress.json'
for line in r:
    item = json.loads(line)
    if 'error' in item:
        progress['error'] = item['error']
    if 'id' in item:
        progress['layers'][item['id']] = {'status':item.get('status'), **item.get('progressDetail',{})}
    if time.time()-last > 5:
        progress['updated'] = time.time()
        out.with_suffix('.tmp').write_text(json.dumps(progress,indent=2))
        out.with_suffix('.tmp').replace(out)
        last = time.time()
progress['complete'] = 'error' not in progress
progress['updated'] = time.time()
out.write_text(json.dumps(progress,indent=2))
print('PULL_COMPLETE', progress['complete'], flush=True)
c.close()
