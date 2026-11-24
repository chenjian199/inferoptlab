import argparse
import json
import sys
from pathlib import Path
from tools.specs import Catalog,ROOT,SpecError
from benchmark.common.offline import load_plan,output,report
from benchmark.accuracy.functional import inspect,compare


def main(argv=None):
    p=argparse.ArgumentParser(description='Offline accuracy preparation and saved HumanEval audit; never executes generated code')
    p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('plan','inspect','compare'):
        c=sub.add_parser(name);c.add_argument('plan',type=Path);c.add_argument('--out',type=Path,required=True)
        if name=='inspect':c.add_argument('--runs',nargs='+',type=Path,required=True)
        if name=='compare':
            c.add_argument('--baseline',nargs=3,type=Path,required=True);c.add_argument('--candidate',nargs=3,type=Path,required=True)
    a=p.parse_args(argv)
    try:
        c=Catalog(a.root);c.load();plan=load_plan(c,a.plan,'AccuracyPlan')
        if a.command=='inspect':result=inspect(c,plan,a.runs)
        elif a.command=='compare':result=compare(c,plan,a.baseline,a.candidate)
        else:
            result=report(c,plan,'accuracy','plan','awaiting_evidence',dict(
                task_count=len(plan['dataset']['task_ids']),required_independent_processes=6,
                gates=['input_environment_integrity','operator_numerics','same_prefix_model_numerics','task_functional_regression'],
                blockers=['Live generation and CPU sandbox adapters are not connected.',
                          'Operator/same-prefix numeric tolerances must be frozen before candidate observation.',
                          'Historical scores cannot replace contemporaneous paired baselines.']))
        output(c,a.out,result)
        print(json.dumps(dict(output=str(a.out),status=result['status'],release_accepted=False),ensure_ascii=False))
        return 0 if result['status'] not in {'fail','invalid','inconclusive'} else 2
    except (SpecError,OSError,ValueError,KeyError,TypeError) as exc:
        print('accuracy: '+str(exc),file=sys.stderr);return 2
