"""Same-prefix one-step replay with rank-0 layer and full processed-logit capture."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import time

ROOT = Path('/experiment')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', choices=['d1','d2'], default='d1')
    args = parser.parse_args()
    plan = json.loads((ROOT/'configs/plan.json').read_text())
    probes = json.loads((ROOT/'data/divergence_probes.json').read_text())
    folder = ROOT/'evidence'/('diagnostics_'+args.label)
    folder.mkdir(exist_ok=False)
    from vllm import LLM, SamplingParams
    settings = dict(plan['settings'], worker_extension_cls='diagnostic_worker.Diagnostic', enable_trace_replay=True)
    llm = LLM(**settings)
    (folder/'environment.json').write_text(json.dumps({'pid':os.getpid(),'settings':settings,
        'workers':llm.collective_rpc('deployment_provenance'),
        'scope':'Diagnostic only: same logical prefix via prefill and forced cached decode; capture pre-override greedy decision on rank 0. Cached trace appends a terminal placeholder (0) because input_processor caps generation to trace length; its returned final token is not a model decision. Trace replay and hooks differ from historical execution.'},indent=2))
    with (folder/'probes.jsonl').open('x') as stream:
        for repeat in range(3):
            for mode in ['prefill','cached']:
                for probe in probes:
                    index=probe['first_divergence_index']
                    forced=probe['input_token_ids'][-index:] if index else []
                    tokens=probe['input_token_ids'][:-index] if mode=='cached' and index else probe['input_token_ids']
                    target=index if mode=='cached' else 0
                    params=SamplingParams(**dict(plan['sampling'],max_tokens=target+1,logprobs=5),
                        trace_decode_token_ids=forced+[0] if mode=='cached' else None)
                    label=args.label+'_'+mode+'_r'+str(repeat)+'_he'+probe['task_id'].split('/')[1]
                    activated=llm.collective_rpc('begin_probe',args=(label,target))
                    response=llm.generate([{'prompt_token_ids':tokens}],params,use_tqdm=False)[0]
                    assert list(response.prompt_token_ids)==tokens
                    result=response.outputs[0]
                    trace=llm.collective_rpc('end_probe')
                    assert len(result.token_ids)==target+1
                    if mode=='cached':
                        assert list(result.token_ids[:index])==forced
                        assert result.token_ids[-1]==0
                    row={'label':label,'task_id':probe['task_id'],'repeat':repeat,'mode':mode,
                        'historical_first_divergence':index,
                        'logical_prefix_sha256':hashlib.sha256(json.dumps(probe['input_token_ids']).encode()).hexdigest(),
                        'input_sha256':hashlib.sha256(json.dumps(tokens).encode()).hexdigest(),
                        'tokens':list(result.token_ids),'text':result.text,'activated':activated,'trace':trace,
                        'returned_final_is_placeholder':mode=='cached',
                        'decision_source':'diagnostic tensor sampling[0] before trace override',
                        'target_logprobs':{str(k):{'logprob':v.logprob,'rank':v.rank,'decoded_token':v.decoded_token}
                                          for k,v in result.logprobs[-1].items()}}
                    stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
                    print(json.dumps({'label':label,'last_token':result.token_ids[-1]}),flush=True)
    (folder/'complete.json').write_text(json.dumps({'status':'complete','probes':len(probes)*3*2,'completed_epoch':time.time()}))


if __name__ == '__main__':
    main()
