import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch


path = Path(__file__).resolve().parents[1] / 'tools/deployment/metax-vllm/preflight.py'
spec = importlib.util.spec_from_file_location('decode_preflight', path)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class PreflightTests(unittest.TestCase):
    def test_concatenated_rank_records_are_complete(self):
        log = '[info] ready\n' + ''.join(json.dumps(dict(rank=i, status='passed')) for i in range(8))
        self.assertEqual({r['rank'] for r in preflight.rank_records(log)}, set(range(8)))

    def test_hardware_failure_restores_exact_original_with_model_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'experiments').mkdir()
            info = dict(Id='original-id', Image='sha256:' + 'a' * 64,
                        Config=dict(Labels={'io.inferoptlab.task': 'owned'},
                                    Cmd=['--port', '18081', '--served-model-name', 'glm53-flash']),
                        State=dict(Running=True, StartedAt='timestamp'))
            args = ['preflight', '--plan', 'plan.yaml', '--baseline', 'baseline.yaml',
                    '--accuracy-plan', 'quality.yaml', '--prompts', 'prompts.jsonl', '--scoring', 'scoring.jsonl',
                    '--out', str(root / 'experiments/test'), '--sandbox-image', info['Image'],
                    '--suspend-container', 'original', '--expected-task-label', 'owned']
            commands = []
            def docker(*argv):
                commands.append(argv)
                return SimpleNamespace(stdout=json.dumps([info]))
            response = MagicMock()
            response.__enter__.return_value.read.return_value = b'vllm:num_requests_running 0\nvllm:num_requests_waiting 0\n'
            with patch.object(preflight, 'ROOT', root), patch.object(preflight, 'Catalog'), \
                 patch.object(preflight, 'load_snapshot', return_value={'execution_issues': []}), \
                 patch.object(preflight, 'docker', side_effect=docker), \
                 patch.object(preflight, 'urlopen', return_value=response), \
                 patch.object(preflight, 'hardware_sanity', side_effect=ValueError('synthetic failure')), \
                 patch.object(preflight, 'wait_ready') as ready, patch.object(preflight.signal, 'signal'), \
                 patch('sys.argv', args):
                with self.assertRaisesRegex(ValueError, 'synthetic failure'):
                    preflight.main()
            self.assertIn(('stop', '--time', '20', 'original-id'), commands)
            self.assertIn(('start', 'original-id'), commands)
            self.assertEqual(ready.call_args.args[0], {'url': 'http://127.0.0.1:18081', 'served_model': 'glm53-flash'})
            state = json.loads((root / 'experiments/test/state.json').read_text())
            self.assertTrue(state['original_restored'])
            self.assertFalse(state['performance_scan_started'])


if __name__ == '__main__':
    unittest.main()
