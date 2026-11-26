"""Resume the same immutable matrix, retaining every failed attempt."""
from __future__ import annotations

import json
import uuid
from copy import deepcopy
from pathlib import Path

from benchmark.common.io import file_hash, inside, json_write, utc_now
from tools.specs import SpecError, read, digest

FAILED = {'failed', 'invalid', 'unverified', 'completed_with_errors'}


def skipping_failures(state):
    return state.get('execution_policy', {}).get('on_failure') == 'skip_configuration'


def enable_failure_skipping(state):
    state.setdefault('execution_policy', dict(on_failure='skip_configuration', requested_by='user',
                     requested_at=utc_now(), reason='Keep failure evidence; continue other configurations without retries.'))
    if not skipping_failures(state):
        raise SpecError('conflicting execution policy')


def terminal(entry, state):
    if entry['status'] in {'completed', 'skipped_by_user'}:
        return True
    return (skipping_failures(state) and (
            (entry.get('failure_evidence') is not None and entry['status'] in FAILED | {'skipped_failed_configuration'})
            or (entry['status']=='skipped_startup_failure' and entry.get('startup_failure') is not None)))


def startup_failures(snapshot, receipt):
    documents={(x['document']['id'],x['document']['version']):x['document'] for x in snapshot['documents']}
    result={}
    for trial in snapshot['trials']:
        ref=trial['deployment_ref'];identity=(ref['id'],ref['version'])
        if ref['id'] in result:
            continue
        dep=documents[identity]
        expected=dict(deployment=digest(dep))
        for name in ('runtime','model','hardware'):
            r=dep[name+'_ref'];expected[name]=digest(documents[(r['id'],r['version'])])
        rows=[row for row in receipt['deployments'] if row['binding']==expected]
        if not any(row['status']=='passed' for row in rows) and any(row['status']=='failed' for row in rows):
            result[ref['id']]=expected
    return result


def apply_startup_failures(directory,state,snapshot,receipt):
    if not skipping_failures(state) or receipt is None:
        return
    failed=startup_failures(snapshot,receipt)
    for entry in state['runs']:
        if entry['deployment'] not in failed or entry['status'] in {'completed','skipped_by_user'}:
            continue
        if entry.get('directory'):
            raise SpecError('startup failure cannot replace existing run evidence')
        entry.update(status='skipped_startup_failure',startup_failure=dict(
            receipt_sha256=file_hash(Path(directory)/'qualification.json'),binding=failed[entry['deployment']]))


def check_startup_failure(directory,entry,state,snapshot):
    if not skipping_failures(state) or state['execution_policy'].get('requested_by')!='user':
        raise SpecError('startup failure skip requires user execution policy')
    path=Path(directory)/'qualification.json';receipt=read(path)
    if receipt.get('content_sha256')!=digest({k:v for k,v in receipt.items() if k!='content_sha256'}):
        raise SpecError('startup failure receipt hash mismatch')
    evidence=entry.get('startup_failure',{})
    expected=startup_failures(snapshot,receipt).get(entry['deployment'])
    if (expected is None or evidence.get('receipt_sha256')!=file_hash(path)
            or evidence.get('binding')!=expected):
        raise SpecError('startup failure skip has no matching failed qualification')


def check_failure_evidence(directory, entry, state):
    if not skipping_failures(state) or state['execution_policy'].get('requested_by') != 'user':
        raise SpecError('failure disposition requires an explicit user execution policy')
    evidence = entry['failure_evidence']
    path = inside(directory, evidence['directory']) / 'run.json'
    record = json.loads(path.read_text(encoding='utf-8'))
    if (record['status'] not in FAILED or record['trial_id'] != key(entry)[0]
            or record['plan_sha256'] != state['plan_sha256']
            or file_hash(path) != evidence['sha256']):
        raise SpecError('failure disposition does not match archived failure evidence')


def apply_failure_policy(directory, state):
    """Keep failed attempts; skip only the same configuration's remaining repeats."""
    if not skipping_failures(state):
        return
    failures = {}
    for entry in state['runs']:
        for attempt in [entry, *reversed(entry.get('attempts', []))]:
            if attempt['status'] in FAILED and attempt.get('directory'):
                evidence = dict(directory=attempt['directory'],
                                sha256=file_hash(inside(directory, attempt['directory']) / 'run.json'))
                check_failure_evidence(directory, dict(entry, failure_evidence=evidence), state)
                failures.setdefault(key(entry)[0], evidence)
                break
    for entry in state['runs']:
        identity = key(entry)[0]
        if identity not in failures or entry['status'] in {'completed', 'skipped_by_user'}:
            continue
        if entry['status'] not in FAILED:
            if entry.get('directory'):
                begin(entry)
            entry['status'] = 'skipped_failed_configuration'
        entry['failure_evidence'] = failures[identity]


