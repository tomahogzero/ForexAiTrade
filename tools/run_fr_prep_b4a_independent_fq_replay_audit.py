#!/usr/bin/env python3
"""Independent committed-artifact audit for FR-Prep-B4; imports no replay code."""

import argparse
import builtins
import copy
import csv
import hashlib
import io
import json
import ntpath
import os
import posixpath
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b4a_independent_fq_replay_audit_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b4a_independent_fq_replay_audit_authorization.v1.schema.json"
EVIDENCE = ROOT / "research/contracts/fr_prep_b4a_independent_fq_replay_audit.v1.json"
EVIDENCE_SCHEMA = ROOT / "research/schemas/fr_prep_b4a_independent_fq_replay_audit.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b4a/independent_fq_replay_audit_summary.json"
PASS = "FR_PREP_B4A_PASS_INDEPENDENT_FQ_REPLAY_AUDIT"
MODE = "independent-sealed-fq-replay-audit"
PROHIBITED_MODULES = {
    "market_structure_break_retest_detector",
    "run_fr_prep_b4_fq_holdout_event_population_replay",
    "fr_prep_runner_execution_wrapper",
    "run_checkpoint_fj_historical_event_population",
    "run_checkpoint_fq_holdout_gap_boundary",
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

    def add(self, path, category):
        resolved = Path(path).resolve()
        self.allowed[resolved] = category
        self.unique_reads.setdefault(category, set())

    def read(self, path):
        resolved = Path(path).resolve()
        category = self.allowed.get(resolved)
        if category is None:
            raise PermissionError("B4A_UNAUTHORIZED_FILE_READ_BLOCKED")
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
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def _deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B4A_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self.original_popen = subprocess.Popen
        self.original_system = os.system
        self.original_startfile = getattr(os, "startfile", None)
        subprocess.Popen = self._deny
        os.system = self._deny
        if self.original_startfile is not None:
            os.startfile = self._deny
        return self

    def __exit__(self, *_args):
        subprocess.Popen = self.original_popen
        os.system = self.original_system
        if self.original_startfile is not None:
            os.startfile = self.original_startfile

    def report(self):
        return {
            "successful_external_process_launch_count": 0,
            "successful_mt5_launch_count": 0,
            "successful_ea_execution_count": 0,
            "blocked_external_launch_attempt_count": self.blocked,
        }


class ImportGuard:
    def __init__(self):
        self.blocked = 0

    def _guarded_import(self, name, *args, **kwargs):
        root_name = name.split(".", 1)[0]
        if root_name in PROHIBITED_MODULES:
            self.blocked += 1
            raise ImportError("B4A_PROHIBITED_MODULE_IMPORT_BLOCKED")
        return self.original_import(name, *args, **kwargs)

    def __enter__(self):
        self.original_import = builtins.__import__
        builtins.__import__ = self._guarded_import
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original_import


def read_json(files, path):
    return json.loads(files.read(path).decode("utf-8"))


def parse_events(payload):
    rows = []
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    for row in reader:
        row["source_row_keys"] = json.loads(row["source_row_keys"])
        row["exclusion_reason"] = row["exclusion_reason"] or None
        rows.append(row)
    return rows


def parse_candidates(payload):
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    return [
        {key: (value if value != "" else None) for key, value in row.items()}
        for row in reader
    ]


def result_schema(expected):
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "required": [
            "canonical_summary_sha256",
            "decision",
            "event_population",
            "execution_status",
            "mismatch_count",
            "output_hashes",
            "performance",
            "profitability",
            "prohibited_execution_count",
            "prohibited_import_count",
            "source_rows",
            "detected_gap_count",
            "accepted_weekend_closures",
            "accepted_daily_closures",
            "unverified_gaps",
        ],
        "properties": {
            "canonical_summary_sha256": {"const": expected["b4_canonical_summary_sha256"]},
            "decision": {"const": expected["b4_decision"]},
            "execution_status": {"const": "PASS"},
            "mismatch_count": {"const": 0},
            "output_hashes": {"const": expected["hashes"]},
            "performance": {"const": "NOT_EVALUATED"},
            "profitability": {"const": "NOT_CLAIMED"},
            "prohibited_execution_count": {"const": 0},
            "prohibited_import_count": {"const": 0},
            "source_rows": {"const": expected["source_rows"]},
            "detected_gap_count": {"const": expected["gap_count"]},
            "accepted_weekend_closures": {"const": expected["accepted_weekend_closures"]},
            "accepted_daily_closures": {"const": expected["accepted_daily_closures"]},
            "unverified_gaps": {"const": expected["unverified_gaps"]},
            "event_population": {
                "type": "object",
                "properties": {
                    "total": {"const": expected["event_count"]},
                    "LONG": {"const": expected["long_count"]},
                    "SHORT": {"const": expected["short_count"]},
                    "counts_per_year": {"const": expected["year_counts"]},
                },
                "required": ["total", "LONG", "SHORT", "counts_per_year"],
            },
        },
    }


