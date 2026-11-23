"""Conservative deterministic observations: correlations are not root causes."""
from collections import defaultdict
from itertools import combinations
from statistics import mean

from tools.specs import SpecError, digest
from diagnosis.contracts import finish, header, snapshot, validate
from diagnosis.evidence import load_batch


def context(catalog,plan):
    result=[]
    for field in ('calibration_refs','historical_refs'):
        for ref in plan[field]:
            d=catalog.get(ref)
            source_errors=[]
            for item in catalog.closure(d):
                if item['kind']=='SourceDocument':source_errors+=catalog.semantic_errors(item,verify_sources=True)
            result.append(dict(ref=ref,evidence_kind=d['evidence_kind'],document_sha256=digest(d),
                title=d['title'],source_issues=source_errors,
                applicability='context_only; requires model/runtime/dtype/shape/topology matching',
                causal_evidence=False))
    return result


def compare(rows,policy):
    result=[]
    for axis in ('input_tokens','concurrency'):
        groups=defaultdict(lambda:defaultdict(list))
        for row in rows:
            if row['eligible']:groups[row['grouping'][axis]][row[axis]].append(row)
        for fingerprint,points in sorted(groups.items()):
            for low,high in combinations(sorted(points),2):
                before,after=points[low],points[high]
                # Independent repetitions, not retries, determine confidence.
                qualified=all(len({r['repetition'] for r in side})>=policy['min_repetitions'] and
                              all(r['counts']['planned']>=policy['min_requests'] for r in side) for side in (before,after))
                values=dict(baseline_point=low,candidate_point=high)
                for metric in ('ttft_mean_ms','tpot_mean_ms','e2e_mean_ms','output_tokens_per_s'):
                    def estimate(side):
                        samples=[r['metrics'][metric] for r in side]
                        return mean(samples) if all(v is not None for v in samples) else None
                    a=estimate(before);b=estimate(after)
                    values[metric]=dict(baseline=a,candidate=b,ratio=b/a if a and b is not None else None)
                if axis=='concurrency':
                    ratio=values['output_tokens_per_s']['ratio']
                    values['scaling_efficiency']=ratio/(high/low) if ratio is not None else None
                limits=['descriptive comparison; no randomization/control or causal confirmation',
                        'point estimates average independent runs equally; requests are not pooled across runs']
                if not qualified:limits.append('insufficient requests or independent repetitions for the configured evidence floor')
                if axis=='input_tokens':limits.append('input length changes request text; tokenizer/content generator/seed/output/cache/protocol are held constant')
                result.append(dict(id='comparison-'+digest([axis,fingerprint,low,high])[:16],axis=axis,
                    baseline_runs=[r['run_id'] for r in before],candidate_runs=[r['run_id'] for r in after],
                    values=values,sample_qualified=qualified,limitations=limits))
    return result


def diagnose(catalog,plan):
    validate(catalog,plan)
    rows=[];artifacts=[];documents=catalog.closure(plan)
    for entry in plan['batches']:
        batch_rows,batch_artifacts,embedded=load_batch(catalog,entry,plan['study_ref'])
        rows+=batch_rows;artifacts+=batch_artifacts
        # Same identity with different content is an invalid evidence bundle.
        for d in embedded:
            if any(x['id']==d['id'] and x['version']==d['version'] and digest(x)!=digest(d) for x in documents):
                raise SpecError('captured/current document identity collision: '+d['id'])
            documents.append(d)
    if len({r['run_id'] for r in rows})!=len(rows):raise SpecError('duplicate run across batches')
    # Reusing replicate numbers would falsely inflate the sample floor.
    groups=set()
    for r in rows:
        if not r['eligible']:continue
        key=(r['grouping']['concurrency'],r['concurrency'],r['repetition'])
        if key in groups:raise SpecError('duplicate independent repetition; retry cannot count as replicate')
        groups.add(key)
    comparisons=compare(rows,plan['policy'])
    hypotheses=[]
    available={r['id']:r for r in plan['method_refs']}
    def add(identifier,observation,cause,method_ids,evidence):
        methods=[available[i] for i in method_ids if i in available]
        if not methods:return
        cards=[catalog.get(r) for r in methods]
        hypotheses.append(dict(id=identifier,status='needs_evidence',observation=observation,possible_cause=cause,
            alternatives=list(dict.fromkeys(s for c in cards for s in c['alternative_explanations'])),
            evidence_ids=evidence,method_refs=methods,missing_evidence=list(dict.fromkeys(s for c in cards for s in c['required_evidence'])),
            falsification='Run the method card controls; if the proposed component is not exposed on the aligned critical path, or its isolated change leaves E2E unchanged, reject or narrow this explanation.',
            priority='measurement_first',expected_gain=None))
    for c in comparisons:
        v=c['values'];ratio=v['ttft_mean_ms']['ratio']
        if c['axis']=='input_tokens' and ratio is not None and ratio>=plan['policy']['ttft_growth_ratio']:
            add('hypothesis-'+c['id'],'Longer-input TTFT ratio %.3f; this may be expected work growth, not an anomaly.'%ratio,
                'Separate prefill compute/attention from host time, scheduling and transfers.',
                ['request-timing','attention-compressor','compute-gemm','scheduling-graphs'],[c['id']])
        if c['axis']=='concurrency':
            efficiency=v['scaling_efficiency']
            if efficiency is not None and efficiency<plan['policy']['scaling_efficiency_floor']:
                add('hypothesis-'+c['id'],'Throughput scaling efficiency %.3f below the configured triage threshold.'%efficiency,
                    'Queueing, batch limits, device work or the load generator may limit scaling.',
                    ['request-timing','scheduling-graphs','host-serving','memory-state'],[c['id']])
    valid=[r for r in rows if r['eligible']]
    if valid:
        add('hypothesis-phase-boundary','E2E metrics are available, but server/device phase attribution is absent.',
            'Client TTFT cannot isolate queue/prefill, and average TPOT cannot identify a slow kernel.',
            ['request-timing'],[r['run_id'] for r in valid])
    unexplained=['No aligned server/device trace or controlled intervention is present; no kernel, memory or communication bottleneck is confirmed.']
    if not valid:unexplained.append('No eligible runs remain after integrity, status and metric checks.')
    if any(r['counts']['planned']<plan['policy']['min_requests'] for r in valid):unexplained.append('Small qualification samples cannot establish tail-latency or repeatability claims.')
    doc={**header('DiagnosisReport',plan['id']+'-result','阶段二归因报告：观察、假设与证据缺口'),
        'plan_ref':dict(id=plan['id'],version=plan['version']),'plan_sha256':digest(plan),'evidence_kind':'derived',
        'status':'needs_evidence' if valid else 'no_valid_runs','artifacts':sorted({a['path']:a for a in artifacts}.values(),key=lambda a:a['path']),
        'catalog_snapshot':snapshot(documents),'runs':rows,'comparisons':comparisons,'hypotheses':hypotheses,'unexplained':unexplained,
        'context':context(catalog,plan),'limitations':['No new GPU execution. Thresholds route investigations; they are not SLA thresholds or significance tests.',
            'Historical reported measurements and hardware calibrations remain contextual, without cross-platform transfer of gains.',
            'No SLA acceptance, tail confidence interval, critical-path fraction or expected optimization gain is inferred.']}
    doc=finish(doc);validate(catalog,doc);return doc
