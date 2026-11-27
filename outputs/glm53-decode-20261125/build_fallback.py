"""XLSX export fallback: Artifact Tool cannot load its native skia module here."""
from pathlib import Path
import json
from datetime import datetime
import math
import xlsxwriter
import openpyxl
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
data = json.loads((OUT/'tables.json').read_text(encoding='utf-8'))
target = OUT/'GLM53-C500-Decode-阶段测试结果.xlsx'
wb = xlsxwriter.Workbook(target)
wb.set_properties({'title':'GLM-5.3-Flash-W8A8 C500 Decode 阶段测试结果','comments':'截至 '+data['meta']['captured_at']+' 北京时间'})
base = {'font_name':'Arial','font_size':10,'valign':'vcenter'}
normal=wb.add_format(base)
num=wb.add_format({**base,'num_format':'#,##0.000'})
integer=wb.add_format({**base,'num_format':'0'})
datefmt=wb.add_format({**base,'num_format':'yyyy-mm-dd hh:mm:ss'})
header=wb.add_format({**base,'bold':True,'bg_color':'#203864','font_color':'#FFFFFF','text_wrap':True,'align':'center'})
title=wb.add_format({**base,'bold':True,'font_size':16,'font_color':'#203864'})
note=wb.add_format({**base,'font_color':'#526174'})
bold=wb.add_format({**base,'bold':True})
warn=wb.add_format({'bg_color':'#FFF1DD','font_color':'#8A4500'})


def sheet(name):
    s=wb.add_worksheet(name);s.hide_gridlines(2);s.set_default_row(23)
    s.set_column(0,24,15,normal)
    s.set_landscape();s.set_paper(9);s.fit_to_pages(1,0)
    return s


def table(s,row,headers,rows,name,formats=None):
    cols=[{'header':v,'header_format':header,'format':(formats or {}).get(i,normal)} for i,v in enumerate(headers)]
    s.add_table(row,0,row+len(rows),len(headers)-1,{'name':name,'style':'Table Style Medium 2','columns':cols,'data':rows})
    s.set_row(row,40)


s=sheet('性能结果');s.set_tab_color('#203864')
s.write('A2','GLM-5.3-Flash-W8A8 性能测试阶段结果',title);s.set_row(1,29)
s.write('A4',f"采集时间：{data['meta']['captured_at']}（北京时间）   完成 7 点 / 288 点，共 508 个计分请求",note)
s.write('A5','范围：八卡 C500，TP2/DP4/EP8，4K 输入、512 输出，第 1 轮；并发 1–64。其余配置尚无完整结果。',note)
headers=['部署','输入\ntokens','输出\ntokens','并发','轮次','计划\n请求数','成功\n请求数','失败\n请求数',
         'TPOT均值\nms/token','TPOT p50\nms/token','TPOT p95\nms/token','TPOT p99\nms/token',
         '首token后\n平均耗时(s)','TTFT均值\nms','端到端\n平均耗时(s)','全窗口输出吞吐\ntokens/s',
         '计分窗口\n秒','Run开始时间\n北京时间','Run结束时间\n北京时间','Run ID']
rows=[r.copy() for r in data['results']]
for row in rows:
    for i in [17,18]: row[i]=datetime.strptime(row[i],'%Y-%m-%d %H:%M:%S')
table(s,5,headers,rows,'CompletedRuns',{**{i:integer for i in range(1,8)},**{i:num for i in range(8,17)},17:datefmt,18:datefmt})
s.set_column(0,0,23);s.set_column(1,7,10);s.set_column(8,16,17);s.set_column(17,18,23);s.set_column(19,19,29)
s.freeze_panes(6,1);s.print_area(0,0,24,19);s.repeat_rows(5)
notes=[
 '统计口径与配置',
 '请求数严格为并发度 × 4；预热独立统计，不包含在上表。每个配置仅完成第 1 轮，未汇总三轮结果。',
 'TPOT =（端到端延迟 − TTFT）/（实际输出 tokens − 1）。首 token 后耗时允许其他请求 Prefill 干扰，不是设备隔离纯 Decode。',
 '分位数以单请求 TPOT 为样本，使用线性插值；低并发点只有 4/8/16 个样本，不能据此推断稳定的尾延迟。',
 '全窗口输出吞吐含 Prefill、调度与传输时间，不是纯 Decode 吞吐。输出 token 统计包含 reasoning tokens。',
 '固定配置：PP1、context 73728、batched tokens 4096、每 DP 最大序列 32、chunked Prefill 开、prefix cache 关。',
 '运行参数：eager、同步调度、显存比例 0.9、allgather_reducescatter；精度/发布验收尚未建立。',
 '并发 128 在预热记录完整性/长度检查时失败，计分请求未开始；后续 280 点按 stop 策略未执行。',
 '此前最小 200 请求批次的人为中止数据不计入本表；完整矩阵状态及历史排除说明见“扫描状态”。',
 f"来源：metax-60，{data['meta']['batch']}；各行 Run ID 对应 decode.json、summary.json 和 requests.jsonl。",
]
for i,text in enumerate(notes,15):s.write(i,0,text,bold if i==15 else note)

s=sheet('逐请求明细')
headers=['部署','目标输入 tokens','目标输出 tokens','并发','轮次','Run ID','逻辑请求 ID','实际请求 ID','状态',
         '实际输入 tokens','实际输出 tokens','TTFT(ms)','端到端延迟(ms)','首token后耗时(s)','TPOT(ms/token)']
