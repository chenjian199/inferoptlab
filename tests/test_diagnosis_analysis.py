"""Evidence boundaries, comparison isolation and overlap arithmetic."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.specs import Catalog, ROOT, SpecError, read, digest, instantiate
from benchmark.common.io import file_hash, inside
from diagnosis.contracts import validate
from diagnosis.evidence import sealed_files
from diagnosis.engine import diagnose,compare
from analysis.planner import plan_tasks
from benchmark.breakdown.trace import summarize,union_duration


class DiagnosisAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=Catalog();cls.catalog.load()
        cls.plan=read(ROOT/'recipes/plans/diagnosis/qwen-metax.yaml')
        cls.report=diagnose(cls.catalog,cls.plan)

    def test_real_archive_is_descriptive_not_causal(self):
        r=self.report
        self.assertEqual(4,len(r['runs']))
        self.assertTrue(all(x['eligible'] for x in r['runs']))
        self.assertEqual(2,len(r['comparisons']))
        self.assertFalse(any(x['sample_qualified'] for x in r['comparisons']))
        length=next(c for c in r['comparisons'] if c['axis']=='input_tokens')
        self.assertAlmostEqual(5.34195,length['values']['ttft_mean_ms']['ratio'],places=3)
        self.assertTrue(all(h['status']=='needs_evidence' and h['expected_gain'] is None for h in r['hypotheses']))
        self.assertTrue(all(not x['causal_evidence'] for x in r['context']))

    def test_manifest_tamper_rejected(self):
        entry=copy.deepcopy(self.plan['batches'][0]);entry['manifest_sha256']='0'*64
        with self.assertRaisesRegex(SpecError,'manifest hash'):sealed_files(ROOT,entry)

    def test_input_length_cannot_compare_different_output_lengths(self):
        pairs=self.report['comparisons'];rows={r['run_id']:r for r in self.report['runs']}
        for p in pairs:
            outputs={rows[i]['output_tokens'] for i in p['baseline_runs']+p['candidate_runs']}
            self.assertEqual(1,len(outputs))
        self.assertNotIn(128,[p['values']['baseline_point'] for p in pairs if p['axis']=='input_tokens'])

    def test_single_token_prefill_leaves_tpot_unknown(self):
        rows=copy.deepcopy(self.report['runs'])
        for row in rows:row['metrics']['tpot_mean_ms']=None
        pairs=compare(rows,self.plan['policy'])
        self.assertTrue(all(p['values']['tpot_mean_ms']['ratio'] is None for p in pairs))

    def test_wrong_study_rejected(self):
        p=copy.deepcopy(self.plan);p['study_ref']={'id':'deepseek-bw1000-exploration','version':'1.0.0'}
        with self.assertRaisesRegex(SpecError,'different study'):diagnose(self.catalog,p)

    def test_failed_run_retained_and_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            c=copy.copy(self.catalog);c.root=Path(temp)
            shutil.copytree(ROOT/'schemas/definitions',c.root/'schemas/definitions')
            archive=Path('experiments/evidence/benchmark-qualification/20261123')
            shutil.copytree(ROOT/archive,c.root/archive)
            p=copy.deepcopy(self.plan);batch=inside(c.root,p['batches'][0]['directory'])
            b=read(batch/'batch.json');row=b['runs'][0];row['status']='failed'
            run=batch/row['directory']/'run.json';r=read(run);r.update(status='failed',error='controlled fixture failure')
            run.write_text(json.dumps(r),encoding='utf-8');(batch/'batch.json').write_text(json.dumps(b),encoding='utf-8')
            m=inside(c.root,p['batches'][0]['manifest']);manifest=read(m)
            for path in (run,batch/'batch.json'):manifest[path.relative_to(m.parent).as_posix()]=file_hash(path)
            m.write_text(json.dumps(manifest),encoding='utf-8');p['batches'][0]['manifest_sha256']=file_hash(m)
            result=diagnose(c,p)
            failed=next(x for x in result['runs'] if x['run_id']==r['id'])
            self.assertFalse(failed['eligible']);self.assertIn('run status: failed',failed['reasons'])
            self.assertEqual(4,len(result['runs']))

    def test_analysis_requires_matching_report_and_never_launches(self):
        plan=read(ROOT/'recipes/plans/analysis/qwen-metax.yaml')
        with self.assertRaisesRegex(SpecError,'required'):plan_tasks(self.catalog,plan)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'report.json';p.write_text(json.dumps(self.report),encoding='utf-8')
            out=plan_tasks(self.catalog,plan,p)
            self.assertTrue(all(t['result'] is None and not t['execution_authorized'] for t in out['tasks']))
            by_id={t['method_ref']['id']:t for t in out['tasks']}
            self.assertEqual('not_applicable',by_id['moe-routing']['status'])
            self.assertEqual('not_applicable',by_id['communication']['status'])
            self.assertEqual('needs_capture',by_id['request-timing']['status'])
            broken=copy.deepcopy(self.report);broken['status']='no_valid_runs'
            p.write_text(json.dumps(broken),encoding='utf-8')
            with self.assertRaisesRegex(SpecError,'fingerprint'):plan_tasks(self.catalog,plan,p)

    def test_glm_capacity_budget_and_missing_baseline(self):
        plan=read(ROOT/'recipes/plans/analysis/glm53-w8a8-c500.yaml');out=plan_tasks(self.catalog,plan)
        self.assertTrue(any('exceed allocated physical VRAM' in x for x in out['preflight_issues']))
        self.assertTrue(all(t['status']=='awaiting_baseline' for t in out['tasks']))
        self.assertEqual(11*120*3*3*8,out['proposed_gpu_seconds'])
        plan['budget']['max_proposed_gpu_seconds']=1
        limited=plan_tasks(self.catalog,plan)
        self.assertEqual(0,limited['proposed_gpu_seconds'])
        self.assertTrue(all(t['status']=='deferred_budget' for t in limited['tasks']))

    def test_overlap_and_rank_boundaries(self):
        self.assertEqual(80,union_duration([(0,60),(40,80)]))
        self.assertEqual(80,union_duration([(0,80),(10,20)]))
        result=summarize(self.catalog,ROOT/'examples/traces/overlap.yaml')
        self.assertEqual([80,90],[x['observed_event_union_ns'] for x in result['lanes']])
        self.assertEqual('synthetic',result['evidence_kind'])
        self.assertIsNone(result['critical_path'])

    def test_trace_rejects_clock_mismatch(self):
        trace=read(ROOT/'examples/traces/overlap.yaml');trace['events'][0]['clock_domain']='unsynchronized-node'
        with self.assertRaisesRegex(SpecError,'clock-domain'):validate(self.catalog,trace)

    def test_templates_expand_to_strict_contracts(self):
        paths=list((ROOT/'schemas/templates/analysis').glob('*.yaml'))+list((ROOT/'schemas/templates/diagnosis').glob('*.yaml'))
        for path in paths:
            document=instantiate(read(path),{},self.catalog)
            validate(self.catalog,document)


if __name__=='__main__':unittest.main()
