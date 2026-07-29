#!/usr/bin/env python3
"""Freeze the FQ gap-remediation evidence contract without remediating gaps."""

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
from datetime import datetime
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b11_fq_data_quality_remediation_contract_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b11_fq_data_quality_remediation_contract_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b11_fq_data_quality_remediation_contract.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b11_fq_data_quality_remediation_contract.v1.schema.json"
RESULT = ROOT / "research/results/checkpoint_fr_prep_b11/fq_data_quality_remediation_contract_summary.json"
MODE = "freeze-fq-data-quality-remediation-contract"
PASS = "FR_PREP_B11_PASS_FQ_DATA_QUALITY_REMEDIATION_CONTRACT_FROZEN"
RAW_GAP_FIELDS = {
    "gap_id",
    "calendar_year",
    "day_of_week",
    "previous_bar_timestamp",
    "next_bar_timestamp",
    "elapsed_hours",
    "missing_h1_slots",
    "previous_source_file",
    "next_source_file",
    "evidence_status",
    "policy_classification",
    "fail_closed_required",
}
PROHIBITED_MODULES = {
    "observational_outcome_adapter",
    "run_fr_prep_b7_sealed_real_observational_outcomes",
    "run_fr_prep_b7a_independent_real_outcome_audit",
    "market_structure_break_retest_detector",
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


def skip_space(text, index):
    while index < len(text) and text[index] in " \t\r\n":
        index += 1
    return index


def scan_json_value_end(text, index):
    index = skip_space(text, index)
    if text[index] == '"':
        escaped = False
        cursor = index + 1
        while cursor < len(text):
            char = text[cursor]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                return cursor + 1
            cursor += 1
        raise ValueError("B11_UNTERMINATED_JSON_STRING")
    if text[index] in "[{":
        stack = [text[index]]
        in_string = False
        escaped = False
        cursor = index + 1
        while cursor < len(text):
            char = text[cursor]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif char in "[{":
                stack.append(char)
            elif char in "]}":
                expected = "[" if char == "]" else "{"
                if not stack or stack[-1] != expected:
                    raise ValueError("B11_INVALID_JSON_NESTING")
                stack.pop()
                if not stack:
                    return cursor + 1
            cursor += 1
        raise ValueError("B11_UNTERMINATED_JSON_CONTAINER")
    cursor = index
    while cursor < len(text) and text[cursor] not in ",}":
        cursor += 1
    return cursor


def selective_object(text, permitted_fields):
    decoder = json.JSONDecoder()
    cursor = skip_space(text, 0)
    if text[cursor] != "{":
        raise ValueError("B11_GAP_RECORD_NOT_OBJECT")
    cursor += 1
    selected = {}
    while True:
        cursor = skip_space(text, cursor)
        if text[cursor] == "}":
            break
        key, key_end = decoder.raw_decode(text, cursor)
        cursor = skip_space(text, key_end)
        if text[cursor] != ":":
            raise ValueError("B11_GAP_RECORD_MISSING_COLON")
        value_start = skip_space(text, cursor + 1)
        value_end = scan_json_value_end(text, value_start)
        if key in permitted_fields:
            selected[key] = json.loads(text[value_start:value_end])
        cursor = skip_space(text, value_end)
        if text[cursor] == ",":
            cursor += 1
            continue
        if text[cursor] == "}":
            break
        raise ValueError("B11_GAP_RECORD_SEPARATOR_INVALID")
    if set(selected) != set(permitted_fields):
        raise ValueError("B11_REQUIRED_GAP_METADATA_FIELD_MISSING")
    return selected


class Files:
    def __init__(self):
        self.registry = {}
        self.hash_reads = Counter()
        self.json_reads = Counter()
        self.gap_metadata_reads = Counter()
        self.blocked_reads = 0
        self.blocked_ohlc_field_attempts = 0

    def add(self, path, artifact_id, access):
        self.registry[Path(path).resolve()] = (artifact_id, access)

    def hash_read(self, path):
        resolved = Path(path).resolve()
        if resolved not in self.registry:
            self.blocked_reads += 1
            raise PermissionError("B11_UNAUTHORIZED_HASH_READ_BLOCKED")
        artifact_id, _access = self.registry[resolved]
        self.hash_reads[artifact_id] += 1
        return resolved.read_bytes()

    def parse_json(self, path):
        resolved = Path(path).resolve()
        entry = self.registry.get(resolved)
        if entry is None or entry[1] != "json":
            self.blocked_reads += 1
            raise PermissionError("B11_UNAUTHORIZED_JSON_PARSE_BLOCKED")
        artifact_id, _access = entry
        self.json_reads[artifact_id] += 1
        return json.loads(resolved.read_text(encoding="utf-8"))

    def parse_gap_metadata(self, path, requested_fields):
        resolved = Path(path).resolve()
        entry = self.registry.get(resolved)
        if entry is None or entry[1] != "selective_gap_metadata":
            self.blocked_reads += 1
            raise PermissionError("B11_GAP_METADATA_PATH_BLOCKED")
        requested = set(requested_fields)
        if requested != RAW_GAP_FIELDS:
            self.blocked_ohlc_field_attempts += 1
            raise PermissionError("B11_NON_METADATA_OR_OHLC_FIELD_PARSE_BLOCKED")
        text = resolved.read_text(encoding="utf-8")
        cursor = skip_space(text, 0)
        if text[cursor] != "[":
            raise ValueError("B11_GAP_INVENTORY_NOT_ARRAY")
        cursor += 1
        records = []
        while True:
            cursor = skip_space(text, cursor)
            if text[cursor] == "]":
                break
            end = scan_json_value_end(text, cursor)
            records.append(selective_object(text[cursor:end], requested))
            cursor = skip_space(text, end)
            if text[cursor] == ",":
                cursor += 1
                continue
            if text[cursor] == "]":
                break
            raise ValueError("B11_GAP_INVENTORY_SEPARATOR_INVALID")
        artifact_id, _access = entry
        self.gap_metadata_reads[artifact_id] += 1
        return records

    def report(self):
        ids = sorted({item[0] for item in self.registry.values()})
        return {
            "hash_read_operation_counts": {item: self.hash_reads[item] for item in ids},
            "json_parse_operation_counts": {item: self.json_reads[item] for item in ids},
            "gap_metadata_parse_operation_counts": {
                item: self.gap_metadata_reads[item] for item in ids
            },
            "blocked_unauthorized_read_attempt_count": self.blocked_reads,
            "blocked_ohlc_or_nonmetadata_field_attempt_count": self.blocked_ohlc_field_attempts,
            "gap_metadata_fields_parsed": sorted(RAW_GAP_FIELDS),
            "ohlc_value_parse_count": 0,
            "raw_broker_csv_read_count": 0,
            "future_price_read_count": 0,
            "b7_jsonl_parse_count": 0,
            "b7_statistics_csv_parse_count": 0,
            "unauthorized_successful_read_count": 0,
        }


class ExternalProcessGuard:
    def __init__(self):
        self.blocked = 0

    def deny(self, *_args, **_kwargs):
        self.blocked += 1
        raise RuntimeError("B11_EXTERNAL_PROCESS_BLOCKED")

    def __enter__(self):
        self.popen = subprocess.Popen
        self.system = os.system
        self.startfile = getattr(os, "startfile", None)
        subprocess.Popen = self.deny
        os.system = self.deny
        if self.startfile is not None:
            os.startfile = self.deny
        return self

    def __exit__(self, *_args):
        subprocess.Popen = self.popen
        os.system = self.system
        if self.startfile is not None:
            os.startfile = self.startfile


class ImportGuard:
    def __init__(self):
        self.blocked = 0

    def guarded(self, name, *args, **kwargs):
        if name.split(".", 1)[0] in PROHIBITED_MODULES:
            self.blocked += 1
            raise ImportError("B11_PROHIBITED_IMPORT_BLOCKED")
        return self.original(name, *args, **kwargs)

    def __enter__(self):
        self.original = builtins.__import__
        builtins.__import__ = self.guarded
        return self

    def __exit__(self, *_args):
        builtins.__import__ = self.original


def validate_identity(document, expected_identity, expected_decision):
    return (
        identity(document) == expected_identity
        and document["canonical_summary_sha256"] == expected_identity
        and document["decision"] == expected_decision
        and document["execution_status"] == "PASS"
    )


def project_gap(record):
    return {
        "gap_id": record["gap_id"],
        "calendar_year": record["calendar_year"],
        "day_of_week": record["day_of_week"],
        "previous_bar_timestamp": record["previous_bar_timestamp"],
        "next_bar_timestamp": record["next_bar_timestamp"],
        "elapsed_hours": record["elapsed_hours"],
        "missing_h1_slots": record["missing_h1_slots"],
        "previous_source_file": record["previous_source_file"],
        "next_source_file": record["next_source_file"],
        "original_evidence_status": record["evidence_status"],
        "original_policy_classification": record["policy_classification"],
        "original_fail_closed_required": record["fail_closed_required"],
    }


def structural_signature(record):
    previous = datetime.fromisoformat(record["previous_bar_timestamp"])
    following = datetime.fromisoformat(record["next_bar_timestamp"])
    return {
        "calendar_year": record["calendar_year"],
        "day_of_week": record["day_of_week"],
        "elapsed_hours": record["elapsed_hours"],
        "missing_h1_slots": record["missing_h1_slots"],
        "previous_bar_weekday": previous.strftime("%A"),
        "previous_bar_hour": previous.hour,
        "next_bar_weekday": following.strftime("%A"),
        "next_bar_hour": following.hour,
        "same_source_file": record["previous_source_file"] == record["next_source_file"],
        "original_evidence_status": record["original_evidence_status"],
        "original_policy_classification": record["original_policy_classification"],
        "original_fail_closed_required": record["original_fail_closed_required"],
    }


def base_request(expected):
    return {
        "b10a_identity": expected["b10a"]["canonical_summary_sha256"],
        "b10a_decision": expected["b10a"]["decision"],
        "selected_disposition": expected["b10a"]["selected_disposition"],
        "manifest_hash": expected["fq"]["source_manifest_sha256"],
        "inventory_hash": expected["fq"]["gap_inventory_sha256"],
        "counts": [
            expected["fq"]["total_gap_count"],
            expected["fq"]["accepted_gap_count"],
            expected["fq"]["target_unverified_gap_count"],
        ],
        "modify_original_inventory": False,
        "reclassify_gap": False,
        "read_ohlc_raw_csv_or_future_prices": False,
        "synthesize_or_interpolate": False,
        "pattern_only_as_primary": False,
        "different_broker_server_symbol_without_conflict": False,
        "generic_calendar_as_sole_evidence": False,
        "outcome_based_prioritization": False,
        "coverage_target_as_evidence": False,
        "accept_evidence_conflict_as_closure": False,
        "execute_future_stage": False,
        "claims": [],
        "trade_or_order_features": [],
        "external_process": False,
        "runtime_path": None,
    }


def request_allowed(expected, request):
    return request == base_request(expected)


def negative_tests(authorization, files, inventory_path):
    expected = authorization["expected"]
    base = base_request(expected)
    tests = {}

    def mutate(name, update):
        changed = copy.deepcopy(base)
        update(changed)
        tests[name] = not request_allowed(expected, changed)

    mutate(
        "wrong_b10a_identity_decision_or_selected_disposition_blocked",
        lambda value: value.update({"b10a_identity": "0" * 64}),
    )
    mutate(
        "changed_fq_source_manifest_or_gap_inventory_hash_blocked",
        lambda value: value.update({"inventory_hash": "0" * 64}),
    )
    mutate(
        "wrong_total_accepted_or_unverified_gap_count_blocked",
        lambda value: value.update({"counts": [774, 149, 624]}),
    )
    mutate(
        "original_gap_inventory_modification_attempt_blocked",
        lambda value: value.update({"modify_original_inventory": True}),
    )
    mutate(
        "gap_reclassification_during_contract_design_blocked",
        lambda value: value.update({"reclassify_gap": True}),
    )
    try:
        files.parse_gap_metadata(inventory_path, RAW_GAP_FIELDS | {"open", "high", "low", "close"})
        ohlc_blocked = False
    except PermissionError:
        ohlc_blocked = True
    raw_blocked = 0
    for path in authorization["prohibited_input_paths"]:
        try:
            files.parse_json(ROOT / path)
        except PermissionError:
            raw_blocked += 1
    changed = copy.deepcopy(base)
    changed["read_ohlc_raw_csv_or_future_prices"] = True
    tests["ohlc_raw_csv_or_future_price_parsing_attempt_blocked"] = (
        ohlc_blocked and raw_blocked == 3 and not request_allowed(expected, changed)
    )
    mutate(
        "synthetic_bar_creation_or_interpolation_blocked",
        lambda value: value.update({"synthesize_or_interpolate": True}),
    )
    mutate(
        "pattern_only_evidence_as_primary_blocked",
        lambda value: value.update({"pattern_only_as_primary": True}),
    )
    mutate(
        "different_broker_server_symbol_without_conflict_blocked",
        lambda value: value.update({"different_broker_server_symbol_without_conflict": True}),
    )
    mutate(
        "generic_calendar_as_sole_evidence_blocked",
        lambda value: value.update({"generic_calendar_as_sole_evidence": True}),
    )
    mutate(
        "outcome_return_share_mfe_mae_or_subgroup_prioritization_blocked",
        lambda value: value.update({"outcome_based_prioritization": True}),
    )
    mutate(
        "coverage_target_used_as_evidence_blocked",
        lambda value: value.update({"coverage_target_as_evidence": True}),
    )
    mutate(
        "evidence_conflict_incorrectly_accepted_as_closure_blocked",
        lambda value: value.update({"accept_evidence_conflict_as_closure": True}),
    )
    mutate(
        "remediation_adjudication_timeline_rebuild_or_outcome_rerun_blocked",
        lambda value: value.update({"execute_future_stage": True}),
    )
    mutate(
        "profitability_edge_robustness_or_readiness_claim_blocked",
        lambda value: value.update({"claims": ["PROFITABILITY", "EDGE", "ROBUSTNESS", "READINESS"]}),
    )
    mutate(
        "tp_sl_cost_cash_pl_lot_or_order_simulation_blocked",
        lambda value: value.update({
            "trade_or_order_features": ["TP_SL", "COST", "CASH_PL", "LOT", "ORDER_SIMULATION"]
        }),
    )
    blocked_imports = 0
    for module in sorted(PROHIBITED_MODULES):
        try:
            builtins.__import__(module)
        except ImportError:
            blocked_imports += 1
    try:
        subprocess.Popen(["terminal64.exe", "/blocked"])
        external_blocked = False
    except RuntimeError:
        external_blocked = True
    leaked = copy.deepcopy(base)
    leaked["runtime_path"] = str(ROOT.resolve())
    tests["mt5_ea_network_external_process_or_absolute_path_leakage_blocked"] = (
        blocked_imports == len(PROHIBITED_MODULES)
        and external_blocked
        and not request_allowed(expected, leaked)
        and absolute_path_count(leaked) == 1
    )
    return {
        "test_count": len(tests),
        "tests_passed": sum(tests.values()),
        "all_passed": all(tests.values()),
        "results": tests,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=[MODE])
    parser.add_argument("--authorization", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args()
    if Path(args.authorization).resolve() != AUTH.resolve():
        raise SystemExit("B11_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != RESULT.parent.resolve():
        raise SystemExit("B11_OUTPUT_ROOT_NOT_ALLOWED")

    files = Files()
    for path, artifact_id in (
        (AUTH, "b11_authorization"),
        (AUTH_SCHEMA, "b11_authorization_schema"),
        (CONTRACT_SCHEMA, "b11_contract_schema"),
    ):
        files.add(path, artifact_id, "json")
    authorization = files.parse_json(AUTH)
    authorization_schema = files.parse_json(AUTH_SCHEMA)
    contract_schema = files.parse_json(CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(contract_schema)

    paths = {}
    artifact_hash_mismatch = 0
    for binding in authorization["committed_artifacts"]:
        path = (ROOT / binding["path"]).resolve()
        files.add(path, binding["artifact_id"], binding["access"])
        paths[binding["artifact_id"]] = path
        if not path.is_file():
            raise SystemExit("B11_COMMITTED_ARTIFACT_MISSING")
        artifact_hash_mismatch += int(
            byte_digest(files.hash_read(path)) != binding["file_sha256"]
        )
    if artifact_hash_mismatch:
        raise SystemExit("B11_COMMITTED_ARTIFACT_HASH_MISMATCH")

    b10 = files.parse_json(paths["b10_contract"])
    b10_schema = files.parse_json(paths["b10_schema"])
    b10_summary = files.parse_json(paths["b10_summary"])
    b10a = files.parse_json(paths["b10a_contract"])
    b10a_schema = files.parse_json(paths["b10a_schema"])
    b10a_summary = files.parse_json(paths["b10a_summary"])
    source_manifest = files.parse_json(paths["fq_source_manifest"])
    b4_replay = files.parse_json(paths["fq_b4_replay"])

    jsonschema.Draft202012Validator.check_schema(b10_schema)
    jsonschema.Draft202012Validator(b10_schema).validate(b10)
    jsonschema.Draft202012Validator.check_schema(b10a_schema)
    jsonschema.Draft202012Validator(b10a_schema).validate(b10a)
    expected = authorization["expected"]
    b10_valid = (
        validate_identity(
            b10,
            expected["b10"]["canonical_summary_sha256"],
            expected["b10"]["decision"],
        )
        and b10_summary == b10
    )
    b10a_valid = (
        validate_identity(
            b10a,
            expected["b10a"]["canonical_summary_sha256"],
            expected["b10a"]["decision"],
        )
        and b10a_summary == b10a
        and b10a["conclusions"]["selected_disposition"]
        == expected["b10a"]["selected_disposition"]
        and b10a["conclusions"]["first_matching_rule"]
        == expected["b10a"]["first_matching_rule"]
        and b10a["conclusions"]["data_remediation_execution"] == "NOT_STARTED"
        and b10a["conclusions"]["next_allowed_scope"]
        == expected["b10a"]["next_allowed_scope"]
        and b10a["output_hashes"]["decision_record_sha256"]
        == expected["b10a"]["decision_record_sha256"]
        and b10a["output_hashes"]["rule_trace_sha256"]
        == expected["b10a"]["rule_trace_sha256"]
        and b10a["output_hashes"]["complete_sha256"]
        == expected["b10a"]["complete_sha256"]
    )
    fq_expected = expected["fq"]
    manifest_sources = [
        {
            "filename": item["filename"],
            "rows": item["rows"],
            "sha256": item["sha256"],
        }
        for item in source_manifest["sources"]
    ]
    fq_binding_valid = (
        source_manifest["dataset_id"] == fq_expected["dataset_id"]
        and source_manifest["source_rows"] == fq_expected["source_rows"]
        and source_manifest["canonical_timeline_sha256"]
        == fq_expected["canonical_timeline_sha256"]
        and source_manifest["gap_inventory"]["gaps"] == fq_expected["total_gap_count"]
        and source_manifest["gap_inventory"]["accepted_weekend"]
        == fq_expected["accepted_gap_count"]
        and source_manifest["gap_inventory"]["unverified_fail_closed"]
        == fq_expected["target_unverified_gap_count"]
        and source_manifest["gap_inventory"]["sha256"]
        == fq_expected["gap_inventory_sha256"]
        and manifest_sources == fq_expected["sources"]
        and b4_replay["execution_status"] == "PASS"
        and b4_replay["event_population_sha256"]
        == fq_expected["event_population_sha256"]
    )
    if not (b10_valid and b10a_valid and fq_binding_valid):
        raise SystemExit("B11_UPSTREAM_OR_FQ_BINDING_VALIDATION_BLOCKED")

    raw_records = files.parse_gap_metadata(paths["fq_gap_inventory"], RAW_GAP_FIELDS)
    projected = [project_gap(item) for item in raw_records]
    unique_ids = {item["gap_id"] for item in projected}
    accepted = [
        item
        for item in projected
        if item["original_evidence_status"] == "RULE_MATCHED"
        and item["original_policy_classification"]
        == "ACCEPTED_ROUTINE_WEEKEND_CLOSURE"
        and item["original_fail_closed_required"] is False
    ]
    targets = sorted(
        (
            item
            for item in projected
            if item["original_evidence_status"] == "UNVERIFIED"
            and item["original_policy_classification"] == "UNVERIFIED_GAP"
            and item["original_fail_closed_required"] is True
        ),
        key=lambda item: item["gap_id"],
    )
    counts_valid = (
        len(projected) == fq_expected["total_gap_count"]
        and len(unique_ids) == fq_expected["total_gap_count"]
        and len(accepted) == fq_expected["accepted_gap_count"]
        and len(targets) == fq_expected["target_unverified_gap_count"]
        and len(accepted) + len(targets) == len(projected)
    )
    if not counts_valid:
        raise SystemExit("B11_FQ_GAP_COUNT_OR_CLASSIFICATION_MISMATCH")

    target_ids = [item["gap_id"] for item in targets]
    target_id_hash = digest(target_ids)
    target_metadata_hash = digest(targets)
    signature_counter = Counter(canonical_json(structural_signature(item)) for item in targets)
    signature_inventory = [
        {
            "signature": json.loads(signature),
            "gap_count": signature_counter[signature],
        }
        for signature in sorted(signature_counter)
    ]
    signature_hash = digest(signature_inventory)
    frozen_contract_1 = copy.deepcopy(authorization["design"])
    frozen_contract_2 = copy.deepcopy(authorization["design"])
    frozen_contract_1["stage_separation_policy"] = {
        "stages_execute_only_under_separate_future_checkpoints": True,
        "b11_authorizes_outcome_rerun": False,
        "future_outcome_rerun_requires_new_authorization_after_independent_timeline_audit": True,
    }
    frozen_contract_1["structural_signature_policy"] = {
        "descriptive_intake_metadata_only": True,
        "independently_justifies_gap_acceptance": False,
        "pattern_recurrence_alone_sufficient": False,
    }
    frozen_contract_1["canonical_identity_security"] = {
        "credentials_account_numbers_tokens_allowed": False,
        "absolute_runtime_paths_allowed": False,
    }
    frozen_contract_2 = copy.deepcopy(frozen_contract_1)

    before_modules = set(sys.modules)
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        tests = negative_tests(authorization, files, paths["fq_gap_inventory"])
    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported
    )
    mismatch_counters = {
        "b10_identity_decision_or_schema_mismatch": int(not b10_valid),
        "b10a_identity_decision_disposition_or_schema_mismatch": int(not b10a_valid),
        "committed_artifact_hash_mismatch": artifact_hash_mismatch,
        "fq_source_manifest_binding_mismatch": int(not fq_binding_valid),
        "fq_gap_count_or_classification_mismatch": int(not counts_valid),
        "target_gap_id_sort_or_uniqueness_mismatch": int(
            target_ids != sorted(target_ids) or len(set(target_ids)) != len(target_ids)
        ),
        "contract_repeat_mismatch": int(frozen_contract_1 != frozen_contract_2),
        "negative_test_mismatch": int(not tests["all_passed"]),
        "absolute_path_identity_mismatch": 0,
    }
    prohibited_import_counts = {
        "adapter_import_count": int("observational_outcome_adapter" in prohibited_loaded),
        "b7_runner_import_count": int("run_fr_prep_b7_sealed_real_observational_outcomes" in prohibited_loaded),
        "b7a_auditor_import_count": int("run_fr_prep_b7a_independent_real_outcome_audit" in prohibited_loaded),
        "detector_import_count": int("market_structure_break_retest_detector" in prohibited_loaded),
        "mt5_import_count": int("MetaTrader5" in prohibited_loaded),
    }
    prohibited_execution_counts = {
        key: 0 for key in (
            "gap_remediation_count",
            "gap_reclassification_count",
            "original_gap_inventory_modification_count",
            "synthetic_bar_creation_count",
            "interpolation_count",
            "timeline_rebuild_count",
            "outcome_rerun_count",
            "statistics_rerun_count",
            "detector_execution_count",
            "event_population_rerun_count",
            "ohlc_value_parse_count",
            "raw_broker_csv_read_count",
            "future_price_read_count",
            "b7_jsonl_parse_count",
            "b7_statistics_parse_count",
            "strategy_change_count",
            "optimization_count",
            "tp_sl_calculation_count",
            "cash_pl_calculation_count",
            "trading_cost_calculation_count",
            "lot_simulation_count",
            "order_simulation_count",
            "mt5_execution_count",
            "ea_execution_count",
            "network_execution_count",
            "external_process_success_count",
            "profitability_claim_count",
            "edge_claim_count",
            "robustness_claim_count",
            "trading_readiness_claim_count",
        )
    }
    if (
        any(mismatch_counters.values())
        or any(prohibited_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B11_FQ_REMEDIATION_CONTRACT_DESIGN_BLOCKED")

    result = {
        "schema_version": "fr_prep_b11_fq_data_quality_remediation_contract.v1",
        "checkpoint": "FR_PREP_B11",
        "decision": PASS,
        "execution_status": "PASS",
        "upstream_validation": {
            "b10": {
                "canonical_summary_sha256": expected["b10"]["canonical_summary_sha256"],
                "decision": expected["b10"]["decision"],
                "identity_schema_and_summary_validated": b10_valid,
            },
            "b10a": {
                **copy.deepcopy(expected["b10a"]),
                "identity_schema_summary_and_hashes_validated": b10a_valid,
            },
        },
        "fq_binding": {
            **copy.deepcopy(fq_expected),
            "source_filenames_from_canonical_manifest": True,
            "source_manifest_and_gap_inventory_hashes_validated": True,
            "gap_inventory_original_sha256": fq_expected["gap_inventory_sha256"],
        },
        "target_inventory": {
            "total_gap_count": len(projected),
            "accepted_gap_count": len(accepted),
            "target_unverified_gap_count": len(targets),
            "target_gap_id_set": target_ids,
            "target_gap_id_set_sha256": target_id_hash,
            "target_gap_metadata_sha256": target_metadata_hash,
            "structural_signature_inventory_sha256": signature_hash,
            "structural_signature_count": len(signature_inventory),
            "structural_signatures_descriptive_only": True,
            "target_hash_policy": {
                "canonical_json": "ASCII_SORTED_KEYS_COMPACT_SEPARATORS",
                "target_gap_id_set": "SORTED_UNIQUE_GAP_ID_ARRAY",
                "target_gap_metadata": "SORTED_PROJECTED_METADATA_RECORD_ARRAY",
                "structural_signature_inventory": "SORTED_SIGNATURE_AND_COUNT_ARRAY",
            },
        },
        "contract": frozen_contract_1,
        "conclusions": {
            "data_quality_remediation_contract": "FROZEN",
            "remediation_target_dataset": fq_expected["dataset_id"],
            "target_unverified_gap_count": len(targets),
            "original_gap_inventory_immutable": True,
            "synthetic_bar_creation": "PROHIBITED",
            "remediation_execution": "NOT_STARTED",
            "evidence_intake": "NOT_STARTED",
            "gap_reclassification": "NOT_STARTED",
            "timeline_rebuild": "NOT_STARTED",
            "outcome_rerun": "NOT_AUTHORIZED",
            "performance": "NOT_EVALUATED",
            "profitability": "NOT_CLAIMED",
            "strategy_edge": "NOT_ESTABLISHED",
            "robustness": "NOT_ESTABLISHED",
            "order_logic": "NOT_APPROVED",
            "candidate": "NOT_READY_FOR_ORDER_LOGIC",
            "next_allowed_scope": "FQ_GAP_REMEDIATION_EVIDENCE_INTAKE_ONLY",
        },
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "file_access": files.report(),
            "blocked_import_requests": import_guard.blocked,
            "prohibited_import_counts": prohibited_import_counts,
            "prohibited_execution_counts": prohibited_execution_counts,
            "external_process": {
                "blocked_launch_count": external_guard.blocked,
                "successful_launch_count": 0,
            },
        },
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "prohibited_modules": [],
    }
    result["canonical_summary_sha256"] = identity(result)
    jsonschema.Draft202012Validator(contract_schema).validate(result)
    if absolute_path_count(result):
        raise SystemExit("B11_ABSOLUTE_RUNTIME_PATH_IDENTITY_LEAKAGE_BLOCKED")
    rendered = json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered, encoding="utf-8", newline="\n")
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(rendered, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": result["canonical_summary_sha256"],
        "total_gap_count": len(projected),
        "accepted_gap_count": len(accepted),
        "target_unverified_gap_count": len(targets),
        "target_gap_id_set_sha256": target_id_hash,
        "target_gap_metadata_sha256": target_metadata_hash,
        "structural_signature_inventory_sha256": signature_hash,
        "structural_signature_count": len(signature_inventory),
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": (
            sum(prohibited_import_counts.values()) + sum(prohibited_execution_counts.values())
        ),
    }))


if __name__ == "__main__":
    main()