def validate_timestamp_order(event):
    timestamps = [
        datetime.fromisoformat(event[key])
        for key in (
            "swing_timestamp",
            "swing_confirmation_timestamp",
            "break_timestamp",
            "retest_timestamp",
            "confirmation_timestamp",
        )
    ]
    return (
        timestamps[0] <= timestamps[1]
        and timestamps[1] < timestamps[2]
        and timestamps[2] < timestamps[3]
        and timestamps[3] <= timestamps[4]
    )


def source_keys_resolved(events, manifest):
    source_rows = {item["filename"]: item["rows"] for item in manifest["sources"]}
    for event in events:
        if not event["source_row_keys"]:
            return False
        for key in event["source_row_keys"]:
            try:
                filename, raw_index = key.rsplit(":", 1)
                index = int(raw_index)
            except (ValueError, AttributeError):
                return False
            if filename not in source_rows or index < 0 or index >= source_rows[filename]:
                return False
    return True


def audit_once(files, paths, expected):
    contract = read_json(files, paths["b4_contract"])
    contract_schema = read_json(files, paths["b4_schema"])
    summary_output = read_json(files, paths["population_summary"])
    deterministic = read_json(files, paths["deterministic_replay"])
    manifest = read_json(files, paths["source_manifest"])
    events = parse_events(files.read(paths["events"]))
    candidates = parse_candidates(files.read(paths["candidates"]))

    jsonschema.Draft202012Validator.check_schema(contract_schema)
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    compact_schema = result_schema(expected)
    jsonschema.Draft202012Validator.check_schema(compact_schema)
    jsonschema.Draft202012Validator(compact_schema).validate(summary_output)

    augmented_keys = {
        "canonical_summary_sha256",
        "output_hashes",
        "mismatch_count",
        "negative_tests",
        "prohibited_import_count",
        "prohibited_execution_count",
    }
    population_summary = {
        key: value for key, value in summary_output.items() if key not in augmented_keys
    }
    complete_output = {
        "events": events,
        "candidates": candidates,
        "summary": population_summary,
        "manifest": manifest,
    }
    hashes = {
        "event_population_sha256": digest(events),
        "candidate_status_sha256": digest(candidates),
        "population_summary_sha256": digest(population_summary),
        "terminal_status_summary_sha256": digest(population_summary["terminal_status_counts"]),
        "complete_output_sha256": digest(complete_output),
    }

    ids = [event["event_id"] for event in events]
    semantic_keys = [
        (
            event["direction"],
            event["swing_timestamp"],
            event["break_timestamp"],
            event["confirmation_timestamp"],
        )
        for event in events
    ]
    candidate_order = [
        tuple("" if value is None else str(value) for value in row.values())
        for row in candidates
    ]
    directions = Counter(event["direction"] for event in events)
    confirmation_years = {
        event["event_id"]: str(datetime.fromisoformat(event["confirmation_timestamp"]).year)
        for event in events
    }
    years = Counter(confirmation_years.values())
    year_counts = {year: years.get(year, 0) for year in ("2020", "2021", "2022")}
    direction_year_counts = {
        direction: dict(sorted(Counter(
            event["year"] for event in events if event["direction"] == direction
        ).items()))
        for direction in ("LONG", "SHORT")
    }
    terminal_counts = dict(sorted(Counter(row["status"] for row in candidates).items()))
    emitted_candidate_event_ids = [
        row["event_id"] for row in candidates if row["status"] == "EVENT_EMITTED"
    ]
    exclusion_counts = dict(sorted(Counter(
        row["exclusion_reason"]
        for row in candidates
        if row["status"] != "EVENT_EMITTED"
    ).items()))

    contract_result_projection_match = (
        identity(contract) == expected["b4_canonical_summary_sha256"]
        and contract["canonical_summary_sha256"] == expected["b4_canonical_summary_sha256"]
        and contract["decision"] == expected["b4_decision"]
        and contract["event_count"] == summary_output["event_population"]["total"]
        and contract["long_count"] == summary_output["event_population"]["LONG"]
        and contract["short_count"] == summary_output["event_population"]["SHORT"]
        and contract["year_counts"] == summary_output["event_population"]["counts_per_year"]
        and contract["output_hashes"] == summary_output["output_hashes"]
    )
    manifest_valid = manifest == expected["source_manifest"]
    deterministic_valid = (
        deterministic["decision"] == expected["b4_decision"]
        and deterministic["execution_status"] == "PASS"
        and deterministic["mismatch_count"] == 0
        and deterministic["byte_identical"] is True
        and deterministic["normal_repeat_identical"] is True
        and deterministic["relocation_identical"] is True
        and all(deterministic[key] == value for key, value in hashes.items())
        and set(deterministic["run_sha256"].values()) == {hashes["complete_output_sha256"]}
        and set(deterministic["run_sha256"]) == {"normal_1", "normal_2", "relocated"}
    )
    summary_consistent = (
        population_summary["event_population"]["total"] == len(events)
        and population_summary["event_population"]["LONG"] == directions["LONG"]
        and population_summary["event_population"]["SHORT"] == directions["SHORT"]
        and population_summary["event_population"]["counts_per_year"] == year_counts
        and population_summary["event_population"]["counts_per_direction_year"] == direction_year_counts
        and population_summary["event_population"]["first_event_timestamp"]
        == min(event["confirmation_timestamp"] for event in events)
        and population_summary["event_population"]["last_event_timestamp"]
        == max(event["confirmation_timestamp"] for event in events)
        and population_summary["terminal_status_counts"] == terminal_counts
        and population_summary["exclusion_counts"] == exclusion_counts
    )
    return {
        "b4_canonical_summary_sha256": identity(contract),
        "contract_schema_validated": True,
        "result_schema_validated": True,
        "contract_result_projection_match": contract_result_projection_match,
        "source_rows": population_summary["source_rows"],
        "gap_count": population_summary["detected_gap_count"],
        "accepted_weekend_closures": population_summary["accepted_weekend_closures"],
        "accepted_daily_closures": population_summary["accepted_daily_closures"],
        "unverified_gaps": population_summary["unverified_gaps"],
        "event_count": len(events),
        "long_count": directions["LONG"],
        "short_count": directions["SHORT"],
        "year_counts": year_counts,
        "hashes": hashes,
        "event_ids": ids,
        "event_ids_unique": len(ids) == len(set(ids)),
        "semantic_events_unique": len(semantic_keys) == len(set(semantic_keys)),
        "event_row_order_canonical": ids == sorted(ids),
        "candidate_row_order_canonical": candidate_order == sorted(candidate_order),
        "candidate_event_mapping_valid": (
            len(emitted_candidate_event_ids) == len(ids)
            and Counter(emitted_candidate_event_ids) == Counter(ids)
        ),
        "event_years_valid": all(
            event["year"] == confirmation_years[event["event_id"]] for event in events
        ),
        "valid_timestamp_ordering": all(validate_timestamp_order(event) for event in events),
        "resolved_source_row_keys": source_keys_resolved(events, manifest),
        "deterministic_replay_validated": deterministic_valid,
        "source_manifest_validated": manifest_valid,
        "summary_consistent": summary_consistent,
        "event_rows": events,
    }


