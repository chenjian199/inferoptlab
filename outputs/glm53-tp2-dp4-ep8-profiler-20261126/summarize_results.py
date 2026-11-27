"""Build a concise, evidence-checked report for the final three-scenario capture."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from benchmark.breakdown.torch_trace import display_name, write_report

OUT=Path(__file__).resolve().parent
RUN=OUT/'run-r2'
state=json.loads((RUN/'state.json').read_text(encoding='utf-8'))
assert state['status']=='completed' and len(state['points'])==3
traces=sorted((RUN/'server/observations/profiles').glob('*.pt.trace.json.gz'))
assert len(traces)==24
summary=OUT/'operators'
manifest=write_report(summary,traces)
groups=defaultdict(list)
for row in manifest:
    name=Path(row['trace']).name
    scenario=name.split('_')[0]
    rank=re.search(r'_dp(\d+)_pp(\d+)_tp(\d+)_dcp(\d+)_ep(\d+)_',name)
    assert rank
    row['rank']=dict(zip(['dp','pp','tp','dcp','ep'],map(int,rank.groups())))
    assert row['annotations']=={'execute_context_0(0)_generation_1(1)':32},row['annotations']
    assert row['graph_replay_events'].get('mcGraphLaunch')==32
    assert row['kernel_calls']>0
    groups[scenario].append(row)
for rows in groups.values():
    assert {(r['rank']['dp'],r['rank']['tp'],r['rank']['ep']) for r in rows}=={(dp,tp,dp*2+tp) for dp in range(4) for tp in range(2)}

info=json.loads((RUN/'server/server-info.json').read_text(encoding='utf-8'))['vllm_config']
snapshot=json.loads((RUN/'snapshot.json').read_text(encoding='utf-8'))
lines=['# TP2 / DP4 / EP8：图模式纯 Decode Profiler 简版','',
    '采集完成：'+datetime.fromisoformat(state['updated_at']).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')+'（北京时间）。','',
    '三组场景均已完成：4K / 16K / 64K 输入，输出固定 200 tokens，总并发 4。每个并发槽使用独立上下文并固定到一个 DP rank。','',
    '**24 个 GPU worker trace 齐备**，每个 trace 验证到 32 次图重放及 32 个 `context=0, generation=1` 的迭代标注。',
    '每组先做无 Profiler 对照，再做采样请求；各轮 16 请求（并发×4），共 96 个完整的 200-token 请求。','',
    '原始上下文全命中，线上输入为 L+1（额外一个 P 产生的 seed）；全部请求验证 query=1、零抢占、输出 200。预热 Prefill 与 P→D 传输不计入本次 Decode 时间。','',
    '## running 条数与生效参数','',
    '| 参数 | 实际值 |','|---|---|',
    '| tensor / pipeline / data / expert parallel | 2 / 1 / 4 / 8 |',
    f"| max_num_seqs（每个 DP 调度实例） | {info['scheduler_config']['max_num_seqs']} |",
    '| 配置的四个 DP 实例上限之和 | 64；不代表实际负载 |',
    '| 本轮总并发 | 4，每个 DP 实例 1 |',
    f"| max_num_batched_tokens | {info['scheduler_config']['max_num_batched_tokens']} |",
    f"| max_model_len | {info['model_config']['max_model_len']} |",
    f"| enforce_eager | {info['model_config']['enforce_eager']} |",
    f"| cudagraph_mode | {info['compilation_config']['cudagraph_mode']}（FULL_AND_PIECEWISE） |",
    '| EP 通信后端 | allgather_reducescatter |',
    f"| GPU memory utilization | {info['cache_config']['gpu_memory_utilization']} |",
    f"| mamba_block_size / prefix_match_unit | {info['cache_config']['mamba_block_size']} / {info['cache_config']['prefix_match_unit']} |",
    f"| 实际 attention cache block_size | {info['cache_config']['block_size']}（自动推导，非 batched token 预算） |",
    '| 量化 / 激活 dtype | compressed-tensors W8A8 / bfloat16 |',
    '| 调度 | chunked prefill 开；async scheduling 关 |',
    '| 采样窗口 | delay_iterations=8、max_iterations=32；实测采样 32 个，完整请求仍输出 200 |','',
    '实际配置见 [server-info](run-r2/server/server-info.json)，完整命令见 [launch](run-r2/server/launch.json)，冻结配方见 [snapshot](run-r2/snapshot.json)。','',
    '## 不启用 Profiler 的请求性能','',
    '以下是对照轮，未调用 start_profile。延迟为请求级均值/P95；E2E 仅针对缓存续接的 200-token 请求。','',
    '| 输入 | 请求数 | TTFT ms 平均/P95 | TPOT ms 平均/P95 | E2E s 平均/P95 | 输出 tok/s | 请求 req/s |','|---|---:|---:|---:|---:|---:|---:|']
machine=[]
for point in sorted(state['points'],key=lambda p:int(re.match(r'l(\d+)',p['scenario'])[1])):
    name=point['scenario'];directory=RUN/name
    length=int(re.match(r'l(\d+)',name)[1]);control=point['control']['metrics'];profiled=point['profiled']['metrics']
    actual_running=[]
    for phase in ['control','profiled']:
        engine=json.loads((directory/phase/'engine-verification.json').read_text(encoding='utf-8'))
        checked=json.loads((directory/phase/'profile-verification.json').read_text(encoding='utf-8'))
        assert engine['valid'] and checked['valid'] and len(engine['requests'])==16
        per_dp=defaultdict(int)
        for req in engine['requests'].values():
            assert req['first_computed_tokens']==length and req['max_query_tokens']==1 and req['output_tokens']==200 and req['preemptions']==0
            assert req['max_running_requests']==1 and req['max_scheduled_requests']==1
            actual_running.append(req['max_running_requests']);per_dp[req['dp_rank']]+=1
        assert per_dp=={0:4,1:4,2:4,3:4}
    pair=lambda key,scale=1:' / '.join(f"{control[key][p]/scale:.2f}" for p in ['avg','p95'])
    lines.append(f"| {length//1024}K | 16 | {pair('time_to_first_token')} | {pair('inter_token_latency')} | {pair('request_latency',1000)} | {control['output_token_throughput']['avg']:.2f} | {control['request_throughput']['avg']:.3f} |")
    machine.append(dict(scenario=name,input_tokens=length,control=control,profiled=profiled,max_observed_running_per_dp=max(actual_running),traces=groups[name]))
lines += ['', '**调度实测**：96 个请求的观察记录中，每个 DP rank 的最大 running 和 scheduled 请求数均为 **1**，与总并发 4 的固定路由一致。','',
    '## GPU 采样窗口与热点','',
    '下面选用 DP0/TP0（EP0）作可读示例；八卡完整算子表见 [operators.md](operators/operators.md)。每张卡独立统计，跨卡时间不相加。','',
    '| 输入 | 图重放/迭代 | GPU kernel 调用数 | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |','|---|---:|---:|---:|---:|---:|']
representatives=[]
for point in machine:
    row=next(r for r in point['traces'] if r['rank']['dp']==0 and r['rank']['tp']==0)
    data=json.loads((summary/row['summary']).read_text(encoding='utf-8'));lane=next(iter(row['lanes'].values()))
    representatives.append((point,data))
    lines.append(f"| {point['input_tokens']//1024}K | 32 / 32 | {row['kernel_calls']} | {lane['kernel_duration_sum_ms']:.2f} | {lane['kernel_interval_union_ms']:.2f} | {lane['first_to_last_kernel_ms']:.2f} |")
lines += ['', 'kernel 时长和是采样窗口内 GPU 工作量；区间并集处理重叠。两者均不能直接当作 E2E 或无 Profiler 的单 token 延迟。','']
family_tables=[]
for point,data in representatives:
    values=defaultdict(lambda:dict(calls=0,total_ms=0))
    for row in data['operators']:
        if row['kind']!='gpu_kernel':continue
        values[row['family_hint']]['calls']+=row['calls'];values[row['family_hint']]['total_ms']+=row['total_ms']
    family_tables.append(values)
lines += ['### 同卡算子类别对照（依据 kernel 名称）','',
    '各格为 32 迭代内的 kernel 时长和 ms / 调用数；类别只按名称归类，无法确定的名称保留在 other，不能当成模型模块的精确占比。','',
    '| 类别 | 4K | 16K | 64K |','|---|---:|---:|---:|']
for name in sorted(set().union(*(set(table) for table in family_tables))):
    lines.append('| '+name+' | '+' | '.join(f"{table[name]['total_ms']:.3f} / {table[name]['calls']}" for table in family_tables)+' |')
lines.append('')
for point,data in representatives:
    rows=sorted((r for r in data['operators'] if r['kind']=='gpu_kernel'),key=lambda r:-r['total_ms'])
    lines += [f"### {point['input_tokens']//1024}K：DP0/TP0 前 10 个 GPU kernel",'',
        '| kernel | 32 迭代调用数 | 总 ms | 每次平均 μs | 每次 P95 μs |','|---|---:|---:|---:|---:|']
    for row in rows[:10]:lines.append(f"| `{display_name(row['name'])}` | {row['calls']} | {row['total_ms']:.3f} | {row['mean_us']:.3f} | {row['p95_us']:.3f} |")
    lines.append('')
lines += ['## 文件与计时边界','',
    '- [完整算子调用/耗时表](operators/operators.md)：逐卡 GPU kernel、CPU 算子；JSON 保留完整模板名、最大耗时和分类提示。',
    '- [原始 trace 目录](run-r2/server/observations/profiles)：24 份 `.pt.trace.json.gz`，可解压后在本地 Perfetto 查看；文件名包含场景和 DP/TP/EP rank。',
    '- [运行状态](run-r2/state.json)、[server 日志](run-r2/server/server.log)、各场景 `control/` 与 `profiled/` 保存请求指标和验证证据。',
    '- [可复用采集入口](../../benchmark/breakdown/cached_decode_profile.py)；[部署配方](../../recipes/deployments/glm53-flash/c500/vllm/cached-decode/tp2-dp4-ep8-profiler.yaml)。',
    '- CPU 算子耗时包含子调用；图重放不重新执行所有 Python/ATen 调用。GPU kernel 记录与 CPU 调用覆盖不同，不能补造缺失的算子 shape 或模块层级。',
    '- `profiled/` 请求时延含采样和 trace 导出干扰，仅作诊断；GPU trace 不是 200 个输出 token 的完整时间线，而是其中 32 个迭代。',
    '- 首轮 r1 在 16K 复验时因请求标识重名中止，原始缓存实际全命中。已修正场景标识，并使用 r2 重新完成全部三组；本报告仅使用 r2。',
    '- 本轮结束后，控制器自动停止并清理其拥有的模型服务；这里的 running=1 指采样期间的观测值。','',
    '本地重建报告：`python outputs/glm53-tp2-dp4-ep8-profiler-20261126/summarize_results.py`。','']
(OUT/'quick-read.md').write_text('\n'.join(lines),encoding='utf-8')
(OUT/'results.json').write_text(json.dumps(machine,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(scenarios=len(machine),traces=len(manifest),requests=96,report=str(OUT/'quick-read.md'))))
