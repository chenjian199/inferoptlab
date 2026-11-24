#!/usr/bin/env python3
"""Check source hashes, page coverage, generated text and bookmark destinations."""
import argparse
import json
import sys
from pathlib import Path

from search import ROOT, check_sources


def verify(root):
    manifest = json.loads((root / "generated/manifest.json").read_text(encoding="utf-8"))
    check_sources(root, manifest)
    docs = {d["id"]: d for d in manifest["documents"]}
    if len(docs) != manifest["document_count"]:
        raise ValueError("Duplicate document IDs or incorrect document count")
    seen = {key: set() for key in docs}
    count, characters = 0, 0
    marker = "--- 以下为未经语义改写的 PDF 提取文本 ---\n"
    with (root / "generated/pages.jsonl").open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            doc = docs[row["doc_id"]]
            page = row["pdf_page"]
            if page in seen[doc["id"]] or not 1 <= page <= doc["page_count"]:
                raise ValueError(f"Invalid or duplicate page: {doc['id']}:{page}")
            if row["source_sha256"] != doc["sha256"] or row["source_pdf"] != doc["filename"]:
                raise ValueError(f"Wrong source: {doc['id']}:{page}")
            contents = (root / row["text_path"]).read_text(encoding="utf-8")
            if contents.partition(marker)[2] != row["text"] or len(row["text"]) != row["char_count"]:
                raise ValueError(f"Page text mismatch: {doc['id']}:{page}")
            seen[doc["id"]].add(page)
            count += 1
            characters += row["char_count"]
    for doc in docs.values():
        if seen[doc["id"]] != set(range(1, doc["page_count"] + 1)):
            raise ValueError(f"Missing pages: {doc['id']}")
        outlines = json.loads((root / doc["outline_path"]).read_text(encoding="utf-8"))
        if len(outlines) != doc["outline_count"] or any(not 1 <= o["pdf_page"] <= doc["page_count"] for o in outlines):
            raise ValueError(f"Invalid bookmarks: {doc['id']}")
        if not (root / doc["navigation_path"]).is_file():
            raise ValueError(f"Missing navigation: {doc['id']}")
        for item in doc["applicability_evidence"] + doc["software_requirements_evidence"]:
            if item["pdf_page"] not in seen[doc["id"]] or not (root / item["text_path"]).is_file():
                raise ValueError(f"Invalid evidence: {doc['id']}")
    if count != manifest["page_count"] or count != sum(d["page_count"] for d in docs.values()):
        raise ValueError("Page total mismatch")
    quality = json.loads((root / "generated/quality.json").read_text(encoding="utf-8"))
    if quality["page_count"] != count or quality["document_count"] != len(docs):
        raise ValueError("Quality report totals mismatch")
    print(f"PASS: {len(docs)} PDFs unchanged; {count} pages complete; {characters} characters consistent; bookmarks and evidence targets valid.")
    print(f"Extraction flags: {len(quality['flagged_pages'])} pages; empty text: {len(quality['empty_pages'])}. See generated/quality.json.")


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        verify(args.root.resolve())
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, "FAIL: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
