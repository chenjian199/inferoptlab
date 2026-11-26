"""Synthetic checkpoint evidence only; no real GPU measurements."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.common.io import file_hash, json_write
from benchmark.load import checkpoint
from tools.specs import SpecError, write


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.snapshot = dict(content_sha256='a'*64, trials=[dict(id='same-trial', repetition=i) for i in (1, 2)])
        write(self.root/'resolved.yaml', self.snapshot)
        run = self.root/'run-one'
        raw = run/'raw/aiperf/profile_export.jsonl'
        raw.parent.mkdir(parents=True)
        raw.write_text('synthetic raw evidence\n')
        json_write(run/'run.json', dict(trial_id='same-trial', repetition=1, status='completed',
                   plan_sha256='a'*64, environment_issues=[],
                   dataset_manifest=dict(files={'requests.jsonl': dict(count=4)})))
        json_write(run/'summary.json', dict(validity='valid', raw_sha256=file_hash(raw),
                   counts=dict(planned=4, succeeded=4, failed=0, missing=0)))
        self.state = dict(id='batch-one', status='completed_with_errors', plan_sha256='a'*64,
                         created_at='2026-11-25T00:00:00+00:00', runs=[
                             dict(trial_id='same-trial', repetition=1, status='completed', directory='run-one'),
                             dict(trial_id='same-trial', repetition=2, status='failed', directory='run-two')])
        json_write(self.root/'batch.json', self.state)

    def test_repetitions_are_distinct_and_completed_evidence_is_preserved(self):
        before = (self.root/'run-one/run.json').read_bytes()
        state = checkpoint.reopen(self.root, checkpoint.load(self.root, self.snapshot))
        self.assertEqual(state['runs'][0]['status'], 'completed')
        self.assertEqual(checkpoint.begin(state['runs'][1]), 2)
        self.assertEqual(state['runs'][1]['attempts'][0]['directory'], 'run-two')
        self.assertEqual((self.root/'run-one/run.json').read_bytes(), before)
        self.assertEqual(len(list((self.root/'checkpoints').glob('*.json'))), 1)
        self.assertEqual(self.state['runs'][1]['status'], 'failed')

    def test_changed_output_or_matrix_cannot_resume(self):
        changed = copy.deepcopy(self.snapshot)
        changed['trials'][0]['output_tokens'] = 50
        with self.assertRaisesRegex(SpecError, 'exact archived snapshot'):
            checkpoint.load(self.root, changed)

    def test_tampered_completed_raw_is_rejected(self):
        (self.root/'run-one/raw/aiperf/profile_export.jsonl').write_text('changed')
        with self.assertRaisesRegex(SpecError, 'inconsistent'):
            checkpoint.load(self.root, self.snapshot)

    def test_duplicate_repetition_is_rejected(self):
        self.state['runs'][1]['repetition'] = 1
        json_write(self.root/'batch.json', self.state)
        with self.assertRaisesRegex(SpecError, 'duplicate'):
            checkpoint.load(self.root, self.snapshot)

    def test_invalid_summary_cannot_be_skipped(self):
        path = self.root/'run-one/summary.json'
        value = json.loads(path.read_text())
        value['counts'].update(succeeded=3, failed=1)
        json_write(path, value)
        with self.assertRaisesRegex(SpecError, 'inconsistent'):
            checkpoint.load(self.root, self.snapshot)

    def directive(self, repetition=2):
        json_write(self.root/'exclusions.json', dict(plan_sha256='a'*64,
                   requested_by='user', requested_at='2026-11-25T14:00:00Z',
                   reason='Skip this failing configuration; continue others.',
                   trials=[dict(trial_id='same-trial', repetition=repetition)]))

    def test_explicit_skip_preserves_failed_evidence_and_completed_rows(self):
        self.directive()
        state = checkpoint.reopen(self.root, checkpoint.load(self.root, self.snapshot))
        checkpoint.apply_exclusions(self.root, state, self.snapshot)
        self.assertEqual(state['runs'][0], self.state['runs'][0])
        self.assertEqual(state['runs'][1]['status'], 'skipped_by_user')
        self.assertEqual(state['runs'][1]['status_before_exclusion'], 'failed')
        self.assertEqual(state['runs'][1]['directory'], 'run-two')
        json_write(self.root/'batch.json', state)
        self.assertEqual(checkpoint.load(self.root, self.snapshot), state)
        (self.root/'exclusions.json').unlink()
        with self.assertRaisesRegex(SpecError, 'no matching exclusion'):
            checkpoint.load(self.root, self.snapshot)

    def test_completed_evidence_cannot_be_excluded(self):
        self.directive(repetition=1)
        with self.assertRaisesRegex(SpecError, 'cannot exclude completed'):
            checkpoint.load(self.root, self.snapshot)

    def test_unknown_exclusion_is_rejected(self):
        self.directive(repetition=3)
        with self.assertRaisesRegex(SpecError, 'unknown or duplicate'):
            checkpoint.load(self.root, self.snapshot)


if __name__ == '__main__':
    unittest.main()
