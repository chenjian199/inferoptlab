"""Compare the historical runner flow to the new runner and original results."""
import hashlib
import json
from pathlib import Path
from analyze_repeats import compare,rows

ROOT=Path(__file__).resolve().parents[1]


def main():
    def read(p):return json.loads(p.read_text(encoding='utf-8'))
    legacy=ROOT/'runs/legacy_control_smoke32'
    m=read(legacy/'generation_manifest.json');s=read(legacy/'score_summary.json')
    assert m['status']==s['status']=='complete' and s['tasks']==32
    assert hashlib.sha256((legacy/'generations.jsonl').read_bytes()).hexdigest()==m['generations_sha256']
    outputs=rows(legacy/'generations.jsonl');scores=rows(legacy/'correctness.jsonl')
    assert set(outputs)==set(scores)==set(m['task_ids']) and len(outputs)==32
    assert not any(row['result']=='infrastructure_error' for row in scores.values())
    assert read(ROOT/'evidence/prompt_manifest.json')==read(ROOT/'data/prompt_manifest.json')
    assert read(ROOT/'evidence/generation_environment.json')['settings']==read(ROOT/'configs/plan.json')['settings']
    report={'status':'complete','prompt_manifest_equal':True,'settings_equal':True,'score':s,'comparisons':{}}
    paths={'new_process_a':ROOT/'runs/process_a_plain32_first',
        'historical_smoke32':ROOT.parent/'baseline_ops/runs/20261123_humaneval_v1_smoke32',
        'historical_full164_subset':ROOT.parent/'baseline_ops/runs/20261123_humaneval_v1_full164'}
    for name,folder in paths.items():
        other={k:v for k,v in rows(folder/'generations.jsonl').items() if k in outputs}
        other_scores={k:v for k,v in rows(folder/'correctness.jsonl').items() if k in outputs}
        report['comparisons'][name]=compare(other,outputs,other_scores,scores)
    with (ROOT/'evidence/legacy_comparison.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({'passed':s['passed'],'comparisons':{k:v['exact_token_matches'] for k,v in report['comparisons'].items()}},indent=2))


if __name__=='__main__':main()
