"""Conservative SLA evaluation. Unknown conditions remain inconclusive."""
import operator

OPS={'lt':operator.lt,'le':operator.le,'gt':operator.gt,'ge':operator.ge,'eq':operator.eq}
UNITS={'ttft':'ms','tpot':'ms','e2e_latency':'ms','request_throughput':'requests/s',
    'request_goodput':'requests/s','output_token_goodput':'tokens/s','input_token_throughput':'tokens/s',
    'output_token_throughput':'tokens/s','success_rate':'fraction','joint_slo_attainment':'fraction'}


def convert(value, metric, unit):
    if value is None or metric not in UNITS:
        return None
    native=UNITS[metric]
    if native==unit:
        return value
    if native=='ms' and unit=='s':
        return value/1000
    if native=='fraction' and unit=='percent':
        return value*100
    return None


def evaluate(sla, bundle, records, allocated_devices=None, environment_issues=()):
    result=dict(status='not_evaluated',constraints=[],joint=None,quality_status='not_evaluated',
                acceptance_status='not_evaluated',reasons=list(environment_issues))
    if not sla:
        result['reasons'].append('no SLA is attached to this diagnostic Case')
        return result
    per_request={}
    unresolved=[]
    if bundle['validity']!='valid':
        unresolved.append('measurement is incomplete or invalid')
    if any(i['blocking'] for i in sla['issues']):
        unresolved.append('SLA contains unresolved blocking issues')
    if sla['conditional_requirements'] or sla['quality_requirements']:
        unresolved.append('conditional/quality requirements require a separate evaluator')
    for c in sla['constraints']:
        metric=c['metric']
        reason=None
        value=None
        threshold=c['threshold'].get('value')
        comparison=OPS.get(c['operator'])
        if threshold is None or comparison is None:
            reason='unresolved threshold/operator'
        elif c['population']=='unspecified':
            reason='unspecified population'
        elif c['statistic']=='per_request':
            if c['population']!='all_planned_requests' or c['normalization']['basis']!='system':
                reason='v1 per-request evaluation requires all_planned_requests and system normalization'
            else:
                flags=[]
                for r in records:
                    v=convert(r.get(metric),metric,c['unit'])
                    flags.append(False if r['status']!='success' or r['issues'] else None if v is None else comparison(v,threshold))
                per_request[c['id']]=flags
                if any(v is None for v in flags):
                    reason='required request metric unavailable'
                else:
                    value=sum(flags)/len(records)
        elif c['scope']!='case':
            reason='unsupported aggregation scope'
        else:
            if c['statistic'] in {'rate','fraction'}:
                value=bundle['rates'].get(metric)
                # This implementation's finite-set denominator always includes all planned requests.
                if c['population']!='all_planned_requests':
                    reason='rate/fraction population differs from all_planned_requests protocol'
            else:
                value=bundle['statistics'].get(metric,{}).get(c['statistic'])
                if c['population']!='successful_requests' and bundle['counts']['failed']:
                    reason='failed-request latency is undefined for the requested population'
            value=convert(value,metric,c['unit'])
            basis=c['normalization']['basis']
            if basis!='system':
                if metric not in {'request_throughput','input_token_throughput','output_token_throughput'} or not allocated_devices:
                    reason='normalization is unsupported or actual allocated-device count is unavailable'
                elif basis=='allocated_devices':
                    value=value/allocated_devices if value is not None else None
                elif basis=='reference_device_count':
                    value=value*c['normalization']['device_count']/allocated_devices if value is not None else None
                else:
                    reason='active-device/unspecified normalization is unsupported'
        if value is None and not reason:
            reason='metric unavailable or unit/statistic unsupported'
        if reason:
            status='inconclusive'
            unresolved.append(c['id']+': '+reason)
        elif c['statistic']=='per_request':
            # The value is attainment, not a latency to compare with a latency threshold.
            status='passed' if value==1 else 'failed'
        else:
            status='passed' if comparison(value,threshold) else 'failed'
        result['constraints'].append(dict(id=c['id'],status=status,value=value,severity=c['severity'],reason=reason))
    joint=sla['joint_request_slo']
    if joint:
        vectors=[per_request.get(cid) for cid in joint['constraint_ids']]
        if joint['population']!='all_planned_requests' or any(v is None or any(x is None for x in v) for v in vectors):
            result['joint']=dict(status='inconclusive',attainment=None,request_goodput=None,output_token_goodput=None)
            unresolved.append('joint SLO cannot be evaluated')
        else:
            good=[all(v[i] for v in vectors) for i in range(len(records))]
            attainment=sum(good)/len(records)
            duration=bundle['duration_s']
            result['joint']=dict(status='passed' if attainment>=joint['min_attainment'] else 'failed',attainment=attainment,
                request_goodput=sum(good)/duration if duration else None,
                output_token_goodput=sum((r['output_tokens'] or 0) for r,g in zip(records,good) if g)/duration if duration else None)
    hard_failure=any(c['status']=='failed' and c['severity']=='hard' and c['id'] not in (joint['constraint_ids'] if joint else []) for c in result['constraints'])
    hard_failure=hard_failure or bool(result['joint'] and result['joint']['status']=='failed')
    result['status']='failed' if hard_failure else 'inconclusive' if unresolved or environment_issues else 'passed'
    result['reasons']+=unresolved
    result['reasons'].append('performance SLA only; model correctness/quality and complete Study acceptance are not executed by this module')
    return result
