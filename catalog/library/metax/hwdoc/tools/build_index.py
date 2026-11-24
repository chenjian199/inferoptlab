#!/usr/bin/env python3
"""Rebuild the local PDF catalogue, page text and search index. Never edits PDFs."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

try:
    import pypdf
    from pypdf import PdfReader
except ImportError:
    raise SystemExit("Missing pypdf. Install hwdoc/tools/requirements.txt in your Python environment.")

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize(value):
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"[\u2010-\u2015\u2212]", "-", value)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    temporary.replace(path)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def md(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("[", "\\[").replace("]", "\\]")


def link(path, label, page=None):
    url = quote(str(path).replace("\\", "/"), safe="/.-_")
    if page:
        url += f"#page={page}"
    return f"[{md(label)}]({url})"


def outline_entries(reader):
    entries = []

    def visit(items, depth=1):
        for item in items:
            if isinstance(item, list):
                visit(item, depth + 1)
            else:
                page = reader.get_destination_page_number(item)
                if page is not None and 0 <= page < len(reader.pages):
                    entries.append({"title": item.title, "pdf_page": page + 1, "depth": depth})

    visit(reader.outline)
    return entries


def evidence(row, kind):
    return {"kind": kind, "pdf_page": row["pdf_page"], "page_label": row["page_label"],
            "text_path": row["text_path"]}


def build(root):
    config = json.loads((ROOT / "tools/topics.json").read_text(encoding="utf-8"))
    pdfs = sorted(root.glob("*.pdf"), key=lambda p: p.name.casefold())
    if not pdfs:
        raise SystemExit(f"No PDFs in {root}")
    originals = {p.name: digest(p) for p in pdfs}
    documents, all_pages, seen_ids = [], [], set()
    for path in pdfs:
        reader = PdfReader(path)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF: {path.name}")
        cover = reader.pages[0].extract_text() or ""
        normalized_cover = normalize(cover)
        revision_match = re.search(r"_V(\d+)", normalized_cover) or re.search(r"_V(\d+)", path.stem)
        revision = "V" + revision_match[1] if revision_match else None
        code_match = re.search(r"\b[A-Z]{2}-\d{5}-\d{3}-[A-Z0-9]+_V\d+\b", normalized_cover)
        date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", normalized_cover)
        rule = next((r for r in config["documents"] if r["match"].casefold() in path.name.casefold()), None)
        family = rule["id"] if rule else "doc-" + hashlib.sha256(path.stem.encode()).hexdigest()[:12]
        doc_id = family + ("-" + revision.lower() if revision else "")
        if doc_id in seen_ids:
            doc_id += "-" + hashlib.sha256(path.name.encode()).hexdigest()[:8]
        seen_ids.add(doc_id)
        topics = rule["topics"] if rule else []
        explicit_labels = "/PageLabels" in reader.trailer["/Root"]
        labels = reader.page_labels if explicit_labels else [None] * len(reader.pages)
        outline = outline_entries(reader)
        ordered = sorted(outline, key=lambda x: x["pdf_page"])
        first_body = min((o["pdf_page"] for o in outline), default=None)
        doc_pages = []
        for number, page in enumerate(reader.pages, 1):
            # Preserve extraction output. Search normalization is separate.
            text = page.extract_text() or ""
            on_page = [o["title"] for o in ordered if o["pdf_page"] == number]
            preceding = [o for o in ordered if o["pdf_page"] <= number]
            footer = re.search(r"(?:\|\s*|\n\s*)([0-9]+|[ivxlcdm]+)\s*$", text)
            footer_label = footer[1] if footer else None
            flags = []
            if not text.strip():
                flags.append("no_extracted_text")
            elif len(text.strip()) < 40:
                flags.append("short_text")
            if "\ufffd" in text:
                flags.append("replacement_character")
            private_use = sum(unicodedata.category(c) == "Co" for c in text)
            if private_use:
                flags.append("private_use_characters")
            if footer_label and labels[number - 1] and footer_label != labels[number - 1]:
                flags.append("footer_label_mismatch")
            row = {
                "doc_id": doc_id, "source_pdf": path.name, "source_sha256": originals[path.name],
                "document_revision": revision, "topics": topics, "pdf_page": number,
                "page_label": labels[number - 1], "footer_label_candidate": footer_label,
                "section_hint": preceding[-1]["title"] if preceding else None,
                "bookmarks_on_page": on_page,
                "front_matter": number < first_body if first_body else None,
                "text_path": f"generated/text/{doc_id}/page-{number:04d}.txt",
                "char_count": len(text), "private_use_characters": private_use,
                "quality_flags": flags, "text": text,
            }
            doc_pages.append(row)
        applicability = []
        for entry in outline:
            if "适用产品" in entry["title"]:
                row = doc_pages[entry["pdf_page"] - 1]
                text = row["text"]
                match = re.search(r"(?m)^\s*(?:\d+(?:\.\d+)*\s+)?适用产品\s*$", text)
                excerpt = text[match.end():].strip() if match else text
                excerpt = re.split(r"(?m)^\s*\d+(?:\.\d+)*\s+\S|^.*沐曦.*专有信息", excerpt)[0].strip()
                applicability.append({**evidence(row, "product_scope"), "excerpt": excerpt[:1800],
                                      "status": "extracted_source_requires_context_review"})
        version_evidence = []
        candidates = {o["pdf_page"] for o in outline if re.search("环境|版本|支持|前置|安装|部署|准备", o["title"])}
        if first_body:
            candidates.add(first_body)
        for number in sorted(candidates):
            row = doc_pages[number - 1]
            if re.search(r"版本|依赖|前置|环境准备|支持平台|SDK|Driver|Python|工具包|MACA_PATH", row["text"]):
                version_evidence.append(evidence(row, "software_requirements_candidate"))
        doc = {
            "id": doc_id, "family": family, "filename": path.name,
            "title": re.sub(r"_CN_V\d+$", "", path.stem), "document_revision": revision,
            "document_code": code_match[0] if code_match else None,
            "publication_date": date_match[0] if date_match else None,
            "sha256": originals[path.name], "bytes": path.stat().st_size,
            "page_count": len(reader.pages), "topics": topics,
            "has_explicit_page_labels": explicit_labels, "outline_count": len(outline),
            "outline_path": f"generated/outlines/{doc_id}.json",
            "navigation_path": f"generated/documents/{doc_id}.md",
            "applicability_status": "source_evidence_found" if applicability else "not_explicitly_identified",
            "applicability_evidence": applicability,
            "software_compatibility_status": "not_verified_against_server",
            "software_requirements_evidence": version_evidence,
            "pages_with_quality_flags": sum(bool(p["quality_flags"]) for p in doc_pages),
            "extracted_characters": sum(p["char_count"] for p in doc_pages),
            "cover_text": cover, "outline": outline,
        }
        documents.append(doc)
        all_pages.extend(doc_pages)
        print(f"Extracted {doc_id}: {len(doc_pages)} pages, {len(outline)} bookmarks", flush=True)

    # Reject concurrent PDF changes before publishing derived files.
    if originals != {p.name: digest(p) for p in root.glob("*.pdf")}:
        raise RuntimeError("Source PDFs changed during extraction. Retry the build.")
    now = datetime.now(timezone.utc).isoformat()
    quality = {
        "schema_version": SCHEMA_VERSION, "generated_at_utc": now,
        "document_count": len(documents), "page_count": len(all_pages),
        "source_hashes_verified": True,
        "empty_pages": [evidence(p, "no_extracted_text") | {"doc_id": p["doc_id"]} for p in all_pages if not p["text"].strip()],
        "flagged_pages": [{k: p[k] for k in ("doc_id", "pdf_page", "page_label", "text_path", "quality_flags")} for p in all_pages if p["quality_flags"]],
        "limitations": ["文本提取不保证图表、公式、代码缩进及跨页表格的版式正确；使用时回看 PDF。",
                       "质量标记仅是启发式检查；无标记不等于已完成视觉校验。",
                       "page_label 来自 PDF 元数据，footer_label_candidate 是页脚猜测；PDF 页序号是唯一定位依据。",
                       "主题为人工配置的导航分类；软件兼容性尚未与服务器实测核对。"],
    }
    for p in all_pages:
        header = (f"文档: {p['source_pdf']}\n文档 ID: {p['doc_id']}\nSHA256: {p['source_sha256']}\n"
                  f"PDF 页序号: {p['pdf_page']}\nPDF 页码标签: {p['page_label'] or '未提供'}\n"
                  f"页脚页码候选: {p['footer_label_candidate'] or '未识别'}\n"
                  f"章节提示（书签推断）: {p['section_hint'] or '前置页或无书签'}\n"
                  f"质量标记: {', '.join(p['quality_flags']) or '无启发式标记'}\n"
                  "--- 以下为未经语义改写的 PDF 提取文本 ---\n")
        write(root / p["text_path"], header + p["text"])

    for doc in documents:
        write(root / doc["outline_path"], json_text(doc["outline"]))
        lines = [f"# {doc['title']}", "", f"文档 ID：`{doc['id']}`；文档修订：{doc['document_revision']}；发布日期：{doc['publication_date']}。", "",
                 link('../../' + doc['filename'], '原始 PDF'), "", f"SHA256：`{doc['sha256']}`", "",
                 "文档修订号不等于 SDK 或框架版本。以下仅为原文导航，服务器兼容性尚未验证。", "", "## 适用产品来源", ""]
        for item in doc["applicability_evidence"]:
            lines += [link('../../' + doc['filename'], f"PDF 第 {item['pdf_page']} 页（标签 {item['page_label']}）", item['pdf_page']), "",
                      "> " + item["excerpt"].replace("\n", "\n> "), ""]
        if not doc["applicability_evidence"]:
            lines += ["未从“适用产品”书签识别到明确说明，不能据此推断支持或不支持 C500。", ""]
        lines += ["## 软件环境与版本要求的候选来源", "", "候选页由章节标题和文本关键词定位，不是兼容性结论；阅读完整页面及相邻上下文。", ""]
        for item in doc["software_requirements_evidence"]:
            lines.append("- " + link('../../' + doc['filename'], f"PDF 第 {item['pdf_page']} 页（标签 {item['page_label']}）", item['pdf_page']) + " · " + link('../../' + item['text_path'], '逐页文本'))
        if not doc["software_requirements_evidence"]:
            lines.append("未自动定位到候选页，请检索全文。")
        lines += ["", "## 完整章节书签", "", "标题保持 PDF 书签原样；同页多个章节按原书签顺序列出。", "", "| 层级 | 章节 | PDF 页序号 | 页码标签 | 文本 |", "|---|---|---:|---|---|"]
        doc_rows = [p for p in all_pages if p["doc_id"] == doc["id"]]
        for entry in doc["outline"]:
            row = doc_rows[entry["pdf_page"] - 1]
            lines.append(f"| {entry['depth']} | {md(entry['title'])} | {link('../../' + doc['filename'], entry['pdf_page'], entry['pdf_page'])} | {md(row['page_label'])} | {link('../../' + row['text_path'], '文本')} |")
        lines += ["", "## 全部页面", ""]
        lines += ["- " + link('../../' + row['text_path'], f"PDF {row['pdf_page']} / 标签 {row['page_label']}") for row in doc_rows]
        write(root / doc["navigation_path"], "\n".join(lines) + "\n")

    lines = ["# C500 文档清单", "", f"共 {len(documents)} 份 PDF，{len(all_pages)} 页；原始 PDF 保持原位。", "",
             "由 tools/build_index.py 生成。修订号来自文档，不代表软件版本。完整元数据、哈希、适用产品证据见 [manifest.json](generated/manifest.json)。", "",
             "[使用说明](README.md) · [主题索引](TOPICS.md) · [组件与生态关联](COMPONENTS.md) · [提取质量报告](generated/quality.json)", "",
             "| ID | 文档及章节导航 | 修订 | 发布日期 | 页数 | 适用产品证据（PDF 页） |", "|---|---|---|---|---:|---|"]
    for doc in documents:
        scope = ', '.join(link(doc['filename'], e['pdf_page'], e['pdf_page']) for e in doc['applicability_evidence']) or '未明确识别'
        lines.append(f"| `{doc['id']}` | {link(doc['navigation_path'], doc['title'])} · {link(doc['filename'], 'PDF')} | {doc['document_revision'] or '未知'} | {doc['publication_date'] or '未知'} | {doc['page_count']} | {scope} |")
    lines += ["", "## 来源完整性", "", "SHA256 用于确认派生文本对应哪一份 PDF；更新原件后须重新构建。", "", "| 文档 ID | SHA256 |", "|---|---|"]
    lines += [f"| `{doc['id']}` | `{doc['sha256']}` |" for doc in documents]
    write(root / "CATALOG.md", "\n".join(lines) + "\n")

    lines = ["# C500 主题索引", "", "人工配置文档归类，程序从原始书签筛选章节入口。它是导航，不是经过实测的操作方案。", "",
             "[文档清单](CATALOG.md) · [使用说明](README.md) · [组件与生态关联](COMPONENTS.md)", ""]
    for topic in config["topics"]:
        lines += [f"## {topic['title']} (`{topic['id']}`)", "", topic["purpose"], "", "检索词建议：" + '、'.join(f"`{k}`" for k in topic["keywords"]) + "。", ""]
        lines += [f"[本主题的软件组件与日期快照](COMPONENTS.md#topic-{topic['id']})（导航关联，不代表兼容性验证）", ""]
        for doc in documents:
            if topic["id"] not in doc["topics"]:
                continue
            lines += [f"### {doc['id']}", "", link(doc["navigation_path"], doc["title"] + '：完整章节及页面'), ""]
            selected = [o for o in doc["outline"] if any(k.casefold() in o["title"].casefold() for k in topic["keywords"])][:8]
            if not selected:
                selected = doc["outline"][:3]
            for entry in selected:
                lines.append("- " + link(doc['filename'], f"{entry['title']}（PDF 第 {entry['pdf_page']} 页）", entry['pdf_page']) + " · " + link(f"generated/text/{doc['id']}/page-{entry['pdf_page']:04d}.txt", "文本"))
            lines.append("")
    unknown = [doc for doc in documents if not doc["topics"]]
    if unknown:
        lines += ["## 未分类", "", "在 tools/topics.json 中补充分类后重新构建。", ""]
        lines += ["- " + link(d["navigation_path"], d["title"]) for d in unknown]
    write(root / "TOPICS.md", "\n".join(lines) + "\n")
    write(root / "generated/pages.jsonl", "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in all_pages))
    write(root / "generated/quality.json", json_text(quality))
    manifest = {"schema_version": SCHEMA_VERSION, "generated_at_utc": now,
                "extractor": {"name": "pypdf", "version": pypdf.__version__},
                "document_count": len(documents), "page_count": len(all_pages),
                "topics": config["topics"], "documents": [{k: v for k, v in d.items() if k != "outline"} for d in documents]}
    write(root / "generated/manifest.json", json_text(manifest))
    print(f"Built {len(documents)} documents / {len(all_pages)} pages. Empty pages: {len(quality['empty_pages'])}; flagged pages: {len(quality['flagged_pages'])}.")


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="PDF directory (default: hwdoc beside this script)")
    args = parser.parse_args()
    build(args.root.resolve())


if __name__ == "__main__":
    main()
