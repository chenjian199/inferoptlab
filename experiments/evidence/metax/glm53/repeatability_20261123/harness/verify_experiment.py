"""Read-only verification of repeatability evidence and frozen baseline."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from analyze_repeats import rows
from check_functional_gate import load_run

ROOT=Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def normalized(value):
    value=json.loads(json.dumps(value))
    for row in value.values():
        row['Mounts'].sort(key=lambda m:json.dumps(m,sort_keys=True))
    return value


def main():
    e=ROOT/'evidence'
    input_hashes=read(e/'inputs_sha256.json')
    input_hashes.update({k:v for k,v in read(e/'legacy_inputs_sha256.json')['files'].items() if k!='harness/analyze_tensors.py'})
    input_hashes.update(read(e/'diagnostic_inputs_sha256_v5.json')['files'])
    for name,digest in input_hashes.items():
        path=ROOT/name
        if name=='scoring/scoring.jsonl':
            path=ROOT.parent/'baseline_ops/datasets/prepared/7dce6050a7d6d172f3cc5c32aa97f52fa1a2e544/scoring.jsonl'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,name
    assert read(ROOT/'repeatability_summary.json')['status']=='complete'
    pids=[]
    for process in ['a','b','c']:
        record=read(e/f'process_{process}.json')
        assert record['status']=='complete' and record['exit_code']==0
        env=read(e/f'process_{process}/environment.json')
        assert len(env['workers'])==8
        assert {w['rank'] for w in env['workers']}==set(range(8))
        assert all(w['use_v2_model_runner'] for w in env['workers'])
        assert env['sampling_type']=='GREEDY'
        pids.append(env['pid'])
        load_run(ROOT/f'runs/process_{process}_plain32_first',32)
    assert len(set(pids))==3
    for name in ['diagnostic_process','diagnostic2_process','legacy_control_process']:
        record=read(e/(name+'.json'))
        assert record['status']=='complete' and record['exit_code']==0
    labels=set()
    for process in ['d1','d2']:
        folder=e/('diagnostics_'+process)
        assert read(folder/'complete.json')['probes']==54
        probes=[json.loads(line) for line in (folder/'probes.jsonl').read_text(encoding='utf-8').splitlines()]
        assert len(probes)==54
        for probe in probes:
            assert probe['label'] not in labels
            labels.add(probe['label'])
            trace=[item for item in probe['trace'] if item['rank']==0][0]
            assert trace['sampling_calls']==1 and trace['layers']==135
            assert trace['total_steps']==trace['target_step']+1
    tensors=read(e/'tensor_analysis.json')
    assert tensors['captures']==108 and len(tensors['decisions'])==108
    assert set(tensors['decisions'])==labels and len(tensors['comparisons'])==216
    assert len(tensors['tensor_artifacts'])==108
    assert all(d['temperature']==[0.0] and d['selected_is_max'] and d['finite'] for d in tensors['decisions'].values())
    legacy=read(ROOT/'runs/legacy_control_smoke32/score_summary.json')
    assert legacy['status']=='complete' and legacy['tasks']==32
    outputs=rows(ROOT/'runs/legacy_control_smoke32/generations.jsonl')
    assert len(outputs)==32
    assert read(e/'legacy_comparison.json')['status']=='complete'
    assert normalized(read(e/'preserved_before.json'))==normalized(read(e/'preserved_after.json'))
    child=subprocess.run([sys.executable,'-B',str(ROOT.parent/'baseline_ops/harness/verify_baseline.py')],capture_output=True,text=True)
    assert child.returncode==0,child.stderr+child.stdout
    manifest=ROOT/'artifact_manifest.json'
    checked=0
    if manifest.exists():
        for entry in read(manifest)['files']:
            path=(ROOT/entry['path']).resolve()
            assert path.is_relative_to(ROOT.resolve())
            assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256'],entry['path']
            checked+=1
    print(json.dumps({'status':'passed','independent_plain_processes':len(pids),'diagnostic_captures':len(labels),
        'baseline_verification':json.loads(child.stdout),'artifact_files_checked':checked,
        'boundary':'Local metadata and evidence integrity. Full tensor bytes remain on remote host; their hashes are recorded, not reread by this verifier.'},indent=2))


if __name__=='__main__':main()
