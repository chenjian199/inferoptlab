"""Rebuild the offline review tables. Reads frozen evidence; never contacts a server."""
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'issue'
sources = {}


def read(path):
    p = ROOT / path
    data = p.read_bytes()
    sources[path] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    return data


def js(path):
    return json.loads(read(path))


def csv_rows(path):
    return list(csv.DictReader(read(path).decode('utf-8-sig').splitlines()))


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---']*len(headers)) + '|'] +
                     ['| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows])


def fmt(v):
    return '—' if v is None else f'{v:.3f}'


rows = []
read('outputs/TP8_耗时占比与优化方向分析.md')


def add(source, layout, inp, output, concurrency, repetitions, requests, ttft, tpot, e2e, tok, req, note='', point_ids=None):
    rows.append(dict(source=source, layout=layout, input_tokens=inp, output_tokens=output,
                     concurrency=concurrency, repetitions=repetitions, requests=requests,
                     ttft_mean_ms=ttft[0], ttft_p95_ms=ttft[1], tpot_mean_ms=tpot[0], tpot_p95_ms=tpot[1],
                     e2e_mean_ms=e2e[0], e2e_p95_ms=e2e[1], output_tok_s=tok, request_s=req,
                     note=note, point_ids=point_ids or []))


# The latest frozen old scan, not every overlapping snapshot.
m = js('outputs/glm53-short-output-20261126/markdown-source.json')
archive_path = m['core']['path'].replace('\\', '/')
b = read(archive_path)
assert hashlib.sha256(b).hexdigest() == m['core']['sha256']
archive = json.loads(gzip.decompress(b))
records = {r['ledger_entry']['directory']: r for r in archive['runs']}
old_count = 0
for r in archive['ledger']['runs']:
    if r['status'] != 'completed':
        continue
    f = records[r['directory']]['files']
    for name in ['summary.json', 'decode.json']:
        assert hashlib.sha256(f[name]['text'].encode()).hexdigest() == f[name]['sha256']
    s = json.loads(f['summary.json']['text'])
    assert s['validity'] == 'valid' and s['counts']['succeeded'] == r['concurrency']*4
    st = s['statistics']
    pair = lambda k: (st[k]['mean'], st[k]['p95'])
    layout = 'TP4/DP2/EP8 eager' if 'tp4' in r['deployment'] else 'TP2/DP4/EP8 eager'
    add('A 60含Prefill旧扫描', layout, int(st['input_tokens']['mean']), int(st['output_tokens']['mean']),
        r['concurrency'], r['repetition'], s['counts']['succeeded'], pair('ttft'), pair('tpot'), pair('e2e_latency'),
        s['rates']['output_token_throughput'], s['rates']['request_throughput'],
        'TPOT排除本请求首token；可能受其它请求Prefill干扰', [r['trial_id']])
    old_count += 1
assert old_count == 91

cached = js('outputs/glm53-cached-decode-20261126/quick-read.json')
for g in cached['groups']:
    pair = lambda k: (g[k]['mean_ms'], g[k]['p95_ms'])
    add('B 60缓存Decode r3', 'TP1/DP8/EP8 eager', g['input_tokens'], g['output_tokens'], g['concurrency'],
        g['repetitions'], g['requests'], pair('ttft'), pair('tpot'), pair('e2e'), g['output_throughput']['mean'],
        g['request_throughput']['mean'], '3轮请求合并分位数；速率按累计时长', g['point_ids'])
assert len(cached['groups']) == 26

tp8 = read('outputs/TP8.md').decode('utf8')
tp8_rows = []
for line in tp8.splitlines():
    if not re.match(r'\| (4K|16K|64K) \|', line):
        continue
    cells = [x.strip() for x in line.strip('|').split('|')]
    if len(cells) != 9:
        continue
    vals = [[float(x.strip()) for x in cells[i].split('/')] for i in [4,5,6]]
    rep,n = map(int,cells[3].split('/'))
    layout = 'TP8 EP关 graph' if len(tp8_rows) < 9 else 'TP8/EP8 graph'
    add('C 61同事TP8', layout, int(cells[0][:-1])*1024, int(cells[1]), int(cells[2]), rep, n,
        vals[0], vals[1], [x*1000 for x in vals[2]], float(cells[7]), float(cells[8]), '从舍入MD值提取；精确原始数据见环境核对')
    tp8_rows.append(rows[-1])
assert len(tp8_rows) == 18

tp4 = csv_rows('outputs/tp4_dp2_ep1_summary.csv')
for r in tp4:
    if r['status'] != 'completed':
        continue
    # CSV labels this ITL; do not invent TPOT percentiles or silently equate distributions.
    ttft = float(r['ttft_avg_ms']); e2e = float(r['latency_avg_ms']); output = int(r['output_tokens'])
    calculated_tpot = (e2e-ttft)/(output-1)
    assert abs(calculated_tpot-float(r['itl_avg_ms'])) < 1e-8
    assert abs(float(r['output_throughput_tok_s'])-output*float(r['request_throughput_req_s'])) < 1e-8
    add('D 同事TP4 DP2 EP关', 'TP4/DP2 EP关 graph', int(r['context_tokens']), output, int(r['concurrency']), 1,
        int(r['request_count']), [ttft,None], [calculated_tpot,None], [e2e,None],
        float(r['output_throughput_tok_s']), float(r['request_throughput_req_s']),
        '均值由(E2E−TTFT)/(O−1)校验；原CSV无P95，未插值补造；缺原始请求与完整运行快照', [r['artifact_directory']])

md64 = read('outputs/README-ep8.md').decode('utf8')
for line in md64.splitlines():
    if not line.startswith('| local64-'):
        continue
    c = [x.strip() for x in line.strip('|').split('|')]
    add('E 64同事DP8 EP开', 'TP1/DP8/EP8 模式待核', int(c[1]), int(c[2]), int(c[3]), int(c[4]), int(c[5]),
        [float(c[10]),None], [float(c[6]),float(c[8])], [None,None], float(c[11]),None,
        '逐轮MD；未用TPOT反推缺失E2E，未补造请求速率')

prof = js('outputs/glm53-tp2-dp4-ep8-profiler-20261126/results.json')
for r in prof:
    p = r['control']; pair = lambda k:(p[k]['avg'],p[k]['p95'])
    add('F 60图模式配对control', 'TP2/DP4/EP8 graph', r['input_tokens'], 200, 4, 1, int(p['request_count']['avg']),
        pair('time_to_first_token'), pair('inter_token_latency'), pair('request_latency'),
        p['output_token_throughput']['avg'],p['request_throughput']['avg'],
        'control未启用采样；另有32步profile，不纳入性能对比',[r['scenario']])

# Earlier 512-token outputs are a separate protocol, not duplicates of the short-output scan.
long_output = js('outputs/glm53-decode-20261125/tables.json')
assert len(long_output['results']) == 7 and len(long_output['requests']) == 508
def percentile95(values):
    values=sorted(values); pos=(len(values)-1)*.95
    return values[math.floor(pos)]+(values[math.ceil(pos)]-values[math.floor(pos)])*(pos-math.floor(pos))
for r in long_output['results']:
    requests=[q for q in long_output['requests'] if q[5]==r[19]]
    assert len(requests)==r[5]==4*r[3] and r[7]==0
    tpots=[(q[12]-q[11])/(q[10]-1) for q in requests]
    assert abs(sum(tpots)/len(tpots)-r[8])<1e-8 and abs(percentile95(tpots)-r[10])<1e-8
    add('G 60历史512输出扫描',r[0]+' eager',r[1],r[2],r[3],r[4],r[5],
        [r[13],percentile95([q[11] for q in requests])],[r[8],r[10]],
        [r[14]*1000,percentile95([q[12] for q in requests])],r[15],r[5]/r[16],
        '4K/512，含Prefill；独立旧批次；由原逐请求表重算P95',[r[19]])

# Reconcile the user's three profiler exports independently.
families = csv_rows('outputs/families.csv')
ranks = csv_rows('outputs/ranks.csv')
kernels = csv_rows('outputs/kernels(1).csv')
assert (len(families),len(ranks),len(kernels)) == (60,80,9936)
assert len({(r['case'],r['rank'],r['kernel']) for r in kernels}) == len(kernels)
by_rank = defaultdict(lambda:[0,0.0])
by_family = defaultdict(float)
by_case = defaultdict(float)
for r in kernels:
    by_rank[r['case'],r['rank']][0] += int(r['calls'])
    by_rank[r['case'],r['rank']][1] += float(r['sum_ms'])
    by_family[r['case'],r['family']] += float(r['sum_ms'])
    by_case[r['case']] += float(r['sum_ms'])
for r in ranks:
    calls,ms=by_rank[r['case'],r['rank']]
    assert calls==int(r['gpu_kernel_calls']) and abs(ms-float(r['sum_kernel_ms']))<.002
for r in families:
    assert abs(by_family[r['case'],r['family']]-float(r['sum_rank_ms']))<.002
    assert abs(100*by_family[r['case'],r['family']]/by_case[r['case']]-float(r['share_pct']))<.006
ep_delta=[]
for case in sorted(c for c in by_case if c.startswith('off')):
    on=case.replace('off','on',1);delta=by_case[on]-by_case[case]
    cd=by_family[on,'collective']-by_family[case,'collective']
    ep_delta.append(dict(case=case,total_off_rank_ms=by_case[case],total_on_rank_ms=by_case[on],
                         delta_rank_ms=delta,collective_delta_rank_ms=cd,collective_share_of_delta_pct=100*cd/delta))

# XLSX is a companion view, not an additional experiment. Read cells without modifying the workbook.
book_path='outputs/TP8_耗时与优化分析.xlsx'
read(book_path)
with zipfile.ZipFile(ROOT/book_path) as z:
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    wb=ET.fromstring(z.read('xl/workbook.xml'))
    sheets=[e.attrib['name'] for e in wb.findall('s:sheets/s:sheet',ns)]
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        strings=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    sheet_previews={}
    for name in sorted(n for n in z.namelist() if re.fullmatch(r'xl/worksheets/sheet\d+.xml',n)):
        tree=ET.fromstring(z.read(name)); preview=[]
        for row in tree.findall('s:sheetData/s:row',ns)[:10]:
            cells=[]
            for cell in row:
                v=cell.find('s:v',ns);text=v.text if v is not None else ''.join(cell.find('s:is',ns).itertext()) if cell.find('s:is',ns) is not None else ''
                if cell.attrib.get('t')=='s':text=strings[int(text)]
                cells.append(text)
            preview.append(cells)
        sheet_previews[name]=preview
(ROOT/'outputs/optimization-review-20261126/workbook-preview.json').write_text(json.dumps(dict(sheets=sheets,previews=sheet_previews),ensure_ascii=False,indent=2),encoding='utf8')

# Twenty-four individual GPU traces; no rank-ms converted to wall time.
manifest = js('outputs/glm53-tp2-dp4-ep8-profiler-20261126/operators/manifest.json')
assert len(manifest)==24
profile_families=[]
for item in manifest:
    assert item['graph_replay_events']=={'mcGraphLaunch':32}
    assert item['annotations']=={'execute_context_0(0)_generation_1(1)':32}
    if '_dp0_pp0_tp0_' not in item['summary']:continue
    summary=js('outputs/glm53-tp2-dp4-ep8-profiler-20261126/operators/'+item['summary'])
    bucket=defaultdict(lambda:[0,0.0])
    for op in summary['operators']:
        if op['kind']!='gpu_kernel':continue
        bucket[op['family_hint']][0]+=op['calls'];bucket[op['family_hint']][1]+=op['total_ms']
    total=sum(v[1] for v in bucket.values())
    assert total > 0 and sum(v[0] for v in bucket.values()) == 79712
    memory_ops=[op for op in summary['operators'] if op['kind'] in ('gpu_memcpy','gpu_memset')]
    trace_path='outputs/glm53-tp2-dp4-ep8-profiler-20261126/run-r2/server/observations/profiles/'+item['summary'].replace('-summary.json','.json.gz')
    raw_trace=json.loads(gzip.decompress(read(trace_path)))
    events=[e for e in raw_trace['traceEvents'] if e.get('cat') in ('kernel','gpu_memcpy','gpu_memset') and e.get('ph')=='X']
    intervals=sorted((e['ts'],e['ts']+e['dur']) for e in events)
    assert {e['args']['device'] for e in events} == {0}
    start,end=intervals[0];covered=0
    for a,b in intervals[1:]:
        if a>end:covered+=end-start;start,end=a,b
        else:end=max(end,b)
    covered+=end-start
    span=max(b for a,b in intervals)-intervals[0][0]
    memsets=Counter((e['args'].get('bytes'),e['name']) for e in events if e['cat']=='gpu_memset')
    profile_families.append(dict(trace=item['summary'],total_ms=total,
        memory_ops=memory_ops,
        all_recorded_gpu_activity_union_ms=covered/1000,all_recorded_gpu_activity_span_ms=span/1000,
        uncovered_in_recorded_gpu_span_ms=(span-covered)/1000,
        memset_sizes=[dict(bytes=k[0],name=k[1],calls=v) for k,v in memsets.items()],
        families={k:dict(calls=v[0],ms=v[1],share_pct=100*v[1]/total) for k,v in bucket.items()}))

assert len({(r['source'],r['layout'],r['input_tokens'],r['output_tokens'],r['concurrency'],r['repetitions']) for r in rows})==len(rows)
audit=dict(source_counts=dict(Counter(r['source'] for r in rows)),total_summary_rows=len(rows),
    old_scan_scored_requests=sum(r['requests'] for r in rows if r['source'].startswith('A ')),
    tp8_profile=dict(cases=len(by_case),ranks=len(ranks),kernels=len(kernels),families=len(families)),
    ep_deltas=ep_delta,profile_families=profile_families,workbook_sheets=sheets,sources=sources)
(OUT/'evidence-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'measurements.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# 部署测点明细','',
       '由 `python issue/analyze_evidence.py` 从冻结数据生成。按来源和口径分组，禁止跨组直接计算部署加速比。',
       '延迟单位 ms；单元格为均值 / P95。— 表示原来源缺失。TPOT 是请求级均值的分布，不是逐 token ITL 分布。',
       'D 组只有 ITL 标签及均值关系校验，原始逐请求定义待补齐；表中 TPOT 均值为 (E2E均值−TTFT均值)/(O−1)。',
       'E 组逐轮展示，其重复列是轮次编号；B 组重复列是合并的轮数。','']
for source in sorted(set(r['source'] for r in rows)):
    lines.extend(['## '+source,''])
    selected=sorted([r for r in rows if r['source']==source],key=lambda r:(r['layout'],r['input_tokens'],r['output_tokens'],r['concurrency'],r['repetitions']))
    lines.append(table(['部署','输入/输出','并发','重复/请求','TTFT','TPOT','E2E','输出 tok/s','请求 req/s'],
        [[r['layout'],f"{r['input_tokens']}/{r['output_tokens']}",r['concurrency'],f"{r['repetitions']}/{r['requests']}",
          *(f"{fmt(r[k+'_mean_ms'])} / {fmt(r[k+'_p95_ms'])}" for k in ['ttft','tpot','e2e']),fmt(r['output_tok_s']),fmt(r['request_s'])] for r in selected]))
    lines.append('')
(OUT/'measurements.md').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps({k:audit[k] for k in ['source_counts','total_summary_rows','old_scan_scored_requests','tp8_profile','workbook_sheets']},ensure_ascii=True))
