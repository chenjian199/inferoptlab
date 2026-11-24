"""Read public GitHub metadata and README files; never clone or execute repository code."""
import argparse
import concurrent.futures
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, date
from pathlib import Path

ORG = "MetaX-MACA"
FOCUS = {"vLLM-metax", "sglang", "vllm-omni-metax", "verl-metax", "mcPytorch", "mcTriton",
         "mcoplib", "MXDeepEP", "DeepEP", "FlashMLA", "mcFlashMLA", "TileOPs-Metax",
         "TileKernels-Metax", "mccl_tests", "maca-samples", "op_optimization"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "C500-document-inventory", "Accept": "application/vnd.github+json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read(), dict(r.headers)
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except urllib.error.URLError:
            if attempt == 2:
                raise
        time.sleep(1 + attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    date.fromisoformat(args.date)
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    if (out / "raw_repositories.json").exists():
        parser.error("Existing snapshot; choose a new output folder to preserve history")
    (out / "readmes").mkdir(exist_ok=True)
    repos, pages = [], []
    for page in range(1, 20):
        url = f"https://api.github.com/orgs/{ORG}/repos?per_page=100&type=public&sort=full_name&page={page}"
        raw, headers = get(url)
        batch = json.loads(raw)
        repos.extend(batch)
        pages.append({"url": url, "count": len(batch), "link": headers.get("Link")})
        if len(batch) < 100:
            break
    (out / "raw_repositories.json").write_text(json.dumps(repos, ensure_ascii=False, indent=2), encoding="utf-8")
    detail = {}
    for repo in repos:
        if repo["name"] not in FOCUS:
            continue
        entry = {}
        for endpoint in ("branches?per_page=100", "releases?per_page=3"):
            url = repo["url"] + "/" + endpoint
            try:
                raw, headers = get(url)
                entry[endpoint.split("?")[0]] = {"url": url, "data": json.loads(raw), "link": headers.get("Link")}
            except Exception as exc:
                entry[endpoint.split("?")[0]] = {"url": url, "error": str(exc)}
        detail[repo["name"]] = entry
        print("Details:", repo["name"], flush=True)
    (out / "focus_metadata.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

    def readme(repo):
        branch = repo["default_branch"]
        branches = detail.get(repo["name"], {}).get("branches", {}).get("data", [])
        commit = next((b["commit"]["sha"] for b in branches if b["name"] == branch), None)
        ref = commit or branch
        errors = []
        for name in ("README.md", "README.rst", "readme.md", "README", "Readme.md"):
            url = f"https://raw.githubusercontent.com/{ORG}/{repo['name']}/{urllib.parse.quote(ref, safe='/')}/{name}"
            try:
                raw, _ = get(url)
                path = out / "readmes" / (repo["name"] + ".txt")
                path.write_bytes(raw)
                return {"name": repo["name"], "status": "downloaded", "path": path.relative_to(out).as_posix(),
                        "source_url": url, "readme_filename": name, "branch": branch, "commit": commit,
                        "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    errors.append(str(exc))
                    break
            except Exception as exc:
                errors.append(str(exc))
                break
        return {"name": repo["name"], "status": "not_retrieved", "branch": branch, "errors": errors,
                "note": "Common root README filenames tried; no assertion that repository has no documentation"}

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        readmes = list(pool.map(readme, repos))
    (out / "readme_manifest.json").write_text(json.dumps(readmes, ensure_ascii=False, indent=2), encoding="utf-8")
    coverage = {"observed_on": args.date, "fetched_at_utc": datetime.now(timezone.utc).isoformat(), "organization": ORG,
                "source_url": f"https://github.com/{ORG}", "pages": pages, "repository_count": len(repos),
                "readmes_downloaded": sum(r["status"] == "downloaded" for r in readmes), "focus_repositories": sorted(FOCUS),
                "limitations": ["Public repositories only; repository metadata is not proof of C500 support.",
                    "README files are from default branches, pinned to commit where focus branch API succeeded.",
                    "Only focus repositories have branch lists (first 100) and up to 3 release records; no exhaustive tags/history audit.",
                    "Fork READMEs may retain upstream NVIDIA/CUDA instructions; not proof of MetaX adaptation.",
                    "pushed_at is repository-level activity, not the default branch commit date or maintenance guarantee.",
                    "No repository code, install script, benchmark or model was run. No server validation."]}
    (out / "coverage.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"repositories":len(repos),"readmes":coverage["readmes_downloaded"]}))


if __name__ == "__main__":
    main()
