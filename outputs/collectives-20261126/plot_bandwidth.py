"""Plot verified measured curves; no interpolation used for model estimates."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
verification = json.loads((OUT / 'verification.json').read_text())
assert verification['points'] == 576
fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout='constrained')
groups = [('01234567', 'All 8 GPUs (EP8)'), ('0123', 'GPUs 0-3 (MX group / TP4)'),
          ('01', 'GPUs 0,1 (MX group / TP2)'), ('04', 'GPUs 0,4 (cross-group NODE)')]
for ax, (g, label) in zip(axes.flat, groups):
    for op, name, color in [('all_to_all_roundtrip', '2 x All-to-All', '#e06c3c'),
                             ('all_gather_reduce_scatter', 'All-Gather + Reduce-Scatter', '#137fa8')]:
        rows = [json.loads(x) for x in (OUT / 'raw' / f'gpu{g}-{op}.jsonl').read_text().splitlines()]
        ax.plot([r['size_bytes'] / 1024**2 for r in rows], [r['bus_GBps'] for r in rows],
                'o-', label=name, color=color, markersize=4, linewidth=1.8)
    ax.set_xscale('log', base=2)
    ax.set_xticks([1/128, 1/8, 1, 8, 64, 256], ['8 KiB','128 KiB','1 MiB','8 MiB','64 MiB','256 MiB'])
    ax.tick_params(axis='x', labelsize=8)
    ax.set_ylim(bottom=0)
    ax.set_title(label, fontsize=11, fontweight='bold')
    ax.set_ylabel('Normalized bus bandwidth (GB/s)')
    ax.grid(alpha=.22)
    ax.legend(loc='upper left', fontsize=8)
fig.suptitle('C500 collective bandwidth | BF16 | median of 5 synchronized batches\n'
             'Same S normalization; not model speedup or physical-link counters', fontsize=13)
fig.savefig(OUT / 'bandwidth.png', dpi=170)
fig.savefig(OUT / 'bandwidth.svg')
readme = OUT / 'README.md'
text = readme.read_text(encoding='utf-8')
anchor='## EP8：从 Decode 小消息到 Prefill 大消息'
text=text.replace(anchor, '![C500 通信带宽随消息大小变化](bandwidth.png)\n\n'+anchor)
readme.write_text(text, encoding='utf-8')
print('bandwidth.png and bandwidth.svg written')