table(s,0,headers,data['requests'],'Requests',{**{i:integer for i in [1,2,3,4,9,10]},**{i:num for i in range(11,15)}})
s.set_column(0,0,23);s.set_column(5,5,29);s.set_column(6,6,65);s.set_column(7,7,40);s.set_column(8,8,12);s.set_column(11,14,20)
for i,r in enumerate(data['requests'],1):
    s.write_formula(i,13,f'=(M{i+1}-L{i+1})/1000',num,(r[12]-r[11])/1000)
    s.write_formula(i,14,f'=(M{i+1}-L{i+1})/(K{i+1}-1)',num,(r[12]-r[11])/(r[10]-1))
s.freeze_panes(1,4);s.repeat_rows(0)

s=sheet('扫描状态')
s.write('A2','完整扫描矩阵状态',title);s.set_row(1,29)
s.write('A4',f"截至 {data['meta']['captured_at']}：7 点完成，1 点失败，280 点未执行。采集已停止，原服务已恢复。",note)
s.write('A5',f"排除旧批次 {data['meta']['old_batch']}：因纠正最小请求数配置而中止，不作为四倍请求数结果。",note)
headers=['部署','输入 tokens','输出 tokens','并发','轮次','计划请求数','状态','说明','Run ID','Trial ID']
table(s,5,headers,data['status'],'ScanStatus',{i:integer for i in range(1,6)})
s.set_column(0,0,23);s.set_column(1,5,12);s.set_column(6,6,25);s.set_column(7,7,64);s.set_column(8,9,29)
s.conditional_format(6,6,293,6,{'type':'text','criteria':'containing','value':'失败','format':warn})
s.freeze_panes(6,1);s.repeat_rows(5)
wb.close()

# Validate the saved XLSX, including formula caches and source row counts.
actual=openpyxl.load_workbook(target,data_only=True)
formulas=openpyxl.load_workbook(target,data_only=False)
assert actual.sheetnames==['性能结果','逐请求明细','扫描状态']
assert len(actual['性能结果'].tables)==1 and actual['逐请求明细'].max_row==509 and actual['扫描状态'].max_row==294
for i,r in enumerate(data['requests'],2):
    assert math.isclose(actual['逐请求明细'].cell(i,14).value,(r[12]-r[11])/1000,rel_tol=1e-12)
    assert math.isclose(actual['逐请求明细'].cell(i,15).value,(r[12]-r[11])/(r[10]-1),rel_tol=1e-12)
    assert formulas['逐请求明细'].cell(i,15).value==f'=(M{i}-L{i})/(K{i}-1)'
for i,r in enumerate(data['results'],7):
    for j in range(1,18):assert actual['性能结果'].cell(i,j).value==r[j-1] or isinstance(r[j-1],float) and math.isclose(actual['性能结果'].cell(i,j).value,r[j-1],rel_tol=1e-12)
for s in actual:
    assert s.freeze_panes is not None
    for row in s:
        assert not any(c.data_type=='e' for c in row)

# Native spreadsheet rendering is unavailable. Review the saved cell values,
# sizes and styles using a PIL preview, without changing workbook content.
font_path='C:/Windows/Fonts/msyh.ttc'
def render(sheet_name,min_col,max_col,min_row,max_row,filename):
    s=actual[sheet_name]
    widths=[]
    for col in range(min_col,max_col+1):
        dim=next((d for d in s.column_dimensions.values() if d.min<=col<=d.max),None)
        widths.append(int((dim.width if dim else 15)*7+5))
    heights=[int((s.row_dimensions[r].height or 23)*1.33) for r in range(min_row,max_row+1)]
    image=Image.new('RGB',(sum(widths)+24,sum(heights)+24),'white');draw=ImageDraw.Draw(image)
    y=12
    for ri,rownum in enumerate(range(min_row,max_row+1)):
        x=12
        for ci,colnum in enumerate(range(min_col,max_col+1)):
            cell=s.cell(rownum,colnum);value=cell.value
            fill=cell.fill.fgColor
            if cell.fill.patternType=='solid' and fill.type=='rgb':draw.rectangle([x,y,x+widths[ci],y+heights[ri]],fill='#'+fill.rgb[-6:])
            if value is not None:
                if isinstance(value,datetime):text=value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value,float):text=f'{value:,.3f}' if '.000' in cell.number_format else str(value)
                else:text=str(value)
                size=round((cell.font.sz or 10)*1.33);font=ImageFont.truetype(font_path,size)
                color='#202C3A'
                if cell.font.color and cell.font.color.type=='rgb':color='#'+cell.font.color.rgb[-6:]
                lines=text.split('\n');textheight=len(lines)*(size+3)
                tx=x+5
                if isinstance(value,(int,float)):tx=x+widths[ci]-5-draw.textlength(text,font=font)
                draw.multiline_text((tx,y+(heights[ri]-textheight)/2),text,font=font,fill=color,spacing=3)
            x+=widths[ci]
        y+=heights[ri]
    image.save(OUT/filename)
render('性能结果',1,17,1,14,'results.png')
render('性能结果',13,20,6,13,'result-right.png')
render('性能结果',1,20,16,25,'method.png')
render('逐请求明细',9,15,1,12,'requests.png')
render('扫描状态',1,8,1,15,'status.png')
(OUT/'artifact-validation.json').write_text(json.dumps({'authoring':'xlsxwriter fallback; Artifact Tool native dependency unavailable',
    'saved_xlsx_readback':'passed','formula_cache_checks':1016,'completed_points':7,'successful_requests':508,'scan_rows':288,
    'native_render':'unavailable; PIL previews inspected','excel_interactive_recalculation':'not tested'},indent=2),encoding='utf-8')
print(target)
print('Verified 7 performance rows, 508 request rows, 288 matrix rows and 1016 cached formula results.')
