"""Opt-in observation of the pinned vLLM engine, without changing its decisions.

Loaded only when the deployment explicitly adds this directory to PYTHONPATH.
Scheduler records contain CPU counters; no GPU synchronization is introduced.
Attention metadata logging is enabled only by the qualification marker file.
"""
import importlib.abc
import importlib.machinery
import json
import os
from pathlib import Path
import sys
import time

ROOT = os.environ.get('INFEROPTLAB_DECODE_OBSERVATIONS')


def observe_capacity(module):
    """Capture each EngineCore pool, never the API's summed DP block count."""
    settings = os.environ.get('INFEROPTLAB_CAPACITY_SHAPES')
    if not settings:
        return
    import copy
    import dataclasses
    shapes = json.loads(settings)
    original = module.update_kv_cache_capacity

    def update(config, cache):
        result = original(config, cache)
        try:
            groups = []
            for group in cache.kv_cache_groups:
                spec = group.kv_cache_spec
                groups.append(dict(type=type(spec).__name__,
                    host_resident=getattr(group, 'host_resident', False),
                    layer_names=list(group.layer_names),
                    spec=json.loads(json.dumps(dataclasses.asdict(spec), default=str)),
                    page_bytes=spec.page_size_bytes))
            costs = []
            for length, output in shapes:
                local = copy.copy(config)
                local.model_config = copy.copy(config.model_config)
                local.model_config.max_model_len = length + 1 + output
                entries = []
                for group in cache.kv_cache_groups:
                    spec = group.kv_cache_spec
                    entries.append((spec.max_memory_usage_bytes(local) + spec.page_size_bytes - 1)
                                   // spec.page_size_bytes)
                costs.append(dict(input_tokens=length, output_tokens=output,
                                  runtime_blocks_by_group=entries))
            emit('capacity', dict(dp_rank=config.parallel_config.data_parallel_index,
                num_blocks=cache.num_blocks, max_model_len=config.model_config.max_model_len,
                groups=groups, costs=costs))
        except Exception as exc:
            # Observation must not change the engine's allocation decisions.
            emit('capacity-error', dict(error=repr(exc)))
        return result
    module.update_kv_cache_capacity = update


def emit(kind, value):
    path = Path(ROOT) / f'{kind}-{os.getpid()}.jsonl'
    value.update(pid=os.getpid(), time_ns=time.time_ns())
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(value, separators=(',', ':')) + '\n')


def observe_scheduler(module):
    cls = module.Scheduler
    update, finish = cls._update_after_schedule, cls._free_request

    def after_schedule(self, output):
        records = self.__dict__.setdefault('_inferoptlab_decode_records', {})
        for rid, count in output.num_scheduled_tokens.items():
            if 'cachedD-' not in rid and 'qualifyD-' not in rid:
                continue
            request = self.requests[rid]
            row = records.setdefault(rid, dict(request_id=rid,
                dp_rank=self.parallel_config.data_parallel_index,
                prompt_tokens=request.num_prompt_tokens,
                first_computed_tokens=request.num_computed_tokens,
                first_query_tokens=count, max_query_tokens=0,
                scheduled_tokens=0, steps=0, max_running_requests=0,
                max_scheduled_requests=0))
            row['max_query_tokens'] = max(row['max_query_tokens'], count)
            row['max_running_requests'] = max(row['max_running_requests'], len(self.running))
            row['max_scheduled_requests'] = max(row['max_scheduled_requests'], len(output.num_scheduled_tokens))
            row['scheduled_tokens'] += count
            row['steps'] += 1
        return update(self, output)

    def free_request(self, request, *args, **kwargs):
        records = self.__dict__.get('_inferoptlab_decode_records', {})
        row = records.pop(request.request_id, None)
        if row is not None:
            row.update(output_tokens=request.num_output_tokens,
                       status=str(request.status), preemptions=request.num_preemptions)
            emit('scheduler', row)
        return finish(self, request, *args, **kwargs)

    cls._update_after_schedule = after_schedule
    cls._free_request = free_request
    emit('installed', dict(module=module.__name__, observer='scheduler'))


def observe_attention(module):
    if os.environ.get('INFEROPTLAB_SPARSE_PREFILL_OFFSET64') == '1' and hasattr(module, 'flash_mla_sparse_fwd'):
        from sparse_prefill_repair import prefill
        module.flash_mla_sparse_fwd = prefill
        emit('installed', dict(module=module.__name__, repair='sparse_prefill_offset64'))
    names = ('GDNAttentionMetadataBuilder', 'FlashMLASparseMetadataBuilder')
    for name in names:
        cls = getattr(module, name, None)
        if cls is None:
            continue
        original = cls.build

        def build(self, *args, _original=original, _name=name, **kwargs):
            result = _original(self, *args, **kwargs)
            marker = Path(ROOT) / 'qualification-active.txt'
            try:
                phase = marker.read_text().strip()
            except FileNotFoundError:
                pass
            else:
                emit('attention', dict(builder=_name, phase=phase,
                    num_prefills=int(result.num_prefills),
                    num_decodes=int(result.num_decodes),
                    num_prefill_tokens=int(getattr(result, 'num_prefill_tokens', 0))))
            return result

        cls.build = build
        emit('installed', dict(module=module.__name__, observer=name))


TARGETS = {
    'vllm.v1.core.kv_cache_utils': observe_capacity,
    'vllm.v1.core.sched.scheduler': observe_scheduler,
    'vllm.v1.attention.backends.gdn_attn': observe_attention,
    'vllm_metax.v1.attention.backends.mla.flashmla_sparse': observe_attention,
}


class ObserverLoader(importlib.abc.Loader):
    def __init__(self, loader, callback):
        self.loader, self.callback = loader, callback

    def create_module(self, spec):
        return self.loader.create_module(spec)

    def exec_module(self, module):
        self.loader.exec_module(module)
        self.callback(module)


class ObserverFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname not in TARGETS:
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec and spec.loader:
            spec.loader = ObserverLoader(spec.loader, TARGETS[fullname])
        return spec


if ROOT:
    Path(ROOT).mkdir(parents=True, exist_ok=True)
    sys.meta_path.insert(0, ObserverFinder())
