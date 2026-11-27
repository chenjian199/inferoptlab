import copy
import json
from pathlib import Path
import tempfile
import unittest
import importlib.util
from types import SimpleNamespace
from unittest.mock import patch

from benchmark.load.decode_protocol import cache_evidence, make_fixture, profile_command, scheduler_evidence, validate_profile


class DecodeProtocolTests(unittest.TestCase):
    def test_aiperf_receives_both_concurrency_and_total_request_count(self):
        serving=dict(served_model='model',tokenizer_path='/models/model',url='http://localhost:18082')
        command=profile_command('aiperf',serving,Path('inputs.json'),Path('aiperf'),48,192,900)
        self.assertEqual(command[command.index('--concurrency')+1],'48')
        self.assertEqual(command[command.index('--request-count')+1],'192')
        self.assertIn('--no-allow-dataset-wrap',command)
        self.assertNotIn('--warmup-request-count',command)

    def test_request_fixture_honors_a_multiplier_other_than_four(self):
        slots=[dict(ids=[1,2],rank=0),dict(ids=[3,4],rank=1)]
        fixture,expected=make_fixture(slots,50,3,'model','point')
        self.assertEqual(len(expected),6)
        self.assertEqual([len(s['payloads']) for s in fixture['data']],[3,3])

    def test_reset_failure_prevents_warmup_requests(self):
        from benchmark.load.decode_protocol import prepare_slots
        from tools.specs import SpecError
        tokenizer=SimpleNamespace(apply_chat_template=lambda *a,**k: {'input_ids':[1,2]})
        with tempfile.TemporaryDirectory() as tmp, \
                patch('benchmark.load.decode_protocol.dataset.prompt',return_value='prompt'), \
                patch('benchmark.load.decode_protocol.api',return_value={'success':False}) as api:
            with self.assertRaises(SpecError):
                prepare_slots(tokenizer,dict(url='http://unused',served_model='model'),2,1,1,42,Path(tmp),10)
            self.assertEqual(api.call_count,1)
            self.assertEqual(api.call_args.args[1],'/reset_prefix_cache')

    def test_every_preparation_resets_before_rewarming_identical_sticky_slots(self):
        from benchmark.load.decode_protocol import prepare_slots
        tokenizer=SimpleNamespace(apply_chat_template=lambda messages,**k:
                                  {'input_ids':[int(messages[0]['content']),2]})
        events=[]
        def api(url,endpoint,body=None,rank=0,timeout=900):
            events.append((endpoint,rank))
            if endpoint=='/reset_prefix_cache':return {'success':True}
            return dict(choices=[dict(token_ids=[3])],usage=dict(prompt_tokens=len(body['prompt'])))
        with tempfile.TemporaryDirectory() as tmp, \
                patch('benchmark.load.decode_protocol.dataset.prompt',side_effect=lambda tok,rng,n: str(rng.randrange(1000000))), \
                patch('benchmark.load.decode_protocol.api',side_effect=api):
            results=[]
            for name in ('output128','output512'):
                directory=Path(tmp)/name;directory.mkdir()
                results.append(prepare_slots(tokenizer,dict(url='http://unused',served_model='model'),2,2,2,42,directory,10))
            self.assertEqual(results[0],results[1])
            self.assertEqual(events,[('/reset_prefix_cache',0),('/v1/completions',0),('/v1/completions',0),
                                     ('/v1/completions',1),('/v1/completions',1)]*2)

    def test_qualification_ids_separate_same_named_warmup_directories(self):
        from benchmark.load.decode_protocol import qualification_phase
        first=qualification_phase(Path('attempt1/warmup'))
        second=qualification_phase(Path('attempt2/warmup'))
        self.assertNotEqual(first,second)
        self.assertEqual(first,qualification_phase(Path('attempt1/warmup')))

    def test_offline_aiperf_local_tokenizer_never_uses_hub_resolver(self):
        path=Path(__file__).resolve().parents[1]/'benchmark/load/aiperf_hooks/sitecustomize.py'
        spec=importlib.util.spec_from_file_location('cached_aiperf_tokenizer_hook',path)
        module=importlib.util.module_from_spec(spec)
        import sys
        before=list(sys.meta_path)
        try:
            spec.loader.exec_module(module)
            class Tokenizer:
                @classmethod
                def _resolve_local_snapshot(cls,name,revision):return 'hub:'+name+'@'+revision
            module.local_tokenizer(SimpleNamespace(Tokenizer=Tokenizer))
            with tempfile.TemporaryDirectory() as tmp:
                self.assertEqual(Tokenizer._resolve_local_snapshot(tmp,'main'),str(Path(tmp).resolve()))
            self.assertEqual(Tokenizer._resolve_local_snapshot('org/model','main'),'hub:org/model@main')
        finally:sys.meta_path[:]=before

    def test_aiperf_keeps_rank_headers_when_serializing_raw_payloads(self):
        path=Path(__file__).resolve().parents[1]/'benchmark/load/aiperf_hooks/sitecustomize.py'
        spec=importlib.util.spec_from_file_location('cached_aiperf_test_hook',path)
        module=importlib.util.module_from_spec(spec)
        # Loading this isolated file registers a finder; remove it after testing.
        import sys
        before=list(sys.meta_path)
        try:
            spec.loader.exec_module(module)
            class Loader:
                def convert_to_conversations(self,data):return data
            class Manager:
                def _select_mmap_format(self,conversations):return 'payload_bytes'
            module.attach_ranks(SimpleNamespace(InputsJsonPayloadLoader=Loader))
            module.preserve_headers(SimpleNamespace(DatasetManager=Manager,
                MemoryMapFormat=SimpleNamespace(CONVERSATION='conversation')))
            turn=SimpleNamespace(raw_payload={'_inferoptlab_dp_rank':7,'request_id':'cachedD-test'},extra_headers=None)
            conversations=[SimpleNamespace(turns=[turn])]
            Loader().convert_to_conversations(conversations)
            self.assertNotIn('_inferoptlab_dp_rank',turn.raw_payload)
            self.assertEqual(turn.extra_headers,{'X-data-parallel-rank':'7','X-Request-ID':'cachedD-test'})
            self.assertEqual(Manager()._select_mmap_format(conversations),'conversation')
        finally:
            sys.meta_path[:]=before

    def test_context_ratio_excludes_only_one_real_seed(self):
        response = dict(usage=dict(prompt_tokens=4097, completion_tokens=20,
            prompt_tokens_details=dict(cached_tokens=4096)))
        result = cache_evidence(response, 4096, 20)
        self.assertTrue(result['valid'])
        self.assertEqual(result['original_context_hit_ratio'], 1)
        self.assertLess(result['wire_prompt_hit_ratio'], 1)
        response['usage']['prompt_tokens_details']['cached_tokens'] = 4080
        self.assertFalse(cache_evidence(response, 4096, 20)['valid'])

    def test_sticky_independent_slots_and_four_turns(self):
        slots = [dict(ids=[1, 2, 3], rank=0), dict(ids=[4, 5, 6], rank=1)]
        fixture, expected = make_fixture(slots, 20, 4, 'model', 'point')
        self.assertEqual(len(expected), 8)
        self.assertEqual(len(fixture['data']), 2)
        for slot, session in enumerate(fixture['data']):
            self.assertEqual(len(session['payloads']), 4)
            for request in session['payloads']:
                self.assertEqual(request['_inferoptlab_dp_rank'], slot)
                self.assertEqual(request['prompt'], slots[slot]['ids'])
                self.assertEqual(request['max_tokens'], 20)
        self.assertEqual(len(set(expected)), 8)

    def test_no_missing_duplicate_misrouted_or_prefilled_request(self):
        identity = 'cachedD-point-s000-t00-end'
        row = dict(request_id='cmpl-'+identity+'-0', dp_rank=1, prompt_tokens=4097,
            first_computed_tokens=4096, first_query_tokens=1, max_query_tokens=1,
            scheduled_tokens=20, steps=20, preemptions=0, output_tokens=20)
        expected = {identity: 1}
        self.assertTrue(scheduler_evidence([row], expected, 4096, 20)['valid'])
        self.assertFalse(scheduler_evidence([], expected, 4096, 20)['valid'])
        self.assertFalse(scheduler_evidence([row, row], expected, 4096, 20)['valid'])
        for field, value in [('dp_rank',0),('first_computed_tokens',4080),
                ('max_query_tokens',17),('preemptions',1),('scheduled_tokens',21),('output_tokens',19)]:
            changed = {**row, field: value}
            self.assertFalse(scheduler_evidence([changed], expected, 4096, 20)['valid'], field)

    def test_partial_multiturn_export_is_invalid(self):
        row = dict(metadata=dict(conversation_id='slot-0', turn_index=0, benchmark_phase='profiling'),
            metrics={k:dict(value=v,unit='tokens') for k,v in dict(input_sequence_length=4097,
                output_sequence_length=20, usage_prompt_cache_read_tokens=4096).items()})
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp)
            (artifact/'profile_export.jsonl').write_text(json.dumps(row)+'\n')
            expected={f'cachedD-point-s000-t{i:02d}-end':0 for i in range(4)}
            self.assertFalse(validate_profile(artifact,expected,[],4096,20)['valid'])


if __name__ == '__main__':
    unittest.main()
