"""Produce reviewable investigations; no implicit profiler or optimizer execution."""
from pathlib import Path

from tools.specs import SpecError, digest, read
from benchmark.io import file_hash,inside
from diagnosis.contracts import finish, header, snapshot, validate


def plan_tasks(catalog,plan,diagnosis_path=None):
    validate(catalog,plan)
    report=None;artifact=None
    if diagnosis_path:
        report=read(diagnosis_path);validate(catalog,report)
        if report['kind']!='DiagnosisReport':raise SpecError('expected DiagnosisReport')
        if report['plan_ref']!=plan['diagnosis_plan_ref']:raise SpecError('diagnosis belongs to another plan')
        parent=catalog.get(plan['diagnosis_plan_ref'])
        if report['plan_sha256']!=digest(parent):raise SpecError('diagnosis plan has changed')
        for evidence in report['artifacts']:
            if file_hash(inside(catalog.root,evidence['path']))!=evidence['sha256']:
                raise SpecError('diagnosis evidence changed: '+evidence['path'])
        # Preserve meaning of the already diagnosed evidence and method revisions.
        for item in report['catalog_snapshot']:
            if digest(catalog.get(item['ref']))!=item['sha256']:raise SpecError('diagnosis dependency changed: '+item['ref']['id'])
        artifact=dict(path=str(Path(diagnosis_path).resolve()),sha256=file_hash(diagnosis_path),role='diagnosis_report')
    elif plan['diagnosis_plan_ref']:
        raise SpecError('--diagnosis is required for this plan')
    model=catalog.get(plan['model_ref']);hardware=catalog.get(plan['hardware_ref'])
    hypotheses=report['hypotheses'] if report else []
    eligible=[r for r in report['runs'] if r['eligible']] if report else []
    for r in eligible:
        for field in ('model_ref','hardware_ref','runtime_ref'):
            if r['scope'][field]!=plan[field]:raise SpecError('diagnosis run scope differs from analysis plan')
    architecture=model['architecture'];devices=hardware['resources']['allocated_devices']
    preflight=[]
    if report and any(not c['sample_qualified'] for c in report['comparisons']):
        preflight.append('Baseline observations are below the configured repetition/sample floor; repeat unprofiled controls before causal conclusions or acceptance.')
    if plan['runtime_ref'] is None:preflight.append('No target inference RuntimeSpec is selected or qualified.')
    if not eligible:preflight.append('No eligible E2E baseline for this exact model/hardware/runtime; establish one before attributing performance.')
    checkpoint=model.get('checkpoint') or {}
    capacity=sum(d.get('observed',{}).get('memory_bytes',0) for n in hardware['resources']['nodes'] for d in n['devices'])
    if checkpoint.get('total_file_bytes',0)>capacity>0:
        preflight.append('Checkpoint file bytes exceed allocated physical VRAM; resident layout/offload/multinode feasibility must be resolved before launch. File size is not an exact resident-memory estimate.')
    if hardware.get('discovery',{}).get('availability')=='occupied':preflight.append('Hardware snapshot recorded occupied GPUs; obtain a fresh resource check before any capture.')
    # Put hypothesis-linked methods first, preserving configured order otherwise.
    preferred=[r for h in hypotheses for r in h['method_refs']]
    methods=sorted(enumerate(plan['method_refs']),key=lambda pair:(pair[1] not in preferred,pair[0]))
    tasks=[];spent=0;active=0
    for _,reference in methods:
        method=catalog.get(reference)
        matches=[h for h in hypotheses if reference in h['method_refs']]
        status='needs_capture' if eligible else 'awaiting_baseline'
        reason='An E2E observation needs the method-specific evidence and a controlled experiment.' if eligible else 'Model inspection and historical notes support planning only.'
        arch=method['applicability']['architectures']
        if 'any' not in arch and architecture['type'] not in arch:
            status='not_applicable';reason='Inspected architecture does not match the method applicability.'
        if reference['id']=='communication' and devices==1:
            status='not_applicable';reason='Current allocation is one device; no inter-rank collective is attributable to this baseline.'
        if reference['id']=='speculation' and not architecture.get('mtp_layers'):
            status='not_applicable';reason='No MTP layer in this inspected model; no draft deployment is supplied.'
        if reference['id']=='precision-kernels' and model['precision']['quantization'] is None:
            status='not_applicable';reason='Current checkpoint is unquantized; changing precision requires a new model/quality contract.'
        budget=method['budget'];capture_seconds=budget['max_capture_seconds']*budget['minimum_repetitions']*budget['max_variants']
        if not devices:raise SpecError('a concrete allocated-device count is required to estimate GPU-second budgets')
        estimated=capture_seconds*devices
        if status!='not_applicable':
            if active>=plan['budget']['max_tasks'] or spent+estimated>plan['budget']['max_proposed_gpu_seconds']:
                status='deferred_budget';reason='Proposed capture envelope exceeds this plan budget; task retained.'
            else:spent+=estimated;active+=1
        available=['model_configuration','hardware_inventory']
        if eligible:available.append('client_request_metrics')
        needed=method['required_evidence']
        tasks.append(dict(id='task-'+reference['id'],method_ref=reference,title=method['title'],status=status,reason=reason,
            hypothesis_ids=[h['id'] for h in matches],required_evidence=needed,available_evidence=available,
            missing_evidence=[e for e in needed if e not in available],
            scope=dict(model_ref=plan['model_ref'],hardware_ref=plan['hardware_ref'],runtime_ref=plan['runtime_ref'],
                baseline_run_ids=[r['run_id'] for r in eligible],architecture=architecture,precision=model['precision'],
                inspected_weight_file_bytes=checkpoint.get('total_file_bytes'),physical_memory_bytes=capacity or None),
            method_snapshot=method,budget={**budget,'proposed_capture_seconds':capture_seconds,'allocated_devices':devices,'proposed_gpu_seconds':estimated,
                'counts_launch_compile_or_acceptance_time':False},execution_authorized=False,result=None))
    documents=catalog.closure(plan)
    doc=finish({**header('AnalysisReport',plan['id']+'-tasks','阶段三专项分析任务包'),
        'plan_ref':dict(id=plan['id'],version=plan['version']),'plan_sha256':digest(plan),'execution':'plan_only',
        'diagnosis_artifact':artifact,'context_snapshot':snapshot(documents),'tasks':tasks,'preflight_issues':preflight,
        'proposed_gpu_seconds':spent,'limitations':[
            'No GPU jobs, profiler commands, model loads or code modifications are performed by this planner.',
            'Capture budgets are proposed ceilings, not measured costs; startup, compile and independent acceptance require a separate execution budget.',
            'Native profiler adapters are unverified. Method cards describe evidence requirements, not demonstrated profiler support.',
            'OptimizationTask export remains gated by observed callsites, frozen source, correctness harness and independent E2E acceptance.']})
    validate(catalog,doc);return doc


