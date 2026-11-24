import hashlib,json,os,time
from pathlib import Path

ROOT=Path('/experiment')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')


def main():
    from vllm import LLM,SamplingParams
    config=json.loads((ROOT/'configs/model-plan.json').read_text())
    prompts=json.loads((ROOT/'data/prompt_manifest.json').read_text())['inputs']
    settings=config['settings'];llm=LLM(**settings)
    info=llm.collective_rpc('target_info')
    save(ROOT/'evidence/model_environment.json',{'pid':os.getpid(),'settings':settings,'targets':info,'workers':llm.collective_rpc('deployment_provenance')})
    outputs={}
    for phase in ['baseline32','candidate32','rollback4']:
        if phase=='candidate32':save(ROOT/'evidence/install.json',llm.collective_rpc('install_gemm'))
        if phase=='rollback4':
            stats=llm.collective_rpc('gemm_stats');save(ROOT/'evidence/replacement_stats.json',stats)
            assert all(s['replaced']>0 and s['fallback']==0 and len(s['reference_checks'])==2 for s in stats),stats
            save(ROOT/'evidence/rollback.json',llm.collective_rpc('restore_gemm'))
        ids=config['task_ids'][:4] if phase=='rollback4' else config['task_ids']
        folder=ROOT/'runs'/phase;folder.mkdir(exist_ok=False);os.chown(folder,1000,1000)
        params=SamplingParams(**config['sampling'])
        manifest={'status':'running','task_ids':ids,'completed_tasks':0,'settings':settings,'sampling':config['sampling'],
            'prompt_manifest_sha256':sha(ROOT/'data/prompt_manifest.json'),'plan_sha256':sha(ROOT/'configs/model-plan.json'),
            'harness_sha256':sha(Path(__file__)),'scope':'Single-process one-layer replacement pilot; not full164 release validation.'}
        save(folder/'generation_manifest.json',manifest);outmap={}
        with (folder/'generations.jsonl').open('x') as stream:
            for index,tid in enumerate(ids):
                tokens=prompts[tid]['token_ids'];start=time.monotonic()
                result=llm.generate([{'prompt_token_ids':tokens}],params,use_tqdm=False)[0]
                assert list(result.prompt_token_ids)==tokens
                out=result.outputs[0]
                row={'task_id':tid,'text':out.text,'output_token_ids':list(out.token_ids),'prompt_tokens':len(tokens),
                    'output_tokens':len(out.token_ids),'finish_reason':out.finish_reason,'stop_reason':out.stop_reason,'generation_seconds':time.monotonic()-start}
                stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush();outmap[tid]=row['output_token_ids']
                manifest['completed_tasks']=index+1;save(folder/'generation_manifest.json',manifest)
                print(json.dumps({'phase':phase,'completed':index+1,'task_id':tid,'tokens':len(out.token_ids)}),flush=True)
        manifest.update(status='complete',generations_sha256=sha(folder/'generations.jsonl'));save(folder/'generation_manifest.json',manifest);outputs[phase]=outmap
    summary={'status':'complete','candidate_token_exact':sum(v==outputs['baseline32'][k] for k,v in outputs['candidate32'].items()),
        'candidate_tasks':32,'rollback_token_exact':sum(v==outputs['baseline32'][k] for k,v in outputs['rollback4'].items()),
        'rollback_tasks':4,'targets':info,'final_workers':llm.collective_rpc('deployment_provenance')}
    save(ROOT/'evidence/model_result.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['targets','final_workers']}))


if __name__=='__main__':main()
