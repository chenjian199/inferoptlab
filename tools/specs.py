"""Offline recipe validation, typed template expansion and study resolution.

No GPU work, external reference fetching, or performance acceptance is done here.
Run from any directory: python tools/specs.py --help.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if __name__ == "__main__":
    sys.modules.setdefault("tools.specs", sys.modules[__name__])
SCHEMA_FILES = {
    "OptimizationTask": "optimization-task.json",
    "MechanismCard": "mechanism-card.json",
    "AccuracyPlan": "accuracy.json",
    "OperatorCase": "operator-case.json",
    "BreakdownPlan": "breakdown.json",
    "BenchmarkOfflineReport": "benchmark-offline-report.json",
    "KnowledgeCollection": "knowledge-collection.json",
    "ExperimentRecord": "experiment-record.json",
    "BaselineRecord": "baseline-record.json",
    "SourceDocument": "source.json",
    "ModelSpec": "model.json",
    "HardwareSpec": "hardware.json",
    "RuntimeSpec": "runtime.json",
    "WorkloadSpec": "workload.json",
    "MeasurementProtocol": "measurement-protocol.json",
    "SLAProfile": "sla.json",
    "TestCaseSpec": "test-case.json",
    "StudySpec": "study.json",
    "ReportedMeasurements": "reported-measurements.json",
    "RecipeTemplate": "template.json",
    "ResolvedStudy": "snapshot.json",
    "ValidationPolicy": "validation-policy.json",
    "DeploymentSpec": "deployment.json",
    "BenchmarkScenario": "benchmark-scenario.json",
    "BenchmarkPlan": "benchmark.json",
    "ResolvedBenchmark": "benchmark-snapshot.json",
    "MeasurementBundle": "measurement.json",
    "HardwareMeasurement": "hardware-measurement.json",
    "HardwareTestPlan": "hardware-test.json",
    "AnalysisMethod": "analysis-method.json",
    "DiagnosisPlan": "diagnosis-plan.json",
    "DiagnosisReport": "diagnosis-report.json",
    "AnalysisPlan": "analysis-plan.json",
    "AnalysisReport": "analysis-report.json",
    "TraceCapture": "trace-capture.json",
    "TraceSummary": "trace-summary.json",
    "OptimizationHandoff": "optimization-handoff.json",
}
REFERENCE_KINDS = {
    "operator_case_refs": "OperatorCase",
    "source_ref": "SourceDocument", "model_ref": "ModelSpec",
    "model_refs": "ModelSpec", "hardware_ref": "HardwareSpec",
    "hardware_refs": "HardwareSpec", "device_profile_ref": "HardwareSpec",
    "runtime_ref": "RuntimeSpec", "workload_ref": "WorkloadSpec",
    "protocol_ref": "MeasurementProtocol", "sla_ref": "SLAProfile",
    "case_refs": "TestCaseSpec",
    "correctness_policy_ref": "ValidationPolicy", "quality_policy_ref": "ValidationPolicy",
    "evaluation_policy_ref": "ValidationPolicy",
    "case_ref": "TestCaseSpec", "study_ref": "StudySpec",
    "deployment_refs": "DeploymentSpec", "scenario_refs": "BenchmarkScenario",
    "inventory_source_ref": "SourceDocument",
    "method_ref": "AnalysisMethod", "method_refs": "AnalysisMethod",
    "calibration_refs": "HardwareMeasurement", "historical_refs": "ReportedMeasurements",
    "diagnosis_plan_ref": "DiagnosisPlan",
}
LATENCIES = {"ttft", "tpot", "itl", "chunk_interval", "e2e_latency"}
METRIC_UNITS = {
    **{name: {"ms", "s"} for name in LATENCIES},
    "request_throughput": {"requests/s"}, "request_goodput": {"requests/s"},
    "input_token_throughput": {"tokens/s"}, "output_token_throughput": {"tokens/s"},
    "output_token_goodput": {"tokens/s"}, "success_rate": {"fraction", "percent"},
    "joint_slo_attainment": {"fraction", "percent"}, "peak_memory": {"bytes", "GB", "GiB"},
    "power": {"W"},
}


class SpecError(ValueError):
    pass


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject silently overwritten YAML keys; don't reinterpret date strings."""


