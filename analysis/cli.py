import argparse
import json
from pathlib import Path
import sys

from tools.specs import ROOT,Catalog,SpecError,read,write
from analysis.planner import plan_tasks,render


def main(argv=None):
    p=argparse.ArgumentParser(description='Stage 3 investigation planning; offline only')
    p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('plan');s.add_argument('plan',type=Path);s.add_argument('--diagnosis',type=Path);s.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        c=Catalog(a.root);c.load()
        plan=read(a.plan)
        if plan.get('kind')!='AnalysisPlan':raise SpecError('expected AnalysisPlan')
        result=plan_tasks(c,plan,a.diagnosis);a.out.mkdir(parents=True,exist_ok=False)
        write(a.out/'analysis.yaml',result);(a.out/'report.md').write_text(render(result),encoding='utf-8')
        print(json.dumps(dict(output=str(a.out),kind=result['kind'],new_gpu_execution=False)));return 0
    except (SpecError,OSError,ValueError,KeyError,TypeError) as e:
        print('analysis: '+str(e),file=sys.stderr);return 2
