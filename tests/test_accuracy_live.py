from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from benchmark.accuracy.code_adapter import assemble
from benchmark.accuracy.live import comparison_issues, evaluate
from benchmark.accuracy import sandbox
from tools.specs import Catalog, SpecError


class LiveAccuracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c = Catalog(); c.load()
        cls.deps = [c.get({'id': i, 'version': '1.0.0'}) for i in [
            'glm53-vllm-decode-reference-tp8', 'glm53-vllm-decode-tp4-dp2-ep8', 'glm53-vllm-decode-tp2-dp4-ep8']]

    def test_only_declared_parallelism_changes_allowed(self):
        self.assertEqual(comparison_issues(self.deps), [])
        changed = deepcopy(self.deps)
        changed[1]['backend_options']['--enforce-eager'] = False
        self.assertTrue(comparison_issues(changed))
        changed = deepcopy(self.deps)
        changed[1]['scheduling']['max_running_requests'] = 128
        self.assertTrue(comparison_issues(changed))

    def test_extractor_keeps_indentation_and_rejects_repair(self):
        prompt = 'def f(x):\n    """Example."""\n'
        code, mode = assemble(prompt, '    return x + 1', 'f')
        self.assertIn('    return x + 1', code)
        self.assertEqual(mode, 'continuation')
        with self.assertRaises(SyntaxError):
            assemble(prompt, 'return x + 1', 'f')
        with self.assertRaises(ValueError):
            assemble(prompt, '<think>unfinished', 'f')

    def test_scoring_infrastructure_failure_is_not_model_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sandbox, 'score', return_value=dict(task_id='test', result='infrastructure_error', passed=False, truncated=False)):
                with self.assertRaises(SpecError):
                    evaluate(Path(directory), [dict(task_id='test')], {'test': {}}, 'unused')
            summary = json.loads((Path(directory) / 'score_summary.json').read_text())
            self.assertEqual(summary['status'], 'incomplete')
            self.assertIsNone(summary['pass_at_1'])

    def test_canonical_failure_blocks_candidate_scoring(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(sandbox, 'score', return_value=dict(task_id='test', result='test_failure', passed=False, truncated=False)):
                with self.assertRaises(SpecError):
                    evaluate(Path(directory), [dict(task_id='test')], {'test': {}}, 'unused', canonical=True)


if __name__ == '__main__':
    unittest.main()
