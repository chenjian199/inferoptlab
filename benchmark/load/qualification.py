"""Startup receipts bind live API probes to existing versioned recipe contents.

This is capability evidence, not an accuracy or performance acceptance result.
"""
from __future__ import annotations
import inspect
import copy
import json
import random
import subprocess
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from tools.specs import SpecError, digest, write
from benchmark.common.io import json_write, utc_now
from benchmark.load.adapters import for_runtime, sglang
from benchmark.load.planner import embedded_catalog, scenario_parts, snapshot_errors
from benchmark.load import dataset


def binding(catalog, deployment):
    return {name: digest(value) for name, value in {
        'deployment': deployment,
        'runtime': catalog.get(deployment['runtime_ref']),
        'model': catalog.get(deployment['model_ref']),
        'hardware': catalog.get(deployment['hardware_ref']),
    }.items()}


def verify_receipt(catalog, snapshot, path, allow_failed=False):
    receipt = json.loads(Path(path).read_text(encoding='utf-8'))
    if receipt.get('content_sha256') != digest({k: v for k, v in receipt.items() if k != 'content_sha256'}):
        raise SpecError('qualification receipt hash mismatch')
    plan = catalog.get(snapshot['plan_ref'])
    required = max(scenario_parts(catalog, r)[2]['input']['tokens'] + scenario_parts(catalog, r)[2]['output']['tokens']
                   for r in plan['scenario_refs'])
    required_input = max(scenario_parts(catalog, r)[2]['input']['tokens'] for r in plan['scenario_refs'])
    for reference in plan['deployment_refs']:
        dep = catalog.get(reference)
        # Startup checked this exact deployment's configured context against the
        # live server. A one-token prefill probe may qualify a longer output case
        # within that unchanged limit, but cannot qualify an untested input size.
        matches = [r for r in receipt['deployments'] if r['binding'] == binding(catalog, dep)
                   and r['status'] == 'passed' and (dep['scheduling'].get('max_model_len') or 0) >= required
                   and any(p['status'] == 'passed' and p['input_tokens'] >= required_input for p in r['probes'])]
        if not matches:
            if allow_failed and any(r['binding']==binding(catalog,dep) and r['status']=='failed'
                                    for r in receipt['deployments']):
                continue  # Runner records an explicit startup failure skip; it may not launch this deployment.
            raise SpecError(f'{dep["id"]}: no matching successful startup qualification; changed recipes need requalification')
    return receipt


def select_qualified(catalog, snapshot, path):
    """Materialize an explicit reduced plan; failed candidates remain in its audit trail."""
    embedded = embedded_catalog(catalog, snapshot)
    plan = copy.deepcopy(embedded.get(snapshot['plan_ref']))
    accepted, excluded = [], []
    for reference in plan['deployment_refs']:
        one = copy.deepcopy(plan)
        one['deployment_refs'] = [reference]
        embedded.documents[(one['id'], one['version'])] = one
        try:
            verify_receipt(embedded, snapshot, path)
            accepted.append(reference)
        except SpecError as exc:
            excluded.append(dict(deployment_ref=reference, reason=str(exc)))
    if not accepted:
        raise SpecError('no qualified deployments; inspect startup evidence before changing the plan')
    plan['id'] += '-qualified'
    plan['title'] += ' (startup-qualified subset)'
    plan['deployment_refs'] = accepted
    plan['extensions']['qualification.selection'] = dict(parent_sha256=snapshot['content_sha256'], excluded=excluded)
    return plan


def exact_prompt(active, tokens):
    """Tokenize inside the exact serving image; avoid another tokenizer installation."""
    if not getattr(active, 'container_id', None):
        raise SpecError('exact-context qualification requires an owned Docker deployment')
    source = ('import json, random\nfrom collections.abc import Mapping\n'
              'from transformers import AutoTokenizer\nclass SpecError(ValueError): pass\n'
              + inspect.getsource(dataset.token_count) + '\n' + inspect.getsource(dataset.prompt)
              + '\nt = AutoTokenizer.from_pretrained(' + repr(active.deployment['serving']['model_path'])
              + ', local_files_only=True, trust_remote_code=False)\n'
              + 'print(json.dumps(prompt(t, random.Random(20261124), ' + str(tokens) + ')))\n')
    try:
        completed = subprocess.run(['docker', 'exec', '-i', active.container_id, 'python3', '-'],
                                   input=source, text=True, capture_output=True, timeout=180, check=True)
    except subprocess.CalledProcessError as exc:
        raise SpecError('serving-image tokenizer probe failed: ' + exc.stderr[-4000:]) from exc
    return json.loads(completed.stdout)


def request(serving, text, output_tokens, timeout):
    body = dict(model=serving['served_model'], messages=[dict(role='user', content=text)],
                max_tokens=output_tokens, min_tokens=output_tokens, ignore_eos=True, temperature=0, stream=False)
    req = Request(serving['url'].rstrip('/') + '/v1/chat/completions', data=json.dumps(body).encode(),
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=timeout) as response:
            value = json.load(response)
    except HTTPError as exc:
        raise SpecError(f'qualification API HTTP {exc.code}: ' + exc.read(4000).decode('utf-8', errors='replace')) from exc
    if value.get('error') or not value.get('choices'):
        raise SpecError('qualification request returned no completion')
    if value.get('usage', {}).get('completion_tokens') != output_tokens:
        raise SpecError('qualification output token count differs from requested count')
    return value


