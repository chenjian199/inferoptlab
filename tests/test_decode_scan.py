from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from benchmark.load.metrics.decode import report
from benchmark.load.planner import resolve, scenario_parts
from benchmark.load.counts import request_count
from tools.hardware.payload import verify_manifest
from tools.specs import Catalog, read, digest, SpecError


class DecodeScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog(); cls.catalog.load()

    def test_direct_performance_keeps_full_matrix_and_startup_gate(self):
        plan = read('recipes/plans/benchmark/glm53-vllm/decode-scan.yaml')
        snapshot = resolve(self.catalog, plan)
        self.assertEqual(plan['mode'], 'exploratory')
        self.assertTrue(plan['qualification_required'])
        self.assertEqual(len(snapshot['trials']), 288)
        self.assertEqual(snapshot['execution_issues'], [])
        self.assertTrue(any('/semantics' in e for e in snapshot['readiness_issues']))
        self.assertEqual({t['concurrency'] for t in snapshot['trials']}, {1, 2, 4, 8, 16, 32, 64, 128})
        scenarios = [scenario_parts(self.catalog, ref) for ref in plan['scenario_refs']]
        self.assertEqual({(workload['input']['tokens'], workload['output']['tokens'])
                          for _, _, workload, _ in scenarios},
                         {(i, o) for i in [4096, 16384, 65536] for o in [20, 50]})
        for scene, case, workload, _ in scenarios:
            self.assertEqual(case['declared_context']['output'], str(workload['output']['tokens']))
            self.assertIn('/decode-short-output/', scene['dataset_dir'])

    def test_failure_skip_requires_exact_startup_failure_and_rejects_cleanup_failure(self):
        from benchmark.load.qualification import binding,verify_receipt
        from benchmark.common.io import json_write
        plan=read('recipes/plans/benchmark/glm53-vllm/decode-scan.yaml')
        snapshot=resolve(self.catalog,plan)
        receipt=dict(deployments=[dict(binding=binding(self.catalog,self.catalog.get(r)),status='failed')
                                 for r in plan['deployment_refs']])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'qualification.json'
            def save():
                receipt['content_sha256']=digest({k:v for k,v in receipt.items() if k!='content_sha256'})
                json_write(path,receipt)
            save()
            with self.assertRaises(SpecError):verify_receipt(self.catalog,snapshot,path)
            self.assertEqual(verify_receipt(self.catalog,snapshot,path,allow_failed=True),receipt)
            receipt['deployments'][0]['status']='cleanup_failed';save()
            with self.assertRaises(SpecError):verify_receipt(self.catalog,snapshot,path,allow_failed=True)
            receipt['deployments'][0]['status']='failed'
            receipt['deployments'][0]['binding']['model']='0'*64;save()
            with self.assertRaises(SpecError):verify_receipt(self.catalog,snapshot,path,allow_failed=True)

    def test_all_decode_workloads_use_exactly_four_requests_per_concurrency(self):
        points = [1, 2, 4, 8, 16, 32, 64, 128]
        workloads = list(Path('recipes/workloads/glm53-vllm/decode').glob('*.yaml'))
        self.assertEqual(len(workloads), 6)
        for path in workloads:
            workload = read(path)
            self.assertNotIn('min_count', workload['requests'])
            self.assertEqual([request_count(workload, c) for c in points],
                             [4, 8, 16, 32, 64, 128, 256, 512])

    def test_five_layout_extension_is_disjoint_and_preserves_measurement_contracts(self):
        plans=[read('recipes/plans/benchmark/glm53-vllm/'+name+'.yaml')
               for name in ['decode-scan','decode-additional-layouts','decode-five-layouts']]
        snapshots=[resolve(self.catalog,plan) for plan in plans]
        self.assertEqual([len(s['trials']) for s in snapshots],[288,432,720])
        self.assertTrue(all(not s['execution_issues'] for s in snapshots))
        def points(snapshot):
            return {(t['deployment_ref']['id'],t['scenario_ref']['id'],t['concurrency'],t['repetition'])
                    for t in snapshot['trials']}
        old,added,all_points=map(points,snapshots)
        self.assertFalse(old & added)
        self.assertEqual(old | added,all_points)
        self.assertEqual(plans[0]['scenario_refs'],plans[1]['scenario_refs'])
        for ref in plans[2]['deployment_refs']:
            dep=self.catalog.get(ref)
            self.assertEqual(dep['scheduling']['max_running_requests']*dep['parallelism']['dp'],128)
            self.assertEqual(dep['scheduling']['max_model_len'],73728)
            self.assertEqual(dep['scheduling']['max_num_batched_tokens'],4096)
            self.assertEqual(dep['model_ref']['version'],'1.1.0')
            self.assertFalse(dep['prefix_cache'])
            self.assertTrue(dep['backend_options']['--enforce-eager'])

    def test_post_first_token_excludes_ttft_not_other_requests_prefill(self):
        rows = [dict(id='success', status='success', issues=[], ttft=100, e2e_latency=1120, output_tokens=512),
                dict(id='failed', status='failed', issues=[], ttft=None, e2e_latency=None, output_tokens=None)]
        bundle = dict(validity='valid', raw_sha256='a' * 64, counts=dict(planned=2, succeeded=1, failed=1, missing=0))
        with tempfile.TemporaryDirectory() as directory:
            value = report(Path(directory), rows, bundle, [])
        self.assertEqual(value['post_first_token_ms']['mean'], 1020)
        self.assertEqual(value['tpot_ms']['mean'], 1020 / 511)
        self.assertEqual(value['tpot_ms']['count'], 1)
        self.assertTrue(value['concurrent_prefill_interference_possible'])
        self.assertFalse(value['strict_device_decode'])
        self.assertFalse(value['eligible_for_performance_comparison'])

    def test_payload_identity_is_bound_to_real_manifest(self):
        model = deepcopy(self.catalog.get({'id': 'cluster-glm53-flash-w8a8', 'version': '1.1.0'}))
        self.assertEqual(verify_manifest(self.catalog, model), [])
        model['identity']['weights_sha256'] = '0' * 64
        self.assertTrue(verify_manifest(self.catalog, model))
        del model['checkpoint']['payload_source_ref']
        self.assertTrue(self.catalog.structural_errors(model))


if __name__ == '__main__':
    unittest.main()
