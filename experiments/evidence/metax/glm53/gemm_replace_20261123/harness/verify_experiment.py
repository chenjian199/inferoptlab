"""Offline integrity/scope checks; does not rerun GPU kernels or model inference."""
import hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized(value):
    value=json.loads(json.dumps(value))
    for item in value.values():item['Mounts']=sorted(item['Mounts'],key=lambda m:m['Destination'])
    return value

def main():
    e=ROOT/'evidence';unit=read(e/'device_tests.json');layer=read(e/'isolated_layer_result.json')
    assert unit['status']=='passed' and unit['cases']==len(unit['results'])==56 and unit['devices']==8
    assert {r['device'] for r in unit['results']}==set(range(8))
    for r in unit['results']:
        assert r['int32_exact'] and r['fp32']['exact'] and r['fp32']['finite']
        for d in [r['fp64'],r['original']]:
            if d is not None:assert d['finite'] and d['max_bf16_ulp']<=1
    assert layer['status']=='passed' and layer['cases']==24 and layer['device_used']==0
    assert {s['checkpoint_slice'] for s in layer['results']}==set(range(8))
    cases=[];captures=[]
    for s in layer['results']:
        assert s['device']==0 and s['processed_weight_shape']==[4096,3072]
        assert s['stats']['replaced']==3 and s['stats']['fallback']==0
        assert len(s['cases'])==3 and len(s['stats']['reference_checks'])==2
        for c in s['cases']:
            assert c['comparison']['finite'] and c['comparison']['max_bf16_ulp']<=1 and c['rollback_exact']
            cases.append(c)
        for c in s['stats']['reference_checks']:
            assert c['int32_exact'] and c['fp32']['exact'] and c['fp64']['finite'] and c['fp64']['max_bf16_ulp']<=1
            p=e/'real_inputs'/Path(c['path']).name;assert p.is_file()
            captures.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)})
    for rel,h in read(e/'inputs_sha256.json').items():assert sha(ROOT/rel)==h,rel
    v3=read(e/'isolated_inputs_v3.json')['harness/isolated_layer_probe.py']
    assert sha(e/'isolated_layer_probe.v3.py')==v3
    assert sha(ROOT/'harness/isolated_layer_probe.py')==read(e/'isolated_inputs_v4.json')['harness/isolated_layer_probe.py']
    assert normalized(read(e/'preserved_before.json'))==normalized(read(e/'preserved_after.json'))
    assert not read(e/'cleanup.json')['running']
    assert read(e/'model_process.json')['exit_code']!=0
    assert not list((ROOT/'runs').rglob('generations.jsonl'))
    child=subprocess.run([sys.executable,'-B',str(ROOT.parent/'repeatability_20261123/harness/verify_experiment.py')],capture_output=True,text=True,encoding='utf8')
    assert child.returncode==0,child.stdout+child.stderr
    checked=0
    if (ROOT/'artifact_manifest.json').exists():
        for item in read(ROOT/'artifact_manifest.json')['files']:
            p=(ROOT/item['path']).resolve();assert p.is_relative_to(ROOT.resolve()) and sha(p)==item['sha256'],item['path']
            checked+=1
    report={'status':'passed_with_model_blocked','unit_cases':56,'unit_devices_before_fault':8,
        'isolated_cases':len(cases),'isolated_device':0,'isolated_checkpoint_partitions':8,
        'isolated_exact_cases':sum(c['comparison']['exact'] for c in cases),
        'isolated_max_bf16_ulp':max(c['comparison']['max_bf16_ulp'] for c in cases),
        'isolated_max_abs':max(c['comparison']['max_abs'] for c in cases),
        'rollback_exact_cases':sum(c['rollback_exact'] for c in cases),'fallback':0,
        'captures':captures,'preserved_containers':True,'prior_verification':json.loads(child.stdout),
        'full_model':'Blocked before candidate injection by GPU6/communication fault; zero model generations or HumanEval scores in this experiment.',
        'boundary':'Real checkpoint weights/scales, synthetic activations; single GPU sequential partitions; no TP8 model, performance or release acceptance claim.'}
    print(json.dumps({'verification':report,'artifact_files_checked':checked},indent=2))

if __name__=='__main__':main()
