"""Stage-four evidence integrity and truthful planning boundaries."""
import copy
from pathlib import Path
import tempfile
import unittest

from diagnosis.contracts import finish, validate
from optimization.cli import main
from optimization.handoff import prepare
from tools.specs import Catalog, ROOT, SpecError, read, write


class OptimizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = Catalog()
        cls.catalog.load()
        cls.source = ROOT / "experiments/runs/analysis/qwen-metax-v2/analysis.yaml"

    def test_qwen_evidence_gaps_do_not_become_executable_tasks(self):
        result = prepare(self.catalog, self.source)
        validate(self.catalog, result)
        self.assertEqual(7, sum(t["status"] == "awaiting_evidence" for t in result["tasks"]))
        self.assertEqual(4, sum(t["status"] == "not_applicable" for t in result["tasks"]))
        self.assertTrue(all(t["candidate"] is None and t["acceptance"] is None
                            and t["optimization_task"] is None for t in result["tasks"]))
        source = read(self.source)
        self.assertEqual(source["preflight_issues"], result["preflight_issues"])
        self.assertEqual(source["tasks"][0]["scope"], result["tasks"][0]["scope"])

    def test_glm_remains_without_baseline(self):
        result = prepare(self.catalog, ROOT / "experiments/runs/analysis/glm53-w8a8-v1/analysis.yaml")
        self.assertTrue(all(t["status"] == "awaiting_baseline" for t in result["tasks"]))
        self.assertTrue(any("exceed" in item for item in result["preflight_issues"]))

    def test_rehashed_analysis_change_is_not_trusted(self):
        source = read(self.source)
        source["tasks"][0]["scope"]["baseline_run_ids"] = ["invented-baseline"]
        source = finish({k: v for k, v in source.items() if k != "content_sha256"})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "analysis.yaml"
            write(path, source)
            with self.assertRaisesRegex(SpecError, "reproducible plan"):
                prepare(self.catalog, path)

    def test_parent_fingerprint_change_is_rejected(self):
        source = read(self.source)
        source["diagnosis_artifact"]["sha256"] = "0" * 64
        source = finish({k: v for k, v in source.items() if k != "content_sha256"})
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "analysis.yaml"
            write(path, source)
            with self.assertRaisesRegex(SpecError, "diagnosis artifact has changed"):
                prepare(self.catalog, path)

    def test_schema_rejects_claimed_acceptance(self):
        result = prepare(self.catalog, self.source)
        result["tasks"][0]["acceptance"] = {"status": "accepted"}
        result = finish({k: v for k, v in result.items() if k != "content_sha256"})
        with self.assertRaises(SpecError):
            validate(self.catalog, result)

    def test_duplicate_handoff_task_is_rejected(self):
        result = prepare(self.catalog, self.source)
        result["tasks"].append(copy.deepcopy(result["tasks"][0]))
        result = finish({k: v for k, v in result.items() if k != "content_sha256"})
        with self.assertRaisesRegex(SpecError, "duplicate handoff"):
            validate(self.catalog, result)

    def test_cli_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "handoff"
            arguments = ["plan", str(self.source), "--out", str(output)]
            self.assertEqual(0, main(arguments))
            original = (output / "handoff.yaml").read_bytes()
            self.assertEqual(2, main(arguments))
            self.assertEqual(original, (output / "handoff.yaml").read_bytes())


if __name__ == "__main__":
    unittest.main()
