"""Offline handoff only: no shell, SSH, backend invocation or GPU execution."""
import argparse
import json
from pathlib import Path
import sys

from tools.specs import ROOT, Catalog, SpecError, write
from optimization.handoff import prepare, render


def main(argv=None):
    parser = argparse.ArgumentParser(description="Stage 4 offline optimization handoff")
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("plan")
    command.add_argument("analysis", type=Path)
    command.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        catalog = Catalog(args.root)
        catalog.load()
        result = prepare(catalog, args.analysis)
        args.out.mkdir(parents=True, exist_ok=False)
        write(args.out / "handoff.yaml", result)
        (args.out / "report.md").write_text(render(result), encoding="utf-8")
        print(json.dumps({"output": str(args.out), "kind": result["kind"], "new_gpu_execution": False}))
        return 0
    except (SpecError, OSError, ValueError, KeyError, TypeError) as exc:
        print("optimization: " + str(exc), file=sys.stderr)
        return 2
