"""CLI regression checks with a tiny isolated synthetic index; original PDFs are untouched."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("search.py")


class SearchCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hwdoc-search-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "generated").mkdir()
        # The search tool never parses PDFs, only checks their hashes.
        source = self.root / "示例.pdf"
        source.write_bytes(b"synthetic source for hash validation")
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        manifest = {"topics": [{"id": "communication", "title": "通信"}],
                    "documents": [{"id": "demo-v01", "filename": source.name, "sha256": sha,
                                   "page_count": 3, "topics": ["communication"]}]}
        (self.root / "generated/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        rows = []
        for page, text in enumerate(["目录 环境变量 DMA-BUF", "环 境\n变 量 DMA‑BUF alpha", "beta"], 1):
            rows.append({"doc_id": "demo-v01", "source_pdf": source.name, "source_sha256": sha,
                         "pdf_page": page, "page_label": str(page - 1), "topics": ["communication"],
                         "front_matter": page == 1, "bookmarks_on_page": ["环境变量"] if page == 2 else [],
                         "section_hint": "示例", "text_path": f"generated/page-{page}.txt",
                         "quality_flags": [], "text": text})
        (self.root / "generated/pages.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    def run_cli(self, *args, expected=0):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--root", str(self.root), "--json", *args],
                                capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, expected, result.stderr)
        return json.loads(result.stdout) if expected == 0 else result.stderr

    def test_chinese_wraps_and_body_ranking(self):
        result = self.run_cli("环境变量")
        self.assertEqual(result["total_matches"], 2)
        self.assertEqual(result["results"][0]["pdf_page"], 2)
        self.assertIn("环 境", result["results"][0]["snippet"])

    def test_case_and_unicode_hyphen(self):
        result = self.run_cli("dma-buf", "--body-only")
        self.assertEqual([r["pdf_page"] for r in result["results"]], [2])

    def test_terms_must_match_same_page(self):
        self.assertEqual(self.run_cli("alpha", "beta")["total_matches"], 0)
        self.assertEqual(self.run_cli("alpha", "beta", "--any")["total_matches"], 2)

    def test_topic_and_document_filters(self):
        result = self.run_cli("alpha", "--topic", "communication", "--doc", "示例")
        self.assertEqual(result["total_matches"], 1)
        self.run_cli("alpha", "--topic", "missing", expected=2)
        self.run_cli("alpha", "--doc", "missing", expected=2)

    def test_physical_page_and_full_text(self):
        result = self.run_cli("--doc", "demo-v01", "--page", "2", "--full")
        self.assertEqual(result["total_matches"], 1)
        row = result["results"][0]
        self.assertEqual(row["page_label"], "1")
        self.assertEqual(row["text"], "环 境\n变 量 DMA‑BUF alpha")

    def test_invalid_arguments(self):
        self.run_cli("--page", "2", expected=2)
        self.run_cli("alpha", "--limit", "0", expected=2)
        self.run_cli(expected=2)

    def test_source_change_is_rejected(self):
        (self.root / "示例.pdf").write_bytes(b"changed")
        self.assertIn("PDFs changed", self.run_cli("alpha", expected=2))

    def test_added_or_removed_pdf_is_rejected(self):
        extra = self.root / "new.pdf"
        extra.write_bytes(b"new")
        self.assertIn("PDFs changed", self.run_cli("alpha", expected=2))
        extra.unlink()
        (self.root / "示例.pdf").unlink()
        self.assertIn("PDFs changed", self.run_cli("alpha", expected=2))

    def test_list(self):
        self.assertEqual(self.run_cli("--list")["documents"][0]["id"], "demo-v01")


if __name__ == "__main__":
    unittest.main()
