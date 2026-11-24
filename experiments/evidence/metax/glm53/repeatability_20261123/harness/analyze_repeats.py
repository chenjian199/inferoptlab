"""Offline paired analysis; never executes generated programs."""
import argparse
import itertools
import json
from pathlib import Path


def rows(path):
    items = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    result = {item['task_id']: item for item in items}
    if len(result) != len(items):
        raise ValueError('Duplicate task IDs')
    return result


def first_difference(a, b):
    for index, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return index
    return None if len(a) == len(b) else min(len(a), len(b))


def compare(a, b, sa, sb):
    if not set(a) == set(b) == set(sa) == set(sb):
        raise ValueError('Task sets differ')
    mismatches = {}
    groups = {name: [] for name in ['both_pass','regression','improvement','both_fail']}
    for tid in a:
        index = first_difference(a[tid]['output_token_ids'], b[tid]['output_token_ids'])
        if index is not None:
            mismatches[tid] = index
        left, right = sa[tid]['passed'], sb[tid]['passed']
        key = 'both_pass' if left and right else 'regression' if left else 'improvement' if right else 'both_fail'
        groups[key].append(tid)
    return {'tasks':len(a),'exact_token_matches':len(a)-len(mismatches),
            'first_divergences':mismatches,'score_transitions':groups}


def probability_comparison(a, b):
    output = []
    for tid in a:
        x,y = a[tid],b[tid]
        index = first_difference(x['output_token_ids'], y['output_token_ids'])
        if index is None or index >= min(len(x['output_token_ids']),len(y['output_token_ids'])):
            continue
        ax,by = x['output_token_ids'][index],y['output_token_ids'][index]
        lx,ly = x['logprobs'][index],y['logprobs'][index]
        row = {'task_id':tid,'first_divergence':index,'tokens':[ax,by],
               'a_candidates':lx,'b_candidates':ly,
               'sampled_ranks':[lx[str(ax)]['rank'],ly[str(by)]['rank']]}
        if str(ax) in lx and str(by) in lx and str(ax) in ly and str(by) in ly:
            row['a_minus_b_logprob'] = [lx[str(ax)]['logprob']-lx[str(by)]['logprob'],
                                       ly[str(ax)]['logprob']-ly[str(by)]['logprob']]
        output.append(row)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    r = args.root
    runs, scores, summaries = {}, {}, {}
    for folder in sorted((r/'runs').glob('process_*')):
        if not (folder/'score_summary.json').exists():
            continue
        manifest = json.loads((folder/'generation_manifest.json').read_text(encoding='utf-8'))
        summary = json.loads((folder/'score_summary.json').read_text(encoding='utf-8'))
        if manifest['status'] != 'complete' or summary['status'] != 'complete':
            raise ValueError('Incomplete run: '+folder.name)
        runs[folder.name] = rows(folder/'generations.jsonl')
        scores[folder.name] = rows(folder/'correctness.jsonl')
        summaries[folder.name] = {k:summary[k] for k in ['tasks','passed','pass_at_1','failures_by_type','truncated']}
    expected = ['process_a_plain32_first','process_a_plain32_repeat','process_b_plain32_first',
                'process_b_plain32_reverse','process_c_plain32_first','process_c_diagnostic9_first','process_c_diagnostic9_repeat']
    if set(runs) != set(expected):
        raise ValueError('Not all planned runs have valid scores')
    pairs = [(a,b) for a,b in itertools.combinations(['process_a_plain32_first','process_b_plain32_first','process_c_plain32_first'],2)]
    pairs += [('process_a_plain32_first','process_a_plain32_repeat'),
              ('process_b_plain32_first','process_b_plain32_reverse'),
              ('process_c_diagnostic9_first','process_c_diagnostic9_repeat')]
    comparisons = {a+'__'+b:compare(runs[a],runs[b],scores[a],scores[b]) for a,b in pairs}
    plain = expected[:5]
    ids = list(runs[plain[0]])
    stable_pass = [tid for tid in ids if all(scores[name][tid]['passed'] for name in plain)]
    stable_fail = [tid for tid in ids if all(not scores[name][tid]['passed'] for name in plain)]
    variable = [tid for tid in ids if tid not in stable_pass and tid not in stable_fail]
    token_variants = {tid:len({tuple(runs[name][tid]['output_token_ids']) for name in plain}) for tid in ids}
    history = {}
    history_runs = []
    historical_root = r.parent/'baseline_ops/runs'
    for suffix in ['smoke32','full164']:
        folder = historical_root/('20261123_humaneval_v1_'+suffix)
        old_outputs = {tid:row for tid,row in rows(folder/'generations.jsonl').items() if tid in ids}
        old_scores = {tid:row for tid,row in rows(folder/'correctness.jsonl').items() if tid in ids}
        history[suffix+'_to_process_a'] = compare(old_outputs,runs[plain[0]],old_scores,scores[plain[0]])
        history_runs.append(old_outputs)
    expanded_variants = {tid:len({tuple(run[tid]['output_token_ids']) for run in history_runs+[runs[name] for name in plain]}) for tid in ids}
    report = {'status':'complete','run_scores':summaries,'paired_comparisons':comparisons,
        'stable_pass_observed_32':stable_pass,'stable_fail_observed_32':stable_fail,
        'variable_correctness_observed_32':variable,'token_variant_counts_5_plain_runs':token_variants,
        'historical_comparisons':history,'token_variant_counts_including_history':expanded_variants,
        'diagnostic_first_divergence_probabilities':probability_comparison(runs[expected[5]],runs[expected[6]]),
        'scope':'Three fresh processes, five plain 32-task runs; two separate logprob diagnostic runs in process C. No full164 repeatability claim.'}
    path = r/'repeatability_summary.json'
    with path.open('x',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps({'scores':summaries,'pair_exact_matches':{k:v['exact_token_matches'] for k,v in comparisons.items()},
        'stable_pass':len(stable_pass),'stable_fail':len(stable_fail),'variable':variable,
        'diagnostic_divergences':report['diagnostic_first_divergence_probabilities']},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
