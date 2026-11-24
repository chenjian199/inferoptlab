"""Attach to vLLM; verify its JSON server_info without assuming SGLang fields."""
from urllib.error import URLError

from tools.specs import SpecError
from . import sglang

Deployment = sglang.Deployment  # External attachment does not start or stop the server.


def configuration_issues(deployment, runtime):
    issues = sglang.configuration_issues(deployment, runtime)
    if deployment['serving']['management'] != 'external':
        issues.append('vLLM currently requires an independently started external service')
    return issues


def inspect_server(serving):
    try:
        raw = sglang.get_json(serving['url'].rstrip('/')+'/server_info?config_format=json', timeout=45)
        # Do not archive arbitrary server environment variables from a development endpoint.
        return {'vllm_config': raw.get('vllm_config')}, []
    except (OSError, ValueError, URLError) as exc:
        return None, ['vLLM server configuration unavailable: '+str(exc)]


def verify_server(deployment, info, maximum_context):
    config = (info or {}).get('vllm_config')
    if not isinstance(config, dict):
        return ['cannot verify vLLM parallelism/cache/streaming configuration']
    p, cache = config.get('parallel_config', {}), config.get('cache_config', {})
    scheduler, model = config.get('scheduler_config', {}), config.get('model_config', {})
    expected = {'tensor_parallel_size': deployment['parallelism']['tp'],
                'pipeline_parallel_size': deployment['parallelism']['pp'],
                'data_parallel_size': deployment['parallelism']['dp']}
    issues = []
    for name, value in expected.items():
        if p.get(name) != value:
            issues.append(f'vLLM {name}: expected {value}, observed {p.get(name)}')
    if deployment['parallelism']['ep'] != 1 or p.get('enable_expert_parallel') is not False:
        issues.append('vLLM expert-parallel rank mapping is not verified by this adapter')
    if cache.get('enable_prefix_caching') is not False:
        issues.append('vLLM prefix cache is not confirmed disabled')
    if scheduler.get('stream_interval') != 1:
        issues.append('vLLM single-token stream interval is not confirmed')
    for group, key, expected_value in [(cache, 'block_size', deployment['scheduling']['kv_page_tokens']),
                                      (scheduler, 'max_num_seqs', deployment['scheduling']['max_running_requests'])]:
        if expected_value is not None and group.get(key) != expected_value:
            issues.append(f'vLLM {key} differs from deployment')
    if deployment['scheduling']['chunked_prefill_tokens'] is not None:
        issues.append('vLLM token scheduling budget is not equivalent to SGLang chunked_prefill_tokens')
    context = model.get('max_model_len')
    if context is None:
        issues.append('vLLM context limit unavailable')
    elif context < maximum_context:
        raise SpecError(f'vLLM max_model_len={context} is below required {maximum_context}')
    return issues
