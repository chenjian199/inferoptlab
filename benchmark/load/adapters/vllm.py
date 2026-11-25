"""vLLM configuration verification and owned single-node Docker deployments."""
from __future__ import annotations
import json
import socket
import subprocess
import uuid
from pathlib import Path
from urllib.parse import urlparse
from tools.specs import SpecError
from . import sglang

RESERVED = sglang.RESERVED | {
    '--tokenizer', '--enable-expert-parallel', '--no-enable-expert-parallel',
    '--enable-prefix-caching', '--no-enable-prefix-caching', '--max-num-seqs',
    '--max-num-batched-tokens', '--block-size', '--max-model-len',
    '--enable-chunked-prefill', '--no-enable-chunked-prefill',
    '--data-parallel-size-local', '--data-parallel-rank', '--data-parallel-start-rank',
    '--data-parallel-hybrid-lb', '--data-parallel-external-lb',
    '--enable-prompt-tokens-details',
}


def configuration_issues(deployment, runtime):
    issues = []
    s, p, scheduling = deployment['serving'], deployment['parallelism'], deployment['scheduling']
    if deployment['mode'] != 'aggregated':
        issues.append('vLLM adapter supports aggregated single-node deployments')
    if s['management'] not in {'external', 'vllm-docker'}:
        issues.append('vLLM requires external or vllm-docker management')
    common, extra = runtime['launch_parameters'], deployment['backend_options']
    if set(common) & set(extra):
        issues.append('runtime launch_parameters conflict with deployment backend_options')
    if RESERVED & (set(common) | set(extra)):
        issues.append('backend options conflict with managed serving/parallelism/scheduling flags')
    for option, value in {**common, **extra}.items():
        if not option.startswith('--') or '=' in option or not isinstance(value, (str, int, float, bool)):
            issues.append(f'unsupported backend option: {option}')
    if scheduling['chunked_prefill_tokens'] is not None:
        issues.append('vLLM requires max_num_batched_tokens, not chunked_prefill_tokens')
    if p['ep'] not in {1, p['tp'] * p['dp']}:
        issues.append('vLLM EP must be disabled (1) or equal TP * DP')
    if len(deployment['devices']) != p['tp'] * p['pp'] * p['dp']:
        issues.append('vLLM allocation must contain TP * PP * DP devices; EP shares ranks')
    if s['management'] == 'vllm-docker':
        parsed = urlparse(s['url'])
        if parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost'}:
            issues.append('owned vLLM requires a local HTTP endpoint')
        for field in ('model_path', 'tokenizer_path', 'served_model'):
            if not s[field] or 'REPLACE_' in s[field]:
                issues.append(f'serving.{field} must be configured')
        if s['model_path'] != s['tokenizer_path']:
            issues.append('owned vLLM requires tokenizer files within model_path')
        if runtime.get('container_identity_kind') != 'docker_image_id' or not runtime.get('container_digest', '').startswith('sha256:'):
            issues.append('owned vLLM requires an immutable local Docker image ID')
        for name in ('max_model_len', 'max_num_batched_tokens', 'max_running_requests', 'enable_chunked_prefill'):
            if scheduling.get(name) is None:
                issues.append(f'owned vLLM requires scheduling.{name}')
    return issues


