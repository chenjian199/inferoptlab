"""Human-readable reports complement the complete YAML artifacts."""
def render(doc):
    lines=['# 阶段二：归因报告','',f"状态：`{doc['status']}`。报告由既有证据离线计算，没有新增 GPU 测量。",'',
        '## 运行与证据质量','','| Run | 输入/输出 | 并发 | 可用于观察 | TTFT 均值 ms | TPOT 均值 ms | 输出 tokens/s |','|---|---:|---:|---|---:|---:|---:|']
    def f(x):return 'unknown' if x is None else f'{x:.4f}'
    for r in doc['runs']:
        m=r['metrics'];lines.append(f"| {r['run_id']} | {r['input_tokens']}/{r['output_tokens']} | {r['concurrency']} | {r['eligible']} | {f(m['ttft_mean_ms'])} | {f(m['tpot_mean_ms'])} | {f(m['output_tokens_per_s'])} |")
        if r['reasons']:lines.append('\n排除原因：'+'; '.join(r['reasons'])+'\n')
    lines+=['','## 受控维度比较','']
    for c in doc['comparisons']:
        lines += [f"- `{c['id']}`：{c['axis']} {c['values']['baseline_point']} → {c['values']['candidate_point']}；样本门槛满足：{c['sample_qualified']}。",
                  '  限制：'+'; '.join(c['limitations'])]
    lines+=['','## 待验证假设','']
    for h in doc['hypotheses']:
        lines += [f"### {h['id']}",'',h['observation'],'',h['possible_cause'],'',
            '证据：'+', '.join(h['evidence_ids']),'','替代解释：',*['- '+s for s in h['alternatives']],'',
            '缺失证据：',*['- '+s for s in h['missing_evidence']],'','证伪条件：'+h['falsification'],'',
            '专项方法：'+', '.join(r['id'] for r in h['method_refs']),'']
    lines+=['## 未解释与限制','',*['- '+s for s in doc['unexplained']+doc['limitations']],'',
        '## 历史与校准资料','']
    for c in doc['context']:
        lines.append(f"- `{c['ref']['id']}`：{c['evidence_kind']}；仅作线索；来源问题 {len(c['source_issues'])} 项。")
    return '\n'.join(lines)+'\n'
