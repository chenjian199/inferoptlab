"""Conservative functional gate. Passing it does not certify numerical equivalence."""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from analyze_repeats import rows


def matrix_gate(baselines, candidates):
    if len(baselines) != 3 or len(candidates) != 3:
        raise ValueError('Require exactly three independent runs per side')
    ids = set(baselines[0])
    if not ids or any(set(run) != ids for run in baselines+candidates):
        raise ValueError('Missing, extra or empty task set')
    stable = {tid for tid in ids if all(run[tid] for run in baselines)}
    unstable = {tid for tid in ids if len({run[tid] for run in baselines}) > 1}
    regressions = sorted(tid for tid in stable if not all(run[tid] for run in candidates))
    worsened_variable = sorted(tid for tid in unstable if sum(run[tid] for run in candidates) < sum(run[tid] for run in baselines))
    bcounts = [sum(run.values()) for run in baselines]
    ccounts = [sum(run.values()) for run in candidates]
    aggregate_worse = min(ccounts) < min(bcounts) or sum(ccounts) < sum(bcounts)
    status = 'fail' if regressions else 'inconclusive' if worsened_variable or aggregate_worse else 'pass_functional'
    return {'status':status,'stable_pass_regressions':regressions,
            'worsened_variable_tasks':worsened_variable,'baseline_counts':bcounts,'candidate_counts':ccounts,
            'aggregate_worse':aggregate_worse,'stable_pass_count':len(stable),'variable_count':len(unstable),
            'interpretation':'Engineering screen from three runs, not a statistical non-inferiority proof. Numeric/operator gates remain mandatory.'}


def load_run(folder, expected_count):
    manifest = json.loads((folder/'generation_manifest.json').read_text(encoding='utf-8'))
    summary = json.loads((folder/'score_summary.json').read_text(encoding='utf-8'))
    scores = rows(folder/'correctness.jsonl')
    outputs = rows(folder/'generations.jsonl')
    if manifest['status'] != 'complete' or summary['status'] != 'complete':
        raise ValueError('Incomplete run')
    if (len(scores) != expected_count or len(manifest['task_ids']) != expected_count
        or set(scores) != set(manifest['task_ids']) or set(outputs) != set(scores)
        or list(outputs) != manifest['task_ids']
        or manifest['completed_tasks'] != expected_count or manifest['expected_tasks'] != expected_count):
        raise ValueError('Wrong task set/count')
    if expected_count == 164 and set(scores) != {f'HumanEval/{i}' for i in range(164)}:
        raise ValueError('Not the full HumanEval task set')
    if any(s['result']=='infrastructure_error' or s['passed']!=(s['result']=='passed') for s in scores.values()):
        raise ValueError('Invalid scoring result')
    if summary['tasks'] != len(scores) or summary['passed'] != sum(s['passed'] for s in scores.values()):
        raise ValueError('Score summary mismatch')
    if summary['failures_by_type'] != dict(Counter(s['result'] for s in scores.values())):
        raise ValueError('Failure counts mismatch')
    if summary['truncated'] != sum(s['truncated'] for s in scores.values()):
        raise ValueError('Truncation summary mismatch')
    for tid, output in outputs.items():
        if output['output_tokens'] != len(output['output_token_ids']):
            raise ValueError('Output token count mismatch')
        if scores[tid]['truncated'] != (output['finish_reason']=='length'):
            raise ValueError('Truncation flag mismatch')
        if 'submitted_code' in scores[tid] and hashlib.sha256(scores[tid]['submitted_code'].encode()).hexdigest() != scores[tid]['submitted_code_sha256']:
            raise ValueError('Scored code hash mismatch')
    if hashlib.sha256((folder/'generations.jsonl').read_bytes()).hexdigest() != manifest['generations_sha256']:
        raise ValueError('Generation output hash mismatch')
    if manifest['sampling'].get('logprobs') is not None:
        raise ValueError('Diagnostic sampling cannot enter plain functional gate')
    fingerprint = {k:manifest[k] for k in ['settings','sampling','prompt_manifest_sha256','task_ids']}
    fingerprint.update({k:summary[k] for k in ['adapter_sha256','evaluator_sha256','sandbox_image']})
    return {tid:s['passed'] for tid,s in scores.items()},fingerprint,manifest['process']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--baseline',nargs=3,type=Path,required=True)
    p.add_argument('--candidate',nargs=3,type=Path,required=True)
    p.add_argument('--scope',choices=['smoke32','full164'],required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    count = 32 if args.scope=='smoke32' else 164
    left = [load_run(path,count) for path in args.baseline]
    right = [load_run(path,count) for path in args.candidate]
    if any(item[1] != left[0][1] for item in left+right):
        raise ValueError('Protocol/order/evaluator fingerprint mismatch')
    if len({item[2] for item in left}) != 3 or len({item[2] for item in right}) != 3:
        raise ValueError('Runs are not from three distinct recorded processes')
    result = matrix_gate([item[0] for item in left],[item[0] for item in right])
    result.update(scope=args.scope,release_gate=args.scope=='full164',
                  requirement='Validate experiment input hashes and independent process evidence, then apply operator and fixed-prefix numeric gates. Smoke is screening only.')
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if result['status'] != 'pass_functional':
        raise SystemExit(2)


if __name__=='__main__':
    main()
