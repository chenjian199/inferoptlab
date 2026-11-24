import argparse
import json
import sys
from pathlib import Path
from tools.specs import Catalog,ROOT,SpecError
from benchmark.common.offline import load_plan,output,report
from benchmark.breakdown.trace import summarize
from benchmark.breakdown.operators import prepare


def main(argv=None):
    p=argparse.ArgumentParser(description='Offline E2E/module/kernel/replay preparation and overlap-aware trace summaries')
    p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('plan');q.add_argument('plan',type=Path);q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('trace');q.add_argument('capture',type=Path);q.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        c=Catalog(a.root);c.load()
        if a.command=='trace':result=summarize(c,a.capture)
        else:
            plan=load_plan(c,a.plan,'BreakdownPlan')
            result=report(c,plan,'breakdown','plan','awaiting_evidence',dict(
                stages=plan['stages'],operator_targets=plan['operator_targets'],operator_cases=prepare(c,plan),
                capture=plan['capture'],replay=plan['replay'],timing=plan['timing'],
                blockers=['No qualified native mcTracer/mcProfiler adapter is connected.',
                          'Real model path/shape/rank distributions and baseline self-replay evidence are required.',
                          'Operator-specific numeric thresholds and candidate implementations are not supplied.']),
                limitations=['Summed kernel work is not E2E critical-path time.','Instrumented collection is separate from unprofiled performance scoring.'])
        output(c,a.out,result)
        print(json.dumps(dict(output=str(a.out),kind=result['kind'],new_gpu_execution=False),ensure_ascii=False));return 0
    except (SpecError,OSError,ValueError,KeyError,TypeError) as exc:
        print('breakdown: '+str(exc),file=sys.stderr);return 2
