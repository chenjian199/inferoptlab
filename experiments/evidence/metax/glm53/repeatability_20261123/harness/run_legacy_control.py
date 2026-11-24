"""Offline TP8 generation from prompt-only data; explicit smoke-to-full gate."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

ROOT=Path('/experiment')


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path,data):
    temporary=path.with_suffix(path.suffix+'.partial')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    temporary.replace(path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--label',required=True)
    args=parser.parse_args()
    assert args.label.replace('_','').replace('-','').isalnum()
    config_path=ROOT/'configs/protocol-v1.json'
    config=json.loads(config_path.read_text())
    rows=[json.loads(line) for line in (ROOT/'data/prompts.jsonl').read_text().splitlines()]
    assert len(rows)==164 and all(set(r)=={'task_id','prompt'} for r in rows)
    selection=json.loads((ROOT/'data/selection.json').read_text())
    assert len(selection['smoke32'])==32 and len(selection['all'])==164
    import vllm,vllm_metax
    from transformers import AutoTokenizer
    from vllm import LLM,SamplingParams
    model='/models/GLM-5.3-Flash-W8A8'
    tok=AutoTokenizer.from_pretrained(model,local_files_only=True)
    inputs={}
    for row in rows:
        content=config['prompt_protocol']['instruction_draft']+'\n\n'+row['prompt']
        rendered=tok.apply_chat_template([{'role':'user','content':content}],tokenize=False,
                   add_generation_prompt=True,reasoning_effort=config['chat_template']['reasoning_effort'])
        ids=tok.encode(rendered,add_special_tokens=False)
        assert len(ids)+config['sampling']['max_tokens']<=4096, row['task_id']
        inputs[row['task_id']]=dict(prompt=rendered,token_ids=ids)
    save(ROOT/'evidence/prompt_manifest.json',dict(inputs=inputs,template_sha256=hashlib.sha256(tok.chat_template.encode()).hexdigest(),
        tokenizer_files={p.name:sha(p) for p in Path(model).iterdir() if p.is_file() and p.name in ['tokenizer.json','tokenizer_config.json','chat_template.jinja','special_tokens_map.json']},
        protocol_sha256=sha(config_path),prompts_sha256=sha(ROOT/'data/prompts.jsonl')))
    settings=dict(model=model,tensor_parallel_size=8,distributed_executor_backend='mp',dtype='bfloat16',
                  quantization='compressed-tensors',load_format='safetensors',max_model_len=4096,
                  max_num_seqs=1,max_num_batched_tokens=4096,gpu_memory_utilization=.9,
                  enforce_eager=True,enable_prefix_caching=False,async_scheduling=False,
                  attention_config={'indexer_kv_dtype':'auto'},limit_mm_per_prompt={'image':0,'video':0},
                  trust_remote_code=False,worker_extension_cls='worker_provenance.Provenance')
    started=time.monotonic()
    llm=LLM(**settings)
    provenance=llm.collective_rpc('deployment_provenance')
    assert len(provenance)==8
    assert all(w['use_v2_model_runner'] and len(w['mla_int8_scales'])==33 and
               all(s['finite_positive'] for s in w['mla_int8_scales']) and
               w['parameter_dtype_numel'].get('torch.int8',0)>0 and
               w['vllm_file'].startswith('/work/src/vllm/') and
               w['plugin_file'].startswith('/work/src/vllm-metax/') for w in provenance)
    save(ROOT/'evidence/generation_environment.json',dict(settings=settings,workers=provenance,
        vllm_file=vllm.__file__,plugin_file=vllm_metax.__file__,load_seconds=time.monotonic()-started))
    params=SamplingParams(**config['sampling'])
    for phase in ['smoke32']:
        if phase=='full164':
            gate=ROOT/'evidence'/('authorize_full_'+args.label+'.json')
            print('WAITING_FOR_FULL_GATE',flush=True)
            deadline=time.monotonic()+7200
            while not gate.exists():
                if time.monotonic()>deadline:raise TimeoutError('full phase gate not provided')
                time.sleep(3)
            authorization=json.loads(gate.read_text())
            assert authorization['protocol_sha256']==sha(config_path)
            assert authorization['smoke_scoring_complete'] and authorization['canonical_passed']==164
        run=ROOT/'runs'/(args.label+'_'+phase)
        run.mkdir(exist_ok=False)
        os.chown(run, 1000, 1000)
        ids=selection['smoke32'] if phase=='smoke32' else selection['all']
        manifest=dict(status='running',task_ids=ids,phase=phase,protocol_sha256=sha(config_path),
                      prompt_manifest_sha256=sha(ROOT/'evidence/prompt_manifest.json'),
                      harness_sha256=sha(Path(__file__)),settings=settings,sampling=config['sampling'],
                      same_engine_across_phases=True,expected_tasks=len(ids),completed_tasks=0)
        save(run/'generation_manifest.json',manifest)
        with (run/'generations.jsonl').open('x') as stream:
            for i,tid in enumerate(ids):
                before=time.monotonic()
                result=llm.generate([{'prompt_token_ids':inputs[tid]['token_ids']}],params,use_tqdm=False)[0]
                output=result.outputs[0]
                row=dict(task_id=tid,text=output.text,output_token_ids=list(output.token_ids),
                         prompt_tokens=len(inputs[tid]['token_ids']),output_tokens=len(output.token_ids),
                         finish_reason=output.finish_reason,stop_reason=output.stop_reason,
                         generation_seconds=time.monotonic()-before)
                stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
                manifest['completed_tasks']=i+1
                save(run/'generation_manifest.json',manifest)
                print(json.dumps({k:row[k] for k in ['task_id','prompt_tokens','output_tokens','finish_reason','generation_seconds']}),flush=True)
        manifest.update(status='complete',generations_sha256=sha(run/'generations.jsonl'))
        save(run/'generation_manifest.json',manifest)
        print('PHASE_COMPLETE '+phase,flush=True)
    save(ROOT/'evidence/final_worker_provenance.json',llm.collective_rpc('deployment_provenance'))


if __name__=='__main__':main()