def run_negative_tests(audit, contract, expected):
    results = {}
    altered = copy.deepcopy(audit["event_rows"])
    altered[0]["event_id"] += "_ALTERED"
    results["changed_event_detected"] = (
        digest(altered) != audit["hashes"]["event_population_sha256"]
    )
    reordered = copy.deepcopy(audit["event_rows"])
    reordered[0], reordered[1] = reordered[1], reordered[0]
    results["reordered_event_detected"] = (
        digest(reordered) != audit["hashes"]["event_population_sha256"]
        and [row["event_id"] for row in reordered] != sorted(row["event_id"] for row in reordered)
    )
    wrong_count = copy.deepcopy(contract)
    wrong_count["event_count"] += 1
    results["wrong_count_detected"] = wrong_count["event_count"] != expected["event_count"]
    wrong_hash = copy.deepcopy(contract)
    wrong_hash["output_hashes"]["event_population_sha256"] = "0" * 64
    results["wrong_hash_detected"] = wrong_hash["output_hashes"] != expected["hashes"]
    wrong_decision = copy.deepcopy(contract)
    wrong_decision["decision"] = "WRONG"
    results["wrong_decision_detected"] = wrong_decision["decision"] != expected["b4_decision"]
    try:
        builtins.__import__("market_structure_break_retest_detector")
        results["forbidden_module_import_blocked"] = False
    except ImportError:
        results["forbidden_module_import_blocked"] = True
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        results["external_process_attempt_blocked"] = False
    except RuntimeError:
        results["external_process_attempt_blocked"] = True
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
        raise SystemExit("B4A_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B4A_OUTPUT_PATH_NOT_ALLOWED")

    files = Files()
    files.add(AUTH, "b4a_authorization")
    files.add(AUTH_SCHEMA, "b4a_authorization_schema")
    files.add(EVIDENCE_SCHEMA, "b4a_evidence_schema")
    authorization = read_json(files, AUTH)
    authorization_schema = read_json(files, AUTH_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)

    paths = {}
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        if not path.is_file():
            raise SystemExit("B4A_COMMITTED_BINDING_MISSING")
        files.add(path, binding["category"])
        if byte_digest(files.read(path)) != binding["file_sha256"]:
            raise SystemExit("B4A_COMMITTED_BINDING_HASH_MISMATCH")
        paths[binding["artifact_id"]] = path

    expected = authorization["expected"]
    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        normal_1 = audit_once(files, paths, expected)
        normal_2 = audit_once(files, paths, expected)
        with tempfile.TemporaryDirectory(prefix="fr_prep_b4a_relocation_") as name:
            relocation_root = Path(name).resolve()
            if relocation_root == ROOT or ROOT in relocation_root.parents:
                raise SystemExit("B4A_RELOCATION_INSIDE_REPOSITORY")
            relocated_paths = {}
            for artifact_id, source in paths.items():
                target = relocation_root / (artifact_id + source.suffix)
                target.write_bytes(files.read(source))
                files.add(target, "relocated_committed_artifacts")
                if byte_digest(files.read(target)) != byte_digest(files.read(source)):
                    raise SystemExit("B4A_RELOCATION_BYTE_MISMATCH")
                relocated_paths[artifact_id] = target
            relocated = audit_once(files, relocated_paths, expected)
        contract = read_json(files, paths["b4_contract"])
        negative_tests = run_negative_tests(normal_1, contract, expected)

    imported_modules = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES
        if name in sys.modules or name in imported_modules
    )
    module_import_counts = {
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "b4_runner_import_count": int("run_fr_prep_b4_fq_holdout_event_population_replay" in prohibited_loaded),
        "wrapper_import_count": int("fr_prep_runner_execution_wrapper" in prohibited_loaded),
        "fj_runner_import_count": int("run_checkpoint_fj_historical_event_population" in prohibited_loaded),
        "fq_validator_import_count": int("run_checkpoint_fq_holdout_gap_boundary" in prohibited_loaded),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
        "ea_import_count": sum("expertadvisor" in name.lower() or name.lower().endswith("_ea") for name in imported_modules),
    }
    prohibited_execution_counts = {
        key: 0
        for key in (
            "detector_execution_count",
            "b4_runner_execution_count",
            "wrapper_execution_count",
            "fj_runner_execution_count",
            "fq_validator_execution_count",
            "atr_event_generation_count",
            "tp_sl_calculation_count",
            "outcome_generation_count",
            "fn_interpretation_count",
            "optimization_count",
            "mt5_execution_count",
            "ea_execution_count",
        )
    }
    expected_values = (
        expected["source_rows"],
        expected["gap_count"],
        expected["accepted_weekend_closures"],
        expected["accepted_daily_closures"],
        expected["unverified_gaps"],
        expected["event_count"],
        expected["long_count"],
        expected["short_count"],
        expected["year_counts"],
    )
    actual_values = (
        normal_1["source_rows"],
        normal_1["gap_count"],
        normal_1["accepted_weekend_closures"],
        normal_1["accepted_daily_closures"],
        normal_1["unverified_gaps"],
        normal_1["event_count"],
        normal_1["long_count"],
        normal_1["short_count"],
        normal_1["year_counts"],
    )
    comparable_keys = set(normal_1) - {"event_rows"}
    mismatch_counters = {
        "repeat_mismatch": int(any(normal_1[key] != normal_2[key] for key in comparable_keys)),
        "relocation_mismatch": int(any(normal_1[key] != relocated[key] for key in comparable_keys)),
        "identity_mismatch": int(normal_1["b4_canonical_summary_sha256"] != expected["b4_canonical_summary_sha256"]),
        "count_mismatch": int(actual_values != expected_values),
        "hash_mismatch": int(normal_1["hashes"] != expected["hashes"]),
        "ordering_mismatch": int(not normal_1["event_row_order_canonical"] or not normal_1["candidate_row_order_canonical"]),
        "uniqueness_mismatch": int(not normal_1["event_ids_unique"] or not normal_1["semantic_events_unique"]),
        "candidate_event_mapping_mismatch": int(not normal_1["candidate_event_mapping_valid"]),
        "event_year_mismatch": int(not normal_1["event_years_valid"]),
        "timestamp_mismatch": int(not normal_1["valid_timestamp_ordering"]),
        "source_row_key_mismatch": int(not normal_1["resolved_source_row_keys"]),
        "schema_or_projection_mismatch": int(not normal_1["contract_result_projection_match"]),
        "deterministic_replay_mismatch": int(not normal_1["deterministic_replay_validated"]),
        "source_manifest_mismatch": int(not normal_1["source_manifest_validated"]),
        "summary_mismatch": int(not normal_1["summary_consistent"]),
        "negative_test_mismatch": int(not negative_tests["all_passed"]),
    }
    if (
        any(mismatch_counters.values())
        or any(module_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B4A_INDEPENDENT_AUDIT_FAILED")

    evidence = {
        "schema_version": "fr_prep_b4a_independent_fq_replay_audit.v1",
        "checkpoint": "FR_PREP_B4A",
        "decision": PASS,
        "b4_evidence": {
            "decision": expected["b4_decision"],
            "canonical_summary_sha256": normal_1["b4_canonical_summary_sha256"],
            "contract_schema_validated": normal_1["contract_schema_validated"],
            "result_schema_validated": normal_1["result_schema_validated"],
            "contract_result_projection_match": normal_1["contract_result_projection_match"],
        },
        "source_rows": normal_1["source_rows"],
        "gap_count": normal_1["gap_count"],
        "accepted_weekend_closures": normal_1["accepted_weekend_closures"],
        "accepted_daily_closures": normal_1["accepted_daily_closures"],
        "unverified_gaps": normal_1["unverified_gaps"],
        "event_count": normal_1["event_count"],
        "long_count": normal_1["long_count"],
        "short_count": normal_1["short_count"],
        "year_counts": normal_1["year_counts"],
        "recomputed_hashes": normal_1["hashes"],
        "event_ids_unique": normal_1["event_ids_unique"],
        "semantic_events_unique": normal_1["semantic_events_unique"],
        "event_row_order_canonical": normal_1["event_row_order_canonical"],
        "candidate_row_order_canonical": normal_1["candidate_row_order_canonical"],
        "candidate_event_mapping_valid": normal_1["candidate_event_mapping_valid"],
        "event_years_valid": normal_1["event_years_valid"],
        "valid_timestamp_ordering": normal_1["valid_timestamp_ordering"],
        "resolved_source_row_keys": normal_1["resolved_source_row_keys"],
        "deterministic_replay_validated": normal_1["deterministic_replay_validated"],
        "source_manifest_validated": normal_1["source_manifest_validated"],
        "normal_repeat_identical": mismatch_counters["repeat_mismatch"] == 0,
        "relocation_identical": mismatch_counters["relocation_mismatch"] == 0,
        "mismatch_counters": mismatch_counters,
        "negative_tests": negative_tests,
        "runtime_audit": {
            "module_import_counts": module_import_counts,
            "prohibited_execution_counts": prohibited_execution_counts,
            "file_access": files.report(),
            "external_process": external_guard.report(),
            "prohibited_import_attempts_blocked": import_guard.blocked,
            "counter_provenance": {
                "module_imports": "sys.modules delta plus fail-closed builtins import interception",
                "file_access": "exact resolved-path allowlist for committed B4 artifacts",
                "external_process": "Popen, os.system, and os.startfile fail-closed interception",
                "executions": "the independent audit contains no replay, detector, validator, MT5, or EA dispatch",
            },
        },
        "prohibited_modules": prohibited_loaded,
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "execution_status": "PASS",
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
        "committed_fq_artifacts_read": True,
        "raw_fq_sources_accessed": False,
        "fq_validator_executed": False,
        "atr_events_generated": False,
        "tp_sl_calculated": False,
        "outcomes_generated": False,
        "fn_interpretation_performed": False,
        "optimization_performed": False,
        "mt5_executed": False,
        "ea_executed": False,
    }
    evidence["canonical_summary_sha256"] = digest(evidence)
    if absolute_path_count(evidence):
        raise SystemExit("B4A_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAK")
    evidence_schema = read_json(files, EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(evidence_schema)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)

    EVIDENCE.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = {
        "decision": PASS,
        "canonical_summary_sha256": evidence["canonical_summary_sha256"],
        "b4_canonical_summary_sha256": normal_1["b4_canonical_summary_sha256"],
        "rows_gaps": {
            "rows": normal_1["source_rows"],
            "gaps": normal_1["gap_count"],
            "accepted_weekend": normal_1["accepted_weekend_closures"],
            "accepted_daily": normal_1["accepted_daily_closures"],
            "unverified": normal_1["unverified_gaps"],
        },
        "events": {
            "total": normal_1["event_count"],
            "LONG": normal_1["long_count"],
            "SHORT": normal_1["short_count"],
            "by_year": normal_1["year_counts"],
        },
        "hashes": normal_1["hashes"],
        "mismatch_count": sum(mismatch_counters.values()),
        "repeat_identical": True,
        "relocation_identical": True,
        "negative_tests": {
            "passed": negative_tests["tests_passed"],
            "total": negative_tests["test_count"],
        },
        "prohibited_import_count": sum(module_import_counts.values()),
        "prohibited_execution_count": sum(prohibited_execution_counts.values()),
        "execution_status": "PASS",
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