def server_arguments(deployment, runtime):
    issues = configuration_issues(deployment, runtime)
    if issues:
        raise SpecError('\n'.join(issues))
    s, p, scheduling = deployment['serving'], deployment['parallelism'], deployment['scheduling']
    parsed = urlparse(s['url'])
    args = ['--model', s['model_path'], '--tokenizer', s['tokenizer_path'],
            '--served-model-name', s['served_model'], '--host', '127.0.0.1', '--port', str(parsed.port or 80),
            '--tensor-parallel-size', str(p['tp']), '--pipeline-parallel-size', str(p['pp']),
            '--data-parallel-size', str(p['dp']), '--stream-interval', '1',
            '--enable-prefix-caching' if deployment.get('prefix_cache', False) else '--no-enable-prefix-caching']
    if p['ep'] > 1:
        args += ['--enable-expert-parallel']
    if deployment.get('prefix_cache'):
        args += ['--enable-prompt-tokens-details']
    for name, flag in [('max_model_len', '--max-model-len'), ('max_num_batched_tokens', '--max-num-batched-tokens'),
                       ('max_running_requests', '--max-num-seqs'), ('kv_page_tokens', '--block-size')]:
        if scheduling.get(name) is not None:
            args += [flag, str(scheduling[name])]
    if scheduling.get('enable_chunked_prefill') is not None:
        args += ['--enable-chunked-prefill' if scheduling['enable_chunked_prefill'] else '--no-enable-chunked-prefill']
    for option, value in sorted({**runtime['launch_parameters'], **deployment['backend_options']}.items()):
        if isinstance(value, bool):
            if value:
                args.append(option)
        else:
            args += [option, str(value)]
    return args


def inspect_server(serving):
    try:
        raw = sglang.get_json(serving['url'].rstrip('/') + '/server_info?config_format=json', timeout=45)
        return {'vllm_config': raw.get('vllm_config')}, []
    except (OSError, ValueError) as exc:
        return None, ['server configuration unavailable: ' + str(exc)]


def verify_server(deployment, info, maximum_context):
    config = (info or {}).get('vllm_config')
    if not isinstance(config, dict):
        return ['cannot verify vLLM configuration']
    p, cache = config.get('parallel_config', {}), config.get('cache_config', {})
    scheduler, model = config.get('scheduler_config', {}), config.get('model_config', {})
    declared = deployment['parallelism']
    expected = {'tensor_parallel_size': declared['tp'], 'pipeline_parallel_size': declared['pp'],
                'data_parallel_size': declared['dp'], 'enable_expert_parallel': declared['ep'] > 1}
    issues = []
    for name, value in expected.items():
        if p.get(name) != value:
            issues.append(f'vLLM {name}: expected {value}, observed {p.get(name)}')
    if declared['ep'] > 1 and declared['ep'] != p.get('tensor_parallel_size', 0) * p.get('data_parallel_size', 0):
        issues.append('vLLM expert group size does not match declared EP')
    if cache.get('enable_prefix_caching') is not deployment.get('prefix_cache', False):
        issues.append('vLLM prefix cache differs from deployment')
    if scheduler.get('stream_interval') != 1:
        issues.append('vLLM single-token stream interval is not confirmed')
    for group, key, name in [(cache, 'block_size', 'kv_page_tokens'), (scheduler, 'max_num_seqs', 'max_running_requests'),
                             (scheduler, 'max_num_batched_tokens', 'max_num_batched_tokens'),
                             (scheduler, 'enable_chunked_prefill', 'enable_chunked_prefill'), (model, 'max_model_len', 'max_model_len')]:
        value = deployment['scheduling'].get(name)
        if value is not None and group.get(key) != value:
            issues.append(f'vLLM {key}: expected {value}, observed {group.get(key)}')
    if deployment['scheduling']['chunked_prefill_tokens'] is not None:
        issues.append('vLLM budget cannot be expressed as chunked_prefill_tokens')
    context = model.get('max_model_len')
    if context is None:
        issues.append('vLLM context limit unavailable')
    elif context < maximum_context:
        raise SpecError(f'vLLM context {context} is below required {maximum_context}')
    for flag, group, key, transform in [
        ('--enforce-eager', model, 'enforce_eager', bool),
        ('--gpu-memory-utilization', cache, 'gpu_memory_utilization', float),
        ('--no-async-scheduling', scheduler, 'async_scheduling', lambda v: not v),
        ('--disable-custom-all-reduce', p, 'disable_custom_all_reduce', bool),
        ('--all2all-backend', p, 'all2all_backend', str),
    ]:
        if flag in deployment['backend_options']:
            expected_value = transform(deployment['backend_options'][flag])
            if group.get(key) != expected_value:
                issues.append(f'vLLM {key}: expected {expected_value}, observed {group.get(key)}')
    if deployment['backend_options'].get('--enforce-eager') is False:
        compilation = config.get('compilation_config', {})
        graph_mode = compilation.get('cudagraph_mode')
        if not graph_mode or str(graph_mode).lower() in {'none', 'cudagraphmode.none', '0'} or not compilation.get('cudagraph_capture_sizes'):
            issues.append('graph candidate has no observed active graph mode/capture sizes')
    return issues


