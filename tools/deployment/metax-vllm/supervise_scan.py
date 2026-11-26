"""Host-side periodic inspection and bounded recovery of an immutable benchmark.

Run detached on the benchmark host. SSH connectivity is not part of the control
loop. A repeated failure is retained for diagnosis, never counted as completion.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.specs import Catalog, SpecError, write
from benchmark.common.io import json_write, utc_now
from benchmark.load.cli import load_snapshot
from benchmark.load.planner import embedded_catalog
from benchmark.load.qualification import verify_receipt
from benchmark.load.adapters.sglang import wait_ready


def docker(*args):
    return subprocess.run(['docker', *args], check=True, capture_output=True, text=True, timeout=90).stdout


def progress(batch):
    if batch is None or not (batch/'batch.json').exists():
        return dict(completed=0, accounted=0, counts={}, current_trial=None)
    value = json.loads((batch/'batch.json').read_text())
    counts = Counter(row['status'] for row in value['runs'])
    from benchmark.load.checkpoint import terminal
    result = dict(completed=counts['completed'], counts=dict(counts), current_trial=value.get('current_trial'),
                  batch_status=value['status'], preparing_fixture=value.get('preparing_fixture'))
    result['accounted']=sum(terminal(row,value) for row in value['runs'])
    completed = [r for r in value['runs'] if r['status']=='completed']
    if completed:
        last = completed[-1]
        result['last_completed'] = last
        path = batch/last['directory']/'decode.json'
        if path.exists():
            result['last_decode'] = json.loads(path.read_text())
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    startup = parser.add_mutually_exclusive_group(required=True)
    startup.add_argument('--qualification', type=Path)
    startup.add_argument('--qualify-before-run', action='store_true',
                         help='Run startup and exact-length API probes before this new batch')
    parser.add_argument('--client-root', type=Path, required=True)
    parser.add_argument('--client-image', required=True)
    parser.add_argument('--state-dir', type=Path, required=True)
    parser.add_argument('--resume', type=Path)
    parser.add_argument('--skip-failed-configurations', action='store_true')
    parser.add_argument('--interval', type=int, default=60)
    parser.add_argument('--max-stalled-attempts', type=int, default=3)
    parser.add_argument('--restore-service', help='Owned service to suspend if idle and restore on exit')
    parser.add_argument('--service-label', help='Expected io.inferoptlab.task label')
    args = parser.parse_args(argv)
    if args.qualify_before_run and args.resume:
        raise SpecError('resume requires the existing qualification receipt')
    if args.interval < 1 or args.max_stalled_attempts < 1:
        raise SpecError('interval and retry limit must be positive')
    out = args.state_dir.resolve()
    if not out.is_relative_to(ROOT/'experiments'):
        raise SpecError('state directory must be inside experiments')
    if (ROOT/'experiments/runs/benchmark/.execution.lock').exists():
        raise SpecError('an execution lease exists; inspect the owner before launching')
    catalog = Catalog(ROOT); catalog.load()
    snapshot = load_snapshot(catalog, args.plan)
    if args.qualification:
        verify_receipt(embedded_catalog(catalog, snapshot), snapshot, args.qualification,allow_failed=args.skip_failed_configurations)
    if snapshot['execution_issues']:
        raise SpecError('plan execution is blocked')
    out.mkdir(parents=True, exist_ok=False)
    write(out/'resolved.yaml', snapshot)
    batch = args.resume.resolve() if args.resume else None
    if batch:
        from benchmark.load.checkpoint import load
        load(batch, snapshot)
    state = dict(status='starting', pid=os.getpid(), started_at=utc_now(), total=len(snapshot['trials']),
                 plan_sha256=snapshot['content_sha256'], interval_s=args.interval,
                 release_accepted=False, attempts=[], original_restored=False)
    original = None
    child = None
    client_name = None

    def save():
        state.update(updated_at=utc_now(), batch=str(batch) if batch else None, progress=progress(batch))
        json_write(out/'state.json', state)
        with (out/'checks.jsonl').open('a') as stream:
            stream.write(json.dumps(dict(at=state['updated_at'], status=state['status'],
                         batch=state['batch'], progress=state['progress']))+'\n')
        print(json.dumps(dict(at=state['updated_at'],status=state['status'],progress=state['progress'])),flush=True)

    try:
        save()
        if args.restore_service:
            if not args.service_label:
                raise SpecError('--restore-service requires --service-label')
            original = json.loads(docker('inspect', args.restore_service))[0]
            if original['Config'].get('Labels', {}).get('io.inferoptlab.task') != args.service_label:
                original = None
                raise SpecError('service ownership mismatch')
            cmd = original['Config']['Cmd']
            serving = dict(url='http://127.0.0.1:'+cmd[cmd.index('--port')+1],
                           served_model=cmd[cmd.index('--served-model-name')+1])
            if original['State']['Running']:
                with urlopen(serving['url']+'/metrics',timeout=15) as response:
                    metrics=response.read().decode()
                occupancy=[l for l in metrics.splitlines() if l.startswith(('vllm:num_requests_running','vllm:num_requests_waiting'))]
                if not occupancy or any(float(l.split()[1])!=0 for l in occupancy):
                    original=None
                    raise SpecError('service has active requests or unknown occupancy')
                docker('stop','--time','20',original['Id'])
            json_write(out/'original-service.json',dict(id=original['Id'],serving=serving))
        if args.qualify_before_run:
            from benchmark.load.qualification import qualify
            from benchmark.load.runner import lease
            state['status']='qualifying'; save()
            with lease(ROOT):
                qualify(catalog,snapshot,out/'startup')
            args.qualification=out/'startup/qualification.json'
            verify_receipt(embedded_catalog(catalog,snapshot),snapshot,args.qualification,allow_failed=args.skip_failed_configurations)
            state['qualification']=str(args.qualification)
        stalled=0
        while stalled < args.max_stalled_attempts:
            if (ROOT/'experiments/runs/benchmark/.execution.lock').exists():
                raise SpecError('execution lease remains after exit; owner needs inspection')
            number=len(state['attempts'])+1
            attempt_dir=out/f'attempt-{number:03d}'
            attempt_dir.mkdir()
            output_root=batch.parent if batch else attempt_dir/'batches'
            client_name='inferoptlab-client-'+uuid.uuid4().hex[:12]
            command=[sys.executable,'-u',str(ROOT/'tools/deployment/metax-vllm/run_scan.py'),
                     '--client-root',str(args.client_root.resolve()),'--client-image',args.client_image,
                     '--client-name',client_name,'run',str(out/'resolved.yaml'),
                     '--qualification',str(args.qualification.resolve()),'--out',str(output_root)]
            if batch:
                command+=['--resume',str(batch)]
            if args.skip_failed_configurations:
                command+=['--skip-failed-configurations']
            json_write(attempt_dir/'command.json',command)
            attempt=dict(number=number,started_at=utc_now(),client_name=client_name)
            state['attempts'].append(attempt)
            before=progress(batch)['completed']
            state['status']='running'
            with (attempt_dir/'runner.log').open('x') as log:
                child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                attempt['pid']=child.pid
                while True:
                    if batch is None:
                        found=list(output_root.glob('batch-*/batch.json'))
                        if len(found)>1:
                            raise SpecError('ambiguous batch ownership')
                        if found:
                            batch=found[0].parent
                    save()
                    try:
                        code=child.wait(timeout=args.interval)
                        break
                    except subprocess.TimeoutExpired:
                        pass
            attempt.update(finished_at=utc_now(),returncode=code)
            if batch is None:
                found=list(output_root.glob('batch-*/batch.json'))
                if len(found)==1:
                    batch=found[0].parent
            observed=progress(batch)
            skipped=observed['counts'].get('skipped_by_user',0)
            if code==0 and observed['accounted']==state['total']:
                if observed['completed']!=state['total']:
                    from benchmark.load.checkpoint import load
                    load(batch,snapshot)
                state['status']=observed['batch_status']; save()
                return 0
            stalled=stalled+1 if observed['completed']==before else 0
            state.update(status='retry_wait',stalled_attempts=stalled); save()
            if stalled < args.max_stalled_attempts:
                time.sleep(args.interval)
        state['status']='needs_repair'; save()
        return 1
    except BaseException as exc:
        state.update(status='needs_repair',error=repr(exc))
        raise
    finally:
        if child is not None and child.poll() is None:
            info=json.loads(docker('inspect',client_name))[0]
            if info['Config'].get('Labels',{}).get('io.inferoptlab.role')!='benchmark-client':
                raise SpecError('refusing to interrupt client without ownership label')
            docker('kill','--signal=INT',info['Id'])
            child.wait(timeout=240)
        try:
            if original:
                if (ROOT/'experiments/runs/benchmark/.execution.lock').exists():
                    raise SpecError('execution lease remains; defer service restoration until owner is inspected')
                current=json.loads(docker('inspect',original['Id']))[0]
                if current['Config'].get('Labels',{}).get('io.inferoptlab.task')!=args.service_label:
                    raise SpecError('service ownership changed before restoration')
                docker('start',original['Id'])
                wait_ready(serving,time.monotonic()+900,None)
                state['original_restored']=True
        except BaseException as exc:
            state['restoration_error']=repr(exc)
            raise
        finally:
            state['finished_at']=utc_now(); save()


if __name__=='__main__':
    raise SystemExit(main())
