import copy
import json
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
header=json.loads((ROOT/'schemas/definitions/benchmark.json').read_text(encoding='utf-8'))
properties={k:copy.deepcopy(header['properties'][k]) for k in ['schema_version','kind','id','version','title','provenance','issues','extensions','deployment_refs']}
properties['kind']={'const':'CachedDecodePlan'}
properties.update(workload_refs={'type':'array','minItems':1,'uniqueItems':True,'items':{'$ref':'https://inferoptlab.local/schemas/0.2.0/common.json#/$defs/reference'}},
    context_policy={'const':'independent_per_concurrent_slot'}, cache_policy={'const':'full_original_context_plus_one_seed'},
    request_multiplier={'type':'integer','minimum':1}, repetitions={'type':'integer','minimum':1},seed={'type':'integer','minimum':0},
    request_timeout_s={'type':'number','exclusiveMinimum':0},point_timeout_s={'type':'number','exclusiveMinimum':0})
schema={'$schema':header['$schema'],'$id':'https://inferoptlab.local/schemas/0.2.0/cached-decode.json',
    'title':'Cached Decode continuation plan','type':'object','properties':properties,'required':list(properties),'additionalProperties':False}
(ROOT/'schemas/definitions/cached-decode.json').write_text(json.dumps(schema,indent=2)+'\n',encoding='utf-8')
runtime=yaml.safe_load((ROOT/'recipes/runtimes/metax60-vllm-glm53-source.yaml').read_text(encoding='utf-8'))
runtime.update(id='metax60-vllm-glm53-cached-decode',title='GLM Flash cached Decode with supported sparse MLA prefill')
attention=json.loads(runtime['launch_parameters']['--attention-config'])
attention['sparse_mla_force_mqa']=True
runtime['launch_parameters']['--attention-config']=json.dumps(attention,separators=(',',':'))
runtime['extensions']['cache.prefill_backend']='Force supported Sparse MLA MQA path. Native MHA context gather only supports cache head dimensions 320/576; this GLM checkpoint uses 512. Decode kernels and the image digest are unchanged.'
(ROOT/'recipes/runtimes/metax60-vllm-glm53-cached-decode.yaml').write_text(yaml.safe_dump(runtime,sort_keys=False),encoding='utf-8')
deps=[]
for layout in ['tp1-dp8-ep8','tp8-ep8']:
    d=yaml.safe_load((ROOT/f'recipes/deployments/glm53-flash/c500/vllm/decode/{layout}.yaml').read_text(encoding='utf-8'))
    d.update(id='glm53-vllm-cached-decode-'+layout,title='GLM Flash full-context cached Decode '+layout,prefix_cache=True,
        extensions={'measurement.scope':'L cached context tokens plus one uncached P-produced seed. No P-to-D transfer is measured.'})
    d['backend_options'].update({'--mamba-block-size':256,'--prefix-match-unit':16})
    d['runtime_ref']={'id':runtime['id'],'version':runtime['version']}
    if layout=='tp1-dp8-ep8':
        d['scheduling']['max_num_batched_tokens']=1024
        d['extensions']['startup.workspace']='4096-token startup profiling OOMs in MLA temporary workspace; use 1024. Scored Decode has at most 16 one-token queries per DP rank.'
    path=ROOT/f'recipes/deployments/glm53-flash/c500/vllm/cached-decode/{layout}.yaml'
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(yaml.safe_dump(d,sort_keys=False),encoding='utf-8')
    deps.append(dict(id=d['id'],version=d['version']))
workloads=[]
for label in ['4k','16k','64k']:
    for output in [20,50]:
        w=yaml.safe_load((ROOT/f'recipes/workloads/glm53-vllm/decode/{label}-{output}.yaml').read_text(encoding='utf-8'))
        w.update(id=f'glm53-vllm-cached-decode-{label}-{output}-workload',title=f'GLM Flash cached context {label}, {output} new Decode tokens')
        w['requests'].pop('request_set_sha256_by_concurrency',None)
        w['cache'].update(prefix_reuse='enabled',target_hit_ratio=1,preparation='seed_then_fill_boundary_per_sticky_slot',reset_between_runs=False)
        w['extensions']={'dataset.reuse':'Independent contexts across concurrent slots; each slot replays its context for four sequential requests. Frozen token IDs replace old chat fixture hashes.',
            'cache.ratio':'target_hit_ratio applies to the original L-token context. Wire prompt is L+1 including a P-produced seed.',
            'cache.lifecycle':'Reset before each length/concurrency group; retain the validated contexts across that group repetitions and output lengths. Validate every scored request.'}
        path=ROOT/f'recipes/workloads/glm53-vllm/cached-decode/{label}-{output}.yaml'
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(yaml.safe_dump(w,sort_keys=False),encoding='utf-8')
        workloads.append(dict(id=w['id'],version=w['version']))
plan=dict(schema_version='0.2.0',kind='CachedDecodePlan',id='glm53-vllm-cached-decode-plan',version='1.0.0',
    title='GLM Flash TP8/EP8 and TP1/DP8/EP8 full-context cached Decode scan',provenance=[],issues=[],
    extensions={'measurement.limit':'No cache transfer cost is measured. Client latency includes queueing and streaming. Cold and cached generation are not bitwise deterministic; numerical accuracy acceptance is not established.'},
    deployment_refs=deps,workload_refs=workloads,context_policy='independent_per_concurrent_slot',
    cache_policy='full_original_context_plus_one_seed',request_multiplier=4,repetitions=3,seed=20261125,
    request_timeout_s=900,point_timeout_s=7200)
(ROOT/'recipes/plans/benchmark/glm53-vllm/cached-decode.yaml').write_text(yaml.safe_dump(plan,sort_keys=False),encoding='utf-8')
print('Prepared 2 deployments, 6 workloads, 1 plan, 1 schema')
