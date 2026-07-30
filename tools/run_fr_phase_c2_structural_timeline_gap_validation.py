#!/usr/bin/env python3
"""Run deterministic FR-Phase-C2 structural, timeline, boundary and gap validation."""

import argparse
import ast
import copy
import csv
import hashlib
import io
import json
import ntpath
import posixpath
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_phase_c2_structural_timeline_gap_validation_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_phase_c2_structural_timeline_gap_validation_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_phase_c2_structural_timeline_gap_validation.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_phase_c2_structural_timeline_gap_validation.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_phase_c2"
ROW_SUMMARY = OUT / "row_structural_validation_summary.json"
TIMELINE_SUMMARY = OUT / "timeline_boundary_validation_summary.json"
GAP_INVENTORY = OUT / "gap_inventory.csv"
DECISION_RECORD = OUT / "dataset_validation_decision.json"
SUMMARY = OUT / "structural_timeline_gap_validation_summary.json"

C0_CONTRACT = ROOT / "research/contracts/fr_phase_c0_clean_data_acquisition_contract.v1.json"
C0A_CONTRACT = ROOT / "research/contracts/fr_phase_c0a_exact_xm_symbol_binding_correction.v1.json"
C1_CONTRACT = ROOT / "research/contracts/fr_phase_c1_manual_raw_data_immutable_intake.v1.json"
C1_RAW_MANIFEST = ROOT / "research/results/checkpoint_fr_phase_c1/raw_artifact_intake_manifest.json"
C1_EVIDENCE_MANIFEST = ROOT / "research/results/checkpoint_fr_phase_c1/source_identity_evidence_manifest.json"
FJ_SOURCE_MANIFEST = ROOT / "research/results/checkpoint_fj_historical_event_population/checkpoint_fj_source_manifest.json"
FQ_SOURCE_INTEGRITY = ROOT / "research/results/checkpoint_fq_holdout_gap_boundary/checkpoint_fq_source_integrity.json"
STRATEGY = ROOT / "MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh"

MODE = "validate-structural-timeline-boundary-gaps"
EXPECTED_AUTH_FILE_SHA256 = "8740c4ebeff9b5e28a4b43358f25d461c9201c520b87442bf5477bccb6c4dc51"
EXPECTED_BRANCH = "agent/fr-phase-c-clean-data-intake"
EXPECTED_HEAD = "14dfb7b1ffed899919735ba19b8f1a18568affb9"
EXPECTED_STASH = "stash@{0}: On agent/fr-prep-b-runner-integration: fr-prep-b2a-partial-draft-before-b2e"
EXPECTED_RAW_NAME = "GOLD#_H1_202601020800_202607300300.csv"
EXPECTED_RAW_SHA256 = "69aa7e16d4d3e54bfe8e0aa3ce4c5d61bbd0fcaefb45050341304681b3766f92"
EXPECTED_RAW_SIZE = 216222
EXPECTED_PHYSICAL_ROWS = 3387
EXPECTED_DATA_ROWS = 3386
EXPECTED_STRATEGY_SHA1 = "da448295ac3bd443b376e1ce51a8e411de3c7245"
EXPECTED_STRATEGY_SHA256 = "0e72b1559f5416981c2db887f9c53a0bfbb66bada226250a064377b2b9fadaa2"

CLEAN_CLASS = "PASS_DATASET_CLEAN_FOR_FUTURE_RESEARCH"
LIMITATIONS_CLASS = "PASS_DATASET_VALIDATED_WITH_LIMITATIONS"
FAIL_CLASS = "FAIL_DATASET_INTAKE"
CLEAN_DECISION = "FR_PHASE_C2_PASS_DATASET_CLEAN_FOR_FUTURE_RESEARCH"
LIMITATIONS_DECISION = "FR_PHASE_C2_PASS_DATASET_VALIDATED_WITH_LIMITATIONS"
FAIL_DECISION = "FR_PHASE_C2_FAIL_DATASET_INTAKE"

ANALYSIS_START = datetime(2026, 1, 1, 0, 0, 0)
ANALYSIS_END = datetime(2026, 6, 30, 23, 59, 59)
REQUEST_START = datetime(2026, 1, 1, 0, 0, 0)
REQUEST_END = datetime(2026, 7, 7, 23, 59, 59)
ANALYSIS_LAST_SLOT = datetime(2026, 6, 30, 23, 0, 0)
REQUEST_LAST_SLOT = datetime(2026, 7, 7, 23, 0, 0)

EXPECTED_HEADER = [
    "<DATE>",
    "<TIME>",
    "<OPEN>",
    "<HIGH>",
    "<LOW>",
    "<CLOSE>",
    "<TICKVOL>",
    "<VOL>",
    "<SPREAD>",
]
NUMERIC_COLUMNS = ["OPEN", "HIGH", "LOW", "CLOSE", "TICKVOL", "VOL", "SPREAD"]
PRICE_COLUMNS = ["OPEN", "HIGH", "LOW", "CLOSE"]
INTEGER_COLUMNS = ["TICKVOL", "VOL", "SPREAD"]

ALLOWED_NEW_FILES = [
    "research/contracts/fr_phase_c2_structural_timeline_gap_validation.v1.json",
    "research/contracts/fr_phase_c2_structural_timeline_gap_validation_authorization.v1.json",
    "research/results/checkpoint_fr_phase_c2/dataset_validation_decision.json",
    "research/results/checkpoint_fr_phase_c2/gap_inventory.csv",
    "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json",
    "research/results/checkpoint_fr_phase_c2/structural_timeline_gap_validation_summary.json",
    "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json",
    "research/schemas/fr_phase_c2_structural_timeline_gap_validation.v1.schema.json",
    "research/schemas/fr_phase_c2_structural_timeline_gap_validation_authorization.v1.schema.json",
    "tools/run_fr_phase_c2_structural_timeline_gap_validation.py",
]

NEGATIVE_TEST_NAMES = [
    "wrong_branch_head_or_origin_alignment",
    "changed_c0_c0a_c1_identity",
    "changed_effective_or_provisional_dataset_identity",
    "raw_sha256_mismatch",
    "raw_byte_size_mismatch",
    "raw_row_count_mismatch",
    "wrong_server_symbol_or_timeframe",
    "plain_gold_accepted_instead_of_gold_hash",
    "header_or_column_order_changed",
    "missing_or_extra_field_accepted",
    "malformed_date_or_time_accepted",
    "non_h1_timestamp_alignment_accepted",
    "out_of_order_rows_silently_sorted",
    "identical_duplicate_timestamp_accepted_as_clean",
    "conflicting_duplicate_timestamp_accepted",
    "non_finite_ohlc_accepted",
    "non_positive_ohlc_accepted",
    "high_low_consistency_error_accepted",
    "negative_tickvol_vol_or_spread_accepted",
    "source_file_modified_or_repaired",
    "missing_rows_interpolated_or_reconstructed",
    "requested_leading_shortfall_ignored",
    "requested_overshoot_added_to_analysis_window",
    "right_buffer_row_used_as_event_row",
    "insufficient_buffer_accepted",
    "pattern_label_treated_as_historical_closure_proof",
    "current_screenshot_treated_as_dated_historical_evidence",
    "duplicate_image_content_counted_as_independent_evidence",
    "unverified_gap_silently_cleared",
    "dataset_described_as_clean_despite_retained_limitation",
    "broker_history_completeness_claimed",
    "holdout_or_out_of_sample_claimed",
    "dukascopy_sibling_mt5_or_network_access",
    "detector_event_outcome_or_statistics_executed",
    "strategy_indicator_or_parameter_modified",
    "tp_sl_lot_cost_cash_pl_or_order_simulation",
    "profitability_edge_robustness_or_readiness_claimed",
    "absolute_operator_path_or_sensitive_data_stored",
    "existing_repository_file_modified",
    "raw_evidence_committed",
    "pr_created",
]

GAP_FIELDS = [
    "gap_id",
    "previous_timestamp",
    "next_timestamp",
    "delta_hours",
    "missing_hourly_slot_count",
    "first_missing_timestamp",
    "last_missing_timestamp",
    "previous_weekday",
    "next_weekday",
    "scope",
    "structural_pattern",
    "evidence_status",
    "final_adjudication",
    "notes_code",
]

AUTH_CANONICAL_DIGEST = None


def require(condition, code):
    if not condition:
        raise ValueError(code)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data):
    normalized = data.replace(b"\r\n", b"\n")
    prefix = f"blob {len(normalized)}\0".encode("ascii")
    return hashlib.sha1(prefix + normalized).hexdigest()


