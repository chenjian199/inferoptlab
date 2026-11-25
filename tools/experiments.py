"""Immutable experiment records, verified local index and explicit baseline labels."""
import argparse
import json
from pathlib import Path
import re
import sys

from benchmark.common.io import file_hash, inside, json_write, utc_now
from benchmark.load.cli import load_snapshot
from benchmark.load.planner import embedded_catalog
from tools.specs import Catalog, ROOT, SpecError, digest, read, write


def check(catalog, document):
    errors=catalog.structural_errors(document)
    if errors:raise SpecError('\n'.join(errors))
    if digest({k:v for k,v in document.items() if k!='content_sha256'})!=document['content_sha256']:
        raise SpecError('experiment record digest mismatch')
    for item in document.get('artifacts',[]):
        if file_hash(inside(catalog.root,item['path']))!=item['sha256']:
            raise SpecError('experiment artifact changed: '+item['path'])
    if document['kind']=='ExperimentRecord':
        artifacts={item['path'] for item in document['artifacts']}
        batch=inside(catalog.root,document['batch_path'])
        directory=batch/document['id']
        def pinned(path):
            if path.relative_to(catalog.root).as_posix() not in artifacts:
                raise SpecError('record requires a pinned artifact: '+str(path))
            return read(path)
        for key,path in [('recipe_snapshot',batch/'resolved.yaml'),('run_configuration',directory/'resolved.yaml'),
                         ('measurement',directory/'summary.json'),('sla',directory/'sla.json')]:
            if document[key]!=pinned(path):raise SpecError('record differs from pinned '+key)
        for key in ('environment','commands'):
            if document[key] is not None and document[key]!=pinned(directory/(key+'.json')):
                raise SpecError('record differs from pinned '+key)
        run=pinned(directory/'run.json');config=document['run_configuration'];trial=config['trial'];dep=config['deployment']
        expected=dict(status=run['status'],model_ref=dep['model_ref'],hardware_ref=dep['hardware_ref'],runtime_ref=dep['runtime_ref'],
                      deployment_ref=trial['deployment_ref'],phase=config['protocol']['scope'],method=config['protocol']['method'],
                      concurrency=trial['concurrency'],repetition=run['repetition'],snapshot_state=document['recipe_snapshot']['state'])
        if run['id']!=document['id'] or any(document[k]!=v for k,v in expected.items()):
            raise SpecError('record metadata differs from pinned configuration')