UniqueKeyLoader.yaml_implicit_resolvers = {
    key: [(tag, rx) for tag, rx in values if tag != "tag:yaml.org,2002:timestamp"]
    for key, values in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise SpecError("YAML mapping keys must be strings")
        if key in result:
            raise SpecError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def read(path: Path) -> dict:
    path = Path(path)
    try:
        document = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise SpecError(f"{path}: {exc}") from exc
    if not isinstance(document, dict):
        raise SpecError(f"{path}: expected a document object")
    # Reject YAML-only objects and non-finite floats before any hashing.
    try:
        canonical(document)
    except (ValueError, TypeError, RecursionError) as exc:
        raise SpecError(f"{path}: must be finite, acyclic JSON-compatible data") from exc
    return document


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def key(ref: dict) -> tuple[str, str]:
    return ref["id"], ref["version"]


def walk(value: Any, path: str = ""):
    yield path, value
    if isinstance(value, dict):
        for name, child in value.items():
            yield from walk(child, f"{path}/{name}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}/{index}")


def references(document: dict):
    for path, value in walk(document):
        if path.startswith("/extensions"):
            continue
        if isinstance(value, dict) and set(value) == {"id", "version"}:
            field = path.split("/")[-1]
            if field.isdigit():
                field = path.split("/")[-2]
            if field in REFERENCE_KINDS or field == "evidence_refs":
                yield path, value, REFERENCE_KINDS.get(field)


class Catalog:
    def __init__(self, root: Path = ROOT):
        self.root = root.resolve()
        self.schemas: dict[str, dict] = {}
        resources = []
        definitions = self.root / "schemas" / "definitions"
        for path in sorted(definitions.rglob("*.json")):
            schema = json.loads(path.read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            self.schemas[path.relative_to(definitions).as_posix()] = schema
            if "$id" in schema:
                resources.append((schema["$id"], Resource.from_contents(schema)))
        # No retrieve callback: undeclared remote schema URLs never trigger networking.
        self.registry = Registry().with_resources(resources)
        self.documents: dict[tuple[str, str], dict] = {}
        self.paths: dict[tuple[str, str], Path] = {}

    def structural_errors(self, document: dict) -> list[str]:
        kind = document.get("kind")
        version = document.get("schema_version")
        filename = SCHEMA_FILES.get(kind) if version == "0.2.0" else None
        if filename is None:
            return [f"unsupported kind/version: {kind}/{version}"]
        validator = Draft202012Validator(self.schemas[filename], registry=self.registry)
        errors = [f"/{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(document)]
        if not errors and kind == "RecipeTemplate":
            for path, value in walk(document["body"]):
                if isinstance(value, dict) and "$param" in value:
                    if set(value) != {"$param"} or not isinstance(value["$param"], str) or value["$param"] not in document["parameters"]:
                        errors.append(f"{path}: invalid parameter expression")
            for name, definition in document["parameters"].items():
                if "default" in definition:
                    errors.extend(f"{name}: invalid default: {e.message}" for e in Draft202012Validator(definition).iter_errors(definition["default"]))
        return errors

    def load(self) -> None:
        self.documents.clear()
        self.paths.clear()
        roots = [self.root / "recipes"]
        for path in sorted(p for directory in roots for p in directory.rglob("*.yaml")):
            document = read(path)
            errors = self.structural_errors(document)
            if errors:
                raise SpecError(f"{path}:\n" + "\n".join(errors))
            if document['kind'] in {'ResolvedStudy', 'ResolvedBenchmark', 'MeasurementBundle', 'RecipeTemplate', 'DiagnosisReport', 'AnalysisReport', 'TraceCapture', 'TraceSummary', 'OptimizationHandoff', 'ExperimentRecord', 'BaselineRecord', 'BenchmarkOfflineReport', 'KnowledgeCollection'}:
                raise SpecError(f"{path}: snapshots, results and templates do not belong in recipe directories")
            identity = key(document)
            if identity in self.documents:
                raise SpecError(f"duplicate recipe identity {identity}: {self.paths[identity]} and {path}")
            self.documents[identity] = document
            self.paths[identity] = path

    def get(self, ref: dict) -> dict:
        try:
            return self.documents[key(ref)]
        except KeyError as exc:
            raise SpecError(f"unresolved reference: {ref}") from exc

    def semantic_errors(self, doc: dict, verify_sources: bool = False) -> list[str]:
        if doc['kind'] in {'OptimizationTask','MechanismCard'}:
            return []
        if doc['kind'] in {'AccuracyPlan','BreakdownPlan','OperatorCase','BenchmarkOfflineReport'}:
            from benchmark.common.offline import semantic_errors
            return semantic_errors(self,doc,verify_sources)
        if doc['kind']=='KnowledgeCollection':
            return []
        if doc['kind'] in {'ExperimentRecord','BaselineRecord'}:
            from tools.experiments import check
            try:check(self,doc)
            except (SpecError,OSError) as exc:return [str(exc)]
            return []
        if doc['kind'] in {'AnalysisMethod','DiagnosisPlan','DiagnosisReport','AnalysisPlan','AnalysisReport','TraceCapture','TraceSummary','OptimizationHandoff'}:
            from diagnosis.contracts import semantic_errors
            return semantic_errors(self,doc,verify_sources)
        if doc['kind'] == 'HardwareTestPlan':
            from tools.hardware.config import semantic_errors
            return semantic_errors(doc)
        if doc["kind"] in {"DeploymentSpec", "BenchmarkScenario", "BenchmarkPlan", "ResolvedBenchmark", "MeasurementBundle"}:
            # Lazy import keeps the offline catalog independent of optional GPU packages.
            from benchmark.load.planner import semantic_errors
            return semantic_errors(self, doc, verify_sources)
        if doc["kind"] == "ResolvedStudy":
            return self.snapshot_errors(doc, verify_sources)
        errors = []
        for path, reference, expected in references(doc):
            try:
                target = self.get(reference)
                if expected and target["kind"] != expected:
                    errors.append(f"{path}: expected {expected}, got {target['kind']}")
            except SpecError as exc:
                errors.append(str(exc))
        if errors:
            return errors
        kind = doc["kind"]
        from tools.spec_details import errors as detail_errors
        errors.extend(detail_errors(doc, self))
        if kind == "ModelSpec":
            for field, purpose in (("correctness_policy_ref", "correctness"), ("quality_policy_ref", "quality")):
                reference = doc["semantics"][field]
                if reference and self.get(reference)["purpose"] != purpose:
                    errors.append(f"{field}: requires a {purpose} validation policy")
        elif kind == "SourceDocument":
            path = (self.root / doc["path"]).resolve()
            if not path.is_relative_to(self.root):
                errors.append("source path escapes repository")
            elif verify_sources:
                if not path.is_file():
                    errors.append(f"source is missing: {path}")
                elif hashlib.sha256(path.read_bytes()).hexdigest() != doc["sha256"]:
                    errors.append(f"source hash mismatch: {path}")
        elif kind == "SLAProfile":
            ids = [c["id"] for c in doc["constraints"]]
            if len(ids) != len(set(ids)):
                errors.append("constraint IDs must be unique")
            for c in doc["constraints"]:
                if c["metric"] in METRIC_UNITS and c["unit"] not in METRIC_UNITS[c["metric"]]:
                    errors.append(f"{c['id']}: incompatible metric unit {c['unit']}")
                if c["statistic"] == "per_request" and c["scope"] != "request":
                    errors.append(f"{c['id']}: per_request statistic requires request scope")
                if c["normalization"]["basis"] == "reference_device_count" and "device_count" not in c["normalization"]:
                    errors.append(f"{c['id']}: reference device count is required")
                if "range" in c["threshold"] and c["threshold"]["range"]["min"] > c["threshold"]["range"]["max"]:
                    errors.append(f"{c['id']}: threshold interval is reversed")
                bounds = list(c["threshold"]["range"].values()) if "range" in c["threshold"] else [c["threshold"]["value"]]
                if c["metric"] in METRIC_UNITS and any(x < 0 for x in bounds):
                    errors.append(f"{c['id']}: negative threshold is invalid for this metric")
            joint = doc["joint_request_slo"]
            if joint:
                by_id = {c["id"]: c for c in doc["constraints"]}
                for cid in joint["constraint_ids"]:
                    if cid not in by_id or by_id[cid]["statistic"] != "per_request":
                        errors.append(f"joint SLO must reference per_request constraints: {cid}")
        elif kind == "WorkloadSpec":
            arrival = doc["arrival"]
            if len(arrival['load_points'])!=len(set(arrival['load_points'])):
                errors.append('load points must be unique')
            if doc['requests'].get('count_multiplier') is not None and (arrival['mode']!='closed_loop' or arrival['load_unit']!='concurrency'):
                errors.append('count_multiplier requires closed_loop concurrency')
            if doc['requests'].get('request_set_sha256_by_concurrency') is not None:
                if doc['requests'].get('count_multiplier') is None:
                    errors.append('per-concurrency hashes require count_multiplier')
                if set(doc['requests']['request_set_sha256_by_concurrency'])!={str(int(c)) for c in arrival['load_points']}:
                    errors.append('per-concurrency hashes must cover exactly the declared load points')
            if arrival["mode"] in {"closed_loop", "burst"} and arrival["load_unit"] not in {"concurrency", "per_dp_batch", "unspecified"}:
                errors.append("closed-loop/burst load must use concurrency, not requests/s")
            if arrival["mode"] == "open_loop" and arrival["load_unit"] != "requests/s":
                errors.append("open-loop load must use requests/s")
            if arrival["load_unit"] in {"concurrency", "per_dp_batch"} and any(x != int(x) for x in arrival["load_points"]):
                errors.append("concurrency/per-DP batch points must be integers")
            if doc["cache"]["prefix_reuse"] == "disabled" and doc["cache"]["target_hit_ratio"] not in (None, 0):
                errors.append("disabled prefix reuse cannot declare nonzero hit ratio")
            for field in ("input", "output"):
                length = doc[field]
                if length["origin"] == "unresolved_k" and (length["tokens"] is not None or length["k_multiplier"] is not None):
                    errors.append(f"{field}: unresolved K cannot declare resolved token counts")
                if length["origin"] == "source_defined_k" and (length["tokens"] is None or length["k_multiplier"] is None):
                    errors.append(f"{field}: source-defined K requires exact tokens and multiplier")
        elif kind == "HardwareSpec":
            nodes = [n["node_id"] for n in doc["resources"]["nodes"]]
            if len(nodes) != len(set(nodes)):
                errors.append("physical node IDs must be unique")
            devices = [d["device_id"] for n in doc["resources"]["nodes"] for d in n["devices"]]
            if len(devices) != len(set(devices)):
                errors.append("physical device IDs must be globally unique within a cluster")
            if devices and doc["resources"]["allocated_devices"] != len(set(devices)):
                errors.append("allocated_devices differs from unique physical device mapping")
            if any(c["state"] == "verified" and not c["evidence_refs"] for c in doc["capabilities"]):
                errors.append("verified capability requires evidence")
        elif kind == "TestCaseSpec":
            workload, protocol = self.get(doc["workload_ref"]), self.get(doc["protocol_ref"])
            sla = self.get(doc["sla_ref"]) if doc["sla_ref"] else None
            if protocol["method"] == "prefill_one_token" and workload["output"]["tokens"] != 1:
                errors.append("prefill_one_token requires exactly one output token")
            if protocol["method"] == "prefix_reuse_decode" and workload["cache"]["prefix_reuse"] not in {"enabled", "conflicting"}:
                errors.append("prefix_reuse_decode requires prefix reuse enabled")
            if sla:
                metrics = {c["metric"] for c in sla["constraints"]}
                if workload["output"]["tokens"] == 1 and metrics & {"tpot", "itl"}:
                    errors.append("TPOT/ITL is undefined for one output token")
                if "itl" in metrics and protocol["timing"]["token_timestamps"] == "unavailable":
                    errors.append("true ITL requires token timestamps; chunk timestamps are insufficient")
                for metric in ("ttft", "tpot"):
                    if metric in metrics and protocol["timing"][metric+"_boundary"] == "not_applicable":
                        errors.append(f"{metric}: SLA metric conflicts with not_applicable timing boundary")
            if protocol["method"] == "fake_prefill" and doc["purpose"] != "diagnostic":
                errors.append("fake_prefill can only be used in diagnostic cases")
        elif kind == "StudySpec":
            case_ids = []
            for r in doc["case_refs"]:
                case = self.get(r)
                case_ids.append(case["id"])
                if case["model_ref"] != doc["model_ref"]:
                    errors.append(f"{case['id']}: case model does not match study")
                protocol = self.get(case["protocol_ref"])
                if not set(doc["allowed_deployment_modes"]).issubset(protocol["allowed_deployment_modes"]):
                    errors.append(f"{case['id']}: study deployment modes violate case protocol")
            if len(case_ids) != len(set(case_ids)):
                errors.append("study case references must be unique")
            objective = doc["objective"]
            if objective and objective["aggregation"] == "weighted_geomean":
                weights = objective["case_weights"]
                if set(weights) != set(case_ids) or not math.isclose(sum(weights.values()), 1, abs_tol=1e-9):
                    errors.append("case weights must cover every case exactly and sum to one")
        elif kind == "ReportedMeasurements":
            columns = {c["name"]: c for c in doc["columns"]}
            if len(columns) != len(doc["columns"]):
                errors.append("table column names must be unique")
            row_ids = set()
            for row in doc["rows"]:
                if row["row_id"] in row_ids:
                    errors.append(f"duplicate row ID: {row['row_id']}")
                row_ids.add(row["row_id"])
                if set(row["values"]) != set(columns):
                    errors.append(f"{row['row_id']}: values must match declared columns")
                nulls = {name for name, value in row["values"].items() if value is None}
                if nulls != set(row["missing"]):
                    errors.append(f"{row['row_id']}: every null requires exactly one missing reason")
                for name, value in row["values"].items():
                    if name in columns and value is not None:
                        for error in Draft202012Validator({"type": columns[name]["type"]}).iter_errors(value):
                            errors.append(f"{row['row_id']}/{name}: {error.message}")
        return errors

    def snapshot_errors(self, snapshot: dict, verify_sources: bool = False) -> list[str]:
        """Validate embedded documents independently of mutable catalog contents."""
        errors = []
        payload = {k: v for k, v in snapshot.items() if k != "content_sha256"}
        if digest(payload) != snapshot["content_sha256"]:
            errors.append("snapshot content hash mismatch")
        embedded = Catalog(self.root)
        for entry in snapshot["documents"]:
            doc = entry["document"]
            current = self.structural_errors(doc)
            if current or doc.get("kind") in {"ResolvedStudy", "RecipeTemplate"} or doc.get("schema_version") != "0.2.0":
                errors.extend(current or ["snapshots require v0.2.0 recipes; templates and nested snapshots are not allowed"])
                continue
            if key(entry["ref"]) != key(doc):
                errors.append("embedded document identity mismatch")
            if digest(doc) != entry["sha256"]:
                errors.append(f"{doc['id']}: embedded document hash mismatch")
            if key(doc) in embedded.documents:
                errors.append(f"duplicate embedded document: {key(doc)}")
            embedded.documents[key(doc)] = doc
        if errors:
            return errors
        try:
            study = embedded.get(snapshot["study_ref"])
            if study["kind"] != "StudySpec":
                return ["snapshot root must be a StudySpec"]
            closure = embedded.closure(study)
            if {key(d) for d in closure} != set(embedded.documents):
                errors.append("snapshot contains documents outside the study reference closure")
            for doc in closure:
                errors.extend(embedded.semantic_errors(doc, verify_sources))
            blockers = embedded.readiness_issues(closure)
            if blockers != snapshot["readiness_issues"]:
                errors.append("snapshot readiness issues differ from computed issues")
            if snapshot["state"] == "frozen" and blockers:
                errors.append("frozen snapshot contains unresolved requirements")
        except SpecError as exc:
            errors.append(str(exc))
        return errors

    def closure(self, study: dict) -> list[dict]:
        result, visited, active = {}, set(), set()

        def visit(doc):
            identity = key(doc)
            if identity in active:
                raise SpecError(f"cyclic recipe reference at {identity}")
            if identity in visited:
                return
            active.add(identity)
            for _, reference, _ in references(doc):
                visit(self.get(reference))
            active.remove(identity)
            visited.add(identity)
            result[identity] = doc

        visit(study)
        return [result[k] for k in sorted(result)]

    def readiness_issues(self, documents: list[dict]) -> list[str]:
        problems = []
        for doc in documents:
            label, kind = doc["id"], doc["kind"]
            for issue in doc["issues"]:
                if issue["blocking"]:
                    problems.append(f"{label}{issue['path']}: {issue['reason']}")
            # Readiness is computed, not accepted from a user-editable boolean.
            if kind in {"SourceDocument", "ReportedMeasurements"}:
                continue
            for path, value in walk(doc):
                if path.startswith(("/issues", "/provenance", "/extensions")):
                    continue
                if isinstance(value, str) and ("REPLACE_" in value or value in {"unspecified", "unresolved", "conflicting"}):
                    problems.append(f"{label}{path}: unresolved value {value}")
                if isinstance(value, dict) and "$param" in value:
                    problems.append(f"{label}{path}: unresolved template parameter")
            def require(value, path):
                if value is None or value == [] or value == {}:
                    problems.append(f"{label}{path}: required before freezing")
            if kind == "ModelSpec":
                checkpoint = doc.get("checkpoint")
                if checkpoint:
                    if not checkpoint["payload_verified"]:
                        problems.append(f"{label}/checkpoint: weight payload integrity is not verified")
                    if not checkpoint["index_matches_headers"] or checkpoint["duplicate_tensor_names"]:
                        problems.append(f"{label}/checkpoint: shard index/header ambiguity remains")
                    if checkpoint["compatibility"]["status"] != "observed_loaded":
                        problems.append(f"{label}/checkpoint: target loader compatibility is not verified")
                for field in ("repository", "revision", "weights_sha256"):
                    require(doc["identity"][field], "/identity/"+field)
                for field in ("revision", "sha256"):
                    require(doc["tokenizer"][field], "/tokenizer/"+field)
                require(doc["semantics"]["correctness_policy_ref"], "/semantics/correctness_policy_ref")
                if doc["semantics"]["contract"] == "task_quality":
                    require(doc["semantics"]["quality_policy_ref"], "/semantics/quality_policy_ref")
            elif kind == "HardwareSpec" and doc["profile_type"] == "cluster":
                if doc.get("discovery", {}).get("health") in {"degraded", "unverified"}:
                    problems.append(f"{label}/discovery/health: hardware health is not verified")
                require(doc["resources"]["allocated_devices"], "/resources/allocated_devices")
                require(doc["resources"]["nodes"], "/resources/nodes")
                if not doc["capabilities"] or any(c["state"] != "verified" for c in doc["capabilities"]):
                    problems.append(f"{label}: required hardware capabilities not verified")
            elif kind == "RuntimeSpec":
                for field in ("source_commit", "container_digest", "driver", "device_runtime"):
                    require(doc[field], "/"+field)
                if doc["status"] != "environment_verified":
                    problems.append(f"{label}: runtime environment not verified")
                if doc["source_commit"] and not re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", doc["source_commit"]):
                    problems.append(f"{label}: full immutable source commit required")
                if doc["container_digest"] and not re.fullmatch(r"sha256:[a-f0-9]{64}", doc["container_digest"]):
                    problems.append(f"{label}: sha256 container digest required")
            elif kind == "WorkloadSpec":
                for name in ("input", "output"):
                    require(doc[name]["tokens"], "/"+name+"/tokens")
                if doc['requests'].get('count_multiplier') is not None:
                    hashes=doc['requests'].get('request_set_sha256_by_concurrency',{})
                    for c in doc['arrival']['load_points']:
                        require(hashes.get(str(int(c))), '/requests/request_set_sha256_by_concurrency/'+str(int(c)))
                else:
                    require(doc["requests"]["request_set_sha256"], "/requests/request_set_sha256")
                require(doc["requests"].get("count_multiplier") or doc["requests"]["count"], "/requests/count or count_multiplier")
                require(doc["arrival"]["load_points"], "/arrival/load_points")
                for name, value in doc["generation"].items():
                    require(value, "/generation/"+name)
                require(doc["cache"]["preparation"], "/cache/preparation")
                require(doc["cache"]["reset_between_runs"], "/cache/reset_between_runs")
            elif kind == "MeasurementProtocol":
                for name, value in doc["execution"].items():
                    require(value, "/execution/"+name)
                require(doc["accounting"]["logical_request_deduplication"], "/accounting/logical_request_deduplication")
            elif kind == "TestCaseSpec" and doc["sla_ref"]:
                sla = self.get(doc["sla_ref"])
                protocol = self.get(doc["protocol_ref"])
                if any(c["metric"] == "itl" for c in sla["constraints"]) and protocol["timing"]["token_timestamps"] != "available":
                    problems.append(f"{label}: ITL requires verified token timestamp availability")
            elif kind == "SLAProfile":
                if any("range" in c["threshold"] for c in doc["constraints"]):
                    problems.append(f"{label}: SLA threshold interval must be resolved")
                for requirement in doc["quality_requirements"]:
                    require(requirement["evaluation_policy_ref"], "/quality_requirements/evaluation_policy_ref")
            elif kind == "ValidationPolicy":
                for field in ("evaluator_sha256", "dataset_sha256", "reference_sha256"):
                    require(doc[field], "/"+field)
                require(doc["checks"], "/checks")
                require(doc["execution"]["command"], "/execution/command")
            elif kind == "StudySpec":
                hardware = self.get(doc["hardware_ref"])
                if hardware["profile_type"] != "cluster":
                    problems.append(f"{label}: study requires a concrete cluster, not a device SKU")
                for name, value in doc["budget"].items():
                    require(value, "/budget/"+name)
        return sorted(set(problems))

    def resolve(self, study: dict, freeze: bool = False) -> dict:
        if study.get("kind") != "StudySpec" or study.get("schema_version") != "0.2.0":
            raise SpecError("resolve requires a v0.2.0 StudySpec")
        errors = self.structural_errors(study)
        if errors:
            raise SpecError("\n".join(errors))
        documents = self.closure(study)
        errors = []
        for document in documents:
            errors.extend(self.structural_errors(document))
            errors.extend(self.semantic_errors(document, verify_sources=True))
        if errors:
            raise SpecError("\n".join(errors))
        blockers = self.readiness_issues(documents)
        if freeze and blockers:
            raise SpecError("cannot freeze:\n" + "\n".join(blockers))
        payload = {"schema_version": "0.2.0", "kind": "ResolvedStudy", "state": "frozen" if freeze else "draft",
                   "study_ref": {"id": study["id"], "version": study["version"]},
                   "documents": [{"ref": {"id": d["id"], "version": d["version"]}, "sha256": digest(d), "document": copy.deepcopy(d)} for d in documents],
                   "readiness_issues": blockers}
        return {**payload, "content_sha256": digest(payload)}


def instantiate(template: dict, supplied: dict, catalog: Catalog) -> dict:
    errors = catalog.structural_errors(template)
    if errors:
        raise SpecError("\n".join(errors))
    parameters = template["parameters"]
    unknown = set(supplied) - set(parameters)
    if unknown:
        raise SpecError(f"unknown template parameters: {sorted(unknown)}")
    values = {}
    for name, definition in parameters.items():
        if name not in supplied and "default" not in definition:
            raise SpecError(f"missing template parameter: {name}")
        value = supplied[name] if name in supplied else definition["default"]
        errors = list(Draft202012Validator(definition).iter_errors(value))
        if errors:
            raise SpecError(f"parameter {name}: {errors[0].message}")
        values[name] = copy.deepcopy(value)

    def expand(value):
        if isinstance(value, dict):
            if "$param" in value:
                if set(value) != {"$param"} or value["$param"] not in values:
                    raise SpecError(f"invalid parameter expression: {value}")
                return copy.deepcopy(values[value["$param"]])
            return {name: expand(child) for name, child in value.items()}
        if isinstance(value, list):
            return [expand(child) for child in value]
        return value

    result = expand(template["body"])
    if result.get("kind") != template["target_kind"]:
        raise SpecError("template target_kind differs from expanded body")
    errors = catalog.structural_errors(result)
    if errors:
        raise SpecError("expanded template:\n" + "\n".join(errors))
    return result


def write(path: Path, document: dict) -> None:
    # Exclusive creation protects existing recipe versions and snapshots.
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        if path.suffix == ".json":
            json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        else:
            yaml.safe_dump(document, stream, allow_unicode=True, sort_keys=False)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate all recipes or one file")
    validate.add_argument("path", nargs="?", type=Path)
    validate.add_argument("--sources", action="store_true", help="check source file SHA-256 values")
    create = commands.add_parser("instantiate", help="expand a typed template into a draft recipe")
    create.add_argument("template", type=Path)
    create.add_argument("--params", type=Path, help="YAML/JSON parameter mapping")
    create.add_argument("--out", type=Path, required=True)
    for name in ("resolve", "freeze"):
        resolve = commands.add_parser(name)
        resolve.add_argument("study", type=Path)
        resolve.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        catalog = Catalog(args.root)
        catalog.load()
        if args.command == "validate":
            targets = [(args.path, read(args.path))] if args.path else [(catalog.paths[k], d) for k, d in catalog.documents.items()]
            if not args.path:
                targets += [(p, read(p)) for p in sorted((catalog.root / "schemas" / "templates").rglob("*.yaml"))]
            errors = []
            for path, doc in targets:
                current = catalog.structural_errors(doc)
                if not current and doc.get("schema_version") == "0.2.0" and doc["kind"] != "RecipeTemplate":
                    current += catalog.semantic_errors(doc, args.sources)
                    if doc["kind"] not in {"ResolvedStudy", "ResolvedBenchmark", "MeasurementBundle", "DiagnosisReport", "AnalysisReport", "TraceSummary", "OptimizationHandoff", "ExperimentRecord", "BaselineRecord", "BenchmarkOfflineReport", "KnowledgeCollection", "OptimizationTask", "MechanismCard"}:
                        try:
                            closure = catalog.closure(doc)
                            if args.path and args.sources:
                                for dependency in closure:
                                    if dependency["kind"] == "SourceDocument" and dependency is not doc:
                                        current += catalog.semantic_errors(dependency, verify_sources=True)
                        except SpecError as exc:
                            current.append(str(exc))
                errors.extend(f"{path}: {e}" for e in current)
            if errors:
                raise SpecError("\n".join(errors))
            print(f"Validated {len(targets)} document(s); schemas, references and semantic checks passed.")
            print("Catalog validity does not establish execution readiness or measured performance.")
        elif args.command == "instantiate":
            doc = instantiate(read(args.template), read(args.params) if args.params else {}, catalog)
            write(args.out, doc)
            print(f"Created draft recipe: {args.out}")
        else:
            snapshot = catalog.resolve(read(args.study), freeze=args.command == "freeze")
            write(args.out, snapshot)
            print(f"{snapshot['state']}: {len(snapshot['documents'])} documents; {len(snapshot['readiness_issues'])} readiness issue(s).")
            print(f"SHA-256: {snapshot['content_sha256']}")
        return 0
    except (SpecError, OSError, ValueError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
