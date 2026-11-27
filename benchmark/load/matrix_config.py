"""Expand matrix axes, build deployment settings and verify resolved KV pools.

This module has no execution entrypoint; matrix_run owns the scan lifecycle.
"""
from __future__ import annotations

import itertools
import json
import math

from benchmark.load import decode_protocol as cd
from tools.specs import SpecError, digest


AXES = {'parallelism', 'enable_expert_parallel', 'max_model_len', 'max_num_seqs',
        'max_num_batched_tokens', 'enable_chunked_prefill', 'graph_enabled',
        'gpu_memory_utilization'}


def expand(matrix):
    axes = matrix['deployment_matrix']
    if set(axes) != AXES or any(not isinstance(v, list) or not v for v in axes.values()):
        raise SpecError('unsupported or empty deployment matrix axis')
    if matrix['measurement']['method'] != 'cached_decode':
        raise SpecError('matrix requires cached_decode')
    if matrix['capacity_planning']['concurrency_limit_basis'] != 'kv_residency_only':
        raise SpecError('capacity must not be clipped to running sequences')
    for name, values in matrix['workload_matrix'].items():
        if not values or any(type(x) is not int or x < (2 if name == 'output_tokens' else 1) for x in values):
            raise SpecError(f'invalid workload axis {name}')
    result = []
    seen = set()
    for values in itertools.product(*axes.values()):
        row = dict(zip(axes, values))
        p = row['parallelism']
        if p['pp'] != 1 or math.prod(p.values()) != len(matrix['target']['gpu_indices']):
            raise SpecError('matrix requires single-node PP1 and full selected GPU allocation')
        flat = {**row, **p}
        if any(all(flat.get(k) == v for k, v in rule['match'].items())
               for rule in matrix['combination_rules'].get('exclude', [])):
            continue
        identity = digest(row)[:12]
        if identity in seen:
            raise SpecError('duplicate deployment in matrix')
        seen.add(identity)
        row['id'] = (f'tp{p["tp"]}-dp{p["dp"]}-ep{int(row["enable_expert_parallel"])}'
                     f'-s{row["max_num_seqs"]}-b{row["max_num_batched_tokens"]}-{identity}')
        result.append(row)
    return result


def deployment_specs(matrix, row, cache_dir):
    target, fixed = matrix['target'], dict(matrix['server']['parameters'])
    if fixed.pop('enable_prefix_caching') is not True:
        raise SpecError('cached capacity requires prefix caching')
    if fixed.pop('async_scheduling') is not False:
        raise SpecError('capacity protocol currently requires synchronous scheduling')
    parameters = {}
    for k, v in fixed.items():
        parameters['--' + k.replace('_', '-')] = json.dumps(v) if isinstance(v, (dict, list)) else v
    parameters.update({'--no-async-scheduling': True,
                       '--enforce-eager': not row['graph_enabled'],
                       '--gpu-memory-utilization': row['gpu_memory_utilization']})
    p = row['parallelism']
    dep = dict(id=row['id'], mode='aggregated', prefix_cache=True,
        parallelism={**p, 'ep': p['tp'] * p['dp'] if row['enable_expert_parallel'] else 1},
        scheduling=dict(max_model_len=row['max_model_len'],
                        chunked_prefill_tokens=None, kv_page_tokens=None,
                        max_running_requests=row['max_num_seqs'],
                        max_num_batched_tokens=row['max_num_batched_tokens'],
                        enable_chunked_prefill=row['enable_chunked_prefill']),
        serving=dict(management='vllm-docker', url=f'http://127.0.0.1:{target["port"]}',
                     served_model=target['served_model_name'], model_path=target['model_path'],
                     tokenizer_path=target['tokenizer_path'], device_visibility_env='MACA_VISIBLE_DEVICES',
                     cache_dir=str(cache_dir), startup_timeout_s=matrix['server']['startup_timeout_s']),
        devices=[dict(rank=i, visible_index=g) for i, g in enumerate(target['gpu_indices'])],
        backend_options={})
    env = dict(matrix['server']['environment'])
    env['INFEROPTLAB_CAPACITY_SHAPES'] = json.dumps([
        [length, max(matrix['workload_matrix']['output_tokens'])]
        for length in matrix['workload_matrix']['input_tokens']])
    runtime = dict(engine='vllm-metax', container_digest=target['docker_image_id'],
                   container_identity_kind='docker_image_id', launch_parameters=parameters,
                   execution_profile=dict(environment=env))
    return dep, runtime


def verify(row, info):
    c = info['vllm_config']
    p = c['parallel_config']
    s = c['scheduler_config']
    m = c['model_config']
    checks = [(p['tensor_parallel_size'], row['parallelism']['tp']),
              (p['data_parallel_size'], row['parallelism']['dp']),
              (p['pipeline_parallel_size'], 1),
              (p['enable_expert_parallel'], row['enable_expert_parallel']),
              (s['max_num_seqs'], row['max_num_seqs']),
              (s['max_num_batched_tokens'], row['max_num_batched_tokens']),
              (s['enable_chunked_prefill'], row['enable_chunked_prefill']),
              (m['enforce_eager'], not row['graph_enabled']),
              (c['cache_config']['enable_prefix_caching'], True),
              (c['cache_config']['gpu_memory_utilization'], row['gpu_memory_utilization'])]
    if row['max_model_len'] != 'auto':
        checks.append((m['max_model_len'], row['max_model_len']))
    if any(a != b for a, b in checks):
        raise SpecError('resolved server parameters differ from matrix')
    if row['graph_enabled']:
        mode = str(c.get('compilation_config', {}).get('cudagraph_mode', '')).upper()
        if mode in {'', 'NONE', '0'}:
            raise SpecError('requested graph mode is not active')


def pool_inventory(observations, dp):
    records = cd.observations(observations, 'capacity')
    ranks = {int(r['dp_rank']): r for r in records}
    if set(ranks) != set(range(dp)):
        raise SpecError(f'missing per-engine capacity evidence: have {sorted(ranks)}, need {dp}')
    if any(any(g['host_resident'] for g in r['groups']) for r in ranks.values()):
        raise SpecError('host/offloaded KV pools are not supported by this matrix')
    return [ranks[r] for r in range(dp)]
