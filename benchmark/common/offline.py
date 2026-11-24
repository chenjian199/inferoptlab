"""Contracts for preparation and recomputation, without live execution claims."""
from pathlib import Path
from tools.specs import SpecError, digest, references, read, write
from benchmark.common.io import inside, file_hash


def semantic_errors(catalog, doc, verify_sources=False):
    if doc['kind']=='BenchmarkOfflineReport':
        errors=[]
        if doc['content_sha256']!=digest({k:v for k,v in doc.items() if k!='content_sha256'}):errors.append('offline report digest mismatch')
        for item in doc['context_snapshot']:
            if digest(item['document'])!=item['sha256']:errors.append('embedded context changed')
            errors+=catalog.structural_errors(item['document'])
        if doc['plan']['kind']!=('AccuracyPlan' if doc['module']=='accuracy' else 'BreakdownPlan'):errors.append('report module/plan mismatch')
        if verify_sources:
            for item in doc['artifacts']:
                try:
                    if file_hash(inside(catalog.root,item['path']))!=item['sha256']:errors.append('offline report artifact changed: '+item['path'])
                except (SpecError,OSError) as exc:errors.append(str(exc))
        return errors
    errors=[]
    for path,ref,expected in references(doc):
        try:
            if catalog.get(ref)['kind']!=expected:errors.append(path+': wrong reference type')
        except SpecError as exc:errors.append(str(exc))
    sources=list(doc['method_sources'])
    if doc['kind']=='AccuracyPlan':sources.append(doc['dataset']['manifest'])
    for item in sources:
        try:
            path=inside(catalog.root,item['path'])
            if verify_sources and file_hash(path)!=item['sha256']:errors.append('method source changed: '+item['path'])
        except (SpecError,OSError) as exc:errors.append(str(exc))
    if doc['kind']=='AccuracyPlan':
        ids=doc['dataset']['task_ids']
        if len(ids)!=len(set(ids)):errors.append('duplicate task IDs')
        if doc['dataset']['scope']=='full164' and set(ids)!={f'HumanEval/{i}' for i in range(164)}:errors.append('full164 requires the complete HumanEval task set')
        if doc['dataset']['scope']=='smoke32' and len(ids)!=32:errors.append('smoke32 requires exactly 32 tasks')
    if doc['kind']=='OperatorCase':
        k,n=doc['tensor_contract']['weight_shape_kn']
        if any(shape[1:]!=[n,k] for shape in doc['tensor_contract']['shapes_mnk']):errors.append('MNK shapes differ from KN weight shape')
        for item in doc['fixture_artifacts']:
            try:
                if verify_sources and file_hash(inside(catalog.root,item['path']))!=item['sha256']:errors.append('operator fixture changed')
            except (SpecError,OSError) as exc:errors.append(str(exc))
    return errors


def load_plan(catalog,path,kind):
    plan=read(path)
    if plan.get('kind')!=kind:raise SpecError('expected '+kind)
    errors=catalog.structural_errors(plan) or semantic_errors(catalog,plan,True)
    if errors:raise SpecError('\n'.join(errors))
    return plan


def report(catalog, plan, module, operation, status, findings, artifacts=(), limitations=()):
    closure=catalog.closure(plan)
    result=dict(schema_version='0.2.0',kind='BenchmarkOfflineReport',module=module,operation=operation,status=status,
                new_gpu_execution=False,release_accepted=False,plan=plan,
                context_snapshot=[dict(document=d,sha256=digest(d)) for d in closure],
                findings=findings,artifacts=list(artifacts),limitations=list(limitations))
    result['content_sha256']=digest(result)
    errors=catalog.structural_errors(result)
    if errors:raise SpecError('\n'.join(errors))
    return result


def output(catalog,path,result):
    path=inside(catalog.root,str(path))
    if not path.is_relative_to(catalog.root/'experiments'):
        raise SpecError('new reports must be stored under experiments/')
    write(path,result)


def artifact(root,path,role):
    path=inside(root,str(path))
    return dict(path=path.relative_to(root).as_posix(),sha256=file_hash(path),role=role)
