import copy
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from tools.specs import Catalog, ROOT, SpecError, read
from tools.hardware.metax import parse
from benchmark.load.adapters import for_runtime, vllm
from benchmark.load.dataset import token_count
from benchmark.load.adapters import metax


class ClusterIntakeTests(unittest.TestCase):
    def test_metax_live_binding_uses_serial_bdf_and_driver(self):
        raw=read(ROOT/'experiments/evidence/metax-hardware-baseline/1.0.0/metax/result.json')['inventory']
        hardware=read(ROOT/'recipes/hardware/metax-qwen-smoke-gpu0.yaml')
        dep=read(ROOT/'recipes/deployments/qwen3-06b/metax/vllm/qwen-metax-vllm-attached.yaml')
        commands=raw['commands']
        with patch('benchmark.load.adapters.metax.subprocess.run',side_effect=[SimpleNamespace(**{k:commands[n][k] for k in ('returncode','stdout','stderr')}) for n in ('gpu','hwinfo')]):
            probe=metax.inventory()
        self.assertEqual('observed',probe['status'])
        self.assertEqual([],metax.binding_issues(probe,dep['devices'],hardware))
        probe['devices']['0']['board_serial']='different-board'
        self.assertTrue(metax.binding_issues(probe,dep['devices'],hardware))

    def test_transformers_five_chat_encoding_counts_ids_not_fields(self):
        class Tokenizer:
            def apply_chat_template(self, *args, **kwargs):
                return {'input_ids':[151644,872,198,23268], 'attention_mask':[1,1,1,1]}
        self.assertEqual(4,token_count(Tokenizer(),'apple'))

    def test_new_driver_missing_reservation_is_unknown(self):
        raw=read(ROOT/'experiments/evidence/metax-four-node-inventory/1.0.0/metax-60/result.json')['inventory']
        parsed=parse(raw)
        self.assertEqual(8,len(parsed['devices']))
        self.assertTrue(all(d['observed']['driver_reserved_bytes'] is None for d in parsed['devices']))
        self.assertEqual('occupied',parsed['discovery']['availability'])

    def test_dense_unquantized_model_and_single_file_checkpoint(self):
        catalog=Catalog();catalog.load()
        doc=catalog.get(dict(id='metax-qwen3-06b',version='1.0.0'))
        self.assertIsNone(doc['architecture']['moe'])
        self.assertIsNone(doc['precision']['quantization'])
        self.assertIsNone(doc['checkpoint']['index'])
        self.assertEqual([],catalog.structural_errors(doc))
        self.assertEqual([],catalog.semantic_errors(doc))
        broken=copy.deepcopy(doc);broken['architecture']['type']='moe'
        self.assertIn('MoE architecture requires', '\n'.join(catalog.semantic_errors(broken)))

    def test_all_new_model_source_closures(self):
        catalog=Catalog();catalog.load()
        for name in ('metax-qwen3-06b','cluster-qwen3-06b','cluster-glm53-flash-w8a8','cluster-glm53-w4a8','cluster-glm53-w8a8'):
            for doc in catalog.closure(catalog.get(dict(id=name,version='1.0.0'))):
                self.assertEqual([],catalog.structural_errors(doc))
                self.assertEqual([],catalog.semantic_errors(doc,verify_sources=True))

    def test_vllm_requires_observed_config(self):
        dep=read(ROOT/'recipes/deployments/qwen3-06b/metax/vllm/qwen-metax-vllm-attached.yaml')
        self.assertIs(vllm,for_runtime(dict(engine='vllm-metax')))
        self.assertTrue(vllm.verify_server(dep,None,1024))
        info={'vllm_config':{'parallel_config':{'tensor_parallel_size':1,'pipeline_parallel_size':1,'data_parallel_size':1,'enable_expert_parallel':False},
                            'cache_config':{'enable_prefix_caching':False},'scheduler_config':{'max_num_seqs':4,'stream_interval':1},'model_config':{'max_model_len':12288}}}
        self.assertEqual([],vllm.verify_server(dep,info,8192+32))
        info['vllm_config']['cache_config']['enable_prefix_caching']=True
        self.assertTrue(vllm.verify_server(dep,info,8192+32))
        with self.assertRaises(SpecError):vllm.verify_server(dep,info,65536)
        dep['serving']['management']='sglang'
        self.assertTrue(vllm.configuration_issues(dep,dict(launch_parameters={})))


if __name__=='__main__':unittest.main()
