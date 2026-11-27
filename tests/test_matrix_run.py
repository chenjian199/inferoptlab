import copy
from pathlib import Path
import tempfile
import unittest
import json
import contextlib
from unittest.mock import patch, MagicMock

from benchmark.load.matrix_run import budget, validate, report, run, score
from tools.specs import read, SpecError

ROOT=Path(__file__).resolve().parents[1]

def rank(index=0, blocks=2387):
    return dict(dp_rank=index,num_blocks=blocks,groups=[
        dict(type='MambaSpec',spec=dict(mamba_cache_mode='align',num_speculative_blocks=0,num_prefill_checkpoint_blocks=0)) for _ in range(4)
    ]+[dict(type='MLAAttentionSpec'),dict(type='CircularBufferSpec')],
        costs=[dict(input_tokens=4096,output_tokens=512,runtime_blocks_by_group=[2,2,2,2,8,1])])

class MatrixTests(unittest.TestCase):
    def setUp(self):self.matrix=read(ROOT/'benchmark-matrix.yaml')

    def test_current_matrix_supported(self):validate(self.matrix)

    def test_actual_pool_budget_clamps_without_running_limit(self):
        result=budget(self.matrix,[rank()],4096)
        self.assertEqual(result['capacity_limit'],108)
        self.assertEqual(result['points'][-1]['concurrency'],108)
        self.assertEqual(result['points'][-1]['requests'],432)
        self.assertEqual(result['ranks'][0]['blocks_per_slot'],22)
        self.assertEqual([p['concurrency'] for p in result['points']], [1,2,4,8,16,32,48,64,80,96,108])

    def test_unequal_dp_pool_uses_sticky_bound(self):
        result=budget(self.matrix,[rank(0,45),rank(1,89)],4096)
        self.assertEqual(result['capacity_limit'],4)

    def test_unrecognized_layout_blocks_instead_of_guessing(self):
        row=rank();row['groups'][0]['spec']['mamba_cache_mode']='all'
        with self.assertRaises(SpecError):budget(self.matrix,[row],4096)

    def test_zero_budget_has_no_scored_points(self):
        self.assertEqual(budget(self.matrix,[rank(blocks=19)],4096)['points'],[])

    def test_report_does_not_publish_invalid_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)
            report(out,dict(status='scanning',updated_at='now',deployments=[],points=[dict(directory=tmp,status='failed')]))
            self.assertIn('failed',(out/'summary.csv').read_text(encoding='utf-8-sig'))
            self.assertIn('tpot_p95_ms',(out/'summary.csv').read_text(encoding='utf-8-sig'))

    def _run_fake(self, prepare_error=None, device_fault=False, repetitions=1):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);model=root/'model';model.mkdir()
            matrix=copy.deepcopy(self.matrix)
            matrix['target']['model_path']=str(model);matrix['target']['tokenizer_path']=str(model)
            matrix['workload_matrix'].update(input_tokens=[4096],concurrency=[1])
            matrix['requests']['repetitions']=repetitions
            for axis in matrix['deployment_matrix']:
                matrix['deployment_matrix'][axis]=matrix['deployment_matrix'][axis][:1]
            config=root/'matrix.json';config.write_text(json.dumps(matrix))
            server=MagicMock();server.container_id='owned';server.launch.return_value=['docker','run']
            if device_fault:
                def close_with_fault():
                    for attempt in root.glob('experiments/runs/test/*/server-*'):
                        (attempt/'server.log').write_text('CUDA error: an illegal memory access was encountered')
                server.close.side_effect=close_with_fault
            patches={
                'dataset.tokenizer_fingerprint':dict(sha='test'), 'dataset.load_tokenizer':object(),
                'environment':{}, 'aiperf.check_installation':'aiperf',
                'vllm.Deployment':server,'sglang.wait_ready':None,'mc.verify':None,
                'mc.pool_inventory':[rank()],
                'cd.api':dict(vllm_config=dict(model_config=dict(max_model_len=100000))),
                'cd.prepare_slots':[dict(context_ids=[1],ids=[1,2],rank=0,slot=0)],
                'cd.qualify_slots':dict(valid=True),
            }
            with contextlib.ExitStack() as stack:
                mocks={name:stack.enter_context(patch('benchmark.load.matrix_run.'+name,return_value=value)) for name,value in patches.items()}
                if prepare_error:mocks['cd.prepare_slots'].side_effect=prepare_error
                stack.enter_context(patch('benchmark.load.matrix_run.deadline',side_effect=lambda _:contextlib.nullcontext()))
                score=stack.enter_context(patch('benchmark.load.matrix_run.score',side_effect=[SpecError('test failure')]+[None]*(2*repetitions)))
                stack.enter_context(patch('builtins.print'))
                out=root/'experiments/runs/test';run(root,config,out,root/'cache')
            state=read(out/'state.json')
            return state,mocks,server,score

    def test_failed_point_restarts_rewarms_then_continues_outputs(self):
        state,mocks,server,score=self._run_fake()
        self.assertEqual([p['status'] for p in state['points']],['failed','completed','completed'])
        self.assertEqual(mocks['cd.prepare_slots'].call_count,3)
        self.assertEqual(server.launch.call_count,2)
        self.assertEqual(score.call_count,3)
        self.assertEqual([p['output_tokens'] for p in state['points']],[128,128,512])

    def test_shared_preparation_failure_does_not_retry_each_output(self):
        state,mocks,server,score=self._run_fake(SpecError('prefill failed'))
        self.assertEqual([p['status'] for p in state['points']],['failed','failed','blocked_group_preparation'])
        self.assertEqual(mocks['cd.prepare_slots'].call_count,2)
        self.assertEqual(score.call_count,0)

    def test_each_output_repetition_and_retry_has_independent_preparation(self):
        state,mocks,server,scorer=self._run_fake(repetitions=2)
        self.assertEqual(sum(p['status']=='completed' for p in state['points']),4)
        calls=mocks['cd.prepare_slots'].call_args_list
        self.assertEqual(len(calls),5)
        self.assertEqual(len({str(c.args[6]) for c in calls}),5)
        self.assertEqual({c.args[5] for c in calls},{self.matrix['requests']['seed']})
        self.assertEqual(mocks['cd.qualify_slots'].call_count,5)

    def test_measurement_attempts_do_not_share_attention_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);obs=root/'observations';obs.mkdir()
            phases=[]
            def process(*args,**kwargs):
                phases.append((obs/'qualification-active.txt').read_text())
                child=MagicMock();child.wait.return_value=0;child.poll.return_value=0
                return child
            def observations(directory,kind):
                if kind=='scheduler':return []
                rows=[dict(phase=phases[-1],builder=b,num_prefills=0,num_prefill_tokens=0)
                      for b in ('GDNAttentionMetadataBuilder','FlashMLASparseMetadataBuilder')]
                if len(phases)>1:
                    rows.append(dict(phase=phases[0],builder='FlashMLASparseMetadataBuilder',num_prefills=1,num_prefill_tokens=4096))
                return rows
            slots=[dict(ids=[1,2],context_ids=[1],rank=0)]
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch('benchmark.load.matrix_run.subprocess.Popen',side_effect=process))
                stack.enter_context(patch('benchmark.load.matrix_run.metrics_snapshot'))
                stack.enter_context(patch('benchmark.load.matrix_run.cd.observations',side_effect=observations))
                stack.enter_context(patch('benchmark.load.matrix_run.cd.scheduler_evidence',return_value={'valid':True}))
                stack.enter_context(patch('benchmark.load.matrix_run.cd.validate_profile',return_value={'valid':True}))
                for attempt in ('first','retry'):
                    score(root,'aiperf',self.matrix,dict(served_model='model',tokenizer_path='model',url='http://unused'),
                          obs,slots,1,128,1,'same-point',root/attempt/'measurement')
            self.assertEqual(len(set(phases)),2)
            self.assertFalse((obs/'qualification-active.txt').exists())

    def test_repeated_device_fault_quarantines_deployment(self):
        state,mocks,server,score=self._run_fake(SpecError('HTTP 500'),True)
        self.assertEqual(len(state['points']),2)
        self.assertEqual(state['deployments'][0]['status'],'failed')
        self.assertIn('quarantined',state['deployments'][0]['error'])
        self.assertEqual(score.call_count,0)

if __name__=='__main__':unittest.main()
