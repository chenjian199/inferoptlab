"""Prepare reproducible operator replay cases; no implicit tensor deserialization."""
from tools.specs import SpecError
from benchmark.common.offline import semantic_errors


def prepare(catalog,plan):
    result=[]
    for reference in plan['operator_case_refs']:
        case=catalog.get(reference)
        for field in ('model_ref','hardware_ref','runtime_ref'):
            if case[field]!=plan[field]:raise SpecError('operator case scope differs from breakdown plan: '+field)
        errors=catalog.structural_errors(case) or semantic_errors(catalog,case,True)
        if errors:raise SpecError('\n'.join(errors))
        blockers=[]
        if case['numeric_budget'] is None:blockers.append('Freeze case-specific numerical tolerances before candidate measurement.')
        if not case['fixture_artifacts']:blockers.append('Capture versioned input, state and baseline output artifacts.')
        if case['baseline_self_replay']!='passed':blockers.append('Verify baseline capture -> baseline replay before candidate comparison.')
        blockers.append('GPU replay/timing adapter has not been qualified; historical observations are not execution readiness.')
        result.append(dict(case_ref=reference,module_path=case['module_path'],contract=case['tensor_contract'],blockers=blockers))
    return result
