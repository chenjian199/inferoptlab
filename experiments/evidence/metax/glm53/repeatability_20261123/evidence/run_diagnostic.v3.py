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
    settings = dict(plan['settings'], worker_extension_cls='diagnostic_worker.Diagnostic')
    llm = LLM(**settings)
    (folder/'environment.json').write_text(json.dumps({'pid':os.getpid(),'settings':settings,
        'workers':llm.collective_rpc('deployment_provenance'),
        'scope':'Diagnostic only: same prefix via prefill, one next token, synchronous layer/logit capture on rank 0. Not equivalent to historical cached decode path.'},indent=2))
    params = SamplingParams(**dict(plan['sampling'], max_tokens=1, logprobs=5))
    with (folder/'probes.jsonl').open('x') as stream:
        for repeat in range(3):
            for probe in probes:
                label = args.label+'_r'+str(repeat)+'_he'+probe['task_id'].split('/')[1]
                activated = llm.collective_rpc('begin_probe', args=(label,))
                result = llm.generate([{'prompt_token_ids':probe['input_token_ids']}],params,use_tqdm=False)[0].outputs[0]
                trace = llm.collective_rpc('end_probe')
                row = {'label':label,'task_id':probe['task_id'],'repeat':repeat,
                    'historical_first_divergence':probe['first_divergence_index'],
                    'input_sha256':hashlib.sha256(json.dumps(probe['input_token_ids']).encode()).hexdigest(),
                    'tokens':list(result.token_ids),'text':result.text,'activated':activated,'trace':trace,
                    'logprobs':[{str(k):{'logprob':v.logprob,'rank':v.rank,'decoded_token':v.decoded_token}
                                 for k,v in step.items()} for step in result.logprobs]}
                stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush()
                print(json.dumps({'label':label,'tokens':list(result.token_ids)}),flush=True)
    (folder/'complete.json').write_text(json.dumps({'status':'complete','probes':len(probes)*3,'completed_epoch':time.time()}))


if __name__ == '__main__':
    main()
