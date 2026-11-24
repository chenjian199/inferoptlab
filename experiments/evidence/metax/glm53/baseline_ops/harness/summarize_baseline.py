"""Offline aggregate/paired regression report; never executes candidate programs."""
import argparse
import hashlib
import json
from pathlib import Path


def load_rows(path):
    rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    result={r['task_id']:r for r in rows}
    if len(result)!=len(rows):raise ValueError('Duplicate task ID')
    return result


def compare(left,right):
    if set(left)!=set(right):raise ValueError('Comparisons must use identical task sets')
    groups={k:[] for k in ['both_pass','regression','improvement','both_fail']}
    for tid in sorted(left):
        a,b=left[tid]['passed'],right[tid]['passed']
        key='both_pass' if a and b else 'regression' if a else 'improvement' if b else 'both_fail'
        groups[key].append(tid)
    return groups


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--full',type=Path,required=True)
    parser.add_argument('--smoke',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    full=load_rows(args.full/'correctness.jsonl');smoke=load_rows(args.smoke/'correctness.jsonl')
    assert len(full)==164 and len(smoke)==32 and set(smoke)<=set(full)
    assert all(r['result']!='infrastructure_error' for r in [*full.values(),*smoke.values()])
    gf=load_rows(args.full/'generations.jsonl');gs=load_rows(args.smoke/'generations.jsonl')
    assert set(gf)==set(full) and set(gs)==set(smoke)
    overlap={tid:full[tid] for tid in smoke}
    exact=[tid for tid in smoke if gf[tid]['output_token_ids']==gs[tid]['output_token_ids']]
    report={'status':'complete','full_tasks':164,'full_passed':sum(r['passed'] for r in full.values()),
            'full_pass_at_1':sum(r['passed'] for r in full.values())/164,
            'smoke_tasks':32,'smoke_passed':sum(r['passed'] for r in smoke.values()),
            'smoke_pass_at_1':sum(r['passed'] for r in smoke.values())/32,
            'overlap_score_transitions':compare(smoke,overlap),'overlap_exact_token_matches':len(exact),
            'overlap_token_mismatches':[tid for tid in smoke if tid not in exact],
            'repeatability_scope':'32 overlapping tasks, same loaded engine, different request order. Not independent-process repeatability.',
            'full_failed_tasks':[tid for tid,r in full.items() if not r['passed']],
            'full_truncated_tasks':[tid for tid,r in gf.items() if r['finish_reason']=='length'],
            'full_generated_tokens':sum(r['output_tokens'] for r in gf.values()),
            'full_generation_seconds':sum(r['generation_seconds'] for r in gf.values()),
            'timing_scope':'Observed accuracy workload time only; not a stable performance benchmark.',
            'artifacts':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for folder in [args.full,args.smoke]
                         for p in folder.iterdir() if p.is_file()}}
    with args.output.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!='artifacts'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
