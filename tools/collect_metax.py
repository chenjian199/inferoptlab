"""Archive a read-only remote probe. No shell interpolation of user input."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="metax")
    parser.add_argument("--model", help="Absolute remote model directory; omit for host inventory")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.host.startswith("-"):
        parser.error("host cannot start with '-'")
    if args.out.exists():
        parser.error("output already exists; choose a new observation path")
    script = (Path(__file__).parent / "hardware/probes/metax.py").read_bytes()
    remote = ["python3", "-"] + (["model", args.model] if args.model else [])
    p = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
                        "-o", "StrictHostKeyChecking=yes", args.host, shlex.join(remote)],
                       input=script, capture_output=True, timeout=300)
    if p.returncode:
        raise SystemExit(p.stderr.decode(errors="replace"))
    doc = json.loads(p.stdout)
    doc["probe_sha256"] = hashlib.sha256(script).hexdigest()
    doc["ssh_host"] = args.host
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")
    args.out.with_suffix('.probe.py').write_bytes(script)
    print(args.out)


if __name__ == "__main__":
    main()