def render(doc):
    lines=['# 阶段三：专项分析任务包','','执行状态：`plan_only`。各任务的 `result` 为空，尚未执行采集或确认根因。','',
        '## 前置条件','',*['- '+s for s in doc['preflight_issues']],'',
        f"拟议采集预算上限：{doc['proposed_gpu_seconds']} GPU 秒；不含启动、编译和正式验收。",'']
    for t in doc['tasks']:
        m=t['method_snapshot']
        lines += [f"## {t['id']} · {t['title']}",'',f"状态：`{t['status']}`。{t['reason']}",'',
            '关联假设：'+(', '.join(t['hypothesis_ids']) or '尚无实测假设'),'','所需证据：',*['- '+s for s in t['missing_evidence']],'',
            '采集边界：'+m['capture']['boundary'],'','采集字段：','',
            '| 字段 | 单位 | 含义 |','|---|---|---|',*[f"| {f['name']} | {f['unit']} | {f['meaning']} |" for f in m['capture']['fields']],'',
            '分析步骤：',*[f"{i}. {s['action']} → {s['deliverable']}" for i,s in enumerate(m['steps'],1)],'',
            '区分实验：']
        for e in m['experiments']:
            lines += [f"- {e['id']}：{e['change']}",'  固定：'+'；'.join(e['controls']),'  支持：'+e['supports'],'  证伪：'+e['refutes']]
        lines += ['','计算口径：',*[f"- {x['name']}：`{x['formula']}` [{x['unit']}]。{x['limitations']}" for x in m['calculations']],'',
            '正确性检查：',*['- '+x for x in m['correctness_checks']],'','完成条件：',*['- '+x for x in m['exit_criteria']],'',
            '优化交接：'+m['handoff']['target'],'','回退：'+m['handoff']['rollback'],'']
    lines+=['## 边界','',*['- '+s for s in doc['limitations']]]
    return '\n'.join(lines)+'\n'
