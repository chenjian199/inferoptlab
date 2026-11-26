"""CPU-only HumanEval scoring; never execute generated code in the host process."""
import hashlib
import json
import subprocess
import uuid

from benchmark.accuracy.code_adapter import assemble


INNER = '''import json, subprocess, sys
p = json.load(sys.stdin)
source = p['code'] + '\\n' + p['test'] + '\\ncheck(' + p['entry_point'] + ')\\n'
source = 'import resource\\nresource.setrlimit(resource.RLIMIT_CPU, (8, 8))\\n' + source + '\\nraise SystemExit(42)\\n'
try:
    r = subprocess.run([sys.executable, '-I', '-S', '-c', source], stdin=subprocess.DEVNULL,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, cwd='/tmp')
    result = {'result': 'passed' if r.returncode == 42 else 'test_failure', 'child_exit': r.returncode}
except subprocess.TimeoutExpired:
    result = {'result': 'program_timeout', 'child_exit': None}
print(json.dumps(result), flush=True)
'''


def execute(payload, image):
    if not image.startswith('sha256:') or len(image) != 71:
        raise ValueError('sandbox requires an immutable local image ID')
    token = uuid.uuid4().hex
    name = 'inferoptlab-score-' + token[:16]
    command = ['docker', 'run', '--rm', '--pull=never', '-i', '--init', '--name', name,
               '--label', 'io.inferoptlab.score=' + token, '--network=none', '--read-only',
               '--user=65534:65534', '--cap-drop=ALL', '--security-opt=no-new-privileges',
               '--pids-limit=32', '--memory=512m', '--memory-swap=512m', '--cpus=1',
               '--ulimit', 'nofile=64:64', '--tmpfs', '/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777',
               '-e', 'PYTHONDONTWRITEBYTECODE=1', '-e', 'OMP_NUM_THREADS=1',
               '--entrypoint', 'python3', image, '-I', '-S', '-c', INNER]
    try:
        r = subprocess.run(command, input=json.dumps(payload), text=True, capture_output=True, timeout=45)
        if r.returncode:
            return dict(result='infrastructure_error', diagnostic=r.stderr[-2000:])
        value = json.loads(r.stdout)
        if value.get('result') not in {'passed', 'test_failure', 'program_timeout'}:
            raise ValueError('invalid sandbox response')
        return value
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return dict(result='infrastructure_error', diagnostic=str(exc))
    finally:
        # Only a sandbox carrying this invocation's ownership label is removable.
        r = subprocess.run(['docker', 'inspect', name], capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            info = json.loads(r.stdout)[0]
            if info['Config']['Labels'].get('io.inferoptlab.score') == token:
                subprocess.run(['docker', 'rm', '-f', info['Id']], capture_output=True, timeout=20, check=True)


def score(row, output, image):
    try:
        code, mode = assemble(row['prompt'], output['text'], row['entry_point'])
    except (ValueError, SyntaxError, IndentationError) as exc:
        return dict(task_id=row['task_id'], passed=False, result='parse_failure',
                    diagnostic=type(exc).__name__, truncated=output.get('finish_reason') == 'length')
    result = execute(dict(code=code, test=row['test'], entry_point=row['entry_point']), image)
    return dict(result, task_id=row['task_id'], passed=result['result'] == 'passed',
                adapter_mode=mode, submitted_code=code,
                submitted_code_sha256=hashlib.sha256(code.encode()).hexdigest(),
                truncated=output.get('finish_reason') == 'length')


def selftest(image):
    tests = [
        ('positive', 'def f(): return 1', 'def check(f): assert f() == 1', {'passed'}),
        ('negative', 'def f(): return 0', 'def check(f): assert f() == 1', {'test_failure'}),
        ('loop', 'def f():\n while True: pass', 'def check(f): f()', {'test_failure', 'program_timeout'}),
        ('early_exit', 'import os\nos._exit(0)\ndef f(): pass', 'def check(f): f()', {'test_failure'}),
        ('isolation', '''import os, socket
def f():
 assert os.geteuid() == 65534
 assert not os.path.exists('/dev/dri')
 assert not os.path.exists('/dev/mxcd')
 assert not os.path.exists('/var/run/docker.sock')
 assert 'NoNewPrivs:\\t1' in open('/proc/self/status').read()
 assert 'Seccomp:\\t2' in open('/proc/self/status').read()
 try: open('/root/probe', 'w')
 except OSError: pass
 else: raise AssertionError('writable root')
 try: socket.create_connection(('1.1.1.1', 443), timeout=1)
 except OSError: pass
 else: raise AssertionError('network available')
''', 'def check(f): f()', {'passed'}),
    ]
    results = []
    for name, code, test, expected in tests:
        result = execute(dict(code=code, test=test, entry_point='f'), image)
        results.append(dict(name=name, **result, ok=result['result'] in expected))
    return dict(passed=all(r['ok'] for r in results), checks=results,
                scope='Non-adversarial HumanEval task scoring, not a proof against intentional test-harness evasion.')
