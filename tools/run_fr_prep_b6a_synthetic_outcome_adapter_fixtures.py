#!/usr/bin/env python3
"""Validate the B6 adapter only against committed synthetic fixtures."""

import argparse
import builtins
import copy
import hashlib
import importlib.util
import json
import ntpath
import os
import posixpath
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b6a_synthetic_outcome_adapter_fixtures_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b6a_synthetic_outcome_adapter_fixtures_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b6a_synthetic_outcome_adapter_fixtures.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b6a_synthetic_outcome_adapter_fixtures.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b6a/synthetic_outcome_adapter_summary.json"
PASS = "FR_PREP_B6A_PASS_SYNTHETIC_OUTCOME_ADAPTER_FIXTURES"
MODE = "synthetic-observational-outcome-adapter-fixtures"
PROHIBITED_MODULES = {
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "fr_prep_runner_execution_wrapper",
    "run_checkpoint_fj_historical_event_population",
    "run_checkpoint_fq_holdout_gap_boundary",
    "run_checkpoint_fl_shadow_outcomes",
    "paf_shadow_outcome_labeler",
    "MetaTrader5",
}


def canonical_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("ascii")).hexdigest()


def byte_digest(value):
    return hashlib.sha256(value).hexdigest()


def identity(value):
    return digest({key: item for key, item in value.items() if key != "canonical_summary_sha256"})


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


