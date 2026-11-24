"""Benchmark and serving adapters."""
def for_runtime(runtime):
    from tools.specs import SpecError
    from . import sglang, vllm
    if runtime['engine'] == 'sglang':
        return sglang
    if runtime['engine'] in {'vllm', 'vllm-metax'}:
        return vllm
    raise SpecError('unsupported serving engine: '+runtime['engine'])
