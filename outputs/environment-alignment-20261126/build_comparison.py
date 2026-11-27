"""Derive comparison tables exclusively from the captured read-only evidence."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

formal = read('61-formal61_container.json')['files']
sources = {60: read('60-additional_60.json'), 61: formal,
           64: read('64-read_64_evidence.json') + read('64-additional_64.json'),
           65: read('65-read_65_evidence.json') + read('65-additional_65.json')}
file_index = []
for host, files in sources.items():
    directory = ROOT/'files'/str(host)
    directory.mkdir(parents=True, exist_ok=True)
    for f in files:
        name = hashlib.sha256(f['path'].encode()).hexdigest()[:10]+'-'+Path(f['path']).name
        local = directory/name
        local.write_text(f['text'], encoding='utf-8')
        file_index.append(dict(host=host, remote=f['path'], local=local.relative_to(ROOT).as_posix(),
                               remote_sha256=f['sha256'], truncated=f.get('truncated',False)))
(ROOT/'evidence-files.json').write_text(json.dumps(file_index,ensure_ascii=False,indent=2),encoding='utf-8')

def evidence_link(host, remote):
    f = next(x for x in file_index if x['host']==host and x['remote']==remote)
    return '['+Path(remote).name+']('+f['local']+')'

configs = []
for host, files in sources.items():
    for f in files:
        if not f['path'].endswith('server-info.json'):
            continue
        if host==61 and 'tp8-graph20-formal' not in f['path']:
            continue
        if host==65 and '/full/' in f['path']:
            continue
        raw=json.loads(f['text']); c=raw['vllm_config']; p=c['parallel_config']; s=c['scheduler_config']; k=c['cache_config']
        configs.append(dict(host=host,remote=f['path'],model=c['model_config'],parallel=p,scheduler=s,cache=k,
                            compilation=c['compilation_config'],attention=c.get('attention_config'),
                            v2=raw['vllm_env'].get('VLLM_USE_V2_MODEL_RUNNER','not exposed'),
                            label=str(host)+(' EP on' if p['enable_expert_parallel'] else ' EP off')))

profiles=[]
for f in formal:
    if 'tp8-graph20-formal' not in f['path'] or not f['path'].endswith('profile_export_aiperf.json'):
        continue
    j=json.loads(f['text']); match=re.search(r'/l(\d+)-c(\d+)-',f['path']); length,concurrency=map(int,match.groups())
    directory=f['path'].rsplit('/aiperf/',1)[0]
    engine=json.loads(next(x['text'] for x in formal if x['path']==directory+'/engine-verification.json'))
    profile_check=json.loads(next(x['text'] for x in formal if x['path']==directory+'/profile-verification.json'))
    assert engine['valid'] and profile_check['valid']
    assert j['request_count']['avg']==concurrency*4
    for req in engine['requests'].values():
        assert req['first_computed_tokens']==length and req['prompt_tokens']==length+1
        assert req['max_query_tokens']==1 and req['output_tokens']==20 and req['preemptions']==0
    profiles.append(dict(ep='on' if 'ep-on/' in f['path'] else 'off',input=length,output=20,concurrency=concurrency,
                         requests=int(j['request_count']['avg']),ttft=j['time_to_first_token'],
                         tpot=j['inter_token_latency'],e2e=j['request_latency'],
                         output_tps=j['output_token_throughput']['avg'],request_rps=j['request_throughput']['avg'],
                         aiperf=j['aiperf_version'],remote=f['path']))
assert len(profiles)==18
profiles.sort(key=lambda r:(r['ep'],r['input'],r['concurrency']))

# Check every displayed numeric cell in the colleague's table, including rounding.
ep=None;checked=0
for line in (ROOT.parent/'TP8.md').read_text(encoding='utf-8').splitlines():
    if line.startswith('## TP8'):ep='off' if '关' in line else 'on'
    if not re.match(r'^\| (4K|16K|64K) \|',line):continue
    cells=[x.strip() for x in line.strip('|').split('|')]
    if len(cells)!=9:
        continue
    length={'4K':4096,'16K':16384,'64K':65536}[cells[0]]
    p=next(x for x in profiles if (x['ep'],x['input'],x['concurrency'])==(ep,length,int(cells[2])))
    assert cells[3]==f"1/{p['requests']}"
    for col,metric,div in [(4,'ttft',1),(5,'tpot',1),(6,'e2e',1000)]:
        expected=' / '.join(f"{p[metric][k]/div:.2f}" for k in ['avg','p95'])
        assert cells[col]==expected,(col,cells[col],expected)
    assert cells[7]==f"{p['output_tps']:.2f}" and cells[8]==f"{p['request_rps']:.3f}"
    checked+=1
assert checked==18

models={h:read(f'{h}-inventory.json')['model_metadata'][0] for h in [60,61,64,65]}
shards={h:{f['name']:f['bytes'] for f in model['files'] if f['name'].endswith('.safetensors')} for h,model in models.items()}
assert all(s==shards[60] for s in shards.values())
fingerprints={h:read(f'{h}-fingerprint_{h}.json') for h in models}
def normalize(path):
    for module in ['vllm_metax','vllm']:
        marker='/'+module+'/'
        if marker in path:return module+'/'+path.split(marker,1)[1]
files={h:{normalize(f['path']):f['sha256'] for f in fp['files'] if normalize(f['path'])} for h,fp in fingerprints.items()}
common=set.intersection(*(set(d) for d in files.values()))
assert len(common)==11
assert all(len({files[h][p] for h in files})==1 for p in common)

comparison=dict(configs=configs,profiles61=profiles,verified_table_rows=checked,
                common_source_hashes={p:files[60][p] for p in sorted(common)},
                models={h:dict(path=m['path'],shards=len(shards[h]),weight_bytes=sum(shards[h].values()),
                              metadata_hashes={f['name']:f['sha256'] for f in m['files'] if 'sha256' in f}) for h,m in models.items()})
(ROOT/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf-8')

lines=['# 四机环境证据明细','', '本文件由 `build_comparison.py` 从本地采集快照生成。时间及历史/当前区分见 [分析报告](README.md)。', '',
       '## 服务端实际配置','', '| 参数 | '+' | '.join(c['label'] for c in configs)+' |', '|---|'+'---|'*len(configs)]
for group, keys in [('model',['max_model_len','enforce_eager','dtype','quantization']),
                    ('parallel',['tensor_parallel_size','pipeline_parallel_size','data_parallel_size','enable_expert_parallel','all2all_backend','disable_custom_all_reduce','_api_process_count']),
                    ('scheduler',['max_num_batched_tokens','max_num_seqs','enable_chunked_prefill','async_scheduling','stream_interval']),
                    ('cache',['enable_prefix_caching','gpu_memory_utilization','block_size','mamba_block_size','prefix_match_unit','mamba_cache_mode','num_gpu_blocks','kv_cache_size_tokens']),
                    ('compilation',['mode','cudagraph_mode','cudagraph_capture_sizes'])]:
    for key in keys:
        lines.append('| '+group+'.'+key+' | '+' | '.join('`'+str(c[group].get(key))+'`' for c in configs)+' |')
lines += ['| VLLM_USE_V2_MODEL_RUNNER | '+' | '.join(str(c['v2']) for c in configs)+' |',
          '| 证据 | '+' | '.join(evidence_link(c['host'],c['remote']) for c in configs)+' |','',
          '65 列为已有 4K 运行保存的 server-info；与稍后抓到的进程启动参数存在差异，不能当成同一时刻的完整配置。', '',
          '## 源码与二进制','', '四机以下 11 个采样源码文件的 SHA-256 完全一致；这不是全源码逐文件一致证明。','', '| 文件 | SHA-256 |','|---|---|']
lines += ['| `'+p+'` | `'+files[60][p]+'` |' for p in sorted(common)]
lines += ['', '各机器完整采样指纹：'+', '.join(f'[{h}]({h}-fingerprint_{h}.json)' for h in models), '',
          '## 61 原始性能数据核对','',
          '18/18 行与 `outputs/TP8.md` 的 TTFT/TPOT/E2E 均值和 P95、两类吞吐量及请求数在显示精度上完全一致。每行 engine/profile 验证均通过。', '',
          '| EP | 输入 | 并发 | TTFT ms 平均/P95 | TPOT ms 平均/P95 | E2E ms 平均/P95 | 输出 tok/s | 请求 req/s | 原始数据 |',
          '|---|---:|---:|---:|---:|---:|---:|---:|---|']
for p in profiles:
    pair=lambda k:f"{p[k]['avg']:.3f}/{p[k]['p95']:.3f}"
    lines.append(f"| {p['ep']} | {p['input']} | {p['concurrency']} | {pair('ttft')} | {pair('tpot')} | {pair('e2e')} | {p['output_tps']:.3f} | {p['request_rps']:.3f} | {evidence_link(61,p['remote'])} |")
lines += ['', '## 启动命令及日志定位','', '| 机器 | 远端路径 | 本地证据 |','|---|---|---|']
for f in file_index:
    if Path(f['remote']).name not in ['launch.json','server-info.json','snapshot.json','server.log','state.json']:continue
    if f['host']==61 and 'tp8-graph20-formal' not in f['remote']:continue
    lines.append(f"| {f['host']} | `{f['remote']}` | [{Path(f['remote']).name}]({f['local']}) |")
(ROOT/'details.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(dict(verified_rows=checked,source_files_equal=len(common),model_shards=len(shards[60]),configs=len(configs))))
