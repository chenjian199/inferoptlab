"""Run startup and functional prerequisites, restoring the specified owned service.

No performance scan is started by this command. Run on the serving Linux host.
"""
import argparse
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.specs import Catalog, SpecError
from benchmark.common.io import json_write, utc_now
from benchmark.load.cli import load_snapshot
from benchmark.load.qualification import qualify
from benchmark.load.runner import lease
from benchmark.load.adapters.vllm import docker
from benchmark.load.adapters.sglang import wait_ready
from benchmark.accuracy.live import execute


def rank_records(log):
    # Launcher pipes can join adjacent JSON records on one line.
    rows = []
    decoder = json.JSONDecoder()
    for match in re.finditer(r'\{"rank"\s*:', log):
        try:
            value, _ = decoder.raw_decode(log[match.start():])
            rows.append(value)
        except ValueError:
            continue
    return rows


def hardware_sanity(image, output):
    token = uuid.uuid4().hex
    name = 'inferoptlab-health-' + token[:12]
    probe = ROOT / 'tools/hardware/probes/collective_health.py'
    command = ['docker', 'run', '--rm', '--pull=never', '--name', name,
               '--label', 'io.inferoptlab.health=' + token, '--network=host', '--shm-size=1g',
               '--device=/dev/mxcd', '--device=/dev/dri', '--ulimit', 'memlock=-1:-1',
               '-e', 'MACA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7', '-e', 'OMP_NUM_THREADS=1',
               '--mount', f'type=bind,source={probe},target=/probe.py,readonly',
               '--entrypoint', 'python3', image, '-m', 'torch.distributed.run',
               '--standalone', '--nnodes=1', '--nproc-per-node=8', '/probe.py']
    json_write(output / 'hardware-command.json', command)
    try:
        with (output / 'hardware-sanity.log').open('x', encoding='utf-8') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=300)
        rows = rank_records((output / 'hardware-sanity.log').read_text())
        passed = result.returncode == 0 and len(rows) == 8 and {r['rank'] for r in rows} == set(range(8)) and all(r['status'] == 'passed' for r in rows)
        json_write(output / 'hardware-sanity.json', dict(passed=passed, ranks=rows, returncode=result.returncode,
                   scope='Deterministic small compute/device-copy and 4KiB/4MiB all-reduce/all-gather/reduce-scatter; not exhaustive hardware certification.'))
        if not passed:
            raise SpecError('eight-rank hardware sanity failed; inspect hardware-sanity.log')
    finally:
        info = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True, timeout=20)
        if info.returncode == 0:
            container = json.loads(info.stdout)[0]
            if container['Config']['Labels'].get('io.inferoptlab.health') == token:
                docker('rm', '-f', container['Id'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'baseline', 'accuracy-plan', 'prompts', 'scoring', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--sandbox-image', required=True)
    parser.add_argument('--suspend-container', required=True)
    parser.add_argument('--expected-task-label', required=True)
    args = parser.parse_args()
    os.environ['PATH'] = '/opt/mxdriver/bin:/opt/maca/bin:' + os.environ['PATH']
    catalog = Catalog(ROOT); catalog.load()
    snapshot = load_snapshot(catalog, args.plan)
    if snapshot['execution_issues']:
        raise SpecError('; '.join(snapshot['execution_issues']))
    output = args.out.resolve()
    if not output.is_relative_to(ROOT / 'experiments'):
        raise SpecError('preflight output must be inside experiments/')
    output.mkdir(parents=True, exist_ok=False)
    state = dict(status='starting', started_at=utc_now(), performance_scan_started=False,
                 original_restored=False, error=None)
    def save():
        json_write(output / 'state.json', state)
        print(json.dumps(state, ensure_ascii=False), flush=True)
    def terminate(signum, frame):
        raise KeyboardInterrupt('preflight termination requested')
    signal.signal(signal.SIGTERM, terminate)
    original = None
    stopped = False
    with lease(ROOT):
        try:
            original = json.loads(docker('inspect', args.suspend_container).stdout)[0]
            if original['Config'].get('Labels', {}).get('io.inferoptlab.task') != args.expected_task_label:
                raise SpecError('specified service ownership label does not match')
            if not original['State']['Running']:
                raise SpecError('specified service is not running; inspect host state first')
            command = original['Config']['Cmd']
            port = int(command[command.index('--port') + 1])
            served_model = command[command.index('--served-model-name') + 1]
            url = 'http://127.0.0.1:' + str(port)
            with urlopen(url + '/metrics', timeout=15) as response:
                metrics = response.read().decode()
            running = [line for line in metrics.splitlines() if line.startswith(('vllm:num_requests_running', 'vllm:num_requests_waiting'))]
            if not running or any(float(line.split()[1]) != 0 for line in running):
                raise SpecError('existing service has active/queued requests or occupancy is unknown')
            json_write(output / 'original-service.json', dict(container_id=original['Id'], image=original['Image'],
                       command=command, started_at=original['State']['StartedAt'], request_metrics=running))
            docker('image', 'inspect', args.sandbox_image)
            state['status'] = 'suspending_owned_service'; save()
            # Record intent before stop so cleanup also handles a client-side timeout.
            stopped = True
            docker('stop', '--time', '20', original['Id'])
            state['status'] = 'hardware_sanity'; save()
            hardware_sanity(original['Image'], output)
            state['status'] = 'qualifying_deployments'; save()
            receipt = qualify(catalog, snapshot, output / 'startup')
            if any(row['status'] != 'passed' for row in receipt['deployments']):
                raise SpecError('startup qualification failed; no functional/performance scan started')
            state['status'] = 'functional_regression'; save()
            result = execute(catalog, snapshot, args.baseline, args.prompts, args.scoring,
                             args.sandbox_image, output / 'startup/qualification.json',
                             output / 'functional', args.accuracy_plan)
            state.update(status='functional_complete_pending_numerical_acceptance',
                         comparisons=result.get('comparisons'), release_accepted=False)
        except BaseException as exc:
            state.update(status='failed', error=str(exc)); raise
        finally:
            try:
                if stopped:
                    current = json.loads(docker('inspect', original['Id']).stdout)[0]
                    if current['Config'].get('Labels', {}).get('io.inferoptlab.task') != args.expected_task_label:
                        raise SpecError('original service ownership changed; refusing restoration')
                    docker('start', original['Id'])
                    wait_ready(dict(url=url, served_model=served_model), time.monotonic() + 900, None)
                    state['original_restored'] = True
            except BaseException as exc:
                state['restoration_error'] = str(exc)
                raise
            finally:
                state['finished_at'] = utc_now(); save()


if __name__ == '__main__':
    main()
