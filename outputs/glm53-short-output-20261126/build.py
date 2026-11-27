"""Rebuild the short-output workbook from a hash-verified evidence snapshot.

Fallback authoring: the bundled Artifact Tool cannot load skia.node on this host.
Run with the bundled Python. This reads backups only and never contacts the server.
"""
from collections import Counter
from datetime import datetime, timezone, timedelta
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import xlsxwriter
import openpyxl
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
archives=[];receipts=[];checks=[]
stage_layouts={
    'original':{'glm53-vllm-decode-tp2-dp4-ep8','glm53-vllm-decode-tp4-dp2-ep8'},
    'additional':{'glm53-vllm-decode-tp8','glm53-vllm-decode-tp8-ep8','glm53-vllm-decode-tp1-dp8-ep8'},
}
for stage,directory in [('original','glm53-short-output-collected-20261125'),
                        ('additional','glm53-additional-output-collected-20261125')]:
    evidence=ROOT/'experiments/evidence'/directory
    if stage=='additional' and not (evidence/'latest.json').exists():continue
    receipt=json.loads((evidence/'latest.json').read_text(encoding='utf-8'))
    payload=(ROOT/receipt['path']).read_bytes()
    assert hashlib.sha256(payload).hexdigest()==receipt['sha256']
    archive=json.loads(gzip.decompress(payload))
    check=json.loads((evidence/'local-verification.json').read_text(encoding='utf-8'))
    assert check['archive_sha256']==receipt['sha256']
    assert archive.get('stage','original')==stage
    assert len(archive['ledger']['runs'])==len(stage_layouts[stage])*144
    assert {row['deployment'] for row in archive['ledger']['runs']}==stage_layouts[stage]
    for collection in [archive['files'],*[r['files'] for r in archive['runs']+archive.get('historical_runs',[])]]:
        for item in collection.values():
            assert hashlib.sha256(item['text'].encode('utf-8')).hexdigest()==item['sha256']
    archives.append(archive);receipts.append(dict(receipt,stage=stage));checks.append(check)
data=dict(ledger=dict(runs=[row for archive in archives for row in archive['ledger']['runs']]),
          runs=[row for archive in archives for row in archive['runs']],
          captured_at=max((a['captured_at'] for a in archives),key=datetime.fromisoformat))
verification=dict(completed=sum(c['completed'] for c in checks),requests=sum(c['requests'] for c in checks))

layouts={'glm53-vllm-decode-tp8':'TP8','glm53-vllm-decode-tp8-ep8':'TP8/EP8',
         'glm53-vllm-decode-tp4-dp2-ep8':'TP4/DP2/EP8','glm53-vllm-decode-tp2-dp4-ep8':'TP2/DP4/EP8',
         'glm53-vllm-decode-tp1-dp8-ep8':'TP1/DP8/EP8'}
scenes={f'glm53-vllm-decode-{i}k-{o}':(i*1024,o) for i,o in itertools.product([4,16,64],[20,50])}
plan=(ROOT/'recipes/plans/benchmark/glm53-vllm/decode-five-layouts.yaml').read_text(encoding='utf-8')
assert set(re.findall(r'^- id: (.+)$',plan.split('deployment_refs:')[1].split('scenario_refs:')[0],re.M))==set(layouts)
assert set(re.findall(r'^- id: (.+)$',plan.split('scenario_refs:')[1].split('mode:')[0],re.M))==set(scenes)
def key(r):return r['deployment'],r['scenario'],r['concurrency'],r['repetition']
ledger={key(r):r for r in data['ledger']['runs']}
assert len(ledger)==len(data['ledger']['runs'])==sum(len(stage_layouts[r['stage']])*144 for r in receipts)
assert set(ledger).issubset(set(itertools.product(layouts,scenes,[1,2,4,8,16,32,64,128],[1,2,3])))
captured=datetime.fromisoformat(data['captured_at']).astimezone(timezone(timedelta(hours=8)))
stamp=captured.strftime('%Y-%m-%d %H:%M:%S')
records={r['ledger_entry']['directory']:r for r in data['runs']}
assert len(records)==len(data['runs']),'duplicate run directories across evidence batches'
stage_names={'original':'原两种部署','additional':'新增三种部署'}
source_note='批次快照：'+'；'.join(stage_names[r['stage']]+' '+datetime.fromisoformat(r['captured_at']).astimezone(timezone(timedelta(hours=8))).strftime('%m-%d %H:%M:%S') for r in receipts)
if len(receipts)==1:source_note+='；新增三种部署尚未采集。'
status_names={'completed':'成功','failed':'失败','invalid':'失败','unverified':'失败',
              'completed_with_errors':'失败','skipped_by_user':'用户跳过',
              'skipped_failed_configuration':'失败后跳过','skipped_startup_failure':'启动失败跳过',
              'profiling':'执行中','starting':'执行中','pending':'待执行',
              'skipped_after_failure':'待执行','skipped_budget':'预算未执行'}
