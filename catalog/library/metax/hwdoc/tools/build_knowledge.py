#!/usr/bin/env python3
"""Build/check component navigation and unified knowledge records (stdlib only)."""
import argparse
import json
import sys
from pathlib import Path
from knowledge import ROOT, build_data, render_components


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Recompute and compare without writing")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        data = build_data(root)
        outputs = {root / "generated/knowledge.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                   root / "COMPONENTS.md": render_components(data, root)}
        for path, text in outputs.items():
            if args.check:
                if not path.exists() or path.read_text(encoding="utf-8") != text:
                    raise ValueError(f"Stale or missing output: {path}; run build_knowledge.py")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_suffix(path.suffix + ".tmp")
                temporary.write_text(text, encoding="utf-8")
                temporary.replace(path)
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(f"{'Verified' if args.check else 'Built'} {len(data['components'])} components, {len(data['records'])} knowledge records, {len(data['snapshots'])} web snapshots.")


if __name__ == "__main__":
    main()
