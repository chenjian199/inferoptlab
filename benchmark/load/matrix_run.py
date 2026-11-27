"""Single-file cached Decode performance matrix with inline resolved KV budgets."""
from __future__ import annotations
import argparse
import contextlib
import csv
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import urllib.request

from benchmark.common.io import json_write, utc_now, file_hash
from benchmark.load import capacity, matrix_config as mc, decode_protocol as cd, dataset
from benchmark.load.adapters import aiperf, sglang, vllm
from benchmark.load.runner import lease, environment
from tools.specs import read, digest, SpecError


def budget(matrix, ranks, length):
    """Use resolved group costs, reserving retained states and one tail copy.

    This is a conservative supported-layout budget, not an observed maximum.
    Never silently substitute token capacity or the scheduler's running limit.
    """
    output = max(matrix['workload_matrix']['output_tokens'])
    details = []
    reserve = matrix['capacity_planning']['reserve_null_blocks_per_pool'] + matrix['capacity_planning']['additional_reserved_blocks_per_pool']
    for rank in ranks:
        groups = rank['groups']
        kinds = [g['type'] for g in groups]
        if kinds != ['MambaSpec'] * 4 + ['MLAAttentionSpec', 'CircularBufferSpec']:
            raise SpecError('unrecognized hybrid KV layout: '+str(kinds))
        for group in groups[:4]:
            spec = group['spec']
            if spec['mamba_cache_mode'] != 'align' or spec['num_speculative_blocks'] or spec['num_prefill_checkpoint_blocks']:
                raise SpecError('unsupported state checkpoint accounting')
        cost = next(c for c in rank['costs'] if c['input_tokens']==length and c['output_tokens']==output)
        per_group = cost['runtime_blocks_by_group']
        if per_group[:4] != [2]*4 or per_group[-1] != 1:
            raise SpecError('resolved state/ring costs differ from supported accounting')
        slot = sum(per_group) + 4 + 1
        limit = max(0, (rank['num_blocks']-reserve)//slot)
        details.append(dict(dp_rank=rank['dp_rank'], pool_blocks=rank['num_blocks'],
            reserved_pool_blocks=reserve, runtime_blocks_by_group=per_group,
            retained_prefix_state_blocks=4, attention_tail_copy_blocks=1,
            blocks_per_slot=slot, slots=limit))
    if [d['dp_rank'] for d in details] != list(range(len(ranks))):
        raise SpecError('missing or unordered DP ranks')
    return dict(input_tokens=length, output_reservation=output,
        accounting='conservative_resolved_pool_budget_not_measured_maximum', ranks=details,
        **capacity.concurrency_points(matrix['workload_matrix']['concurrency'],
            [d['slots'] for d in details], matrix['requests']['count_multiplier']))


def validate(matrix):
    mc.expand(matrix)
    if matrix['measurement']['retain_cache_across_outputs_and_repetitions']:
        raise SpecError('matrix comparisons require independent cache preparation per output/repetition')
    required = {'arrival':'closed_loop','temperature':0,'ignore_eos':True,'stream':True,'stop_policy':'fixed_output_tokens'}
    for key, value in required.items():
        if matrix['requests'][key] != value:
            raise SpecError(f'unsupported requests.{key}')
    if matrix['server']['profiler_enabled'] or matrix['execution']['concurrent_deployments'] != 1:
        raise SpecError('requires one deployment and no profiler')
    if matrix['capacity_planning']['mode'] != 'calculate_after_startup':
        raise SpecError('matrix runner requires inline capacity calculation')
    for key in ('count_multiplier','repetitions','request_timeout_s','point_timeout_s'):
        if type(matrix['requests'][key]) is not int or matrix['requests'][key] < 1:
            raise SpecError('invalid request bound: '+key)


@contextlib.contextmanager
def deadline(seconds):
    def expired(*_):
        raise TimeoutError('point preparation/measurement deadline exceeded')
    previous = signal.signal(signal.SIGALRM, expired)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


def metrics_snapshot(serving, path):
    try:
        with urllib.request.urlopen(serving['url']+'/metrics', timeout=15) as response:
            path.write_bytes(response.read())
    except Exception as exc:
        path.with_suffix('.error.json').write_text(json.dumps(dict(error=repr(exc))))


def score(root, executable, matrix, serving, obs, slots, length, output, concurrency, point, path):
    path.mkdir(parents=True)
    fixture, expected = cd.make_fixture(slots, output, matrix['requests']['count_multiplier'], serving['served_model'], point+'-'+digest(str(path))[:8])
    json_write(path/'inputs.json', fixture)
    json_write(path/'expected.json', expected)
    json_write(path/'dataset.json', dict(context_sha256=digest([s['context_ids'] for s in slots]), slots_sha256=digest(slots)))
    command = cd.profile_command(executable, serving, path/'inputs.json', path/'aiperf', concurrency,
        concurrency*matrix['requests']['count_multiplier'], matrix['requests']['request_timeout_s'])
    env = os.environ.copy()
    env.update(PYTHONPATH=str(root/'benchmark/load/aiperf_hooks')+os.pathsep+str(root), AIPERF_DATASET_MMAP_CACHE_ENABLED='false')
    json_write(path/'command.json', dict(argv=command))
    marker = obs/'qualification-active.txt'
    phase = point+'-'+cd.qualification_phase(path)
    json_write(path/'observation-phase.json', dict(phase=phase))
    metrics_snapshot(serving, path/'metrics-before.txt')
    marker.write_text(phase)
    try:
        with (path/'aiperf.log').open('w') as log:
            process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True)
            try:
                code = process.wait(timeout=matrix['requests']['point_timeout_s'])
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=10)
    finally:
        marker.unlink(missing_ok=True)
        metrics_snapshot(serving, path/'metrics-after.txt')
    engine = cd.scheduler_evidence(cd.observations(obs,'scheduler'),expected,length,output)
    profile = cd.validate_profile(path/'aiperf',expected,slots,length,output)
    attention = [r for r in cd.observations(obs,'attention') if r['phase']==phase]
    attention_ok = {'GDNAttentionMetadataBuilder','FlashMLASparseMetadataBuilder'} <= {r['builder'] for r in attention} and all(r['num_prefills']==0 and r['num_prefill_tokens']==0 for r in attention)
    json_write(path/'engine-verification.json',engine)
    json_write(path/'profile-verification.json',profile)
    json_write(path/'attention-verification.json',dict(valid=attention_ok, rows=len(attention)))
    valid = code==0 and engine['valid'] and profile['valid'] and attention_ok
    json_write(path/'result.json',dict(valid=valid, returncode=code, finished_at=utc_now()))
    if not valid:
        raise SpecError('invalid request/cache/routing/Decode evidence; see verification files')


