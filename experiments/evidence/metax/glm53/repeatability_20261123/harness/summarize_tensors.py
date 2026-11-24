"""Compact summary of full tensor analysis; does not load or execute model code."""
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    r=json.loads((ROOT/'evidence/tensor_analysis.json').read_text())
    groups={}
    for scope in sorted({c['scope'] for c in r['comparisons']}):
        rows=[c for c in r['comparisons'] if c['scope']==scope]
        groups[scope]={'pairs':len(rows),'exact_logits':sum(c['logits']['exact'] for c in rows),
            'winner_changes':sum(c['winner_changed'] for c in rows),
            'max_logit_abs_delta':max(c['logits']['max_abs'] for c in rows),
            'max_logit_rmse':max(c['logits']['rmse'] for c in rows),
            'first_changed_modules':dict(Counter(c['first_changed_module'] or 'none' for c in rows))}
    decisions=list(r['decisions'].values())
    summary={'captures':r['captures'],'tasks':r['tasks'],'finite':sum(d['finite'] for d in decisions),
        'zero_temperature':sum(d['temperature']==[0.0] for d in decisions),
        'greedy_at_max':sum(d['selected_is_max'] for d in decisions),
        'cpu_gpu_argmax_match':sum(d['cpu_argmax']==d['gpu_argmax']==d['selected'] for d in decisions),
        'decisions_with_ties':sum(d['max_ties']>1 for d in decisions),
        'top1_top2_gap_range':[min(d['top1_top2_gap'] for d in decisions),max(d['top1_top2_gap'] for d in decisions)],
        'comparisons':groups,'tasks_first_repeat':{},'scope':r['scope']}
    for tid in sorted({c['task_id'] for c in r['comparisons']},key=lambda t:int(t.split('/')[1])):
        n=tid.split('/')[1]
        a=r['decisions'][f'd1_prefill_r0_he{n}'];b=r['decisions'][f'd1_cached_r0_he{n}']
        c=next(c for c in r['comparisons'] if c['left']==f'd1_prefill_r0_he{n}' and c['right']==f'd1_cached_r0_he{n}')
        summary['tasks_first_repeat'][tid]={'prefill':a,'cached':b,'cross_mode_logit_delta':c['logits'],
                                             'first_changed_module':c['first_changed_module']}
    with (ROOT/'evidence/tensor_summary.json').open('x') as f:json.dump(summary,f,indent=2)
    print(json.dumps({k:v for k,v in summary.items() if k!='tasks_first_repeat'},indent=2))


if __name__=='__main__':main()
