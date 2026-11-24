"""Shared stage contracts, kept independent of GPU and profiler packages."""
from tools.specs import SpecError, digest, references
from benchmark.common.io import inside


RESULTS={'DiagnosisReport','AnalysisReport','TraceSummary','OptimizationHandoff'}


def validate(catalog,doc):
    errors=catalog.structural_errors(doc)
    if not errors:errors=catalog.semantic_errors(doc)
    if errors:raise SpecError('\n'.join(errors))


def semantic_errors(catalog,doc,verify_sources=False):
    errors=[]
    kind=doc['kind']
    if kind in RESULTS:
        if digest({k:v for k,v in doc.items() if k!='content_sha256'})!=doc['content_sha256']:
            errors.append('analysis artifact fingerprint mismatch')
        if kind=='OptimizationHandoff':
            for field in ('id','analysis_task_id'):
                if len({t[field] for t in doc['tasks']})!=len(doc['tasks']):
                    errors.append('duplicate handoff '+field)
        snapshots=doc.get('catalog_snapshot',doc.get('context_snapshot',[]))
        seen=set()
        for item in snapshots:
            d=item['document'];key=(item['ref']['id'],item['ref']['version'])
            if key in seen:errors.append('duplicate embedded document')
            seen.add(key)
            if digest(d)!=item['sha256'] or item['ref']!={'id':d.get('id'),'version':d.get('version')}:
                errors.append('embedded document fingerprint/identity mismatch')
            errors+=catalog.structural_errors(d)
        return errors
    if kind=='TraceCapture':
        windows={w['clock_domain']:w for w in doc['windows']}
        if len(windows)!=len(doc['windows']):errors.append('duplicate clock domain window')
        if len({e['id'] for e in doc['events']})!=len(doc['events']):errors.append('duplicate event ID')
        for w in windows.values():
            if w['end_ns']<=w['start_ns']:errors.append('trace window must have positive duration')
        for e in doc['events']:
            w=windows.get(e['clock_domain'])
            if not w or e['start_ns']<w['start_ns'] or e['start_ns']+e['duration_ns']>w['end_ns']:
                errors.append('event outside its clock-domain capture window')
        return errors
    for path,reference,expected in references(doc):
        try:
            target=catalog.get(reference)
            if target['kind']!=expected:errors.append(f'{path}: expected {expected}')
        except SpecError as exc:errors.append(str(exc))
    for field in ('method_refs','historical_refs','calibration_refs'):
        refs=doc.get(field,[])
        if len({(r['id'],r['version']) for r in refs})!=len(refs):errors.append(field+' contains duplicate references')
    if kind=='DiagnosisPlan':
        for batch in doc['batches']:
            for field in ('directory','manifest'):
                try:inside(catalog.root,batch[field])
                except SpecError as exc:errors.append(str(exc))
        if len({b['directory'] for b in doc['batches']})!=len(doc['batches']):errors.append('duplicate batch directory')
    if kind=='AnalysisMethod':
        for field in ('steps','experiments'):
            if len({s['id'] for s in doc[field]})!=len(doc[field]):errors.append('duplicate '+field+' ID')
    if kind=='AnalysisPlan' and not errors and doc['diagnosis_plan_ref']:
        parent=catalog.get(doc['diagnosis_plan_ref']);study=catalog.get(parent['study_ref'])
        for field in ('model_ref','hardware_ref','runtime_ref'):
            if doc[field]!=study[field]:errors.append('analysis scope differs from diagnosis study: '+field)
    return errors


def header(kind,id,title):
    return dict(schema_version='0.2.0',kind=kind,id=id,version='1.0.0',title=title,provenance=[],issues=[],extensions={})


def snapshot(documents):
    unique={(d['id'],d['version']):d for d in documents}
    return [dict(ref=dict(id=d['id'],version=d['version']),sha256=digest(d),document=d) for _,d in sorted(unique.items())]


def finish(doc):
    return {**doc,'content_sha256':digest(doc)}
