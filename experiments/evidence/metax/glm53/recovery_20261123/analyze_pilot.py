"""Offline paired model comparison; no generated code is executed here."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent/'pilot'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def rows(p):
    values=[json.loads(x) for x in p.read_text(encoding='utf8').splitlines() if x.strip()]
    result={x['task_id']:x for x in values};assert len(result)==len(values);return result
def main():
    e=ROOT/'evidence';plan=read(ROOT/'configs/model-plan.json');ids=plan['task_ids']
    assert read(e/'communication_check.json')['status']=='passed'
    assert read(e/'model_process.json')['exit_code']==0
    generations={};scores={};summaries={}
    for phase,count in [('baseline32',32),('candidate32',32),('rollback4',4)]:
        r=ROOT/'runs'/phase;g=rows(r/'generations.jsonl');s=rows(r/'correctness.jsonl')
        m=read(r/'generation_manifest.json');summary=read(r/'score_summary.json')
        assert m['status']==summary['status']=='complete' and m['completed_tasks']==summary['tasks']==count
        assert list(m['task_ids'])==ids[:count] and set(g)==set(s)==set(ids[:count])
        assert hashlib.sha256((r/'generations.jsonl').read_bytes()).hexdigest()==m['generations_sha256']
        assert all(x['result']!='infrastructure_error' for x in s.values())
        assert sum(x['passed'] for x in s.values())==summary['passed']
        assert m['sampling']==plan['sampling'] and m['settings']==plan['settings']
        generations[phase]=g;scores[phase]=s;summaries[phase]=summary
    stats=read(e/'replacement_stats.json')
    assert len(stats)==8 and {x['rank'] for x in stats}==set(range(8))
    for s in stats:
        assert s['replaced']>0 and s['fallback']==0 and s['max_bf16_ulp']<=1
        assert len(s['reference_checks'])==2
        for check in s['reference_checks']:
            assert check['int32_exact'] and check['fp32']['exact'] and check['fp64']['max_bf16_ulp']<=1
    assert len(read(e/'install.json'))==len(read(e/'rollback.json'))==8
    assert all(x['installed'] for x in read(e/'install.json')) and all(x['restored'] for x in read(e/'rollback.json'))
    pairs=[]
    for tid in ids:
        b=generations['baseline32'][tid];c=generations['candidate32'][tid]
        pairs.append({'task_id':tid,'baseline_pass':scores['baseline32'][tid]['passed'],'candidate_pass':scores['candidate32'][tid]['passed'],
          'tokens_exact':b['output_token_ids']==c['output_token_ids'],'baseline_tokens':len(b['output_token_ids']),'candidate_tokens':len(c['output_token_ids'])})
    rollback=[{'task_id':tid,'tokens_exact':generations['rollback4'][tid]['output_token_ids']==generations['baseline32'][tid]['output_token_ids'],
        'pass_equal':scores['rollback4'][tid]['passed']==scores['baseline32'][tid]['passed']} for tid in ids[:4]]
    regressions=[p['task_id'] for p in pairs if p['baseline_pass'] and not p['candidate_pass']]
    improved=[p['task_id'] for p in pairs if not p['baseline_pass'] and p['candidate_pass']]
    result={'status':'passed' if not regressions and all(r['tokens_exact'] and r['pass_equal'] for r in rollback) else 'regression_requires_review',
      'scores':{k:{x:v[x] for x in ['tasks','passed','pass_at_1','truncated']} for k,v in summaries.items()},
      'paired_pass_regressions':regressions,'paired_pass_improvements':improved,'candidate_token_exact':sum(p['tokens_exact'] for p in pairs),
      'paired':pairs,'rollback':rollback,'ranks_replaced':8,'candidate_calls_total':sum(s['replaced'] for s in stats),'fallback':0,
      'max_bf16_ulp':max(s['max_bf16_ulp'] for s in stats),'max_abs':max(s['max_abs'] for s in stats),
      'scope':'Single engine paired32/32/4, one dense layer acrossTP8; not full164/multi-process release/performance acceptance.'}
    (ROOT/'comparison_summary.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['paired','rollback']},indent=2))
if __name__=='__main__':main()