def register_batch(catalog, batch):
    batch=Path(batch).resolve()
    if not batch.is_relative_to(catalog.root):raise SpecError('batch must be inside project')
    state=read(batch/'batch.json')
    if state['status'] not in {'completed','completed_with_errors','failed','stopped'}:
        raise SpecError('only terminal batches can be registered')
    snapshot=load_snapshot(catalog,batch/'resolved.yaml')
    if state['plan_sha256']!=snapshot['content_sha256']:raise SpecError('batch snapshot mismatch')
    embedded=embedded_catalog(catalog,snapshot)
    trials={(t['id'],t['repetition']):t for t in snapshot['trials']}
    records=[]
    for entry in state['runs']:
        if not entry.get('directory'):continue
        directory=inside(batch,entry['directory'])
        run=read(directory/'run.json');summary=read(directory/'summary.json');resolved=read(directory/'resolved.yaml')
        if not re.fullmatch(r'[a-zA-Z0-9._-]+',run['id']):raise SpecError('invalid run ID')
        identity=(run['trial_id'],run['repetition'])
        if identity not in trials or entry['trial_id']!=run['trial_id'] or entry['repetition']!=run['repetition'] or entry['status']!=run['status']:
            raise SpecError('run ledger identity mismatch')
        if run['plan_sha256']!=snapshot['content_sha256'] or summary['run_id']!=run['id']:
            raise SpecError('run/result identity mismatch')
        if summary['comparison_sha256']!=run['comparison_sha256']:
            raise SpecError('result comparison identity mismatch')
        # Recompute the immutable request evidence before accepting it into the index.
        from benchmark.load.metrics.normalize import normalize
        from diagnosis.evidence import close
        workload=resolved['workload'];manifest=run['dataset_manifest']
        raw=directory/'raw/aiperf/profile_export.jsonl'
        _,computed=normalize(raw,manifest['files']['requests.jsonl']['session_ids'],workload['input']['tokens'],workload['output']['tokens'],run['id'],run['comparison_sha256'],summary['evidence_kind'])
        for field in ('counts','statistics','rates','duration_s','raw_sha256'):
            if not close(summary[field],computed[field]):raise SpecError('stored result differs from raw '+field)
        dep=resolved['deployment'];scene=embedded.get(trials[identity]['scenario_ref'])
        case=embedded.get(scene['case_ref'])
        from benchmark.load.counts import at_point,fixture_name,protocol_at_point
        declared=embedded.get(case['workload_ref'])
        if resolved['trial']!=trials[identity] or dep!=embedded.get(trials[identity]['deployment_ref']) or resolved['case']!=case or workload!=at_point(declared,trials[identity]['concurrency']) or resolved['protocol']!=protocol_at_point(embedded.get(case['protocol_ref']),trials[identity]['concurrency']):
            raise SpecError('resolved recipe differs from batch snapshot')
        fixture=batch/'datasets'/fixture_name(scene,declared,trials[identity]['concurrency'])
        if read(fixture/'manifest.json')!=manifest:raise SpecError('dataset manifest differs')
        for filename,info in manifest['files'].items():
            if file_hash(inside(fixture,filename))!=info['sha256']:raise SpecError('dataset changed')
        if resolved['protocol']['method']=='prefix_reuse_decode':
            from benchmark.load.cache import verify_replay
            cached=verify_replay(directory,manifest['files']['requests.jsonl']['session_ids'],workload,resolved['protocol'],manifest['files']['requests.jsonl']['sha256'])
            if cached!=summary.get('cache_replay'):raise SpecError('stored cache result differs from raw evidence')
            if cached['status']!='passed' and summary['validity']=='valid':raise SpecError('invalid cache evidence cannot be a valid result')
        paths=[batch/'resolved.yaml',*directory.rglob('*'),*fixture.rglob('*')]
        artifacts=[dict(path=p.relative_to(catalog.root).as_posix(),sha256=file_hash(p)) for p in sorted(set(paths)) if p.is_file()]
        data=dict(schema_version='0.2.0',kind='ExperimentRecord',id=run['id'],batch_id=state['id'],
                  batch_path=batch.relative_to(catalog.root).as_posix(),status=run['status'],
                  model_ref=dep['model_ref'],hardware_ref=dep['hardware_ref'],runtime_ref=dep['runtime_ref'],
                  deployment_ref=trials[identity]['deployment_ref'],phase=resolved['protocol']['scope'],
                  method=resolved['protocol']['method'],concurrency=trials[identity]['concurrency'],repetition=run['repetition'],
                  snapshot_state=snapshot['state'],recipe_snapshot=snapshot,run_configuration=resolved,
                  environment=read(directory/'environment.json') if (directory/'environment.json').exists() else None,
                  commands=read(directory/'commands.json') if (directory/'commands.json').exists() else None,
                  measurement=summary,sla=read(directory/'sla.json'),artifacts=artifacts)
        data['content_sha256']=digest(data)
        check(catalog,data)
        output=catalog.root/'experiments/records'/f'{run["id"]}.yaml'
        if output.exists():
            if read(output)!=data:raise SpecError('record identity already exists with different content')
        else:write(output,data)
        records.append(output)
    return records


def index(catalog):
    rows=[];errors=[]
    for path in sorted((catalog.root/'experiments/records').glob('*.yaml')):
        try:
            record=read(path);check(catalog,record)
            rows.append({**{k:record[k] for k in ('id','batch_id','model_ref','hardware_ref','runtime_ref','deployment_ref','phase','method','status','concurrency','repetition','content_sha256')},
                         'path':path.relative_to(catalog.root).as_posix(),'measurement':record['measurement'],'sla':record['sla']})
        except (SpecError,OSError) as exc:errors.append(dict(path=str(path),error=str(exc)))
    baselines=[]
    for path in sorted((catalog.root/'experiments/baselines').glob('*.yaml')):
        try:
            label=read(path);check(catalog,label)
            for item in label['records']:
                if not any(r['id']==item['id'] and r['content_sha256']==item['sha256'] for r in rows):
                    raise SpecError('baseline record is missing or changed')
            baselines.append(label)
        except (SpecError,OSError) as exc:errors.append(dict(path=str(path),error=str(exc)))
    sources=[]
    for d in catalog.documents.values():
        if d['kind']!='SourceDocument':continue
        path=inside(catalog.root,d['path'])
        status='missing' if not path.is_file() else 'verified' if file_hash(path)==d['sha256'] else 'changed'
        sources.append(dict(ref={'id':d['id'],'version':d['version']},path=path.relative_to(catalog.root).as_posix(),
                            sha256=d['sha256'],integrity=status,role=d['role'],title=d['title']))
    offline=[]
    for module in ('accuracy','breakdown'):
        for path in sorted((catalog.root/'experiments/runs'/module).rglob('*.yaml')):
            try:
                doc=read(path)
                if doc.get('kind')!='BenchmarkOfflineReport':continue
                problems=catalog.structural_errors(doc) or catalog.semantic_errors(doc,verify_sources=True)
                if problems:raise SpecError('; '.join(problems))
                offline.append(dict(path=path.relative_to(catalog.root).as_posix(),module=doc['module'],operation=doc['operation'],
                                    status=doc['status'],model_ref=doc['plan']['model_ref'],hardware_ref=doc['plan']['hardware_ref'],
                                    content_sha256=doc['content_sha256'],release_accepted=False,new_gpu_execution=False))
            except (SpecError,OSError,KeyError,ValueError) as exc:errors.append(dict(path=str(path),error=str(exc)))
    result=dict(format_version=1,generated_at=utc_now(),runs=rows,offline_reports=offline,sources=sources,baselines=baselines,errors=errors)
    json_write(catalog.root/'experiments/index.json',result)
    return result


