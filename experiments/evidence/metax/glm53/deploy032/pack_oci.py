"""Package verified official blobs without recompressing or changing the manifest."""
import hashlib
import io
import json
from pathlib import Path
import tarfile

root = Path(__file__).resolve().parent
store = root / 'image_download'
meta = json.loads((root / 'mim_base_manifest.json').read_text())
raw = (store / 'manifest.raw.json').read_bytes()
assert 'sha256:' + hashlib.sha256(raw).hexdigest() == meta['manifest_digest']
manifest = json.loads(raw)
desc = {'mediaType': manifest['mediaType'], 'digest': meta['manifest_digest'],
        'size': len(raw), 'platform': {'os': 'linux', 'architecture': 'amd64'},
        'annotations': {'io.containerd.image.name': meta['image'],
                        'org.opencontainers.image.ref.name': meta['image']}}
index = {'schemaVersion': 2, 'mediaType': 'application/vnd.oci.image.index.v1+json',
         'manifests': [desc]}
destination = root / 'mim-base.oci.tar'
temporary = destination.with_suffix('.tar.part')


class HashReader:
    def __init__(self, f):
        self.f = f
        self.hash = hashlib.sha256()

    def read(self, n=-1):
        data = self.f.read(n)
        self.hash.update(data)
        return data


with tarfile.open(temporary, 'w') as tar:
    def add_bytes(name, value):
        h = tarfile.TarInfo(name)
        h.size = len(value)
        h.mode = 0o644
        tar.addfile(h, io.BytesIO(value))

    add_bytes('oci-layout', b'{"imageLayoutVersion":"1.0.0"}')
    add_bytes('index.json', json.dumps(index).encode())
    add_bytes('blobs/sha256/' + meta['manifest_digest'].split(':')[1], raw)
    descriptors = {d['digest']: d for d in [manifest['config'], *manifest['layers']]}
    for digest, descriptor in descriptors.items():
        key = digest.split(':')[1]
        path = store / key
        assert path.stat().st_size == descriptor['size'], key
        h = tarfile.TarInfo('blobs/sha256/' + key)
        h.size = descriptor['size']
        h.mode = 0o644
        with path.open('rb') as f:
            reader = HashReader(f)
            tar.addfile(h, reader)
            assert reader.hash.hexdigest() == key, key
        print('PACKED', key[:12], flush=True)
temporary.replace(destination)
print('OCI_ARCHIVE_READY', destination, destination.stat().st_size, flush=True)