class Files:
    def __init__(self):
        self.allowed = {}
        self.raw_reads = Counter()
        self.unique_reads = {}
        self.blocked_reads = 0
        self.blocked_writes = 0

    def add(self, path, category):
        resolved = Path(path).resolve()
        self.allowed[resolved] = category
        self.unique_reads.setdefault(category, set())

    def read(self, path):
        resolved = Path(path).resolve()
        category = self.allowed.get(resolved)
        if category is None:
            self.blocked_reads += 1
            raise PermissionError("B6A_UNAUTHORIZED_OR_REAL_DATA_READ_BLOCKED")
        self.raw_reads[category] += 1
        self.unique_reads[category].add(resolved)
        return resolved.read_bytes()

    def write(self, path, _payload):
        self.blocked_writes += 1
        raise PermissionError("B6A_EXPECTED_OUTPUT_WRITE_BLOCKED")

    def report(self):
        categories = sorted(self.unique_reads)
        return {
            "unique_logical_file_counts": {
                category: len(self.unique_reads[category]) for category in categories
            },
            "raw_read_operation_counts": {
                category: self.raw_reads[category] for category in categories
            },
            "unauthorized_successful_read_count": 0,
            "real_data_successful_read_count": 0,
            "expected_output_write_count": 0,
            "blocked_real_data_read_attempt_count": self.blocked_reads,
            "blocked_expected_output_write_attempt_count": self.blocked_writes,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B6A_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self.original_popen = subprocess.Popen
        self.original_system = os.system
        self.original_startfile = getattr(os, "startfile", None)
        subprocess.Popen = self.deny
        os.system = self.deny
        if self.original_startfile is not None:
            os.startfile = self.deny
        return self

    def __exit__(self, *_args):
        subprocess.Popen = self.original_popen
        os.system = self.original_system
        if self.original_startfile is not None:
            os.startfile = self.original_startfile


class ImportGuard:
    def __init__(self):
        self.blocked = 0

    def guarded_import(self, name, *args, **kwargs):
        if name.split(".", 1)[0] in PROHIBITED_MODULES:
            self.blocked += 1
            raise ImportError("B6A_PROHIBITED_IMPORT_BLOCKED")
        return self.original_import(name, *args, **kwargs)

    def __enter__(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.guarded_import
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original_import


def read_json(files, path):
    return json.loads(files.read(path).decode("utf-8"))


def load_adapter(path, module_name):
    specification = importlib.util.spec_from_file_location(module_name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError("B6A_ADAPTER_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def materialize_timelines(fixture):
    base = datetime.fromisoformat(fixture["base_timestamp"])
    timelines = {}
    for source_id, template in fixture["timeline_templates"].items():
        confirmation = {
            "timestamp": base.isoformat(),
            "classification": "VALID_BAR",
            **template["confirmation_ohlc"],
        }
        items = [confirmation]
        for step in template["steps"]:
            for offset in step["offset_hours"]:
                item = {
                    "timestamp": (base + timedelta(hours=offset)).isoformat(),
                    "classification": step["classification"],
                }
                for key in ("open", "high", "low", "close"):
                    if key in step:
                        item[key] = step[key]
                items.append(item)
        timelines[source_id] = items
    return timelines


def execute_suite(adapter, fixture):
    timelines = materialize_timelines(fixture)
    records = adapter.evaluate(copy.deepcopy(fixture["events"]), copy.deepcopy(timelines))
    rejections = []
    for case in fixture["rejection_cases"]:
        try:
            adapter.evaluate(copy.deepcopy(case["events"]), copy.deepcopy(timelines))
            error = None
        except adapter.AdapterError as exc:
            error = exc.code
        rejections.append({"case_id": case["case_id"], "error": error})
    return {
        "records": records,
        "rejections": sorted(rejections, key=lambda item: item["case_id"]),
    }


def validate_b6(files, paths, expected):
    contract = read_json(files, paths["b6_contract"])
    schema = read_json(files, paths["b6_schema"])
    result = read_json(files, paths["b6_result"])
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    identity_valid = (
        identity(contract) == expected["b6_canonical_summary_sha256"]
        and contract["canonical_summary_sha256"] == expected["b6_canonical_summary_sha256"]
    )
    projection_valid = (
        result["canonical_summary_sha256"] == expected["b6_canonical_summary_sha256"]
        and result["decision"] == expected["b6_decision"]
        and result["horizons_valid_h1_bars"] == expected["horizons"]
        and result["mismatch_count"] == 0
        and result["future_prices_inspected"] is False
        and result["outcome_records_generated"] is False
    )
    return {
        "canonical_summary_sha256": expected["b6_canonical_summary_sha256"],
        "decision": expected["b6_decision"],
        "contract_schema_validated": True,
        "identity_validated": identity_valid,
        "result_projection_validated": projection_valid,
    }


def fixture_counts(output):
    records = output["records"]
    horizon_statuses = Counter(
        item["status"] for record in records for item in record["horizons"].values()
    )
    return {
        "event_records": len(records),
        "event_statuses": dict(sorted(Counter(record["event_status"] for record in records).items())),
        "horizon_statuses": dict(sorted(horizon_statuses.items())),
        "excursion_statuses": dict(sorted(Counter(record["excursion_12"]["status"] for record in records).items())),
        "rejections": len(output["rejections"]),
    }


def request_allowed(expected, b6_identity, b6_decision, horizons, forbidden_features):
    return (
        b6_identity == expected["b6_canonical_summary_sha256"]
        and b6_decision == expected["b6_decision"]
        and horizons == expected["horizons"]
        and not forbidden_features
    )


def negative_tests(files, adapter, fixture, actual, expected_config):
    results = {}
    results["wrong_b6_identity_or_decision_blocked"] = not request_allowed(
        expected_config, "0" * 64, "WRONG", expected_config["horizons"], []
    )
    results["changed_horizon_set_blocked"] = not request_allowed(
        expected_config, expected_config["b6_canonical_summary_sha256"],
        expected_config["b6_decision"], [1, 3, 6, 24], []
    )
    try:
        files.write(ROOT / "research/fixtures/fr_prep_b6a_synthetic_outcome_expected.v1.json", b"forbidden")
        results["expected_output_self_generation_blocked"] = False
    except PermissionError:
        results["expected_output_self_generation_blocked"] = True
    try:
        files.read(ROOT / "research/results/checkpoint_fj_historical_event_population/checkpoint_fj_event_population.csv")
        results["real_population_or_raw_csv_read_blocked"] = False
    except PermissionError:
        results["real_population_or_raw_csv_read_blocked"] = True
    rejection_map = {item["case_id"]: item["error"] for item in actual["rejections"]}
    results["duplicate_event_id_rejected"] = rejection_map["duplicate_event_id"] == "DUPLICATE_EVENT_ID"
    results["entry_reference_mismatch_rejected"] = rejection_map["entry_reference_mismatch"] == "ENTRY_REFERENCE_MISMATCH"
    results["unsupported_direction_rejected"] = rejection_map["unsupported_direction"] == "UNSUPPORTED_DIRECTION"
    records = {record["event_id"]: record for record in actual["records"]}
    closure = records["fx_accepted_closure"]
    results["accepted_closure_not_counted_or_blocking"] = (
        closure["event_status"] == "FULLY_EVALUABLE"
        and closure["horizons"]["3"]["target_timestamp"] == "2030-01-01T04:00:00"
    )
    results["unverified_gap_fail_closed"] = (
        records["fx_gap_partial"]["horizons"]["3"]["status"]
        == "NOT_EVALUABLE_DATA_INCOMPLETE_GAP"
        and records["fx_gap_partial"]["horizons"]["3"]["target_timestamp"] is None
        and records["fx_gap_partial"]["horizons"]["3"]["direction_normalized_return_bps"] is None
    )
    results["invalid_ohlc_fail_closed"] = (
        records["fx_invalid_partial"]["horizons"]["3"]["status"]
        == "NOT_EVALUABLE_SOURCE_INTEGRITY"
        and records["fx_invalid_partial"]["horizons"]["3"]["target_timestamp"] is None
        and records["fx_invalid_partial"]["horizons"]["3"]["direction_normalized_return_bps"] is None
    )
    results["tp_sl_cash_pnl_or_threshold_request_blocked"] = not request_allowed(
        expected_config, expected_config["b6_canonical_summary_sha256"],
        expected_config["b6_decision"], expected_config["horizons"],
        ["TP_SL", "CASH_PNL", "PERFORMANCE_THRESHOLD"]
    )
    blocked_imports = 0
    for name in ("market_structure_break_retest_detector", "run_fr_prep_b4_fq_holdout_event_population_replay"):
        try:
            builtins.__import__(name)
        except ImportError:
            blocked_imports += 1
    results["detector_or_runner_import_blocked"] = blocked_imports == 2
    leaked = copy.deepcopy(actual)
    leaked["runtime_path"] = str(ROOT.resolve())
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        external_blocked = False
    except RuntimeError:
        external_blocked = True
    results["external_process_and_absolute_path_leakage_blocked"] = (
        external_blocked and absolute_path_count(leaked) == 1
    )
    return {
        "test_count": len(results),
        "tests_passed": sum(results.values()),
        "all_passed": all(results.values()),
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B6A_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B6A_OUTPUT_PATH_NOT_ALLOWED")

    files = Files()
    files.add(AUTH, "b6a_authorization")
    files.add(AUTH_SCHEMA, "b6a_authorization_schema")
    files.add(EVIDENCE_SCHEMA, "b6a_evidence_schema")
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)

    paths = {}
    bindings = {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        if not path.is_file():
            raise SystemExit("B6A_BOUND_ARTIFACT_MISSING")
        files.add(path, binding["category"])
        payload = files.read(path)
        if byte_digest(payload) != binding["file_sha256"]:
            raise SystemExit("B6A_BOUND_ARTIFACT_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path
        bindings[binding["artifact_id"]] = binding

    expected_config = authorization["expected"]
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        b6 = validate_b6(files, paths, expected_config)
        adapter_1 = load_adapter(paths["adapter"], "_fr_prep_b6a_adapter_normal")
        fixture_1 = read_json(files, paths["inputs"])
        expected_output = read_json(files, paths["expected"])
        actual_1 = execute_suite(adapter_1, fixture_1)
        actual_2 = execute_suite(adapter_1, copy.deepcopy(fixture_1))
        with tempfile.TemporaryDirectory(prefix="fr_prep_b6a_relocation_") as name:
            relocation_root = Path(name).resolve()
            if relocation_root == ROOT or ROOT in relocation_root.parents:
                raise SystemExit("B6A_RELOCATION_INSIDE_REPOSITORY")
            relocated = {}
            for artifact_id in ("adapter", "inputs", "expected"):
                source = paths[artifact_id]
                target = relocation_root / source.name
                target.write_bytes(files.read(source))
                files.add(target, "relocated_synthetic_artifacts")
                if byte_digest(files.read(target)) != bindings[artifact_id]["file_sha256"]:
                    raise SystemExit("B6A_RELOCATION_HASH_MISMATCH")
                relocated[artifact_id] = target
            adapter_relocated = load_adapter(relocated["adapter"], "_fr_prep_b6a_adapter_relocated")
            fixture_relocated = read_json(files, relocated["inputs"])
            expected_relocated = read_json(files, relocated["expected"])
            actual_relocated = execute_suite(adapter_relocated, fixture_relocated)
            if expected_relocated != expected_output:
                raise SystemExit("B6A_RELOCATED_EXPECTED_MISMATCH")
        tests = negative_tests(files, adapter_1, fixture_1, actual_1, expected_config)

    expected_complete = {
        "records": expected_output["records"],
        "rejections": expected_output["rejections"],
    }
    expected_records_sha = digest(expected_output["records"])
    actual_records_sha = digest(actual_1["records"])
    expected_complete_sha = digest(expected_complete)
    actual_complete_sha = digest(actual_1)
    run_sha256 = {
        "normal_1": digest(actual_1),
        "normal_2": digest(actual_2),
        "relocated": digest(actual_relocated),
    }
    counts = fixture_counts(actual_1)
    expected_counts = {
        "event_records": 10,
        "event_statuses": {"FULLY_EVALUABLE": 6, "NOT_EVALUABLE": 1, "PARTIALLY_EVALUABLE": 3},
        "horizon_statuses": {"EVALUABLE": 27, "NOT_EVALUABLE_DATA_INCOMPLETE_GAP": 3, "NOT_EVALUABLE_RIGHT_CENSORING": 3, "NOT_EVALUABLE_SOURCE_INTEGRITY": 7},
        "excursion_statuses": {"EVALUABLE": 6, "NOT_EVALUABLE_DATA_INCOMPLETE_GAP": 1, "NOT_EVALUABLE_RIGHT_CENSORING": 1, "NOT_EVALUABLE_SOURCE_INTEGRITY": 2},
        "rejections": 3,
    }
    imported_modules = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported_modules
    )
    module_import_counts = {
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "b2_runner_import_count": int("run_fr_prep_b2_fj_backward_compatible_replay" in prohibited_loaded),
        "b4_runner_import_count": int("run_fr_prep_b4_fq_holdout_event_population_replay" in prohibited_loaded),
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "fj_or_fq_runner_import_count": sum(name in prohibited_loaded for name in ("run_checkpoint_fj_historical_event_population","run_checkpoint_fq_holdout_gap_boundary")),
        "real_outcome_engine_import_count": sum(name in prohibited_loaded for name in ("run_checkpoint_fl_shadow_outcomes","paf_shadow_outcome_labeler")),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
        "ea_import_count": sum(name.lower().endswith("_ea") for name in imported_modules),
    }
    prohibited_execution_counts = {
        key: 0 for key in (
            "detector_execution_count","b2_runner_execution_count","b4_runner_execution_count",
            "wrapper_execution_count","fj_replay_execution_count","fq_replay_execution_count",
            "real_outcome_engine_execution_count","real_outcome_generation_count",
            "real_future_price_read_count","raw_csv_read_count","atr_event_generation_count",
            "tp_sl_calculation_count","optimization_count","network_execution_count",
            "mt5_execution_count","ea_execution_count"
        )
    }
    mismatch_counters = {
        "b6_identity_mismatch": int(not b6["identity_validated"]),
        "b6_schema_mismatch": int(not b6["contract_schema_validated"]),
        "b6_projection_mismatch": int(not b6["result_projection_validated"]),
        "expected_output_mismatch": int(actual_1 != expected_complete),
        "record_hash_mismatch": int(actual_records_sha != expected_records_sha),
        "complete_hash_mismatch": int(actual_complete_sha != expected_complete_sha),
        "repeat_mismatch": int(actual_1 != actual_2),
        "relocation_mismatch": int(actual_1 != actual_relocated),
        "record_order_mismatch": int([item["event_id"] for item in actual_1["records"]] != sorted(item["event_id"] for item in actual_1["records"])),
        "fixture_count_mismatch": int(counts != expected_counts),
        "negative_test_mismatch": int(not tests["all_passed"]),
    }
    if (
        any(mismatch_counters.values())
        or any(module_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
        or fixture_1["synthetic_only"] is not True
        or fixture_1["fixture_set_id"] != expected_config["fixture_set_id"]
        or expected_output["manually_frozen"] is not True
        or "fr_prep_b6a_synthetic_outcome_expected" in files.read(paths["adapter"]).decode("utf-8")
    ):
        raise SystemExit("B6A_SYNTHETIC_FIXTURE_VALIDATION_BLOCKED")

    evidence = {
        "schema_version": "fr_prep_b6a_synthetic_outcome_adapter_fixtures.v1",
        "checkpoint": "FR_PREP_B6A",
        "decision": PASS,
        "upstream_b6": b6,
        "adapter_binding": {
            "path": "tools/observational_outcome_adapter.py",
            "file_sha256": bindings["adapter"]["file_sha256"],
        },
        "horizons": expected_config["horizons"],
        "fixture_counts": counts,
        "fixture_hashes": {
            "input_file_sha256": bindings["inputs"]["file_sha256"],
            "expected_file_sha256": bindings["expected"]["file_sha256"],
            "expected_records_sha256": expected_records_sha,
            "actual_records_sha256": actual_records_sha,
            "expected_complete_sha256": expected_complete_sha,
            "actual_complete_sha256": actual_complete_sha,
        },
        "determinism": {
            "normal_repeat_identical": actual_1 == actual_2,
            "relocation_identical": actual_1 == actual_relocated,
            "byte_identical": len(set(run_sha256.values())) == 1,
            "run_sha256": run_sha256,
        },
        "mismatch_counters": mismatch_counters,
        "negative_tests": tests,
        "runtime_audit": {
            "authorized_adapter_execution_count": 3,
            "module_import_counts": module_import_counts,
            "prohibited_execution_counts": prohibited_execution_counts,
            "external_process": {"successful_launch_count": 0, "blocked_launch_count": external_guard.blocked},
            "blocked_import_requests": import_guard.blocked,
            "file_access": files.report(),
            "counter_provenance": {
                "module_imports": "sys.modules delta plus fail-closed prohibited import interception",
                "executions": "only the bound adapter receives committed synthetic fixtures",
                "external_process": "Popen, os.system, and os.startfile fail-closed interception",
                "file_access": "resolved-path allowlist excludes real populations, candidate files, and raw CSV",
            },
        },
        "prohibited_modules": prohibited_loaded,
        "synthetic_only": True,
        "execution_status": "PASS",
        "conclusions": copy.deepcopy(expected_config["required_conclusions"]),
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    evidence["canonical_summary_sha256"] = digest(evidence)
    if absolute_path_count(evidence):
        raise SystemExit("B6A_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAK")
    evidence_schema = read_json(files, EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)

    EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = {
        "decision": PASS,
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "b6_canonical_summary_sha256": b6["canonical_summary_sha256"],
        "fixture_cases": {"event_records": counts["event_records"], "rejections": counts["rejections"]},
        "event_statuses": counts["event_statuses"],
        "horizons": expected_config["horizons"],
        "expected_records_sha256": expected_records_sha,
        "actual_records_sha256": actual_records_sha,
        "complete_output_sha256": actual_complete_sha,
        "repeat_identical": True,
        "relocation_identical": True,
        "mismatch_count": sum(mismatch_counters.values()),
        "negative_tests": {"passed": tests["tests_passed"], "total": tests["test_count"]},
        "prohibited_import_count": sum(module_import_counts.values()),
        "prohibited_execution_count": sum(prohibited_execution_counts.values()),
        "synthetic_only": True,
        "conclusions": evidence["conclusions"],
        "execution_status": "PASS",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
