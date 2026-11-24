"""Create a new immutable local archive; refuse to replace an existing one."""
import hashlib,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=ROOT/'artifact_manifest.json';archive=ROOT/'archives/gemm_replace_20261123_v1.tar.gz'
    assert not manifest.exists() and not archive.exists(),'Already frozen; use a new experiment directory.'
    paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and 'archives' not in p.parts and '__pycache__' not in p.parts and p.name!='archive_receipt.json')
    records=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]
    manifest.write_text(json.dumps({'date':'2026-11-23','scope':'Local reviewed experiment files, not full remote logs/cache/checkpoint. No whole-model success claim.','files':records},indent=2),encoding='utf8')
    archive.parent.mkdir(exist_ok=True)
    with tarfile.open(archive,'w:gz') as tf:
        for p in paths+[manifest]:tf.add(p,arcname=p.relative_to(ROOT).as_posix(),recursive=False)
    receipt={'status':'local_verified_remote_pending','archive':archive.as_posix(),'sha256':sha(archive),'bytes':archive.stat().st_size,'hashed_files':len(records),'remote_verified':False}
    (ROOT/'archive_receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf8')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
