"""Offline integrity and completeness checks for the frozen HumanEval v1 baseline."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABEL = '20261123_humaneval_v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rows(path):
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    mapped = {row['task_id']: row for row in records}
    require(len(mapped) == len(records), f'Duplicate IDs: {path}')
    return mapped


def normalized_containers(value):
    """Docker inspect may reorder mount arrays; compare every mount field."""
    result = json.loads(json.dumps(value))
    for container in result.values():
        container['Mounts'].sort(key=lambda mount: json.dumps(mount, sort_keys=True))
    return result


def main():
    evidence = ROOT / 'evidence/humaneval_v1'
    frozen = read(ROOT / 'configs/humaneval_regression.frozen.json')
    dataset_path = ROOT / 'datasets/humaneval/manifest.json'
    dataset = read(dataset_path)
    require(sha(dataset_path) == frozen['dataset_manifest_sha256'], 'Dataset manifest changed')
    require(dataset['revision'] == frozen['dataset_revision'], 'Dataset revision changed')
    for entry in dataset['raw_files'] + dataset['prepared_files']:
        require(sha(ROOT / entry['path']) == entry['sha256'], 'Dataset file changed: ' + entry['path'])
    prepared = ROOT / 'datasets/prepared' / dataset['revision']
    require(sha(prepared / 'prompts.jsonl') == frozen['generation_input_sha256'], 'Prompts changed')
    require(sha(prepared / 'scoring.jsonl') == frozen['scoring_input_sha256'], 'Tests changed')
    prompts = rows(prepared / 'prompts.jsonl')
    require(all(set(row) == {'task_id', 'prompt'} for row in prompts.values()), 'Scoring fields leaked into prompts')
    expected = {f'HumanEval/{i}' for i in range(164)}
    require(set(prompts) == expected, 'Wrong full task IDs')
    selection = read(prepared / 'selection.json')
    require(set(selection['all']) == expected and len(selection['all']) == 164, 'Selection mismatch')
    smoke = sorted(expected, key=lambda tid: (hashlib.sha256(('glm53-humaneval-smoke-v1:' + tid).encode()).hexdigest(), tid))[:32]
    require(selection['smoke32'] == smoke == dataset['smoke_task_ids'], 'Smoke selection changed')
    for name, digest in frozen['harness_sha256'].items():
        require(sha(evidence / 'harness-executed' / name) == digest, 'Executed harness changed: ' + name)
    require(sha(evidence / 'protocol-v1.executed.json') == frozen['protocol_sha256'], 'Protocol changed')
    require(sha(evidence / 'prompt_manifest.json') == frozen['prompt_manifest_sha256'], 'Tokenized prompts changed')
    canonical = read(ROOT / 'runs/canonical_v1/score_summary.json')
    canonical_rows = rows(ROOT / 'runs/canonical_v1/correctness.jsonl')
    require(set(canonical_rows) == expected and all(row['passed'] for row in canonical_rows.values()), 'Canonical failure')
    require(canonical['status'] == 'complete' and canonical['passed'] == 164 and canonical['selftests_passed'], 'Sandbox not validated')
    results = {}
    for phase, ids in [('smoke32', smoke), ('full164', selection['all'])]:
        folder = ROOT / 'runs' / (LABEL + '_' + phase)
        generation = read(folder / 'generation_manifest.json')
        outputs = rows(folder / 'generations.jsonl')
        scores = rows(folder / 'correctness.jsonl')
        summary = read(folder / 'score_summary.json')
        require(generation['status'] == summary['status'] == 'complete', 'Incomplete phase: ' + phase)
        require(generation['task_ids'] == ids and generation['completed_tasks'] == len(ids), 'Task manifest mismatch')
        require(set(outputs) == set(scores) == set(ids), 'Missing/extra tasks: ' + phase)
        require(sha(folder / 'generations.jsonl') == generation['generations_sha256'], 'Generated data changed')
        require(generation['protocol_sha256'] == frozen['protocol_sha256'], 'Wrong run protocol')
        require(generation['prompt_manifest_sha256'] == frozen['prompt_manifest_sha256'], 'Wrong run prompt manifest')
        require(generation['harness_sha256'] == frozen['harness_sha256']['generate_humaneval.py'], 'Wrong generator')
        require(summary['evaluator_sha256'] == frozen['harness_sha256']['evaluate_humaneval.py'], 'Wrong evaluator')
        require(summary['adapter_sha256'] == frozen['harness_sha256']['code_adapter.py'], 'Wrong adapter')
        require(summary['sandbox_image'] == frozen['scoring']['image_id'], 'Wrong sandbox image')
        require(not any(r['result'] == 'infrastructure_error' for r in scores.values()), 'Infrastructure error')
        require(all(r['passed'] == (r['result'] == 'passed') for r in scores.values()), 'Inconsistent scoring flags')
        passed = sum(r['passed'] for r in scores.values())
        require(summary['tasks'] == len(ids) and summary['passed'] == passed, 'Wrong summary count')
        require(summary['pass_at_1'] == passed / len(ids), 'Wrong pass@1')
        require(summary['failures_by_type'] == dict(Counter(r['result'] for r in scores.values())), 'Wrong failure counts')
        for tid, output in outputs.items():
            require(output['output_tokens'] == len(output['output_token_ids']), 'Wrong output token count: ' + tid)
            require(scores[tid]['truncated'] == (output['finish_reason'] == 'length'), 'Wrong truncation flag')
            if 'submitted_code' in scores[tid]:
                require(hashlib.sha256(scores[tid]['submitted_code'].encode()).hexdigest() == scores[tid]['submitted_code_sha256'], 'Submitted code changed')
        results[phase] = {'tasks': len(ids), 'passed': passed, 'pass_at_1': passed / len(ids)}
    require(read(evidence / 'generation_process.json')['exit_code'] == 0, 'Generation process failed')
    require(normalized_containers(read(evidence / 'preserved_before.json')) == normalized_containers(read(evidence / 'preserved_after.json')), 'Original container identity/state/mounts changed')
    archive = read(ROOT / 'artifact_manifest.json')
    for entry in archive['files']:
        path = (ROOT / entry['path']).resolve()
        require(path.is_relative_to(ROOT.resolve()), 'Archive path escapes root')
        require(sha(path) == entry['sha256'], 'Archive hash mismatch: ' + entry['path'])
    print(json.dumps({'status': 'passed', 'archive_files_checked': len(archive['files']),
                      'results': results, 'scope': 'Offline integrity and completeness; no inference or candidate code execution.'}, indent=2))


if __name__ == '__main__':
    main()