matrix=[]
for dep,scene,c,rep in itertools.product(layouts,scenes,[1,2,4,8,16,32,64,128],[1,2,3]):
    row=ledger.get((dep,scene,c,rep));inp,out=scenes[scene]
    status=status_names[row['status']] if row else '待执行'
    run=row.get('directory') if row else None
    reason=''
    if row and row.get('failure_evidence'):reason='同配置失败记录：'+row['failure_evidence']['directory']
    if row and status=='用户跳过':reason='用户要求跳过该配置的三轮重复；原失败记录保留。'
    if row and status=='失败' and run in records:
        reason=json.loads(records[run]['files']['run.json']['text']).get('error') or reason
    if row and status=='启动失败跳过':
        reason='启动资格验证失败；证据 SHA256：'+row['startup_failure']['receipt_sha256']
    matrix.append([layouts[dep],inp,out,c,rep,4*c,status,reason,run,row['trial_id'] if row else None])
assert len(matrix)==720
counts=Counter(r[6] for r in matrix)
results=[];requests=[]
for item in data['runs']:
    row=item['ledger_entry']
    if row['status']!='completed':continue
    f=item['files'];record=json.loads(f['run.json']['text']);summary=json.loads(f['summary.json']['text']);decode=json.loads(f['decode.json']['text'])
    inp,out=scenes[row['scenario']];layout=layouts[row['deployment']]
    assert summary['validity']=='valid' and decode['eligible_for_performance_comparison']
    t=decode['tpot_ms'];s=summary['statistics']
    results.append([layout,inp,out,row['concurrency'],row['repetition'],summary['counts']['planned'],summary['counts']['succeeded'],
                    t['mean'],t['p50'],t['p95'],t['p99'],decode['post_first_token_ms']['mean']/1000,
                    s['ttft']['mean'],s['e2e_latency']['mean']/1000,summary['rates']['output_token_throughput'],row['directory']])
    for line in f['raw/aiperf/profile_export.jsonl']['text'].splitlines():
        if not line.strip():continue
        native=json.loads(line);m=native['metrics'];ttft=m['time_to_first_token']['value'];e2e=m['request_latency']['value']
        requests.append([layout,inp,out,row['concurrency'],row['repetition'],row['directory'],native['metadata']['conversation_id'],ttft,e2e,(e2e-ttft)/1000,(e2e-ttft)/(out-1)])
assert len(results)==counts['成功']==verification['completed']
assert len(requests)==verification['requests']==sum(r[6] for r in results)
results.sort(key=lambda r:(r[0],r[1],r[2],r[3],r[4]))

target=OUT/'GLM53-C500-20_50tokens-阶段结果.xlsx'
wb=xlsxwriter.Workbook(target)
wb.set_properties({'title':'GLM-5.3-Flash-W8A8 C500 短输出阶段结果','comments':'快照截至 '+stamp+' 北京时间'})
base={'font_name':'Arial','font_size':10,'valign':'vcenter'}
normal=wb.add_format(base);integer=wb.add_format({**base,'num_format':'#,##0'})
number=wb.add_format({**base,'num_format':'#,##0.000'})
head=wb.add_format({**base,'bold':True,'bg_color':'#203864','font_color':'#FFFFFF','text_wrap':True,'align':'center'})
title=wb.add_format({**base,'font_size':16,'bold':True,'font_color':'#203864'})
note=wb.add_format({**base,'font_color':'#526174'})
warning=wb.add_format({'bg_color':'#FFF1DD','font_color':'#8A4500'})
def sheet(name):
    s=wb.add_worksheet(name);s.hide_gridlines(2);s.set_default_row(23)
    s.set_landscape();s.fit_to_pages(1,0);return s
def table(s,start,headers,rows,name,formats=None):
    cols=[{'header':h,'header_format':head,'format':(formats or {}).get(i,normal)} for i,h in enumerate(headers)]
    s.add_table(start,0,start+len(rows),len(headers)-1,{'name':name,'style':'Table Style Medium 2','columns':cols,'data':rows})
    s.set_row(start,42)
