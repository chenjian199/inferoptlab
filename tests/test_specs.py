"""Specification contract tests; synthetic fixtures never represent GPU evidence."""
import copy
import hashlib
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.specs import Catalog, ROOT, SpecError, digest, instantiate, key, read, write


def ref(name):
    return {"id": name, "version": "1.0.0"}


class SpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Catalog()
        cls.base.load()

    def setUp(self):
        self.catalog = copy.copy(self.base)
        self.catalog.documents = copy.deepcopy(self.base.documents)

    def get(self, name):
        return self.catalog.get(ref(name))

    def study(self):
        return self.get("deepseek-bw1000-contract")

    def fixture_sources(self):
        """Isolate unit tests from optional original attachments; never edit real recipes."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copytree(ROOT / "schemas/definitions", root / "schemas/definitions")
        self.catalog.root = root
        for document in self.catalog.documents.values():
            if document["kind"] == "SourceDocument":
                data = ("SYNTHETIC UNIT TEST SOURCE: " + document["id"]).encode()
                document["path"] = "fixtures/" + document["id"] + ".txt"
                path = root / document["path"]
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(data)
                document["sha256"] = hashlib.sha256(data).hexdigest()

    def complete_synthetic_study(self):
        """Complete *metadata* fixture only: no fabricated persisted recipe/evidence."""
        self.fixture_sources()
        study = self.study()
        study["case_refs"] = [ref("case-deepseek-contract-5-prefill")]
        study["budget"] = dict(max_candidates=1, max_device_hours=1, max_wall_hours=1)
        model = self.get(study["model_ref"]["id"])
        model["identity"].update(repository="fixture://model", revision="a"*40, weights_sha256="b"*64)
        model["tokenizer"].update(revision="a"*40, sha256="c"*64)
        model["semantics"].update(contract="numerical_tolerance", correctness_policy_ref=ref("fixture-policy"))
        policy = dict(schema_version="0.2.0", kind="ValidationPolicy", id="fixture-policy", version="1.0.0",
            title="SYNTHETIC TEST ONLY", provenance=[], issues=[], extensions={}, purpose="correctness",
            evaluator_sha256="d"*64, dataset_sha256="e"*64, reference_sha256="f"*64,
            checks=[dict(metric="absolute_error", operator="le", threshold=0.001, unit="absolute", aggregation="max")],
            execution=dict(command="fixture-only-no-execution", parameters={}))
        self.catalog.documents[key(policy)] = policy
        hardware = self.get(study["hardware_ref"]["id"])
        hardware["resources"]["allocated_devices"] = 8
        hardware["resources"]["nodes"] = [dict(node_id="fixture-node", cpu="fixture", dram_gb=512,
            nics=["fixture-nic"], devices=[dict(device_id=f"fixture:{i}", device_profile_ref=ref("bw1000")) for i in range(8)])]
        hardware["capabilities"] = [dict(name="fixture-only", state="verified", scope="fixture-only",
            evidence_refs=[ref("source-deepseek-project")])]
        runtime = self.get(study["runtime_ref"]["id"])
        runtime.update(source_commit="a"*40, container_digest="sha256:"+"c"*64, driver="fixture",
            device_runtime="fixture", status="environment_verified")
        workload = self.get("workload-deepseek-contract-5-prefill")
        workload["input"].update(tokens=4096, k_multiplier=1024, origin="source_defined_k")
        workload["requests"].update(request_set_sha256="d"*64, seed=0, count=16)
        workload["generation"].update(ignore_eos=False, sampling="greedy", stop_policy="fixed_output_tokens")
        workload["arrival"]["load_points"] = [16]
        workload["cache"].update(preparation="reset", reset_between_runs=True)
        protocol = self.get("deepseek-contract-prefill")
        protocol["timing"].update(ttft_boundary="client_submit_to_first_content_token", window="fixed_request_set",
            start="first_planned_send", finish="last_completion_or_timeout")
        protocol["execution"].update(warmup="one excluded run", timeout_s=60, repetitions=3, profiler_during_scoring=False)
        protocol["accounting"].update(primary_population="all_planned_requests", failure_policy="retain_in_denominator",
            logical_request_deduplication=True)
        sla = self.get("sla-deepseek-contract-5-prefill")
        sla["conditional_requirements"] = []
        for constraint in sla["constraints"]:
            constraint["population"] = "all_planned_requests"
        for document in self.catalog.closure(study):
            document["issues"] = []
        return study

    def test_all_recipe_structures_and_references_validate(self):
        for document in self.catalog.documents.values():
            with self.subTest(document=document["id"]):
                self.assertEqual(self.catalog.structural_errors(document), [])
                self.assertEqual(self.catalog.semantic_errors(document), [])
                self.catalog.closure(document)

    def test_original_source_hashes_when_attachments_available(self):
        sources = [d for d in self.catalog.documents.values() if d["kind"] == "SourceDocument"]
        missing = [d for d in sources if not (ROOT / d["path"]).resolve().is_file()]
        for document in sources:
            errors = self.catalog.semantic_errors(document, verify_sources=True)
            if document in missing:
                self.assertTrue(any("source is missing" in e for e in errors))
            else:
                self.assertEqual(errors, [])
        if missing:
            self.skipTest(f"{len(missing)} original attachments absent; source validation correctly rejects them")

    def test_current_examples_validate_and_old_versions_are_rejected(self):
        for path in ["examples/study.example.yaml", "examples/deployments.example.yaml", "examples/optimization-task.example.yaml",
                     "catalog/mechanisms/reduce-redundant-materialization.yaml"]:
            self.assertEqual(self.catalog.structural_errors(read(ROOT/path)), [], path)
            old=read(ROOT/path);old['schema_version']='0.1'
            self.assertTrue(self.catalog.structural_errors(old))

    def test_every_template_expands_and_validates_references(self):
        for path in sorted((ROOT/"schemas/templates").rglob("*.yaml")):
            params = "-".join(path.relative_to(ROOT/"schemas/templates").parts)
            with self.subTest(path=path):
                result = instantiate(read(path), read(ROOT/"examples/parameters"/params), self.catalog)
                self.assertEqual(self.catalog.structural_errors(result), [])
                self.assertEqual(self.catalog.semantic_errors(result), [])

    def test_template_parameter_type_and_unknown_names(self):
        template = read(ROOT/"schemas/templates/slas/latency.yaml")
        params = read(ROOT/"examples/parameters/slas-latency.yaml")
        params["threshold_ms"] = "5000"
        with self.assertRaisesRegex(SpecError, "parameter threshold_ms"):
            instantiate(template, params, self.catalog)
        params["threshold_ms"] = 5000
        params["unexpected"] = True
        with self.assertRaisesRegex(SpecError, "unknown template"):
            instantiate(template, params, self.catalog)

    def test_template_unresolved_parameter_is_rejected(self):
        template = read(ROOT/"schemas/templates/slas/latency.yaml")
        template["body"]["id"] = {"$param": "undeclared"}
        with self.assertRaisesRegex(SpecError, "invalid parameter"):
            instantiate(template, read(ROOT/"examples/parameters/slas-latency.yaml"), self.catalog)

    def test_unknown_fields_rejected(self):
        model = self.get("glm-5.3")
        model["identitiy"] = {}
        self.assertTrue(self.catalog.structural_errors(model))

    def test_extensions_require_namespace(self):
        self.study()["extensions"] = {"unnamespaced": {}}
        self.assertTrue(self.catalog.structural_errors(self.study()))

    def test_reference_wrong_kind_and_missing_version(self):
        case = self.get("case-deepseek-contract-5-prefill")
        case["model_ref"] = ref("bw1000")
        self.assertIn("expected ModelSpec", "\n".join(self.catalog.semantic_errors(case)))
        case["model_ref"]["version"] = "9.9.9"
        self.assertIn("unresolved reference", "\n".join(self.catalog.semantic_errors(case)))

    def test_duplicate_yaml_and_non_finite_data_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"bad.yaml"
            for content in ["a: 1\na: 2\n", "nested:\n  a: 1\n  a: 2\n", "value: .nan\n"]:
                path.write_text(content, encoding="utf-8")
                with self.assertRaises(SpecError):
                    read(path)

    def test_duplicate_global_identity_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            shutil.copytree(ROOT/"schemas/definitions", root/"schemas/definitions")
            (root/"recipes").mkdir()
            for name in ["a.yaml", "b.yaml"]:
                write(root/"recipes"/name, self.get("bw1000"))
            with self.assertRaisesRegex(SpecError, "duplicate recipe identity"):
                Catalog(root).load()

    def test_source_hash_and_path_check(self):
        self.fixture_sources()
        source = self.get("source-industry-sla")
        source["sha256"] = "0"*64
        self.assertIn("source hash mismatch", "\n".join(self.catalog.semantic_errors(source, True)))
        source["path"] = "../outside.png"
        self.assertIn("source path escapes", "\n".join(self.catalog.semantic_errors(source)))

    def test_single_token_tpot_rejected(self):
        case = self.get("case-deepseek-contract-5-prefill")
        case["sla_ref"] = ref("sla-deepseek-contract-5-decode")
        self.assertIn("undefined for one output token", "\n".join(self.catalog.semantic_errors(case)))

    def test_undefined_timing_boundary_rejected(self):
        protocol = self.get("deepseek-contract-prefill")
        protocol["timing"]["ttft_boundary"] = "not_applicable"
        self.assertIn("not_applicable", "\n".join(self.catalog.semantic_errors(self.get("case-deepseek-contract-5-prefill"))))

    def test_mean_and_aggregated_only_are_legitimate(self):
        study = self.study()
        self.assertEqual(study["allowed_deployment_modes"], ["aggregated"])
        self.assertEqual(self.catalog.semantic_errors(study), [])
        self.assertEqual(self.get("sla-deepseek-contract-5-prefill")["constraints"][1]["statistic"], "mean")

    def test_modes_and_weights_must_match_cases(self):
        self.study()["allowed_deployment_modes"] = ["aggregated", "pd"]
        self.assertIn("deployment modes", "\n".join(self.catalog.semantic_errors(self.study())))
        self.study()["allowed_deployment_modes"] = ["aggregated"]
        self.study()["objective"] = dict(metric="request_throughput", direction="maximize", aggregation="weighted_geomean", case_weights={"wrong": 1})
        self.assertIn("weights", "\n".join(self.catalog.semantic_errors(self.study())))

    def test_wrong_units_and_negative_thresholds_rejected(self):
        sla = self.get("sla-deepseek-contract-5-decode")
        sla["constraints"][1]["unit"] = "tokens/s"
        sla["constraints"][1]["threshold"]["value"] = -1
        errors = "\n".join(self.catalog.semantic_errors(sla))
        self.assertIn("incompatible metric unit", errors)
        self.assertIn("negative threshold", errors)

    def test_fractional_concurrency_and_disabled_cache(self):
        workload = self.get("workload-deepseek-contract-5-prefill")
        workload["arrival"]["load_points"] = [1.5]
        workload["cache"]["target_hit_ratio"] = 0.9
        errors = "\n".join(self.catalog.semantic_errors(workload))
        self.assertIn("integers", errors)
        self.assertIn("disabled prefix reuse", errors)

    def test_duplicate_devices_rejected(self):
        self.complete_synthetic_study()
        hardware = self.get("bw1000-eight-card-budget")
        hardware["resources"]["nodes"][0]["devices"][1]["device_id"] = "fixture:0"
        self.assertIn("globally unique", "\n".join(self.catalog.semantic_errors(hardware)))

    def test_fake_prefill_cannot_be_contract_acceptance(self):
        case = self.get("case-glm53-decode-4k")
        case["purpose"] = "contract"
        self.assertIn("diagnostic", "\n".join(self.catalog.semantic_errors(case)))

    def test_table_null_and_unsupported_are_distinct(self):
        table = self.get("glm53-h20-relative-summary")
        reasons = {v for row in table["rows"] for v in row["missing"].values()}
        self.assertIn("unsupported", reasons)
        self.assertIn("not_reported", reasons)
        row = next(r for r in table["rows"] if r["missing"])
        row["missing"] = {}
        self.assertIn("missing reason", "\n".join(self.catalog.semantic_errors(table)))

    def test_transcription_counts_and_distinct_contract_cases(self):
        self.assertEqual(len(self.get("glm53-prefill-matrix")["rows"]), 75)
        decode = self.get("glm53-decode-visible-series")["rows"]
        self.assertEqual(len(decode), 354)
        self.assertEqual(sum(bool(r["missing"]) for r in decode), 40)
        seven = self.get("sla-deepseek-contract-7-decode")["constraints"][1]["threshold"]["value"]
        eight = self.get("sla-deepseek-contract-8-decode")["constraints"][1]["threshold"]["value"]
        self.assertEqual((seven, eight), (33, 25))

    def test_real_study_resolves_deterministically_but_cannot_freeze(self):
        self.fixture_sources()
        first = self.catalog.resolve(self.study())
        second = self.catalog.resolve(self.study())
        self.assertEqual(first, second)
        self.assertEqual(first["state"], "draft")
        self.assertTrue(first["readiness_issues"])
        with self.assertRaisesRegex(SpecError, "cannot freeze"):
            self.catalog.resolve(self.study(), freeze=True)

    def test_resolve_rejects_malformed_input_before_following_references(self):
        self.study().pop("model_ref")
        with self.assertRaisesRegex(SpecError, "required property"):
            self.catalog.resolve(self.study())

    def test_synthetic_complete_metadata_can_freeze(self):
        study = self.complete_synthetic_study()
        snapshot = self.catalog.resolve(study, freeze=True)
        self.assertEqual(snapshot["state"], "frozen")
        self.assertEqual(snapshot["readiness_issues"], [])
        self.assertEqual(self.catalog.structural_errors(snapshot), [])
        self.assertEqual(self.catalog.snapshot_errors(snapshot, True), [])

    def test_sla_range_blocks_freeze_even_without_declared_issue(self):
        study = self.complete_synthetic_study()
        sla = self.get("sla-deepseek-contract-5-prefill")
        sla["constraints"][1]["threshold"] = dict(range=dict(min=1000, max=3000), selection="unresolved")
        with self.assertRaisesRegex(SpecError, "threshold interval"):
            self.catalog.resolve(study, freeze=True)

    def test_source_labels_cannot_substitute_for_immutable_runtime(self):
        study = self.complete_synthetic_study()
        self.get(study["runtime_ref"]["id"])["container_digest"] = "image:latest"
        with self.assertRaisesRegex(SpecError, "container digest"):
            self.catalog.resolve(study, freeze=True)

    def test_snapshot_detects_document_and_payload_tampering(self):
        self.fixture_sources()
        snapshot = self.catalog.resolve(self.study())
        self.assertEqual(self.catalog.snapshot_errors(snapshot, True), [])
        snapshot["documents"][0]["document"]["title"] = "modified"
        errors = "\n".join(self.catalog.snapshot_errors(snapshot))
        self.assertIn("content hash mismatch", errors)
        self.assertIn("document hash mismatch", errors)

    def test_rehashing_cannot_hide_invalid_frozen_state(self):
        self.fixture_sources()
        snapshot = self.catalog.resolve(self.study())
        snapshot["state"] = "frozen"
        snapshot["readiness_issues"] = []
        snapshot["content_sha256"] = digest({k: v for k, v in snapshot.items() if k != "content_sha256"})
        errors = "\n".join(self.catalog.snapshot_errors(snapshot))
        self.assertIn("computed issues", errors)
        self.assertIn("unresolved requirements", errors)

    def test_snapshot_is_independent_of_live_catalog(self):
        self.fixture_sources()
        snapshot = self.catalog.resolve(self.study())
        self.get("deepseek-v4-flash-w8a8")["title"] = "new mutable catalog title"
        self.assertEqual(self.catalog.snapshot_errors(snapshot), [])

    def test_reference_cycles_are_rejected(self):
        source = self.get("source-deepseek-project")
        source["provenance"] = [dict(source_ref=ref(source["id"]), locator="cycle")]
        with self.assertRaisesRegex(SpecError, "cyclic recipe reference"):
            self.catalog.closure(self.study())

    def test_write_never_overwrites_existing_version(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"recipe.yaml"
            write(path, self.study())
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                write(path, {"different": True})
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
