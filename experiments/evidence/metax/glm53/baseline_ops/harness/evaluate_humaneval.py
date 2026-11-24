"""CPU-only, per-task Docker isolation. No generated code executes on the host."""
import argparse
import hashlib
import json
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from code_adapter import assemble, VERSION

ROOT = Path('/home/metax/glm53-baseline-ops')
IMAGE = 'sha256:96bbee871d4ea038b123276eacd65f77825b093b9255157938e0b1628e121f0b'
INNER = '''import json,sys,subprocess,resource,os
payload=json.load(sys.stdin)
source=payload['code']+'\\n'+payload['test']+'\\ncheck('+payload['entry_point']+')\\n'
wrapped='import resource\\nresource.setrlimit(resource.RLIMIT_CPU,(8,8))\\n'+source+'\\nraise SystemExit(42)\\n'
try:
 p=subprocess.run([sys.executable,'-I','-S','-c',wrapped],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10,cwd='/tmp')
 result={'result':'passed' if p.returncode==42 else 'test_failure','child_exit':p.returncode}
except subprocess.TimeoutExpired:
 result={'result':'program_timeout','child_exit':None}
print(json.dumps(result),flush=True)
'''


def sandbox(payload):
    name = 'glm53-heval-' + uuid.uuid4().hex[:16]
    args = ['docker','run','--rm','-i','--init','--name',name,
            '--label','com.codex.task=glm53-baseline-ops-score',
            '--network=none','--read-only','--user=65534:65534','--cap-drop=ALL',
            '--security-opt=no-new-privileges','--pids-limit=32','--memory=512m',
            '--memory-swap=512m','--cpus=1','--ulimit','nofile=64:64',
            '--tmpfs','/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777',
            '--env','PYTHONDONTWRITEBYTECODE=1','--env','OMP_NUM_THREADS=1',
            '--entrypoint','python3',IMAGE,'-I','-S','-c',INNER]
    started = time.monotonic()
    try:
        p = subprocess.run(args, input=json.dumps(payload), capture_output=True, text=True, timeout=45)
        if p.returncode != 0:
            return dict(result='infrastructure_error', docker_exit=p.returncode,
                        diagnostic=p.stderr[-1200:], seconds=time.monotonic()-started)
        result = json.loads(p.stdout)
        assert result['result'] in {'passed','test_failure','program_timeout'}
        return dict(result, seconds=time.monotonic()-started)
    except subprocess.TimeoutExpired:
        return dict(result='infrastructure_error', diagnostic='outer_container_deadline',seconds=time.monotonic()-started)
    except (ValueError, AssertionError) as exc:
        return dict(result='infrastructure_error', diagnostic=type(exc).__name__,seconds=time.monotonic()-started)
    finally:
        # Only this invocation's uniquely named sandbox; never task/GPU containers.
        subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=20)


def evaluate(row, output):
    try:
        code, mode = assemble(row['prompt'], output['text'], row['entry_point'])
    except (ValueError, SyntaxError, IndentationError) as exc:
        return dict(task_id=row['task_id'],result='parse_failure',diagnostic=type(exc).__name__,
                    truncated=output.get('finish_reason')=='length',passed=False)
    result = sandbox(dict(code=code,test=row['test'],entry_point=row['entry_point']))
    return dict(result,task_id=row['task_id'],passed=result['result']=='passed',adapter_mode=mode,
                submitted_code_sha256=hashlib.sha256(code.encode()).hexdigest(),
                submitted_code=code,truncated=output.get('finish_reason')=='length')


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--canonical',action='store_true')
    parser.add_argument('--selftest',action='store_true')
    args=parser.parse_args()
    run=args.run.resolve()
    assert run.is_relative_to(ROOT/'runs')
    run.mkdir(exist_ok=True)
    target=run/'correctness.jsonl'
    if target.exists():raise FileExistsError('Refusing to overwrite score results')
    rows=read_jsonl(ROOT/'scoring/scoring.jsonl')
    if args.canonical:
        outputs={r['task_id']:dict(text=r['canonical_solution'],finish_reason='canonical') for r in rows}
    else:
        samples=read_jsonl(run/'generations.jsonl')
        outputs={r['task_id']:r for r in samples}
        assert len(outputs)==len(samples),'duplicate generated IDs'
        expected=json.loads((run/'generation_manifest.json').read_text())['task_ids']
        assert set(outputs)==set(expected),'missing/extra generated IDs'
        rows=[r for r in rows if r['task_id'] in outputs]
        assert len(rows)==len(expected)
    results=[]
    with target.open('x') as stream, ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda r:evaluate(r,outputs[r['task_id']]),rows):
            stream.write(json.dumps(result,ensure_ascii=False)+'\n');stream.flush()
            results.append(result)
            print(json.dumps(dict(scored=len(results),task_id=result['task_id'],result=result['result'])),flush=True)
    infra=[r for r in results if r['result']=='infrastructure_error']
    summary=dict(status='incomplete' if infra else 'complete',tasks=len(results),passed=sum(r['passed'] for r in results),
                 pass_at_1=None if infra else sum(r['passed'] for r in results)/len(results),
                 failures_by_type={kind:sum(r['result']==kind for r in results) for kind in sorted({r['result'] for r in results})},
                 truncated=sum(r['truncated'] for r in results),adapter_version=VERSION,
                 evaluator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 adapter_sha256=hashlib.sha256(Path(__file__).with_name('code_adapter.py').read_bytes()).hexdigest(),
                 sandbox_image=IMAGE,canonical=args.canonical,
                 scope='Original HumanEval tests; one generation per task; local chat-adapted protocol. No HumanEval+ tests.')
    if args.selftest:
        probes=[('assertion',dict(code='def f(): return 0',test='def check(f): assert f()==1',entry_point='f'),'test_failure'),
                ('infinite_loop',dict(code='def f():\n while True: pass',test='def check(f): f()',entry_point='f'),'test_failure'),
                ('premature_exit',dict(code='import os\nos._exit(0)\ndef f(): pass',test='def check(f): pass',entry_point='f'),'test_failure'),
                ('isolation',dict(code='import os,socket\ndef f():\n assert os.geteuid()==65534\n assert not os.path.exists("/dev/dri")\n assert not os.path.exists("/work/src")\n assert not os.path.exists("/var/run/docker.sock")\n assert "NoNewPrivs:\\t1" in open("/proc/self/status").read()\n assert "Seccomp:\\t2" in open("/proc/self/status").read()\n try:\n  open("/root/probe","w")\n except OSError: pass\n else: raise AssertionError("writable root")\n try:\n  socket.create_connection(("1.1.1.1",443),timeout=1)\n except OSError: pass\n else: raise AssertionError("network allowed")',test='def check(f): f()',entry_point='f'),'passed')]
        checks=[]
        for name,payload,expected in probes:
            result=sandbox(payload)
            checks.append(dict(name=name,expected=expected,**result,ok=result['result']==expected or (name=='infinite_loop' and result['result']=='program_timeout')))
        summary['selftests']=checks
        summary['selftests_passed']=all(r['ok'] for r in checks)
    (run/'score_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary),flush=True)
    assert not infra
    if args.canonical:assert summary['passed']==164
    if args.selftest:assert summary['selftests_passed']


if __name__=='__main__':main()
