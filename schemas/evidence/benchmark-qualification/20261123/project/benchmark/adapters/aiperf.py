"""AIPerf 0.12.0 CLI adapter. No importing its worker stack in the controller."""
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import shutil

from tools.specs import SpecError
from benchmark.process import run


def check_installation(expected='0.12.0'):
    try:
        installed=version('aiperf')
    except PackageNotFoundError as exc:
        raise SpecError('AIPerf is not installed; install benchmark/requirements.txt in the Linux benchmark environment') from exc
    if installed!=expected:
        raise SpecError(f'AIPerf version mismatch: expected {expected}, installed {installed}')
    executable=shutil.which('aiperf')
    if not executable:
        raise SpecError('aiperf executable is missing from PATH')
    return executable


def command(executable, plan, deployment, workload, protocol, concurrency, dataset_dir, artifact_dir, warmup=False):
    s=deployment['serving']
    count=protocol['execution']['warmup_request_count'] if warmup else workload['requests']['count']
    filename='warmup.jsonl' if warmup else 'requests.jsonl'
    args=[executable,'profile','--model',s['served_model'],'--tokenizer',s['tokenizer_path'],
        '--url',s['url'],'--endpoint-type','chat','--endpoint','/v1/chat/completions','--streaming',
        '--input-file',str(Path(dataset_dir)/filename),'--custom-dataset-type','single_turn',
        '--dataset-sampling-strategy','sequential','--no-allow-dataset-wrap',
        '--request-count',str(count),'--concurrency',str(min(concurrency,count)),
        '--random-seed',str(workload['requests']['seed']),
        '--request-timeout-seconds',str(protocol['execution']['timeout_s']),
        '--artifact-dir',str(artifact_dir),'--ui-type','none','--export-level','raw',
        '--use-server-token-count','--extra-inputs',f'max_tokens:{workload["output"]["tokens"]}',
        '--extra-inputs',f'min_tokens:{workload["output"]["tokens"]}',
        '--extra-inputs','ignore_eos:true','--extra-inputs','temperature:0']
    if plan['aiperf']['server_metrics']:
        args+=['--server-metrics',*plan['aiperf']['server_metrics']]
    if plan['aiperf']['gpu_telemetry']:
        args+=['--gpu-telemetry',*plan['aiperf']['gpu_telemetry']]
    return args


def telemetry_issues(artifact_dir, requirement):
    """A required missing collector must prevent an apparently complete result."""
    import json
    issues=[]
    summary=Path(artifact_dir)/'profile_export_aiperf.json'
    if not summary.is_file():
        return ['AIPerf aggregate export is missing']
    try:
        value=json.loads(summary.read_text(encoding='utf-8'))
    except (OSError,ValueError):
        return ['AIPerf aggregate export is unreadable']
    if not isinstance(value,dict):
        return ['AIPerf aggregate export must be an object']
    if value.get('aiperf_version')!='0.12.0':
        issues.append('unsupported/missing AIPerf export version')
    if value.get('was_cancelled'):
        issues.append('AIPerf reported a cancelled benchmark')
    if value.get('server_metrics_error_summary'):
        issues.append('AIPerf reported server-metrics collection errors')
    telemetry=value.get('telemetry_data') or {}
    if isinstance(telemetry,dict) and telemetry.get('error_summary'):
        issues.append('AIPerf reported GPU telemetry errors')
    if requirement in {'gpu','both'}:
        endpoints=telemetry.get('endpoints',{}) if isinstance(telemetry,dict) else {}
        has_metrics=any(gpu.get('metrics') for endpoint in endpoints.values() if isinstance(endpoint,dict)
                        for gpu in endpoint.get('gpus',{}).values() if isinstance(gpu,dict)) if isinstance(endpoints,dict) else False
        if not has_metrics:
            issues.append('required gpu telemetry is missing or empty')
        info=telemetry.get('summary',{}) if isinstance(telemetry,dict) else {}
        if set(info.get('endpoints_configured') or [])-set(info.get('endpoints_successful') or []):
            issues.append('required GPU telemetry has unsuccessful endpoints')
    if requirement in {'server','both'}:
        try:
            server=json.loads((Path(artifact_dir)/'server_metrics_export.json').read_text(encoding='utf-8'))
            metrics=server.get('metrics',{})
            if not any(item.get('series') for item in metrics.values() if isinstance(item,dict)):
                issues.append('required server telemetry is empty')
            info=server.get('summary',{})
            if set(info.get('endpoints_configured') or [])-set(info.get('endpoints_successful') or []):
                issues.append('required server telemetry has unsuccessful endpoints')
        except (OSError,ValueError,AttributeError):
            issues.append('required server telemetry is missing or unreadable')
    return issues
