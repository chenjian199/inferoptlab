"""Cross-source regression tests: dated snapshots, aliases, provenance and staleness."""
import json
import subprocess
import sys
from pathlib import Path

import test_search

BUILDER = Path(__file__).with_name("build_knowledge.py")


class UnifiedSearchCLI(test_search.SearchCLI):
    # Inherit the original PDF tests and exercise them with ecosystem data present.
    def setUp(self):
        super().setUp()
        (self.root / "tools").mkdir()
        config = {"components": [
            {"id": "mcpytorch", "name": "mcPyTorch", "aliases": ["PyTorch", "maca-pytorch"],
             "images": ["maca-pytorch"], "packages": ["Pytorch"], "topics": ["communication"],
             "documents": ["demo-v01"]},
            {"id": "mctriton", "name": "mcTriton", "aliases": ["mcTriton"], "topics": ["communication"],
             "documents": ["demo-v01"]}],
             "extra_topics": [], "group_topics": {}, "category_topics": {"AI": ["communication"]}}
        self.save(self.root / "tools/components.json", config)
        # Supply renderer metadata that the original minimal search fixture omits.
        manifest = json.loads((self.root / "generated/manifest.json").read_text(encoding="utf-8"))
        manifest["documents"][0].update(title="示例", document_revision="V01", navigation_path="generated/demo.md")
        self.save(self.root / "generated/manifest.json", manifest)
        for day, version in [("2026-10-01", "old"), ("2026-11-21", "new")]:
            folder = self.root / "ecosystem" / day
            folder.mkdir(parents=True)
            self.save(folder / "coverage.json", {"observed_on": day, "limitations": ["sample only"]})
            self.save(folder / "images.json", {"observed_on": day, "families": [
                {"family": "maca-pytorch", "category": "AI", "source_url": "https://example.com/images",
                 "verification": "public_listing_observed_not_downloaded_or_run",
                 "representative": {"image_name_and_tag": "maca-pytorch:" + version, "recommended_driver": "3.100.0"},
                 "ubuntu22_amd64_example": {"image_name_and_tag": "maca-pytorch:ubuntu22"}},
                {"family": "triton-inference-server", "category": "AI", "source_url": "https://example.com/images",
                 "verification": "not_run", "representative": {"image_name_and_tag": "triton-inference-server:1"}}]})
            self.save(folder / "software_packages.json", {"observed_on": day, "entries": [
                {"name": "Pytorch", "category": "AI", "group": "训练框架", "source_url": "https://example.com/packages",
                 "verification": "directory_entry_observed"}]})
            (folder / "README.md").write_text("# 测试盘点\n\n## SDK 前置\nSDK 最低驱动 >= 3.7.0；不是推荐驱动。\n", encoding="utf-8")
        self.build()

    def save(self, path, data):
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def build(self, *args, expected=0):
        result = subprocess.run([sys.executable, "-B", str(BUILDER), "--root", str(self.root), *args],
                                capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stderr)

    def test_latest_and_historical_dates(self):
        result = self.run_cli("maca-pytorch", "--source", "ecosystem")
        self.assertEqual(result["snapshot_dates"], ["2026-11-21"])
        self.assertTrue(all(r["snapshot_date"] == "2026-11-21" for r in result["results"]))
        old = self.run_cli("maca-pytorch:old", "--snapshot", "2026-10-01")
        self.assertEqual(old["total_matches"], 1)
        self.assertEqual(self.run_cli("maca-pytorch", "--snapshot", "all")["total_matches"], 4)
        self.run_cli("maca-pytorch", "--snapshot", "2026-01-01", expected=2)

    def test_component_alias_and_pdf_cross_reference(self):
        result = self.run_cli("--component", "PyTorch", "--limit", "30")
        self.assertEqual(result["component"], "mcpytorch")
        self.assertEqual(result["matches_by_source"], {"pdf": 3, "ecosystem": 2, "github": 0, "practice": 0})
        rows = self.run_cli("mcPyTorch", "--source", "ecosystem")["results"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r["alias_matches"] for r in rows))

    def test_triton_names_do_not_merge(self):
        self.assertEqual(self.run_cli("--component", "mcTriton", "--source", "ecosystem")["total_matches"], 0)
        result = self.run_cli("--component", "triton-inference-server")
        self.assertEqual(result["matches_by_source"], {"pdf": 0, "ecosystem": 1, "github": 0, "practice": 0})

    def test_prose_and_provenance(self):
        result = self.run_cli("最低驱动", "--source", "ecosystem", "--full")
        row = result["results"][0]
        self.assertEqual(row["record_kind"], "report")
        self.assertEqual(row["source_line"], 3)
        self.assertIn("3.7.0", row["text"])
        rows = self.run_cli("maca-pytorch:new", "--source", "ecosystem")["results"]
        self.assertEqual(rows[0]["json_pointer"], "/families/0")
        self.assertEqual(rows[0]["data"]["representative"]["recommended_driver"], "3.100.0")
        self.assertNotIn("recommended_driver", rows[0]["data"]["ubuntu22_amd64_example"])

    def test_invalid_source_filter_combinations(self):
        self.run_cli("alpha", "--source", "ecosystem", "--doc", "demo", expected=2)
        self.run_cli("alpha", "--source", "pdf", "--snapshot", "all", expected=2)
        self.run_cli("alpha", "--body-only", "--snapshot", "all", expected=2)
        self.run_cli("--component", "unknown", expected=2)

    def test_snapshot_edits_and_added_files_require_rebuild(self):
        path = self.root / "ecosystem/2026-11-21/README.md"
        path.write_text("changed", encoding="utf-8")
        self.assertIn("Knowledge sources changed", self.run_cli("alpha", expected=2))
        self.assertEqual(self.run_cli("alpha", "--source", "pdf")["total_matches"], 1)
        self.build("--check", expected=2)
        self.build()
        self.build("--check")
        (path.parent / "new.md").write_text("new", encoding="utf-8")
        self.run_cli("maca", expected=2)

    def test_ecosystem_search_independent_of_pdf_hash(self):
        (self.root / "示例.pdf").write_bytes(b"changed")
        self.assertGreater(self.run_cli("maca-pytorch", "--source", "ecosystem")["total_matches"], 0)
        self.run_cli("alpha", "--source", "pdf", expected=2)

    def test_check_detects_generated_corruption(self):
        self.build("--check")
        (self.root / "COMPONENTS.md").write_text("corrupt", encoding="utf-8")
        self.build("--check", expected=2)

    def add_github(self, day):
        import hashlib
        folder = self.root / "repositories" / day
        (folder / "readmes").mkdir(parents=True)
        readme = folder / "readmes/mcPytorch.txt"
        readme.write_text("# GPU_DOC_TEST\nSource constraints only; not server verified.\n", encoding="utf-8")
        self.save(folder / "coverage.json", {"observed_on": day})
        (folder / "README.md").write_text("# GitHub snapshot", encoding="utf-8")
        self.save(folder / "repositories.json", {"observed_on": day, "repositories": [
            {"name": "mcPytorch", "source_url": "https://github.com/example/mcPytorch", "topics": ["communication"],
             "default_branch": "2.4", "readme": {"status": "downloaded", "path": "readmes/mcPytorch.txt",
                "sha256": hashlib.sha256(readme.read_bytes()).hexdigest(), "branch": "2.4", "commit": "a" * 40,
                "source_url": "https://raw.githubusercontent.com/example/mcPytorch/" + "a" * 40 + "/README.md"}}]})
        path = self.root / "tools/components.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["repository_bindings"] = {"mcPytorch": "mcpytorch"}
        self.save(path, config)

    def test_github_source_and_component_navigation(self):
        self.add_github("2026-10-20")
        self.build()
        result = self.run_cli("--component", "mcpytorch", "--source", "github")
        self.assertEqual(result["matches_by_source"], {"pdf": 0, "ecosystem": 0, "github": 2, "practice": 0})
        self.assertTrue(all(r["source_type"] == "github" for r in result["results"]))
        row = self.run_cli("GPU_DOC_TEST", "--source", "github", "--full")["results"][0]
        self.assertEqual(row["commit"], "a" * 40)
        self.assertEqual(row["source_line"], 1)
        self.assertEqual(row["record_kind"], "repository_readme")
        self.assertIn("Source constraints", row["text"])
        self.assertEqual(self.run_cli("GPU_DOC_TEST", "--source", "ecosystem")["total_matches"], 0)

    def test_latest_selected_independently_per_source(self):
        self.add_github("2026-10-12")
        self.add_github("2026-10-20")
        self.build()
        result = self.run_cli("--component", "mcpytorch", "--limit", "100")
        self.assertEqual(result["snapshots_by_source"], {"ecosystem": ["2026-11-21"], "github": ["2026-10-20"]})
        self.assertEqual(result["matches_by_source"], {"pdf": 3, "ecosystem": 2, "github": 2, "practice": 0})
        result = self.run_cli("--component", "mcpytorch", "--snapshot", "all", "--source", "github")
        self.assertEqual(result["total_matches"], 4)
        self.assertEqual(self.run_cli("--list")["snapshots_by_source"]["github"], ["2026-10-12", "2026-10-20"])

    def test_github_invalid_filters_and_hash_isolation(self):
        self.add_github("2026-10-20")
        self.build()
        self.run_cli("mcpytorch", "--source", "github", "--doc", "demo", expected=2)
        self.run_cli("mcpytorch", "--source", "github", "--snapshot", "2026-11-21", expected=2)
        (self.root / "示例.pdf").write_bytes(b"changed PDF")
        self.assertEqual(self.run_cli("GPU_DOC_TEST", "--source", "github")["total_matches"], 1)

    def test_github_readme_change_rejected(self):
        self.add_github("2026-10-20")
        self.build()
        (self.root / "repositories/2026-10-20/readmes/mcPytorch.txt").write_text("changed", encoding="utf-8")
        self.assertIn("Knowledge sources changed", self.run_cli("mcpytorch", "--source", "github", expected=2))
        self.build("--check", expected=2)

    def test_unknown_repository_binding_rejected(self):
        self.add_github("2026-10-20")
        path = self.root / "tools/components.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["repository_bindings"]["mcPytorch"] = "unknown"
        self.save(path, config)
        self.build(expected=2)
