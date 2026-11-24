"""Synthetic cache replay, proportional counts, immutable records and baselines."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.specs import Catalog, ROOT, SpecError, read, digest
from tools.experiments import index, baseline, check
from benchmark.load.counts import at_point, request_count, fixture_source
from benchmark.load.cache import assess
from benchmark.load.dataset import prepare
from benchmark.common.io import json_write, jsonl_write, inside
from benchmark.load.planner import resolve, execution_issues
from benchmark.load.runner import _execute
from benchmark.load.cli import analyze
from test_benchmark import native, ref, TokenizerFixture


class ExperimentFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=Catalog();cls.base.load()

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'schemas/definitions',self.root/'schemas/definitions')
        self.c=copy.copy(self.base);self.c.root=self.root;self.c.documents=copy.deepcopy(self.base.documents)

    def get(self,name):return self.c.get(ref(name))

    def configure(self):
        plan=self.get('benchmark-smoke-plan')
        scene=self.get('benchmark-smoke')
        work=self.get('workload-benchmark-smoke');proto=self.get('benchmark-smoke-protocol')
        work['requests'].update(count=None,count_multiplier=3)
        work['arrival']['load_points']=[1,2]
        work['cache'].update(prefix_reuse='enabled',target_hit_ratio=1.0,preparation='preload_exact_input_dataset')
        proto.update(scope='decode',method='prefix_reuse_decode',cache_replay=dict(fill_output_tokens=1,max_uncached_tokens_per_request=0))
        proto['execution'].update(repetitions=2,warmup_request_count=1)
        plan['budget']['max_runs']=4
        dep=self.get('dsv4-bw1000-attached');dep['prefix_cache']=True
        tokenizer=self.root/'tokenizer';tokenizer.mkdir();(tokenizer/'tokenizer.json').write_text('{}')
        dep['serving'].update(management='sglang',served_model='fixture',model_path='/fixture',tokenizer_path=str(tokenizer))
        dep['devices']=[dict(rank=i,visible_index=i,device_id=f'gpu-{i}') for i in range(8)]
        hw=self.c.get(dep['hardware_ref']);hw['resources']['nodes']=[dict(node_id='fixture',devices=[dict(device_id=f'gpu-{i}',device_profile_ref=ref('bw1000')) for i in range(8)],cpu='fixture',dram_gb=512,nics=[])]
        hw['resources']['allocated_devices']=8
        for concurrency in work['arrival']['load_points']:
            prepare(at_point(work,concurrency),proto,tokenizer,inside(self.root,fixture_source(scene,work,concurrency)),tokenizer=TokenizerFixture())
        return plan,work,proto,dep

    def test_counts_and_invalid_ambiguity(self):
        work=self.get('workload-benchmark-smoke');work['requests'].update(count=None,count_multiplier=4)
        self.assertEqual(512,request_count(work,128))
        self.assertEqual(12,at_point(work,3)['requests']['count'])
        work['requests']['count']=32
        self.assertTrue(self.c.structural_errors(work))
        with self.assertRaises(SpecError):request_count(work,2)

    def test_same_input_identity_across_p_and_d(self):
        plan,work,proto,dep=self.configure()
        w=at_point(work,2);w['output']['tokens']=1
        m=prepare(w,proto,dep['serving']['tokenizer_path'],self.root/'prefill',tokenizer=TokenizerFixture())
        original=read(inside(self.root,fixture_source(self.get('benchmark-smoke'),work,2))/'manifest.json')
        self.assertEqual(original['input_content_sha256'],m['input_content_sha256'])
        self.assertEqual(original['files']['requests.jsonl']['sha256'],m['files']['requests.jsonl']['sha256'])

    def test_external_cache_reset_is_rejected(self):
        plan,work,proto,dep=self.configure();dep['serving']['management']='external'
        self.assertIn('owned SGLang','\n'.join(execution_issues(self.c,plan)))

    def test_cache_usage_is_required_and_residual_is_not_hidden(self):
        plan,work,proto,dep=self.configure();raw=self.root/'raw.jsonl'
        row=native('a');jsonl_write(raw,[row])
        self.assertEqual('invalid',assess(raw,['a'],work,proto)['status'])
        row['metrics']['usage_prompt_cache_read_tokens']=dict(value=127,unit='tokens');jsonl_write(raw,[row])
        self.assertEqual('invalid',assess(raw,['a'],work,proto)['status'])
        row['metrics']['usage_prompt_cache_read_tokens']['value']=128;jsonl_write(raw,[row])
        self.assertEqual('passed',assess(raw,['a'],work,proto)['status'])
        self.assertEqual('invalid',assess(raw,['a','b'],work,proto)['status'])

    def test_full_replay_multirun_registration_reanalysis_and_baseline(self):
        self.pipeline(False)

    def test_cache_miss_cannot_become_valid_baseline(self):
        self.pipeline(True)

    def pipeline(self,miss):
        plan,work,proto,dep=self.configure();events=[]
        snapshot=resolve(self.c,plan)
        self.assertFalse(snapshot['execution_issues'])
        class Response:
            status=200
            def __enter__(self):events.append('reset');return self
            def __exit__(self,*args):pass
            def read(self):return b'Cache flushed.'
        def invoke(command,log_path,timeout_s):
            out=Path(command[command.index('--artifact-dir')+1]);out.mkdir(parents=True,exist_ok=True)
            filename=Path(command[command.index('--input-file')+1])
            ids=[json.loads(line)['session_id'] for line in filename.read_text(encoding='utf-8').splitlines()]
            count=int(command[command.index('--request-count')+1]);self.assertEqual(count,len(ids))
            osl=int(next(x.split(':')[1] for x in command if x.startswith('max_tokens:')))
            phase='fill' if out.name=='cache-fill' else 'warmup' if out.name=='warmup' else 'score'
            events.append(phase)
            if phase=='score':self.assertEqual(['reset','fill'],events[-3:-1])
            rows=[]
            for identity in ids:
                row=native(identity,osl=osl)
                row['metrics']['usage_prompt_cache_read_tokens']=dict(value=64 if miss else 128,unit='tokens')
                rows.append(row)
            jsonl_write(out/'profile_export.jsonl',rows);json_write(out/'profile_export_aiperf.json',dict(aiperf_version='0.12.0'))
            log_path.write_text('SYNTHETIC; NO GPU EXECUTION',encoding='utf-8')
            return dict(returncode=0,timed_out=False,elapsed_s=.01)
        observed=dict(server_args=dict(tp_size=8,pp_size=1,ep_size=8,dp_size=1,disable_radix_cache=False,enable_cache_report=True,stream_interval=1,context_length=4096))
        env=dict(device_probe=dict(provider='nvidia-smi',status='observed',output='\n'.join(f'{i}, gpu-{i}' for i in range(8))))
        with patch('benchmark.load.dataset.load_tokenizer',return_value=TokenizerFixture()),patch('benchmark.load.adapters.aiperf.run',side_effect=invoke),patch('benchmark.load.adapters.sglang.Deployment.launch',return_value=['synthetic']),patch('benchmark.load.adapters.sglang.wait_ready'),patch('benchmark.load.adapters.sglang.smoke'),patch('benchmark.load.adapters.sglang.inspect_server',return_value=(observed,[])),patch('benchmark.load.runner.environment',return_value=env),patch('benchmark.load.cache.urlopen',return_value=Response()):
            directory,state=_execute(self.c,snapshot,plan,'fixture-aiperf',self.root/'experiments/runs/benchmark')
        self.assertEqual(4,len(state['runs']))
        run=directory/state['runs'][0]['directory'];summary=read(run/'summary.json')
        self.assertEqual(3,summary['counts']['planned'])
        self.assertEqual('invalid' if miss else 'passed',summary['cache_replay']['status'])
        recomputed=analyze(self.c,run,self.root/'reanalysis')
        self.assertEqual(summary['cache_replay'],recomputed['cache_replay'])
        idx=index(self.c);self.assertFalse(idx['errors']);self.assertEqual(4,len(idx['runs']))
        identity=idx['runs'][0]['id']
        if miss:
            with self.assertRaises(SpecError):baseline(self.c,'bad',[identity],'workflow','fixture')
        else:
            baseline(self.c,'workflow',[identity],'workflow','fixture-only')
            with self.assertRaises(SpecError):baseline(self.c,'formal',[identity],'performance','not frozen')
            with self.assertRaises(FileExistsError):baseline(self.c,'workflow',[identity],'workflow','must not overwrite')
            record=read(self.root/'experiments/records'/f'{identity}.yaml')
            record['concurrency']=99
            record['content_sha256']=digest({k:v for k,v in record.items() if k!='content_sha256'})
            with self.assertRaisesRegex(SpecError,'metadata differs'):check(self.c,record)
            lifecycle=run/'cache-lifecycle.json';saved=lifecycle.read_bytes()
            value=read(lifecycle);value['input_sha256']='0'*64;json_write(lifecycle,value)
            bad=analyze(self.c,run,self.root/'reanalysis-bad-cache')
            self.assertEqual('invalid',bad['cache_replay']['status'])
            self.assertNotEqual('valid',bad['validity'])
            lifecycle.write_bytes(saved)
        (run/'raw/aiperf/profile_export.jsonl').write_text('{}\n',encoding='utf-8')
        idx=index(self.c);self.assertTrue(idx['errors']);self.assertEqual(3,len(idx['runs']))


if __name__=='__main__':unittest.main()
