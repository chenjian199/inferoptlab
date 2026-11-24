"""Eight-GPU real-weight text generation; run only after environment checks."""
import json
import os
import time
from pathlib import Path

os.environ.setdefault('USE_PRECOMPILED_KERNEL', '1')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')

def main():
    import vllm
    import vllm_metax
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams

    model = '/models/GLM-5.3-Flash-W8A8'
    tok = AutoTokenizer.from_pretrained(model, local_files_only=True)
    filler = tok.decode(tok.encode('这是测试用的工作记录，所有事项均按计划执行。\n' * 240,
                                   add_special_tokens=False)[:2400])
    cases = ['请用中文简短介绍你自己。', '只回答最终结果：1+1等于多少？',
             '本次验证的识别词是“青松”。\n' + filler + '\n请只输出本次验证的识别词。']
    prompts = [tok.apply_chat_template(
        [{'role': 'user', 'content': text}], tokenize=False,
        add_generation_prompt=True, reasoning_effort='low') for text in cases]
    prompt_lengths = [len(tok.encode(prompt, add_special_tokens=False)) for prompt in prompts]
    assert 2048 < prompt_lengths[-1] <= 3072, prompt_lengths
    settings = dict(model=model, tensor_parallel_size=8,
                    distributed_executor_backend='mp', dtype='bfloat16',
                    quantization='compressed-tensors', load_format='safetensors',
                    max_model_len=4096, max_num_seqs=int(os.environ.get('GLM53_MAX_SEQS', '2')),
                    max_num_batched_tokens=4096, gpu_memory_utilization=0.9,
                    enforce_eager=True, enable_prefix_caching=False,
                    attention_config={'indexer_kv_dtype': 'auto'},
                    limit_mm_per_prompt={'image': 0, 'video': 0},
                    trust_remote_code=False,
                    worker_extension_cls='worker_provenance.Provenance')
    if os.environ.get('GLM53_SYNC_SCHEDULING') == '1':
        settings['async_scheduling'] = False
    started = time.monotonic()
    llm = LLM(**settings)
    loaded = time.monotonic()
    preflight = llm.collective_rpc('deployment_provenance')
    assert len(preflight) == 8
    assert all(len(w['mla_int8_scales']) == 33 and
               all(s['finite_positive'] for s in w['mla_int8_scales'])
               for w in preflight), 'MLA INT8 scale loading failed'
    sampling = dict(temperature=1.0, top_p=0.95, seed=0, max_tokens=1024)
    outputs = llm.generate(prompts, SamplingParams(**sampling))
    workers = llm.collective_rpc('deployment_provenance')
    assert len(workers) == 8, len(workers)
    assert all(w['parameter_dtype_numel'].get('torch.int8', 0) > 0 for w in workers), workers
    assert all(w['vllm_file'].startswith('/work/src/vllm/') and
               w['plugin_file'].startswith('/work/src/vllm-metax/') for w in workers), workers
    report = {'settings': settings, 'sampling': sampling, 'vllm_file': vllm.__file__,
              'runner_override': os.environ.get('VLLM_USE_V2_MODEL_RUNNER'),
              'plugin_file': vllm_metax.__file__,
              'load_seconds': loaded-started,
              'generate_seconds': time.monotonic()-loaded,
              'workers': workers, 'cases': []}
    for query, result, prompt_length in zip(cases, outputs, prompt_lengths, strict=True):
        out = result.outputs[0]
        assert out.token_ids and out.text.strip(), 'Empty generation'
        report['cases'].append({'query': query, 'text': out.text,
                                'prompt_tokens': prompt_length,
                                'tokens': len(out.token_ids),
                                'finish_reason': out.finish_reason})
    answers = [case['text'].split('</think>')[-1].strip() for case in report['cases']]
    report['answer_checks'] = {
        'all_finished': all(case['finish_reason'] == 'stop' for case in report['cases']),
        'arithmetic': answers[1].strip('*`。.!！ \n') == '2',
        'long_context_needle': '青松' in answers[2],
    }
    report['passed'] = all(report['answer_checks'].values())
    target = Path('/work/evidence/inference_smoke.json')
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
    assert report['passed'], report['answer_checks']

if __name__ == '__main__':
    main()
