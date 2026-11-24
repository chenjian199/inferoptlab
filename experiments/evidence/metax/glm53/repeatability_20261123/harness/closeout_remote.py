"""Close only this experiment after all scheduled GPU jobs and scoring complete."""
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile
import time

ROOT=Path('/home/metax/glm53-repeatability-20261123')


def read(p):return json.loads(p.read_text())


def save(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2)


def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def inspect(names):
    values=json.loads(subprocess.check_output(['docker','inspect',*names],text=True))
    return {v['Name'].lstrip('/'):{**{k:v[k] for k in ['Id','Image','Created','Mounts']},
        'State':{k:v['State'][k] for k in ['Running','Paused','StartedAt','FinishedAt','Restarting']}} for v in values}


def normalized(value):
    value=json.loads(json.dumps(value))
    for row in value.values():row['Mounts'].sort(key=lambda m:json.dumps(m,sort_keys=True))
    return value


def main():
    e=ROOT/'evidence'
    with Path('/home/metax/.glm53-c500-tp8.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        for n in ['process_a','process_b','process_c','diagnostic_process','diagnostic2_process','legacy_control_process']:
            v=read(e/(n+'.json'));assert v['status']=='complete' and v['exit_code']==0,n
        analysis=read(e/'tensor_analysis.json');assert analysis['captures']==108
        own=inspect(['glm53-repeat-v1'])['glm53-repeat-v1']
        assert own['Id']=='e02d1b6b99df48c1999a509a36ca01b2a764b65c4e6bcc0237d002a521b96450'
        p=subprocess.run(['docker','stop','--time','20','glm53-repeat-v1'],capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        after=inspect(['dcc','glm53-vllm032','glm53-heval-v1'])
        save(e/'preserved_after.json',after)
        assert normalized(after)==normalized(read(e/'preserved_before.json'))
        save(e/'experiment_container_after.json',inspect(['glm53-repeat-v1']))
        gpu=subprocess.run(['/usr/bin/mx-smi'],capture_output=True,text=True)
        (e/'gpu_after.txt').write_text(gpu.stdout+gpu.stderr)
        archives=ROOT/'archives';archives.mkdir(exist_ok=True)
        target=archives/'diagnostic_tensors_20261123.tar.gz'
        assert not target.exists()
        with tarfile.open(target,'w:gz',compresslevel=1) as tar:
            for entry in analysis['tensor_artifacts']:
                p=e/'diagnostic_tensors'/Path(entry['path']).name
                assert sha(p)==entry['sha256']
                tar.add(p,arcname='diagnostic_tensors/'+p.name,recursive=False)
        checked=0
        expected={Path(entry['path']).name:entry['sha256'] for entry in analysis['tensor_artifacts']}
        with tarfile.open(target,'r:gz') as tar:
            for member in tar:
                f=tar.extractfile(member);assert f is not None
                assert hashlib.sha256(f.read()).hexdigest()==expected[Path(member.name).name]
                checked+=1
        assert checked==108
        original=Path('/home/metax/glm53-baseline-ops/archive/20261123_humaneval_v1.tar.gz')
        assert sha(original)=='95278d7b264b88db8398d4916ab78f0f3869f935639cb0041c0dc37394af45e6'
        record={'status':'complete','completed_epoch':time.time(),'original_containers_unchanged':True,
            'experiment_container_stopped':True,'original_baseline_archive_sha256':sha(original),
            'mx_smi_exit_code':gpu.returncode,'mx_smi_boundary':'Raw exit code retained; do not interpret exit 4 as a health-check pass.',
            'tensor_archive':{'path':str(target),'bytes':target.stat().st_size,'sha256':sha(target),'verified_tensors':checked},
            'failed_v4':'Retained separately under evidence/failed_diagnostic_v4; excluded from final tensor archive.'}
        save(e/'closeout.json',record);print(json.dumps(record,indent=2))


if __name__=='__main__':main()
