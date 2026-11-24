"""Practice search acceptance: retained history, attribution, evidence and isolation."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_knowledge
from verify_practice import secret_rules


class PracticeSearch(unittest.TestCase):
    # Reuse the synthetic fixture, without inheriting and duplicating its test suite.
    save = test_knowledge.UnifiedSearchCLI.save
    build = test_knowledge.UnifiedSearchCLI.build
    run_cli = test_knowledge.UnifiedSearchCLI.run_cli

    def setUp(self):
        fixture = test_knowledge.UnifiedSearchCLI()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root = fixture.root
        folder = self.root / "practice"
        folder.mkdir()
        (folder / "scope.json").write_text('{"scope":"single sequence only"}', encoding="utf-8")
        evidence = folder / "evidence.json"
        evidence.write_text('{"passed":true,"private_search_marker":"EVIDENCE_ONLY"}', encoding="utf-8")
        self.entries = []
        for day, name in [("2026-09-01", "old"), ("2026-11-22", "new")]:
            (folder / (name + ".md")).write_text("# Case\n\n## Repair\nPRACTICE_ONLY scale fix " + name + "\n\n## Unrelated\nNOT_THIS_SECTION\n", encoding="utf-8")
            self.entries.append({"id": name, "kind": "issue", "title": "Scale ownership repair",
                "path": "practice/" + name + ".md", "section": "## Repair", "observed_on": day,
                "components": ["mcpytorch", "mctriton"], "topics": ["communication"],
                "verification": "scoped_test_only", "applicability": "single sequence only",
                "coverage_path": "practice/scope.json", "evidence": [{"path": "practice/evidence.json",
                    "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest()}]})
        self.write_records()
        self.build()

    def write_records(self):
        self.save(self.root / "practice/records.json", {"schema_version": 1, "records": self.entries})

    def test_default_and_latest_retain_independent_old_cases(self):
        for args in [(), ("--snapshot", "latest"), ("--snapshot", "all")]:
            result = self.run_cli("PRACTICE_ONLY", *args)
            self.assertEqual(result["matches_by_source"]["practice"], 2)
            self.assertEqual(result["snapshots_by_source"]["practice"], ["2026-09-01", "2026-11-22"])
            self.assertEqual(result["snapshots_by_source"]["ecosystem"],
                             ["2026-10-01", "2026-11-21"] if args == ("--snapshot", "all") else ["2026-11-21"])
        result = self.run_cli("PRACTICE_ONLY", "--source", "practice", "--snapshot", "2026-09-01")
        self.assertEqual(result["total_matches"], 1)
        self.assertEqual(result["results"][0]["record_id"], "practice/old")
        self.run_cli("PRACTICE_ONLY", "--source", "practice", "--snapshot", "2026-10-01", expected=2)

    def test_secondary_component_scope_provenance_and_section(self):
        result = self.run_cli("--source", "practice", "--component", "mctriton", "--topic", "communication", "--full")
        self.assertEqual(result["total_matches"], 2)
        row = result["results"][0]
        self.assertEqual(row["source_line"], 3)
        self.assertEqual(row["verification"], "scoped_test_only")
        self.assertEqual(row["applicability"], "single sequence only")
        self.assertEqual(len(row["evidence"][0]["sha256"]), 64)
        self.assertNotIn("NOT_THIS_SECTION", row["text"])
        navigation = (self.root / "COMPONENTS.md").read_text(encoding="utf-8")
        self.assertIn("Scale ownership repair", navigation)

    def test_evidence_and_unlisted_markdown_not_fulltext_indexed(self):
        (self.root / "practice/unlisted.md").write_text("UNLISTED_MARKER", encoding="utf-8")
        self.build()
        for term in ["EVIDENCE_ONLY", "UNLISTED_MARKER", "NOT_THIS_SECTION"]:
            self.assertEqual(self.run_cli(term, "--source", "practice")["total_matches"], 0)

    def test_source_filters_and_pdf_independence(self):
        for source in ["pdf", "github", "ecosystem"]:
            self.assertEqual(self.run_cli("PRACTICE_ONLY", "--source", source)["total_matches"], 0)
        for flags in [("--doc", "demo"), ("--body-only",), ("--doc", "demo", "--page", "1")]:
            self.run_cli("scale", "--source", "practice", *flags, expected=2)
        (self.root / "示例.pdf").write_bytes(b"changed")
        self.assertEqual(self.run_cli("PRACTICE_ONLY", "--source", "practice")["total_matches"], 2)

    def test_source_change_and_evidence_corruption_rejected(self):
        (self.root / "practice/old.md").write_text("changed", encoding="utf-8")
        self.run_cli("scale", "--source", "practice", expected=2)
        self.build(expected=2)  # Required section disappeared.
        (self.root / "practice/old.md").write_text("## Repair\nchanged", encoding="utf-8")
        self.build()
        (self.root / "practice/evidence.json").write_text("{}", encoding="utf-8")
        self.run_cli("scale", "--source", "practice", expected=2)
        self.build(expected=2)  # A rebuild cannot silently bless corrupted evidence.

    def test_bad_metadata_and_paths_rejected(self):
        original = json.loads(json.dumps(self.entries))
        for field, value in [("components", ["unknown"]), ("topics", ["unknown"]),
                             ("observed_on", "not-a-date"), ("kind", "unknown"),
                             ("applicability", ""), ("evidence", []),
                             ("path", "tools/components.json")]:
            self.entries = json.loads(json.dumps(original))
            self.entries[0][field] = value
            self.write_records()
            self.build(expected=2)
        self.entries = original + [original[0]]
        self.write_records()
        self.build(expected=2)

    def test_readable_output_includes_scope_without_blanket_unverified_label(self):
        cmd = [sys.executable, "-B", str(Path(__file__).with_name("search.py")),
               "--root", str(self.root), "scale", "--source", "practice"]
        result = subprocess.run(cmd, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("适用范围", result.stdout)
        self.assertIn("SHA256", result.stdout)
        self.assertNotIn("；未在服务器验证。", result.stdout)


class SecretHeuristics(unittest.TestCase):
    def test_detects_synthetic_credentials_without_returning_values(self):
        for sample in ['{"api_key":"synthetic-secret-value"}',
                       'https://user:synthetic-value@example.invalid',
                       'https://example.invalid/sub?token=synthetic-value',
                       'Bearer synthetic-long-secret-value']:
            result = secret_rules(sample)
            self.assertTrue(result)
            self.assertNotIn("synthetic", " ".join(result))
        self.assertEqual(secret_rules('proxy_without_auth=407; controller_without_auth=401; SHA256 recorded'), [])
