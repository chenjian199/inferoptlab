"""Recompute historical GLM capacity budgets; never label them new-matrix measurements."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from benchmark.load.capacity import concurrency_points, glm_slot_blocks, rank_limit

SOURCES = [
    ('TP8 EP关闭', '61', 'outputs/environment-alignment-20261126/files/61/196f3bc276-server-info.json'),
    ('TP8 EP开启', '61', 'outputs/environment-alignment-20261126/files/61/d72c9f19f0-server-info.json'),
    ('TP4/DP2 EP关闭', '65', 'outputs/environment-alignment-20261126/files/65/5cf5cbc5e3-server-info.json'),
    ('TP2/DP4 EP开启', '60', 'outputs/glm53-tp2-dp4-ep8-profiler-20261126/run-r2/server/server-info.json'),
    ('TP1/DP8 EP关闭', '64', 'outputs/environment-alignment-20261126/files/64/8f6caa64f8-server-info.json'),
    ('TP1/DP8 EP开启', '60', 'outputs/glm53-cached-decode-20261126/scan-r3/glm53-vllm-cached-decode-tp1-dp8-ep8/server-1795668837263403759/server-info.json'),
]
rows = []
for label, host, relative in SOURCES:
    path = ROOT/relative
    cfg = json.loads(path.read_text(encoding='utf-8'))['vllm_config']
    p, k, s, m = [cfg[key] for key in ['parallel_config', 'cache_config', 'scheduler_config', 'model_config']]
    dp, total, block = p['data_parallel_size'], k['num_gpu_blocks'], k['block_size']
    # core_client.py adds the startup response num_gpu_blocks of all DP engines.
    # Division assumes equal DP pools. The logged per-engine capacity provides
    # a cross-check but is not a complete rank-by-rank pool inventory.
    assert total % dp == 0
    per_rank = total // dp
    active_at_max = math.ceil(m['max_model_len'] / block) + 9
    ratio = per_rank / active_at_max
    assert abs(ratio - k['kv_cache_max_concurrency']) < 1e-9, (label, ratio)
    record = dict(deployment=label, host=host, source=relative,
                  source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  tp=p['tensor_parallel_size'], dp=dp, ep=p['enable_expert_parallel'],
                  graph=not m['enforce_eager'], max_num_seqs=s['max_num_seqs'],
                  token_budget=s['max_num_batched_tokens'], max_model_len=m['max_model_len'],
                  aggregate_blocks=total, per_rank_blocks=per_rank,
                  attention_block_tokens=block, logged_capacity_ratio=ratio,
                  assumption='equal DP pools; archived GLM group model; not a new auto deployment',
                  lengths=[])
    for length in [4096, 16384, 65536]:
        budget = glm_slot_blocks(length, 512, block)
        item = dict(input_tokens=length, output_reserve=512, **budget)
        fits_length = length + 1 + 512 <= m['max_model_len']
        limits = rank_limit(pools=[dict(total_blocks=per_rank, reserved_blocks=1,
                                       blocks_per_slot=budget['reserved_slot_blocks'])],
                            max_num_seqs=s['max_num_seqs'],
                            max_num_batched_tokens=s['max_num_batched_tokens'])
        item.update(limits)
        item['resident_budget_total'] = dp * limits['kv_limit'] if fits_length else None
        item['runtime_model_total'] = dp * ((per_rank - 1) // budget['runtime_model_blocks']) if fits_length else None
        item['fits_archived_model_len'] = fits_length
        item['scan'] = concurrency_points([1, 2, 4, 8, 16, 32, 64, 128],
                                         [limits['kv_limit']] * dp) if fits_length else None
        record['lengths'].append(item)
    rows.append(record)

out = Path(__file__).resolve().parent
(out/'calculation.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
lines = ['# 历史缓存池的容量重算', '',
    '这些数字是用已保存部署的实际块总数计算的保守预算，不是当前 auto 矩阵的实测最大值。',
    '每 rank 池数按总块数÷DP恢复，并用该部署日志容量比值交叉核对；均匀 DP 池仍是明确假设。',
    '预留输出512。每槽预算 b=ceil((L+1+512)/A)+14：4组KDA各2活动块+1原始前缀块，1个ring块，另加1个Attention尾页副本。',
    '单rank预算=floor((B_rank−1)/b)，服务预算=DP×单rank预算；不受max_num_seqs裁剪。',
    '额外保留项是可审查的保守假设，未用真实生命周期峰值验证；预算0不等于物理上不能运行。', '',
    '| 历史部署 | 机器 | 图 | max_seqs / token预算 | 总块 / 每rank块 | A | 4K预算 | 16K预算 | 64K预算 |',
    '|---|---|---|---|---|---:|---:|---:|---:|']
for r in rows:
    values = ['长度超限' if x['resident_budget_total'] is None else str(x['resident_budget_total']) for x in r['lengths']]
    lines.append(f"| {r['deployment']} | {r['host']} | {r['graph']} | {r['max_num_seqs']} / {r['token_budget']} | {r['aggregate_blocks']} / {r['per_rank_blocks']} | {r['attention_block_tokens']} | " + ' | '.join(values) + ' |')
lines += ['', 'TP4/DP2 EP开启、TP2/DP4 EP关闭缺少相应历史缓存池快照，不能用另一种EP状态的容量代替。', '',
    '## 对当前48种配置的适用性', '',
    '上述历史配置的机器、图模式、max_model_len、max_num_seqs或token预算与新矩阵不同。新矩阵必须逐部署采集真实池，不能把表中数字写成已实测容量。', '',
    '## 逐输入长度的裁剪结果（历史配置、预算模型）', '']
for r in rows:
    lines += [f"### {r['deployment']} / {r['host']}", '', f"来源：[{Path(r['source']).name}](../../{r['source']})", '']
    for x in r['lengths']:
        points = [p['concurrency'] for p in x['scan']['points']] if x['scan'] else '长度超限'
        lines.append(f"- L={x['input_tokens']}：每槽预留{x['reserved_slot_blocks']}块；总驻留预算{x['resident_budget_total']}；扫描{points}。")
    lines.append('')
(out/'README.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
for r in rows:
    print(r['deployment'], r['per_rank_blocks'], [x['resident_budget_total'] for x in r['lengths']])