summary_sheet=sheet('性能结果');detail=sheet('逐请求明细');status_sheet=sheet('扫描状态')
summary_sheet.set_tab_color('#203864')
summary_sheet.set_column(0,0,20,normal);summary_sheet.set_column(1,6,11,integer)
summary_sheet.set_column(7,14,18,number);summary_sheet.set_column(15,15,29,normal)
summary_sheet.write('A2','GLM-5.3-Flash-W8A8 短输出阶段结果',title)
summary_sheet.write('A3',f'最新采集 {stamp} 北京时间。完整计划 720 点，当前成功 {len(results)} 点，计分请求 {len(requests):,} 个。',note)
summary_sheet.write('A4','输入 4K / 16K / 64K，输出 20 / 50 tokens。允许 Prefill，仅统计首 token 后的解码延迟。',note)
summary_sheet.write('A5','本表为已采集结果快照，未测与失败项不代表零性能；不标记质量验收或 SLA 通过。',note)
summary_headers=['部署','计划点','成功','失败','用户跳过','失败后跳过','启动失败跳过','执行中','待执行','预算未执行']
summary_rows=[]
for label in layouts.values():
    rows=[r for r in matrix if r[0]==label];c=Counter(r[6] for r in rows)
    summary_rows.append([label,len(rows),*[c[x] for x in summary_headers[2:]]])
table(summary_sheet,6,summary_headers,summary_rows,'LayoutProgress')
for i,row in enumerate(summary_rows,8):
    summary_sheet.write_formula(i-1,1,f'=COUNTIFS(\'扫描状态\'!$A$5:$A$724,$A{i})',integer,row[1])
    for col,status in enumerate(summary_headers[2:],2):
        summary_sheet.write_formula(i-1,col,f'=COUNTIFS(\'扫描状态\'!$A$5:$A$724,$A{i},\'扫描状态\'!$G$5:$G$724,{xlsxwriter.utility.xl_col_to_name(col)}$7)',integer,row[col])
summary_sheet.write('A13',source_note,note)
summary_sheet.write('A14','TPOT=(端到端延迟−TTFT)/(实际输出 tokens−1)。分位数按请求计算；并发 Prefill 仍可能影响 TPOT。',note)
summary_sheet.write('A15','每点计分请求=4×并发；预热另计。每轮独立保留，不平均分位数。全窗口输出吞吐包含 Prefill。',note)
headers=['部署','输入 tokens','输出 tokens','并发','轮次','计分请求','成功请求','TPOT均值\nms/token','TPOT p50\nms/token','TPOT p95\nms/token','TPOT p99\nms/token','首token后\n平均耗时(s)','TTFT均值\nms','端到端\n平均耗时(s)','全窗口输出吞吐\ntokens/s','Run ID']
table(summary_sheet,16,headers,results,'CompletedRuns',{**{i:integer for i in range(1,7)},**{i:number for i in range(7,15)}})
summary_sheet.freeze_panes(17,1)
summary_sheet.repeat_rows(16);summary_sheet.print_area(0,0,16+len(results),15)

detail.set_column(0,0,20,normal);detail.set_column(1,4,12,integer);detail.set_column(5,5,29,normal)
detail.set_column(6,6,64,normal);detail.set_column(7,10,21,number)
detail.write('A1',f'来源：metax-60 AIPerf 原始计分记录；快照 {stamp} 北京时间；不含预热。',note)
detail.write('A2','\n'.join(stage_names[r['stage']]+'归档 SHA256：'+r['sha256'] for r in receipts),note)
detail.set_row(1,23*len(receipts))
detail.write_comment('A2',source_note)
request_headers=['部署','实际输入 tokens','实际输出 tokens','并发','轮次','Run ID','逻辑请求 ID','TTFT(ms)','端到端延迟(ms)','首token后耗时(s)','TPOT(ms/token)']
table(detail,3,request_headers,requests,'NativeRequests',{**{i:integer for i in range(1,5)},**{i:number for i in range(7,11)}})
for i,row in enumerate(requests,5):
    detail.write_formula(i-1,9,f'=(I{i}-H{i})/1000',number,row[9])
    detail.write_formula(i-1,10,f'=(I{i}-H{i})/(C{i}-1)',number,row[10])
detail.freeze_panes(4,1);detail.repeat_rows(3)

