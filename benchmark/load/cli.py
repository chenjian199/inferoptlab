"""CLI for planning, fixture preparation, execution and offline recomputation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.specs import ROOT, Catalog, SpecError, digest, read, write
from benchmark.load import dataset
from benchmark.common.io import inside, file_hash, json_write, jsonl_write
from benchmark.load.planner import embedded_catalog, resolve, scenario_parts, snapshot_errors
from benchmark.load.metrics.normalize import normalize
from benchmark.load.metrics.evaluate import evaluate
from benchmark.load.metrics.report import run_report, batch_report
from benchmark.load.counts import at_point, fixture_source, protocol_at_point


def load_snapshot(catalog,path,freeze=False):
    value=read(path)
    if value.get('kind')=='ResolvedBenchmark':
        errors=catalog.structural_errors(value) or snapshot_errors(catalog,value,verify_sources=freeze)
        if errors:
            raise SpecError('\n'.join(errors))
        if freeze and value['state']!='frozen':
            raise SpecError('freeze the original BenchmarkPlan after resolving readiness issues')
        return value
    return resolve(catalog,value,freeze=freeze)


def analyze(catalog,directory,output):
    directory=directory.resolve()
    snapshot=load_snapshot(catalog,directory.parent/'resolved.yaml')
    embedded=embedded_catalog(catalog,snapshot)
    record=json.loads((directory/'run.json').read_text(encoding='utf-8'))
    if record['plan_sha256']!=snapshot['content_sha256']:
        raise SpecError('run/snapshot fingerprint mismatch')
    trials=[t for t in snapshot['trials'] if t['id']==record['trial_id'] and t['repetition']==record['repetition']]
    if len(trials)!=1:
        raise SpecError('run does not identify exactly one frozen trial')
    trial=trials[0]
    scene,case,workload,protocol=scenario_parts(embedded,trial['scenario_ref'])
    workload=at_point(workload,trial['concurrency'])
    protocol=protocol_at_point(protocol,trial['concurrency'])
    manifest=record['dataset_manifest']
    comparison=digest(dict(contract=trial['comparison_sha256'],dataset=manifest['files'],tokenizer=manifest['tokenizer']['sha256']))
    if comparison!=record['comparison_sha256']:
        raise SpecError('run dataset/comparison fingerprint mismatch')
    raw=directory/'raw/aiperf/profile_export.jsonl'
    original=json.loads((directory/'summary.json').read_text(encoding='utf-8'))
    if original['raw_sha256'] is not None and file_hash(raw)!=original['raw_sha256']:
        raise SpecError('raw AIPerf export changed since original collection')
    records,bundle=normalize(raw,manifest['files']['requests.jsonl']['session_ids'],workload['input']['tokens'],workload['output']['tokens'],record['id'],comparison,evidence_kind=original['evidence_kind'])
    if protocol['method']=='prefix_reuse_decode':
        from benchmark.load.cache import verify_replay
        bundle['cache_replay']=verify_replay(directory,manifest['files']['requests.jsonl']['session_ids'],workload,protocol,manifest['files']['requests.jsonl']['sha256'])
        bundle['issues']+=bundle['cache_replay']['issues']
    # Collection/process validity cannot be repaired merely by rerunning aggregation.
    bundle['issues']=sorted(set(bundle['issues']+original['issues']))
    if bundle['issues']:
        bundle['validity']='incomplete' if bundle['counts']['missing'] else 'invalid'
    deployment=embedded.get(trial['deployment_ref'])
    hardware=embedded.get(deployment['hardware_ref'])
    verdict=evaluate(embedded.get(case['sla_ref']) if case['sla_ref'] else None,bundle,records,hardware['resources']['allocated_devices'],record['environment_issues'])
    output.mkdir(parents=True,exist_ok=False)
    jsonl_write(output/'requests.jsonl',records)
    json_write(output/'summary.json',bundle)
    json_write(output/'sla.json',verdict)
    json_write(output/'provenance.json',dict(source_run=str(directory),source_raw_sha256=bundle['raw_sha256'],operation='offline_reanalysis',new_gpu_execution=False))
    if protocol['scope'] == 'decode' and protocol['method'] == 'full_request':
        from benchmark.load.metrics.decode import report as decode_report
        decode_report(output, records, bundle, record['environment_issues'])
    run_report(output,record,bundle,verdict)
    return bundle


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    commands=parser.add_subparsers(dest='command',required=True)
    plan=commands.add_parser('plan',help='validate and preview a deterministic matrix without launching processes')
    plan.add_argument('path',type=Path)
    plan.add_argument('--out',type=Path)
    plan.add_argument('--freeze',action='store_true')
    prep=commands.add_parser('prepare',help='generate or import exact-length single-turn request fixtures')
    prep.add_argument('path',type=Path)
    prep.add_argument('--tokenizer',type=Path,required=True,help='local tokenizer directory; no implicit download/remote code')
    prep.add_argument('--input',type=Path,help='JSONL text fixture; only allowed for a single-scenario plan')
    run=commands.add_parser('run',help='execute on the Linux benchmark host')
    run.add_argument('path',type=Path)
    run.add_argument('--out',type=Path)
    run.add_argument('--qualification',type=Path,help='Matching startup qualification receipt')
    run.add_argument('--resume',type=Path,help='Resume this batch with its exact archived snapshot; preserve all attempts')
    run.add_argument('--skip-failed-configurations',action='store_true',help='Record user-directed failure skips; never retry a failed configuration')
    qualification=commands.add_parser('qualify',help='Start each deployment and verify exact-length API probes; no performance scoring')
    qualification.add_argument('path',type=Path)
    qualification.add_argument('--out',type=Path,required=True)
    selection=commands.add_parser('select',help='Write a reduced plan containing only successfully qualified deployments')
    selection.add_argument('path',type=Path)
    selection.add_argument('--qualification',type=Path,required=True)
    selection.add_argument('--out',type=Path,required=True)
    recalc=commands.add_parser('analyze',help='recompute an archived run without GPU execution')
    recalc.add_argument('directory',type=Path)
    recalc.add_argument('--out',type=Path,required=True)
    report=commands.add_parser('report',help='regenerate a batch comparison report')
    report.add_argument('directory',type=Path)
    args=parser.parse_args(argv)
    try:
        catalog=Catalog(args.root)
        catalog.load()
        if args.command=='plan':
            snapshot=load_snapshot(catalog,args.path,args.freeze)
            if args.out:
                write(args.out,snapshot)
            source_issues=[error for entry in snapshot['documents'] if entry['document']['kind']=='SourceDocument'
                           for error in catalog.semantic_errors(entry['document'],verify_sources=True)]
            print(json.dumps(dict(state=snapshot['state'],trials=len(snapshot['trials']),content_sha256=snapshot['content_sha256'],
                execution_issues=snapshot['execution_issues'],formal_readiness_issue_count=len(snapshot['readiness_issues']),
                source_issues=source_issues,
                output=str(args.out) if args.out else None),ensure_ascii=False,indent=2))
        elif args.command=='prepare':
            snapshot=load_snapshot(catalog,args.path)
            embedded=embedded_catalog(catalog,snapshot)
            plan=embedded.get(snapshot['plan_ref'])
            if args.input and len(plan['scenario_refs'])!=1:
                raise SpecError('--input requires a single-scenario plan')
            for reference in plan['scenario_refs']:
                scene,case,workload,protocol=scenario_parts(embedded,reference)
                points=workload['arrival']['load_points'] if workload['requests'].get('count_multiplier') is not None else [workload['arrival']['load_points'][0]]
                for concurrency in points:
                    target=inside(catalog.root,fixture_source(scene,workload,concurrency))
                    manifest=dataset.prepare(at_point(workload,concurrency),protocol_at_point(protocol,concurrency),args.tokenizer,target,args.input)
                    print(json.dumps(dict(scenario=scene['id'],concurrency=concurrency,directory=str(target),request_set_sha256=manifest['files']['requests.jsonl']['sha256']),ensure_ascii=False))
        elif args.command=='run':
            from benchmark.load.runner import execute
            directory,state=execute(catalog,load_snapshot(catalog,args.path),args.out or catalog.root/'experiments/runs/benchmark',args.qualification,args.resume,args.skip_failed_configurations)
            print(json.dumps(dict(directory=str(directory),status=state['status']),ensure_ascii=False))
            return 0 if state['status'] in {'completed','completed_with_skips','finished_with_failures'} else 1
        elif args.command=='qualify':
            from benchmark.load.qualification import qualify
            from benchmark.load.runner import lease
            with lease(catalog.root):
                receipt=qualify(catalog,load_snapshot(catalog,args.path),args.out)
            print(json.dumps(dict(output=str(args.out),statuses={r['id']:r['status'] for r in receipt['deployments']})))
            return 0 if all(r['status']=='passed' for r in receipt['deployments']) else 1
        elif args.command=='select':
            from benchmark.load.qualification import select_qualified
            if args.out.exists():
                raise SpecError('selected plan output already exists')
            selected=select_qualified(catalog,load_snapshot(catalog,args.path),args.qualification)
            resolve(catalog,selected)
            write(args.out,selected)
            print(json.dumps(dict(output=str(args.out),deployments=selected['deployment_refs'])))
        elif args.command=='analyze':
            bundle=analyze(catalog,args.directory,args.out)
            print(json.dumps(dict(output=str(args.out),validity=bundle['validity']),ensure_ascii=False))
        else:
            state=json.loads((args.directory/'batch.json').read_text(encoding='utf-8'))
            batch_report(args.directory,state['runs'])
            print(args.directory/'report.md')
        return 0
    except (SpecError,OSError,ValueError,KeyError) as exc:
        print(f'benchmark: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
