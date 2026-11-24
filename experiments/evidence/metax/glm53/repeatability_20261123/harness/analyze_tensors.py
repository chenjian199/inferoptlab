"""Analyze self-created CPU tensor captures; intended inside the pinned image."""
import hashlib
import itertools
import json
from pathlib import Path
import torch

ROOT = Path('/experiment/evidence')


def metric(a,b):
    if a.shape != b.shape:
        return {'shape_match':False}
    d=(a-b).double()
    return {'shape_match':True,'exact':bool(torch.equal(a,b)),
            'max_abs':float(d.abs().max()),'mean_abs':float(d.abs().mean()),
            'rmse':float(d.square().mean().sqrt()),'reference_abs_max':float(a.abs().max())}


def decision(sample):
    logits=sample['processed_logits'][0]
    values,ids=logits.topk(5)
    token=int(sample['sampled'].reshape(-1)[0])
    cpu=int(logits.argmax())
    gpu=int(sample['argmax'].reshape(-1)[0])
    return {'temperature':sample['temperature'],'seeds':sample['seeds'],'fused':sample['fused'],
        'dtype':sample['logits_dtype'],'sampler':sample['original_sampler_module'],
        'finite':bool(torch.isfinite(logits).all()),'selected':token,
        'cpu_argmax':cpu,'gpu_argmax':gpu,'selected_is_max':bool(logits[token]==logits.max()),
        'selected_equals_cpu_argmax':token==cpu,'max_ties':int((logits==logits.max()).sum()),
        'top_ids':ids.tolist(),'top_logits':values.tolist(),'top1_top2_gap':float(values[0]-values[1])}


def main():
    data={}
    entries=[]
    for process in ['d1','d2']:
        folder=ROOT/('diagnostics_'+process)
        assert json.loads((folder/'complete.json').read_text())['status']=='complete'
        for line in (folder/'probes.jsonl').read_text().splitlines():
            row=json.loads(line);entries.append(row)
            path=ROOT/'diagnostic_tensors'/(row['label']+'.pt')
            data[row['label']]=torch.load(path,map_location='cpu',weights_only=True)
    decisions={label:decision(value['sampling'][0]) for label,value in data.items()}
    assert all(len(value['sampling'])==1 for value in data.values())
    comparisons=[]
    tasks=sorted({row['task_id'] for row in entries},key=lambda tid:int(tid.split('/')[1]))
    for tid in tasks:
        number=tid.split('/')[1]
        pairs=[]
        for mode in ['prefill','cached']:
            for process in ['d1','d2']:
                pairs.extend((f'{process}_{mode}_r{x}_he{number}',f'{process}_{mode}_r{y}_he{number}','within_process_'+mode) for x,y in itertools.combinations(range(3),2))
            pairs.extend((f'd1_{mode}_r{x}_he{number}',f'd2_{mode}_r{x}_he{number}','across_process_'+mode) for x in range(3))
        for process in ['d1','d2']:
            pairs.extend((f'{process}_prefill_r{x}_he{number}',f'{process}_cached_r{x}_he{number}','prefill_vs_cached') for x in range(3))
        for left,right,scope in pairs:
            a,b=data[left],data[right]
            lm=metric(a['sampling'][0]['processed_logits'],b['sampling'][0]['processed_logits'])
            layers=[]
            assert set(a['layers'])==set(b['layers'])
            for name in a['layers']:
                assert len(a['layers'][name])==len(b['layers'][name])==1
                xa,xb=a['layers'][name][0],b['layers'][name][0]
                assert len(xa)==len(xb)
                metrics=[metric(x['last'],y['last']) for x,y in zip(xa,xb)]
                layers.append({'name':name,'outputs':metrics,'exact':all(m.get('exact',False) for m in metrics)})
            comparisons.append({'task_id':tid,'left':left,'right':right,'scope':scope,
                'logits':lm,'winner_changed':decisions[left]['selected']!=decisions[right]['selected'],
                'first_changed_module':next((row['name'] for row in layers if not row['exact']),None),
                'changed_modules':[row for row in layers if not row['exact']]})
    manifest=[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
              for p in sorted((ROOT/'diagnostic_tensors').glob('*.pt'))]
    report={'status':'complete','tasks':len(tasks),'captures':len(data),'decisions':decisions,
            'comparisons':comparisons,'tensor_artifacts':manifest,
            'scope':'Rank 0 synchronous observation, same logical prefix via prefill and forced cached decode, within-process and two fresh-process comparisons. Instrumentation differs from historical unobserved execution.'}
    target=ROOT/'tensor_analysis.json'
    with target.open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps({'captures':len(data),'greedy_at_max':sum(d['selected_is_max'] for d in decisions.values()),
        'finite':sum(d['finite'] for d in decisions.values()),
        'comparison_count':len(comparisons),'winner_changes':sum(c['winner_changed'] for c in comparisons),
        'max_logit_abs_delta':max(c['logits']['max_abs'] for c in comparisons),
        'first_changed_modules':sorted({c['first_changed_module'] for c in comparisons if c['first_changed_module']})},indent=2))


if __name__=='__main__':
    main()
