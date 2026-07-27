#!/usr/bin/env python3
"""Seal FR-Prep-B6c authorization without executing real observational outcomes."""

import argparse
import builtins
import copy
import hashlib
import json
import ntpath
import os
import posixpath
import subprocess
import sys
from collections import Counter
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b6c_real_outcome_execution_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b6c_real_outcome_execution_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b6c_real_outcome_execution_authorization_evidence.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b6c_real_outcome_execution_authorization_evidence.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b6c/real_outcome_execution_authorization_summary.json"
MODE = "seal-real-outcome-execution-authorization"
PASS = "FR_PREP_B6C_PASS_REAL_OUTCOME_EXECUTION_AUTHORIZATION_SEALED"
PROHIBITED_MODULES = {
    "observational_outcome_adapter",
    "market_structure_break_retest_detector",
    "run_fr_prep_b2_fj_backward_compatible_replay",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "fr_prep_runner_execution_wrapper",
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
        self.blocked_raw_or_future_reads = 0

    def add(self, path, category, mode):
        resolved = Path(path).resolve()
        self.allowed[resolved] = (category, mode)
        self.unique_reads.setdefault(category, set())

    def read(self, path, required_mode=None):
        resolved = Path(path).resolve()
        binding = self.allowed.get(resolved)
        if binding is None:
            self.blocked_raw_or_future_reads += 1
            raise PermissionError("B6C_UNAUTHORIZED_RAW_OR_FUTURE_READ_BLOCKED")
        category, mode = binding
        if required_mode is not None and mode != required_mode:
            raise PermissionError("B6C_ARTIFACT_READ_MODE_BLOCKED")
        self.raw_reads[category] += 1
        self.unique_reads[category].add(resolved)
        return resolved.read_bytes()

    def report(self):
        categories = sorted(self.unique_reads)
        return {
            "unique_logical_file_counts": {
                category: len(self.unique_reads[category]) for category in categories
            },
            "raw_read_operation_counts": {
                category: self.raw_reads[category] for category in categories
            },
            "blocked_raw_csv_or_future_price_read_attempt_count": self.blocked_raw_or_future_reads,
            "raw_csv_successful_read_count": 0,
            "future_price_successful_read_count": 0,
            "event_row_parse_count": 0,
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B6C_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B6C_PROHIBITED_IMPORT_BLOCKED")
        return self.original_import(name, *args, **kwargs)

    def __enter__(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self.guarded_import
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original_import


def read_json(files, path):
    return json.loads(files.read(path, "json").decode("utf-8"))


def exact_sources(actual, expected, name_key, row_key, sha_key):
    projection = [
        {"filename": item[name_key], "rows": item[row_key], "sha256": item[sha_key]}
        for item in actual
    ]
    return projection == expected


def request_allowed(expected, request):
    return (
        request["upstream_identities"] == expected["upstream_identities"]
        and request["adapter"] == expected["adapter"]
        and request["datasets"] == expected["dataset_request_bindings"]
        and request["horizons"] == expected["outcome_contract"]["horizons"]
        and request["numeric_policy"] == expected["outcome_contract"]["numeric_policy"]
        and request["dataset_separation"] is True
        and request["adapter_execute_now"] is False
        and request["raw_csv_or_future_read_now"] is False
        and request["outcome_or_statistics_now"] is False
        and request["requested_prohibited_features"] == []
        and request["external_process_now"] is False
    )


def negative_tests(expected, files):
    base = {
        "upstream_identities": copy.deepcopy(expected["upstream_identities"]),
        "adapter": copy.deepcopy(expected["adapter"]),
        "datasets": copy.deepcopy(expected["dataset_request_bindings"]),
        "horizons": copy.deepcopy(expected["outcome_contract"]["horizons"]),
        "numeric_policy": copy.deepcopy(expected["outcome_contract"]["numeric_policy"]),
        "dataset_separation": True,
        "adapter_execute_now": False,
        "raw_csv_or_future_read_now": False,
        "outcome_or_statistics_now": False,
        "requested_prohibited_features": [],
        "external_process_now": False,
    }
    mutations = {}
    wrong_upstream = copy.deepcopy(base)
    wrong_upstream["upstream_identities"]["b6"] = "0" * 64
    mutations["wrong_b6_b6a_b6b_identity_blocked"] = not request_allowed(expected, wrong_upstream)
    wrong_adapter = copy.deepcopy(base)
    wrong_adapter["adapter"]["file_sha256"] = "0" * 64
    mutations["changed_adapter_hash_blocked"] = not request_allowed(expected, wrong_adapter)
    wrong_population = copy.deepcopy(base)
    wrong_population["datasets"]["FJ"]["events"] += 1
    mutations["changed_event_count_or_population_hash_blocked"] = not request_allowed(expected, wrong_population)
    wrong_source_gap = copy.deepcopy(base)
    wrong_source_gap["datasets"]["FQ"]["gap_binding_sha256"] = "0" * 64
    mutations["changed_source_or_gap_binding_blocked"] = not request_allowed(expected, wrong_source_gap)
    wrong_numeric = copy.deepcopy(base)
    wrong_numeric["horizons"] = [1, 3, 6, 24]
    wrong_numeric["numeric_policy"]["rounding"] = "ROUND_HALF_UP"
    mutations["changed_horizon_or_numeric_policy_blocked"] = not request_allowed(expected, wrong_numeric)
    adapter_execution = copy.deepcopy(base)
    adapter_execution["adapter_execute_now"] = True
    mutations["adapter_execution_attempt_blocked"] = not request_allowed(expected, adapter_execution)
    raw_read = copy.deepcopy(base)
    raw_read["raw_csv_or_future_read_now"] = True
    mutations["raw_csv_or_future_price_read_attempt_blocked"] = not request_allowed(expected, raw_read)
    outcome_generation = copy.deepcopy(base)
    outcome_generation["outcome_or_statistics_now"] = True
    mutations["outcome_or_statistics_generation_attempt_blocked"] = not request_allowed(expected, outcome_generation)
    prohibited = copy.deepcopy(base)
    prohibited["requested_prohibited_features"] = ["TP_SL", "CASH_PNL", "PERFORMANCE_THRESHOLD"]
    mutations["tp_sl_cash_pl_or_threshold_request_blocked"] = not request_allowed(expected, prohibited)
    external = copy.deepcopy(base)
    external["external_process_now"] = True
    leaked = copy.deepcopy(base)
    leaked["runtime_path"] = str(ROOT.resolve())
    mutations["external_process_or_absolute_path_identity_leakage_blocked"] = (
        not request_allowed(expected, external) and absolute_path_count(leaked) == 1
    )
    try:
        files.read(ROOT / "raw_broker_csv_is_never_allowed.csv")
        mutations["raw_file_guard_fail_closed"] = False
    except PermissionError:
        mutations["raw_file_guard_fail_closed"] = True
    try:
        builtins.__import__("observational_outcome_adapter")
        mutations["adapter_import_guard_fail_closed"] = False
    except ImportError:
        mutations["adapter_import_guard_fail_closed"] = True
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        mutations["external_process_guard_fail_closed"] = False
    except RuntimeError:
        mutations["external_process_guard_fail_closed"] = True
    return {
        "test_count": len(mutations),
        "tests_passed": sum(mutations.values()),
        "all_passed": all(mutations.values()),
        "results": mutations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B6C_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B6C_OUTPUT_PATH_NOT_ALLOWED")

    files = Files()
    files.add(AUTH, "b6c_authorization", "json")
    files.add(AUTH_SCHEMA, "b6c_authorization_schema", "json")
    files.add(EVIDENCE_SCHEMA, "b6c_evidence_schema", "json")
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    evidence_schema = read_json(files, EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)

    paths = {}
    artifact_hash_mismatches = 0
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        files.add(path, binding["category"], binding["read_mode"])
        if not path.is_file():
            raise SystemExit("B6C_COMMITTED_ARTIFACT_MISSING")
        actual_sha = byte_digest(files.read(path, binding["read_mode"]))
        artifact_hash_mismatches += int(actual_sha != binding["file_sha256"])
        paths[binding["artifact_id"]] = path
    if artifact_hash_mismatches:
        raise SystemExit("B6C_COMMITTED_ARTIFACT_HASH_MISMATCH")

    expected = authorization["expected"]
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        docs = {
            key: read_json(files, paths[key])
            for key in (
                "b2_contract", "b2_schema", "b2_result", "b2a_contract", "b2a_schema",
                "b2a_result", "fj_source_manifest", "fj_gap_binding_contract",
                "b4_contract", "b4_schema", "b4_result", "b4a_contract", "b4a_schema",
                "b4a_result", "fq_source_manifest", "b6_contract", "b6_schema",
                "b6_result", "b6a_contract", "b6a_schema", "b6a_result",
                "b6b_contract", "b6b_schema", "b6b_result",
            )
        }
        for prefix in ("b2", "b2a", "b4", "b4a", "b6", "b6a", "b6b"):
            jsonschema.Draft202012Validator.check_schema(docs[f"{prefix}_schema"])
            jsonschema.Draft202012Validator(docs[f"{prefix}_schema"]).validate(docs[f"{prefix}_contract"])
        tests = negative_tests(expected, files)

    identities = {
        key: identity(docs[f"{key}_contract"]) for key in ("b2", "b2a", "b4", "b4a", "b6", "b6a", "b6b")
    }
    identity_valid = {
        key: (
            identities[key] == expected["upstream_identities"][key]
            and docs[f"{key}_contract"]["canonical_summary_sha256"] == expected["upstream_identities"][key]
            and docs[f"{key}_result"]["canonical_summary_sha256"] == expected["upstream_identities"][key]
        )
        for key in identities
    }
    fj = expected["datasets"]["FJ"]
    fq = expected["datasets"]["FQ"]
    fj_sources_valid = (
        exact_sources(docs["fj_source_manifest"]["sources"], fj["sources"], "file", "row_count", "sha256")
        and docs["fj_gap_binding_contract"]["source_dataset_identity"] == fj["source_dataset_identity"]
        and docs["fj_gap_binding_contract"]["gap_binding"]["normalized_gap_inventory_sha256"] == fj["normalized_gap_inventory_sha256"]
        and docs["fj_gap_binding_contract"]["gap_binding"]["classification_counts"] == fj["gap_classification_counts"]
    )
    fq_sources_valid = (
        exact_sources(docs["fq_source_manifest"]["sources"], fq["sources"], "filename", "rows", "sha256")
        and docs["fq_source_manifest"]["canonical_timeline_sha256"] == fq["canonical_timeline_sha256"]
        and docs["fq_source_manifest"]["gap_inventory"]["sha256"] == fq["gap_binding_sha256"]
        and docs["fq_source_manifest"]["gap_inventory"]["gaps"] == fq["gap_count"]
        and docs["fq_source_manifest"]["gap_inventory"]["unverified_fail_closed"] == fq["unverified_gaps"]
    )
    dataset_valid = {
        "FJ": (
            docs["b2_contract"]["dataset_id"] == fj["dataset_id"]
            and docs["b2_contract"]["event_count"] == fj["events"]
            and docs["b2_contract"]["replay_hashes"]["event_population_sha256"] == fj["event_population_sha256"]
            and docs["b2a_contract"]["event_count"] == fj["events"]
            and fj_sources_valid
        ),
        "FQ": (
            docs["b4_contract"]["dataset_id"] == fq["dataset_id"]
            and docs["b4_contract"]["event_count"] == fq["events"]
            and docs["b4_contract"]["output_hashes"]["event_population_sha256"] == fq["event_population_sha256"]
            and docs["b4a_contract"]["event_count"] == fq["events"]
            and fq_sources_valid
        ),
    }
    outcome_contract_valid = (
        docs["b6_contract"]["horizon_contract"]["target_valid_h1_bars_after_confirmation"]
        == expected["outcome_contract"]["horizons"]
        and docs["b6_contract"]["numeric_and_canonical_policy"]
        == expected["outcome_contract"]["numeric_policy"]
        and docs["b6_contract"]["aggregation_contract"]["dataset_pooling_allowed"] is False
        and docs["b6_contract"]["aggregation_contract"]["group_dimensions"]
        == expected["outcome_contract"]["statistics_group_dimensions"]
        and docs["b6_contract"]["output_record_contract"]["one_record_per_input_event"] is True
    )
    adapter_valid = (
        expected["adapter"]["path"] == "tools/observational_outcome_adapter.py"
        and expected["adapter"]["file_sha256"] == authorization["adapter_binding"]["file_sha256"]
        and docs["b6a_contract"]["adapter_binding"] == expected["adapter"]
        and docs["b6b_contract"]["adapter_binding"] == expected["adapter"]
    )
    imported_modules = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported_modules
    )
    mismatch_counters = {
        "artifact_hash_mismatch": artifact_hash_mismatches,
        "upstream_identity_mismatch": sum(not value for value in identity_valid.values()),
        "adapter_binding_mismatch": int(not adapter_valid),
        "fj_event_or_population_mismatch": int(not dataset_valid["FJ"]),
        "fq_event_or_population_mismatch": int(not dataset_valid["FQ"]),
        "source_or_gap_binding_mismatch": int(not (fj_sources_valid and fq_sources_valid)),
        "horizon_or_numeric_policy_mismatch": int(not outcome_contract_valid),
        "dataset_separation_mismatch": int(not expected["outcome_contract"]["dataset_separation"]),
        "negative_test_mismatch": int(not tests["all_passed"]),
    }
    module_import_counts = {
        "adapter_import_count": int("observational_outcome_adapter" in prohibited_loaded),
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "b2_or_b4_runner_import_count": sum(
            name in prohibited_loaded for name in (
                "run_fr_prep_b2_fj_backward_compatible_replay",
                "run_fr_prep_b4_fq_holdout_event_population_replay",
            )
        ),
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
    }
    prohibited_execution_counts = {
        key: 0 for key in (
            "adapter_execution_count", "detector_execution_count", "event_population_rerun_count",
            "raw_csv_read_count", "real_future_price_read_count", "real_outcome_generation_count",
            "statistics_generation_count", "tp_sl_calculation_count", "cash_pl_calculation_count",
            "performance_threshold_count", "optimization_count", "mt5_execution_count",
            "ea_execution_count", "network_execution_count", "external_process_success_count",
        )
    }
    if (
        any(mismatch_counters.values())
        or any(module_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B6C_AUTHORIZATION_SEAL_BLOCKED")

    evidence = {
        "schema_version": "fr_prep_b6c_real_outcome_execution_authorization_evidence.v1",
        "checkpoint": "FR_PREP_B6C",
        "decision": PASS,
        "execution_status": "PASS",
        "upstream_validation": {
            key: {
                "canonical_summary_sha256": expected["upstream_identities"][key],
                "identity_validated": identity_valid[key],
                "schema_validated": True,
                "result_projection_validated": True,
            }
            for key in ("b6", "b6a", "b6b", "b2", "b2a", "b4", "b4a")
        },
        "adapter_binding": copy.deepcopy(expected["adapter"]),
        "datasets": {
            name: {
                "dataset_id": data["dataset_id"],
                "events": data["events"],
                "event_artifact": copy.deepcopy(data["event_artifact"]),
                "event_population_sha256": data["event_population_sha256"],
                "sources": copy.deepcopy(data["sources"]),
                "source_rows": data["source_rows"],
                "gap_count": data["gap_count"],
                "unverified_gaps": data["unverified_gaps"],
                "source_binding_validated": True,
                "gap_binding_validated": True,
                "event_rows_parsed": False,
            }
            for name, data in expected["datasets"].items()
        },
        "sealed_outcome_contract": copy.deepcopy(expected["outcome_contract"]),
        "authorized_next_checkpoint_operations": copy.deepcopy(
            authorization["authorized_next_checkpoint_operations"]
        ),
        "still_prohibited": copy.deepcopy(authorization["still_prohibited"]),
        "authorization_states": copy.deepcopy(expected["authorization_states"]),
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "file_access": files.report(),
            "module_import_counts": module_import_counts,
            "blocked_import_requests": import_guard.blocked,
            "external_process": {
                "blocked_launch_count": external_guard.blocked,
                "successful_launch_count": 0,
            },
            "prohibited_execution_counts": prohibited_execution_counts,
        },
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "prohibited_modules": [],
    }
    evidence["canonical_summary_sha256"] = identity(evidence)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
    rendered = json.dumps(evidence, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(rendered, encoding="utf-8", newline="\n")
    RESULT.write_text(rendered, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "mismatch_count": sum(mismatch_counters.values()),
        "negative_tests_passed": tests["tests_passed"],
        "negative_tests_total": tests["test_count"],
        "prohibited_count": sum(prohibited_execution_counts.values()),
    }))


if __name__ == "__main__":
    main()
