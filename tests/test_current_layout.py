"""Current paths and entrypoints fail explicitly; no legacy path resolution."""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from benchmark.common.io import file_hash, inside
from tools.hardware.model import inspect_model
from tools.specs import ROOT, SpecError, read


class CurrentLayoutTests(unittest.TestCase):
    def test_missing_paths_are_not_redirected(self):
        old = ROOT/'schemas/recipes/models/metax-glm-5.3-flash-w8a8.yaml'
        self.assertEqual(old.resolve(), inside(ROOT, str(old)))
        with self.assertRaises(SpecError):read(old)
        with self.assertRaises(FileNotFoundError):file_hash(old)
        with self.assertRaises(SpecError):inside(ROOT, '../outside')

    def test_model_probe_archive_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'model.json'
            completed = subprocess.CompletedProcess([], 0, b'{"model_path":"/model with spaces"}', b'')
            with patch('tools.hardware.model.subprocess.run', return_value=completed) as remote:
                inspect_model('metax', '/model with spaces', target)
                argv = remote.call_args.args[0]
                self.assertEqual("python3 - model '/model with spaces'", argv[-1])
                self.assertIn('BatchMode=yes', argv)
                self.assertEqual(hashlib.sha256(target.with_suffix('.probe.py').read_bytes()).hexdigest(), read(target)['probe_sha256'])
                with self.assertRaises(SpecError):inspect_model('metax', '/model', target)
                self.assertEqual(1, remote.call_count)

    def test_invalid_model_probe_target_never_connects(self):
        with patch('tools.hardware.model.subprocess.run') as remote:
            for host, model in [('-oProxyCommand=bad', '/model'), ('metax', 'relative/model')]:
                with self.assertRaises(SpecError):inspect_model(host, model, Path('unused.json'))
            remote.assert_not_called()