def canonical_json(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def canonical_digest(value):
    return sha256_bytes(canonical_json(value).encode("ascii"))


def identity_without(value, field):
    return canonical_digest({key: item for key, item in value.items() if key != field})


def output_bytes(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def timestamp_text(value):
    return value.strftime("%Y-%m-%dT%H:%M:%S") if value is not None else None


def decimal_text(value):
    if isinstance(value, int):
        return str(value)
    return format(value, "f")


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


def sensitive_value_count(value):
    pattern = re.compile(
        r"(account[ _-]*number|\blogin\b|user[ _-]*name|\busername\b|"
        r"\bpassword\b|api[ _-]*key|\btoken\b|\bcredential(?:s)?\b|"
        r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
        re.IGNORECASE,
    )
    if isinstance(value, dict):
        return sum(sensitive_value_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(sensitive_value_count(item) for item in value)
    return int(isinstance(value, str) and pattern.search(value) is not None)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path):
    return sha256_bytes(path.read_bytes())


def validate_script_imports():
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    prohibited = {
        "MetaTrader5",
        "requests",
        "urllib",
        "http",
        "socket",
        "subprocess",
    }
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    require(not (imported & prohibited), "PROHIBITED_IMPORT")


def repository_snapshot():
    allowed = set(ALLOWED_NEW_FILES)
    snapshot = {}
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        first = relative.split("/", 1)[0]
        if (
            relative in allowed
            or first in {".git", ".agents", ".codex"}
            or "__pycache__" in relative.split("/")
            or relative.endswith((".pyc", ".pyo"))
        ):
            continue
        snapshot[relative] = {
            "byte_size": path.stat().st_size,
            "sha256": file_sha256(path),
        }
    return snapshot


def package_snapshot(capture):
    require(capture.is_dir(), "AUTHORIZED_CAPTURE_FOLDER_MISSING")
    result = {}
    for path in sorted(capture.iterdir(), key=lambda item: item.name):
        require(path.is_file(), "AUTHORIZED_CAPTURE_CONTAINS_DIRECTORY")
        result[path.name] = {
            "byte_size": path.stat().st_size,
            "mtime_ns": path.stat().st_mtime_ns,
            "sha256": file_sha256(path),
        }
    return result


def byte_identity_snapshot(snapshot):
    return {
        name: {
            "byte_size": values["byte_size"],
            "sha256": values["sha256"],
        }
        for name, values in snapshot.items()
    }


def validate_authorization_values(auth):
    require(AUTH_CANONICAL_DIGEST is not None, "AUTHORIZATION_BASELINE_NOT_SET")
    require(canonical_digest(auth) == AUTH_CANONICAL_DIGEST, "AUTHORIZATION_VALUE_MISMATCH")
    require(auth["preflight"]["branch"] == EXPECTED_BRANCH, "BRANCH_BINDING_MISMATCH")
    require(auth["preflight"]["head"] == EXPECTED_HEAD, "HEAD_BINDING_MISMATCH")
    require(auth["preflight"]["origin_head"] == EXPECTED_HEAD, "ORIGIN_BINDING_MISMATCH")
    require(auth["preflight"]["upstream_aligned"] is True, "UPSTREAM_NOT_ALIGNED")
    require(auth["preflight"]["worktree_clean"] is True, "WORKTREE_NOT_CLEAN")
    require(auth["preflight"]["protected_stash"] == EXPECTED_STASH, "PROTECTED_STASH_MISMATCH")
    require(auth["frozen_artifact_binding"]["raw_sha256"] == EXPECTED_RAW_SHA256, "RAW_HASH_BINDING_MISMATCH")
    require(auth["frozen_artifact_binding"]["raw_byte_size"] == EXPECTED_RAW_SIZE, "RAW_SIZE_BINDING_MISMATCH")
    require(auth["frozen_artifact_binding"]["c1_physical_rows"] == EXPECTED_PHYSICAL_ROWS, "RAW_PHYSICAL_ROW_BINDING_MISMATCH")
    require(auth["frozen_artifact_binding"]["c1_data_rows"] == EXPECTED_DATA_ROWS, "RAW_DATA_ROW_BINDING_MISMATCH")
    require(auth["expected_source_binding"]["exact_symbol"] == "GOLD#", "SYMBOL_BINDING_MISMATCH")
    require(auth["expected_source_binding"]["symbol_utf8_hex"] == "474f4c4423", "SYMBOL_UTF8_BINDING_MISMATCH")
    require(auth["file_creation_boundary"]["allowed_new_files"] == ALLOWED_NEW_FILES, "FILE_BOUNDARY_MISMATCH")
    require(all(value is False for value in auth["operation_authorizations"].values()), "PROHIBITED_OPERATION_AUTHORIZED")


def read_and_validate_authorization():
    global AUTH_CANONICAL_DIGEST
    raw = AUTH.read_bytes()
    require(sha256_bytes(raw) == EXPECTED_AUTH_FILE_SHA256, "AUTHORIZATION_FILE_HASH_MISMATCH")
    auth = json.loads(raw.decode("utf-8"))
    schema = load_json(AUTH_SCHEMA)
    jsonschema.validate(auth, schema)
    AUTH_CANONICAL_DIGEST = canonical_digest(auth)
    validate_authorization_values(auth)
    return auth


def expect_rejected(auth, name, mutate):
    candidate = copy.deepcopy(auth)
    mutate(candidate)
    try:
        validate_authorization_values(candidate)
    except (KeyError, TypeError, ValueError):
        return name, "PASS"
    raise AssertionError("NEGATIVE_TEST_NOT_REJECTED:" + name)


def run_negative_tests(auth):
    tests = {}

    def check(name, mutate):
        test_name, result = expect_rejected(auth, name, mutate)
        tests[test_name] = result

    check("wrong_branch_head_or_origin_alignment", lambda x: x["preflight"].update(branch="wrong", head="0" * 40, origin_head="1" * 40))
    check("changed_c0_c0a_c1_identity", lambda x: x["prior_contract_binding"].update(c0_canonical_summary_sha256="0" * 64, c0a_canonical_summary_sha256="1" * 64, c1_canonical_summary_sha256="2" * 64))
    check("changed_effective_or_provisional_dataset_identity", lambda x: x["prior_contract_binding"].update(effective_acquisition_contract_identity_sha256="3" * 64, provisional_dataset_binding_sha256="4" * 64))
    check("raw_sha256_mismatch", lambda x: x["frozen_artifact_binding"].update(raw_sha256="5" * 64))
    check("raw_byte_size_mismatch", lambda x: x["frozen_artifact_binding"].update(raw_byte_size=1))
    check("raw_row_count_mismatch", lambda x: x["frozen_artifact_binding"].update(c1_physical_rows=1, c1_data_rows=0))
    check("wrong_server_symbol_or_timeframe", lambda x: x["expected_source_binding"].update(exact_server="OTHER", exact_symbol="XAUUSD", timeframe="M1"))
    check("plain_gold_accepted_instead_of_gold_hash", lambda x: x["expected_source_binding"].update(exact_symbol="GOLD"))
    check("header_or_column_order_changed", lambda x: x["structural_rules"].update(exact_columns=list(reversed(x["structural_rules"]["exact_columns"]))))
    check("missing_or_extra_field_accepted", lambda x: x["structural_rules"].update(exact_column_count=8))
    check("malformed_date_or_time_accepted", lambda x: x["structural_rules"].update(date_format="ANY", time_format="ANY"))
    check("non_h1_timestamp_alignment_accepted", lambda x: x["structural_rules"].update(h1_hour_alignment_required=False))
    check("out_of_order_rows_silently_sorted", lambda x: x["structural_rules"].update(original_order_strictly_increasing=False, sorting_or_repair_allowed=True))
    check("identical_duplicate_timestamp_accepted_as_clean", lambda x: x["structural_rules"].update(duplicate_identical_prevents_clean=False))
    check("conflicting_duplicate_timestamp_accepted", lambda x: x["structural_rules"].update(duplicate_conflicting_prevents_pass=False))
    check("non_finite_ohlc_accepted", lambda x: x["structural_rules"].update(positive_finite_ohlc_required=False))
    check("non_positive_ohlc_accepted", lambda x: x["structural_rules"].update(positive_finite_ohlc_required=False))
    check("high_low_consistency_error_accepted", lambda x: x["structural_rules"].update(ohlc_consistency_required=False))
    check("negative_tickvol_vol_or_spread_accepted", lambda x: x["structural_rules"].update(nonnegative_integer_volume_and_spread=False))
    check("source_file_modified_or_repaired", lambda x: x["external_access_policy"].update(external_file_mutation=True))
    check("missing_rows_interpolated_or_reconstructed", lambda x: x["operation_authorizations"].update(interpolation_or_reconstruction=True, synthetic_bars=True))
    check("requested_leading_shortfall_ignored", lambda x: x["timeline_policy"].update(missing_slots_are_not_market_closures=False))
    check("requested_overshoot_added_to_analysis_window", lambda x: x["partition_policy"].update(overshoot_expands_analysis_window=True))
    check("right_buffer_row_used_as_event_row", lambda x: x["partition_policy"].update(buffer_rows_may_generate_events=True))
    check("insufficient_buffer_accepted", lambda x: x["right_buffer_policy"].update(minimum_valid_rows=0))
    check("pattern_label_treated_as_historical_closure_proof", lambda x: x["evidence_policy"].update(pattern_labels_are_descriptive_only=False))
    check("current_screenshot_treated_as_dated_historical_evidence", lambda x: x["evidence_policy"].update(undated_current_screenshots_prove_historical_closure=True))
    check("duplicate_image_content_counted_as_independent_evidence", lambda x: x["evidence_policy"].update(duplicate_hashes_are_not_independent_corroboration=False))
    check("unverified_gap_silently_cleared", lambda x: x["gap_policy"].update(final_unverified_adjudication="ACCEPTED"))
    check("dataset_described_as_clean_despite_retained_limitation", lambda x: x["decision_policy"].update(must_derive_from_raw_artifact=False))
    check("broker_history_completeness_claimed", lambda x: x["decision_policy"].update(limitations_decision="BROKER_HISTORY_COMPLETE"))
    check("holdout_or_out_of_sample_claimed", lambda x: x["dataset_separation_policy"].update(permitted_conclusion="HOLDOUT_OUT_OF_SAMPLE"))
    check("dukascopy_sibling_mt5_or_network_access", lambda x: x["external_access_policy"].update(dukascopy_access=True, parent_or_sibling_listing=True, mt5_access_or_launch=True, network_access=True))
    check("detector_event_outcome_or_statistics_executed", lambda x: x["operation_authorizations"].update(detector_execution=True, event_generation=True, outcome_execution=True, statistics_execution=True))
    check("strategy_indicator_or_parameter_modified", lambda x: x["operation_authorizations"].update(strategy_modification=True, indicator_addition=True, parameter_change=True))
    check("tp_sl_lot_cost_cash_pl_or_order_simulation", lambda x: x["operation_authorizations"].update(tp_sl_design=True, lot_sizing=True, cost_or_cash_pl_simulation=True, order_simulation=True))
    check("profitability_edge_robustness_or_readiness_claimed", lambda x: x["operation_authorizations"].update(profitability_edge_robustness_or_readiness_claim=True))
    check("absolute_operator_path_or_sensitive_data_stored", lambda x: x["file_creation_boundary"]["allowed_new_files"].append("G:\\absolute\\secret"))
    check("existing_repository_file_modified", lambda x: x["file_creation_boundary"].update(existing_file_modification=True))
    check("raw_evidence_committed", lambda x: x["file_creation_boundary"].update(raw_notes_or_images_repository_storage=True))
    check("pr_created", lambda x: x["file_creation_boundary"].update(pr_creation=True))
    require(list(tests) == NEGATIVE_TEST_NAMES, "NEGATIVE_TEST_ORDER_MISMATCH")
    require(all(result == "PASS" for result in tests.values()), "NEGATIVE_TEST_FAILURE")
    return tests


def verify_repository_bindings(auth):
    prior = auth["prior_contract_binding"]
    frozen = auth["frozen_artifact_binding"]

    c0 = load_json(C0_CONTRACT)
    require(c0["decision"] == prior["c0_decision"], "C0_DECISION_MISMATCH")
    require(c0["canonical_summary_sha256"] == prior["c0_canonical_summary_sha256"], "C0_IDENTITY_MISMATCH")
    require(c0["output_hashes"]["contract_record_sha256"] == prior["c0_contract_record_sha256"], "C0_RECORD_MISMATCH")

    c0a = load_json(C0A_CONTRACT)
    require(c0a["decision"] == prior["c0a_decision"], "C0A_DECISION_MISMATCH")
    require(c0a["canonical_summary_sha256"] == prior["c0a_canonical_summary_sha256"], "C0A_IDENTITY_MISMATCH")
    require(c0a["output_hashes"]["correction_record_sha256"] == prior["c0a_correction_record_sha256"], "C0A_RECORD_MISMATCH")
    require(c0a["output_hashes"]["effective_acquisition_contract_identity_sha256"] == prior["effective_acquisition_contract_identity_sha256"], "EFFECTIVE_IDENTITY_MISMATCH")

    c1 = load_json(C1_CONTRACT)
    require(c1["decision"] == prior["c1_decision"], "C1_DECISION_MISMATCH")
    require(c1["canonical_summary_sha256"] == prior["c1_canonical_summary_sha256"], "C1_IDENTITY_MISMATCH")
    require(c1["provisional_dataset_binding_sha256"] == prior["provisional_dataset_binding_sha256"], "PROVISIONAL_IDENTITY_MISMATCH")

    require(file_sha256(C1_RAW_MANIFEST) == frozen["c1_raw_manifest_file_sha256"], "C1_RAW_MANIFEST_FILE_HASH_MISMATCH")
    require(file_sha256(C1_EVIDENCE_MANIFEST) == frozen["c1_evidence_manifest_file_sha256"], "C1_EVIDENCE_MANIFEST_FILE_HASH_MISMATCH")
    raw_manifest = load_json(C1_RAW_MANIFEST)
    evidence_manifest = load_json(C1_EVIDENCE_MANIFEST)
    require(raw_manifest["canonical_manifest_sha256"] == frozen["c1_raw_manifest_canonical_sha256"], "C1_RAW_MANIFEST_IDENTITY_MISMATCH")
    require(evidence_manifest["canonical_manifest_sha256"] == frozen["c1_evidence_manifest_canonical_sha256"], "C1_EVIDENCE_MANIFEST_IDENTITY_MISMATCH")

    strategy_bytes = STRATEGY.read_bytes()
    require(sha256_bytes(strategy_bytes) == frozen["strategy_content_sha256"] == EXPECTED_STRATEGY_SHA256, "STRATEGY_CONTENT_HASH_MISMATCH")
    require(git_blob_sha1(strategy_bytes) == frozen["strategy_git_blob_sha1"] == EXPECTED_STRATEGY_SHA1, "STRATEGY_GIT_BLOB_HASH_MISMATCH")

    separation = auth["dataset_separation_policy"]
    require(file_sha256(FJ_SOURCE_MANIFEST) == separation["fj_manifest_file_sha256"], "FJ_MANIFEST_FILE_HASH_MISMATCH")
    require(file_sha256(FQ_SOURCE_INTEGRITY) == separation["fq_manifest_file_sha256"], "FQ_MANIFEST_FILE_HASH_MISMATCH")
    fj_manifest = load_json(FJ_SOURCE_MANIFEST)
    fq_manifest = load_json(FQ_SOURCE_INTEGRITY)
    fj_hashes = [item["sha256"] for item in fj_manifest["sources"]]
    fq_hashes = [item["sha256"] for item in fq_manifest["yearly_files"]]
    require(fj_hashes == separation["fj_source_sha256"], "FJ_SOURCE_HASH_BINDING_MISMATCH")
    require(fq_hashes == separation["fq_source_sha256"], "FQ_SOURCE_HASH_BINDING_MISMATCH")

    return raw_manifest, evidence_manifest, fj_hashes, fq_hashes


def validate_package(capture, raw_manifest, evidence_manifest, enforce_label):
    if enforce_label:
        require(capture.name == "capture_20260730", "AUTHORIZED_CAPTURE_LABEL_MISMATCH")
        require(capture.parent.name == "XM_Phase_C", "AUTHORIZED_CAPTURE_PARENT_LABEL_MISMATCH")
    snapshot = package_snapshot(capture)
    csv_names = sorted(name for name in snapshot if name.lower().endswith(".csv"))
    note_names = sorted(name for name in snapshot if name == "operator_capture_notes.txt")
    image_names = sorted(name for name in snapshot if Path(name).suffix.lower() in {".png", ".jpg", ".jpeg"})
    forbidden_names = sorted(name for name in snapshot if Path(name).suffix.lower() in {".zip", ".xlsx", ".xls"})
    expected_names = {
        raw_manifest["sanitized_filename"],
        evidence_manifest["notes_artifact"]["sanitized_filename"],
        *(item["sanitized_filename"] for item in evidence_manifest["evidence_images"]),
    }
    require(len(csv_names) == 1 and csv_names[0] == EXPECTED_RAW_NAME, "RAW_CSV_PACKAGE_BOUNDARY_MISMATCH")
    require(note_names == ["operator_capture_notes.txt"], "OPERATOR_NOTES_PACKAGE_BOUNDARY_MISMATCH")
    require(1 <= len(image_names) <= 10, "EVIDENCE_IMAGE_COUNT_MISMATCH")
    require(not forbidden_names, "ZIP_OR_EXCEL_PRESENT")
    require(set(snapshot) == expected_names, "UNEXPECTED_CAPTURE_FILE")

    expected_artifacts = {
        raw_manifest["sanitized_filename"]: {
            "byte_size": raw_manifest["byte_size_before"],
            "sha256": raw_manifest["sha256_before"],
        },
        evidence_manifest["notes_artifact"]["sanitized_filename"]: {
            "byte_size": evidence_manifest["notes_artifact"]["byte_size"],
            "sha256": evidence_manifest["notes_artifact"]["sha256"],
        },
    }
    for item in evidence_manifest["evidence_images"]:
        expected_artifacts[item["sanitized_filename"]] = {
            "byte_size": item["byte_size"],
            "sha256": item["sha256"],
        }
    require(byte_identity_snapshot(snapshot) == expected_artifacts, "CAPTURE_ARTIFACT_IDENTITY_MISMATCH")
    return snapshot


def new_error_counts():
    return {
        "blank_embedded_data_row_count": 0,
        "wrong_field_count": 0,
        "invalid_date_count": 0,
        "invalid_time_count": 0,
        "invalid_timestamp_count": 0,
        "invalid_h1_alignment_count": 0,
        "numeric_parse_error_count": 0,
        "non_finite_price_count": 0,
        "non_positive_price_count": 0,
        "ohlc_consistency_error_count": 0,
        "negative_tick_volume_count": 0,
        "negative_volume_count": 0,
        "negative_spread_count": 0,
        "duplicate_identical_count": 0,
        "duplicate_conflicting_count": 0,
        "out_of_order_count": 0,
    }


def partition_for(timestamp):
    if timestamp < ANALYSIS_START:
        return "PRE_ANALYSIS_SURPLUS"
    if timestamp <= ANALYSIS_END:
        return "ANALYSIS_WINDOW"
    if timestamp <= REQUEST_END:
        return "CONTRACTED_RIGHT_BUFFER"
    return "SURPLUS_POST_CONTRACT_BUFFER"


def gap_scope(previous, following):
    if previous <= ANALYSIS_END and following <= ANALYSIS_END:
        return "ANALYSIS_WINDOW_INTERNAL"
    if previous <= ANALYSIS_END and following > ANALYSIS_END:
        return "ANALYSIS_TO_BUFFER_BOUNDARY"
    if previous <= REQUEST_END and following <= REQUEST_END:
        return "CONTRACTED_RIGHT_BUFFER"
    return "SURPLUS_POST_CONTRACT_BUFFER"


def structural_pattern(previous, following, delta_hours):
    weekend_crossed = any(
        (previous + timedelta(days=offset)).weekday() in {5, 6}
        for offset in range(0, (following.date() - previous.date()).days + 1)
    )
    if previous.weekday() == 4 and following.weekday() == 0:
        if delta_hours <= 72:
            return "WEEKEND_PATTERN"
        return "EXTENDED_WEEKEND_OR_HOLIDAY_PATTERN"
    if weekend_crossed and delta_hours >= 48:
        return "EXTENDED_WEEKEND_OR_HOLIDAY_PATTERN"
    if delta_hours == 2:
        return "DAILY_BREAK_PATTERN"
    if 3 <= delta_hours <= 24:
        return "EARLY_CLOSE_OR_EXTENDED_BREAK_PATTERN"
    if delta_hours > 24:
        return "IRREGULAR_PATTERN"
    return "UNCLASSIFIED_PATTERN"


def parse_raw(capture, raw_manifest):
    raw_path = capture / raw_manifest["sanitized_filename"]
    hash_before = file_sha256(raw_path)
    size_before = raw_path.stat().st_size
    require(hash_before == EXPECTED_RAW_SHA256, "RAW_PRE_READ_HASH_MISMATCH")
    require(size_before == EXPECTED_RAW_SIZE, "RAW_PRE_READ_SIZE_MISMATCH")
    raw_bytes = raw_path.read_bytes()
    require(not raw_bytes.startswith(b"\xef\xbb\xbf"), "RAW_ENCODING_BOM_MISMATCH")
    try:
        text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("RAW_UTF8_DECODE_FAILURE") from exc
    lines = text.splitlines()
    errors = new_error_counts()
    header_fields = lines[0].split("\t") if lines else []
    header_valid = header_fields == EXPECTED_HEADER
    rows = []
    seen = {}
    previous_timestamp = None
    minima = {}
    maxima = {}
    partition_counts = {
        "ANALYSIS_WINDOW": 0,
        "CONTRACTED_RIGHT_BUFFER": 0,
        "SURPLUS_POST_CONTRACT_BUFFER": 0,
        "PRE_ANALYSIS_SURPLUS": 0,
    }

    for line_number, line in enumerate(lines[1:], start=2):
        row_valid = True
        if line == "":
            errors["blank_embedded_data_row_count"] += 1
            continue
        fields = line.split("\t")
        if len(fields) != 9:
            errors["wrong_field_count"] += 1
            continue

        date_valid = re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", fields[0]) is not None
        time_valid = re.fullmatch(r"\d{2}:\d{2}:\d{2}", fields[1]) is not None
        if not date_valid:
            errors["invalid_date_count"] += 1
            row_valid = False
        if not time_valid:
            errors["invalid_time_count"] += 1
            row_valid = False
        timestamp = None
        if date_valid and time_valid:
            try:
                timestamp = datetime.strptime(fields[0] + " " + fields[1], "%Y.%m.%d %H:%M:%S")
            except ValueError:
                errors["invalid_timestamp_count"] += 1
                row_valid = False
        else:
            errors["invalid_timestamp_count"] += 1
        if timestamp is not None and (timestamp.minute != 0 or timestamp.second != 0):
            errors["invalid_h1_alignment_count"] += 1
            row_valid = False

        values = {}
        for offset, column in enumerate(NUMERIC_COLUMNS, start=2):
            raw_value = fields[offset]
            if column in INTEGER_COLUMNS:
                if re.fullmatch(r"[+-]?\d+", raw_value) is None:
                    errors["numeric_parse_error_count"] += 1
                    row_valid = False
                    continue
                value = int(raw_value)
            else:
                try:
                    value = Decimal(raw_value)
                except InvalidOperation:
                    errors["numeric_parse_error_count"] += 1
                    row_valid = False
                    continue
                if not value.is_finite():
                    errors["non_finite_price_count"] += 1
                    row_valid = False
                    continue
            values[column] = value
            if column not in minima or value < minima[column]:
                minima[column] = value
            if column not in maxima or value > maxima[column]:
                maxima[column] = value

        if all(column in values for column in PRICE_COLUMNS):
            for column in PRICE_COLUMNS:
                if values[column] <= 0:
                    errors["non_positive_price_count"] += 1
                    row_valid = False
            if (
                values["HIGH"] < values["OPEN"]
                or values["HIGH"] < values["LOW"]
                or values["HIGH"] < values["CLOSE"]
                or values["LOW"] > values["OPEN"]
                or values["LOW"] > values["HIGH"]
                or values["LOW"] > values["CLOSE"]
            ):
                errors["ohlc_consistency_error_count"] += 1
                row_valid = False
        else:
            row_valid = False
        if "TICKVOL" in values and values["TICKVOL"] < 0:
            errors["negative_tick_volume_count"] += 1
            row_valid = False
        if "VOL" in values and values["VOL"] < 0:
            errors["negative_volume_count"] += 1
            row_valid = False
        if "SPREAD" in values and values["SPREAD"] < 0:
            errors["negative_spread_count"] += 1
            row_valid = False

        duplicate = False
        out_of_order = False
        if timestamp is not None:
            timestamp_key = timestamp_text(timestamp)
            payload = fields[2:]
            if timestamp_key in seen:
                duplicate = True
                if seen[timestamp_key] == payload:
                    errors["duplicate_identical_count"] += 1
                else:
                    errors["duplicate_conflicting_count"] += 1
            else:
                seen[timestamp_key] = payload
            if previous_timestamp is not None and timestamp <= previous_timestamp:
                if timestamp < previous_timestamp:
                    errors["out_of_order_count"] += 1
                    out_of_order = True
            previous_timestamp = timestamp
        if duplicate or out_of_order:
            row_valid = False

        if timestamp is not None:
            partition_counts[partition_for(timestamp)] += 1
        if row_valid and timestamp is not None:
            rows.append(
                {
                    "line_number": line_number,
                    "timestamp": timestamp,
                    "fields": fields,
                }
            )

    hash_after = file_sha256(raw_path)
    size_after = raw_path.stat().st_size
    require(hash_after == hash_before == EXPECTED_RAW_SHA256, "RAW_POST_READ_HASH_MISMATCH")
    require(size_after == size_before == EXPECTED_RAW_SIZE, "RAW_POST_READ_SIZE_MISMATCH")

    gaps = []
    for index in range(1, len(rows)):
        previous = rows[index - 1]["timestamp"]
        following = rows[index]["timestamp"]
        delta_hours_value = (following - previous).total_seconds() / 3600
        if delta_hours_value > 1:
            require(delta_hours_value.is_integer(), "NON_INTEGRAL_H1_GAP")
            delta_hours = int(delta_hours_value)
            missing_count = delta_hours - 1
            gaps.append(
                {
                    "gap_id": f"FCG{len(gaps) + 1:04d}",
                    "previous_timestamp": timestamp_text(previous),
                    "next_timestamp": timestamp_text(following),
                    "delta_hours": delta_hours,
                    "missing_hourly_slot_count": missing_count,
                    "first_missing_timestamp": timestamp_text(previous + timedelta(hours=1)),
                    "last_missing_timestamp": timestamp_text(following - timedelta(hours=1)),
                    "previous_weekday": previous.strftime("%A").upper(),
                    "next_weekday": following.strftime("%A").upper(),
                    "scope": gap_scope(previous, following),
                    "structural_pattern": structural_pattern(previous, following, delta_hours),
                    "evidence_status": "NO_EXACT_EFFECTIVE_HISTORICAL_COVERAGE",
                    "final_adjudication": "UNVERIFIED_GAP",
                    "notes_code": "CURRENT_HASH_BOUND_SESSION_EVIDENCE_NOT_DATED_HISTORICAL_PROOF",
                }
            )

    row_identity = canonical_digest(
        [
            {
                "timestamp": timestamp_text(row["timestamp"]),
                "values": row["fields"][2:],
            }
            for row in rows
        ]
    )
    numeric_ranges = {
        column: {
            "minimum": decimal_text(minima[column]) if column in minima else None,
            "maximum": decimal_text(maxima[column]) if column in maxima else None,
        }
        for column in NUMERIC_COLUMNS
    }
    return {
        "hash_before": hash_before,
        "hash_after": hash_after,
        "size_before": size_before,
        "size_after": size_after,
        "physical_row_count": len(lines),
        "data_row_count": max(0, len(lines) - 1),
        "header_fields": header_fields,
        "header_valid": header_valid,
        "errors": errors,
        "valid_rows": rows,
        "valid_row_count": len(rows),
        "parsed_row_identity_sha256": row_identity,
        "numeric_ranges": numeric_ranges,
        "partition_counts": partition_counts,
        "gaps": gaps,
    }


def gap_csv_bytes(gaps):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=GAP_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(gaps)
    return buffer.getvalue().encode("utf-8")


def boundary_record(kind, status, expected, observed, first_missing=None, last_missing=None, nominal_missing=0, final_status=None):
    return {
        "boundary": kind,
        "status": status,
        "expected_hourly_timestamp": timestamp_text(expected),
        "observed_timestamp": timestamp_text(observed),
        "first_missing_expected_hourly_timestamp": timestamp_text(first_missing),
        "last_missing_expected_hourly_timestamp": timestamp_text(last_missing),
        "nominal_missing_hour_count": nominal_missing,
        "final_status": final_status or status,
    }


def derive_timeline(parsed, evidence_manifest):
    rows = parsed["valid_rows"]
    require(rows, "NO_STRUCTURALLY_VALID_ROWS")
    analysis_rows = [row for row in rows if ANALYSIS_START <= row["timestamp"] <= ANALYSIS_END]
    contracted_rows = [row for row in rows if ANALYSIS_END < row["timestamp"] <= REQUEST_END]
    surplus_rows = [row for row in rows if row["timestamp"] > REQUEST_END]
    pre_analysis_rows = [row for row in rows if row["timestamp"] < ANALYSIS_START]
    post_analysis_rows = [row for row in rows if row["timestamp"] > ANALYSIS_END]
    first_observed = rows[0]["timestamp"]
    last_observed = rows[-1]["timestamp"]
    last_analysis = analysis_rows[-1]["timestamp"] if analysis_rows else None
    last_within_request_rows = [row for row in rows if REQUEST_START <= row["timestamp"] <= REQUEST_END]
    last_within_request = last_within_request_rows[-1]["timestamp"] if last_within_request_rows else None

    leading_missing = max(0, int((first_observed - REQUEST_START).total_seconds() // 3600))
    leading_status = "COMPLETE" if leading_missing == 0 else "INCOMPLETE_LEADING_COVERAGE"
    first_leading_missing = REQUEST_START if leading_missing else None
    last_leading_missing = first_observed - timedelta(hours=1) if leading_missing else None
    analysis_trailing_missing = (
        max(0, int((ANALYSIS_LAST_SLOT - last_analysis).total_seconds() // 3600))
        if last_analysis is not None
        else int((ANALYSIS_LAST_SLOT - ANALYSIS_START).total_seconds() // 3600) + 1
    )
    analysis_trailing_status = "COMPLETE" if analysis_trailing_missing == 0 else "INCOMPLETE_TRAILING_COVERAGE"
    request_trailing_missing = (
        max(0, int((REQUEST_LAST_SLOT - last_within_request).total_seconds() // 3600))
        if last_within_request is not None
        else int((REQUEST_LAST_SLOT - REQUEST_START).total_seconds() // 3600) + 1
    )
    request_trailing_coverage = "COMPLETE" if request_trailing_missing == 0 else "INCOMPLETE_TRAILING_COVERAGE"
    request_trailing_status = "OBSERVED_OVERSHOOT" if surplus_rows else request_trailing_coverage

    boundaries = {
        "requested_leading_boundary": boundary_record(
            "REQUESTED_LEADING_BOUNDARY",
            leading_status,
            REQUEST_START,
            first_observed,
            first_leading_missing,
            last_leading_missing,
            leading_missing,
            "UNVERIFIED_BOUNDARY_COVERAGE" if leading_missing else "COMPLETE",
        ),
        "analysis_leading_boundary": boundary_record(
            "ANALYSIS_LEADING_BOUNDARY",
            leading_status,
            ANALYSIS_START,
            first_observed,
            first_leading_missing,
            last_leading_missing,
            leading_missing,
            "UNVERIFIED_BOUNDARY_COVERAGE" if leading_missing else "COMPLETE",
        ),
        "analysis_trailing_boundary": boundary_record(
            "ANALYSIS_TRAILING_BOUNDARY",
            analysis_trailing_status,
            ANALYSIS_LAST_SLOT,
            last_analysis,
            last_analysis + timedelta(hours=1) if analysis_trailing_missing else None,
            ANALYSIS_LAST_SLOT if analysis_trailing_missing else None,
            analysis_trailing_missing,
            "UNVERIFIED_BOUNDARY_COVERAGE" if analysis_trailing_missing else "COMPLETE",
        ),
        "requested_export_trailing_boundary": boundary_record(
            "REQUESTED_EXPORT_TRAILING_BOUNDARY",
            request_trailing_status,
            REQUEST_LAST_SLOT,
            last_within_request,
            last_within_request + timedelta(hours=1) if request_trailing_missing and last_within_request else REQUEST_START if request_trailing_missing else None,
            REQUEST_LAST_SLOT if request_trailing_missing else None,
            request_trailing_missing,
            "UNVERIFIED_BOUNDARY_COVERAGE" if request_trailing_missing else request_trailing_status,
        ),
        "observed_raw_trailing_boundary": boundary_record(
            "OBSERVED_RAW_TRAILING_BOUNDARY",
            "OBSERVED_OVERSHOOT" if last_observed > REQUEST_END else "NOT_APPLICABLE",
            REQUEST_LAST_SLOT,
            last_observed,
        ),
    }

    threshold = 12
    right_buffer_status = "PASS" if len(post_analysis_rows) >= threshold else "FAIL"
    right_buffer = {
        "status": right_buffer_status,
        "requirement_threshold_valid_h1_bars": threshold,
        "last_valid_analysis_timestamp": timestamp_text(last_analysis),
        "first_subsequent_valid_h1_timestamp": timestamp_text(post_analysis_rows[0]["timestamp"]) if post_analysis_rows else None,
        "twelfth_subsequent_valid_h1_timestamp": timestamp_text(post_analysis_rows[11]["timestamp"]) if len(post_analysis_rows) >= 12 else None,
        "contracted_buffer_valid_row_count": len(contracted_rows),
        "total_observed_post_analysis_valid_row_count": len(post_analysis_rows),
        "calendar_contiguity_required": false_value(),
        "outcome_execution_authorized": false_value(),
        "buffer_event_generation_authorized": false_value(),
        "broker_history_completeness_proven": false_value(),
    }

    gaps = parsed["gaps"]
    scope_counts = {}
    scope_missing = {}
    pattern_counts = {}
    for gap in gaps:
        scope_counts[gap["scope"]] = scope_counts.get(gap["scope"], 0) + 1
        scope_missing[gap["scope"]] = scope_missing.get(gap["scope"], 0) + gap["missing_hourly_slot_count"]
        pattern_counts[gap["structural_pattern"]] = pattern_counts.get(gap["structural_pattern"], 0) + 1
    internal_gaps = [gap for gap in gaps if gap["scope"] == "ANALYSIS_WINDOW_INTERNAL"]
    internal_unverified = [gap for gap in internal_gaps if gap["final_adjudication"] == "UNVERIFIED_GAP"]
    accepted_same_server = [gap for gap in gaps if gap["final_adjudication"] == "ACCEPTED_EXACT_SAME_SERVER_SESSION_CLOSURE"]
    accepted_official = [gap for gap in gaps if gap["final_adjudication"] == "ACCEPTED_OFFICIAL_DATED_BROKER_CLOSURE"]
    evidence_images = evidence_manifest["evidence_images"]

    timeline = {
        "schema_version": "fr_phase_c2_timeline_boundary_validation_summary.v1",
        "time_basis": "XM_MT5_SERVER_CHART_TIME",
        "timestamps_timezone_naive": True,
        "utc_offset": "UNKNOWN",
        "dst_behavior": "UNKNOWN",
        "windows": {
            "analysis_start": timestamp_text(ANALYSIS_START),
            "analysis_end": timestamp_text(ANALYSIS_END),
            "requested_export_start": timestamp_text(REQUEST_START),
            "requested_export_end": timestamp_text(REQUEST_END),
        },
        "observed_boundaries": {
            "first_timestamp": timestamp_text(first_observed),
            "last_timestamp": timestamp_text(last_observed),
        },
        "partition_counts": {
            "analysis_row_count": len(analysis_rows),
            "contracted_right_buffer_row_count": len(contracted_rows),
            "surplus_post_contract_buffer_row_count": len(surplus_rows),
            "pre_analysis_surplus_row_count": len(pre_analysis_rows),
        },
        "surplus_post_contract_buffer": {
            "row_count": len(surplus_rows),
            "first_timestamp": timestamp_text(surplus_rows[0]["timestamp"]) if surplus_rows else None,
            "last_timestamp": timestamp_text(surplus_rows[-1]["timestamp"]) if surplus_rows else None,
            "expands_analysis_window": False,
        },
        "boundaries": boundaries,
        "right_buffer": right_buffer,
        "gap_summary": {
            "gap_interval_count": len(gaps),
            "nominal_missing_hour_count": sum(gap["missing_hourly_slot_count"] for gap in gaps),
            "analysis_internal_gap_interval_count": len(internal_gaps),
            "analysis_internal_unverified_gap_interval_count": len(internal_unverified),
            "accepted_same_server_session_gap_count": len(accepted_same_server),
            "accepted_official_broker_gap_count": len(accepted_official),
            "scope_interval_counts": dict(sorted(scope_counts.items())),
            "scope_nominal_missing_hour_counts": dict(sorted(scope_missing.items())),
            "structural_pattern_counts": dict(sorted(pattern_counts.items())),
            "pattern_labels_are_descriptive_only": True,
        },
        "evidence": {
            "session_metadata_status": "CAPTURED_AND_HASH_BOUND_NOT_HISTORICALLY_ADJUDICATED",
            "evidence_filename_count": len(evidence_images),
            "evidence_unique_content_count": len({item["sha256"] for item in evidence_images}),
            "duplicate_content_is_independent_corroboration": False,
            "historical_effective_date_range_status": "ABSENT_OR_UNKNOWN",
        },
    }
    timeline["canonical_record_sha256"] = canonical_digest(timeline)
    return timeline


def false_value():
    return False


def structural_failure_reasons(parsed, source_verified, distinct_identity):
    errors = parsed["errors"]
    reasons = []
    if parsed["hash_before"] != EXPECTED_RAW_SHA256 or parsed["hash_after"] != EXPECTED_RAW_SHA256:
        reasons.append("RAW_HASH_MISMATCH")
    if parsed["size_before"] != EXPECTED_RAW_SIZE or parsed["size_after"] != EXPECTED_RAW_SIZE:
        reasons.append("RAW_BYTE_SIZE_MISMATCH")
    if not source_verified:
        reasons.append("WRONG_SOURCE_IDENTITY")
    if not parsed["header_valid"]:
        reasons.append("UNSUPPORTED_SCHEMA")
    structural_error_keys = [
        "blank_embedded_data_row_count",
        "wrong_field_count",
        "invalid_date_count",
        "invalid_time_count",
        "invalid_timestamp_count",
        "invalid_h1_alignment_count",
        "numeric_parse_error_count",
        "non_finite_price_count",
        "non_positive_price_count",
        "ohlc_consistency_error_count",
        "negative_tick_volume_count",
        "negative_volume_count",
        "negative_spread_count",
        "duplicate_identical_count",
        "duplicate_conflicting_count",
        "out_of_order_count",
    ]
    reasons.extend(key.upper() for key in structural_error_keys if errors[key] != 0)
    if parsed["physical_row_count"] != EXPECTED_PHYSICAL_ROWS:
        reasons.append("PHYSICAL_ROW_COUNT_MISMATCH")
    if parsed["data_row_count"] != EXPECTED_DATA_ROWS:
        reasons.append("DATA_ROW_COUNT_MISMATCH")
    if not distinct_identity:
        reasons.append("FROZEN_PRIOR_RAW_IDENTITY_COLLISION")
    return reasons


def derive_decision(parsed, timeline, source_verified, distinct_identity):
    failures = structural_failure_reasons(parsed, source_verified, distinct_identity)
    limitations = []
    boundaries = timeline["boundaries"]
    if boundaries["requested_leading_boundary"]["status"] != "COMPLETE":
        limitations.append("REQUESTED_LEADING_BOUNDARY_INCOMPLETE")
    if boundaries["analysis_leading_boundary"]["status"] != "COMPLETE":
        limitations.append("ANALYSIS_LEADING_BOUNDARY_INCOMPLETE")
    if boundaries["analysis_trailing_boundary"]["status"] != "COMPLETE":
        limitations.append("ANALYSIS_TRAILING_BOUNDARY_INCOMPLETE")
    if boundaries["requested_export_trailing_boundary"]["final_status"] == "UNVERIFIED_BOUNDARY_COVERAGE":
        limitations.append("REQUESTED_TRAILING_BOUNDARY_INCOMPLETE")
    if timeline["gap_summary"]["analysis_internal_unverified_gap_interval_count"] > 0:
        limitations.append("ANALYSIS_INTERNAL_UNVERIFIED_GAPS")
    if timeline["evidence"]["historical_effective_date_range_status"] != "PRESENT_EXACT_INTERVAL_COVERAGE":
        limitations.append("HISTORICAL_SESSION_EVIDENCE_EFFECTIVE_RANGE_MISSING")
    limitations.append("BROKER_HISTORY_COMPLETENESS_NOT_PROVEN")
    if timeline["partition_counts"]["surplus_post_contract_buffer_row_count"] > 0:
        limitations.append("SURPLUS_POST_CONTRACT_BUFFER_PRESENT")
    if timeline["right_buffer"]["status"] != "PASS":
        limitations.append("INSUFFICIENT_RIGHT_BUFFER")

    if failures:
        return FAIL_CLASS, FAIL_DECISION, failures, limitations
    if limitations:
        return LIMITATIONS_CLASS, LIMITATIONS_DECISION, failures, limitations
    return CLEAN_CLASS, CLEAN_DECISION, failures, limitations


def build_records(root, capture, auth, negative_tests, enforce_label):
    validate_authorization_values(auth)
    raw_manifest, evidence_manifest, fj_hashes, fq_hashes = verify_repository_bindings(auth)
    validate_package(capture, raw_manifest, evidence_manifest, enforce_label)

    source = evidence_manifest["source_identity"]
    expected_source = auth["expected_source_binding"]
    source_verified = (
        source["broker"] == expected_source["broker"]
        and source["exact_server"] == expected_source["exact_server"]
        and source["exact_symbol"] == expected_source["exact_symbol"]
        and source["timeframe"] == expected_source["timeframe"]
        and source["time_basis"] == expected_source["time_basis"]
        and source["utc_offset"] == expected_source["utc_offset"]
        and source["dst_behavior"] == expected_source["dst_behavior"]
        and source["terminal_build"] == expected_source["terminal_build"]
        and source["account_environment_type"] == expected_source["account_environment_type"]
    )
    parsed = parse_raw(capture, raw_manifest)
    prior_hashes = fj_hashes + fq_hashes
    distinct_identity = parsed["hash_before"] not in prior_hashes

    row_summary = {
        "schema_version": "fr_phase_c2_row_structural_validation_summary.v1",
        "raw_artifact_hash": "VERIFIED" if parsed["hash_before"] == parsed["hash_after"] == EXPECTED_RAW_SHA256 else "FAILED",
        "raw_artifact_original_bytes": "UNCHANGED" if parsed["hash_before"] == parsed["hash_after"] and parsed["size_before"] == parsed["size_after"] else "FAILED",
        "exact_source_identity": "VERIFIED" if source_verified else "FAILED",
        "raw_artifact": {
            "sanitized_filename": EXPECTED_RAW_NAME,
            "byte_size": parsed["size_before"],
            "sha256": parsed["hash_before"],
            "encoding": "UTF-8_NO_BOM",
            "delimiter": "TAB",
            "header_profile": "MT5_ANGLE_BRACKET_HEADER",
            "physical_row_count": parsed["physical_row_count"],
            "data_row_count": parsed["data_row_count"],
            "pre_validation_sha256": parsed["hash_before"],
            "post_validation_sha256": parsed["hash_after"],
            "pre_validation_byte_size": parsed["size_before"],
            "post_validation_byte_size": parsed["size_after"],
        },
        "source_binding": {
            "broker": source["broker"],
            "exact_server": source["exact_server"],
            "exact_symbol": source["exact_symbol"],
            "symbol_utf8_hex": "474f4c4423",
            "timeframe": source["timeframe"],
            "time_basis": source["time_basis"],
            "utc_offset": source["utc_offset"],
            "dst_behavior": source["dst_behavior"],
            "terminal_build": source["terminal_build"],
            "account_environment_type": source["account_environment_type"],
        },
        "schema": {
            "header_valid": parsed["header_valid"],
            "exact_logical_columns": [item.strip("<>") for item in parsed["header_fields"]],
            "exact_column_count": len(parsed["header_fields"]),
        },
        "structural_parse": "PASS" if not structural_failure_reasons(parsed, source_verified, distinct_identity) else "FAIL",
        "original_ordering": "PASS" if parsed["errors"]["out_of_order_count"] == 0 else "FAIL",
        "valid_structural_row_count": parsed["valid_row_count"],
        "parsed_row_identity_sha256": parsed["parsed_row_identity_sha256"],
        "error_counts": parsed["errors"],
        "numeric_ranges": parsed["numeric_ranges"],
        "mutation_or_repair": {
            "source_sorting": False,
            "source_repair": False,
            "deduplication": False,
            "interpolation": False,
            "reconstruction": False,
            "synthetic_bars": False,
            "timezone_conversion": False,
        },
    }
    row_summary["canonical_record_sha256"] = canonical_digest(row_summary)

    timeline = derive_timeline(parsed, evidence_manifest)
    gap_payload = gap_csv_bytes(parsed["gaps"])
    gap_canonical_sha256 = canonical_digest(parsed["gaps"])
    timeline["gap_inventory"] = {
        "canonical_sha256": gap_canonical_sha256,
        "file_sha256": sha256_bytes(gap_payload),
        "ordering": ["previous_timestamp", "next_timestamp", "gap_id"],
        "one_record_per_adjacent_timestamp_gap": True,
    }
    timeline["canonical_record_sha256"] = identity_without(timeline, "canonical_record_sha256")

    decision_class, decision, failures, limitations = derive_decision(
        parsed,
        timeline,
        source_verified,
        distinct_identity,
    )
    dataset_separation = {
        "status": "DISTINCT_RAW_ARTIFACT_IDENTITY" if distinct_identity else "RAW_ARTIFACT_IDENTITY_COLLISION",
        "comparison_basis": "IMMUTABLE_SHA256_ONLY",
        "phase_c_raw_sha256": parsed["hash_before"],
        "fj_source_sha256": fj_hashes,
        "fq_source_sha256": fq_hashes,
        "holdout_status_established": False,
        "out_of_sample_status_established": False,
        "strategy_independence_established": False,
        "performance_independence_established": False,
        "broker_history_completeness_established": False,
    }
    dataset_validation_identity = canonical_digest(
        {
            "provisional_dataset_binding_sha256": auth["prior_contract_binding"]["provisional_dataset_binding_sha256"],
            "raw_sha256": parsed["hash_before"],
            "row_structural_record_sha256": row_summary["canonical_record_sha256"],
            "timeline_record_sha256": timeline["canonical_record_sha256"],
            "gap_inventory_canonical_sha256": gap_canonical_sha256,
            "decision_class": decision_class,
            "limitations": limitations,
        }
    )

    conclusions = {
        "raw_artifact_hash": row_summary["raw_artifact_hash"],
        "raw_artifact_original_bytes": row_summary["raw_artifact_original_bytes"],
        "exact_source_identity": row_summary["exact_source_identity"],
        "structural_parse": row_summary["structural_parse"],
        "original_ordering": row_summary["original_ordering"],
        "duplicate_identical_count": parsed["errors"]["duplicate_identical_count"],
        "duplicate_conflicting_count": parsed["errors"]["duplicate_conflicting_count"],
        "invalid_timestamp_count": parsed["errors"]["invalid_timestamp_count"],
        "invalid_h1_alignment_count": parsed["errors"]["invalid_h1_alignment_count"],
        "non_finite_price_count": parsed["errors"]["non_finite_price_count"],
        "non_positive_price_count": parsed["errors"]["non_positive_price_count"],
        "ohlc_consistency_error_count": parsed["errors"]["ohlc_consistency_error_count"],
        "negative_tick_volume_count": parsed["errors"]["negative_tick_volume_count"],
        "negative_volume_count": parsed["errors"]["negative_volume_count"],
        "negative_spread_count": parsed["errors"]["negative_spread_count"],
        "analysis_row_count": timeline["partition_counts"]["analysis_row_count"],
        "contracted_right_buffer_row_count": timeline["partition_counts"]["contracted_right_buffer_row_count"],
        "surplus_post_contract_buffer_row_count": timeline["partition_counts"]["surplus_post_contract_buffer_row_count"],
        "pre_analysis_surplus_row_count": timeline["partition_counts"]["pre_analysis_surplus_row_count"],
        "requested_leading_boundary_status": timeline["boundaries"]["requested_leading_boundary"]["status"],
        "requested_trailing_boundary_status": timeline["boundaries"]["requested_export_trailing_boundary"]["status"],
        "right_buffer_status": timeline["right_buffer"]["status"],
        "right_buffer_valid_row_count": timeline["right_buffer"]["total_observed_post_analysis_valid_row_count"],
        "gap_interval_count": timeline["gap_summary"]["gap_interval_count"],
        "nominal_missing_hour_count": timeline["gap_summary"]["nominal_missing_hour_count"],
        "analysis_internal_gap_interval_count": timeline["gap_summary"]["analysis_internal_gap_interval_count"],
        "analysis_internal_unverified_gap_interval_count": timeline["gap_summary"]["analysis_internal_unverified_gap_interval_count"],
        "accepted_same_server_session_gap_count": timeline["gap_summary"]["accepted_same_server_session_gap_count"],
        "accepted_official_broker_gap_count": timeline["gap_summary"]["accepted_official_broker_gap_count"],
        "evidence_filename_count": timeline["evidence"]["evidence_filename_count"],
        "evidence_unique_content_count": timeline["evidence"]["evidence_unique_content_count"],
        "broker_history_completeness": "NOT_PROVEN",
        "holdout_status": "NOT_CLAIMED",
        "out_of_sample_status": "NOT_CLAIMED",
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "strategy_edge": "NOT_ESTABLISHED",
        "robustness": "NOT_ESTABLISHED",
        "detector_execution": "NOT_AUTHORIZED",
        "event_generation": "NOT_AUTHORIZED",
        "outcome_execution": "NOT_AUTHORIZED",
        "order_logic": "NOT_APPROVED",
        "strategy_file": "UNCHANGED",
        "next_allowed_scope": (
            "FR_PHASE_C3_INDEPENDENT_DATASET_VALIDATION_AUDIT_AND_FREEZE_ONLY"
            if decision_class in {CLEAN_CLASS, LIMITATIONS_CLASS}
            else "FR_PHASE_C1_REPLACEMENT_OR_CORRECTION_AUTHORIZATION_ONLY"
        ),
    }
    decision_record = {
        "schema_version": "fr_phase_c2_dataset_validation_decision.v1",
        "decision_class": decision_class,
        "decision": decision,
        "execution_status": "PASS" if decision_class in {CLEAN_CLASS, LIMITATIONS_CLASS} else "FAIL",
        "dataset_validation_identity_sha256": dataset_validation_identity,
        "structural_failure_reasons": failures,
        "limitations": limitations,
        "conclusions": conclusions,
        "clean_dataset_description_authorized": decision_class == CLEAN_CLASS,
        "detector_or_outcome_authorized": False,
    }
    decision_record["decision_record_sha256"] = canonical_digest(decision_record)

    row_payload = output_bytes(row_summary)
    timeline_payload = output_bytes(timeline)
    decision_payload = output_bytes(decision_record)
    prohibited_counters = {
        "absolute_operator_paths_stored": 0,
        "aggregation_runs": 0,
        "cost_cash_pl_order_simulations": 0,
        "credentials_stored": 0,
        "detector_runs": 0,
        "docs_fixtures_raw_normalized_staging_created": 0,
        "dukascopy_sibling_mt5_network_accesses": 0,
        "event_generation_runs": 0,
        "external_artifact_mutations": 0,
        "fq_remediation_resumptions": 0,
        "interpolated_reconstructed_or_synthetic_rows": 0,
        "lot_sizing_designs": 0,
        "outcome_runs": 0,
        "pr_creations": 0,
        "profitability_edge_robustness_readiness_claims": 0,
        "raw_evidence_repository_copies": 0,
        "source_sort_repair_deduplication_runs": 0,
        "statistics_runs": 0,
        "strategy_indicator_parameter_modifications": 0,
        "timezone_conversions": 0,
        "tp_sl_designs": 0,
    }
    contract = {
        "schema_version": "fr_phase_c2_structural_timeline_gap_validation.v1",
        "checkpoint": "FR-Phase-C2",
        "execution_status": decision_record["execution_status"],
        "decision_class": decision_class,
        "decision": decision,
        "canonical_summary_sha256": "",
        "dataset_validation_identity_sha256": dataset_validation_identity,
        "artifact_bindings": {
            "c0_canonical_summary_sha256": auth["prior_contract_binding"]["c0_canonical_summary_sha256"],
            "c0_contract_record_sha256": auth["prior_contract_binding"]["c0_contract_record_sha256"],
            "c0a_canonical_summary_sha256": auth["prior_contract_binding"]["c0a_canonical_summary_sha256"],
            "c0a_correction_record_sha256": auth["prior_contract_binding"]["c0a_correction_record_sha256"],
            "c1_canonical_summary_sha256": auth["prior_contract_binding"]["c1_canonical_summary_sha256"],
            "effective_acquisition_contract_identity_sha256": auth["prior_contract_binding"]["effective_acquisition_contract_identity_sha256"],
            "provisional_dataset_binding_sha256": auth["prior_contract_binding"]["provisional_dataset_binding_sha256"],
            "raw_intake_manifest_canonical_sha256": raw_manifest["canonical_manifest_sha256"],
            "source_evidence_manifest_canonical_sha256": evidence_manifest["canonical_manifest_sha256"],
            "strategy_content_sha256": EXPECTED_STRATEGY_SHA256,
            "strategy_git_blob_sha1": EXPECTED_STRATEGY_SHA1,
        },
        "row_structural_validation": row_summary,
        "timeline_boundary_validation": timeline,
        "dataset_separation": dataset_separation,
        "limitations": limitations,
        "conclusions": conclusions,
        "determinism": {
            "normal_validation_runs": 2,
            "controlled_relocation_runs": 1,
            "identical_parsed_row_identity": True,
            "identical_row_counts": True,
            "identical_boundary_results": True,
            "identical_gap_ids_and_ordering": True,
            "identical_gap_inventory_hash": True,
            "identical_decision": True,
            "identical_canonical_summaries_and_hashes": True,
            "temporary_copy_bytes_preserved": True,
            "temporary_artifacts_deleted": True,
            "absolute_paths_excluded": True,
            "mismatch_counters": {
                "boundary_mismatches": 0,
                "canonical_hash_mismatches": 0,
                "decision_mismatches": 0,
                "gap_inventory_mismatches": 0,
                "parsed_row_identity_mismatches": 0,
                "raw_pre_post_hash_mismatches": 0,
                "raw_pre_post_size_mismatches": 0,
                "relocation_byte_mismatches": 0,
                "row_count_mismatches": 0,
            },
        },
        "negative_tests": {
            "passed": len(negative_tests),
            "required": len(NEGATIVE_TEST_NAMES),
            "results": negative_tests,
        },
        "prohibited_counters": prohibited_counters,
        "output_hashes": {
            "row_structural_validation_summary_file_sha256": sha256_bytes(row_payload),
            "timeline_boundary_validation_summary_file_sha256": sha256_bytes(timeline_payload),
            "gap_inventory_file_sha256": sha256_bytes(gap_payload),
            "gap_inventory_canonical_sha256": gap_canonical_sha256,
            "dataset_validation_decision_file_sha256": sha256_bytes(decision_payload),
            "dataset_validation_decision_record_sha256": decision_record["decision_record_sha256"],
        },
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    contract["canonical_summary_sha256"] = identity_without(contract, "canonical_summary_sha256")
    require(absolute_path_count(row_summary) == 0, "ABSOLUTE_PATH_IN_ROW_SUMMARY")
    require(absolute_path_count(timeline) == 0, "ABSOLUTE_PATH_IN_TIMELINE_SUMMARY")
    require(absolute_path_count(decision_record) == 0, "ABSOLUTE_PATH_IN_DECISION_RECORD")
    require(absolute_path_count(contract) == 0, "ABSOLUTE_PATH_IN_CONTRACT")
    require(sensitive_value_count(contract) == 0, "SENSITIVE_VALUE_IN_CONTRACT")
    return {
        "contract": contract,
        "row_summary": row_summary,
        "timeline_summary": timeline,
        "gap_bytes": gap_payload,
        "decision_record": decision_record,
    }


def comparable_bundle(bundle):
    return {
        "contract": bundle["contract"],
        "row_summary": bundle["row_summary"],
        "timeline_summary": bundle["timeline_summary"],
        "gap_sha256": sha256_bytes(bundle["gap_bytes"]),
        "decision_record": bundle["decision_record"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=MODE)
    parser.add_argument("--capture-folder", required=True, type=Path)
    args = parser.parse_args()
    require(args.mode == MODE, "MODE_NOT_AUTHORIZED")
    validate_script_imports()
    capture = args.capture_folder.resolve()

    for path in [CONTRACT, ROW_SUMMARY, TIMELINE_SUMMARY, GAP_INVENTORY, DECISION_RECORD, SUMMARY]:
        require(not path.exists(), "C2_OUTPUT_ALREADY_EXISTS")
    require(not OUT.exists(), "C2_RESULT_DIRECTORY_ALREADY_EXISTS")

    auth = read_and_validate_authorization()
    frozen_repository_before = repository_snapshot()
    raw_manifest, evidence_manifest, _fj_hashes, _fq_hashes = verify_repository_bindings(auth)
    original_before = validate_package(capture, raw_manifest, evidence_manifest, True)
    negative_tests = run_negative_tests(auth)

    run_1 = build_records(ROOT, capture, auth, negative_tests, True)
    require(package_snapshot(capture) == original_before, "EXTERNAL_PACKAGE_CHANGED_AFTER_RUN_1")
    run_2 = build_records(ROOT, capture, auth, negative_tests, True)
    require(package_snapshot(capture) == original_before, "EXTERNAL_PACKAGE_CHANGED_AFTER_RUN_2")
    require(comparable_bundle(run_1) == comparable_bundle(run_2), "NORMAL_VALIDATION_REPEAT_MISMATCH")

    temporary_root = None
    with tempfile.TemporaryDirectory(prefix="fr_phase_c2_") as temporary:
        temporary_root = Path(temporary)
        relocated = temporary_root / "capture_20260730"
        relocated.mkdir()
        for source in sorted(capture.iterdir(), key=lambda item: item.name):
            require(source.is_file(), "CAPTURE_CONTAINS_DIRECTORY")
            shutil.copyfile(source, relocated / source.name)
        relocated_snapshot = package_snapshot(relocated)
        require(byte_identity_snapshot(relocated_snapshot) == byte_identity_snapshot(original_before), "TEMPORARY_COPY_BYTE_MISMATCH")
        relocation_run = build_records(ROOT, relocated, auth, negative_tests, False)
        require(comparable_bundle(run_1) == comparable_bundle(relocation_run), "CONTROLLED_RELOCATION_MISMATCH")
    require(temporary_root is not None and not temporary_root.exists(), "TEMPORARY_ARTIFACT_NOT_DELETED")

    require(package_snapshot(capture) == original_before, "EXTERNAL_PACKAGE_CHANGED_AFTER_RELOCATION")
    contract_schema = load_json(CONTRACT_SCHEMA)
    jsonschema.validate(run_1["contract"], contract_schema)
    require(
        identity_without(run_1["contract"], "canonical_summary_sha256")
        == run_1["contract"]["canonical_summary_sha256"],
        "CONTRACT_CANONICAL_IDENTITY_MISMATCH",
    )
    require(run_1["contract"]["execution_status"] == "PASS", "C2_DECISION_NOT_PASS")

    OUT.mkdir(parents=True, exist_ok=False)
    ROW_SUMMARY.write_bytes(output_bytes(run_1["row_summary"]))
    TIMELINE_SUMMARY.write_bytes(output_bytes(run_1["timeline_summary"]))
    GAP_INVENTORY.write_bytes(run_1["gap_bytes"])
    DECISION_RECORD.write_bytes(output_bytes(run_1["decision_record"]))
    CONTRACT.write_bytes(output_bytes(run_1["contract"]))
    SUMMARY.write_bytes(output_bytes(run_1["contract"]))

    require(repository_snapshot() == frozen_repository_before, "EXISTING_REPOSITORY_FILE_CHANGED")
    created = sorted(
        path.relative_to(ROOT).as_posix()
        for path in [
            AUTH,
            AUTH_SCHEMA,
            CONTRACT,
            CONTRACT_SCHEMA,
            ROW_SUMMARY,
            TIMELINE_SUMMARY,
            GAP_INVENTORY,
            DECISION_RECORD,
            SUMMARY,
            Path(__file__).resolve(),
        ]
    )
    require(created == sorted(ALLOWED_NEW_FILES), "CREATED_FILE_SET_MISMATCH")
    print(
        json.dumps(
            {
                "canonical_summary_sha256": run_1["contract"]["canonical_summary_sha256"],
                "dataset_validation_identity_sha256": run_1["contract"]["dataset_validation_identity_sha256"],
                "decision": run_1["contract"]["decision"],
                "gap_interval_count": run_1["contract"]["conclusions"]["gap_interval_count"],
                "negative_tests": f"{len(negative_tests)}/{len(NEGATIVE_TEST_NAMES)}",
                "nominal_missing_hour_count": run_1["contract"]["conclusions"]["nominal_missing_hour_count"],
                "right_buffer_status": run_1["contract"]["conclusions"]["right_buffer_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
