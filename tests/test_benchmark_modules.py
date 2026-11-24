"""Offline module boundaries and evidence validity; no GPU or scoring execution."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.specs import ROOT,Catalog,SpecError,read
from benchmark.cli import main
from benchmark.common.offline import report,semantic_errors
from benchmark.accuracy.functional import audit_run,matrix_gate,inspect,compare
from benchmark.breakdown.operators import prepare
from catalog.library import build,collection,verify_intake


class BenchmarkModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=Catalog();cls.catalog.load()
        cls.archive=ROOT/'experiments/evidence/metax/glm53'
        cls.full=cls.catalog.get(dict(id='glm53-humaneval-full164',version='1.0.0'))
        cls.smoke=cls.catalog.get(dict(id='glm53-humaneval-smoke32',version='1.0.0'))
        cls.breakdown=cls.catalog.get(dict(id='glm53-c500-breakdown',version='1.0.0'))
        cls.historical=cls.archive/'baseline_ops/runs/20261123_humaneval_v1_full164'

    def test_explicit_module_dispatch_rejects_unqualified_command(self):
        with patch('benchmark.load.cli.main',return_value=7) as load:
            with self.assertRaises(SystemExit) as error:main(['plan','x.yaml'])
            self.assertEqual(2,error.exception.code)
            load.assert_not_called()
            self.assertEqual(7,main(['load','plan','x.yaml']))
            load.assert_called_with(['plan','x.yaml'])
        with patch('benchmark.accuracy.cli.main',return_value=0) as accuracy:
            main(['accuracy','plan','x.yaml']);accuracy.assert_called_once_with(['plan','x.yaml'])

    def test_catalog_integrity_and_coverage(self):
        result=build(ROOT,'metax')
        self.assertEqual(16,sum(r['kind']=='vendor_document' for r in result['entries']))
        self.assertEqual(899,sum(r.get('pages',0) for r in result['entries']))
        self.assertEqual(16,result['external_index']['source_counts']['practice'])
        with patch('catalog.library.file_hash',return_value='0'*64):
            with self.assertRaisesRegex(SpecError,'source changed'):collection(ROOT,'metax')

    def test_received_inventory_and_tamper_detection(self):
        self.assertEqual(1665,verify_intake(ROOT)['files'])
        with patch('catalog.library.file_hash',return_value='0'*64):
            with self.assertRaisesRegex(SpecError,'organized file changed'):verify_intake(ROOT)

    def test_historical_full164_audit_is_not_new_acceptance(self):
        with patch('subprocess.run',side_effect=AssertionError('must not execute code')):
            result=inspect(self.catalog,self.full,[self.historical])
        self.assertEqual('history_verified',result['status'])
        self.assertEqual(153,result['findings']['runs'][0]['passed'])
        self.assertFalse(result['release_accepted']);self.assertFalse(result['new_gpu_execution'])
        changed=copy.deepcopy(result);changed['release_accepted']=True
        self.assertTrue(self.catalog.structural_errors(changed))
        with patch('benchmark.common.offline.file_hash',return_value='0'*64):
            self.assertTrue(semantic_errors(self.catalog,result,True))

    def test_duplicate_native_rows_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run';run.mkdir()
            for name in ('generation_manifest.json','score_summary.json','correctness.jsonl','generations.jsonl'):
                shutil.copyfile(self.historical/name,run/name)
            p=run/'correctness.jsonl'
            with p.open('a',encoding='utf-8') as f:f.write(p.read_text(encoding='utf-8').splitlines()[0]+'\n')
            with self.assertRaisesRegex(SpecError,'duplicate task'):audit_run(Path(tmp),run,self.full['dataset']['task_ids'])

    def test_parse_failure_is_retained_in_denominator(self):
        source=self.archive/'baseline_ops/runs/20261123_humaneval_v1_smoke32'
        result=audit_run(ROOT,source,self.smoke['dataset']['task_ids'])
        self.assertEqual(32,result['total']);self.assertEqual(31,result['passed'])
        self.assertFalse(result['scores']['HumanEval/37'])

    def test_score_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=Path(tmp)/'run';run.mkdir()
            for name in ('generation_manifest.json','score_summary.json','correctness.jsonl','generations.jsonl'):
                shutil.copyfile(self.historical/name,run/name)
            p=run/'score_summary.json';d=read(p);d['passed']=164;p.write_text(json.dumps(d),encoding='utf-8')
            with self.assertRaisesRegex(SpecError,'summary differs'):audit_run(Path(tmp),run,self.full['dataset']['task_ids'])

    def test_stable_regression_not_cancelled_by_other_improvement(self):
        b=[dict(a=True,b=False) for _ in range(3)];c=[dict(a=False,b=True) for _ in range(3)]
        result=matrix_gate(b,c)
        self.assertEqual('fail',result['status']);self.assertEqual(['a'],result['stable_pass_regressions'])

    def test_variable_regression_is_inconclusive(self):
        b=[dict(a=True),dict(a=True),dict(a=False)];c=[dict(a=True),dict(a=False),dict(a=False)]
        self.assertEqual('inconclusive',matrix_gate(b,c)['status'])
        with self.assertRaises(SpecError):matrix_gate(b,c[:2])
        with self.assertRaises(SpecError):matrix_gate(b,[dict(a=1)]*3)

    def test_same_run_cannot_be_its_own_candidate(self):
        with self.assertRaisesRegex(SpecError,'cannot be reused'):
            compare(self.catalog,self.full,[self.historical]*3,[self.historical]*3)

    def test_operator_case_retains_real_shape_and_readiness_gaps(self):
        result=prepare(self.catalog,self.breakdown)
        self.assertEqual([4096,3072],result[0]['contract']['weight_shape_kn'])
        self.assertEqual('synthetic_with_checkpoint_weights',result[0]['contract']['activation_origin'])
        self.assertTrue(any('tolerances' in s for s in result[0]['blockers']))
        changed=copy.deepcopy(self.breakdown);changed['model_ref']=dict(id='different',version='1.0.0')
        with self.assertRaisesRegex(SpecError,'scope differs'):prepare(self.catalog,changed)


if __name__=='__main__':unittest.main()
