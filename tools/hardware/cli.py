"""Reusable hardware inventory, bounded calibration and recipe export."""
import argparse
import json
from pathlib import Path

from tools.specs import SpecError, read
from .config import load
from .export import export
from .runner import execute, verify
from .model import inspect_model


def report(directory):
    manifest, plan = verify(directory)
    lines = [f'{plan["id"]}@{plan["version"]}: {manifest["mode"]} / {manifest["status"]}']
    for entry in manifest['hosts']:
        raw = read(Path(directory)/entry['path'])
        lines.append(f'{entry["id"]}: {entry["status"]}' + (f' -- {raw["error"]}' if raw.get('error') else ''))
        for attempt in raw.get('attempts', []):
            lines.append(f'  GPU{attempt["ordinal"]}: {attempt["status"]}' + (f' -- {attempt["error"]}' if attempt.get('error') else ''))
            if attempt['status'] == 'measured':
                for m in attempt['result']['measurements']:
                    lines.append(f'    {m["name"]}: {m["value"]:.3f} {m["unit"]} (median; n={len(m["samples_ms"])})')
    missing = {h['id'] for h in plan['hosts']} - {h['id'] for h in manifest['hosts']}
    if missing:
        lines.append('Unfinished hosts: ' + ', '.join(sorted(missing)))
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    model = commands.add_parser('inspect-model', help='Read checkpoint metadata without GPU allocation')
    model.add_argument('--host', required=True)
    model.add_argument('--model', required=True, help='Absolute remote checkpoint directory')
    model.add_argument('--out', required=True, type=Path)
    for name in ('plan', 'inspect', 'run'):
        command = commands.add_parser(name)
        command.add_argument('plan', type=Path)
        if name != 'plan':
            command.add_argument('--out', type=Path, required=True, help='New artifact directory; never overwrite')
    for name in ('report', 'export'):
        command = commands.add_parser(name)
        command.add_argument('run', type=Path)
        if name == 'export':
            command.add_argument('--out', type=Path, required=True, help='Recipe/evidence root inside this repository')
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect-model':
            print(inspect_model(args.host, args.model, args.out))
        elif args.command == 'plan':
            print(json.dumps(load(args.plan), indent=2, ensure_ascii=False))
        elif args.command in ('inspect', 'run'):
            manifest = execute(load(args.plan), args.out, args.command)
            print(report(args.out))
            return 0 if manifest['status'] == 'complete' else 2
        elif args.command == 'report':
            print(report(args.run))
        else:
            paths = export(args.run, args.out)
            print(f'Exported {len(paths)} validated YAML recipes to {args.out}')
        return 0
    except (SpecError, OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
        parser.exit(2, f'hardware: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
