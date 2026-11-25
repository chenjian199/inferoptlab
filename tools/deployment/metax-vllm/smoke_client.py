"""Diagnostic AIPerf replay using the project's fixture and CLI adapters.

This is a bounded deployment check, not a frozen BenchmarkPlan or SLA result.
Run inside the independent AIPerf client environment with this repository on
PYTHONPATH and the model/tokenizer mounted read-only.
"""
import argparse
import json
import subprocess
from pathlib import Path

from benchmark.load import dataset
from benchmark.load.adapters import aiperf

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tokenizer', required=True)
    parser.add_argument('--url', default='http://127.0.0.1:18081')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    executable = aiperf.check_installation('0.12.0')
    deployment = {'serving': {'served_model': 'glm53-flash', 'url': args.url, 'tokenizer_path': args.tokenizer}}
    protocol = {'execution': {'warmup_request_count': 1, 'timeout_s': 120}}
    plan = {'aiperf': {'server_metrics': [], 'gpu_telemetry': []}}
    results = []
    for label, input_tokens, output_tokens in [('prefill-smoke', 128, 1), ('short-smoke', 128, 32), ('long-smoke', 1024, 32)]:
        workload = {'id': label, 'input': {'tokens': input_tokens}, 'output': {'tokens': output_tokens},
                    'requests': {'count': 4, 'seed': 20261124, 'request_set_sha256': None}}
        root = args.output / label
        root.mkdir()
        (root / 'workload.json').write_text(json.dumps(workload, indent=2))
        fixture = root / 'dataset'
        dataset.prepare(workload, protocol, args.tokenizer, fixture)
        dataset.verify(workload, protocol, args.tokenizer, fixture)
        for warmup in (True, False):
            phase = 'warmup' if warmup else 'profile'
            artifact = root / phase
            command = aiperf.command(executable, plan, deployment, workload, protocol, 1, fixture, artifact, warmup=warmup)
            (root / (phase + '-command.json')).write_text(json.dumps(command, indent=2))
            with (root / (phase + '.log')).open('wb') as stream:
                completed = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, timeout=300)
            assert completed.returncode == 0, f'{label}/{phase}: AIPerf exited {completed.returncode}'
            issues = aiperf.telemetry_issues(artifact, 'none')
            assert not issues, issues
            result = json.loads((artifact / 'profile_export_aiperf.json').read_text())
            expected_count = 1 if warmup else 4
            assert not result.get('error_summary'), result.get('error_summary')
            assert result['request_count']['avg'] == expected_count, result['request_count']
            assert result['request_latency']['count'] == expected_count
            for metric, expected in [('input_sequence_length', input_tokens), ('output_sequence_length', output_tokens)]:
                assert result[metric]['min'] == result[metric]['max'] == expected, (metric, result[metric])
            assert result['time_to_first_token']['count'] == expected_count
            assert result['time_to_first_token']['min'] > 0
            (root / (phase + '-summary.json')).write_text(json.dumps(result, indent=2))
            print('AIPERF_EXPORTED', label, phase, flush=True)
        results.append({'scenario': label, 'concurrency': 1, 'request_count': 4,
                        'request_multiplier': 4, 'input_tokens': input_tokens, 'output_tokens': output_tokens})
    (args.output / 'diagnostic-runs.json').write_text(json.dumps({'formal_baseline': False, 'runs': results}, indent=2))

if __name__ == '__main__':
    main()
