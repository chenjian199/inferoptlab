"""Explicit, local practice records. Evidence is hashed, never automatically indexed."""
from datetime import date
import hashlib
import json
from pathlib import Path


def practice_path(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to((root / "practice").resolve()):
        raise ValueError("Practice path escapes practice directory: " + relative)
    if not path.is_file():
        raise ValueError("Missing practice source: " + relative)
    return path


def load_records(root, components, known_topics):
    manifest = root / "practice/records.json"
    if not manifest.exists():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data["schema_version"] != 1:
        raise ValueError("Unsupported practice schema")
    records, ids = [], set()
    for entry in data["records"]:
        rid = "practice/" + entry["id"]
        if rid in ids:
            raise ValueError("Duplicate practice record: " + rid)
        ids.add(rid)
        date.fromisoformat(entry["observed_on"])
        if entry["kind"] not in {"runbook", "case", "issue"}:
            raise ValueError("Unknown practice kind: " + rid)
        if not entry["components"] or set(entry["components"]) - components.keys():
            raise ValueError("Unknown or empty practice components: " + rid)
        if not entry["topics"] or set(entry["topics"]) - known_topics:
            raise ValueError("Unknown or empty practice topics: " + rid)
        if not entry["verification"] or not entry["applicability"] or not entry["evidence"]:
            raise ValueError("Missing practice scope/evidence: " + rid)
        path = practice_path(root, entry["path"])
        if path.suffix != ".md":
            raise ValueError("Practice searchable text must be Markdown: " + rid)
        practice_path(root, entry["coverage_path"])
        for evidence in entry["evidence"]:
            source = practice_path(root, evidence["path"])
            if hashlib.sha256(source.read_bytes()).hexdigest() != evidence["sha256"]:
                raise ValueError("Practice evidence hash mismatch: " + evidence["path"])
        text = path.read_text(encoding="utf-8")
        line = 1
        if entry.get("section"):
            lines = text.splitlines(keepends=True)
            matches = [i for i, value in enumerate(lines) if value.rstrip() == entry["section"]]
            if len(matches) != 1 or not entry["section"].startswith("## "):
                raise ValueError("Missing or ambiguous practice section: " + rid)
            start = matches[0]
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
            text, line = "".join(lines[start:end]), start + 1
        aliases = list(entry.get("keywords", []))
        for cid in entry["components"]:
            c = components[cid]
            c["records"].append(rid)
            aliases.extend([cid, c["name"], *c["aliases"]])
        records.append({"record_id": rid, "source_type": "practice", "record_kind": entry["kind"],
            "snapshot_date": entry["observed_on"], "component_id": entry["components"][0],
            "component_ids": entry["components"], "title": entry["title"],
            "source_path": entry["path"], "source_line": line,
            "verification": entry["verification"], "applicability": entry["applicability"],
            "coverage_path": entry["coverage_path"], "evidence": entry["evidence"],
            "topics": entry["topics"], "aliases": list(dict.fromkeys(aliases)),
            "documents": [], "related_documents": [], "text": text})
    return records