status_sheet.set_column(0,0,20,normal);status_sheet.set_column(1,5,12,integer)
status_sheet.set_column(6,6,18,normal);status_sheet.set_column(7,7,85,normal);status_sheet.set_column(8,9,29,normal)
status_sheet.write('A1','全部 720 个计划点；'+source_note,note)
status_sheet.write('A2','“待执行”包含前次中断后尚未执行的点；失败后跳过保留原失败 Run ID，不计为成功。',note)
table(status_sheet,3,['部署','输入 tokens','输出 tokens','并发','轮次','计划计分请求','状态','说明','Run ID','Trial ID'],matrix,'FullMatrix',{i:integer for i in range(1,6)})
for i,row in enumerate(matrix,5):status_sheet.write_formula(i-1,5,f'=D{i}*4',integer,row[5])
status_sheet.conditional_format('G5:G724',{'type':'text','criteria':'containing','value':'失败','format':warning})
status_sheet.freeze_panes(4,1);status_sheet.repeat_rows(3)
wb.close()

# Read the saved workbook; validate every metric, matrix row and formula cache.
actual=openpyxl.load_workbook(target,data_only=True);formulas=openpyxl.load_workbook(target,data_only=False)
for i,row in enumerate(results,18):
    for j,value in enumerate(row,1):
        saved=actual['性能结果'].cell(i,j).value
        assert saved==value or isinstance(value,float) and math.isclose(saved,value,rel_tol=1e-12)
for i,row in enumerate(requests,5):
    for j in (10,11):assert math.isclose(actual['逐请求明细'].cell(i,j).value,row[j-1],rel_tol=1e-12)
    assert formulas['逐请求明细'].cell(i,11).value==f'=(I{i}-H{i})/(C{i}-1)'
for i,row in enumerate(matrix,5):
    for j,value in enumerate(row,1):
        assert actual['扫描状态'].cell(i,j).value==(None if value in (None,'') else value)
for i,row in enumerate(summary_rows,8):
    assert [actual['性能结果'].cell(i,j).value for j in range(1,len(row)+1)]==row
    assert sum(row[2:])==row[1]
for s in actual:
    assert s.freeze_panes and len(s.tables)>=1
    assert not any(c.data_type=='e' for row in s for c in row)

def render(name,c1,c2,r1,r2,filename):
    s=actual[name];widths=[]
    for c in range(c1,c2+1):
        dim=next((d for d in s.column_dimensions.values() if d.min<=c<=d.max),None)
        widths.append(round((dim.width if dim else 15)*7+5))
    heights=[round((s.row_dimensions[r].height or 23)*1.33) for r in range(r1,r2+1)]
    im=Image.new('RGB',(sum(widths)+24,sum(heights)+24),'white');draw=ImageDraw.Draw(im);y=12
    for ri,r in enumerate(range(r1,r2+1)):
        x=12
        for ci,c in enumerate(range(c1,c2+1)):
            cell=s.cell(r,c);v=cell.value
            if cell.fill.patternType=='solid' and cell.fill.fgColor.type=='rgb':draw.rectangle((x,y,x+widths[ci],y+heights[ri]),fill='#'+cell.fill.fgColor.rgb[-6:])
            if v is not None:
                text=f'{v:,.3f}' if isinstance(v,float) and '.000' in cell.number_format else str(v)
                font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',round((cell.font.sz or 10)*1.33))
                color='#'+cell.font.color.rgb[-6:] if cell.font.color and cell.font.color.type=='rgb' else '#202C3A'
                tx=x+5 if not isinstance(v,(int,float)) else x+widths[ci]-5-draw.textlength(text,font=font)
                draw.multiline_text((tx,y+5),text,font=font,fill=color,spacing=3)
            x+=widths[ci]
        y+=heights[ri]
    im.save(OUT/filename)
for args in [('性能结果',1,10,1,12,'overview.png'),('性能结果',1,11,17,28,'results.png'),
             ('性能结果',12,16,17,25,'result-right.png'),('逐请求明细',8,11,4,14,'requests.png'),
             ('扫描状态',1,8,4,16,'matrix.png'),('性能结果',1,11,13,15,'provenance.png'),
             ('逐请求明细',1,11,1,4,'request-heading.png'),('扫描状态',1,10,1,4,'matrix-heading.png')]:render(*args)
first_skip=next(i+5 for i,row in enumerate(matrix) if row[6]=='用户跳过')
render('扫描状态',1,10,first_skip-1,first_skip+3,'matrix-skips.png')
validation=dict(snapshots=[dict(stage=r['stage'],sha256=r['sha256'],captured_at=r['captured_at']) for r in receipts],captured_at=data['captured_at'],completed_points=len(results),
                successful_requests=len(requests),planned_points=len(matrix),status_counts=dict(counts),
                saved_xlsx_readback='passed',formula_caches='checked against source records and independent counts',
                native_recalculation='not tested; standard formulas and checked cached values',
                rendering='PIL from saved values/styles; native Artifact Tool unavailable (skia.node)',
                output=str(target))
(OUT/'verification.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(validation,ensure_ascii=True))
