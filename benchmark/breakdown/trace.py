"""Overlap-safe interval summaries within explicit rank/clock-domain boundaries."""
from collections import defaultdict
from tools.specs import read
from benchmark.common.io import file_hash
from diagnosis.contracts import finish,header,validate


def union_duration(intervals):
    end=None;total=0
    for start,stop in sorted(intervals):
        if end is None or start>end:total+=stop-start
        else:total+=max(0,stop-end)
        end=max(end,stop) if end is not None else stop
    return total


def summarize(catalog,path):
    capture=read(path);validate(catalog,capture)
    if capture['kind']!='TraceCapture':raise ValueError('expected TraceCapture')
    groups=defaultdict(list)
    for event in capture['events']:groups[(event['clock_domain'],event['rank'])].append(event)
    windows={w['clock_domain']:w for w in capture['windows']}
    lanes=[]
    for (domain,rank),events in sorted(groups.items()):
        by_category=defaultdict(list);by_name=defaultdict(list)
        for e in events:
            by_category[e['category']].append(e);by_name[(e['category'],e['name'])].append(e)
        def span(es):return union_duration([(e['start_ns'],e['start_ns']+e['duration_ns']) for e in es])
        window=windows[domain]['end_ns']-windows[domain]['start_ns']
        covered=span(events)
        lanes.append(dict(clock_domain=domain,rank=rank,window_ns=window,observed_event_union_ns=covered,
            uncovered_window_ns=window-covered,covered_fraction=covered/window,
            category_union_ns={k:span(v) for k,v in sorted(by_category.items())},
            hotspots=[dict(category=k[0],name=k[1],calls=len(es),duration_sum_ns=sum(e['duration_ns'] for e in es),
                interval_union_ns=span(es)) for k,es in sorted(by_name.items(),key=lambda kv:-sum(e['duration_ns'] for e in kv[1]))]))
    result=finish({**header('TraceSummary',capture['id']+'-summary','重叠感知 trace 汇总'),
        'input_artifact':dict(path=str(path.resolve()),sha256=file_hash(path),role='normalized_trace'),
        'evidence_kind':'synthetic' if capture['evidence_kind']=='synthetic' else 'derived_from_measured',
        'lanes':lanes,'critical_path':None,'limitations':[
            'Each lane is independent. Different clocks or ranks are never added into a global latency.',
            'Category unions may overlap; hotspot duration sums are work accounting, not E2E shares.',
            'Uncovered window means absent captured events; it does not prove GPU idle or host starvation.',
            'No dependency graph, correlation IDs or synchronized boundaries: critical path remains unknown.',
            'Profiler overhead must be measured against an unprofiled control before performance attribution.']})
    validate(catalog,result);return result
