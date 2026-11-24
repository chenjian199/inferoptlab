"""Fresh-process, prompt-token-fixed repeats; no mutation of baseline assets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

ROOT = Path('/experiment')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    temporary = path.with_suffix(path.suffix + '.partial')
    temporary.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--process', choices=['a', 'b', 'c'], required=True)
    args = parser.parse_args()
    plan = json.loads((ROOT/'configs/plan.json').read_text())
    prompts = json.loads((ROOT/'data/prompt_manifest.json').read_text())['inputs']
    settings = plan['settings']
    evidence = ROOT/'evidence'/('process_' + args.process)
    evidence.mkdir(exist_ok=False)
    from vllm import LLM, SamplingParams
    started = time.monotonic()
    llm = LLM(**settings)
    workers = llm.collective_rpc('deployment_provenance')
    assert len(workers) == 8 and all(w['use_v2_model_runner'] for w in workers)
    base_params = SamplingParams(**plan['sampling'])
    assert base_params.temperature == 0 and base_params.sampling_type.name == 'GREEDY'
    save(evidence/'environment.json', dict(pid=os.getpid(), workers=workers,
        load_seconds=time.monotonic()-started, sampling_repr=repr(base_params),
        sampling_type=base_params.sampling_type.name,
        default_sampling_repr=repr(llm.get_default_sampling_params()),
        plan_sha256=sha(ROOT/'configs/plan.json'), script_sha256=sha(Path(__file__))))
    for phase in plan['processes'][args.process]:
        name = 'process_' + args.process + '_' + phase['name']
        folder = ROOT/'runs'/name
        folder.mkdir(exist_ok=False)
        os.chown(folder, 1000, 1000)
        params_dict = dict(plan['sampling'])
        if phase.get('logprobs'):
            params_dict['logprobs'] = 5
        params = SamplingParams(**params_dict)
        ids = phase['task_ids']
        manifest = dict(status='running', task_ids=ids, completed_tasks=0,
            expected_tasks=len(ids), process=args.process, phase=phase,
            sampling=params_dict, effective_sampling_repr=repr(params),
            settings=settings, prompt_manifest_sha256=sha(ROOT/'data/prompt_manifest.json'),
            plan_sha256=sha(ROOT/'configs/plan.json'), harness_sha256=sha(Path(__file__)))
        save(folder/'generation_manifest.json', manifest)
        with (folder/'generations.jsonl').open('x') as stream:
            for index, tid in enumerate(ids):
                tokens = prompts[tid]['token_ids']
                assert len(tokens)+params.max_tokens <= 4096
                before = time.monotonic()
                response = llm.generate([{'prompt_token_ids': tokens}], params, use_tqdm=False)[0]
                out = response.outputs[0]
                row = dict(task_id=tid, text=out.text, output_token_ids=list(out.token_ids),
                    prompt_tokens=len(tokens), output_tokens=len(out.token_ids),
                    finish_reason=out.finish_reason, stop_reason=out.stop_reason,
                    generation_seconds=time.monotonic()-before)
                if phase.get('logprobs'):
                    row['logprobs'] = [{str(k): dict(logprob=v.logprob, rank=v.rank,
                        decoded_token=v.decoded_token) for k,v in step.items()} for step in out.logprobs]
                stream.write(json.dumps(row, ensure_ascii=False)+'\n'); stream.flush()
                manifest['completed_tasks'] = index+1
                save(folder/'generation_manifest.json', manifest)
                print(json.dumps({'run':name,'completed':index+1,'task_id':tid,'tokens':len(out.token_ids)}), flush=True)
        manifest.update(status='complete', generations_sha256=sha(folder/'generations.jsonl'))
        save(folder/'generation_manifest.json', manifest)
    save(evidence/'final_workers.json', llm.collective_rpc('deployment_provenance'))
    print('PROCESS_COMPLETE '+args.process, flush=True)


if __name__ == '__main__':
    main()
