#!/usr/bin/env python3
"""Verify curated practice evidence, links and secret heuristics without remote access."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

from knowledge import ROOT, build_data


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded_file(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file():
        raise ValueError("Missing or out-of-scope asset path")
    return path


def secret_rules(text):
    # Deliberately report rule names only, never matching values.
    rules = {
        "URL with embedded credentials": r"https?://[^\s/\"<>]+:[^\s/\"<>]+@",
        "signed or subscription query": r"https?://[^\s\"<>]+[?&](?:token|key|auth|access_token|signature|x-amz-signature|sub)=[^\s\"<>]+",
        "credential assignment": r'''["']?(?:password|passwd|api[_-]?key|client[_-]?secret|subscription_url|access_token|refresh_token)["']?\s*[:=]\s*["'][^"'\r\n]{4,}["']''',
        "authorization value": r"\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/-]{16,}=*",
        "private key material": r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----",
    }
    return [name for name, pattern in rules.items() if re.search(pattern, text, re.I)]


def verify(root, check_originals=False):
    data = build_data(root)  # Includes record scope, sections and evidence digests.
    project = Path(__file__).resolve().parents[5]
    snapshots = references = 0
    for path in sorted((root / "practice").rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        rules = secret_rules(text)
        if rules:
            raise ValueError(f"Potential secret in {path.relative_to(root)}: {', '.join(rules)}")
        if path.suffix == ".md":
            for raw in re.findall(r"\]\(([^)]+)\)", text):
                link = urlsplit(raw)
                if link.scheme or not link.path:
                    continue
                target = (path.parent / unquote(link.path)).resolve()
                if not target.is_relative_to(project.resolve()) or not target.exists():
                    raise ValueError("Broken local link in " + str(path.relative_to(root)))
        if path.name != "artifacts.json":
            continue
        artifacts = json.loads(text)
        for row in artifacts["evidence_snapshots"]:
            snapshot = bounded_file(path.parent, row["snapshot"])
            if digest(snapshot) != row["snapshot_sha256"]:
                raise ValueError("Snapshot hash mismatch: " + str(snapshot.relative_to(root)))
            snapshots += 1
            if check_originals:
                original = bounded_file(project, row["original_path"])
                if digest(original) != row["original_sha256"]:
                    raise ValueError("Original evidence changed: " + row["original_path"])
        for row in artifacts["local_references"]:
            references += 1
            if check_originals:
                original = bounded_file(project, row["path"])
                if digest(original) != row["sha256"]:
                    raise ValueError("Referenced original changed: " + row["path"])
    return {"records": sum(r["source_type"] == "practice" for r in data["records"]),
            "snapshots": snapshots, "local_references": references,
            "originals_checked": check_originals, "remote_assets_checked": False,
            "secret_scan": "heuristics passed; manual review still required"}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check-originals", action="store_true")
    args = parser.parse_args()
    try:
        result = verify(args.root.resolve(), args.check_originals)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
