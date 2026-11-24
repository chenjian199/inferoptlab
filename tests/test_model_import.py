"""Model intake writes nested recipes and retains evidence and duplicate protection."""
import contextlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools import import_inspected_model as importer
from tools.specs import Catalog, ROOT, SpecError, read


class ModelImportTests(unittest.TestCase):
    def test_import_into_new_model_directory_and_refuse_duplicate(self):
        observation = ROOT/'experiments/evidence/model-intake/metax-qwen3-06b/1.0.0/metadata.json'
        catalog = Catalog()
        catalog.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            definitions = root/'schemas/definitions'
            definitions.mkdir(parents=True)
            shutil.copyfile(ROOT/'schemas/definitions/inspected.json', definitions/'inspected.json')
            argv = ['import_inspected_model', str(observation), '--id', 'test-qwen-intake',
                    '--family', 'qwen', '--model', 'qwen3-0.6b']
            with patch.object(importer, 'ROOT', root), patch.object(importer, 'Catalog', return_value=catalog), \
                    patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()):
                importer.main()
                output = root/'recipes/models/qwen/qwen3-0.6b/test-qwen-intake.yaml'
                model = read(output)
                self.assertEqual('test-qwen-intake', model['id'])
                self.assertEqual('Qwen3-0.6B', model['identity']['name'])
                self.assertEqual([], catalog.structural_errors(model))
                source = read(root/'recipes/sources/source-test-qwen-intake.yaml')
                archived = root/source['path']
                self.assertEqual(observation.read_bytes(), archived.read_bytes())
                self.assertEqual(observation.with_suffix('.probe.py').read_bytes(),
                                 archived.with_suffix('.probe.py').read_bytes())
                before = output.read_bytes()
                with self.assertRaisesRegex(SpecError, 'already exists'):
                    importer.main()
                self.assertEqual(before, output.read_bytes())

    def test_invalid_group_or_identity_cannot_escape_catalog(self):
        for family, model, identity in [('..', 'model', 'id'), ('glm', '../model', 'id'),
                                        ('glm', 'model', '../../id'), ('C:\\models', 'model', 'id'),
                                        ('glm', 'model/variant', 'id')]:
            with self.subTest(family=family, model=model, identity=identity):
                with self.assertRaises(SpecError):
                    importer.model_recipe_path(ROOT, family, model, identity)


if __name__ == '__main__':
    unittest.main()
