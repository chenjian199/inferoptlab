"""Read-only source verification and a catalog entry to the supplied search engine."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from benchmark.common.io import inside, file_hash
from tools.specs import ROOT, Catalog, SpecError, read, write


def verify_intake(root):
    """Audit current files against their receipt; never resolve old file names."""
    manifest=read(root/'experiments/evidence/metax/intake/organized-files.json')
    if manifest.get('format_version')!=1 or manifest.get('file_count')!=len(manifest['files']):
        raise SpecError('invalid organized-file inventory')
    seen=set()
    for item in manifest['files']:
        path=inside(root,item['path'])
        if path in seen:raise SpecError('duplicate organized file: '+item['path'])
        seen.add(path)
        if path.stat().st_size!=item['bytes'] or file_hash(path)!=item['sha256']:
            raise SpecError('organized file changed: '+item['path'])
    return dict(files=len(seen),unchanged_since_receipt=sum(i['sha256']==i['received_sha256'] for i in manifest['files']))


def collection(root, name):
    if name!='metax':raise SpecError('unknown collection: '+name)
    doc=read(root/'catalog/library/metax/collection.yaml')
    errors=Catalog(root).structural_errors(doc)
    if errors:raise SpecError('\n'.join(errors))
    base=inside(root,doc['source_root'])
    for artifact in doc['pinned_files']:
        if file_hash(inside(base,artifact['path']))!=artifact['sha256']:
            raise SpecError('collection source changed: '+artifact['path'])
    return doc,base


def build(root,name):
    doc,base=collection(root,name)
    library=base/'catalog/library/metax/hwdoc'
    manifest=read(library/'generated/manifest.json')
    rows=[]
    for item in manifest['documents']:
        path=inside(library,item['filename'])
        if file_hash(path)!=item['sha256']:raise SpecError('PDF changed: '+item['id'])
        rows.append(dict(id=item['id'],kind='vendor_document',title=item['title'],revision=item['document_revision'],
                         publication_date=item['publication_date'],pages=item['page_count'],sha256=item['sha256'],
                         path=path.relative_to(root).as_posix(),navigation=(library/item['navigation_path']).relative_to(root).as_posix(),
                         topics=item['topics'],verification=item['software_compatibility_status']))
    for item in doc['curated']:
        path=inside(base,item['path'])
        rows.append({**item,'path':path.relative_to(root).as_posix(),'sha256':file_hash(path)})
    knowledge=read(library/'generated/knowledge.json')
    for path,expected in knowledge['source_hashes'].items():
        if file_hash(inside(library,path))!=expected:raise SpecError('indexed knowledge source changed: '+path)
    return dict(format_version=1,collection=doc['id'],source_root=doc['source_root'],entries=rows,
                external_index=dict(path=(library/'generated/knowledge.json').relative_to(root).as_posix(),
                                    records=len(knowledge['records']),source_counts={k:sum(r['source_type']==k for r in knowledge['records']) for k in sorted({r['source_type'] for r in knowledge['records']})}),
                scope='Local supplied sources only. Historical results are not current-machine qualification.')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for action in ('index','verify'):
        p=sub.add_parser(action);p.add_argument('collection',choices=['metax'])
        if action=='index':p.add_argument('--out',type=Path)
    search=sub.add_parser('search');search.add_argument('collection',choices=['metax']);search.add_argument('terms',nargs='*')
    search.add_argument('--source',choices=['all','pdf','practice','github','ecosystem'],default='all')
    for flag in ('component','doc','snapshot'):search.add_argument('--'+flag)
    search.add_argument('--page',type=int);search.add_argument('--limit',type=int,default=5)
    search.add_argument('--json',action='store_true');search.add_argument('--full',action='store_true')
    a=parser.parse_args(argv)
    try:
        doc,base=collection(ROOT,a.collection)
        if a.command=='search':
            command=[sys.executable,'-B','-X','utf8',str(base/'catalog/library/metax/hwdoc/tools/search.py'),*a.terms,'--source',a.source,'--limit',str(a.limit)]
            for flag in ('component','doc','snapshot','page'):
                if getattr(a,flag) is not None:command+=['--'+flag,str(getattr(a,flag))]
            for flag in ('json','full'):
                if getattr(a,flag):command+=['--'+flag]
            # Existing source engine verifies its own PDF/practice/snapshot hashes.
            return subprocess.run(command,cwd=base,check=False).returncode
        result=build(ROOT,a.collection)
        if a.command=='index' and a.out:write(a.out,result)
        print(json.dumps(result if a.command=='index' else dict(status='verified',entries=len(result['entries']),external_index=result['external_index'],intake=verify_intake(ROOT)),ensure_ascii=False,indent=2))
        return 0
    except (SpecError,OSError,ValueError,KeyError) as exc:
        print('catalog: '+str(exc),file=sys.stderr);return 2
