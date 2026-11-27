"""Independently recompute request counts and TPOT from copied native evidence."""
import gzip
import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',choices=['original','additional'],default='original')
options=parser.parse_args()
root=Path('experiments/evidence') / ('glm53-short-output-collected-20261125' if options.stage=='original' else 'glm53-additional-output-collected-20261125')
receipt=json.loads((root/'latest.json').read_text(encoding='utf-8'))
compressed=Path(receipt['path']).read_bytes()
assert hashlib.sha256(compressed).hexdigest()==receipt['sha256']
archive=json.loads(gzip.decompress(compressed))
assert archive.get('stage','original')==options.stage
verified=[]
for collection in [archive['files'],*[entry['files'] for entry in archive['runs']+archive.get('historical_runs',[])]]:
    for name,item in collection.items():
        assert hashlib.sha256(item['text'].encode('utf-8')).hexdigest()==item['sha256'],name

def percentile(values,q):
    ordered=sorted(values);pos=(len(ordered)-1)*q
    low=math.floor(pos);high=math.ceil(pos)
    return ordered[low]+(ordered[high]-ordered[low])*(pos-low)

for entry in archive['runs']:
    row=entry['ledger_entry']
    if row['status']!='completed':continue
    files=entry['files']
    record=json.loads(files['run.json']['text'])
    summary=json.loads(files['summary.json']['text'])
    decode=json.loads(files['decode.json']['text'])
    manifest=record['dataset_manifest']
    n=4*row['concurrency']
    assert record['status']=='completed' and not record['environment_issues']
    assert summary['validity']=='valid'
    assert summary['counts']==dict(planned=n,observed=n,succeeded=n,failed=0,missing=0)
    assert summary['raw_sha256']==files['raw/aiperf/profile_export.jsonl']['sha256']==decode['source_raw_sha256']
    assert decode['eligible_for_performance_comparison'] and not decode['strict_device_decode']
    assert manifest['input_tokens'] in {4096,16384,65536} and manifest['output_tokens'] in {20,50}
    native=[json.loads(line) for line in files['raw/aiperf/profile_export.jsonl']['text'].splitlines() if line.strip()]
    assert len(native)==n
    ids=[r['metadata']['conversation_id'] for r in native]
    assert len(set(ids))==n and set(ids)==set(manifest['files']['requests.jsonl']['session_ids'])
    tpot=[]
    for request in native:
        assert not request.get('error')
        m=request['metrics']
        assert m['input_sequence_length']==dict(value=manifest['input_tokens'],unit='tokens')
        assert m['output_sequence_length']==dict(value=manifest['output_tokens'],unit='tokens')
        assert m['request_latency']['unit']==m['time_to_first_token']['unit']=='ms'
        duration=m['request_latency']['value']-m['time_to_first_token']['value']
        assert duration>=0
        tpot.append(duration/(manifest['output_tokens']-1))
    expected=dict(count=n,mean=sum(tpot)/n,min=min(tpot),max=max(tpot),
                  **{name:percentile(tpot,q) for name,q in [('p50',.5),('p90',.9),('p95',.95),('p99',.99)]})
    for name,value in expected.items():
        assert math.isclose(decode['tpot_ms'][name],value,rel_tol=1e-9,abs_tol=1e-8),(row['directory'],name)
    args=json.loads(files['commands.json']['text'])['aiperf']
    assert int(args[args.index('--request-count')+1])==n
    assert int(args[args.index('--concurrency')+1])==row['concurrency']
    assert 'max_tokens:'+str(manifest['output_tokens']) in args and 'min_tokens:'+str(manifest['output_tokens']) in args
    warm=json.loads(files['warmup-summary.json']['text'])
    assert warm['validity']=='valid' and warm['counts']['succeeded']==max(4,row['concurrency'])
    verified.append(dict(run=row['directory'],requests=n,tpot_mean_ms=expected['mean']))

result=dict(verified_at=datetime.now(timezone.utc).isoformat(),captured_at=archive['captured_at'],
            stage=options.stage,scope='completed native requests in copied '+options.stage+' batch; not whole-campaign completion',
            archive_sha256=receipt['sha256'],completed=len(verified),requests=sum(r['requests'] for r in verified),
            checks=['archive/file/raw hashes','4*C counts and unique IDs','exact input/output lengths',
                    'native ms units and post-first-token TPOT mean/percentiles','client arguments','separate warmup'],runs=verified)
(root/'local-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='runs'}))
