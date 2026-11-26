"""Bind an inspected ModelSpec to the complete local-payload observation."""
import hashlib
import json


def verify_manifest(catalog, model):
    from tools.specs import digest
    errors = []
    checkpoint = model['checkpoint']
    source = catalog.get(checkpoint['payload_source_ref'])
    path = (catalog.root / source['path']).resolve()
    if not path.is_relative_to(catalog.root):
        return ['checkpoint payload source escapes repository']
    try:
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != source['sha256']:
            return ['checkpoint payload source hash mismatch']
        value = json.loads(data)
        if value['status'] != 'completed' or value['verification_scope'] != 'all_indexed_payload_bytes_and_index_headers':
            errors.append('checkpoint payload observation is not complete')
        shards = value['shards']
        if len({s['name'] for s in shards}) != len(shards) or shards != sorted(shards, key=lambda s: s['name']):
            errors.append('checkpoint payload manifest must have unique sorted shard names')
        identity = [dict(name=s['name'], size_bytes=s['size_bytes'], sha256=s['sha256']) for s in shards]
        if digest(identity) != value['weights_sha256'] or value['weights_sha256'] != model['identity']['weights_sha256']:
            errors.append('checkpoint payload identity differs from ModelSpec')
        if sum(s['size_bytes'] for s in shards) != checkpoint['total_file_bytes'] or len(shards) != checkpoint['shard_count']:
            errors.append('checkpoint payload manifest size/count differs from ModelSpec')
        if value['index_sha256'] != checkpoint['index']['sha256'] or value['tensor_count'] != checkpoint['tensor_count']:
            errors.append('checkpoint payload index/tensor count differs from ModelSpec')
        headers = [dict(name=s['name'], size_bytes=s['size_bytes'], header_sha256=s['header_sha256']) for s in shards]
        if digest(headers) != checkpoint['manifest_sha256']:
            errors.append('checkpoint header identity differs from payload observation')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append('invalid checkpoint payload source: ' + str(exc))
    return errors
