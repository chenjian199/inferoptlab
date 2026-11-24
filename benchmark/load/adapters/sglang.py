"""Single-node SGLang launcher and OpenAI-compatible endpoint checks."""
from __future__ import annotations

import json
import os
import socket
import sys
import time
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from tools.specs import SpecError
from benchmark.common import process

RESERVED = {'--model-path','--model','--model-name','--served-model-name','--tokenizer-path','--host','--port',
    '--tp','--tp-size','--tensor-parallel-size','--pp','--pp-size','--pipeline-parallel-size',
    '--ep','--ep-size','--expert-parallel-size','--dp','--dp-size','--data-parallel-size',
    '--chunked-prefill-size','--page-size','--max-running-requests','--disable-radix-cache','--enable-metrics',
    '--stream-interval','--enable-cache-report','--enable-dp-attention','--nnodes','--node-rank','--dist-init-addr','--base-gpu-id','--gpu-id-step'}


def configuration_issues(deployment, runtime):
    issues = []
    serving = deployment['serving']
    if deployment['mode'] != 'aggregated':
        issues.append('v1 managed/attached testing supports aggregated deployment only')
    for field in ('served_model', 'tokenizer_path'):
        if not serving[field] or 'REPLACE_' in serving[field]:
            issues.append(f'serving.{field} must be configured')
    common = runtime['launch_parameters']
    extra = deployment['backend_options']
    if set(common) & set(extra):
        issues.append('runtime launch_parameters conflict with deployment backend_options')
    if RESERVED & (set(common) | set(extra)):
        issues.append('backend options conflict with managed parallelism, cache, streaming or serving flags')
    for option, value in {**common, **extra}.items():
        if not option.startswith('--') or '=' in option or not isinstance(value, (str,int,float,bool)):
            issues.append(f'unsupported backend option: {option}')
    if serving['management'] == 'sglang':
        if not serving['model_path'] or 'REPLACE_' in serving['model_path']:
            issues.append('managed deployment requires model_path')
        parsed = urlparse(serving['url'])
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1','localhost'}:
            issues.append('managed v1 launcher requires a local HTTP endpoint')
        p = deployment['parallelism']
        if p['dp'] != 1:
            issues.append('v1 launcher supports dp=1; multi-replica routing requires another adapter')
        # In this adapter TP groups are nested inside PP stages; EP shares TP ranks.
        if p['tp'] % p['ep']:
            issues.append('single-node adapter requires EP to divide TP')
        if len(deployment['devices']) != p['tp'] * p['pp']:
            issues.append('single-node TP/PP rank map must contain tp * pp distinct devices (EP shares ranks)')
    return issues


def command(deployment, runtime):
    issues = configuration_issues(deployment, runtime)
    if issues:
        raise SpecError('\n'.join(issues))
    s, p = deployment['serving'], deployment['parallelism']
    parsed = urlparse(s['url'])
    args = [sys.executable, '-m', 'sglang.launch_server', '--model-path', s['model_path'],
        '--tokenizer-path', s['tokenizer_path'], '--served-model-name', s['served_model'],
        '--host', '127.0.0.1', '--port', str(parsed.port or 80),
        '--tp-size', str(p['tp']), '--pp-size', str(p['pp']), '--ep-size', str(p['ep']), '--dp-size', str(p['dp']),
        '--enable-metrics', '--stream-interval', '1']
    args += ['--enable-cache-report'] if deployment.get('prefix_cache',False) else ['--disable-radix-cache']
    for name, option in [('chunked_prefill_tokens','--chunked-prefill-size'),('kv_page_tokens','--page-size'),('max_running_requests','--max-running-requests')]:
        if deployment['scheduling'][name] is not None:
            args += [option, str(deployment['scheduling'][name])]
    for option, value in sorted({**runtime['launch_parameters'], **deployment['backend_options']}.items()):
        if isinstance(value, bool):
            if value:
                args.append(option)
        else:
            args += [option, str(value)]
    return args


def get_json(url, timeout=10):
    with urlopen(url, timeout=timeout) as response:
        return json.load(response)


