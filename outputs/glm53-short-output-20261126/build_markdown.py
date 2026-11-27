"""Export the frozen, hash-verified measurement snapshot to Markdown."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import statistics

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
DEST = OUT / 'markdown'
DEST.mkdir(exist_ok=True)
SOURCES = DEST / 'sources'
SOURCES.mkdir(exist_ok=True)
manifest = json.loads((OUT / 'markdown-source.json').read_text(encoding='utf-8'))

def read_archive(receipt):
    raw = (ROOT / receipt['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == receipt['sha256']
    return json.loads(gzip.decompress(raw))

core = read_archive(manifest['core'])
extra = read_archive(manifest['details'])
assert extra['source_sha256'] == manifest['core']['sha256']
for files in [core['files'], extra['files'], *[e['files'] for e in core['runs'] + core.get('historical_runs', [])]]:
    for item in files.values():
        assert hashlib.sha256(item['text'].encode()).hexdigest() == item['sha256']
verification = json.loads((ROOT / 'experiments/evidence/glm53-short-output-collected-20261125/local-verification.json').read_text())
assert verification['archive_sha256'] == manifest['core']['sha256']
layouts = {f'glm53-vllm-decode-{s}': name for s,name in [
    ('tp8','TP8'),('tp8-ep8','TP8/EP8'),('tp4-dp2-ep8','TP4/DP2/EP8'),
    ('tp2-dp4-ep8','TP2/DP4/EP8'),('tp1-dp8-ep8','TP1/DP8/EP8')]}
entries = sorted([e for e in core['runs'] if e['ledger_entry']['status']=='completed'],
    key=lambda e:(list(layouts).index(e['ledger_entry']['deployment']),
                  json.loads(e['files']['run.json']['text'])['dataset_manifest']['input_tokens'],
                  json.loads(e['files']['run.json']['text'])['dataset_manifest']['output_tokens'],
                  e['ledger_entry']['concurrency'],e['ledger_entry']['repetition']))
assert len(entries) == verification['completed']

def fmt(v):
    if v is None: return '—'
    if isinstance(v,bool): return str(v).lower()
    if isinstance(v,int): return str(v)
    if isinstance(v,float):
        if not math.isfinite(v): return str(v)
        if v != 0 and abs(v)<1e-5: return f'{v:.6g}'
        return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'
    return str(v).replace('|','&#124;').replace('\n','<br>')

def table(headers, rows):
    rows=list(rows)
    assert all(len(r)==len(headers) for r in rows)
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(fmt(v) for v in r)+' |' for r in rows])+'\n'

def pct(values,q):
    xs=sorted(values);p=(len(xs)-1)*q;lo=math.floor(p);hi=math.ceil(p)
    return xs[lo]+(xs[hi]-xs[lo])*(p-lo)

def stats(values):
    return dict(avg=statistics.fmean(values),min=min(values),max=max(values),std=statistics.pstdev(values),
                count=len(values),sum=sum(values),**{f'p{q}':pct(values,q/100) for q in [1,5,10,25,50,75,90,95,99]})

checked=0
native_fields=Counter()
client_metric_names=set()
server_metric_names=set()
server_series_count=0
all_server_stat_fields=set()
labels={}
client=['# 客户端全部指标\n', '[返回总览](./README.md)\n',
        '每个测点单独列出；计分与预热分开。数值保留到小数点后 6 位，源 JSON 保留原始精度。`—` 表示原始导出没有该统计项，不表示零。\n',
        '均值/分位数均沿用 AIPerf 0.12.0 的对应统计总体；能从逐请求原始记录重算的指标已独立核对。`inter_token_latency` 是请求级平均间隔的分布，`inter_chunk_latency` 是流式分块间隔分布，两者不能混用。\n']
server=['# 服务端全部指标\n', '[返回总览](./README.md)\n',
        '保留 AIPerf 服务端导出的原始单位、指标类型、标签和统计字段。`*_estimate` 为 Prometheus histogram 桶估计分位数，不是客户端逐请求精确分位数。不同 engine 标签不合并，分位数不取平均。\n',
        'Gauge 的分位数针对采样值；Counter 的 total/rate 与 Histogram 的 count/sum/count_rate/sum_rate 沿用导出窗口。该窗口可能覆盖请求边界附近的采样，不能直接与客户端窗口吞吐视为相同口径。未知单位标为“未声明”，不猜测。\n']
overview=[]
detail_index=[]
warmup_requests=0
for number,entry in enumerate(entries,1):
    row=entry['ledger_entry'];files=entry['files'];run=row['directory'];anchor=f'point-{number:03d}'
    record=json.loads(files['run.json']['text']);summary=json.loads(files['summary.json']['text'])
    dec=json.loads(files['decode.json']['text']);dm=record['dataset_manifest']
    title=f"{number:03d} · {layouts[row['deployment']]} · {dm['input_tokens']}→{dm['output_tokens']} · C{row['concurrency']} · 第{row['repetition']}轮"
    native=json.loads(files['raw/aiperf/profile_export_aiperf.json']['text'])
    raw=[json.loads(line) for line in files['raw/aiperf/profile_export.jsonl']['text'].splitlines() if line.strip()]
    assert len(raw)==4*row['concurrency'] and all(not r.get('error') for r in raw)
    for name,metric in native.items():
        if not isinstance(metric,dict) or 'unit' not in metric:continue
        native_fields.update(metric.keys());client_metric_names.add(name)
        values=[]
        for request in raw:
            m=request['metrics'].get(name)
            if m is None:continue
            assert m['unit']==metric['unit']
            value=m['value'];values.extend(value if isinstance(value,list) else [value])
        if values:
            expected=stats(values)
            for field,value in expected.items():
                if field in metric:
                    assert math.isclose(value,metric[field],rel_tol=1e-8,abs_tol=1e-7),(run,name,field,value,metric[field])
                    checked+=1
    n=summary['counts']['succeeded'];warm=json.loads(files['warmup-summary.json']['text'])
    warmup_requests+=warm['counts']['succeeded']
    overview.append(dict(row=row,run=run,title=title,anchor=anchor,dm=dm,n=n,summary=summary,dec=dec,native=native))
    detail_index.append([number,layouts[row['deployment']],dm['input_tokens'],dm['output_tokens'],row['concurrency'],row['repetition'],
                        f'[客户端](client-metrics.md#{anchor}) / [服务端](server-metrics.md#{anchor})',run])
    for dest in [client,server]:dest.extend([f'<a id="{anchor}"></a>\n',f'## {title}\n',f'Run ID：`{run}`；Trial ID：`{row["trial_id"]}`。\n'])
    client.append(f"计分 {n}/{4*row['concurrency']} 成功；独立预热 {warm['counts']['succeeded']} 成功；客户端计分窗口 {fmt(summary['duration_s'])} 秒。\n")
    client.append('项目统一口径：\n'+table(['指标','数值','单位'],[
        ['成功率',summary['rates']['success_rate'],'ratio'],
        ['请求吞吐',summary['rates']['request_throughput'],'requests/s'],
        ['输入吞吐',summary['rates']['input_token_throughput'],'tokens/s'],
        ['输出吞吐（含 Prefill 的完整窗口）',summary['rates']['output_token_throughput'],'tokens/s']]))
    for phase,phase_title in [('aiperf','计分'),('warmup','预热（不计入性能汇总）')]:
        native_name=f'raw/{phase}/profile_export_aiperf.json'
        doc=json.loads(files[native_name]['text'])
        source_name=f'{run}-{phase}-client.json'
        (SOURCES/source_name).write_text(files[native_name]['text'],encoding='utf-8')
        client.append(f'### {phase_title}\n\n[完整原始 JSON](sources/{source_name})；开始时间 `{doc.get("start_time")}`，结束时间 `{doc.get("end_time")}`（原始时间字符串未标注时区）。\n')
        metrics={k:v for k,v in doc.items() if isinstance(v,dict) and 'unit' in v}
        columns=['avg','min','p50','p90','p95','p99','max','std','count']
        client.append(table(['指标','单位',*columns],([k,v['unit'],*[v.get(c) for c in columns]] for k,v in metrics.items())))
        columns2=sorted(set().union(*(set(v) for v in metrics.values()))-set(columns)-{'unit'},key=lambda s:(0,int(s[1:])) if s.startswith('p') and s[1:].isdigit() else (1,s))
        client.append('其余分位数与统计字段：\n'+table(['指标',*columns2],([k,*[v.get(c) for c in columns2]] for k,v in metrics.items())))
        telemetry=doc.get('telemetry_data',{})
        client.append(f"GPU 遥测成功端点：`{json.dumps(telemetry.get('summary',{}).get('endpoints_successful',[]))}`；错误摘要：`{json.dumps(doc.get('error_summary',[]),ensure_ascii=False)}`。\n")
        key=f'{run}/raw/{phase}/server_metrics_export.json'
        if key not in extra['files']:
            server.append(f'### {phase_title}\n\n服务端导出缺失。\n');continue
        export=json.loads(extra['files'][key]['text']);source_name=f'{run}-{phase}-server.json'
        (SOURCES/source_name).write_text(extra['files'][key]['text'],encoding='utf-8')
        server.append(f'### {phase_title}\n\n[完整原始 JSON（含直方图桶、标签、采样窗口）](sources/{source_name})\n')
        info=export['summary']
        server.append(table(['采集端点','抓取次数','采样跨度 s','平均抓取延迟 ms','平均采样间隔 ms'],
            ([url,d.get('total_fetches'),d.get('duration_seconds'),d.get('avg_fetch_latency_ms'),d.get('avg_update_interval_ms')] for url,d in info.get('endpoint_info',{}).items())))
        groups=defaultdict(list)
        for name,metric in export['metrics'].items():
            server_metric_names.add(name)
            for series in metric['series']:
                lab=dict(endpoint=series.get('endpoint_url'),**series.get('labels',{}))
                text=json.dumps(lab,ensure_ascii=False,sort_keys=True)
                label='L'+hashlib.sha256(text.encode()).hexdigest()[:12]
                assert label not in labels or labels[label]==text
                labels[label]=text
                values=series.get('stats',{})
                all_server_stat_fields.update(values)
                groups[metric['type']].append((name,metric.get('unit','未声明'),f'[{label}](server-labels.md#{label.lower()})',values))
                server_series_count+=1
        for kind,series in groups.items():
            server.append(f'#### {kind}\n')
            keys=set().union(*(set(v) for _,_,_,v in series))
            main=[k for k in ['avg','min','p50','p90','p95','p99','p50_estimate','p90_estimate','p95_estimate','p99_estimate','max','std','count','total','rate'] if k in keys]
            rest=sorted(keys-set(main))
            for cols in [main,rest]:
                if cols:server.append(table(['指标','单位','标签',*cols],([name,unit,label,*[v.get(k) for k in cols]] for name,unit,label,v in series)))

stamp=datetime.fromisoformat(core['captured_at']).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
report=['# GLM-5.3-Flash-W8A8 / C500 已完成性能数据\n',
    f'快照时间：**{stamp}（北京时间）**。共 **{len(entries)} 个有效测点、{verification["requests"]:,} 个计分请求**。测试仍在继续，本报告是该时刻已完成数据的固定快照。\n',
    '## 文件导航\n',
    '- [客户端全部指标：平均数、全部已有分位数及计数](client-metrics.md)\n- [服务端全部指标：按 engine/标签保留](server-metrics.md)\n- [服务端标签索引](server-labels.md)\n- [来源与校验记录](verification.json)\n',
    '## 统计口径\n',
    '- 输入 4096 / 16384 / 65536 tokens，输出 20 / 50 tokens；并发 1、2、4、8、16、32、64、128；每个计分点严格 **4 × 并发** 个请求。\n'
    f'- 本报告已完成点的独立预热共 {warmup_requests:,} 个请求，单点为 max(4, 并发)，与计分数据分开。已完成的轮次编号为 {sorted(set(e["ledger_entry"]["repetition"] for e in entries))}；逐行展示实际轮次，不把单轮结果当作 3 轮重复统计。\n'
    '- 允许正常 Prefill；TPOT = (客户端端到端耗时 − TTFT) / (实际输出 tokens − 1)。Decode 耗时为端到端耗时减去 TTFT。包含客户端传输及并发调度影响，不是隔离的设备 Decode。\n'
    '- 客户端请求级分位数采用 (N−1)×q 线性插值；P99 在低并发的小样本下仅作描述统计。服务端 histogram 分位数为桶估计，明确保留 `_estimate` 后缀。\n'
    '- 保留 avg、min、max、std、count、sum 及 P1/P5/P10/P25/P50/P75/P90/P95/P99 等全部实际导出字段；缺失项用 —，不补零、不制造分位数。\n'
    '- 不跨不同输入/输出/并发点混合计算一个全局延迟均值，也不把各点分位数再平均。全部统计在各测点内展示。\n'
    '- AIPerf 原生吞吐与项目重算吞吐的计时窗口略有差异，两者分别保留；完整窗口吞吐包含 Prefill，不称为纯 Decode 吞吐。\n'
    '- `effective_*` / `active_*` 是 AIPerf 客户端派生指标，不能解释为 GPU 利用率；`reasoning_token_count` 为实际服务上报的推理 token。短输出并不保证完成最终回答。\n'
    '- 本轮没有成功采集 GPU 遥测端点，因此没有真实 GPU 利用率、显存带宽、功耗和温度结果；服务端 KV cache 比例及进程内存不能替代这些指标。\n'
    '- 本次是性能采集，不表示模型绝对精度验收或 SLA 达标。失败、用户跳过、执行中不计入有效性能表。\n',
    '## 五种部署覆盖情况\n']
states=core['ledger']['runs']
coverage=[]
for dep,name in layouts.items():
    c=Counter(r['status'] for r in states if r['deployment']==dep)
    success=c['completed'];fail=c['failed']+c['invalid']+c['unverified']+c['completed_with_errors'];skip=c['skipped_by_user']+c['skipped_failed_configuration']+c['skipped_startup_failure'];running=c['profiling']+c['starting']
    coverage.append([name,144,success,fail,c['skipped_by_user'],c['skipped_failed_configuration'],running,144-success-fail-skip-running])
report.append(table(['部署','计划','成功','失败','用户跳过','失败后跳过','执行中','待执行'],coverage))
report.append('五种部署完整矩阵为 **720 点**；原 TP4/DP2/EP8 与 TP2/DP4/EP8 两种部署为 288 点，新增三种为 432 点，目前尚未产生成功结果。\n')
report.append('## 指标速查\n'+table(['名称 / 原始字段','含义与限制'],[
    ['TTFT / time_to_first_token','请求开始至首 token 的客户端耗时，含排队、Prefill 和传输。'],
    ['TPOT / inter_token_latency','每个请求的首 token 后平均 token 间隔；表中分位数针对这些请求级均值。'],
    ['decode_duration','每个请求的 E2E − TTFT；不代表隔离的设备内核耗时。'],
    ['request_latency','客户端完整请求端到端耗时。'],
    ['time_to_second_token','AIPerf 上报的首 token 到第二 token 间隔，不与 TTFT 混用。'],
    ['inter_chunk_latency','流式响应分块之间间隔；样本数通常多于请求数，不保证分块等于 token。'],
    ['output_token_throughput_per_user','单请求首 token 后 token 速率；分位数针对请求级速率。'],
    ['e2e_output_token_throughput','每个请求输出 tokens / 完整 E2E；单位 tokens/sec/user。'],
    ['prefill_throughput_per_user','AIPerf 按输入 tokens 与 TTFT 派生的单用户速率，包含排队影响，不是纯 Prefill 算力。'],
    ['request_throughput / *_token_throughput','完整采集窗口请求或 token 速率；见来源区分项目重算值与 AIPerf 原生值。'],
    ['effective_* / active_* / tokens_in_flight','AIPerf 时序派生指标；保留原始值，不解释为硬件利用率或纯算子吞吐。'],
    ['http_req_*','客户端 HTTP 连接、发送、等待、接收、数据量及复用指标，单位逐行标注。'],
    ['usage_* / total_* / *_sequence_length','服务上报或客户端统计的 token 用量、长度、总量；保留原始字段名区分。'],
    ['vllm:* / process_* / http_*','服务端 Prometheus 指标；按 engine 等标签独立展示。'],
    ['avg / count / sum / std','均值、统计样本数、合计和标准差；仅有 avg 的整体量或总量不代表逐请求均值。'],
    ['P1…P99 / *_estimate','客户端已有分位数或 Gauge 采样分位数；带 estimate 的 Histogram 分位数仅为桶估计。']]))
report.append('## 各点主要指标\n\n以下延迟以 ms 表示，吞吐以 tokens/s 或 requests/s 表示；每一行对应一次实际完成的重复。\n')
for dep,name in layouts.items():
    rows=[x for x in overview if x['row']['deployment']==dep]
    if not rows:continue
    report.append(f'### {name}\n')
    report.append(table(['输入','输出','并发','轮次','成功请求','TPOT均值 ms','TPOT P95 ms','TTFT均值 ms','E2E均值 ms','输出吞吐 tokens/s','请求吞吐 req/s','详情'],
        ([x['dm']['input_tokens'],x['dm']['output_tokens'],x['row']['concurrency'],x['row']['repetition'],x['n'],x['dec']['tpot_ms']['mean'],x['dec']['tpot_ms']['p95'],x['summary']['statistics']['ttft']['mean'],x['summary']['statistics']['e2e_latency']['mean'],x['summary']['rates']['output_token_throughput'],x['summary']['rates']['request_throughput'],f"[{x['anchor']}](client-metrics.md#{x['anchor']})"] for x in rows)))
report.append('## 核心延迟分位数\n')
for metric,label in [('inter_token_latency','TPOT（请求级平均 token 间隔）'),('time_to_first_token','TTFT'),('request_latency','端到端耗时'),('decode_duration','首 token 后 Decode 耗时')]:
    report.append(f'### {label} / ms\n')
    cols=['avg','min','p1','p5','p10','p25','p50','p75','p90','p95','p99','max','std']
    report.append(table(['测点','部署','输入→输出','并发',*cols],
        ([f"[{x['anchor']}](client-metrics.md#{x['anchor']})",layouts[x['row']['deployment']],f"{x['dm']['input_tokens']}→{x['dm']['output_tokens']}",x['row']['concurrency'],*[x['native'][metric].get(k) for k in cols]] for x in overview)))
report.append('## 失败与跳过记录\n')
abnormal=[]
for r in states:
    if r['status'] in {'failed','invalid','unverified','completed_with_errors','skipped_by_user','skipped_failed_configuration','skipped_startup_failure'}:
        evidence=r.get('failure_evidence',{});abnormal.append([layouts[r['deployment']],r['scenario'],r['concurrency'],r['repetition'],r['status'],r.get('directory') or evidence.get('directory'),evidence.get('sha256')])
report.append(table(['部署','场景','并发','轮次','状态','Run / 失败来源','证据 SHA256'],abnormal))
report.append('`skipped_after_failure` 在旧批次中表示此前中断留下的待执行点，已在覆盖表计为待执行，不误记为最终跳过。用户跳过记录保留原失败数据；失败后的其余重复不重试。\n')
report.append('状态含义：`failed` 为实际执行失败；`skipped_by_user` 为用户指定跳过；`skipped_failed_configuration` 为该配置失败后跳过其余重复。失败和跳过项没有有效性能值，不填零。\n')
report.append('## 测点索引\n'+table(['编号','部署','输入','输出','并发','轮次','全部指标','Run ID'],detail_index))
report.append('## 数据来源\n'+f"- 远端：`{core['host']}:{core['batch']}`。\n- 核心快照：`{manifest['core']['path']}`；SHA256 `{manifest['core']['sha256']}`。\n- 服务端指标补充包：`metric-details.json.gz`；SHA256 `{manifest['details']['sha256']}`。\n- 已核对原始文件哈希、4×并发计数、请求 ID、输入输出长度和核心延迟统计；客户端逐请求可重算统计另核对 {checked:,} 项。\n")
report.append(f'- 实际计分客户端指标名称 {len(client_metric_names)} 种；计分及预热服务端指标名称 {len(server_metric_names)} 种，服务端序列记录共 {server_series_count:,} 条（同指标不同标签分别保留）。\n')
labels_doc=['# 服务端序列标签\n','[返回总览](README.md)\n']
for label,text in sorted(labels.items()):labels_doc.extend([f'<a id="{label.lower()}"></a>\n',f'## {label}\n',f'```json\n{json.dumps(json.loads(text),ensure_ascii=False,indent=2)}\n```\n'])
for name,lines in [('README.md',report),('client-metrics.md',client),('server-metrics.md',server),('server-labels.md',labels_doc)]:
    content='\n'.join(lines)
    assert '\ufffd' not in content
    (DEST/name).write_text(content,encoding='utf-8')
result=dict(captured_at=core['captured_at'],completed_points=len(entries),scored_requests=verification['requests'],warmup_requests=warmup_requests,
    core_sha256=manifest['core']['sha256'],details_sha256=manifest['details']['sha256'],independent_stat_checks=checked,
    client_metric_names=sorted(client_metric_names),client_stat_fields=sorted(native_fields),server_metric_names=sorted(server_metric_names),
    server_stat_fields=sorted(all_server_stat_fields),server_series_count=server_series_count,labels=len(labels),
    markdown_files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in DEST.glob('*.md')})
(DEST/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if not k.endswith('_names') and not k.endswith('_fields')},ensure_ascii=True))
