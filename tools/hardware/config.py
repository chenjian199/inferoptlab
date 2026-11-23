"""Plan validation and allocation bounds; no remote calls."""
from pathlib import Path

from tools.specs import Catalog, SpecError, read


def validate(plan):
    errors = Catalog().structural_errors(plan)
    if errors:
        raise SpecError('\n'.join(errors))
    errors = semantic_errors(plan)
    if errors:
        raise SpecError('\n'.join(errors))
    return plan


def semantic_errors(plan):
    errors = []
    hosts = plan['hosts']
    if len({h['id'] for h in hosts}) != len(hosts) or len({h['ssh'] for h in hosts}) != len(hosts):
        errors.append('host IDs and SSH aliases must be unique')
    if any(h['devices'] != 'all' and len(h['devices']) > h['max_devices'] for h in hosts):
        errors.append('selected GPUs exceed max_devices')
    protocol = plan['protocol']
    for shape in protocol['gemm_shapes']:
        if any(n % 64 for n in shape):
            errors.append('GEMM dimensions must be multiples of 64 for the fixed correctness probe')
        m, n, k = shape
        if (m*k+k*n+m*n)*4 + m*n > protocol['max_allocation_mib'] * 1024**2:
            errors.append('GEMM buffers exceed max_allocation_mib (including correctness scratch)')
    if any(mib*2.25 > protocol['max_allocation_mib'] for mib in protocol['copy_sizes_mib']):
        errors.append('copy buffers exceed max_allocation_mib (including correctness scratch)')
    return errors


def load(path):
    return validate(read(Path(path)))
