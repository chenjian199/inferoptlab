"""Recipe reuse, startup gates and observed vLLM configuration contracts."""
import copy
import json
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from tools.specs import Catalog, ROOT, SpecError, digest, read
from benchmark.load.adapters import vllm
from benchmark.load.counts import request_count, at_point, protocol_at_point
from benchmark.load.planner import resolve, embedded_catalog
from benchmark.load.qualification import binding, verify_receipt, select_qualified, qualify
from benchmark.load.cache import verify_reset


class ScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog(); cls.catalog.load()

    def setUp(self):
        self.dep = read(ROOT/'recipes/deployments/glm53-flash/c500/vllm/a-tp8.yaml')
        self.runtime = self.catalog.get(self.dep['runtime_ref'])
        self.plan = read(ROOT/'recipes/plans/benchmark/glm53-vllm/00-layout.yaml')

    def test_scan_plans_resolve_without_shadow_configuration(self):
        for path in (ROOT/'recipes/plans/benchmark/glm53-vllm').glob('*.yaml'):
            snapshot = resolve(self.catalog, read(path))
            self.assertEqual(snapshot['execution_issues'], [], path)
            self.assertTrue(snapshot['readiness_issues'])  # Not silently promoted to formal acceptance.
        self.assertEqual(len(resolve(self.catalog, self.plan)['trials']), 24)

    def test_tp_dp_ep_rank_count_and_command(self):
        d = copy.deepcopy(self.dep)
        d['parallelism'].update(tp=4, dp=2, ep=8)
        args = vllm.server_arguments(d, self.runtime)
        self.assertIn('--enable-expert-parallel', args)
        self.assertEqual(args[args.index('--data-parallel-size')+1], '2')
        d['parallelism']['ep'] = 4
        self.assertIn('EP must', '\n'.join(vllm.configuration_issues(d, self.runtime)))

    def test_budget_is_not_sglang_chunk_and_cannot_be_overridden(self):
        self.dep['scheduling']['chunked_prefill_tokens'] = 4096
        self.assertTrue(vllm.configuration_issues(self.dep, self.runtime))
        self.dep['scheduling']['chunked_prefill_tokens'] = None
        self.dep['backend_options']['--max-num-batched-tokens'] = 1
        self.assertIn('conflict', '\n'.join(vllm.configuration_issues(self.dep, self.runtime)))

    def test_request_multiplier_minimum_rounds_up_by_concurrency(self):
        workload = read(ROOT/'recipes/workloads/glm53-vllm/e2e-16k-confirm.yaml')
        self.assertEqual([request_count(workload, c) for c in [1, 16, 64, 128]], [200, 208, 256, 512])
        self.assertEqual(at_point(workload, 16)['requests']['count'], 208)
        self.assertEqual(self.catalog.structural_errors(at_point(workload, 16)), [])
        self.assertIsNone(workload['requests']['count'])
        protocol = read(ROOT/'recipes/protocols/glm53-vllm/e2e-confirm.yaml')
        self.assertEqual(protocol_at_point(protocol, 1)['execution']['warmup_request_count'], 4)
        self.assertEqual(protocol_at_point(protocol, 128)['execution']['warmup_request_count'], 128)
        self.assertEqual(protocol['execution']['warmup_request_count'], 4)

    def test_configuration_observation_detects_budget_and_graph_drift(self):
        actual = dict(parallel_config=dict(tensor_parallel_size=8,pipeline_parallel_size=1,data_parallel_size=1,enable_expert_parallel=False),
                      cache_config=dict(enable_prefix_caching=False,block_size=640),
                      scheduler_config=dict(max_num_seqs=1,max_num_batched_tokens=4096,enable_chunked_prefill=True,stream_interval=1),
                      model_config=dict(max_model_len=4096,enforce_eager=True))
        d = read(ROOT/'recipes/deployments/glm53-flash/c500/vllm/metax60-tp8-smoke.yaml')
        self.assertEqual(vllm.verify_server(d, {'vllm_config': actual}, 1024), [])
        d['backend_options']['--enforce-eager'] = False
        d['scheduling']['max_num_batched_tokens'] = 8192
        issues = '\n'.join(vllm.verify_server(d, {'vllm_config': actual}, 1024))
        self.assertIn('max_num_batched_tokens', issues)
        self.assertIn('enforce_eager', issues)
        actual['model_config']['enforce_eager'] = False
        actual['scheduler_config']['max_num_batched_tokens'] = 8192
        self.assertIn('graph candidate', '\n'.join(vllm.verify_server(d, {'vllm_config': actual}, 1024)))
        actual['compilation_config'] = dict(mode=0, cudagraph_mode=[2, 1], cudagraph_capture_sizes=[1, 2])
        self.assertEqual(vllm.verify_server(d, {'vllm_config': actual}, 1024), [])

    def test_qualification_gate_rejects_changes_and_records_excluded_candidates(self):
        snapshot = resolve(self.catalog, self.plan)
        catalog = embedded_catalog(self.catalog, snapshot)
        receipt = dict(deployments=[dict(id=self.dep['id'], binding=binding(catalog, self.dep), status='passed', maximum_context=16385,
                                        probes=[dict(input_tokens=16384, output_tokens=1, status='passed')])])
        receipt['content_sha256'] = digest(receipt)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'qualification.json'; path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(SpecError, 'no matching'):
                verify_receipt(catalog, snapshot, path)
            selected = select_qualified(self.catalog, snapshot, path)
            self.assertEqual(len(selected['deployment_refs']), 1)
            self.assertEqual(len(selected['extensions']['qualification.selection']['excluded']), 3)
            resolved = resolve(self.catalog, selected)
            embedded = embedded_catalog(self.catalog, resolved)
            verify_receipt(embedded, resolved, path)
            receipt['deployments'][0]['probes'][0]['input_tokens'] = 128
            receipt['content_sha256'] = digest({k:v for k,v in receipt.items() if k != 'content_sha256'})
            path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(SpecError, 'no matching'):
                verify_receipt(embedded, resolved, path)
            receipt['deployments'][0]['probes'][0]['input_tokens'] = 16384
            receipt['content_sha256'] = digest({k:v for k,v in receipt.items() if k != 'content_sha256'})
            path.write_text(json.dumps(receipt))
            embedded.get(self.dep)['scheduling']['max_running_requests'] = 7
            with self.assertRaisesRegex(SpecError, 'no matching'):
                verify_receipt(embedded, resolved, path)
            receipt['deployments'][0]['maximum_context'] = 999999
            path.write_text(json.dumps(receipt))
            with self.assertRaisesRegex(SpecError, 'hash mismatch'):
                verify_receipt(catalog, snapshot, path)

    def test_container_ownership_is_checked_before_stopping(self):
        owned = vllm.Deployment(self.dep, self.runtime, Path('not-written.log'))
        owned.container_id = 'other-container'
        with patch.object(vllm, 'docker') as docker:
            docker.return_value.stdout = json.dumps([{'Config': {'Labels': {'io.inferoptlab.owner': 'someone-else'}}}])
            with self.assertRaisesRegex(SpecError, 'ownership'):
                owned.close()
            self.assertEqual(docker.call_count, 1)

    def test_vllm_http_200_does_not_prove_cache_was_reset(self):
        response = dict(status=200, endpoint='/reset_prefix_cache', body='{"success":false}')
        with self.assertRaisesRegex(SpecError, 'success=false'):
            verify_reset(response)
        response['body'] = '{"success":true}'
        verify_reset(response)
        verify_reset(dict(status=200, endpoint='/flush_cache', body='Cache flushed.'))

    def test_failed_startup_is_persisted_and_never_qualified(self):
        self.plan['deployment_refs'] = self.plan['deployment_refs'][:1]
        snapshot = resolve(self.catalog, self.plan)
        class FailedDeployment:
            def __init__(self, *args): pass
            def launch(self): raise SpecError('synthetic startup failure; no GPU execution')
            def close(self): pass
        with tempfile.TemporaryDirectory(dir=ROOT/'experiments') as tmp:
            output = Path(tmp)/'qualification'
            with patch('benchmark.load.qualification.for_runtime', return_value=SimpleNamespace(Deployment=FailedDeployment)), \
                 patch('benchmark.load.adapters.metax.inventory', return_value={'status':'observed'}), \
                 patch('benchmark.load.adapters.metax.binding_issues', return_value=[]):
                receipt = qualify(self.catalog, snapshot, output)
            self.assertEqual(receipt['deployments'][0]['status'], 'failed')
            self.assertIn('synthetic startup failure', (output/'report.md').read_text(encoding='utf-8'))
            self.assertTrue((output/'resolved.yaml').is_file())
            with self.assertRaisesRegex(SpecError, 'no matching'):
                verify_receipt(embedded_catalog(self.catalog,snapshot),snapshot,output/'qualification.json')


if __name__ == '__main__':
    unittest.main()
