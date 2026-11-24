"""Build dated web and practice records plus component navigation, without changing sources."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import quote
from practice import load_records

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_dirs(root, directory="ecosystem"):
    result = []
    for path in sorted((root / directory).glob("*")):
        if path.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.name):
            date.fromisoformat(path.name)
            result.append(path)
    return result


def source_paths(root):
    paths = [root / "tools/components.json", root / "generated/manifest.json"]
    for folder in snapshot_dirs(root):
        paths += sorted(p for p in folder.iterdir() if p.suffix in {".json", ".md"})
    for folder in snapshot_dirs(root, "repositories"):
        paths += sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix in {".json", ".md", ".txt"})
    paths += sorted(p for p in (root / "practice").rglob("*") if p.is_file() and p.suffix in {".json", ".md"})
    return paths


def source_hashes(root):
    return {p.relative_to(root).as_posix(): digest(p) for p in source_paths(root)}


def slug(name):
    return re.sub(r"[^a-z0-9._-]+", "-", name.casefold()).strip("-") or "component"


def build_data(root):
    hashes = source_hashes(root)
    config = read_json(root / "tools/components.json")
    manifest = read_json(root / "generated/manifest.json")
    docs = {d["id"]: d for d in manifest["documents"]}
    topics = [{"id": t["id"], "title": t["title"]} for t in manifest["topics"]] + config["extra_topics"]
    known_topics = {t["id"] for t in topics}
    components = {}
    bindings = {"images": {}, "packages": {}}
    for original in config["components"]:
        c = dict(original)
        if c["id"] in components:
            raise ValueError("Duplicate component: " + c["id"])
        for field in ("aliases", "images", "packages", "topics", "documents", "related_documents", "related_components"):
            c.setdefault(field, [])
        c["records"] = []
        c["_topic_priority"] = 3 if c["topics"] else -1
        c.setdefault("note", "")
        components[c["id"]] = c
        for field in bindings:
            for name in c[field]:
                key = name.casefold()
                if key in bindings[field]:
                    raise ValueError("Duplicate binding: " + name)
                bindings[field][key] = c["id"]

    records, snapshots = [], []
    for folder in snapshot_dirs(root):
        observed = folder.name
        coverage = read_json(folder / "coverage.json")
        images = read_json(folder / "images.json")
        packages = read_json(folder / "software_packages.json")
        for obj in (coverage, images, packages):
            if obj["observed_on"] != observed:
                raise ValueError("Snapshot date mismatch: " + observed)
        snapshots.append({"date": observed, "source_type": "ecosystem", "report": f"ecosystem/{observed}/README.md", "coverage": coverage})
        for field, rows, filename in (("images", images["families"], "images.json"),
                                      ("packages", packages["entries"], "software_packages.json")):
            for i, row in enumerate(rows):
                name = row["family"] if field == "images" else row["name"]
                component_id = bindings[field].get(name.casefold())
                if component_id is None:
                    # Only identical names (case-insensitive) auto-associate; no fuzzy merges.
                    component_id = next((k for k, c in components.items()
                                         if name.casefold() in [v.casefold() for v in c["images"] + c["packages"]]), None)
                if component_id is None:
                    component_id = slug(name)
                    if component_id in components:
                        component_id += "-" + hashlib.sha256(name.encode()).hexdigest()[:8]
                    components[component_id] = {"id": component_id, "name": name, "aliases": [name],
                        "images": [], "packages": [], "topics": [], "documents": [],
                        "related_documents": [], "related_components": [], "records": [], "note": "", "_topic_priority": -1}
                c = components[component_id]
                if name not in c[field]:
                    c[field].append(name)
                if name.casefold() in config.get("name_topics", {}):
                    priority, row_topics = 2, config["name_topics"][name.casefold()]
                elif row.get("group") in config["group_topics"]:
                    priority, row_topics = 1, config["group_topics"][row["group"]]
                else:
                    priority, row_topics = 0, config["category_topics"].get(row["category"], [])
                if priority > c["_topic_priority"]:
                    c["topics"], c["_topic_priority"] = row_topics, priority
                record_id = f"{observed}/{field}/{i}"
                c["records"].append(record_id)
                records.append({"record_id": record_id, "source_type": "ecosystem", "record_kind": field,
                    "snapshot_date": observed, "component_id": component_id, "title": name,
                    "source_path": f"ecosystem/{observed}/{filename}",
                    "json_pointer": f"/{'families' if field == 'images' else 'entries'}/{i}",
                    "source_url": row["source_url"], "verification": row["verification"],
                    "data": row, "text": json.dumps(row, ensure_ascii=False, indent=2)})

        # Preserve prose-only constraints (e.g. SDK minimum driver) as sourced sections.
        report = folder / "README.md"
        text = report.read_text(encoding="utf-8")
        sections = re.split(r"(?m)(?=^## )", text)
        line = 1
        for i, section in enumerate(sections):
            records.append({"record_id": f"{observed}/report/{i}", "source_type": "ecosystem",
                "record_kind": "report", "snapshot_date": observed, "component_id": None,
                "title": section.splitlines()[0].lstrip("# "),
                "source_path": f"ecosystem/{observed}/README.md", "source_line": line,
                "source_urls": list(dict.fromkeys(re.findall(r"\]\((https?://[^)]+)\)", section))),
                "verification": "snapshot_summary_not_server_validated", "text": section})
            line += section.count("\n")

    for folder in snapshot_dirs(root, "repositories"):
        observed = folder.name
        catalogue = read_json(folder / "repositories.json")
        coverage = read_json(folder / "coverage.json")
        if catalogue["observed_on"] != observed or coverage["observed_on"] != observed:
            raise ValueError("Repository snapshot date mismatch: " + observed)
        snapshots.append({"date": observed, "source_type": "github", "report": f"repositories/{observed}/README.md", "coverage": coverage})
        for i, row in enumerate(catalogue["repositories"]):
            name = row["name"]
            component_id = config.get("repository_bindings", {}).get(name)
            if component_id is not None and component_id not in components:
                raise ValueError("Unknown repository component binding: " + component_id)
            if component_id is None:
                component_id = "repo-" + slug(name)
                if component_id not in components:
                    components[component_id] = {"id": component_id, "name": name, "aliases": [name],
                        "images": [], "packages": [], "topics": row["topics"], "documents": [],
                        "related_documents": [], "related_components": [], "records": [], "note": "GitHub 仓库导航；C500 适用性以具体分支资料为准。", "_topic_priority": 3}
            c = components[component_id]
            c["aliases"] = list(dict.fromkeys([*c["aliases"], name]))
            base = {"source_type": "github", "snapshot_date": observed, "component_id": component_id,
                    "source_url": row["source_url"], "verification": "repository_observed_not_built_or_run",
                    "coverage_path": f"repositories/{observed}/coverage.json"}
            rid = f"{observed}/github/{name}"
            c["records"].append(rid)
            records.append(dict(base, record_id=rid, record_kind="repository", title=name,
                source_path=f"repositories/{observed}/repositories.json", json_pointer=f"/repositories/{i}",
                data=row, text=json.dumps(row, ensure_ascii=False, indent=2)))
            readme = row.get("readme", {})
            if readme.get("status") == "downloaded":
                path = folder / readme["path"]
                if digest(path) != readme["sha256"]:
                    raise ValueError("README hash mismatch: " + name)
                records.append(dict(base, record_id=rid + "/readme", record_kind="repository_readme",
                    title=name + " README", source_path=path.relative_to(root).as_posix(), source_line=1,
                    source_url=readme["source_url"], branch=readme["branch"], commit=readme.get("commit"),
                    text=path.read_text(encoding="utf-8", errors="replace")))

    records.extend(load_records(root, components, known_topics))
    for c in components.values():
        c.pop("_topic_priority")
        if set(c["topics"]) - known_topics:
            raise ValueError("Unknown component topic: " + c["id"])
        for doc_id in c["documents"] + c["related_documents"]:
            if doc_id not in docs:
                raise ValueError("Unknown document: " + doc_id)
        for other in c["related_components"]:
            if other not in components:
                raise ValueError("Unknown related component: " + other)
    for row in records:
        if row["source_type"] == "practice":
            continue
        c = components.get(row["component_id"])
        row["topics"] = c["topics"] if c else []
        row["aliases"] = list(dict.fromkeys([c["id"], c["name"], *c["aliases"], *c["images"], *c["packages"]])) if c else []
        row["documents"] = c["documents"] if c else []
        row["related_documents"] = c["related_documents"] if c else []
        row.setdefault("coverage_path", f"ecosystem/{row['snapshot_date']}/coverage.json")
    if hashes != source_hashes(root):
        raise ValueError("Sources changed during build; retry")
    return {"schema_version": 1, "source_hashes": hashes, "topics": topics,
            "snapshots": snapshots, "components": sorted(components.values(), key=lambda c: c["id"]), "records": records}


def render_components(data, root):
    docs = {d["id"]: d for d in read_json(root / "generated/manifest.json")["documents"]}
    lines = ["# C500 组件关联索引", "", "由 tools/build_knowledge.py 生成；维护 tools/components.json，勿手改本文件。",
        "", "[使用说明](README.md) · [PDF 清单](CATALOG.md) · [PDF 主题](TOPICS.md) · [实践知识](practice/README.md)", "",
        "关联用于定位资料，不构成版本兼容、配套安装或服务器验证结论。直接文档为对应组件资料；背景文档仅供查阅。",
        "相同名称可自动关联；近似名称需显式配置。无 PDF 关联表示尚未建立映射，不代表不支持。",
        "版本、tag、推荐驱动保留在日期快照中；最低版本、推荐版本和实测结果不得互相替代。", "",
        f"组件导航条目：{len(data['components'])}（含文档组件及发行分支，不是独立软件产品数）。", "", "## 日期快照", ""]
    for snap in data["snapshots"]:
        folder = Path(snap["report"]).parent.as_posix()
        lines.append(f"- [{snap['source_type']} / {snap['date']}]({snap['report']}) · [覆盖范围]({folder}/coverage.json)")
    lines += ["", "最新指本地采集日期最新，不能代表官网当前最新版本。", "", "## 按主题定位", ""]
    for topic in data["topics"]:
        lines += [f"<a id=\"topic-{topic['id']}\"></a>", f"### {topic['title']}", "", " · ".join(
            f"[{c['name']}](#{c['id']})" for c in data["components"] if topic["id"] in c["topics"]) or "暂无关联", ""]
    for c in data["components"]:
        lines += [f"<a id=\"{c['id']}\"></a>", f"## {c['name']} (`{c['id']}`)", "",
                  "主题：" + ", ".join(c["topics"]), "", "检索别名：" + "、".join(c["aliases"]), ""]
        for field, label in (("documents", "直接文档"), ("related_documents", "背景文档")):
            for doc_id in c[field]:
                d = docs[doc_id]
                lines.append(f"- {label}：[{d['title']} · {d['document_revision']}]({quote(d['navigation_path'])})（章节与物理页定位见链接）")
        if not c["documents"] and not c["related_documents"]:
            lines.append("- 本地 PDF：未建立关联。")
        for snap in data["snapshots"]:
            records = [r for r in data["records"] if r["component_id"] == c["id"] and r["snapshot_date"] == snap["date"]
                       and r["source_type"] == snap["source_type"] and "json_pointer" in r]
            if records:
                lines.append(f"- [{snap['date']} / {snap['source_type']}]({snap['report']})：" + "；".join(
                    f"[{r['title']}]({r['source_path']}) ({r['record_kind']}, `{r['json_pointer']}`)" for r in records))
        for row in data["records"]:
            if row["source_type"] == "practice" and c["id"] in row["component_ids"]:
                lines.append(f"- 实践 {row['snapshot_date']} / {row['record_kind']}：[{row['title']}]({row['source_path']})（行 {row['source_line']}；{row['verification']}；适用范围见原文）")
        if c["related_components"]:
            lines.append("- 相关入口（不自动扩展检索范围）：" + "、".join(f"[{x}](#{x})" for x in c["related_components"]))
        if c["note"]:
            lines.append("- 说明：" + c["note"])
        lines.append("")
    return "\n".join(lines) + "\n"


def load_knowledge(root):
    target = root / "generated/knowledge.json"
    if not target.exists() and not snapshot_dirs(root) and not snapshot_dirs(root, "repositories") and not (root / "tools/components.json").exists():
        return {"topics": [], "snapshots": [], "components": [], "records": []}
    if not target.exists():
        raise ValueError("Knowledge index missing; run tools/build_knowledge.py")
    data = read_json(target)
    if data["source_hashes"] != source_hashes(root):
        raise ValueError("Knowledge sources changed; run tools/build_knowledge.py")
    return data
