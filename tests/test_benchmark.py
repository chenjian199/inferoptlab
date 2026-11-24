"""Synthetic native-format fixtures; these tests do not measure GPU performance."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.specs import Catalog, ROOT, SpecError, digest, read
from benchmark.load import dataset
from benchmark.common import process
from benchmark.load.adapters import aiperf, sglang
from benchmark.load.cli import analyze
from benchmark.common.io import json_write, jsonl_write, inside
from benchmark.load.metrics.evaluate import evaluate
from benchmark.load.metrics.normalize import normalize
from benchmark.load.planner import resolve, snapshot_errors, execution_issues
from benchmark.load.runner import _execute, lease


def ref(name):
    return dict(id=name,version='1.0.0')


def native(logical,start=1_000_000_000,end=2_000_000_000,error=None,isl=128,osl=16,ttft=100,latency=250):
    return dict(metadata=dict(conversation_id=logical,x_request_id='http-'+logical,turn_index=0,
        request_start_ns=start,request_end_ns=end,benchmark_phase='profiling',was_cancelled=False),
        metrics={} if error else {name:dict(value=value,unit=unit) for name,value,unit in [
            ('input_sequence_length',isl,'tokens'),('output_sequence_length',osl,'tokens'),
            ('time_to_first_token',ttft,'ms'),('request_latency',latency,'ms')]},error=error)


class TokenizerFixture:
    """One word = one token, plus five template tokens. Test fixture only."""
    def encode(self,text,add_special_tokens=False):
        return list(range(len(text.split())))
    def apply_chat_template(self,messages,tokenize=True,add_generation_prompt=True,return_dict=True):
        return {'input_ids':[0]*5+self.encode(messages[0]['content'])}


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Catalog()
        cls.base.load()

    def setUp(self):
        self.catalog=copy.copy(self.base)
        self.catalog.documents=copy.deepcopy(self.base.documents)
        temporary=tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory=Path(temporary.name)

    def get(self,name):
        return self.catalog.get(ref(name))

    def export(self,rows,ids=('a','b'),isl=128,osl=16):
        path=self.directory/'profile_export.jsonl'
        jsonl_write(path,rows)
        return normalize(path,list(ids),isl,osl,'fixture-run','a'*64,evidence_kind='imported')

    def test_matrix_is_deterministic_and_preserves_comparison_groups(self):
        plan=self.get('benchmark-compare-plan')
        first=resolve(self.catalog,plan)
        self.assertEqual(first,resolve(self.catalog,plan))
        self.assertEqual(len(first['trials']),54)
        self.assertEqual(len({t['id'] for t in first['trials']}),18)
        self.assertEqual(len({t['comparison_sha256'] for t in first['trials']}),6)
        self.assertTrue(first['execution_issues'])
        self.assertEqual(self.catalog.structural_errors(first),[])
        self.assertEqual(snapshot_errors(self.catalog,first),[])

    def test_snapshot_rehash_cannot_hide_matrix_tampering(self):
        snapshot=resolve(self.catalog,self.get('benchmark-smoke-plan'))
        snapshot['trials'][0]['concurrency']=99
        snapshot['content_sha256']=digest({k:v for k,v in snapshot.items() if k!='content_sha256'})
        self.assertTrue(snapshot_errors(self.catalog,snapshot))

    def test_freeze_preserves_real_blockers(self):
        with self.assertRaisesRegex(SpecError,'cannot freeze benchmark|source is missing'):
            resolve(self.catalog,self.get('benchmark-compare-plan'),freeze=True)

    def test_snapshot_cli_validation_does_not_need_live_attachments(self):
        import contextlib
        import io
        from tools.specs import main, write
        snapshot=resolve(self.catalog,self.get('benchmark-smoke-plan'))
        target=self.directory/'snapshot.yaml'
        write(target,snapshot)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['validate',str(target)]),0)

    def test_matrix_budget_and_reference_mismatch(self):
        plan=self.get('benchmark-compare-plan')
        plan['budget']['max_runs']=2
        with self.assertRaisesRegex(SpecError,'max_runs'):
            resolve(self.catalog,plan)
        self.get('dsv4-bw1000-baseline')['model_ref']=ref('glm-5.3')
        self.assertIn('model_ref differs','\n'.join(self.catalog.semantic_errors(plan)))

    def test_contract_case_cannot_use_exploratory_bypass(self):
        self.get('case-benchmark-short')['purpose']='contract'
        errors=execution_issues(self.catalog,self.get('benchmark-baseline-plan'))
        self.assertIn('explicitly diagnostic','\n'.join(errors))

    def test_backend_reserved_options_are_not_silently_overridden(self):
        deployment=self.get('dsv4-bw1000-attached')
        deployment['backend_options']={'--tp':2}
        self.assertIn('conflict','\n'.join(sglang.configuration_issues(deployment,self.get('sglang-dsv4-v0.5.15-post1-dev'))))

    def test_rank_map_does_not_multiply_ep(self):
        deployment=self.get('dsv4-bw1000-baseline')
        deployment['serving'].update(model_path='/fixture/model',tokenizer_path='/fixture/tokenizer',served_model='fixture')
        deployment['devices']=[dict(rank=i,device_id=f'fixture:{i}',visible_index=i) for i in range(8)]
        runtime=self.get('sglang-dsv4-v0.5.15-post1-dev')
        self.assertEqual(sglang.configuration_issues(deployment,runtime),[])
        cmd=sglang.command(deployment,runtime)
        self.assertEqual(cmd[cmd.index('--ep-size')+1],'8')
        self.assertIn('--disable-radix-cache',cmd)
        self.assertIn('--stream-interval',cmd)

    def test_dataset_preparation_and_tamper_detection(self):
        tokenizer=self.directory/'tokenizer'
        tokenizer.mkdir()
        (tokenizer/'tokenizer.json').write_text('{}')
        workload=self.get('workload-benchmark-smoke')
        protocol=self.get('benchmark-smoke-protocol')
        target=self.directory/'data'
        manifest=dataset.prepare(workload,protocol,tokenizer,target,tokenizer=TokenizerFixture())
        self.assertEqual(manifest['files']['requests.jsonl']['count'],4)
        with patch('benchmark.load.dataset.load_tokenizer',return_value=TokenizerFixture()):
            self.assertEqual(dataset.verify(workload,protocol,tokenizer,target),manifest)
        with (target/'requests.jsonl').open('a') as stream:
            stream.write('{}\n')
        with self.assertRaisesRegex(SpecError,'hash mismatch'):
            dataset.verify(workload,protocol,tokenizer,target,retokenize=False)

    def test_dataset_rejects_tokenizer_change_and_path_escape(self):
        tokenizer=self.directory/'tokenizer'
        tokenizer.mkdir()
        (tokenizer/'tokenizer.json').write_text('{}')
        workload=self.get('workload-benchmark-smoke')
        protocol=self.get('benchmark-smoke-protocol')
        target=self.directory/'data'
        dataset.prepare(workload,protocol,tokenizer,target,tokenizer=TokenizerFixture())
        (tokenizer/'tokenizer.json').write_text('{"changed":true}')
        with self.assertRaisesRegex(SpecError,'fingerprint differs'):
            dataset.verify(workload,protocol,tokenizer,target,retokenize=False)
        scene=self.get('benchmark-short')
        scene['dataset_dir']='../escape'
        self.assertIn('escapes repository','\n'.join(self.catalog.semantic_errors(scene)))

    def test_native_exports_include_failed_requests_and_full_drain(self):
        rows,bundle=self.export([native('a'),native('b',end=4_000_000_000,error=dict(type='TimeoutError'))])
        self.assertEqual(bundle['validity'],'valid')
        self.assertEqual(bundle['duration_s'],3)
        self.assertEqual(bundle['counts']['failed'],1)
        self.assertAlmostEqual(bundle['rates']['request_throughput'],1/3)
        self.assertEqual(bundle['rates']['success_rate'],.5)
        self.assertEqual(rows[0]['tpot'],10)
        self.assertIsNone(rows[0]['itl'])
        self.assertEqual(self.catalog.structural_errors(bundle),[])

    def test_missing_records_do_not_create_fake_throughput(self):
        rows,bundle=self.export([native('a')])
        self.assertEqual(bundle['counts']['missing'],1)
        self.assertEqual(bundle['validity'],'incomplete')
        self.assertIsNone(bundle['rates']['request_throughput'])
        self.assertEqual(bundle['rates']['success_rate'],.5)

    def test_duplicate_ids_and_output_mismatch_invalidate_run(self):
        rows,bundle=self.export([native('a'),native('a'),native('b',osl=2)])
        self.assertEqual(bundle['validity'],'invalid')
        self.assertIn('duplicate',' '.join(bundle['issues']))
        self.assertIn('output_tokens',' '.join(bundle['issues']))

    def test_single_token_output_has_no_tpot(self):
        rows,bundle=self.export([native('a',osl=1)],ids=('a',),osl=1)
        self.assertIsNone(rows[0]['tpot'])
        self.assertEqual(bundle['statistics']['tpot']['count'],0)

    def test_unit_conversion_and_warmup_exclusion(self):
        warm=native('warm')
        warm['metadata']['benchmark_phase']='warmup'
        record=native('a')
        record['metrics']['time_to_first_token']=dict(value=.1,unit='s')
        rows,bundle=self.export([warm,record],ids=('a',))
        self.assertEqual(rows[0]['ttft'],100)
        self.assertEqual(bundle['counts']['observed'],1)

    def test_joint_slo_requires_each_request_to_meet_all_constraints(self):
        rows,bundle=self.export([native('a'),native('b',ttft=500,latency=650)])
        constraint=lambda name,metric,value:dict(id=name,metric=metric,scope='request',statistic='per_request',operator='lt',threshold=dict(value=value),unit='ms',normalization=dict(basis='system'),severity='hard',population='all_planned_requests',raw_text='fixture')
        sla=dict(issues=[],constraints=[constraint('first','ttft',200),constraint('next','tpot',20)],
            joint_request_slo=dict(constraint_ids=['first','next'],min_attainment=.5,population='all_planned_requests'),quality_requirements=[],conditional_requirements=[])
        result=evaluate(sla,bundle,rows)
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['joint']['attainment'],.5)
        self.assertEqual(result['joint']['request_goodput'],1)
        self.assertEqual(result['quality_status'],'not_evaluated')
        self.assertEqual(evaluate(sla,bundle,rows,environment_issues=['unknown cache'])['status'],'inconclusive')

    def test_unsupported_itl_or_unresolved_sla_cannot_pass(self):
        rows,bundle=self.export([native('a'),native('b')])
        sla=copy.deepcopy(self.get('sla-deepseek-contract-5-decode'))
        sla['constraints'][1]['metric']='itl'
        self.assertEqual(evaluate(sla,bundle,rows)['status'],'inconclusive')

    def test_aiperf_command_freezes_inputs_and_excludes_warmup(self):
        deployment=self.get('dsv4-bw1000-attached')
        deployment['serving']['tokenizer_path']='/fixture/tokenizer'
        cmd=aiperf.command('aiperf',self.get('benchmark-smoke-plan'),deployment,self.get('workload-benchmark-smoke'),self.get('benchmark-smoke-protocol'),1,self.directory,self.directory/'raw')
        # AIPerf 0.12 rejects an explicit zero; omitted warmup options disable
        # its built-in phase because the controller runs a separate fixture.
        self.assertNotIn('--warmup-request-count',cmd)
        self.assertNotIn('--warmup-duration',cmd)
        self.assertEqual(cmd[cmd.index('--dataset-sampling-strategy')+1],'sequential')
        self.assertIn('--use-server-token-count',cmd)
        self.assertEqual(cmd[cmd.index('--export-level')+1],'raw')

    def test_timeout_terminates_owned_process_and_keeps_logs(self):
        result=process.run([sys.executable,'-c','import time; print("fixture",flush=True); time.sleep(10)'],self.directory/'process.log',.3)
        self.assertTrue(result['timed_out'])
        self.assertIn('fixture',(self.directory/'process.log').read_text())

    def test_required_telemetry_rejects_empty_or_partial_collectors(self):
        json_write(self.directory/'profile_export_aiperf.json',dict(aiperf_version='0.12.0'))
        json_write(self.directory/'server_metrics_export.json',{})
        self.assertIn('empty',' '.join(aiperf.telemetry_issues(self.directory,'both')))
        json_write(self.directory/'server_metrics_export.json',dict(metrics={'fixture':{'series':[{'stats':{'avg':0}}]}},
            summary=dict(endpoints_configured=['a','b'],endpoints_successful=['a'])))
        self.assertIn('unsuccessful',' '.join(aiperf.telemetry_issues(self.directory,'server')))

    def test_lease_prevents_simultaneous_execution(self):
        with lease(self.directory):
            with self.assertRaisesRegex(SpecError,'lease exists'):
                with lease(self.directory):
                    pass
        self.assertFalse((self.directory/'experiments/runs/benchmark/.execution.lock').exists())

    def test_pipeline_archives_results_and_offline_reanalysis(self):
        self._pipeline(False)

    def test_pipeline_retains_nonzero_exit_and_partial_results(self):
        self._pipeline(True)

    def _pipeline(self,fail):
        import shutil
        shutil.copytree(ROOT/'schemas/definitions',self.directory/'schemas/definitions')
        self.catalog.root=self.directory
        tokenizer=self.directory/'tokenizer'
        tokenizer.mkdir()
        (tokenizer/'tokenizer.json').write_text('{}')
        deployment=self.get('dsv4-bw1000-attached')
        deployment['serving'].update(tokenizer_path=str(tokenizer),served_model='fixture')
        workload=self.get('workload-benchmark-smoke')
        protocol=self.get('benchmark-smoke-protocol')
        protocol['execution']['repetitions']=2
        fixture=inside(self.directory,self.get('benchmark-smoke')['dataset_dir'])
        dataset.prepare(workload,protocol,tokenizer,fixture,tokenizer=TokenizerFixture())
        plan=self.get('benchmark-smoke-plan')
        snapshot=resolve(self.catalog,plan)
        def invoke(command,log_path,timeout_s):
            output=Path(command[command.index('--artifact-dir')+1])
            output.mkdir(parents=True,exist_ok=True)
            inputs=Path(command[command.index('--input-file')+1])
            ids=[json.loads(line)['session_id'] for line in inputs.read_text().splitlines()]
            jsonl_write(output/'profile_export.jsonl',[native(x) for x in ids[:1] if fail] if fail else [native(x) for x in ids])
            json_write(output/'profile_export_aiperf.json',dict(aiperf_version='0.12.0'))
            log_path.write_text('SYNTHETIC AIPerf subprocess fixture; not measured GPU evidence')
            return dict(returncode=7 if fail else 0,timed_out=False,elapsed_s=.1)
        observed=dict(server_args=dict(tp_size=8,pp_size=1,ep_size=8,dp_size=1,disable_radix_cache=True,stream_interval=1,context_length=4096))
        with patch('benchmark.load.dataset.load_tokenizer',return_value=TokenizerFixture()),patch('benchmark.load.adapters.aiperf.run',side_effect=invoke),patch('benchmark.load.adapters.sglang.wait_ready'),patch('benchmark.load.adapters.sglang.smoke'),patch('benchmark.load.adapters.sglang.inspect_server',return_value=(observed,[])),patch('benchmark.load.runner.environment',return_value=dict(device_probe=dict(status='unavailable'))):
            directory,state=_execute(self.catalog,snapshot,plan,'fixture-aiperf',self.directory/'results')
        self.assertEqual(state['status'],'completed_with_errors')
        self.assertEqual(len(state['runs']),2)
        self.assertEqual(state['runs'][0]['trial_id'],state['runs'][1]['trial_id'])
        self.assertEqual(state['runs'][0]['status'],'failed' if fail else 'unverified')
        run=directory/state['runs'][0]['directory']
        for filename in ['run.json','commands.json','environment.json','requests.jsonl','summary.json','sla.json','report.md','raw/aiperf/profile_export.jsonl']:
            self.assertTrue((run/filename).is_file(),filename)
        result=analyze(self.catalog,run,self.directory/'reanalysis')
        self.assertEqual(result['validity'],'incomplete' if fail else 'valid')
        self.assertFalse(json.loads((self.directory/'reanalysis/provenance.json').read_text())['new_gpu_execution'])


if __name__=='__main__':
    unittest.main()
