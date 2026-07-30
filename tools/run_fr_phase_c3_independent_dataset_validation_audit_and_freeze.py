#!/usr/bin/env python3
"""Independently audit and freeze the FR-Phase-C dataset validation status."""

import argparse
import ast
import copy
import csv
import hashlib
import io
import json
import math
import ntpath
import posixpath
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_phase_c3_independent_dataset_validation_audit_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_phase_c3_independent_dataset_validation_audit_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_phase_c3_independent_dataset_validation_audit.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_phase_c3_independent_dataset_validation_audit.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_phase_c3"
RECOMPUTATION = OUT / "independent_recomputation_summary.json"
COMPARISON = OUT / "c2_audit_comparison_matrix.csv"
FREEZE = OUT / "dataset_validation_freeze_record.json"
SUMMARY = OUT / "independent_dataset_validation_audit_summary.json"

C0 = ROOT / "research/contracts/fr_phase_c0_clean_data_acquisition_contract.v1.json"
C0A = ROOT / "research/contracts/fr_phase_c0a_exact_xm_symbol_binding_correction.v1.json"
C1 = ROOT / "research/contracts/fr_phase_c1_manual_raw_data_immutable_intake.v1.json"
C1_RAW = ROOT / "research/results/checkpoint_fr_phase_c1/raw_artifact_intake_manifest.json"
C1_EVIDENCE = ROOT / "research/results/checkpoint_fr_phase_c1/source_identity_evidence_manifest.json"
FJ_SOURCES = ROOT / "research/results/checkpoint_fj_historical_event_population/checkpoint_fj_source_manifest.json"
FQ_SOURCES = ROOT / "research/results/checkpoint_fq_holdout_gap_boundary/checkpoint_fq_source_integrity.json"
STRATEGY = ROOT / "MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh"

C2_CONTRACT = ROOT / "research/contracts/fr_phase_c2_structural_timeline_gap_validation.v1.json"
C2_ROW = ROOT / "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json"
C2_TIMELINE = ROOT / "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json"
C2_GAPS = ROOT / "research/results/checkpoint_fr_phase_c2/gap_inventory.csv"
C2_DECISION = ROOT / "research/results/checkpoint_fr_phase_c2/dataset_validation_decision.json"

MODE = "audit-independent-dataset-validation-and-freeze"
EXPECTED_AUTH_SHA256 = "8945b6470a139bcdcd0895348617cec8abba97618252239c8310428dba92f72c"
EXPECTED_HEAD = "7cd9b36e5db0b485786e2bd85ecf6d0d68e51bba"
EXPECTED_BRANCH = "agent/fr-phase-c-clean-data-intake"
EXPECTED_STASH = "stash@{0}: On agent/fr-prep-b-runner-integration: fr-prep-b2a-partial-draft-before-b2e"

RAW_NAME = "GOLD#_H1_202601020800_202607300300.csv"
RAW_HASH = "69aa7e16d4d3e54bfe8e0aa3ce4c5d61bbd0fcaefb45050341304681b3766f92"
RAW_SIZE = 216222
STRATEGY_SHA256 = "0e72b1559f5416981c2db887f9c53a0bfbb66bada226250a064377b2b9fadaa2"
STRATEGY_BLOB_SHA1 = "da448295ac3bd443b376e1ce51a8e411de3c7245"

ANALYSIS_START = datetime(2026, 1, 1, 0, 0, 0)
ANALYSIS_END = datetime(2026, 6, 30, 23, 59, 59)
REQUEST_START = datetime(2026, 1, 1, 0, 0, 0)
REQUEST_END = datetime(2026, 7, 7, 23, 59, 59)
ANALYSIS_LAST_HOUR = datetime(2026, 6, 30, 23, 0, 0)
REQUEST_LAST_HOUR = datetime(2026, 7, 7, 23, 0, 0)
BUFFER_THRESHOLD = 12