def qualify(catalog, snapshot, output):
    errors = snapshot_errors(catalog, snapshot)
    if errors or snapshot['execution_issues']:
        raise SpecError('\n'.join(errors + snapshot['execution_issues']))
    embedded = embedded_catalog(catalog, snapshot)
    plan = embedded.get(snapshot['plan_ref'])
    deployments_by_id = {r['id']: embedded.get(r) for r in plan['deployment_refs']}
    if len(deployments_by_id) != len(plan['deployment_refs']):
        raise SpecError('startup qualification requires distinct deployment IDs within a plan')
    output = Path(output).resolve()
    if not output.is_relative_to((catalog.root / 'experiments').resolve()):
        raise SpecError('qualification output must be within experiments/')
    output.mkdir(parents=True, exist_ok=False)
    write(output / 'resolved.yaml', snapshot)
    maximum = max(scenario_parts(embedded, r)[2]['input']['tokens'] + scenario_parts(embedded, r)[2]['output']['tokens']
                  for r in plan['scenario_refs'])
    input_tokens = max(scenario_parts(embedded, r)[2]['input']['tokens'] for r in plan['scenario_refs'])
    receipt = dict(format_version=1, created_at=utc_now(), scope='startup_and_api_only',
                   accuracy_qualified=False, performance_baseline=False, plan_sha256=snapshot['content_sha256'], deployments=[])
    def save():
        receipt['content_sha256'] = digest({k: v for k, v in receipt.items() if k != 'content_sha256'})
        json_write(output / 'qualification.json', receipt)
        lines = ['# Startup qualification', '', 'Scope: startup and exact-length API probes; not accuracy or performance acceptance.', '',
                 '| Deployment | TP / PP / DP / EP | Context | Token budget | Max sequences / DP | Status | Detail |',
                 '| --- | --- | ---: | ---: | ---: | --- | --- |']
        for row in receipt['deployments']:
            d = deployments_by_id[row['id']]
            parallel = ' / '.join(str(d['parallelism'][k]) for k in ('tp', 'pp', 'dp', 'ep'))
            schedule = d['scheduling']
            detail = (row['error'] or ', '.join(f"{p['input_tokens']}→{p['output_tokens']}" for p in row['probes'])).replace('|', '/').replace('\n', ' ')
            lines.append(f"| {row['id']} | {parallel} | {schedule.get('max_model_len')} | {schedule.get('max_num_batched_tokens')} | {schedule['max_running_requests']} | {row['status']} | {detail} |")
        (output / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    save()
    for reference in plan['deployment_refs']:
        dep = embedded.get(reference)
        runtime = embedded.get(dep['runtime_ref'])
        adapter = for_runtime(runtime)
        directory = output / dep['id']
        directory.mkdir()
        entry = dict(id=dep['id'], binding=binding(embedded, dep), status='starting', maximum_context=maximum,
                     started_at=utc_now(), probes=[], error=None)
        receipt['deployments'].append(entry)
        save()
        active = adapter.Deployment(dep, runtime, directory / 'server.log')
        print('QUALIFY_START', dep['id'], flush=True)
        try:
            from benchmark.load.adapters.metax import inventory, binding_issues
            probe = inventory()
            json_write(directory / 'devices.json', probe)
            errors = binding_issues(probe, dep['devices'], embedded.get(dep['hardware_ref']))
            if probe['status'] != 'observed' or errors:
                raise SpecError('device inventory verification failed: ' + '; '.join(errors))
            entry['command'] = active.launch()
            save()
            sglang.wait_ready(dep['serving'], time.monotonic() + dep['serving']['startup_timeout_s'], active.process)
            entry['http_ready'] = True
            info, issues = adapter.inspect_server(dep['serving'])
            issues += adapter.verify_server(dep, info, maximum)
            json_write(directory / 'server-info.json', info)
            if issues:
                raise SpecError('; '.join(issues))
            sglang.smoke(dep['serving'], timeout=120)
            for length, out in sorted({(128, 32), (input_tokens, 1)}):
                text = exact_prompt(active, length)
                response = request(dep['serving'], text, out, 600)
                json_write(directory / f'probe-{length}-{out}.json', response)
                if response['usage']['prompt_tokens'] != length:
                    raise SpecError('server input token count differs from frozen tokenizer count')
                entry['probes'].append(dict(input_tokens=length, output_tokens=out, status='passed'))
            if dep.get('prefix_cache'):
                text = exact_prompt(active, input_tokens)
                request(dep['serving'], text, 1, 600)
                replay = request(dep['serving'], text, 32, 600)
                json_write(directory / 'cache-replay.json', replay)
                cached = replay.get('usage', {}).get('prompt_tokens_details', {}).get('cached_tokens')
                entry['cached_tokens'] = cached
                for r in plan['scenario_refs']:
                    _, _, workload, protocol = scenario_parts(embedded, r)
                    if protocol['method'] == 'prefix_reuse_decode':
                        if cached is None or cached / input_tokens < workload['cache']['target_hit_ratio'] or input_tokens - cached > protocol['cache_replay']['max_uncached_tokens_per_request']:
                            raise SpecError('cache replay does not satisfy declared per-request cache requirement')
            entry['status'] = 'passed'
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            entry.update(status='failed', error=str(exc))
        finally:
            try:
                active.close()
            except (OSError, ValueError, subprocess.SubprocessError) as exc:
                entry.update(status='cleanup_failed', error='owned deployment cleanup failed: ' + str(exc))
                raise SpecError(entry['error']) from exc
            finally:
                entry['finished_at'] = utc_now()
                save()
                print('QUALIFY_RESULT', dep['id'], entry['status'], entry['error'], flush=True)
    return receipt
