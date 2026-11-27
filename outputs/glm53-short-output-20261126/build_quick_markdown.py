"""Build a compact side-by-side view of the same frozen Markdown snapshot."""
from collections import Counter
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import json
from pathlib import Path
import zipfile

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
DEST=OUT/'markdown'
manifest=json.loads((OUT/'markdown-source.json').read_text(encoding='utf-8'))
payload=(ROOT/manifest['core']['path']).read_bytes()
assert hashlib.sha256(payload).hexdigest()==manifest['core']['sha256']
archive=json.loads(gzip.decompress(payload))
verification=json.loads((DEST/'verification.json').read_text(encoding='utf-8'))
assert verification['core_sha256']==manifest['core']['sha256']
deps=['glm53-vllm-decode-tp4-dp2-ep8','glm53-vllm-decode-tp2-dp4-ep8']
names=['TP4/DP2/EP8','TP2/DP4/EP8']
ledger={(r['deployment'],r['scenario'],r['concurrency'],r['repetition']):r for r in archive['ledger']['runs']}
records={e['ledger_entry']['directory']:e for e in archive['runs']}
completed=[r for r in archive['ledger']['runs'] if r['status']=='completed']
assert {r['repetition'] for r in completed}=={1},'This compact report is explicitly first-round only'
assert len(completed)==verification['completed_points']
for e in records.values():
    for item in e['files'].values():
        assert hashlib.sha256(item['text'].encode()).hexdigest()==item['sha256']

def values(row):
    f=records[row['directory']]['files']
    s=json.loads(f['summary.json']['text']);d=json.loads(f['decode.json']['text'])
    assert s['counts']['succeeded']==4*row['concurrency'] and s['validity']=='valid'
    return d['tpot_ms']['mean'],d['tpot_ms']['p95'],s['statistics']['ttft']['mean']/1000,s['rates']['output_token_throughput']

paired=[]
for key,row in ledger.items():
    dep,scene,c,rep=key
    other=ledger.get((deps[1],scene,c,rep))
    if dep==deps[0] and row['status']=='completed' and other and other['status']=='completed':
        paired.append((values(row),values(other)))
counts=Counter(r['deployment'] for r in completed)
stamp=datetime.fromisoformat(archive['captured_at']).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
lines=['# GLM-5.3-Flash / C500 性能简版','',
    f'**{stamp} 快照 · {len(completed)} 个有效测点 · {verification["scored_requests"]:,} 个计分请求 · 当前均为第 1 轮**','',
    f'- {names[0]} 完成 **{counts[deps[0]]}** 点；{names[1]} 完成 **{counts[deps[1]]}** 点。TP8、TP8/EP8、TP1/DP8/EP8 尚无结果。',
    f'- {len(paired)} 组相同负载的有效配对中，TP4 的平均 TPOT 较低 **{sum(a[0]<b[0] for a,b in paired)}** 组，输出吞吐较高 **{sum(a[3]>b[3] for a,b in paired)}** 组。结果随负载变化，暂不能认定一种部署全面更优。',
    '- 下表每行按相同并发比较两种部署；每个计分点请求数 = **4 × 并发**。失败、跳过和进行中的点不填性能值。','',
    '**怎么看：** TPOT 为“平均 / P95”，单位 ms，越低越好；TTFT 为平均首 token 延迟，单位 s；输出吞吐单位 tokens/s，越高越好。输出吞吐按包含 Prefill 的完整请求窗口计算，TPOT 统计首 token 之后的平均间隔。','',
    '[完整分位数与口径](README.md) · [客户端全部指标](client-metrics.md) · [服务端全部指标](server-metrics.md)','']
status={'failed':'失败','skipped_by_user':'用户跳过','skipped_failed_configuration':'失败后跳过','profiling':'测试中','starting':'启动/预热中','skipped_after_failure':'待执行','pending':'待执行'}
shown=0
for inp in [4,16,64]:
    for out in [20,50]:
        scene=f'glm53-vllm-decode-{inp}k-{out}'
        lines.extend([f'## {inp}K 输入 → {out} tokens 输出','',
            '| 并发 | TP4 TPOT 均值 / P95 (ms) | TP4 TTFT (s) | TP4 吞吐 (tokens/s) | TP2 TPOT 均值 / P95 (ms) | TP2 TTFT (s) | TP2 吞吐 (tokens/s) |',
            '| --- | --- | --- | --- | --- | --- | --- |'])
        for c in [1,2,4,8,16,32,64,128]:
            cells=[str(c)]
            for dep in deps:
                row=ledger[(dep,scene,c,1)]
                if row['status']=='completed':
                    avg,p95,ttft,throughput=values(row)
                    cells.extend([f'{avg:.2f} / {p95:.2f}',f'{ttft:.2f}',f'{throughput:.2f}']);shown+=1
                else:cells.extend([status[row['status']],'—','—'])
            lines.append('| '+' | '.join(cells)+' |')
        lines.append('')
lines.extend(['## 当前异常点','',
    '- **TP4/DP2/EP8：** 4K → 50、并发 128 失败。',
    '- **TP2/DP4/EP8：** 16K → 50、并发 64 和 128 失败；4K → 50、并发 128 按用户要求跳过。',
    '- 失败配置的其余重复已跳过；原始失败证据保留。TP4 的 64K → 50、并发 128 在此快照时尚未完成。','',
    '这是单轮阶段数据；低并发点样本少，P95/P99 仅作描述统计。尚未完成三轮扫描，也不代表精度或 SLA 验收通过。GPU 功耗、温度、利用率等遥测本轮未采集到。',''])
assert shown==len(completed)
target=DEST/'quick-read.md'
content='\n'.join(lines)
assert '\ufffd' not in content
target.write_text(content,encoding='utf-8')
readme=DEST/'README.md'
full=readme.read_text(encoding='utf-8')
link='- [简版：两种部署并排快速阅读](quick-read.md)\n'
if link not in full:full=full.replace('## 文件导航\n\n','## 文件导航\n\n'+link)
readme.write_text(full,encoding='utf-8')
for p in [target,readme]:
    verification['markdown_files'][p.name]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
verification['quick_read']=dict(points=shown,paired_points=len(paired),repetition=1,rows=48)
(DEST/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
bundle=OUT/'GLM53-C500-completed-Markdown.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,'markdown/'+str(p.relative_to(DEST)))
with zipfile.ZipFile(bundle) as z:assert z.testzip() is None
print(json.dumps(dict(path=str(target),points=shown,paired=len(paired),lines=len(lines),bytes=target.stat().st_size),ensure_ascii=True))
