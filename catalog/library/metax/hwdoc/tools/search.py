#!/usr/bin/env python3
"""Search PDFs, dated web snapshots and scoped practice records (standard library only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from knowledge import load_knowledge

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_sources(root, manifest):
    expected = {doc["filename"]: doc["sha256"] for doc in manifest["documents"]}
    actual = {p.name: sha256(p) for p in root.glob("*.pdf")}
    if actual != expected:
        changed = sorted(k for k in expected.keys() | actual.keys() if expected.get(k) != actual.get(k))
        raise ValueError("PDFs changed; run tools/build_index.py first: " + ", ".join(changed))


def compact(text, positions=False):
    """Ignore case, whitespace, common Unicode hyphen variants and fullwidth forms."""
    output, offsets = [], []
    for i, char in enumerate(text):
        normalized = unicodedata.normalize("NFKC", char).casefold()
        for c in normalized:
            if c.isspace():
                continue
            if c in "‐‑‒–—―−":
                c = "-"
            output.append(c)
            if positions:
                offsets.append(i)
    return ("".join(output), offsets) if positions else "".join(output)


def snippet(text, needles, radius=85):
    normalized, offsets = compact(text, positions=True)
    starts = [normalized.find(n) for n in needles if n in normalized]
    at = offsets[min(starts)] if starts else 0
    lo, hi = max(0, at - radius), min(len(text), at + radius * 2)
    return ("…" if lo else "") + re.sub(r"\s+", " ", text[lo:hi]).strip() + ("…" if hi < len(text) else "")


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="*", help="Terms; all must match the same page by default")
    parser.add_argument("--any", action="store_true", help="Match any term instead of all")
    parser.add_argument("--doc", help="Document ID or filename substring")
    parser.add_argument("--topic", help="Topic ID (see --list)")
    parser.add_argument("--page", type=int, help="1-based physical PDF page; requires --doc")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--body-only", action="store_true", help="Exclude pages before the first PDF bookmark")
    parser.add_argument("--full", action="store_true", help="Display complete extracted page text")
    parser.add_argument("--json", action="store_true", help="Return machine-readable JSON")
    parser.add_argument("--list", action="store_true", help="List documents and topic IDs")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--source", choices=["all", "pdf", "ecosystem", "github", "practice"], default="all")
    parser.add_argument("--snapshot", default=None, help="Date: latest per web source (default; all practice records retained), all, or YYYY-MM-DD")
    parser.add_argument("--component", help="Exact component ID or unambiguous alias; see --list")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.limit < 1 or (args.page is not None and (args.page < 1 or not args.doc)):
        parser.error("--limit and --page must be positive; --page requires --doc")
    pdf_filter = bool(args.doc or args.page is not None or args.body_only)
    if pdf_filter and args.source in {"ecosystem", "github", "practice"}:
        parser.error("--doc, --page and --body-only are PDF-only filters")
    effective_source = "pdf" if pdf_filter else args.source
    if effective_source == "pdf" and args.snapshot is not None:
        parser.error("--snapshot cannot be combined with PDF-only search")
    try:
        manifest = json.loads((root / "generated/manifest.json").read_text(encoding="utf-8"))
        if effective_source in {"pdf", "all"}:
            check_sources(root, manifest)
        knowledge = load_knowledge(root) if effective_source != "pdf" or args.component or args.list else {
            "topics": [], "snapshots": [], "components": [], "records": []}
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, str(exc) + "\n")
    topics = {t["id"]: t for t in [*manifest["topics"], *knowledge["topics"]]}
    dates_by_source = {kind: sorted({s["date"] for s in knowledge["snapshots"] if s.get("source_type", "ecosystem") == kind})
                       for kind in ("ecosystem", "github")}
    practice_dates = sorted({r["snapshot_date"] for r in knowledge["records"] if r["source_type"] == "practice"})
    if practice_dates or effective_source == "practice":
        dates_by_source["practice"] = practice_dates
    dates = sorted({day for values in dates_by_source.values() for day in values})
    searchable_sources = [effective_source] if effective_source in dates_by_source else list(dates_by_source)
    available_dates = {day for kind in searchable_sources for day in dates_by_source[kind]}
    requested_date = args.snapshot or "latest"
    if requested_date not in {"latest", "all", *available_dates}:
        parser.error("Unknown snapshot date; see --list")
    selected_by_source = {kind: (values if requested_date == "all" or (kind == "practice" and requested_date == "latest") else values[-1:] if requested_date == "latest"
                                else [requested_date] if requested_date in values else [])
                          for kind, values in dates_by_source.items() if kind in searchable_sources}
    selected_dates = sorted({day for values in selected_by_source.values() for day in values})
    component = None
    if args.component:
        exact = [c for c in knowledge["components"] if compact(c["id"]) == compact(args.component)]
        matches = exact or [c for c in knowledge["components"] if compact(args.component) in
                           {compact(v) for v in [c["name"], *c["aliases"], *c["images"], *c["packages"]]}]
        if len(matches) != 1:
            parser.error("Unknown or ambiguous component; use exact ID from --list")
        component = matches[0]
    if args.list:
        result = {"topics": [{"id": t["id"], "title": t["title"]} for t in topics.values()],
                  "documents": [{"id": d["id"], "filename": d["filename"], "pages": d["page_count"], "topics": d["topics"]} for d in manifest["documents"]],
                  "components": [{k: c[k] for k in ("id", "name", "aliases", "topics")} for c in knowledge["components"]],
                  "snapshots": dates, "latest_snapshot": dates[-1] if dates else None, "snapshots_by_source": dates_by_source}
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for topic in result["topics"]:
                print(f"{topic['id']}: {topic['title']}")
            print()
            for doc in result["documents"]:
                print(f"{doc['id']} ({doc['pages']} pages): {doc['filename']}")
            print("\n快照: " + ", ".join(dates))
            for c in result["components"]:
                print(f"{c['id']}: {c['name']} ({', '.join(c['topics'])})")
        return
    if args.topic and args.topic not in topics:
        parser.error("Unknown topic; see --list")
    if args.doc and not any(compact(args.doc) in compact(d["id"] + " " + d["filename"]) for d in manifest["documents"]):
        parser.error("No matching document; see --list")
    # Each positional argument is a term. Quoting groups a phrase, whose whitespace is ignored.
    terms = list(dict.fromkeys(compact(q) for q in args.query if compact(q)))
    if not terms and args.page is None and component is None:
        parser.error("Supply search terms, --component ID, --doc ID --page NUMBER, or --list")
    hits = []
    pdf_rows = (root / "generated/pages.jsonl").read_text(encoding="utf-8").splitlines() if effective_source in {"pdf", "all"} else []
    if pdf_rows:
        for line in pdf_rows:
            row = json.loads(line)
            if component and row["doc_id"] not in component["documents"] + component["related_documents"]:
                continue
            if args.doc and compact(args.doc) not in compact(row["doc_id"] + " " + row["source_pdf"]):
                continue
            if args.topic and args.topic not in row["topics"]:
                continue
            if args.page is not None and row["pdf_page"] != args.page:
                continue
            if args.body_only and row["front_matter"] is True:
                continue
            text = compact(row["text"])
            matched = [term for term in terms if term in text]
            if terms and not (bool(matched) if args.any else len(matched) == len(terms)):
                continue
            heading = compact(" ".join(row["bookmarks_on_page"]))
            score = (100 * len(matched) + sum(min(text.count(t), 15) for t in matched)
                     + 20 * sum(t in heading for t in matched) - (30 if row["front_matter"] else 0))
            hit = {k: v for k, v in row.items() if k != "text"}
            hit.update(score=score, snippet=snippet(row["text"], terms),
                       source_path=str(root / row["source_pdf"]), text_file=str(root / row["text_path"]))
            doc = next(d for d in manifest["documents"] if d["id"] == row["doc_id"])
            hit.update(source_type="pdf", verification="document_description_not_server_validated",
                       document_revision=doc.get("document_revision"), publication_date=doc.get("publication_date"))
            if component:
                hit["component_relation"] = "direct_document" if row["doc_id"] in component["documents"] else "background_document"
            if args.full:
                hit["text"] = row["text"]
            hits.append(hit)
    if effective_source != "pdf":
        for row in knowledge["records"]:
            if row["snapshot_date"] not in selected_by_source.get(row["source_type"], []):
                continue
            if component and component["id"] not in row.get("component_ids", [row["component_id"]]):
                continue
            if args.topic and args.topic not in row["topics"]:
                continue
            # Alias metadata broadens non-PDF lookup, never rewrites PDF text.
            text = compact(row["text"] + " " + " ".join(row["aliases"]))
            matched = [term for term in terms if term in text]
            if terms and not (bool(matched) if args.any else len(matched) == len(terms)):
                continue
            hit = {k: v for k, v in row.items() if k != "text"}
            hit.update(score=100 * len(matched) + sum(min(text.count(t), 15) for t in matched)
                       + 20 * sum(t in compact(row["title"]) for t in matched),
                       snippet=snippet(row["text"], terms), source_path=str(root / row["source_path"]),
                       alias_matches=[a for a in row["aliases"] if any(t in compact(a) for t in terms)])
            if args.full:
                hit["text"] = row["text"]
            hits.append(hit)
    hits.sort(key=lambda h: (-h["score"], h["source_type"], h.get("record_id", h.get("doc_id", "")), h.get("pdf_page", 0)))
    counts = {s: sum(h["source_type"] == s for h in hits) for s in ("pdf", "ecosystem", "github", "practice")}
    result = {"query": args.query, "mode": "any" if args.any else "all", "source": effective_source,
              "snapshot_dates": selected_dates if effective_source != "pdf" else [],
              "snapshots_by_source": selected_by_source if effective_source != "pdf" else {},
              "component": component["id"] if component else None, "matches_by_source": counts,
              "total_matches": len(hits), "results": hits[:args.limit]}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(f"匹配 {len(hits)} 条（PDF {counts['pdf']} 页 / 生态 {counts['ecosystem']} 条 / GitHub {counts['github']} 条 / 实践 {counts['practice']} 条），显示 {min(args.limit, len(hits))} 条。")
    if effective_source != "pdf":
        print("本地来源日期: " + json.dumps(selected_by_source, ensure_ascii=False) + "；验证状态逐条标注。latest 对生态/GitHub 分别取最新日期，实践保留全部案例。")
    for n, hit in enumerate(result["results"], 1):
        if hit["source_type"] != "pdf":
            print(f"\n{n}. [{hit['source_type']}/{hit['record_kind']}] {hit['title']} | {hit['snapshot_date']} | {hit['verification']}")
            print(f"   快照: {hit['source_path']} {hit.get('json_pointer', 'line ' + str(hit.get('source_line', '')))}")
            print("   覆盖范围与限制: " + str(root / hit["coverage_path"]))
            if hit["source_type"] == "practice":
                print("   适用范围: " + hit["applicability"])
                for evidence in hit["evidence"]:
                    print("   证据: " + str(root / evidence["path"]) + " | SHA256 " + evidence["sha256"])
            urls = [hit["source_url"]] if "source_url" in hit else hit.get("source_urls", [])
            for url in urls:
                print("   网页来源: " + url)
            if hit["source_type"] == "github":
                info = hit.get("data", hit)
                print(f"   分支: {info.get('default_branch', info.get('branch', '未知'))} | README commit: {info.get('readme', info).get('commit') or '未固定'}")
            if hit["alias_matches"]:
                print("   别名匹配: " + ", ".join(hit["alias_matches"]))
            if hit["documents"] or hit["related_documents"]:
                print("   文档关联: " + ", ".join(hit["documents"]) + "；背景资料: " + ", ".join(hit["related_documents"]))
            print(hit["text"] if args.full else "   " + hit["snippet"])
            continue
        print(f"\n{n}. {hit['doc_id']} | PDF 第 {hit['pdf_page']} 页 | 标签 {hit['page_label']} | {hit['section_hint'] or '前置页'}")
        print(f"   [pdf] 修订 {hit['document_revision']} | 发布 {hit['publication_date']} | 文档描述，未在服务器验证")
        if hit.get("component_relation"):
            print("   组件关联: " + hit["component_relation"])
        print(f"   原文: {hit['source_path']}")
        print(f"   文本: {hit['text_file']}")
        print(hit["text"] if args.full else "   " + hit["snippet"])
        if hit["quality_flags"]:
            print("   质量标记: " + ", ".join(hit["quality_flags"]))


if __name__ == "__main__":
    main()
