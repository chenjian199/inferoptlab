"""Summarize torch Chrome traces per worker/device, retaining overlap semantics."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import re

from benchmark.breakdown.trace import union_duration
from benchmark.common.io import file_hash, json_write


def percentile(values, q):
    values=sorted(values)
    position=(len(values)-1)*q;lo=int(position);hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(position-lo)


def family(name):
    """A name-based hint, not proof of framework module attribution."""
    n=name.lower()
    if any(k in n for k in ['allreduce','all_reduce','allgather','all_gather','reducescatter','reduce_scatter','alltoall','all_to_all','nccl','mccl']):return 'collective'
    if 'mhc' in n:return 'mhc'
    if any(k in n for k in ['indexer','topk','top_k']):return 'indexer_or_topk'
    if any(k in n for k in ['flash_mla','flashmla','mla_decode','attention','attn']):return 'attention'
    if any(k in n for k in ['kda','gated_delta','scatter_states','causal_conv','recurrent']):return 'kda_or_state'
    if 'gemm' in n and 'moe' in n:return 'moe_gemm'
    if any(k in n for k in ['gemm','matmul','gemv']):return 'gemm'
    if any(k in n for k in ['moe','expert','route','align_block']):return 'moe_routing_or_compute'
    if any(k in n for k in ['quant','dequant']):return 'quantization'
    if any(k in n for k in ['rms','norm']):return 'normalization'
    return 'other'


def summarize_events(events):
    categories=Counter(e.get('cat','') for e in events)
    groups=defaultdict(list);device_intervals=defaultdict(list);annotations=Counter();replays=Counter()
    for e in events:
        if e.get('ph')!='X' or not isinstance(e.get('dur'),(int,float)) or e['dur']<0:continue
        cat=e.get('cat','');name=e.get('name','');args=e.get('args',{})
        if name.startswith('execute_') and cat=='user_annotation':annotations[name]+=1
        if 'graphlaunch' in name.lower() or 'cudagraph.replay' in name.lower():replays[name]+=1
        if cat=='kernel':
            lane=str(args.get('device',e.get('pid','unknown')))
            groups[('gpu_kernel',lane,name)].append(e['dur'])
            device_intervals[lane].append((e['ts'],e['ts']+e['dur']))
        elif cat=='cpu_op':groups[('cpu_op',str(e.get('pid','unknown')),name)].append(e['dur'])
        elif cat in {'gpu_memcpy','gpu_memset'}:groups[(cat,str(args.get('device',e.get('pid','unknown'))),name)].append(e['dur'])
    rows=[]
    for (kind,lane,name),durations in groups.items():
        rows.append(dict(kind=kind,lane=lane,name=name,family_hint=family(name),calls=len(durations),
            total_ms=sum(durations)/1000,mean_us=sum(durations)/len(durations),p95_us=percentile(durations,.95),max_us=max(durations)))
    rows.sort(key=lambda x:(x['kind'],-x['total_ms'],x['name']))
    lanes={lane:dict(kernel_interval_union_ms=union_duration(intervals)/1000,
                    first_to_last_kernel_ms=(max(b for a,b in intervals)-min(a for a,b in intervals))/1000,
                    kernel_duration_sum_ms=sum(b-a for a,b in intervals)/1000) for lane,intervals in device_intervals.items()}
    return dict(categories=dict(categories),annotations=dict(annotations),graph_replay_events=dict(replays),lanes=lanes,operators=rows)


def summarize_file(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt',encoding='utf-8') as stream:raw=json.load(stream)
    result=summarize_events(raw['traceEvents'])
    result.update(path=str(path),sha256=file_hash(path),bytes=path.stat().st_size,
        display_time_unit=raw.get('displayTimeUnit'),timestamp_unit='Chrome trace ts/dur in microseconds')
    return result


def write_report(directory, traces):
    directory.mkdir(parents=True,exist_ok=True)
    lines=['# torch.profiler Decode 算子采样','',
        '按 worker/device 独立统计。GPU kernel 时长求和不等于墙钟时间；CPU 算子为包含子调用的总时长，不能与 GPU 时长相加。',
        '图重放可能保留 GPU kernel 名称但不重新产生每个 Python/ATen 调用；缺失 CPU 调用不表示该算子未执行。',
        'family_hint 仅按名称归类。完整名称、调用次数、均值、P95、最大值和总时长保存在各 trace 的 JSON 中；过长的模板名称在表内缩写并附名称哈希。','']
    manifest=[]
    for path in traces:
        result=summarize_file(path)
        name=path.name.removesuffix('.gz').removesuffix('.json')+'-summary.json'
        json_write(directory/name,result)
        kernel_rows=[r for r in result['operators'] if r['kind']=='gpu_kernel']
        manifest.append(dict(trace=str(path),summary=name,kernel_calls=sum(r['calls'] for r in kernel_rows),lanes=result['lanes'],graph_replay_events=result['graph_replay_events'],annotations=result['annotations']))
        lines += ['## '+path.name,'',f'[完整算子表]({name})；GPU kernel 调用数：{manifest[-1]["kernel_calls"]}。','',
                  '| Device | kernel 时长和 ms | kernel 区间并集 ms | 首末 kernel 跨度 ms |','|---|---:|---:|---:|']
        for lane,stats in result['lanes'].items():
            lines.append(f"| {lane} | {stats['kernel_duration_sum_ms']:.3f} | {stats['kernel_interval_union_ms']:.3f} | {stats['first_to_last_kernel_ms']:.3f} |")
        lines += ['', '迭代标注：`'+json.dumps(result['annotations'],ensure_ascii=False)+'`。图重放事件：`'+json.dumps(result['graph_replay_events'])+'`。','',
                  '| GPU kernel（前 20） | 调用数 | 总 ms | 平均 μs | P95 μs | 最大 μs |','|---|---:|---:|---:|---:|---:|']
        for row in sorted(kernel_rows,key=lambda r:-r['total_ms'])[:20]:
            name=display_name(row['name'])
            lines.append(f"| `{name}` | {row['calls']} | {row['total_ms']:.3f} | {row['mean_us']:.3f} | {row['p95_us']:.3f} | {row['max_us']:.3f} |")
        lines += ['', '| CPU 算子（包含子调用，前 10） | 调用数 | 总 ms | 平均 μs |','|---|---:|---:|---:|']
        for row in sorted((r for r in result['operators'] if r['kind']=='cpu_op'),key=lambda r:-r['total_ms'])[:10]:
            name=row['name'].replace('|','\\|')
            lines.append(f"| `{name}` | {row['calls']} | {row['total_ms']:.3f} | {row['mean_us']:.3f} |")
        lines.append('')
    json_write(directory/'manifest.json',manifest)
    (directory/'operators.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    if not traces or any(not r['kernel_calls'] for r in manifest):raise ValueError('missing GPU kernel events; CPU-only traces do not prove device profiling')
    return manifest


def display_name(name):
    if len(name)>180:
        name=name[:145]+' … #'+hashlib.sha256(name.encode()).hexdigest()[:10]
    return name.replace('|','\\|')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('traces',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    paths=sorted(set(args.traces.rglob('*.pt.trace.json.gz'))|set(args.traces.rglob('*.pt.trace.json')))
    manifest=write_report(args.out,paths)
    print(json.dumps(dict(traces=len(manifest),kernels=sum(r['kernel_calls'] for r in manifest))))


if __name__=='__main__':main()
