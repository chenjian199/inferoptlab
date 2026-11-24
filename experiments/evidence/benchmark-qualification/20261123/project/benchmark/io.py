"""Artifact helpers. Configuration files use the strict loader in tools.specs."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from tools.specs import SpecError


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def file_hash(path: Path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def json_write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace only our own mutable run-status artifacts, never recipe versions.
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def jsonl_write(path: Path, records):
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")


def inside(root: Path, name: str):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()):
        raise SpecError(f"path escapes repository: {name}")
    return path
