"""Install the pinned vendor ABI set from the completed local wheelhouse only."""
import hashlib
import importlib.metadata as md
import json
import os
import subprocess
import sys
from pathlib import Path
from packaging.requirements import Requirement
from packaging.utils import parse_wheel_filename
from urllib.parse import urlsplit, unquote, parse_qs
from html.parser import HTMLParser
import concurrent.futures
import requests

assert Path('/.dockerenv').exists() and os.environ.get('GLM53_ISOLATED_ENV') == '1'
requirements = Path('/work/src/vllm-metax/requirements/maca_private.txt')
exact_mcoplib = 'mcoplib==0.4.14+gf3794c4.maca3.9.0.31.torch2.10'
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get('href')
        if tag == 'a' and href:
            self.links.append(href)

def verify(wheel):
    digest = hashlib.sha256()
    with wheel.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            digest.update(block)
    name, _, _, _ = parse_wheel_filename(wheel.name)
    session = requests.Session()
    session.trust_env = False
    url = 'https://repos.metax-tech.com/r/maca-pypi/simple/' + name + '/'
    page = session.get(url, timeout=(20,60))
    page.raise_for_status()
    links = Links()
    links.feed(page.text)
    matching = [link for link in links.links
                if unquote(urlsplit(link).path.rsplit('/',1)[-1]) == wheel.name]
    assert len(matching) == 1, wheel.name
    expected = parse_qs(urlsplit(matching[0]).fragment)['sha256'][0]
    assert digest.hexdigest() == expected, wheel.name
    return {'file':wheel.name,'bytes':wheel.stat().st_size,'sha256':digest.hexdigest(),
            'repository_sha256':expected,'repository_hash_matches':True}

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    manifest = list(pool.map(verify, sorted(Path('/wheelhouse').glob('*.whl'))))
Path('/work/evidence/native_wheel_manifest.json').write_text(json.dumps(manifest,indent=2))
subprocess.run([sys.executable,'-m','pip','install','--no-index','--no-deps',
                '--find-links','/wheelhouse','-r',str(requirements),exact_mcoplib],check=True)
versions = {}
for line in requirements.read_text().splitlines():
    line = line.split('#',1)[0].strip()
    if not line or line.startswith('-'):
        continue
    req = Requirement(line)
    version = md.version(req.name)
    assert req.specifier.contains(version), (str(req),version)
    versions[req.name] = version
assert md.version('mcoplib') == exact_mcoplib.split('==')[1]
Path('/work/evidence/native_installed_versions.json').write_text(json.dumps(versions,indent=2))
print('NATIVE_INSTALL_READY',json.dumps(versions),flush=True)
