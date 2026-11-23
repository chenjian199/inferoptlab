import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools.specs import Catalog, ROOT, digest, read
from tools.probes.metax_inventory import model
from tools.probes.c500_calibrate import active_gpu_pids


class InspectedRecipesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog()
        cls.catalog.load()

    def recipe(self, name):
        return copy.deepcopy(self.catalog.get({'id': name, 'version': '1.0.0'}))

    def test_actual_recipe_closures_and_source_bytes(self):
        for name in ('metax-c500-8gpu', 'metax-glm-5.3-flash-w8a8',
                     'metax-deepseek-v4-flash-w8a8-mtp', 'metax-deepseek-v4.1-flash-w8a8',
                     'metax-vllm-glm53-observed', 'metax-c500-gpu0-20261123'):
            for document in self.catalog.closure(self.recipe(name)):
                self.assertEqual([], self.catalog.structural_errors(document))
                self.assertEqual([], self.catalog.semantic_errors(document, verify_sources=True))

    def test_model_recipe_matches_collected_metadata(self):
        for name in ('metax-glm-5.3-flash-w8a8', 'metax-deepseek-v4-flash-w8a8-mtp',
                     'metax-deepseek-v4.1-flash-w8a8'):
            doc = self.recipe(name)
            source = self.catalog.get(doc['provenance'][0]['source_ref'])
            raw = json.loads((ROOT / source['path']).read_text(encoding='utf-8'))
            config = raw['files']['config.json']['content']
            text = config.get('text_config', config)
            self.assertEqual(text['num_hidden_layers'], doc['architecture']['text']['num_hidden_layers'])
            self.assertEqual(digest(raw['weights']['shards']), doc['checkpoint']['manifest_sha256'])
            self.assertEqual(sum(s['size_bytes'] for s in raw['weights']['shards']), doc['checkpoint']['total_file_bytes'])
            self.assertEqual(raw['files']['tokenizer.json']['sha256'], doc['tokenizer']['sha256'])
            self.assertEqual(raw['weights']['scale_tensor_dtypes'], doc['precision']['quantization']['scale_dtypes'])

    def test_moe_and_hybrid_layout_errors(self):
        doc = self.recipe('metax-glm-5.3-flash-w8a8')
        doc['architecture']['moe']['experts_per_token'] = 999
        doc['architecture']['linear_attention']['layers'].append(3)
        errors = '\n'.join(self.catalog.semantic_errors(doc))
        self.assertIn('experts_per_token', errors)
        self.assertIn('linear attention layer IDs', errors)

    def test_inspected_cannot_drop_required_details(self):
        doc = self.recipe('metax-glm-5.3-flash-w8a8')
        del doc['checkpoint']
        self.assertTrue(self.catalog.structural_errors(doc))
        doc = self.recipe('metax-c500-8gpu')
        del doc['resources']['nodes'][0]['devices'][0]['observed']
        self.assertTrue(self.catalog.structural_errors(doc))

    def test_hardware_memory_units_and_device_uniqueness(self):
        doc = self.recipe('metax-c500-8gpu')
        node = doc['resources']['nodes'][0]
        node['dram_gb'] = doc['discovery']['dram_bytes'] / 1024**3
        node['devices'][1]['observed']['pci_bus_id'] = node['devices'][0]['observed']['pci_bus_id']
        errors = '\n'.join(self.catalog.semantic_errors(doc))
        self.assertIn('decimal GB', errors)
        self.assertIn('duplicate observed device pci_bus_id', errors)

    def test_measured_values_recompute_from_samples(self):
        doc = self.recipe('metax-c500-gpu0-20261123')
        self.assertEqual([], self.catalog.semantic_errors(doc))
        doc['measurements'][0]['value'] *= 8
        self.assertIn('raw timing', '\n'.join(self.catalog.semantic_errors(doc)))
        doc = self.recipe('metax-c500-gpu0-20261123')
        doc['measurements'][-1]['unit'] = 'TFLOPS'
        self.assertIn('GB/s', '\n'.join(self.catalog.semantic_errors(doc)))

    def test_inspection_never_implies_freeze_or_conversion(self):
        model_doc = self.recipe('metax-deepseek-v4-flash-w8a8-mtp')
        model_doc['issues'] = []
        errors = '\n'.join(self.catalog.readiness_issues([model_doc]))
        self.assertIn('payload integrity', errors)
        self.assertIn('loader compatibility', errors)
        model_doc['checkpoint']['compatibility']['status'] = 'observed_loaded'
        self.assertIn('Ascend', '\n'.join(self.catalog.semantic_errors(model_doc)))
        hardware = self.recipe('metax-c500-8gpu')
        hardware['issues'] = []
        self.assertIn('hardware health', '\n'.join(self.catalog.readiness_issues([hardware])))

    def test_executed_probe_artifact_is_exact(self):
        root = ROOT / 'schemas/evidence/metax/20261123'
        raw = json.loads((root / 'calibration-v3.json').read_text(encoding='utf-8'))
        self.assertEqual(raw['probe_sha256'], hashlib.sha256((root / 'calibration-v3.probe.py').read_bytes()).hexdigest())
        self.assertEqual('measured', raw['status'])
        self.assertEqual([], active_gpu_pids(raw['gpu_before']))
        self.assertEqual([], active_gpu_pids(raw['gpu_after']))


class ProbeTests(unittest.TestCase):
    def test_process_probe_fails_closed(self):
        with self.assertRaises(RuntimeError):
            active_gpu_pids('mx-smi failed')
        with self.assertRaises(RuntimeError):
            active_gpu_pids('Attached GPUs : 8\nProcess:\nEnd of Log')
        self.assertEqual(['123'], active_gpu_pids('Attached GPUs : 8\nProcess:\n| 0 123 VLLM::Worker 4096 |\nEnd of Log'))

    def test_vendor_index_is_used_instead_of_all_directory_weights(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            header = json.dumps({'layers.0.weight': {'dtype': 'I8', 'shape': [4], 'data_offsets': [0, 4]}}).encode()
            shard = struct.pack('<Q', len(header)) + header + b'\x01\x02\x03\x04'
            (root / 'weight.safetensors').write_bytes(shard)
            (root / 'unrelated.safetensors').write_bytes(shard)
            (root / 'quant_model_weights.safetensors.index.json').write_text(json.dumps({'weight_map': {'layers.0.weight': 'weight.safetensors'}}), encoding='utf-8')
            result = model(tmp)
            self.assertEqual([], result['errors'])
            self.assertTrue(result['weights']['index_matches_headers'])
            self.assertEqual(['unrelated.safetensors'], result['weights']['unindexed_safetensors'])
            self.assertEqual(1, len(result['weights']['shards']))
            (root / 'weight.safetensors').unlink()
            result = model(tmp)
            self.assertIn('missing shard: weight.safetensors', result['errors'])
            self.assertFalse(result['weights']['index_matches_headers'])


if __name__ == '__main__':
    unittest.main()
