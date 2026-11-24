"""Audit saved HumanEval outputs without executing generated code or tests.

Method source: supplied repeatability_20261123/REGRESSION_POLICY.md.
This is an offline functional screen, never numerical/release acceptance.
"""
from collections import Counter
import hashlib
import json

from tools.specs import SpecError, digest, read
from benchmark.common.io import file_hash, inside
from benchmark.common.offline import artifact, report


def rows(path):
    result={}
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        item=json.loads(line);identity=item['task_id']
        if identity in result:raise SpecError('duplicate task ID in '+str(path))
        result[identity]=item
    return result


def audit_run(root, directory, task_ids):
    directory=inside(root,str(directory))
    manifest=read(directory/'generation_manifest.json');summary=read(directory/'score_summary.json')
    scores=rows(directory/'correctness.jsonl');outputs=rows(directory/'generations.jsonl')
    if manifest['status']!='complete' or summary['status']!='complete':raise SpecError('incomplete generation/scoring')
    if manifest['task_ids']!=task_ids or list(outputs)!=task_ids or set(scores)!=set(task_ids):raise SpecError('task set/order differs from frozen plan')
    if manifest['expected_tasks']!=len(task_ids) or manifest['completed_tasks']!=len(task_ids):raise SpecError('task count mismatch')
    if file_hash(directory/'generations.jsonl')!=manifest['generations_sha256']:raise SpecError('generation hash mismatch')
    for tid,s in scores.items():
        if type(s['passed']) is not bool or s['result']=='infrastructure_error' or s['passed']!=(s['result']=='passed'):
            raise SpecError('invalid scoring/infrastructure result')
        o=outputs[tid]
        if o['output_tokens']!=len(o['output_token_ids']) or s['truncated']!=(o['finish_reason']=='length'):
            raise SpecError('token count/truncation mismatch')
        if 'submitted_code' in s:
            if not isinstance(s['submitted_code'],str) or hashlib.sha256(s['submitted_code'].encode()).hexdigest()!=s['submitted_code_sha256']:
                raise SpecError('submitted code changed')
        elif s['result']!='parse_failure':
            raise SpecError('submitted code missing outside an explicit parse failure')
    passed=sum(s['passed'] for s in scores.values())
    if summary['tasks']!=len(task_ids) or summary['passed']!=passed or summary['failures_by_type']!=dict(Counter(s['result'] for s in scores.values())) or summary['truncated']!=sum(s['truncated'] for s in scores.values()):
        raise SpecError('score summary differs from individual results')
    if abs(summary['pass_at_1']-passed/len(task_ids))>1e-12:raise SpecError('score rate mismatch')
    if manifest['sampling'].get('logprobs') is not None:raise SpecError('diagnostic generation cannot enter plain functional screen')
    identity={k:manifest[k] for k in ('settings','sampling','prompt_manifest_sha256','task_ids')}
    identity.update({k:summary[k] for k in ('adapter_sha256','evaluator_sha256','sandbox_image')})
    return dict(directory=directory.relative_to(root).as_posix(),passed=passed,total=len(task_ids),
                scores={tid:s['passed'] for tid,s in scores.items()},fingerprint=digest(identity),
                process=manifest.get('process'),
                artifacts=[artifact(root,directory/name,role) for name,role in [('generation_manifest.json','generation_manifest'),('score_summary.json','score_summary'),('correctness.jsonl','task_scores'),('generations.jsonl','generated_outputs')]])


def matrix_gate(baselines,candidates):
    if len(baselines)!=3 or len(candidates)!=3:raise SpecError('exactly three runs are required on each side')
    ids=set(baselines[0])
    if not ids or any(set(r)!=ids or any(type(v) is not bool for v in r.values()) for r in baselines+candidates):
        raise SpecError('invalid or inconsistent task set')
    stable={t for t in ids if all(r[t] for r in baselines)}
    variable={t for t in ids if len({r[t] for r in baselines})>1}
    regressions=sorted(t for t in stable if not all(r[t] for r in candidates))
    worsened=sorted(t for t in variable if sum(r[t] for r in candidates)<sum(r[t] for r in baselines))
    b=[sum(r.values()) for r in baselines];c=[sum(r.values()) for r in candidates]
    aggregate=min(c)<min(b) or sum(c)<sum(b)
    return dict(status='fail' if regressions else 'inconclusive' if worsened or aggregate else 'pass_functional',
                stable_pass_regressions=regressions,worsened_variable_tasks=worsened,
                baseline_counts=b,candidate_counts=c,aggregate_worse=aggregate)


def inspect(catalog,plan,paths):
    items=[audit_run(catalog.root,p,plan['dataset']['task_ids']) for p in paths]
    return report(catalog,plan,'accuracy','inspect','history_verified',
                  dict(runs=[{k:v for k,v in r.items() if k not in {'scores','artifacts'}} for r in items]),
                  [a for r in items for a in r['artifacts']],
                  ['Only archived generation/scoring consistency was recomputed; no model or generated code was executed.',
                   'The historical evaluator was not rerun. Runtime, process independence and original input provenance need separate verification.'])


def compare(catalog,plan,baselines,candidates):
    items=[audit_run(catalog.root,p,plan['dataset']['task_ids']) for p in baselines+candidates]
    if len(baselines)!=3 or len(candidates)!=3:raise SpecError('three independent runs per side are required')
    if len({r['fingerprint'] for r in items})!=1:raise SpecError('generation/scoring configuration mismatch')
    if len({r['directory'] for r in items})!=6:raise SpecError('baseline/candidate evidence cannot be reused as independent runs')
    processes=[r['process'] for r in items]
    if any(p is None for p in processes) or len({digest(p) for p in processes})!=6:
        raise SpecError('six distinct recorded process identities are required')
    result=matrix_gate([r['scores'] for r in items[:3]],[r['scores'] for r in items[3:]])
    return report(catalog,plan,'accuracy','compare',result['status'],result,
                  [a for r in items for a in r['artifacts']],
                  ['Functional screen only; recorded process identities are not independent launch attestation.',
                   'Operator contracts, same-prefix numerical gates, complete source/input integrity and sandbox execution evidence remain mandatory.',
                   'Smoke32 is screening only; even full164 does not establish numerical equivalence or general model quality.'])
