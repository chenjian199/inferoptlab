"""Offline integrity/scope verifier; never executes generated HumanEval code."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normalized(v):
    v=json.loads(json.dumps(v))
    for x in v.values():x['Mounts']=sorted(x['Mounts'],key=lambda m:m['Destination'])
    return v
def main():
    p=ROOT/'pilot';e=p/'evidence'
    for rel,h in read(p/'inputs_sha256.json').items():assert sha(p/rel)==h,rel
    comm=read(e/'communication_check.json');assert comm['status']=='passed' and comm['MCCL_P2P_DISABLE']=='1'
    for rank in range(8):
        assert read(e/f'local_compute_rank{rank}.json')['passed']
        c=read(e/f'comm_rank{rank}.json');assert c['passed'] and c['expected_sum']==36 and c['all_reduce_lengths']==[1,16,1024]
    scope=read(e/'runtime_scope.json');assert scope['environment']['MCCL_P2P_DISABLE']=='1'
    source=read(e/'source_archive_check.json')
    assert source['status']=='passed' and source['files_checked']==9334 and not source['mismatches']
    assert source['archive_sha256']=='da769ed300e32876f2bd358a1c537a8618f7fdbc8f56830eacfec57f6d1ab592'
    assert scope['model_plan']['settings']['disable_custom_all_reduce']
    before=read(ROOT/'evidence/preflight.json');after=read(ROOT/'evidence/preserved_after.json')
    assert normalized(before['containers'])==normalized(after['old_containers'])
    assert before['host']['boot_id']==after['boot_id']==scope['boot_id']
    assert not after['new_container_running'] and after['metax_refcnt']=='0'
    env=read(e/'model_environment.json');assert env['settings']==scope['model_plan']['settings']
    assert len(env['targets'])==len(env['workers'])==8
    assert {w['rank'] for w in env['workers']}==set(range(8))
    for target in env['targets']:
        assert target['target']=='language_model.model.layers.0.mlp.gate_up_proj'
        assert target['weight_dtype']=='torch.int8' and target['scheme_aliases']==[target['target']]
    for stat in read(e/'replacement_stats.json'):
        for check in stat['reference_checks']:
            assert (e/'real_inputs'/Path(check['path']).name).is_file()
    # Analyzer checks paired scoring, token changes, actual8rank hit/fallback and rollback.
    run=subprocess.run([sys.executable,'-B',str(ROOT/'analyze_pilot.py')],capture_output=True,text=True,encoding='utf8')
    assert run.returncode==0,run.stdout+run.stderr
    result=read(p/'comparison_summary.json')
    # A failed correctness gate is a valid recorded outcome, never silently reclassified.
    assert result['status'] in ['passed','regression_requires_review']
    prior=subprocess.run([sys.executable,'-B',str(ROOT.parent/'gemm_replace_20261123/harness/verify_experiment.py')],capture_output=True,text=True,encoding='utf8')
    assert prior.returncode==0,prior.stdout+prior.stderr
    previous=ROOT.parent/'recovery_20261123'
    old=read(previous/'artifact_manifest.json')
    for item in old['files']:assert sha(previous/item['path'])==item['sha256'],item['path']
    checked=0
    if (ROOT/'artifact_manifest.json').exists():
        for item in read(ROOT/'artifact_manifest.json')['files']:
            file=(ROOT/item['path']).resolve();assert file.is_relative_to(ROOT.resolve()) and sha(file)==item['sha256'],item['path']
            checked+=1
    print(json.dumps({'evidence_integrity':'passed','pilot_correctness_gate':result['status'],'preserved_old_experiments':True,
        'prior_recovery_files_checked':len(old['files']),'current_files_checked':checked,
        'boundary':'P2P-disabled single-engine32/32/4 pilot only; does not certify MetaXLink, default transport, full164, multiple engines or performance.'},indent=2))
if __name__=='__main__':main()