def docker(*args, **kwargs):
    return subprocess.run(['docker', *args], check=True, capture_output=True, text=True, timeout=60, **kwargs)


class Deployment:
    def __init__(self, deployment, runtime, log_path):
        self.deployment, self.runtime, self.log_path = deployment, runtime, Path(log_path)
        self.container_id = None
        self.token = uuid.uuid4().hex
        self.process = None

    def launch(self):
        if self.deployment['serving']['management'] == 'external':
            return None
        args = server_arguments(self.deployment, self.runtime)
        s = self.deployment['serving']
        model = Path(s['model_path']).resolve(strict=True)
        parsed = urlparse(s['url'])
        with socket.socket() as probe:
            # TIME_WAIT from the previous owned server is not an active listener.
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind((parsed.hostname, parsed.port or 80))
        image_id = self.runtime['container_digest']
        if json.loads(docker('image', 'inspect', image_id).stdout)[0]['Id'] != image_id:
            raise SpecError('Docker image identity differs from RuntimeSpec')
        cmd = ['run', '-d', '--pull=never', '--name', 'inferoptlab-scan-' + self.token[:12],
               '--label', 'io.inferoptlab.owner=' + self.token, '--network=host', '--shm-size=32g',
               '--ulimit', 'memlock=-1:-1', '--ulimit', 'stack=67108864:67108864',
               '--mount', f'type=bind,source={model},target={model},readonly']
        if s['device_visibility_env'] == 'MACA_VISIBLE_DEVICES':
            cmd += ['--device=/dev/mxcd', '--device=/dev/dri']
        else:
            raise SpecError('Docker device passthrough is currently qualified for MetaX only')
        visible = ','.join(str(d['visible_index']) for d in sorted(self.deployment['devices'], key=lambda d: d['rank']))
        env = dict(self.runtime.get('execution_profile', {}).get('environment', {}))
        env.update({s['device_visibility_env']: visible, 'VLLM_SERVER_DEV_MODE': '1',
                    'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1'})
        for name, value in sorted(env.items()):
            cmd += ['-e', f'{name}={value}']
        if s.get('cache_dir'):
            for suffix, target in [('cache', '/root/.cache'), ('triton', '/root/.triton')]:
                path = Path(s['cache_dir']).resolve() / image_id.split(':')[1] / suffix
                path.mkdir(parents=True, exist_ok=True)
                cmd += ['--mount', f'type=bind,source={path},target={target}']
        cmd += ['--entrypoint', 'python3', image_id, '-m', 'vllm.entrypoints.openai.api_server', *args]
        try:
            self.container_id = docker(*cmd).stdout.strip()
        except subprocess.SubprocessError as exc:
            raise SpecError(f'Docker launch failed: {getattr(exc, "stderr", str(exc))}') from exc
        self.process = self
        return ['docker', *cmd]

    def poll(self):
        state = json.loads(docker('inspect', self.container_id).stdout)[0]['State']
        return None if state['Running'] else state['ExitCode']

    def close(self):
        if not self.container_id:
            return
        info = json.loads(docker('inspect', self.container_id).stdout)[0]
        if info['Config']['Labels'].get('io.inferoptlab.owner') != self.token:
            raise SpecError('refusing to stop a container without matching ownership')
        docker('stop', '--time', '20', self.container_id)
        logs = docker('logs', self.container_id)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text(logs.stdout + logs.stderr, encoding='utf-8')
        docker('rm', self.container_id)
        self.container_id = None
        self.process = None
