import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

from tools.hardware.probes.checkpoint_payload import fingerprint


class CheckpointFingerprintTests(unittest.TestCase):
    def fixture(self, root, offsets=(0, 4)):
        header = json.dumps({'weight': {'dtype': 'I8', 'shape': [4],
                                       'data_offsets': list(offsets)}}).encode()
        payload = struct.pack('<Q', len(header)) + header + b'\x00\x01\x02\x03'
        (root / 'weights.safetensors').write_bytes(payload)
        (root / 'model.safetensors.index.json').write_text(json.dumps(
            {'weight_map': {'weight': 'weights.safetensors'}}), encoding='utf-8')
        return payload

    def test_all_bytes_hashed_and_payload_change_changes_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self.fixture(root)
            before = fingerprint(root)
            self.assertEqual(before['shards'][0]['sha256'], hashlib.sha256(payload).hexdigest())
            self.assertFalse(before['upstream_authenticity_verified'])
            (root / 'weights.safetensors').write_bytes(payload[:-1] + b'\x04')
            after = fingerprint(root)
            self.assertNotEqual(before['weights_sha256'], after['weights_sha256'])
            self.assertEqual(before['shards'][0]['header_sha256'], after['shards'][0]['header_sha256'])

    def test_index_header_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / 'model.safetensors.index.json').write_text(json.dumps(
                {'weight_map': {'wrong': 'weights.safetensors'}}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'map mismatch'):
                fingerprint(root)

    def test_unaccounted_payload_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, (0, 3))
            with self.assertRaisesRegex(ValueError, 'unaccounted'):
                fingerprint(root)

    def test_mutation_after_first_read_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = self.fixture(root)
            def mutate(_):
                (root / 'weights.safetensors').write_bytes(payload + b'changed')
            with self.assertRaisesRegex(ValueError, 'changed during'):
                fingerprint(root, mutate)


if __name__ == '__main__':
    unittest.main()
