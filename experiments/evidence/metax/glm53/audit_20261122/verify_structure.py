"""Validate checkpoint index/header consistency without allocating model tensors."""
import collections
import json
import math
import struct
from pathlib import Path

root=Path('/models/GLM_Series/GLM-5.3-Flash-W8A8')
out=Path('/workspace/audit_20261122')
index=json.loads((root/'model.safetensors.index.json').read_text())
mapping=index['weight_map']
errors=[]
counts=collections.Counter()
sizes=collections.Counter()
actual={}
for filename in sorted(set(mapping.values())):
    p=root/filename
    if not p.exists():
        errors.append('missing '+filename)
        continue
    with p.open('rb') as f:
        length=struct.unpack('<Q',f.read(8))[0]
        if length>100_000_000:raise ValueError('Oversize header')
        header=json.loads(f.read(length))
    data_size=p.stat().st_size-8-length
    intervals=[]
    for key,meta in header.items():
        if key=='__metadata__':continue
        start,end=meta['data_offsets']
        if not 0<=start<=end<=data_size:errors.append('invalid offset '+key)
        width={'F32':4,'BF16':2,'I8':1}.get(meta['dtype'])
        if width is None:errors.append('unchecked dtype '+meta['dtype'])
        elif math.prod(meta['shape'])*width != end-start:errors.append('shape byte count mismatch '+key)
        intervals.append((start,end))
        if key in actual:errors.append('duplicate key '+key)
        actual[key]=filename
        counts[meta['dtype']]+=1
        sizes[meta['dtype']]+=end-start
        if mapping.get(key)!=filename:errors.append('index mismatch '+key)
    cursor=0
    for a,b in sorted(intervals):
        if a!=cursor:errors.append('gap/overlap '+filename)
        cursor=b
    if cursor!=data_size:errors.append('unused payload '+filename)
for key in mapping:
    if key not in actual:errors.append('missing tensor '+key)
metadata=index.get('metadata',{})
tensor_errors=list(errors)
if metadata.get('total_size') is not None and metadata['total_size']!=sum(sizes.values()):
    errors.append('index total_size mismatch')
config=json.loads((root/'config.json').read_text())
quant=[]
def walk(d,path=''):
    if isinstance(d,dict):
        if 'quant_method' in d:quant.append({'path':path,'method':d['quant_method'],'format':d.get('format'),'config_groups':d.get('config_groups'),'ignored_count':len(d.get('ignore',[]))})
        for k,v in d.items():walk(v,path+'/'+k)
walk(config)
report={'complete':not errors,'tensor_data_and_mapping_valid':not tensor_errors,'errors':errors,'shards':len(set(mapping.values())),'indexed_tensors':len(mapping),'actual_tensors':len(actual),'tensor_counts_by_dtype':dict(counts),'tensor_bytes_by_dtype':dict(sizes),'computed_total_tensor_bytes':sum(sizes.values()),'index_metadata':metadata,'quantization':quant,'architecture':config.get('architectures'),'original_checkpoint_modified':False}
(out/'structure_verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
raise SystemExit(bool(errors))
