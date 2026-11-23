import argparse
import json
from pathlib import Path
import sys

from tools.specs import ROOT, Catalog, SpecError, read, write
from benchmark.io import file_hash
from diagnosis.contracts import validate
from diagnosis.engine import diagnose
from diagnosis.report import render


def main(argv=None):
    p=argparse.ArgumentParser(description='Stage 2 offline diagnosis; never starts GPU jobs')
    p.add_argument('--root',type=Path,default=ROOT)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ('plan','run'):
        s=sub.add_parser(name);s.add_argument('plan',type=Path)
        if name=='run':s.add_argument('--out',type=Path,required=True)
    s=sub.add_parser('seal',help='hash an already completed batch; creates an evidence manifest, not authenticity proof')
    s.add_argument('directory',type=Path);s.add_argument('--out',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        if a.command=='seal':
            directory=a.directory.resolve();target=a.out.resolve()
            if not directory.is_dir():raise SpecError('batch directory missing')
            if not directory.is_relative_to(target.parent):raise SpecError('manifest parent must contain batch directory')
            state=read(directory/'batch.json')['status']
            if state not in {'completed','completed_with_errors','failed','stopped'}:raise SpecError('cannot seal an active batch')
            value={f.relative_to(target.parent).as_posix():file_hash(f) for f in sorted(directory.rglob('*')) if f.is_file()}
            write(target,value);print(json.dumps(dict(path=str(target),sha256=file_hash(target))));return 0
        c=Catalog(a.root);c.load();plan=read(a.plan);validate(c,plan)
        if plan['kind']!='DiagnosisPlan':raise SpecError('expected DiagnosisPlan')
        if a.command=='plan':
            print(json.dumps(dict(batches=len(plan['batches']),methods=len(plan['method_refs']),execution='offline_only'),indent=2));return 0
        result=diagnose(c,plan)
        a.out.mkdir(parents=True,exist_ok=False)
        write(a.out/'diagnosis.yaml',result)
        (a.out/'report.md').write_text(render(result),encoding='utf-8')
        print(json.dumps(dict(output=str(a.out),status=result['status'],runs=len(result['runs']),hypotheses=len(result['hypotheses']))));return 0
    except (SpecError,OSError,ValueError,KeyError,TypeError) as e:
        print('diagnosis: '+str(e),file=sys.stderr);return 2