def baseline(catalog, name, record_ids, purpose, note):
    if not re.fullmatch(r'[a-z0-9][a-z0-9._-]*',name):raise SpecError('invalid baseline name')
    if not record_ids or len(record_ids)!=len(set(record_ids)):raise SpecError('baseline requires unique run IDs')
    records=[];scope=None
    for identity in record_ids:
        if not re.fullmatch(r'[a-zA-Z0-9._-]+',identity):raise SpecError('invalid run ID')
        record=read(catalog.root/'experiments/records'/f'{identity}.yaml');check(catalog,record)
        current=[record[k] for k in ('model_ref','hardware_ref','runtime_ref','deployment_ref')]
        if scope is not None and current!=scope:raise SpecError('baseline runs must have identical model/hardware/runtime/deployment scope')
        scope=current
        if record['status']!='completed' or record['measurement']['validity']!='valid' or record['measurement']['counts']['failed'] or record['measurement']['evidence_kind']!='measured':
            raise SpecError('baseline requires completed, valid measured runs')
        if purpose=='performance' and (record['snapshot_state']!='frozen' or record['sla']['status']!='passed'):
            raise SpecError('performance baseline requires frozen inputs and passed performance SLA; use workflow for qualification data')
        records.append(dict(id=identity,sha256=record['content_sha256']))
    result=dict(schema_version='0.2.0',kind='BaselineRecord',id=name,purpose=purpose,note=note,created_at=utc_now(),records=records,
                quality_acceptance='not_established_by_baseline_label')
    result['content_sha256']=digest(result);check(catalog,result)
    output=catalog.root/'experiments/baselines'/f'{name}.yaml';write(output,result)
    return output


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    add=sub.add_parser('register');add.add_argument('batch',type=Path)
    sub.add_parser('index')
    q=sub.add_parser('query')
    q.add_argument('--module',choices=['load','accuracy','breakdown'])
    for name in ('model','hardware','phase','status'):q.add_argument('--'+name)
    b=sub.add_parser('baseline');b.add_argument('name');b.add_argument('--runs',nargs='+',required=True);b.add_argument('--purpose',choices=['workflow','performance'],default='workflow');b.add_argument('--note',required=True)
    a=p.parse_args(argv)
    try:
        c=Catalog(a.root);c.load()
        if a.command=='register':result=[str(path) for path in register_batch(c,inside(c.root,str(a.batch)))];index(c)
        elif a.command=='baseline':result=str(baseline(c,a.name,a.runs,a.purpose,a.note));index(c)
        else:
            result=index(c)
            if a.command=='query':
                result={**result,'runs':[r for r in result['runs'] if all(getattr(a,k) is None or (r[k+'_ref']['id'] if k in {'model','hardware'} else r[k])==getattr(a,k) for k in ('model','hardware','phase','status'))]}
                result['offline_reports']=[r for r in result['offline_reports'] if a.module in (None,r['module']) and a.phase is None and all(getattr(a,k) is None or (r[k+'_ref']['id'] if k in {'model','hardware'} else r[k])==getattr(a,k) for k in ('model','hardware','status'))]
                if a.module in {'accuracy','breakdown'}:result['runs']=[];result['baselines']=[]
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (SpecError,OSError,KeyError,ValueError) as exc:
        print('experiments: '+str(exc),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())