def wait_ready(serving, deadline, owned=None):
    last = 'no readiness response'
    while time.monotonic() < deadline:
        if owned is not None and owned.poll() is not None:
            raise SpecError('SGLang exited before readiness; see server.log')
        try:
            models = get_json(serving['url'].rstrip('/') + '/v1/models', min(5, max(.1, deadline-time.monotonic())))
            if any(item.get('id') == serving['served_model'] for item in models.get('data', [])):
                return models
            last = 'served model is absent from /v1/models'
        except (OSError, ValueError, URLError) as exc:
            last = str(exc)
        time.sleep(min(1, max(0, deadline-time.monotonic())))
    raise SpecError('readiness deadline exceeded: ' + last)


def smoke(serving, timeout=30):
    deadline=time.monotonic()+timeout
    body = dict(model=serving['served_model'], messages=[dict(role='user',content='Reply with one word.')],max_tokens=1,stream=True,temperature=0)
    request = Request(serving['url'].rstrip('/')+'/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=timeout) as response:
        for line in response:
            if time.monotonic()>deadline:
                raise SpecError('smoke response exceeded deadline')
            if line.startswith(b'data:') and line.strip() != b'data: [DONE]':
                event=json.loads(line[5:])
                if event.get('error'):
                    raise SpecError('smoke stream returned an error')
                for choice in event.get('choices',[]):
                    delta=choice.get('delta',{})
                    if delta.get('content') or delta.get('reasoning_content') or delta.get('reasoning'):
                        return
    raise SpecError('smoke request produced no streamed content')


def inspect_server(serving):
    try:
        return get_json(serving['url'].rstrip('/')+'/get_server_info'), []
    except (OSError, ValueError, URLError) as exc:
        return None, ['server configuration unavailable: '+str(exc)]


def verify_server(deployment, info, maximum_context):
    """Observed checks; unknown external configuration never becomes verified."""
    if not isinstance(info,dict):
        return ['cannot verify external parallelism/cache/streaming configuration']
    args=info.get('server_args',info)
    if not isinstance(args,dict):
        return ['server_args is not an object']
    expected={'tp_size':deployment['parallelism']['tp'],'pp_size':deployment['parallelism']['pp'],
        'ep_size':deployment['parallelism']['ep'],'dp_size':deployment['parallelism']['dp'],
        'disable_radix_cache':not deployment.get('prefix_cache',False),'stream_interval':1}
    if deployment.get('prefix_cache',False):
        expected['enable_cache_report']=True
    for key, value in [('chunked_prefill_size',deployment['scheduling']['chunked_prefill_tokens']),('page_size',deployment['scheduling']['kv_page_tokens']),('max_running_requests',deployment['scheduling']['max_running_requests'])]:
        if value is not None:
            expected[key]=value
    issues=[]
    for name,value in expected.items():
        if args.get(name) != value:
            issues.append(f'server {name}: expected {value!r}, observed {args.get(name)!r}')
    context=args.get('context_length')
    if context is not None and context < maximum_context:
        raise SpecError(f'server context_length={context} is below required {maximum_context}; no truncation permitted')
    if context is None:
        issues.append('server context length unavailable')
    return issues


class Deployment:
    def __init__(self, deployment, runtime, log_path):
        self.deployment,self.runtime,self.log_path=deployment,runtime,log_path
        self.process=None
        self.log=None

    def launch(self):
        if self.deployment['serving']['management']=='external':
            return None
        if os.name != 'posix':
            raise SpecError('managed SGLang execution requires Linux; Windows supports planning/reporting')
        parsed=urlparse(self.deployment['serving']['url'])
        with socket.socket() as probe:
            if probe.connect_ex((parsed.hostname,parsed.port or 80))==0:
                raise SpecError('managed endpoint port is occupied; existing service will not be replaced')
        args=command(self.deployment,self.runtime)
        env=os.environ.copy()
        for name in ('CUDA_VISIBLE_DEVICES','HIP_VISIBLE_DEVICES','ROCR_VISIBLE_DEVICES','MACA_VISIBLE_DEVICES'):
            env.pop(name,None)
        env[self.deployment['serving']['device_visibility_env']]=','.join(str(d['visible_index']) for d in sorted(self.deployment['devices'],key=lambda d:d['rank']))
        self.log=self.log_path.open('wb')
        self.process=process.start(args,self.log,env)
        return args

    def close(self):
        try:
            process.stop(self.process)
        finally:
            if self.log:
                self.log.close()
