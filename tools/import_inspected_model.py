"""Convert archived config/tokenizer/shard-header observations to model recipes.

Supported inspected families: Qwen3 dense and GLM5 text/hybrid MoE. Unknown fields
stay in hashed source evidence; no pickle/Python-tagged quantization YAML is loaded.
"""
import argparse
import hashlib
from pathlib import Path
import re
import shutil

import yaml

from tools.specs import Catalog, ROOT, SpecError, digest, read
from tools.hardware.export import meta, ref


def model_recipe_path(root, family, model, identity):
    """Use explicit catalogue groups; never infer a base model from quantization tags."""
    for name, value in [('family', family), ('model', model), ('id', identity)]:
        if not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', value):
            raise SpecError(f'{name} must be a lowercase slug containing letters, digits, dots or hyphens')
    return root/'recipes'/'models'/family/model/(identity+'.yaml')


def convert(raw, identity, source):
    files, weights = raw['files'], raw['weights']
    config = files['config.json']['content']
    text = config.get('text_config', config)
    if text['model_type'] not in {'qwen3', 'glm5_next_text', 'glm_moe_dsa'}:
        raise SpecError('unsupported inspected model_type: '+text['model_type'])
    if raw['errors']:
        raise SpecError('checkpoint inspection errors: '+str(raw['errors']))
    moe = 'n_routed_experts' in text
    doc = meta('ModelSpec', identity, source['version'], Path(raw['path']).name+' inspected checkpoint', source)
    doc['evidence_level'] = 'inspected'
    doc['issues'] = [dict(code=code, path=path, status='unverified', blocking=True, reason=reason) for code,path,reason in [
        ('payload-not-hashed','/identity/weights_sha256','Only metadata and every shard header were verified; weight payload bytes were not hashed.'),
        ('upstream-revision-unavailable','/identity/revision','No immutable upstream revision was established from this directory.'),
        ('quality-policy-missing','/semantics','No model-quality acceptance policy has been attached.')]]
    doc['identity'] = dict(name=Path(raw['path']).name, family='GLM' if moe else 'Qwen3', variant=None,
                           repository=None, revision=None, weights_sha256=None)
    template = files.get('chat_template.jinja', {}).get('sha256')
    if template is None:
        value = files['tokenizer_config.json']['content'].get('chat_template')
        if isinstance(value, str):
            template = hashlib.sha256(value.encode()).hexdigest()
    doc['tokenizer'] = dict(revision=None, sha256=files['tokenizer.json']['sha256'], chat_template_sha256=template)
    doc['semantics'] = dict(contract='unspecified',correctness_policy_ref=None,quality_policy_ref=None)
    attention_fields = read(ROOT/'schemas/definitions/inspected.json')['$defs']['attention']['properties']
    arch = dict(type='moe' if moe else 'dense', attention='hybrid' if 'linear_attn_config' in text else 'sparse_mla' if moe else 'gqa',
                context_limit_tokens=text['max_position_embeddings'], parameters={},
                state_types=['kv_cache'] if not moe else ['compressed_kv','indexer_state'],
                text={k:text[k] for k in ('num_hidden_layers','hidden_size','vocab_size','num_attention_heads','num_key_value_heads','max_position_embeddings','model_type')},
                moe=None, attention_config={k:v for k,v in text.items() if k in attention_fields and v is not None},
                mtp_layers=text.get('num_nextn_predict_layers',0), modalities=['text'], implementation=config['architectures'])
    arch['text']['layer_types'] = text.get('layer_types', [])
    if moe:
        arch['moe'] = dict(routed_experts=text['n_routed_experts'], shared_experts=text['n_shared_experts'],
            experts_per_token=text['num_experts_per_tok'], intermediate_size=text['moe_intermediate_size'],
            first_dense_layers=text['first_k_dense_replace'], router_dtype=text.get('moe_router_dtype'), scoring_function=text.get('scoring_func'))
    if 'linear_attn_config' in text:
        linear=text['linear_attn_config']
        arch['linear_attention']=dict(num_heads=linear['num_heads'],head_dim=linear['head_dim'],conv_kernel_size=linear['short_conv_kernel_size'],layers=linear['kda_layers'])
        arch['state_types'].append('linear_attention_state')
    if 'vision_config' in config:
        v=config['vision_config'];arch['modalities']+=['image','video']
        arch['vision']=dict(model_type=v['model_type'],hidden_size=v['hidden_size'],num_hidden_layers=v['depth'],num_attention_heads=v['num_heads'],patch_size=v['patch_size'])
    if 'hc_mult' in text:
        arch['hyper_connections']=dict(multiplier=text['hc_mult'],sinkhorn_iterations=text['hc_sinkhorn_iters'],epsilon=float(text['hc_eps']))
    doc['architecture']=arch
    compression=config.get('compression_config')
    quant=None
    if compression:
        groups=compression['config_groups']; group=next(iter(groups.values()))
        weight=group['weights']; act=group['input_activations']
        bits=sorted({g['weights']['num_bits'] for g in groups.values()})
        quant=dict(format=compression['format'],method=compression.get('quant_method','compressed-tensors'),
            weight_bits=min(bits),activation_bits=act['num_bits'],activation_dynamic=act['dynamic'],
            weight_strategy=weight['strategy'],activation_strategy=act['strategy'],symmetric=weight['symmetric'],
            scale_dtypes=weights['scale_tensor_dtypes'],excluded_modules=compression.get('ignore',[]),description_file='config.json')
        doc['extensions']['model.quantization_groups']=groups
        if len(bits)>1:
            doc['issues'].append(dict(code='mixed-weight-bits',path='/precision/quantization/weight_bits',status='ambiguous',blocking=False,
                reason='weight_bits is the minimum group precision; exact Linear/MoE bit widths are in extensions.model.quantization_groups.'))
    doc['precision']=dict(label=Path(raw['path']).name.split('-')[-1] if quant else text.get('torch_dtype',text.get('dtype')),
        weights=' + '.join(weights['dtype_summary']),activations='dynamic INT8 on configured groups' if quant else text.get('torch_dtype',text.get('dtype')),
        kv_cache=None,quantization=quant)
    index=weights['index_file']
    doc['checkpoint']=dict(host=raw['ssh_host'],path=raw['path'],captured_at=raw['captured_at'],format='safetensors',
        config_sha256=files['config.json']['sha256'],index=dict(name=index,size_bytes=files[index]['size_bytes'],sha256=files[index]['sha256']) if index else None,
        shard_count=len(weights['shards']),total_file_bytes=sum(s['size_bytes'] for s in weights['shards']),
        tensor_count=sum(s['tensor_count'] for s in weights['dtype_summary'].values()),
        storage_dtypes=[dict(dtype=k,**v) for k,v in weights['dtype_summary'].items()],manifest_sha256=digest(weights['shards']),
        manifest_algorithm='sha256_canonical_json_shard_name_size_header_sha256',verification_scope='index_and_headers',
        index_matches_headers=weights['index_matches_headers'] if index else None,duplicate_tensor_names=[],payload_verified=False,
        auxiliary_files=[],compatibility=dict(target_vendor='MetaX',status='unverified',reason='Checkpoint inspected; loading and numerical correctness are separate tests.'))
    return doc


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('observation',type=Path); parser.add_argument('--id',required=True); parser.add_argument('--version',default='1.0.0')
    parser.add_argument('--family', required=True, help='Catalogue family directory, e.g. glm or qwen')
    parser.add_argument('--model', required=True, help='Base model directory, e.g. glm-5.3-flash; omit quantization/host tags')
    args=parser.parse_args()
    model_path=model_recipe_path(ROOT,args.family,args.model,args.id)
    evidence=ROOT/'experiments/evidence/model-intake'/args.id/args.version/'metadata.json'
    source=meta('SourceDocument','source-'+args.id,args.version,args.id+' machine-collected model metadata')
    source.update(path=evidence.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(args.observation.read_bytes()).hexdigest(),
        media_type='application/json',role='model_metadata',authority='machine_collected',
        coverage=dict(status='partial',description='Config, tokenizer and all shard headers; no full payload hashing or model execution.'))
    raw=read(args.observation); model=convert(raw,args.id,source)
    catalog=Catalog();catalog.load()
    paths=[]
    for group,doc in [('sources',source),('models',model)]:
        path=model_path if group=='models' else ROOT/'recipes'/group/(doc['id']+'.yaml')
        if (doc['id'],doc['version']) in catalog.documents or path.exists() or evidence.exists():
            raise SpecError('recipe/evidence already exists')
        catalog.documents[(doc['id'],doc['version'])]=doc;paths.append(path)
    for doc in (source,model):
        errors=catalog.structural_errors(doc) or catalog.semantic_errors(doc)
        if errors:raise SpecError('\n'.join(errors))
    probe=args.observation.with_suffix('.probe.py')
    if hashlib.sha256(probe.read_bytes()).hexdigest()!=raw['probe_sha256']:
        raise SpecError('archived probe hash differs from observation')
    evidence.parent.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(args.observation,evidence);shutil.copyfile(probe,evidence.with_suffix('.probe.py'))
    for doc,path in zip((source,model),paths):
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8',newline='\n') as f:yaml.safe_dump(doc,f,sort_keys=False,allow_unicode=True)
    print(paths[-1])


if __name__=='__main__':
    main()
