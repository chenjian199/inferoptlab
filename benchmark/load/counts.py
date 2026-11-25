"""Resolve explicit or concurrency-proportional request counts at each point."""
import copy
import math
from tools.specs import SpecError


def request_count(workload, concurrency):
    requests = workload['requests']
    multiplier = requests.get('count_multiplier')
    if multiplier is None:
        return requests['count']
    if requests['count'] is not None or isinstance(multiplier, bool) or not isinstance(multiplier, int) or multiplier < 1:
        raise SpecError('count_multiplier must be a positive integer and count must be null')
    if isinstance(concurrency, bool) or int(concurrency) != concurrency or concurrency < 1:
        raise SpecError('concurrency must be a positive integer')
    return int(concurrency) * max(multiplier, math.ceil(requests.get('min_count', 1) / concurrency))


def at_point(workload, concurrency):
    result = copy.deepcopy(workload)
    if workload['requests'].get('count_multiplier') is not None:
        result['requests']['count'] = request_count(workload, concurrency)
        result['requests'].pop('count_multiplier')
        result['requests'].pop('min_count', None)
        hashes=result['requests'].pop('request_set_sha256_by_concurrency',{})
        result['requests']['request_set_sha256']=hashes.get(str(int(concurrency)),result['requests']['request_set_sha256'])
    return result


def protocol_at_point(protocol, concurrency):
    result = copy.deepcopy(protocol)
    execution = result['execution']
    multiplier = execution.pop('warmup_request_multiplier', None)
    if multiplier is not None:
        execution['warmup_request_count'] = max(execution['warmup_request_count'], int(concurrency) * multiplier)
    return result


def fixture_name(scene, workload, concurrency):
    return scene['id'] + (f'/c{int(concurrency)}' if workload['requests'].get('count_multiplier') is not None else '')


def fixture_source(scene, workload, concurrency):
    return scene['dataset_dir'] + (f'/c{int(concurrency)}' if workload['requests'].get('count_multiplier') is not None else '')