def report(out, state):
    columns = ['deployment','context_tokens','output_tokens','concurrency','repetition','requests','status']
    fields = [('ttft','time_to_first_token'),('tpot','inter_token_latency'),('e2e','request_latency')]
    columns += [f'{name}_{stat}_ms' for name,_ in fields for stat in ('avg','p50','p90','p95','p99')]
    columns += ['output_tokens_per_second','requests_per_second']
    rows=[]
    for p in state['points']:
        row={k:p.get(k) for k in columns}
        raw=Path(p['directory'])/'aiperf/profile_export_aiperf.json'
        if p['status']=='completed' and raw.exists():
            data=read(raw)
            for name, key in fields:
                for stat in ('avg','p50','p90','p95','p99'):
                    row[f'{name}_{stat}_ms']=data.get(key,{}).get(stat)
            row['output_tokens_per_second']=data.get('output_token_throughput',{}).get('avg')
            row['requests_per_second']=data.get('request_throughput',{}).get('avg')
        rows.append(row)
    with (out/'summary.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    lines=['# 单文件矩阵性能扫描','',f"状态：{state['status']}；更新时间：{state['updated_at']}",'',
        '容量按实际池计算保守预算，不额外搜索边界；有效性能点逐请求验证缓存及Decode路径。精度验收未建立。','',
        '| 部署 | 输入 | 输出 | 并发 | 状态 | TPOT avg ms | TPOT p95 ms | tokens/s | req/s |',
        '|---|---:|---:|---:|---|---:|---:|---:|---:|']
    for r in rows:
        values=[r[k] for k in ['deployment','context_tokens','output_tokens','concurrency','status','tpot_avg_ms','tpot_p95_ms','output_tokens_per_second','requests_per_second']]
        lines.append('| '+' | '.join(f'{v:.3f}' if isinstance(v,float) else str(v if v is not None else '—') for v in values)+' |')
    lines += ['', '## 部署与排除记录', '', *['- '+json.dumps(d,ensure_ascii=False) for d in state['deployments'] if d.get('error')]]
    (out/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def run(root, matrix_path, out, cache_dir):
    matrix=read(matrix_path);validate(matrix)
    out.mkdir(parents=True,exist_ok=True)
    fingerprint=dict(matrix=matrix,code={str(p.relative_to(root)):file_hash(p) for base in ('benchmark','tools','contracts') for p in (root/base).rglob('*.py')},
        native_extensions={str(p.relative_to(root)):file_hash(p) for p in (root/'tools/deployment/metax-vllm/observers').glob('*.so')},
        tokenizer=dataset.tokenizer_fingerprint(matrix['target']['tokenizer_path']),
        model_files=[dict(path=str(p.relative_to(matrix['target']['model_path'])),size=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns) for p in sorted(Path(matrix['target']['model_path']).rglob('*')) if p.is_file()])
    if (out/'identity.json').exists() and read(out/'identity.json') != fingerprint:
        raise SpecError('resume identity changed; use new run directory')
    json_write(out/'identity.json',fingerprint)
    (out/'matrix.yaml').write_bytes(matrix_path.read_bytes())
    json_write(out/'expanded-deployments.json',mc.expand(matrix))
    json_write(out/'environment.json',environment('MACA_VISIBLE_DEVICES'))
    executable=aiperf.check_installation()
    tokenizer=dataset.load_tokenizer(matrix['target']['tokenizer_path'])
    state=read(out/'state.json') if (out/'state.json').exists() else dict(points=[],deployments=[])
    def save(**updates):
        state.update(updates,updated_at=utc_now());json_write(out/'state.json',state);report(out,state)
        print(json.dumps(updates,ensure_ascii=False),flush=True)
    with lease(root):
        for index,row in enumerate(mc.expand(matrix)):
            if any(d['id']==row['id'] and d['status']=='completed' for d in state['deployments']):continue
            record=dict(id=row['id'],status='starting');state['deployments'].append(record)
            dep,runtime=mc.deployment_specs(matrix,row,cache_dir)
            server=None;obs=None;ranks=None;info=None;attempt=None
            def close():
                nonlocal server
                if server is not None:
                    server.close();server=None
            def start():
                nonlocal server,obs,ranks,info,attempt
                close()
                attempt=out/row['id']/('server-'+str(time.time_ns()));attempt.mkdir(parents=True)
                obs=attempt/'observations'
                server=vllm.Deployment(dep,runtime,attempt/'server.log',observation=dict(hooks=root/'tools/deployment/metax-vllm/observers',records=obs))
                save(status='starting',deployment=row['id'],deployment_index=index+1,deployment_total=len(mc.expand(matrix)))
                command=server.launch();json_write(attempt/'launch.json',dict(command=command,container_id=server.container_id))
                save(container_id=server.container_id,server_directory=str(attempt))
                sglang.wait_ready(dep['serving'],time.monotonic()+dep['serving']['startup_timeout_s'],server)
                info=cd.api(dep['serving']['url'],'/server_info?config_format=json');mc.verify(row,info)
                json_write(attempt/'server-info.json',info)
                ranks=mc.pool_inventory(obs,row['parallelism']['dp']);json_write(attempt/'per-rank-capacity.json',ranks)
            try:
                start()
                for length in matrix['workload_matrix']['input_tokens']:
                    if length+1+max(matrix['workload_matrix']['output_tokens'])>info['vllm_config']['model_config']['max_model_len']:
                        record.setdefault('exclusions',[]).append(dict(input_tokens=length,reason='context_length_exceeded'));save(status='scanning');continue
                    planned=budget(matrix,ranks,length)
                    json_write(out/row['id']/f'capacity-l{length}.json',planned)
                    if not planned['points']:
                        record.setdefault('exclusions',[]).append(dict(input_tokens=length,reason='conservative_budget_zero_not_physical_zero'));save(status='scanning');continue
                    for entry in planned['points']:
                        concurrency=entry['concurrency'];preparation_failure=None
                        for output in matrix['workload_matrix']['output_tokens']:
                            for repetition in range(matrix['requests']['repetitions']):
                                identity=f'{row["id"]}-l{length}-o{output}-c{concurrency}-r{repetition}'
                                if any(p['id']==identity and p['status']=='completed' for p in state['points']):continue
                                if preparation_failure:
                                    state['points'].append(dict(id=identity,deployment=row['id'],context_tokens=length,output_tokens=output,concurrency=concurrency,repetition=repetition,requests=entry['requests'],directory=preparation_failure,status='blocked_group_preparation'))
                                    save(status='group_output_blocked',point=identity,reason='same input/concurrency preparation already exhausted retries')
                                    continue
                                for retry in range(matrix['execution']['max_point_retries']+1):
                                    path=out/row['id']/(identity+'-a'+str(time.time_ns()))
                                    point=dict(id=identity,deployment=row['id'],context_tokens=length,output_tokens=output,concurrency=concurrency,repetition=repetition,requests=entry['requests'],directory=str(path),retry=retry,status='running')
                                    state['points'].append(point);path.mkdir(parents=True)
                                    stage='starting'
                                    try:
                                        if server is None:start()
                                        current=budget(matrix,ranks,length)
                                        json_write(path/'resolved.json',dict(deployment=row,capacity=current,server_directory=str(attempt)))
                                        if concurrency>current['capacity_limit']:raise SpecError('restarted pool smaller than planned concurrency')
                                        with deadline(matrix['requests']['point_timeout_s']):
                                            stage='warming'
                                            prep=path/'warmup';prep.mkdir()
                                            save(status='warming',point=identity,concurrency=concurrency,input_tokens=length,output_tokens=output)
                                            slots=cd.prepare_slots(tokenizer,dep['serving'],length,concurrency,row['parallelism']['dp'],matrix['requests']['seed'],prep,matrix['requests']['request_timeout_s'])
                                            q=cd.qualify_slots(slots,dep['serving'],length,obs,prep,matrix['requests']['request_timeout_s'],output=2)
                                            if not q['valid']:raise SpecError('cached Decode route qualification failed')
                                            stage='scoring'
                                            save(status='scoring',point=identity,point_directory=str(path),input_tokens=length,output_tokens=output,concurrency=concurrency)
                                            score(root,executable,matrix,dep['serving'],obs,slots,length,output,concurrency,identity,path/'measurement')
                                        point.update(status='completed',directory=str(path/'measurement'))
                                        save(status='point_completed');break
                                    except Exception as exc:
                                        point.update(status='failed',error=repr(exc),failure_stage=stage)
                                        save(status='point_failed',point=identity,stage=stage,error=repr(exc));close()
                                        if retry==matrix['execution']['max_point_retries'] and stage=='warming':
                                            preparation_failure=str(path)
                                        log=attempt/'server.log'
                                        if retry==matrix['execution']['max_point_retries'] and log.exists() and 'illegal memory access' in log.read_text(errors='replace'):
                                            raise SpecError('repeated_device_illegal_access: deployment quarantined; remaining points not measured')
                                # All failed attempts are retained. Continue with the next matrix point.
                record['status']='completed'
            except Exception as exc:
                record.update(status='failed',error=repr(exc));save(status='deployment_failed')
            finally:
                close();save(status='between_deployments',container_id=None)
        save(status='completed_with_exclusions' if any(p['status']!='completed' for p in state['points']) or any(d.get('exclusions') or d['status']=='failed' for d in state['deployments']) else 'completed')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('matrix',type=Path);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--cache-dir',type=Path,required=True);parser.add_argument('--preview',action='store_true')
    args=parser.parse_args();matrix=read(args.matrix);validate(matrix)
    if args.preview:
        rows=mc.expand(matrix)
        for row in rows:
            dep,runtime=mc.deployment_specs(matrix,row,args.cache_dir);vllm.server_arguments(dep,runtime)
        print(f'{len(rows)} deployments; performance points computed after each startup')
    else:run(Path(__file__).resolve().parents[2],args.matrix.resolve(),args.out.resolve(),args.cache_dir)

if __name__=='__main__':main()
