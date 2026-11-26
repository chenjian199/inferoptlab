"""Collect a contemporary TP8 functional reference and parallelism regressions.

Each repetition starts a new owned serving container. Reuses DeploymentSpec and
the benchmark plan; never starts the performance scan or grants release approval.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import time
from urllib.request import Request, urlopen

from benchmark.accuracy import code_adapter, sandbox
from benchmark.accuracy.functional import audit_run, matrix_gate
from benchmark.common.io import file_hash, json_write, utc_now
from benchmark.load.adapters import vllm, sglang
from benchmark.load.cli import load_snapshot
from benchmark.load.planner import embedded_catalog
from benchmark.load.qualification import binding, verify_receipt
from benchmark.load.runner import lease
from tools.specs import Catalog, SpecError, digest, read, write

INSTRUCTION = ('Complete the Python function from the following prefix. Output only the missing '
               'continuation, preserving indentation. Do not repeat the prefix or include explanations.')
SAMPLING = dict(temperature=0.0, top_p=1.0, seed=0, max_tokens=1024, ignore_eos=False)


def comparison_issues(deployments):
    """Only the declared parallelism and derived per-DP capacity may change."""
    issues = []
    baseline = deployments[0]
    for dep in deployments:
        for field in ('model_ref', 'hardware_ref', 'runtime_ref', 'prefix_cache', 'backend_options', 'serving', 'devices', 'mode'):
            if dep[field] != baseline[field]:
                issues.append(f'{dep["id"]}: undeclared comparison change in {field}')
        for field, value in baseline['scheduling'].items():
            if field != 'max_running_requests' and dep['scheduling'].get(field) != value:
                issues.append(f'{dep["id"]}: undeclared scheduling change in {field}')
        if dep['scheduling']['max_running_requests'] * dep['parallelism']['dp'] != baseline['scheduling']['max_running_requests']:
            issues.append(f'{dep["id"]}: aggregate sequence capacity differs from reference')
    return issues


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def evaluate(directory, rows, outputs, image, canonical=False):
    results = []
    with (directory / 'correctness.jsonl').open('x', encoding='utf-8') as stream, ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda row: sandbox.score(row, outputs[row['task_id']], image), rows):
            stream.write(json.dumps(result, ensure_ascii=False) + '\n')
            stream.flush()
            results.append(result)
    infrastructure = any(r['result'] == 'infrastructure_error' for r in results)
    passed = sum(r['passed'] for r in results)
    summary = dict(status='incomplete' if infrastructure else 'complete', tasks=len(rows), passed=passed,
                   pass_at_1=None if infrastructure else passed / len(rows),
                   failures_by_type=dict(Counter(r['result'] for r in results)),
                   truncated=sum(r['truncated'] for r in results), canonical=canonical,
                   adapter_sha256=file_hash(code_adapter.__file__), evaluator_sha256=file_hash(sandbox.__file__),
                   sandbox_image=image)
    json_write(directory / 'score_summary.json', summary)
    if infrastructure or (canonical and passed != len(rows)):
        raise SpecError('CPU scorer failed canonical/infrastructure verification')
    return summary


def generate(catalog, deployment, prompts, directory, shared):
    runtime = catalog.get(deployment['runtime_ref'])
    active = vllm.Deployment(deployment, runtime, directory / 'server.log')
    manifest = dict(status='starting', task_ids=[r['task_id'] for r in prompts],
                    expected_tasks=len(prompts), completed_tasks=0, sampling=SAMPLING,
                    settings=shared, deployment_binding=binding(catalog, deployment))
    json_write(directory / 'generation_manifest.json', manifest)
    try:
        command = active.launch()
        info = json.loads(vllm.docker('inspect', active.container_id).stdout)[0]
        manifest['process'] = dict(container_id=info['Id'], pid=info['State']['Pid'], started_at=info['State']['StartedAt'])
        json_write(directory / 'launch.json', dict(command=command, process=manifest['process'], deployment=deployment))
        sglang.wait_ready(deployment['serving'], time.monotonic() + deployment['serving']['startup_timeout_s'], active.process)
        server, issues = vllm.inspect_server(deployment['serving'])
        issues += vllm.verify_server(deployment, server, 4096)
        json_write(directory / 'server-info.json', server)
        if issues:
            raise SpecError('; '.join(issues))
        inputs = {}
        manifest['status'] = 'running'
        with (directory / 'generations.jsonl').open('x', encoding='utf-8') as stream:
            for row in prompts:
                body = dict(SAMPLING, model=deployment['serving']['served_model'], stream=False,
                            messages=[dict(role='user', content=INSTRUCTION + '\n\n' + row['prompt'])],
                            chat_template_kwargs=dict(reasoning_effort='low'), return_token_ids=True)
                request = Request(deployment['serving']['url'] + '/v1/chat/completions',
                                  data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
                start = time.monotonic()
                with urlopen(request, timeout=600) as response:
                    value = json.load(response)
                choice = value['choices'][0]
                input_ids, output_ids = value.get('prompt_token_ids'), choice.get('token_ids')
                if not isinstance(input_ids, list) or not isinstance(output_ids, list) or not output_ids:
                    raise SpecError('API did not return actual prompt/output token IDs')
                if value['usage']['prompt_tokens'] != len(input_ids) or value['usage']['completion_tokens'] != len(output_ids):
                    raise SpecError('usage and actual token IDs disagree')
                if len(input_ids) + SAMPLING['max_tokens'] > 4096:
                    raise SpecError('HumanEval input exceeds frozen 4096-token quality context budget')
                inputs[row['task_id']] = input_ids
                result = dict(task_id=row['task_id'], text=choice['message'].get('content') or '',
                              reasoning=choice['message'].get('reasoning') or choice['message'].get('reasoning_content'),
                              output_token_ids=output_ids, prompt_tokens=len(input_ids), output_tokens=len(output_ids),
                              finish_reason=choice['finish_reason'], stop_reason=choice.get('stop_reason'),
                              generation_seconds=time.monotonic() - start)
                stream.write(json.dumps(result, ensure_ascii=False) + '\n'); stream.flush()
                manifest['completed_tasks'] += 1
                json_write(directory / 'generation_manifest.json', manifest)
                print(json.dumps(dict(run=directory.name, completed=manifest['completed_tasks'], task=row['task_id'])), flush=True)
        json_write(directory / 'prompt-token-ids.json', inputs)
        manifest.update(status='complete', generations_sha256=file_hash(directory / 'generations.jsonl'),
                        prompt_manifest_sha256=digest(inputs))
    except BaseException as exc:
        manifest.update(status='failed', error=str(exc))
        raise
    finally:
        try:
            active.close()
        finally:
            json_write(directory / 'generation_manifest.json', manifest)


def execute(catalog, snapshot, baseline, prompts_path, scoring_path, image, qualification, output, accuracy_plan):
    embedded = embedded_catalog(catalog, snapshot)
    plan = embedded.get(snapshot['plan_ref'])
    verify_receipt(embedded, snapshot, qualification)
    deployments = [read(baseline)] + [embedded.get(r) for r in plan['deployment_refs']]
    issues = comparison_issues(deployments)
    if issues:
        raise SpecError('; '.join(issues))
    for field in ('model_ref', 'hardware_ref', 'runtime_ref'):
        if any(d[field] != deployments[0][field] for d in deployments):
            raise SpecError('reference and candidates must bind the same model, hardware and runtime')
    if deployments[0]['parallelism'] != dict(tp=8, pp=1, dp=1, ep=1):
        raise SpecError('reference must be TP8/PP1/DP1/EP disabled')
    prompts, scoring = jsonl(prompts_path), jsonl(scoring_path)
    accuracy = read(accuracy_plan)
    manifest = accuracy['dataset']['manifest']
    if file_hash(catalog.root / manifest['path']) != manifest['sha256']:
        raise SpecError('HumanEval dataset manifest differs from the accuracy plan')
    dataset_manifest = read(catalog.root / manifest['path'])
    expected = {Path(f['path']).name: f['sha256'] for f in dataset_manifest['prepared_files']}
    if file_hash(prompts_path) != expected['prompts.jsonl'] or file_hash(scoring_path) != expected['scoring.jsonl']:
        raise SpecError('HumanEval prompts/tests differ from the fixed dataset revision')
    ids = [r['task_id'] for r in prompts]
    if ids != ['HumanEval/' + str(i) for i in range(164)] or [r['task_id'] for r in scoring] != ids:
        raise SpecError('requires all 164 original tasks in frozen order')
    if any(set(r) != {'task_id', 'prompt'} for r in prompts):
        raise SpecError('generation inputs must not contain tests or answers')
    if any(a['prompt'] != b['prompt'] for a, b in zip(prompts, scoring)):
        raise SpecError('prompt/scoring dataset mismatch')
    output = output.resolve()
    if not output.is_relative_to((catalog.root / 'experiments').resolve()):
        raise SpecError('accuracy output must be in experiments/')
    output.mkdir(parents=True, exist_ok=False)
    shared = dict(prompts_sha256=file_hash(prompts_path), scoring_sha256=file_hash(scoring_path),
                  instruction=INSTRUCTION, chat_template_kwargs=dict(reasoning_effort='low'),
                  request_concurrency=1, reference_kind='contemporary_same_image_tp8',
                  permitted_variables=['parallelism', 'max_running_requests_per_dp', 'derived_kv_block_size'],
                  runtime_sha256=digest(embedded.get(deployments[0]['runtime_ref'])),
                  model_sha256=digest(embedded.get(deployments[0]['model_ref'])))
    write(output / 'performance-plan-snapshot.yaml', snapshot)
    write(output / 'accuracy-method.yaml', accuracy)
    json_write(output / 'protocol.json', dict(shared=shared, sampling=SAMPLING, repetitions=3,
               deployment_bindings=[binding(embedded, d) for d in deployments],
               code_sha256={p.name: file_hash(p) for p in [Path(__file__), Path(sandbox.__file__), Path(code_adapter.__file__)]}))
    state = dict(status='running', created_at=utc_now(), runs=[], release_accepted=False,
                 numerical_acceptance='not_established', absolute_model_quality='not_established')
    try:
        test = sandbox.selftest(image)
        json_write(output / 'sandbox-selftest.json', test)
        if not test['passed']:
            raise SpecError('scoring sandbox self-test failed')
        canonical = output / 'canonical'; canonical.mkdir()
        evaluate(canonical, scoring, {r['task_id']: dict(text=r['canonical_solution'], finish_reason='canonical') for r in scoring}, image, True)
        for repetition in range(1, 4):
            for index, dep in enumerate(deployments):
                directory = output / f'repeat-{repetition}-deployment-{index}'
                directory.mkdir()
                row = dict(repetition=repetition, deployment=dep['id'], index=index,
                           directory=directory.relative_to(catalog.root).as_posix(), status='generating')
                state['runs'].append(row); json_write(output / 'state.json', state)
                generate(embedded, dep, prompts, directory, shared)
                row['status'] = 'scoring'; json_write(output / 'state.json', state)
                scores = evaluate(directory, scoring, {r['task_id']: r for r in jsonl(directory / 'generations.jsonl')}, image)
                row.update(status='complete', passed=scores['passed']); json_write(output / 'state.json', state)
        audits = {i: [audit_run(catalog.root, r['directory'], ids) for r in state['runs'] if r['index'] == i] for i in range(len(deployments))}
        all_runs = [a for rows in audits.values() for a in rows]
        if len({a['fingerprint'] for a in all_runs}) != 1 or len({digest(a['process']) for a in all_runs}) != len(all_runs):
            raise SpecError('input/scoring identity or independent-process evidence differs')
        state['comparisons'] = {deployments[i]['id']: matrix_gate([a['scores'] for a in audits[0]], [a['scores'] for a in audits[i]]) for i in range(1, len(deployments))}
        state['status'] = 'completed_functional_only'
    except BaseException as exc:
        state.update(status='failed', error=str(exc)); raise
    finally:
        state['finished_at'] = utc_now(); json_write(output / 'state.json', state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--prompts', type=Path, required=True)
    parser.add_argument('--scoring', type=Path, required=True)
    parser.add_argument('--accuracy-plan', type=Path, required=True, help='Existing full164 AccuracyPlan for dataset identity/method provenance')
    parser.add_argument('--sandbox-image', required=True)
    parser.add_argument('--qualification', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    catalog = Catalog(args.root); catalog.load()
    with lease(catalog.root):
        state = execute(catalog, load_snapshot(catalog, args.plan), args.baseline, args.prompts,
                        args.scoring, args.sandbox_image, args.qualification, args.out, args.accuracy_plan)
    print(json.dumps(state, ensure_ascii=False))


if __name__ == '__main__':
    main()