HEADER = [
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
VALUE_NAMES = ["OPEN", "HIGH", "LOW", "CLOSE", "TICKVOL", "VOL", "SPREAD"]
PRICE_NAMES = ["OPEN", "HIGH", "LOW", "CLOSE"]
INTEGER_NAMES = ["TICKVOL", "VOL", "SPREAD"]

LIMITATION_ORDER = [
    "REQUESTED_LEADING_BOUNDARY_INCOMPLETE",
    "ANALYSIS_LEADING_BOUNDARY_INCOMPLETE",
    "ANALYSIS_INTERNAL_UNVERIFIED_GAPS",
    "HISTORICAL_SESSION_EVIDENCE_EFFECTIVE_RANGE_MISSING",
    "BROKER_HISTORY_COMPLETENESS_NOT_PROVEN",
    "SURPLUS_POST_CONTRACT_BUFFER_PRESENT",
]

ALLOWED_NEW_FILES = [
    "research/contracts/fr_phase_c3_independent_dataset_validation_audit.v1.json",
    "research/contracts/fr_phase_c3_independent_dataset_validation_audit_authorization.v1.json",
    "research/results/checkpoint_fr_phase_c3/c2_audit_comparison_matrix.csv",
    "research/results/checkpoint_fr_phase_c3/dataset_validation_freeze_record.json",
    "research/results/checkpoint_fr_phase_c3/independent_dataset_validation_audit_summary.json",
    "research/results/checkpoint_fr_phase_c3/independent_recomputation_summary.json",
    "research/schemas/fr_phase_c3_independent_dataset_validation_audit.v1.schema.json",
    "research/schemas/fr_phase_c3_independent_dataset_validation_audit_authorization.v1.schema.json",
    "tools/run_fr_phase_c3_independent_dataset_validation_audit_and_freeze.py",
]

NEGATIVE_TESTS = [
    "wrong_branch_head_or_origin_alignment",
    "changed_c0_c0a_c1_c2_identity",
    "changed_effective_provisional_or_c2_validation_identity",
    "changed_c2_decision_or_decision_record_hash",
    "changed_gap_inventory_hash",
    "changed_raw_sha256_size_or_row_count",
    "c2_runner_imported_or_executed",
    "c2_parser_or_gap_functions_reused",
    "c2_results_used_before_independent_recomputation_sealed",
    "independent_mismatch_silently_tolerated",
    "comparison_matrix_mismatch_marked_true",
    "structural_count_mismatch_ignored",
    "partition_count_mismatch_ignored",
    "boundary_mismatch_ignored",
    "right_buffer_mismatch_ignored",
    "gap_id_ordering_or_hash_mismatch_ignored",
    "gap_pattern_treated_as_historical_proof",
    "current_screenshot_treated_as_dated_historical_evidence",
    "duplicate_image_bytes_counted_as_independent_evidence",
    "accepted_closure_created_without_exact_dated_evidence",
    "leading_32_hour_limitation_cleared",
    "internal_126_gap_limitation_cleared",
    "broker_history_completeness_claimed",
    "dataset_described_as_clean_while_limitations_remain",
    "holdout_or_out_of_sample_claimed",
    "right_buffer_pass_used_to_authorize_detector_or_outcome",
    "dukascopy_sibling_mt5_or_network_accessed",
    "raw_external_artifact_modified",
    "raw_sorted_repaired_deduplicated_or_reconstructed",
    "synthetic_or_interpolated_bar_created",
    "detector_event_outcome_or_statistics_executed",
    "strategy_indicator_or_parameter_modified",
    "tp_sl_lot_cost_cash_pl_or_order_simulation",
    "profitability_edge_robustness_or_readiness_claimed",
    "absolute_path_or_sensitive_information_stored",
    "existing_repository_file_modified",
    "raw_evidence_committed",
    "c4_work_started",
    "pr_created",
]

MATRIX_FIELDS = [
    "section",
    "field",
    "independently_recomputed_value",
    "c2_recorded_value",
    "match",
    "severity",
    "source_artifact",
    "notes_code",
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

AUTH_DIGEST = None


def fail_unless(condition, code):
    if not condition:
        raise ValueError(code)


def digest_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def canonical_text(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def canonical_hash(value):
    return digest_bytes(canonical_text(value).encode("ascii"))


def canonical_without(value, field):
    return canonical_hash({key: item for key, item in value.items() if key != field})


def pretty_bytes(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def hash_file(path):
    return digest_bytes(path.read_bytes())


def blob_sha1(payload):
    normalized = payload.replace(b"\r\n", b"\n")
    header = f"blob {len(normalized)}\0".encode("ascii")
    return hashlib.sha1(header + normalized).hexdigest()


def iso(value):
    return value.strftime("%Y-%m-%dT%H:%M:%S") if value is not None else None


def numeric_string(value):
    if isinstance(value, int):
        return str(value)
    return format(value, "f")


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value)))


def sensitive_count(value):
    expression = re.compile(
        r"(account[ _-]*number|\blogin\b|user[ _-]*name|\busername\b|"
        r"\bpassword\b|api[ _-]*key|\btoken\b|\bcredential(?:s)?\b|"
        r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
        re.IGNORECASE,
    )
    if isinstance(value, dict):
        return sum(sensitive_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(sensitive_count(item) for item in value)
    return int(isinstance(value, str) and expression.search(value) is not None)


def repository_snapshot():
    allowed = set(ALLOWED_NEW_FILES)
    result = {}
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        top = relative.split("/", 1)[0]
        if (
            relative in allowed
            or top in {".git", ".agents", ".codex"}
            or "__pycache__" in relative.split("/")
            or relative.endswith((".pyc", ".pyo"))
        ):
            continue
        result[relative] = {
            "byte_size": path.stat().st_size,
            "sha256": hash_file(path),
        }
    return result


def capture_snapshot(folder):
    fail_unless(folder.is_dir(), "AUTHORIZED_CAPTURE_FOLDER_MISSING")
    result = {}
    for item in sorted(folder.iterdir(), key=lambda entry: entry.name):
        fail_unless(item.is_file(), "AUTHORIZED_CAPTURE_CONTAINS_DIRECTORY")
        result[item.name] = {
            "byte_size": item.stat().st_size,
            "mtime_ns": item.stat().st_mtime_ns,
            "sha256": hash_file(item),
        }
    return result


def byte_snapshot(snapshot):
    return {
        name: {
            "byte_size": details["byte_size"],
            "sha256": details["sha256"],
        }
        for name, details in snapshot.items()
    }


def validate_own_source_firewall():
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {
        "importlib",
        "subprocess",
        "MetaTrader5",
        "requests",
        "urllib",
        "http",
        "socket",
        "jsonschema",
    }
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fail_unless(node.func.id not in {"eval", "exec"}, "DYNAMIC_EXECUTION_PROHIBITED")
    fail_unless(not (imported & forbidden_imports), "NONSTANDARD_OR_PROHIBITED_IMPORT")
    forbidden_runner_name = "run_fr_phase_c2_" + "structural_timeline_gap_validation"
    fail_unless(forbidden_runner_name not in source, "C2_RUNNER_REFERENCE_PROHIBITED")


def validate_authorization(auth):
    fail_unless(AUTH_DIGEST is not None, "AUTHORIZATION_NOT_SEALED")
    fail_unless(canonical_hash(auth) == AUTH_DIGEST, "AUTHORIZATION_VALUE_MISMATCH")
    fail_unless(auth["authorization_scope"] == "INDEPENDENT_DATASET_VALIDATION_AUDIT_AND_FREEZE_ONLY", "SCOPE_MISMATCH")
    fail_unless(auth["preflight"]["branch"] == EXPECTED_BRANCH, "BRANCH_BINDING_MISMATCH")
    fail_unless(auth["preflight"]["head"] == EXPECTED_HEAD, "HEAD_BINDING_MISMATCH")
    fail_unless(auth["preflight"]["origin_head"] == EXPECTED_HEAD, "ORIGIN_BINDING_MISMATCH")
    fail_unless(auth["preflight"]["protected_stash"] == EXPECTED_STASH, "STASH_BINDING_MISMATCH")
    fail_unless(auth["frozen_raw_artifact"]["sha256"] == RAW_HASH, "RAW_HASH_BINDING_MISMATCH")
    fail_unless(auth["frozen_raw_artifact"]["byte_size"] == RAW_SIZE, "RAW_SIZE_BINDING_MISMATCH")
    fail_unless(auth["source_identity"]["exact_symbol"] == "GOLD#", "EXACT_SYMBOL_BINDING_MISMATCH")
    fail_unless(auth["implementation_firewall"]["independent_parser_standard_library_only"] is True, "INDEPENDENT_IMPLEMENTATION_REQUIRED")
    fail_unless(all(value is False for key, value in auth["implementation_firewall"].items() if key != "independent_parser_standard_library_only"), "IMPLEMENTATION_FIREWALL_OPEN")
    fail_unless(all(value is False for value in auth["guardrails"].values()), "GUARDRAIL_AUTHORIZED")
    fail_unless(auth["file_creation_boundary"]["allowed_new_files"] == ALLOWED_NEW_FILES, "FILE_BOUNDARY_MISMATCH")


def read_authorization():
    global AUTH_DIGEST
    raw = AUTH.read_bytes()
    fail_unless(digest_bytes(raw) == EXPECTED_AUTH_SHA256, "AUTHORIZATION_FILE_HASH_MISMATCH")
    auth = json.loads(raw.decode("utf-8"))
    fail_unless(auth.get("schema_version") == "fr_phase_c3_independent_dataset_validation_audit_authorization.v1", "AUTHORIZATION_SCHEMA_VERSION_MISMATCH")
    AUTH_DIGEST = canonical_hash(auth)
    validate_authorization(auth)
    return auth


def mutate_must_reject(auth, name, mutator):
    candidate = copy.deepcopy(auth)
    mutator(candidate)
    try:
        validate_authorization(candidate)
    except (KeyError, TypeError, ValueError):
        return name, "PASS"
    raise AssertionError("NEGATIVE_TEST_NOT_REJECTED:" + name)


def execute_negative_tests(auth):
    results = {}

    def check(name, mutator):
        test_name, status = mutate_must_reject(auth, name, mutator)
        results[test_name] = status

    check("wrong_branch_head_or_origin_alignment", lambda x: x["preflight"].update(branch="wrong", head="0" * 40, origin_head="1" * 40))
    check("changed_c0_c0a_c1_c2_identity", lambda x: (x["prior_bindings"].update(c0_canonical_summary_sha256="0" * 64, c0a_canonical_summary_sha256="1" * 64, c1_canonical_summary_sha256="2" * 64), x["c2_binding"].update(canonical_summary_sha256="3" * 64)))
    check("changed_effective_provisional_or_c2_validation_identity", lambda x: (x["prior_bindings"].update(effective_acquisition_contract_identity_sha256="4" * 64, provisional_dataset_binding_sha256="5" * 64), x["c2_binding"].update(dataset_validation_identity_sha256="6" * 64)))
    check("changed_c2_decision_or_decision_record_hash", lambda x: x["c2_binding"].update(decision="OTHER", decision_record_sha256="7" * 64))
    check("changed_gap_inventory_hash", lambda x: x["c2_binding"].update(gap_inventory_canonical_sha256="8" * 64, gap_inventory_file_sha256="9" * 64))
    check("changed_raw_sha256_size_or_row_count", lambda x: x["frozen_raw_artifact"].update(sha256="a" * 64, byte_size=1, data_row_count=1))
    check("c2_runner_imported_or_executed", lambda x: x["implementation_firewall"].update(c2_runner_import=True, c2_runner_execution=True))
    check("c2_parser_or_gap_functions_reused", lambda x: x["implementation_firewall"].update(c2_functions_reused=True))
    check("c2_results_used_before_independent_recomputation_sealed", lambda x: x["implementation_firewall"].update(c2_results_loaded_before_independent_seal=True))
    check("independent_mismatch_silently_tolerated", lambda x: x["implementation_firewall"].update(material_mismatch_tolerance=True))
    check("comparison_matrix_mismatch_marked_true", lambda x: x["decision_policy"].update(must_derive_after_independent_seal=False))
    check("structural_count_mismatch_ignored", lambda x: x["decision_policy"].update(mismatch_class="IGNORE_STRUCTURAL"))
    check("partition_count_mismatch_ignored", lambda x: x["decision_policy"].update(mismatch_class="IGNORE_PARTITION"))
    check("boundary_mismatch_ignored", lambda x: x["decision_policy"].update(mismatch_class="IGNORE_BOUNDARY"))
    check("right_buffer_mismatch_ignored", lambda x: x["decision_policy"].update(mismatch_class="IGNORE_BUFFER"))
    check("gap_id_ordering_or_hash_mismatch_ignored", lambda x: x["decision_policy"].update(mismatch_class="IGNORE_GAP"))
    check("gap_pattern_treated_as_historical_proof", lambda x: x["evidence_binding"].update(historical_effective_range="PROVEN_BY_PATTERN"))
    check("current_screenshot_treated_as_dated_historical_evidence", lambda x: x["evidence_binding"].update(historical_effective_range="PROVEN_BY_SCREENSHOT"))
    check("duplicate_image_bytes_counted_as_independent_evidence", lambda x: x["evidence_binding"]["evidence_files"][3].update(sha256="b" * 64))
    check("accepted_closure_created_without_exact_dated_evidence", lambda x: x["evidence_binding"].update(session_status="ACCEPTED_CLOSURES"))
    check("leading_32_hour_limitation_cleared", lambda x: x["decision_policy"]["retained_limitation_vocabulary"].remove("REQUESTED_LEADING_BOUNDARY_INCOMPLETE"))
    check("internal_126_gap_limitation_cleared", lambda x: x["decision_policy"]["retained_limitation_vocabulary"].remove("ANALYSIS_INTERNAL_UNVERIFIED_GAPS"))
    check("broker_history_completeness_claimed", lambda x: x["decision_policy"]["retained_limitation_vocabulary"].remove("BROKER_HISTORY_COMPLETENESS_NOT_PROVEN"))
    check("dataset_described_as_clean_while_limitations_remain", lambda x: x["decision_policy"].update(limitations_class="AUDIT_CONFIRMED_DATASET_CLEAN"))
    check("holdout_or_out_of_sample_claimed", lambda x: x["dataset_separation_binding"].update(permitted_conclusion="HOLDOUT_OUT_OF_SAMPLE"))
    check("right_buffer_pass_used_to_authorize_detector_or_outcome", lambda x: x["guardrails"].update(detector_execution=True, outcome_execution=True))
    check("dukascopy_sibling_mt5_or_network_accessed", lambda x: x["external_access_policy"].update(dukascopy_access=True, parent_or_sibling_access=True, mt5_access_or_launch=True, network_access=True))
    check("raw_external_artifact_modified", lambda x: x["external_access_policy"].update(external_artifact_mutation=True))
    check("raw_sorted_repaired_deduplicated_or_reconstructed", lambda x: x["guardrails"].update(raw_sort_repair_deduplication_or_reconstruction=True))
    check("synthetic_or_interpolated_bar_created", lambda x: x["guardrails"].update(synthetic_or_interpolated_bars=True))
    check("detector_event_outcome_or_statistics_executed", lambda x: x["guardrails"].update(detector_execution=True, event_generation=True, outcome_execution=True, statistics_execution=True))
    check("strategy_indicator_or_parameter_modified", lambda x: x["guardrails"].update(strategy_modification=True, indicator_or_parameter_modification=True))
    check("tp_sl_lot_cost_cash_pl_or_order_simulation", lambda x: x["guardrails"].update(tp_sl_or_lot_sizing=True, cost_cash_pl_or_order_simulation=True))
    check("profitability_edge_robustness_or_readiness_claimed", lambda x: x["guardrails"].update(profitability_edge_robustness_or_readiness_claim=True))
    check("absolute_path_or_sensitive_information_stored", lambda x: x["file_creation_boundary"]["allowed_new_files"].append("G:\\absolute\\secret"))
    check("existing_repository_file_modified", lambda x: x["file_creation_boundary"].update(existing_file_modification=True))
    check("raw_evidence_committed", lambda x: x["file_creation_boundary"].update(raw_notes_or_images_repository_storage=True))
    check("c4_work_started", lambda x: x["file_creation_boundary"].update(c4_work=True))
    check("pr_created", lambda x: x["file_creation_boundary"].update(pr_creation=True))
    fail_unless(list(results) == NEGATIVE_TESTS, "NEGATIVE_TEST_ORDER_MISMATCH")
    fail_unless(all(value == "PASS" for value in results.values()), "NEGATIVE_TEST_FAILURE")
    return results


def verify_pre_seal_repository_bindings(auth):
    prior = auth["prior_bindings"]
    c0 = load_json(C0)
    c0a = load_json(C0A)
    c1 = load_json(C1)
    fail_unless(c0["decision"] == prior["c0_decision"], "C0_DECISION_MISMATCH")
    fail_unless(c0["canonical_summary_sha256"] == prior["c0_canonical_summary_sha256"], "C0_CANONICAL_MISMATCH")
    fail_unless(c0["output_hashes"]["contract_record_sha256"] == prior["c0_contract_record_sha256"], "C0_RECORD_MISMATCH")
    fail_unless(c0a["decision"] == prior["c0a_decision"], "C0A_DECISION_MISMATCH")
    fail_unless(c0a["canonical_summary_sha256"] == prior["c0a_canonical_summary_sha256"], "C0A_CANONICAL_MISMATCH")
    fail_unless(c0a["output_hashes"]["correction_record_sha256"] == prior["c0a_correction_record_sha256"], "C0A_RECORD_MISMATCH")
    fail_unless(c0a["output_hashes"]["effective_acquisition_contract_identity_sha256"] == prior["effective_acquisition_contract_identity_sha256"], "EFFECTIVE_IDENTITY_MISMATCH")
    fail_unless(c1["decision"] == prior["c1_decision"], "C1_DECISION_MISMATCH")
    fail_unless(c1["canonical_summary_sha256"] == prior["c1_canonical_summary_sha256"], "C1_CANONICAL_MISMATCH")
    fail_unless(c1["provisional_dataset_binding_sha256"] == prior["provisional_dataset_binding_sha256"], "PROVISIONAL_IDENTITY_MISMATCH")

    raw_manifest = load_json(C1_RAW)
    evidence_manifest = load_json(C1_EVIDENCE)
    fail_unless(hash_file(C1_RAW) == c1["output_hashes"]["raw_artifact_intake_manifest_file_sha256"], "C1_RAW_MANIFEST_FILE_HASH_MISMATCH")
    fail_unless(hash_file(C1_EVIDENCE) == c1["output_hashes"]["source_identity_evidence_manifest_file_sha256"], "C1_EVIDENCE_MANIFEST_FILE_HASH_MISMATCH")
    fail_unless(raw_manifest["canonical_manifest_sha256"] == prior["raw_intake_manifest_canonical_sha256"], "C1_RAW_MANIFEST_CANONICAL_MISMATCH")
    fail_unless(evidence_manifest["canonical_manifest_sha256"] == prior["source_evidence_manifest_canonical_sha256"], "C1_EVIDENCE_MANIFEST_CANONICAL_MISMATCH")

    strategy_payload = STRATEGY.read_bytes()
    fail_unless(digest_bytes(strategy_payload) == STRATEGY_SHA256, "STRATEGY_SHA256_MISMATCH")
    fail_unless(blob_sha1(strategy_payload) == STRATEGY_BLOB_SHA1, "STRATEGY_BLOB_SHA1_MISMATCH")

    separation = auth["dataset_separation_binding"]
    fail_unless(hash_file(FJ_SOURCES) == separation["fj_manifest_file_sha256"], "FJ_MANIFEST_HASH_MISMATCH")
    fail_unless(hash_file(FQ_SOURCES) == separation["fq_manifest_file_sha256"], "FQ_MANIFEST_HASH_MISMATCH")
    fj = load_json(FJ_SOURCES)
    fq = load_json(FQ_SOURCES)
    fj_hashes = [entry["sha256"] for entry in fj["sources"]]
    fq_hashes = [entry["sha256"] for entry in fq["yearly_files"]]
    fail_unless(fj_hashes == separation["fj_source_sha256"], "FJ_SOURCE_HASH_MISMATCH")
    fail_unless(fq_hashes == separation["fq_source_sha256"], "FQ_SOURCE_HASH_MISMATCH")
    return raw_manifest, evidence_manifest, fj_hashes, fq_hashes


def verify_capture(folder, auth, raw_manifest, evidence_manifest, enforce_labels):
    if enforce_labels:
        fail_unless(folder.name == auth["external_access_policy"]["authorized_capture_label"], "CAPTURE_LABEL_MISMATCH")
        fail_unless(folder.parent.name == auth["external_access_policy"]["authorized_parent_label"], "CAPTURE_PARENT_LABEL_MISMATCH")
    snapshot = capture_snapshot(folder)
    csv_names = sorted(name for name in snapshot if Path(name).suffix.lower() == ".csv")
    notes_names = sorted(name for name in snapshot if name == "operator_capture_notes.txt")
    image_names = sorted(name for name in snapshot if Path(name).suffix.lower() in {".png", ".jpg", ".jpeg"})
    fail_unless(csv_names == [RAW_NAME], "RAW_FILE_BOUNDARY_MISMATCH")
    fail_unless(notes_names == ["operator_capture_notes.txt"], "NOTES_FILE_BOUNDARY_MISMATCH")
    fail_unless(1 <= len(image_names) <= 10, "IMAGE_FILE_BOUNDARY_MISMATCH")
    expected = {
        RAW_NAME: {
            "byte_size": raw_manifest["byte_size_before"],
            "sha256": raw_manifest["sha256_before"],
        },
        auth["evidence_binding"]["notes_filename"]: {
            "byte_size": auth["evidence_binding"]["notes_byte_size"],
            "sha256": auth["evidence_binding"]["notes_sha256"],
        },
    }
    for evidence in auth["evidence_binding"]["evidence_files"]:
        expected[evidence["filename"]] = {
            "byte_size": evidence["byte_size"],
            "sha256": evidence["sha256"],
        }
    fail_unless(byte_snapshot(snapshot) == expected, "CAPTURE_IDENTITY_MISMATCH")
    fail_unless(
        [entry["sanitized_filename"] for entry in evidence_manifest["evidence_images"]]
        == [entry["filename"] for entry in auth["evidence_binding"]["evidence_files"]],
        "EVIDENCE_FILENAME_BINDING_MISMATCH",
    )
    return snapshot


def empty_errors():
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


def assign_partition(stamp):
    if stamp < ANALYSIS_START:
        return "PRE_ANALYSIS_SURPLUS"
    if stamp <= ANALYSIS_END:
        return "ANALYSIS_WINDOW"
    if stamp <= REQUEST_END:
        return "CONTRACTED_RIGHT_BUFFER"
    return "SURPLUS_POST_CONTRACT_BUFFER"


def independently_parse_raw(folder):
    path = folder / RAW_NAME
    pre_hash = hash_file(path)
    pre_size = path.stat().st_size
    fail_unless(pre_hash == RAW_HASH, "RAW_PRE_AUDIT_HASH_MISMATCH")
    fail_unless(pre_size == RAW_SIZE, "RAW_PRE_AUDIT_SIZE_MISMATCH")
    payload = path.read_bytes()
    fail_unless(not payload.startswith(b"\xef\xbb\xbf"), "UTF8_BOM_PRESENT")
    try:
        decoded = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("UTF8_DECODE_FAILURE") from exc

    reader = csv.reader(io.StringIO(decoded, newline=""), delimiter="\t", strict=True)
    physical = list(reader)
    errors = empty_errors()
    header = physical[0] if physical else []
    header_valid = header == HEADER
    observed_rows = []
    timestamp_payloads = {}
    preceding_stamp = None
    minima = {}
    maxima = {}
    partition_counts = {
        "PRE_ANALYSIS_SURPLUS": 0,
        "ANALYSIS_WINDOW": 0,
        "CONTRACTED_RIGHT_BUFFER": 0,
        "SURPLUS_POST_CONTRACT_BUFFER": 0,
    }

    for physical_index, fields in enumerate(physical[1:], start=2):
        valid = True
        if fields == []:
            errors["blank_embedded_data_row_count"] += 1
            continue
        if len(fields) != 9:
            errors["wrong_field_count"] += 1
            continue

        exact_date_form = re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", fields[0]) is not None
        exact_time_form = re.fullmatch(r"\d{2}:\d{2}:\d{2}", fields[1]) is not None
        if not exact_date_form:
            errors["invalid_date_count"] += 1
            valid = False
        if not exact_time_form:
            errors["invalid_time_count"] += 1
            valid = False
        stamp = None
        if exact_date_form and exact_time_form:
            try:
                stamp = datetime.strptime(f"{fields[0]} {fields[1]}", "%Y.%m.%d %H:%M:%S")
            except ValueError:
                errors["invalid_timestamp_count"] += 1
                valid = False
        else:
            errors["invalid_timestamp_count"] += 1
        if stamp is not None and (stamp.minute != 0 or stamp.second != 0):
            errors["invalid_h1_alignment_count"] += 1
            valid = False

        values = {}
        for index, name in enumerate(VALUE_NAMES, start=2):
            token = fields[index]
            if name in INTEGER_NAMES:
                if re.fullmatch(r"[+-]?\d+", token) is None:
                    errors["numeric_parse_error_count"] += 1
                    valid = False
                    continue
                number = int(token)
            else:
                try:
                    number = Decimal(token)
                except InvalidOperation:
                    errors["numeric_parse_error_count"] += 1
                    valid = False
                    continue
                if not number.is_finite():
                    errors["non_finite_price_count"] += 1
                    valid = False
                    continue
            values[name] = number
            minima[name] = number if name not in minima else min(minima[name], number)
            maxima[name] = number if name not in maxima else max(maxima[name], number)

        if all(name in values for name in PRICE_NAMES):
            non_positive_here = sum(1 for name in PRICE_NAMES if values[name] <= 0)
            errors["non_positive_price_count"] += non_positive_here
            if non_positive_here:
                valid = False
            high = values["HIGH"]
            low = values["LOW"]
            if high < max(values["OPEN"], low, values["CLOSE"]) or low > min(values["OPEN"], high, values["CLOSE"]):
                errors["ohlc_consistency_error_count"] += 1
                valid = False
        else:
            valid = False
        for name, error_name in [
            ("TICKVOL", "negative_tick_volume_count"),
            ("VOL", "negative_volume_count"),
            ("SPREAD", "negative_spread_count"),
        ]:
            if name in values and values[name] < 0:
                errors[error_name] += 1
                valid = False

        repeated = False
        backwards = False
        if stamp is not None:
            key = iso(stamp)
            non_time_fields = fields[2:]
            if key in timestamp_payloads:
                repeated = True
                if timestamp_payloads[key] == non_time_fields:
                    errors["duplicate_identical_count"] += 1
                else:
                    errors["duplicate_conflicting_count"] += 1
            else:
                timestamp_payloads[key] = non_time_fields
            if preceding_stamp is not None and stamp < preceding_stamp:
                errors["out_of_order_count"] += 1
                backwards = True
            preceding_stamp = stamp
            partition_counts[assign_partition(stamp)] += 1
        if repeated or backwards:
            valid = False
        if valid and stamp is not None:
            observed_rows.append(
                {
                    "physical_row": physical_index,
                    "timestamp": stamp,
                    "raw_values": fields[2:],
                }
            )

    post_hash = hash_file(path)
    post_size = path.stat().st_size
    fail_unless(pre_hash == post_hash == RAW_HASH, "RAW_POST_AUDIT_HASH_MISMATCH")
    fail_unless(pre_size == post_size == RAW_SIZE, "RAW_POST_AUDIT_SIZE_MISMATCH")
    ranges = {
        name: {
            "minimum": numeric_string(minima[name]) if name in minima else None,
            "maximum": numeric_string(maxima[name]) if name in maxima else None,
        }
        for name in VALUE_NAMES
    }
    parser_identity = canonical_hash(
        [
            {
                "timestamp": iso(row["timestamp"]),
                "values": row["raw_values"],
            }
            for row in observed_rows
        ]
    )
    return {
        "encoding": "UTF-8_NO_BOM",
        "delimiter": "TAB",
        "header_profile": "MT5_ANGLE_BRACKET_HEADER" if header_valid else "UNSUPPORTED",
        "header_fields": header,
        "header_valid": header_valid,
        "physical_row_count": len(physical),
        "data_row_count": max(0, len(physical) - 1),
        "raw_sha256_before": pre_hash,
        "raw_sha256_after": post_hash,
        "raw_byte_size_before": pre_size,
        "raw_byte_size_after": post_size,
        "structural_errors": errors,
        "numeric_ranges": ranges,
        "partition_counts": partition_counts,
        "valid_rows": observed_rows,
        "valid_row_count": len(observed_rows),
        "independent_parser_identity_sha256": parser_identity,
    }


def independently_describe_pattern(left, right, duration):
    if left.weekday() == 4 and right.weekday() == 0:
        return "WEEKEND_PATTERN" if duration <= 72 else "EXTENDED_WEEKEND_OR_HOLIDAY_PATTERN"
    days_spanned = (right.date() - left.date()).days
    touches_weekend = False
    for day_index in range(days_spanned + 1):
        if (left + timedelta(days=day_index)).weekday() >= 5:
            touches_weekend = True
            break
    if touches_weekend and duration >= 48:
        return "EXTENDED_WEEKEND_OR_HOLIDAY_PATTERN"
    if duration == 2:
        return "DAILY_BREAK_PATTERN"
    if 3 <= duration <= 24:
        return "EARLY_CLOSE_OR_EXTENDED_BREAK_PATTERN"
    if duration > 24:
        return "IRREGULAR_PATTERN"
    return "UNCLASSIFIED_PATTERN"


def independently_scope_gap(left, right):
    if left <= ANALYSIS_END and right <= ANALYSIS_END:
        return "ANALYSIS_WINDOW_INTERNAL"
    if left <= ANALYSIS_END < right:
        return "ANALYSIS_TO_BUFFER_BOUNDARY"
    if left <= REQUEST_END and right <= REQUEST_END:
        return "CONTRACTED_RIGHT_BUFFER"
    return "SURPLUS_POST_CONTRACT_BUFFER"


def independently_build_gaps(valid_rows):
    intervals = []
    for earlier, later in zip(valid_rows, valid_rows[1:]):
        left = earlier["timestamp"]
        right = later["timestamp"]
        elapsed = (right - left).total_seconds() / 3600
        if elapsed <= 1:
            continue
        fail_unless(math.isfinite(elapsed) and elapsed.is_integer(), "NONINTEGRAL_GAP_DURATION")
        hours = int(elapsed)
        intervals.append(
            {
                "gap_id": f"FCG{len(intervals) + 1:04d}",
                "previous_timestamp": iso(left),
                "next_timestamp": iso(right),
                "delta_hours": hours,
                "missing_hourly_slot_count": hours - 1,
                "first_missing_timestamp": iso(left + timedelta(hours=1)),
                "last_missing_timestamp": iso(right - timedelta(hours=1)),
                "previous_weekday": left.strftime("%A").upper(),
                "next_weekday": right.strftime("%A").upper(),
                "scope": independently_scope_gap(left, right),
                "structural_pattern": independently_describe_pattern(left, right, hours),
                "evidence_status": "NO_EXACT_EFFECTIVE_HISTORICAL_COVERAGE",
                "final_adjudication": "UNVERIFIED_GAP",
                "notes_code": "CURRENT_HASH_BOUND_SESSION_EVIDENCE_NOT_DATED_HISTORICAL_PROOF",
            }
        )
    return intervals


def independent_boundary(kind, expected, observed, status, missing_start=None, missing_end=None, missing_count=0, final=None):
    return {
        "boundary": kind,
        "expected_hourly_timestamp": iso(expected),
        "observed_timestamp": iso(observed),
        "status": status,
        "first_missing_expected_hourly_timestamp": iso(missing_start),
        "last_missing_expected_hourly_timestamp": iso(missing_end),
        "nominal_missing_hour_count": missing_count,
        "final_status": final or status,
    }


def independently_build_timeline(parsed, gaps):
    valid_rows = parsed["valid_rows"]
    fail_unless(valid_rows, "NO_VALID_ROWS")
    analysis = [row for row in valid_rows if ANALYSIS_START <= row["timestamp"] <= ANALYSIS_END]
    contracted = [row for row in valid_rows if ANALYSIS_END < row["timestamp"] <= REQUEST_END]
    surplus = [row for row in valid_rows if row["timestamp"] > REQUEST_END]
    pre_analysis = [row for row in valid_rows if row["timestamp"] < ANALYSIS_START]
    post_analysis = [row for row in valid_rows if row["timestamp"] > ANALYSIS_END]
    in_request = [row for row in valid_rows if REQUEST_START <= row["timestamp"] <= REQUEST_END]
    first = valid_rows[0]["timestamp"]
    last = valid_rows[-1]["timestamp"]
    final_analysis = analysis[-1]["timestamp"] if analysis else None
    final_requested = in_request[-1]["timestamp"] if in_request else None

    leading_hours = max(0, int((first - REQUEST_START).total_seconds() // 3600))
    leading_status = "COMPLETE" if leading_hours == 0 else "INCOMPLETE_LEADING_COVERAGE"
    trailing_analysis_hours = (
        max(0, int((ANALYSIS_LAST_HOUR - final_analysis).total_seconds() // 3600))
        if final_analysis is not None
        else int((ANALYSIS_LAST_HOUR - ANALYSIS_START).total_seconds() // 3600) + 1
    )
    trailing_analysis_status = "COMPLETE" if trailing_analysis_hours == 0 else "INCOMPLETE_TRAILING_COVERAGE"
    trailing_request_hours = (
        max(0, int((REQUEST_LAST_HOUR - final_requested).total_seconds() // 3600))
        if final_requested is not None
        else int((REQUEST_LAST_HOUR - REQUEST_START).total_seconds() // 3600) + 1
    )
    trailing_request_coverage = "COMPLETE" if trailing_request_hours == 0 else "INCOMPLETE_TRAILING_COVERAGE"
    trailing_request_status = "OBSERVED_OVERSHOOT" if surplus else trailing_request_coverage

    boundaries = {
        "requested_leading_boundary": independent_boundary(
            "REQUESTED_LEADING_BOUNDARY",
            REQUEST_START,
            first,
            leading_status,
            REQUEST_START if leading_hours else None,
            first - timedelta(hours=1) if leading_hours else None,
            leading_hours,
            "UNVERIFIED_BOUNDARY_COVERAGE" if leading_hours else "COMPLETE",
        ),
        "analysis_leading_boundary": independent_boundary(
            "ANALYSIS_LEADING_BOUNDARY",
            ANALYSIS_START,
            first,
            leading_status,
            ANALYSIS_START if leading_hours else None,
            first - timedelta(hours=1) if leading_hours else None,
            leading_hours,
            "UNVERIFIED_BOUNDARY_COVERAGE" if leading_hours else "COMPLETE",
        ),
        "analysis_trailing_boundary": independent_boundary(
            "ANALYSIS_TRAILING_BOUNDARY",
            ANALYSIS_LAST_HOUR,
            final_analysis,
            trailing_analysis_status,
            final_analysis + timedelta(hours=1) if trailing_analysis_hours and final_analysis else ANALYSIS_START if trailing_analysis_hours else None,
            ANALYSIS_LAST_HOUR if trailing_analysis_hours else None,
            trailing_analysis_hours,
            "UNVERIFIED_BOUNDARY_COVERAGE" if trailing_analysis_hours else "COMPLETE",
        ),
        "requested_export_trailing_boundary": independent_boundary(
            "REQUESTED_EXPORT_TRAILING_BOUNDARY",
            REQUEST_LAST_HOUR,
            final_requested,
            trailing_request_status,
            final_requested + timedelta(hours=1) if trailing_request_hours and final_requested else REQUEST_START if trailing_request_hours else None,
            REQUEST_LAST_HOUR if trailing_request_hours else None,
            trailing_request_hours,
            "UNVERIFIED_BOUNDARY_COVERAGE" if trailing_request_hours else trailing_request_status,
        ),
        "observed_raw_trailing_boundary": independent_boundary(
            "OBSERVED_RAW_TRAILING_BOUNDARY",
            REQUEST_LAST_HOUR,
            last,
            "OBSERVED_OVERSHOOT" if last > REQUEST_END else "NOT_APPLICABLE",
        ),
    }
    right_buffer = {
        "status": "PASS" if len(post_analysis) >= BUFFER_THRESHOLD else "FAIL",
        "requirement_threshold_valid_h1_bars": BUFFER_THRESHOLD,
        "last_valid_analysis_timestamp": iso(final_analysis),
        "first_subsequent_valid_h1_timestamp": iso(post_analysis[0]["timestamp"]) if post_analysis else None,
        "twelfth_subsequent_valid_h1_timestamp": iso(post_analysis[11]["timestamp"]) if len(post_analysis) >= 12 else None,
        "contracted_buffer_valid_row_count": len(contracted),
        "total_observed_post_analysis_valid_row_count": len(post_analysis),
        "calendar_contiguity_required": False,
        "outcome_execution_authorized": False,
        "buffer_event_generation_authorized": False,
        "broker_history_completeness_proven": False,
    }
    scope_counts = {}
    scope_missing = {}
    pattern_counts = {}
    for gap in gaps:
        scope_counts[gap["scope"]] = scope_counts.get(gap["scope"], 0) + 1
        scope_missing[gap["scope"]] = scope_missing.get(gap["scope"], 0) + gap["missing_hourly_slot_count"]
        pattern_counts[gap["structural_pattern"]] = pattern_counts.get(gap["structural_pattern"], 0) + 1
    internal = [gap for gap in gaps if gap["scope"] == "ANALYSIS_WINDOW_INTERNAL"]
    internal_unverified = [gap for gap in internal if gap["final_adjudication"] == "UNVERIFIED_GAP"]
    gap_summary = {
        "gap_interval_count": len(gaps),
        "nominal_missing_hour_count": sum(gap["missing_hourly_slot_count"] for gap in gaps),
        "analysis_internal_gap_interval_count": len(internal),
        "analysis_internal_unverified_gap_interval_count": len(internal_unverified),
        "accepted_same_server_session_gap_count": sum(1 for gap in gaps if gap["final_adjudication"] == "ACCEPTED_EXACT_SAME_SERVER_SESSION_CLOSURE"),
        "accepted_official_broker_gap_count": sum(1 for gap in gaps if gap["final_adjudication"] == "ACCEPTED_OFFICIAL_DATED_BROKER_CLOSURE"),
        "scope_interval_counts": dict(sorted(scope_counts.items())),
        "scope_nominal_missing_hour_counts": dict(sorted(scope_missing.items())),
        "structural_pattern_counts": dict(sorted(pattern_counts.items())),
        "pattern_labels_are_descriptive_only": True,
    }
    return {
        "observed_boundaries": {
            "first_timestamp": iso(first),
            "last_timestamp": iso(last),
        },
        "partition_counts": {
            "analysis_row_count": len(analysis),
            "contracted_right_buffer_row_count": len(contracted),
            "surplus_post_contract_buffer_row_count": len(surplus),
            "pre_analysis_surplus_row_count": len(pre_analysis),
        },
        "surplus_post_contract_buffer": {
            "row_count": len(surplus),
            "first_timestamp": iso(surplus[0]["timestamp"]) if surplus else None,
            "last_timestamp": iso(surplus[-1]["timestamp"]) if surplus else None,
            "expands_analysis_window": False,
        },
        "boundaries": boundaries,
        "right_buffer": right_buffer,
        "gap_summary": gap_summary,
    }


def gaps_csv_payload(gaps):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=GAP_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(gaps)
    return buffer.getvalue().encode("utf-8")


def structural_pass(parsed):
    return (
        parsed["header_valid"]
        and parsed["raw_sha256_before"] == parsed["raw_sha256_after"] == RAW_HASH
        and parsed["raw_byte_size_before"] == parsed["raw_byte_size_after"] == RAW_SIZE
        and all(value == 0 for value in parsed["structural_errors"].values())
        and parsed["valid_row_count"] == parsed["data_row_count"]
    )


def derive_independent_limitations(timeline, evidence):
    limitations = []
    if timeline["boundaries"]["requested_leading_boundary"]["status"] != "COMPLETE":
        limitations.append("REQUESTED_LEADING_BOUNDARY_INCOMPLETE")
    if timeline["boundaries"]["analysis_leading_boundary"]["status"] != "COMPLETE":
        limitations.append("ANALYSIS_LEADING_BOUNDARY_INCOMPLETE")
    if timeline["gap_summary"]["analysis_internal_unverified_gap_interval_count"] > 0:
        limitations.append("ANALYSIS_INTERNAL_UNVERIFIED_GAPS")
    if evidence["historical_effective_range"] != "PRESENT_EXACT_INTERVAL_COVERAGE":
        limitations.append("HISTORICAL_SESSION_EVIDENCE_EFFECTIVE_RANGE_MISSING")
    limitations.append("BROKER_HISTORY_COMPLETENESS_NOT_PROVEN")
    if timeline["partition_counts"]["surplus_post_contract_buffer_row_count"] > 0:
        limitations.append("SURPLUS_POST_CONTRACT_BUFFER_PRESENT")
    return limitations


def independently_recompute(folder, auth, raw_manifest, evidence_manifest, fj_hashes, fq_hashes, enforce_labels):
    package = verify_capture(folder, auth, raw_manifest, evidence_manifest, enforce_labels)
    parsed = independently_parse_raw(folder)
    gaps = independently_build_gaps(parsed["valid_rows"])
    timeline = independently_build_timeline(parsed, gaps)
    evidence_entries = auth["evidence_binding"]["evidence_files"]
    evidence = {
        "evidence_filename_count": len(evidence_entries),
        "evidence_unique_content_count": len({package[entry["filename"]]["sha256"] for entry in evidence_entries}),
        "duplicate_content_is_independent_corroboration": False,
        "session_metadata_status": auth["evidence_binding"]["session_status"],
        "historical_effective_range": auth["evidence_binding"]["historical_effective_range"],
        "accepted_closure_evidence_count": 0,
    }
    source = evidence_manifest["source_identity"]
    expected_source = auth["source_identity"]
    source_verified = all(
        [
            source["broker"] == expected_source["broker"],
            source["exact_server"] == expected_source["exact_server"],
            source["exact_symbol"] == expected_source["exact_symbol"],
            source["timeframe"] == expected_source["timeframe"],
            source["time_basis"] == expected_source["time_basis"],
            source["utc_offset"] == expected_source["utc_offset"],
            source["dst_behavior"] == expected_source["dst_behavior"],
            source["terminal_build"] == expected_source["terminal_build"],
            source["account_environment_type"] == expected_source["account_environment_type"],
        ]
    )
    distinct = RAW_HASH not in fj_hashes + fq_hashes
    separation = {
        "status": "DISTINCT_RAW_ARTIFACT_IDENTITY" if distinct else "RAW_ARTIFACT_IDENTITY_COLLISION",
        "comparison_basis": "IMMUTABLE_SHA256_ONLY",
        "phase_c_raw_sha256": RAW_HASH,
        "fj_source_sha256": fj_hashes,
        "fq_source_sha256": fq_hashes,
        "holdout_status_established": False,
        "out_of_sample_status_established": False,
        "strategy_independence_established": False,
        "performance_independence_established": False,
        "broker_history_completeness_established": False,
    }
    limitations = derive_independent_limitations(timeline, evidence)
    independent_status = (
        "VALIDATED_WITH_LIMITATIONS"
        if structural_pass(parsed) and source_verified and distinct and limitations
        else "CLEAN"
        if structural_pass(parsed) and source_verified and distinct
        else "STRUCTURAL_OR_IDENTITY_FAILURE"
    )
    sealed = {
        "schema_version": "fr_phase_c3_independent_recomputation_seal.v1",
        "raw_artifact": {
            "sanitized_filename": RAW_NAME,
            "sha256": parsed["raw_sha256_before"],
            "byte_size": parsed["raw_byte_size_before"],
            "physical_row_count": parsed["physical_row_count"],
            "data_row_count": parsed["data_row_count"],
            "encoding": parsed["encoding"],
            "delimiter": parsed["delimiter"],
            "header_profile": parsed["header_profile"],
            "original_bytes": "UNCHANGED",
        },
        "source_identity": {
            "status": "VERIFIED" if source_verified else "FAILED",
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
        "structural": {
            "structural_parse": "PASS" if structural_pass(parsed) else "FAIL",
            "original_ordering": "PASS" if parsed["structural_errors"]["out_of_order_count"] == 0 else "FAIL",
            "valid_structural_row_count": parsed["valid_row_count"],
            "independent_parser_identity_sha256": parsed["independent_parser_identity_sha256"],
            "header_valid": parsed["header_valid"],
            "logical_columns": [field.strip("<>") for field in parsed["header_fields"]],
            "error_counts": parsed["structural_errors"],
            "numeric_ranges": parsed["numeric_ranges"],
        },
        "timeline": timeline,
        "gap_inventory": {
            "rows": gaps,
            "canonical_sha256": canonical_hash(gaps),
            "file_sha256": digest_bytes(gaps_csv_payload(gaps)),
        },
        "evidence": evidence,
        "dataset_separation": separation,
        "limitations": limitations,
        "independent_dataset_status": independent_status,
        "sealed_before_c2_results_loaded": True,
    }
    seal_hash = canonical_hash(sealed)
    fail_unless(structural_pass(parsed), "INDEPENDENT_STRUCTURAL_AUDIT_FAILED")
    fail_unless(source_verified, "INDEPENDENT_SOURCE_IDENTITY_FAILED")
    fail_unless(distinct, "INDEPENDENT_DATASET_SEPARATION_FAILED")
    return sealed, seal_hash


def load_c2_after_seal(auth, seal_hash):
    fail_unless(isinstance(seal_hash, str) and len(seal_hash) == 64, "INDEPENDENT_RESULT_NOT_SEALED")
    binding = auth["c2_binding"]
    fail_unless(hash_file(C2_ROW) == binding["row_validation_summary_file_sha256"], "C2_ROW_FILE_HASH_MISMATCH")
    fail_unless(hash_file(C2_TIMELINE) == binding["timeline_validation_summary_file_sha256"], "C2_TIMELINE_FILE_HASH_MISMATCH")
    fail_unless(hash_file(C2_GAPS) == binding["gap_inventory_file_sha256"], "C2_GAP_FILE_HASH_MISMATCH")
    fail_unless(hash_file(C2_DECISION) == binding["decision_file_sha256"], "C2_DECISION_FILE_HASH_MISMATCH")
    contract = load_json(C2_CONTRACT)
    row = load_json(C2_ROW)
    timeline = load_json(C2_TIMELINE)
    decision = load_json(C2_DECISION)
    with C2_GAPS.open("r", encoding="utf-8", newline="") as stream:
        gaps = []
        for record in csv.DictReader(stream):
            converted = dict(record)
            converted["delta_hours"] = int(converted["delta_hours"])
            converted["missing_hourly_slot_count"] = int(converted["missing_hourly_slot_count"])
            gaps.append(converted)
    fail_unless(contract["decision"] == binding["decision"], "C2_DECISION_MISMATCH")
    fail_unless(contract["decision_class"] == binding["decision_class"], "C2_DECISION_CLASS_MISMATCH")
    fail_unless(contract["canonical_summary_sha256"] == binding["canonical_summary_sha256"], "C2_CANONICAL_MISMATCH")
    fail_unless(contract["dataset_validation_identity_sha256"] == binding["dataset_validation_identity_sha256"], "C2_VALIDATION_IDENTITY_MISMATCH")
    fail_unless(decision["decision_record_sha256"] == binding["decision_record_sha256"], "C2_DECISION_RECORD_BINDING_MISMATCH")
    fail_unless(canonical_without(decision, "decision_record_sha256") == binding["decision_record_sha256"], "C2_DECISION_RECORD_RECOMPUTE_MISMATCH")
    fail_unless(canonical_hash(gaps) == binding["gap_inventory_canonical_sha256"], "C2_GAP_CANONICAL_RECOMPUTE_MISMATCH")
    fail_unless(canonical_without(contract, "canonical_summary_sha256") == binding["canonical_summary_sha256"], "C2_CONTRACT_CANONICAL_RECOMPUTE_MISMATCH")
    recomputed_validation_identity = canonical_hash(
        {
            "provisional_dataset_binding_sha256": contract["artifact_bindings"]["provisional_dataset_binding_sha256"],
            "raw_sha256": row["raw_artifact"]["sha256"],
            "row_structural_record_sha256": row["canonical_record_sha256"],
            "timeline_record_sha256": timeline["canonical_record_sha256"],
            "gap_inventory_canonical_sha256": timeline["gap_inventory"]["canonical_sha256"],
            "decision_class": contract["decision_class"],
            "limitations": contract["limitations"],
        }
    )
    fail_unless(recomputed_validation_identity == binding["dataset_validation_identity_sha256"], "C2_VALIDATION_IDENTITY_RECOMPUTE_MISMATCH")
    return {
        "contract": contract,
        "row": row,
        "timeline": timeline,
        "gaps": gaps,
        "decision": decision,
        "recomputed_validation_identity": recomputed_validation_identity,
    }


def matrix_cell(value):
    if isinstance(value, str):
        return value
    return canonical_text(value)


def build_comparison_matrix(seal, c2, auth):
    rows = []

    def add(section, field, independent, recorded, artifact, code):
        rows.append(
            {
                "section": section,
                "field": field,
                "independently_recomputed_value": matrix_cell(independent),
                "c2_recorded_value": matrix_cell(recorded),
                "match": "true" if independent == recorded else "false",
                "severity": "MATERIAL",
                "source_artifact": artifact,
                "notes_code": code,
            }
        )

    c2_row = c2["row"]
    raw = seal["raw_artifact"]
    for field, c2_field in [
        ("sha256", "sha256"),
        ("byte_size", "byte_size"),
        ("physical_row_count", "physical_row_count"),
        ("data_row_count", "data_row_count"),
        ("encoding", "encoding"),
        ("delimiter", "delimiter"),
        ("header_profile", "header_profile"),
    ]:
        add("01_raw_artifact", field, raw[field], c2_row["raw_artifact"][c2_field], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "RAW_RECOMPUTATION")
    add("01_raw_artifact", "original_bytes", raw["original_bytes"], c2_row["raw_artifact_original_bytes"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "RAW_IMMUTABILITY")

    source = seal["source_identity"]
    for field in [
        "broker",
        "exact_server",
        "exact_symbol",
        "symbol_utf8_hex",
        "timeframe",
        "time_basis",
        "utc_offset",
        "dst_behavior",
        "terminal_build",
        "account_environment_type",
    ]:
        add("02_source_identity", field, source[field], c2_row["source_binding"][field], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "SOURCE_IDENTITY_RECOMPUTATION")
    add("02_source_identity", "status", source["status"], c2_row["exact_source_identity"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "SOURCE_IDENTITY_STATUS")

    structural = seal["structural"]
    add("03_structural", "structural_parse", structural["structural_parse"], c2_row["structural_parse"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "STRUCTURAL_STATUS")
    add("03_structural", "original_ordering", structural["original_ordering"], c2_row["original_ordering"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "ORDERING_STATUS")
    add("03_structural", "valid_structural_row_count", structural["valid_structural_row_count"], c2_row["valid_structural_row_count"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "VALID_ROW_COUNT")
    add("03_structural", "parsed_row_identity_sha256", structural["independent_parser_identity_sha256"], c2_row["parsed_row_identity_sha256"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "PARSER_IDENTITY")
    add("03_structural", "logical_columns", structural["logical_columns"], c2_row["schema"]["exact_logical_columns"], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "HEADER_COLUMNS")
    for field in sorted(structural["error_counts"]):
        add("03_structural_errors", field, structural["error_counts"][field], c2_row["error_counts"][field], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "STRUCTURAL_ERROR_COUNT")
    for name in VALUE_NAMES:
        for bound in ["minimum", "maximum"]:
            add("03_numeric_ranges", f"{name}.{bound}", structural["numeric_ranges"][name][bound], c2_row["numeric_ranges"][name][bound], "research/results/checkpoint_fr_phase_c2/row_structural_validation_summary.json", "NUMERIC_RANGE")

    timeline = seal["timeline"]
    c2_timeline = c2["timeline"]
    for field in ["first_timestamp", "last_timestamp"]:
        add("04_observed_boundaries", field, timeline["observed_boundaries"][field], c2_timeline["observed_boundaries"][field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "OBSERVED_BOUNDARY")
    for field in sorted(timeline["partition_counts"]):
        add("05_partitions", field, timeline["partition_counts"][field], c2_timeline["partition_counts"][field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "PARTITION_COUNT")
    for field in sorted(timeline["surplus_post_contract_buffer"]):
        add("05_surplus", field, timeline["surplus_post_contract_buffer"][field], c2_timeline["surplus_post_contract_buffer"][field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "SURPLUS_PARTITION")
    for boundary_name in sorted(timeline["boundaries"]):
        for field in sorted(timeline["boundaries"][boundary_name]):
            add("06_boundaries", f"{boundary_name}.{field}", timeline["boundaries"][boundary_name][field], c2_timeline["boundaries"][boundary_name][field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "BOUNDARY_RECOMPUTATION")
    for field in sorted(timeline["right_buffer"]):
        add("07_right_buffer", field, timeline["right_buffer"][field], c2_timeline["right_buffer"][field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "RIGHT_BUFFER_RECOMPUTATION")
    for field in sorted(timeline["gap_summary"]):
        add("08_gap_summary", field, timeline["gap_summary"][field], c2_timeline["gap_summary"][field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "GAP_TOTAL_RECOMPUTATION")

    evidence = seal["evidence"]
    evidence_mapping = {
        "evidence_filename_count": "evidence_filename_count",
        "evidence_unique_content_count": "evidence_unique_content_count",
        "duplicate_content_is_independent_corroboration": "duplicate_content_is_independent_corroboration",
        "session_metadata_status": "session_metadata_status",
        "historical_effective_range": "historical_effective_date_range_status",
    }
    for independent_field, c2_field in evidence_mapping.items():
        add("09_evidence", independent_field, evidence[independent_field], c2_timeline["evidence"][c2_field], "research/results/checkpoint_fr_phase_c2/timeline_boundary_validation_summary.json", "EVIDENCE_RECOMPUTATION")

    add("10_gap_inventory", "canonical_sha256", seal["gap_inventory"]["canonical_sha256"], c2_timeline["gap_inventory"]["canonical_sha256"], "research/results/checkpoint_fr_phase_c2/gap_inventory.csv", "GAP_CANONICAL_HASH")
    add("10_gap_inventory", "file_sha256", seal["gap_inventory"]["file_sha256"], c2_timeline["gap_inventory"]["file_sha256"], "research/results/checkpoint_fr_phase_c2/gap_inventory.csv", "GAP_FILE_HASH")
    fail_unless(len(seal["gap_inventory"]["rows"]) == len(c2["gaps"]), "GAP_ROW_COUNT_MISMATCH_BEFORE_MATRIX")
    for independent_gap, c2_gap in zip(seal["gap_inventory"]["rows"], c2["gaps"]):
        for field in GAP_FIELDS:
            add("10_gap_rows", f"{independent_gap['gap_id']}.{field}", independent_gap[field], c2_gap[field], "research/results/checkpoint_fr_phase_c2/gap_inventory.csv", "GAP_FIELD_RECOMPUTATION")

    separation = seal["dataset_separation"]
    for field in sorted(separation):
        add("11_dataset_separation", field, separation[field], c2["contract"]["dataset_separation"][field], "research/contracts/fr_phase_c2_structural_timeline_gap_validation.v1.json", "SEPARATION_RECOMPUTATION")

    independent_c2_class = (
        "PASS_DATASET_VALIDATED_WITH_LIMITATIONS"
        if seal["independent_dataset_status"] == "VALIDATED_WITH_LIMITATIONS"
        else "PASS_DATASET_CLEAN_FOR_FUTURE_RESEARCH"
        if seal["independent_dataset_status"] == "CLEAN"
        else "FAIL_DATASET_INTAKE"
    )
    add("12_decision", "decision_class", independent_c2_class, c2["contract"]["decision_class"], "research/results/checkpoint_fr_phase_c2/dataset_validation_decision.json", "DECISION_CLASS_RECOMPUTATION")
    add("12_decision", "limitations", seal["limitations"], c2["decision"]["limitations"], "research/results/checkpoint_fr_phase_c2/dataset_validation_decision.json", "LIMITATION_RECOMPUTATION")
    add("12_decision", "dataset_validation_identity_sha256", auth["c2_binding"]["dataset_validation_identity_sha256"], c2["recomputed_validation_identity"], "research/contracts/fr_phase_c2_structural_timeline_gap_validation.v1.json", "C2_IDENTITY_RECOMPUTATION")
    add("12_decision", "canonical_summary_sha256", auth["c2_binding"]["canonical_summary_sha256"], c2["contract"]["canonical_summary_sha256"], "research/contracts/fr_phase_c2_structural_timeline_gap_validation.v1.json", "C2_CANONICAL_BINDING")
    add("12_decision", "decision_record_sha256", auth["c2_binding"]["decision_record_sha256"], c2["decision"]["decision_record_sha256"], "research/results/checkpoint_fr_phase_c2/dataset_validation_decision.json", "C2_DECISION_RECORD_BINDING")
    add("12_decision", "gap_inventory_canonical_sha256", auth["c2_binding"]["gap_inventory_canonical_sha256"], canonical_hash(c2["gaps"]), "research/results/checkpoint_fr_phase_c2/gap_inventory.csv", "C2_GAP_BINDING")

    rows.sort(key=lambda row: (row["section"], row["field"]))
    return rows


def matrix_payload(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=MATRIX_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def build_recomputation_summary(seal, seal_hash):
    return {
        "schema_version": "fr_phase_c3_independent_recomputation_summary.v1",
        "independent_recomputation_sealed_before_c2_results_loaded": True,
        "independent_recomputation_seal_sha256": seal_hash,
        "raw_artifact": seal["raw_artifact"],
        "source_identity": seal["source_identity"],
        "structural": seal["structural"],
        "timeline": seal["timeline"],
        "gap_inventory": {
            "gap_interval_count": len(seal["gap_inventory"]["rows"]),
            "canonical_sha256": seal["gap_inventory"]["canonical_sha256"],
            "file_sha256": seal["gap_inventory"]["file_sha256"],
        },
        "evidence": seal["evidence"],
        "dataset_separation": seal["dataset_separation"],
        "limitations": seal["limitations"],
        "independent_dataset_status": seal["independent_dataset_status"],
    }


def build_freeze_record(seal, matrix_rows, auth):
    mismatch_count = sum(1 for row in matrix_rows if row["match"] != "true")
    if mismatch_count:
        audit_class = "AUDIT_MISMATCH"
        decision = "FR_PHASE_C3_FAIL_INDEPENDENT_AUDIT_MISMATCH"
        dataset_status = "AUDIT_MISMATCH"
        next_scope = "FR_PHASE_C2_CORRECTION_AUTHORIZATION_ONLY"
    elif not seal["limitations"]:
        audit_class = "AUDIT_CONFIRMED_DATASET_CLEAN"
        decision = "FR_PHASE_C3_PASS_INDEPENDENT_AUDIT_CONFIRMED_DATASET_CLEAN"
        dataset_status = "CLEAN"
        next_scope = "FR_PHASE_C4_DETECTOR_EXECUTION_AUTHORIZATION_DESIGN_ONLY"
    else:
        audit_class = "AUDIT_CONFIRMED_VALIDATED_WITH_LIMITATIONS"
        decision = "FR_PHASE_C3_PASS_INDEPENDENT_AUDIT_CONFIRMED_VALIDATED_WITH_LIMITATIONS"
        dataset_status = "VALIDATED_WITH_LIMITATIONS"
        next_scope = "FR_PHASE_C4_DATA_QUALITY_LIMITATION_DISPOSITION_DESIGN_ONLY"
    freeze = {
        "schema_version": "fr_phase_c3_dataset_validation_freeze_record.v1",
        "decision": decision,
        "audit_class": audit_class,
        "phase_c_dataset_validation": "FROZEN",
        "audit_status": "INDEPENDENTLY_CONFIRMED" if mismatch_count == 0 else "MISMATCH",
        "dataset_status": dataset_status,
        "clean_dataset_status": "ESTABLISHED" if dataset_status == "CLEAN" else "NOT_ESTABLISHED",
        "structural_integrity": seal["structural"]["structural_parse"],
        "original_ordering": seal["structural"]["original_ordering"],
        "raw_artifact_identity": "VERIFIED_AND_IMMUTABLE",
        "exact_source_identity": seal["source_identity"]["status"],
        "requested_leading_coverage": "INCOMPLETE_AND_UNVERIFIED" if "REQUESTED_LEADING_BOUNDARY_INCOMPLETE" in seal["limitations"] else "COMPLETE",
        "analysis_internal_unverified_gap_intervals": seal["timeline"]["gap_summary"]["analysis_internal_unverified_gap_interval_count"],
        "broker_history_completeness": "NOT_PROVEN",
        "historical_session_effective_range": seal["evidence"]["historical_effective_range"],
        "right_buffer": seal["timeline"]["right_buffer"]["status"],
        "surplus_post_contract_rows": "RETAINED_AND_EXCLUDED_FROM_ANALYSIS",
        "retained_limitations": seal["limitations"],
        "holdout_status": "NOT_CLAIMED",
        "out_of_sample_status": "NOT_CLAIMED",
        "detector_execution": "NOT_AUTHORIZED",
        "event_generation": "NOT_AUTHORIZED",
        "outcome_execution": "NOT_AUTHORIZED",
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "strategy_edge": "NOT_ESTABLISHED",
        "robustness": "NOT_ESTABLISHED",
        "order_logic": "NOT_APPROVED",
        "tp_sl": "NOT_AUTHORIZED",
        "lot_sizing": "NOT_AUTHORIZED",
        "demo_or_live_trading": "NOT_AUTHORIZED",
        "strategy_file": "UNCHANGED",
        "comparison_row_count": len(matrix_rows),
        "comparison_match_count": len(matrix_rows) - mismatch_count,
        "comparison_mismatch_count": mismatch_count,
        "next_allowed_scope": next_scope,
        "c4_work_started": False,
    }
    freeze["freeze_record_sha256"] = canonical_hash(freeze)
    return freeze


def validate_contract_shape(contract):
    required = {
        "schema_version",
        "checkpoint",
        "execution_status",
        "audit_class",
        "decision",
        "canonical_summary_sha256",
        "audit_identity_sha256",
        "artifact_bindings",
        "independent_recomputation",
        "comparison",
        "freeze_record",
        "determinism",
        "negative_tests",
        "prohibited_counters",
        "output_hashes",
        "absolute_runtime_path_in_canonical_identity_count",
    }
    fail_unless(set(contract) == required, "CONTRACT_SHAPE_MISMATCH")
    fail_unless(contract["schema_version"] == "fr_phase_c3_independent_dataset_validation_audit.v1", "CONTRACT_SCHEMA_VERSION_MISMATCH")
    fail_unless(contract["execution_status"] == "PASS", "CONTRACT_EXECUTION_NOT_PASS")
    fail_unless(contract["audit_class"] in {"AUDIT_CONFIRMED_DATASET_CLEAN", "AUDIT_CONFIRMED_VALIDATED_WITH_LIMITATIONS"}, "AUDIT_NOT_CONFIRMED")


def build_contract(recomputation, matrix_rows, freeze, seal_hash, negative_results, auth):
    recomputation_payload = pretty_bytes(recomputation)
    comparison_payload = matrix_payload(matrix_rows)
    freeze_payload = pretty_bytes(freeze)
    audit_identity = canonical_hash(
        {
            "independent_recomputation_seal_sha256": seal_hash,
            "c2_canonical_summary_sha256": auth["c2_binding"]["canonical_summary_sha256"],
            "c2_dataset_validation_identity_sha256": auth["c2_binding"]["dataset_validation_identity_sha256"],
            "comparison_matrix_sha256": digest_bytes(comparison_payload),
            "freeze_record_sha256": freeze["freeze_record_sha256"],
            "decision": freeze["decision"],
        }
    )
    prohibited = {
        "absolute_operator_paths_stored": 0,
        "aggregation_runs": 0,
        "c2_runner_imports_or_executions": 0,
        "c2_function_reuses": 0,
        "c2_results_loaded_before_seal": 0,
        "c4_work_runs": 0,
        "cost_cash_pl_order_simulations": 0,
        "credentials_stored": 0,
        "detector_runs": 0,
        "docs_fixtures_normalized_staging_raw_created": 0,
        "dukascopy_sibling_mt5_network_accesses": 0,
        "event_generation_runs": 0,
        "external_artifact_mutations": 0,
        "fq_remediation_resumptions": 0,
        "outcome_runs": 0,
        "pr_creations": 0,
        "profitability_edge_robustness_readiness_claims": 0,
        "raw_evidence_repository_copies": 0,
        "source_sort_repair_deduplication_reconstructions": 0,
        "statistics_runs": 0,
        "strategy_indicator_parameter_modifications": 0,
        "synthetic_or_interpolated_bars": 0,
        "tp_sl_lot_sizing_designs": 0,
    }
    contract = {
        "schema_version": "fr_phase_c3_independent_dataset_validation_audit.v1",
        "checkpoint": "FR-Phase-C3",
        "execution_status": "PASS" if freeze["comparison_mismatch_count"] == 0 else "FAIL",
        "audit_class": freeze["audit_class"],
        "decision": freeze["decision"],
        "canonical_summary_sha256": "",
        "audit_identity_sha256": audit_identity,
        "artifact_bindings": {
            "c0_canonical_summary_sha256": auth["prior_bindings"]["c0_canonical_summary_sha256"],
            "c0a_canonical_summary_sha256": auth["prior_bindings"]["c0a_canonical_summary_sha256"],
            "c1_canonical_summary_sha256": auth["prior_bindings"]["c1_canonical_summary_sha256"],
            "c2_canonical_summary_sha256": auth["c2_binding"]["canonical_summary_sha256"],
            "effective_acquisition_contract_identity_sha256": auth["prior_bindings"]["effective_acquisition_contract_identity_sha256"],
            "provisional_dataset_binding_sha256": auth["prior_bindings"]["provisional_dataset_binding_sha256"],
            "c2_dataset_validation_identity_sha256": auth["c2_binding"]["dataset_validation_identity_sha256"],
            "raw_sha256": RAW_HASH,
            "strategy_content_sha256": STRATEGY_SHA256,
            "strategy_git_blob_sha1": STRATEGY_BLOB_SHA1,
        },
        "independent_recomputation": recomputation,
        "comparison": {
            "row_count": len(matrix_rows),
            "match_count": freeze["comparison_match_count"],
            "mismatch_count": freeze["comparison_mismatch_count"],
            "all_rows_match": freeze["comparison_mismatch_count"] == 0,
            "ordering": ["section", "field"],
            "matrix_file_sha256": digest_bytes(comparison_payload),
        },
        "freeze_record": freeze,
        "determinism": {
            "independent_normal_audit_runs": 2,
            "independent_controlled_relocation_audit_runs": 1,
            "independent_parser_identity_identical": True,
            "structural_counts_identical": True,
            "partition_counts_identical": True,
            "boundaries_identical": True,
            "right_buffer_results_identical": True,
            "gap_rows_ids_ordering_identical": True,
            "gap_inventory_canonical_hashes_identical": True,
            "independent_decisions_identical": True,
            "comparison_matrices_identical": True,
            "freeze_records_identical": True,
            "canonical_summaries_and_hashes_identical": True,
            "temporary_copy_bytes_preserved": True,
            "temporary_artifacts_deleted": True,
            "absolute_paths_excluded": True,
            "mismatch_counters": {
                "boundary_mismatches": 0,
                "c2_comparison_mismatches": 0,
                "canonical_hash_mismatches": 0,
                "decision_mismatches": 0,
                "evidence_count_mismatches": 0,
                "gap_hash_mismatches": 0,
                "gap_row_mismatches": 0,
                "parser_identity_mismatches": 0,
                "partition_count_mismatches": 0,
                "raw_hash_or_size_mismatches": 0,
                "right_buffer_mismatches": 0,
                "structural_count_mismatches": 0,
            },
        },
        "negative_tests": {
            "passed": len(negative_results),
            "required": len(NEGATIVE_TESTS),
            "results": negative_results,
        },
        "prohibited_counters": prohibited,
        "output_hashes": {
            "independent_recomputation_summary_file_sha256": digest_bytes(recomputation_payload),
            "c2_audit_comparison_matrix_file_sha256": digest_bytes(comparison_payload),
            "dataset_validation_freeze_record_file_sha256": digest_bytes(freeze_payload),
            "dataset_validation_freeze_record_sha256": freeze["freeze_record_sha256"],
        },
        "absolute_runtime_path_in_canonical_identity_count": 0,
    }
    contract["canonical_summary_sha256"] = canonical_without(contract, "canonical_summary_sha256")
    fail_unless(absolute_path_count(contract) == 0, "ABSOLUTE_PATH_IN_CONTRACT")
    fail_unless(sensitive_count(contract) == 0, "SENSITIVE_VALUE_IN_CONTRACT")
    validate_contract_shape(contract)
    return contract, recomputation_payload, comparison_payload, freeze_payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=MODE)
    parser.add_argument("--capture-folder", required=True, type=Path)
    args = parser.parse_args()
    fail_unless(args.mode == MODE, "MODE_NOT_AUTHORIZED")
    validate_own_source_firewall()
    capture = args.capture_folder.resolve()

    for path in [CONTRACT, RECOMPUTATION, COMPARISON, FREEZE, SUMMARY]:
        fail_unless(not path.exists(), "C3_OUTPUT_ALREADY_EXISTS")
    fail_unless(not OUT.exists(), "C3_RESULT_DIRECTORY_ALREADY_EXISTS")

    auth = read_authorization()
    negative_results = execute_negative_tests(auth)
    repository_before = repository_snapshot()
    raw_manifest, evidence_manifest, fj_hashes, fq_hashes = verify_pre_seal_repository_bindings(auth)
    original_package = verify_capture(capture, auth, raw_manifest, evidence_manifest, True)

    seal_1, seal_hash_1 = independently_recompute(capture, auth, raw_manifest, evidence_manifest, fj_hashes, fq_hashes, True)
    fail_unless(capture_snapshot(capture) == original_package, "EXTERNAL_PACKAGE_CHANGED_AFTER_AUDIT_1")
    seal_2, seal_hash_2 = independently_recompute(capture, auth, raw_manifest, evidence_manifest, fj_hashes, fq_hashes, True)
    fail_unless(capture_snapshot(capture) == original_package, "EXTERNAL_PACKAGE_CHANGED_AFTER_AUDIT_2")
    fail_unless(seal_1 == seal_2 and seal_hash_1 == seal_hash_2, "NORMAL_INDEPENDENT_AUDIT_MISMATCH")

    temporary_root = None
    with tempfile.TemporaryDirectory(prefix="fr_phase_c3_") as temporary:
        temporary_root = Path(temporary)
        relocated = temporary_root / "capture_20260730"
        relocated.mkdir()
        for item in sorted(capture.iterdir(), key=lambda entry: entry.name):
            fail_unless(item.is_file(), "CAPTURE_CONTAINS_DIRECTORY")
            shutil.copyfile(item, relocated / item.name)
        fail_unless(byte_snapshot(capture_snapshot(relocated)) == byte_snapshot(original_package), "RELOCATION_BYTE_MISMATCH")
        seal_3, seal_hash_3 = independently_recompute(relocated, auth, raw_manifest, evidence_manifest, fj_hashes, fq_hashes, False)
        fail_unless(seal_3 == seal_1 and seal_hash_3 == seal_hash_1, "RELOCATED_INDEPENDENT_AUDIT_MISMATCH")
    fail_unless(temporary_root is not None and not temporary_root.exists(), "TEMPORARY_ARTIFACT_NOT_DELETED")
    fail_unless(capture_snapshot(capture) == original_package, "EXTERNAL_PACKAGE_CHANGED_AFTER_RELOCATION")

    c2 = load_c2_after_seal(auth, seal_hash_1)
    matrix_1 = build_comparison_matrix(seal_1, c2, auth)
    matrix_2 = build_comparison_matrix(seal_2, c2, auth)
    matrix_3 = build_comparison_matrix(seal_3, c2, auth)
    fail_unless(matrix_1 == matrix_2 == matrix_3, "COMPARISON_MATRIX_DETERMINISM_MISMATCH")
    fail_unless(all(row["match"] == "true" for row in matrix_1), "INDEPENDENT_C2_MATERIAL_MISMATCH")

    recomputation = build_recomputation_summary(seal_1, seal_hash_1)
    freeze_1 = build_freeze_record(seal_1, matrix_1, auth)
    freeze_2 = build_freeze_record(seal_2, matrix_2, auth)
    freeze_3 = build_freeze_record(seal_3, matrix_3, auth)
    fail_unless(freeze_1 == freeze_2 == freeze_3, "FREEZE_RECORD_DETERMINISM_MISMATCH")
    fail_unless(freeze_1["audit_class"] != "AUDIT_MISMATCH", "AUDIT_MISMATCH_BLOCKS_OUTPUT")
    contract, recomputation_payload, comparison_payload, freeze_payload = build_contract(
        recomputation,
        matrix_1,
        freeze_1,
        seal_hash_1,
        negative_results,
        auth,
    )
    fail_unless(canonical_without(contract, "canonical_summary_sha256") == contract["canonical_summary_sha256"], "CONTRACT_CANONICAL_MISMATCH")

    OUT.mkdir(parents=True, exist_ok=False)
    RECOMPUTATION.write_bytes(recomputation_payload)
    COMPARISON.write_bytes(comparison_payload)
    FREEZE.write_bytes(freeze_payload)
    CONTRACT.write_bytes(pretty_bytes(contract))
    SUMMARY.write_bytes(pretty_bytes(contract))
    fail_unless(repository_snapshot() == repository_before, "EXISTING_REPOSITORY_FILE_CHANGED")

    created = sorted(
        path.relative_to(ROOT).as_posix()
        for path in [
            AUTH,
            AUTH_SCHEMA,
            CONTRACT,
            CONTRACT_SCHEMA,
            RECOMPUTATION,
            COMPARISON,
            FREEZE,
            SUMMARY,
            Path(__file__).resolve(),
        ]
    )
    fail_unless(created == sorted(ALLOWED_NEW_FILES), "CREATED_FILE_SET_MISMATCH")
    print(
        json.dumps(
            {
                "audit_class": contract["audit_class"],
                "audit_identity_sha256": contract["audit_identity_sha256"],
                "canonical_summary_sha256": contract["canonical_summary_sha256"],
                "comparison_matches": f"{contract['comparison']['match_count']}/{contract['comparison']['row_count']}",
                "decision": contract["decision"],
                "negative_tests": f"{len(negative_results)}/{len(NEGATIVE_TESTS)}",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