def key(value):
    return value.get('trial_id', value.get('id')), value['repetition']


def exclusions(directory, snapshot):
    """Explicit user exclusions are separate from the immutable measurement plan."""
    path = Path(directory) / 'exclusions.json'
    if not path.exists():
        return {}, None
    directive = json.loads(path.read_text(encoding='utf-8'))
    if (directive.get('plan_sha256') != snapshot['content_sha256']
            or directive.get('requested_by') != 'user'
            or not directive.get('requested_at') or not directive.get('reason', '').strip()):
        raise SpecError('exclusions require a user reason, timestamp and matching plan fingerprint')
    known = {key(t) for t in snapshot['trials']}
    selected = {}
    for item in directive['trials']:
        identity = key(item)
        if identity not in known or identity in selected:
            raise SpecError('exclusions contain an unknown or duplicate trial/repetition')
        selected[identity] = directive['reason']
    if not selected:
        raise SpecError('exclusions must identify at least one trial/repetition')
    return selected, file_hash(path)


def apply_exclusions(directory, state, snapshot):
    selected, fingerprint = exclusions(directory, snapshot)
    for entry in state['runs']:
        if key(entry) not in selected:
            continue
        if entry['status'] == 'completed':
            raise SpecError('cannot exclude completed evidence')
        if entry['status'] != 'skipped_by_user':
            entry['status_before_exclusion'] = entry['status']
        # Keep the failed run directory and its original record intact.
        entry.update(status='skipped_by_user', exclusion_reason=selected[key(entry)],
                     exclusions_sha256=fingerprint)


def load(directory, snapshot):
    """Read and validate before changing anything; completion requires raw evidence."""
    directory = Path(directory)
    if read(directory / 'resolved.yaml') != snapshot:
        raise SpecError('resume requires the exact archived snapshot; changed recipes need a new batch')
    state = json.loads((directory / 'batch.json').read_text(encoding='utf-8'))
    if state['plan_sha256'] != snapshot['content_sha256']:
        raise SpecError('resume batch/snapshot fingerprint mismatch')
    trials = {key(t): t for t in snapshot['trials']}
    selected, fingerprint = exclusions(directory, snapshot)
    seen = set()
    for entry in state['runs']:
        identity = key(entry)
        if identity not in trials or identity in seen:
            raise SpecError('resume ledger has an unknown or duplicate trial/repetition')
        seen.add(identity)
        if entry['status']=='skipped_startup_failure':
            check_startup_failure(directory,entry,state,snapshot)
        if entry.get('failure_evidence') or entry['status'] == 'skipped_failed_configuration':
            if not entry.get('failure_evidence'):
                raise SpecError('failure skip has no evidence')
            check_failure_evidence(directory, entry, state)
        if entry['status'] == 'skipped_by_user':
            if (identity not in selected or entry.get('exclusions_sha256') != fingerprint
                    or entry.get('exclusion_reason') != selected[identity]):
                raise SpecError('user-skipped row has no matching exclusion directive')
        if entry['status'] == 'completed' and identity in selected:
            raise SpecError('cannot exclude completed evidence')
        if entry['status'] != 'completed':
            continue
        run = inside(directory, entry['directory'])
        record = json.loads((run / 'run.json').read_text(encoding='utf-8'))
        bundle = json.loads((run / 'summary.json').read_text(encoding='utf-8'))
        counts = bundle['counts']
        if (key(record) != identity or record['status'] != 'completed'
                or record['plan_sha256'] != snapshot['content_sha256']
                or record.get('environment_issues') or bundle['validity'] != 'valid'
                or counts['failed'] or counts['missing']
                or counts['succeeded'] != counts['planned']
                or counts['planned'] != record['dataset_manifest']['files']['requests.jsonl']['count']
                or bundle['raw_sha256'] != file_hash(run / 'raw/aiperf/profile_export.jsonl')):
            raise SpecError(f'resume completed evidence is inconsistent: {entry["directory"]}')
    return state


def reopen(directory, state):
    """Archive mutable progress; old run directories are never modified."""
    json_write(Path(directory) / 'checkpoints' / (uuid.uuid4().hex + '.json'), state)
    state = deepcopy(state)
    state.update(status='preparing', resumed_at=utc_now(), current_trial=None)
    state.pop('finished_at', None)
    state.pop('error', None)
    return state


def begin(entry):
    if entry.get('directory'):
        history = entry.setdefault('attempts', [])
        history.append({k: deepcopy(v) for k, v in entry.items() if k != 'attempts'})
    entry.update(status='pending', directory=None)
    return len(entry.get('attempts', [])) + 1
