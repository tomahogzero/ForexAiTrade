#!/usr/bin/env python3
"""Freeze the deterministic FR-Phase-C0 clean-data acquisition contract."""

import argparse
import ast
import copy
import hashlib
import json
import ntpath
import posixpath
import shutil
import sys
import tempfile
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_phase_c0_clean_data_acquisition_contract_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_phase_c0_clean_data_acquisition_contract_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_phase_c0_clean_data_acquisition_contract.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_phase_c0_clean_data_acquisition_contract.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_phase_c0"
SUMMARY = OUT / "clean_data_acquisition_contract_summary.json"

MODE = "freeze-clean-data-acquisition-contract"
PASS = "FR_PHASE_C0_PASS_CLEAN_DATA_ACQUISITION_CONTRACT_FROZEN"
EXPECTED_BRANCH = "agent/fr-phase-c-clean-data-intake"
EXPECTED_HEAD = "b05e10e6e8f48a46e9cab9a97e92e0ee6c6fadf8"
EXPECTED_STASH = "stash@{0}: On agent/fr-prep-b-runner-integration: fr-prep-b2a-partial-draft-before-b2e"
EXPECTED_B11C_DECISION = "FR_PREP_B11C_PASS_FQ_DATA_QUALITY_REMEDIATION_DEFERRED"
EXPECTED_B11C_IDENTITY = "6888ef561e0cd9636353621a1c9137609da1b1bec6957e80356509c5dc8ac25e"
EXPECTED_B11C_RECORD = "c17357dcc1280709792409ab93904a7d932aff7e6f53bc47dec0cff3d37853e7"
EXPECTED_STRATEGY_SHA1 = "da448295ac3bd443b376e1ce51a8e411de3c7245"
EXPECTED_STRATEGY_SHA256 = "0e72b1559f5416981c2db887f9c53a0bfbb66bada226250a064377b2b9fadaa2"

ALLOWED_NEW_FILES = [
    "research/contracts/fr_phase_c0_clean_data_acquisition_contract.v1.json",
    "research/contracts/fr_phase_c0_clean_data_acquisition_contract_authorization.v1.json",
    "research/results/checkpoint_fr_phase_c0/clean_data_acquisition_contract_summary.json",
    "research/schemas/fr_phase_c0_clean_data_acquisition_contract.v1.schema.json",
    "research/schemas/fr_phase_c0_clean_data_acquisition_contract_authorization.v1.schema.json",
    "tools/run_fr_phase_c0_clean_data_acquisition_contract_design.py",
]

NEGATIVE_TEST_NAMES = [
    "wrong_branch_or_baseline_head",
    "changed_b11c_identity_decision_or_record_hash",
    "protected_stash_changed",
    "frozen_strategy_hash_changed",
    "strategy_modification_attempted",
    "analysis_or_export_window_changed",
    "right_buffer_removed_or_shortened",
    "wrong_broker_server_symbol_or_timeframe_accepted",
    "holdout_or_out_of_sample_status_claimed",
    "timezone_or_dst_inferred",
    "mt5_raw_acquisition_external_path_scan_or_network_attempted",
    "dukascopy_read_or_canonical_registration_attempted",
    "raw_mutation_interpolation_reconstruction_or_deletion_authorized",
    "fq_remediation_resumed",
    "fj_or_fq_data_pooling_authorized",
    "detector_event_outcome_or_statistics_execution_authorized",
    "tp_sl_lot_cost_cash_pl_or_order_simulation_authorized",
    "profitability_edge_robustness_or_readiness_claimed",
    "credential_account_token_or_absolute_path_leakage",
    "existing_file_modification_authorized",
    "docs_raw_or_staging_content_created",
    "pr_creation_authorized",
]


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


def canonical_identity(value):
    return canonical_digest(
        {key: item for key, item in value.items() if key != "canonical_summary_sha256"}
    )


def output_bytes(value):
    return (
        json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def absolute_path_count(value):
    if isinstance(value, dict):
        return sum(absolute_path_count(item) for item in value.values())
    if isinstance(value, list):
        return sum(absolute_path_count(item) for item in value)
    return int(
        isinstance(value, str)
        and (ntpath.isabs(value) or posixpath.isabs(value))
    )


def require(condition, code):
    if not condition:
        raise ValueError(code)


def validate_authorization_values(auth):
    preflight = auth["preflight"]
    require(preflight["branch"] == EXPECTED_BRANCH, "BRANCH_MISMATCH")
    require(preflight["head"] == EXPECTED_HEAD, "BASELINE_HEAD_MISMATCH")
    require(
        preflight["remote_baseline_branch"] == "origin/agent/fr-prep-b-runner-integration"
        and preflight["remote_baseline_head"] == EXPECTED_HEAD,
        "REMOTE_BASELINE_MISMATCH",
    )
    require(preflight["protected_stash"] == EXPECTED_STASH, "PROTECTED_STASH_MISMATCH")
    require(preflight["worktree_clean"] is True, "WORKTREE_PREFLIGHT_MISMATCH")
    require(preflight["phase_c_upstream_before_first_push"] == "NONE", "UPSTREAM_MISMATCH")

    prior = auth["prior_phase_binding"]
    require(prior["decision"] == EXPECTED_B11C_DECISION, "B11C_DECISION_MISMATCH")
    require(
        prior["canonical_summary_sha256"] == EXPECTED_B11C_IDENTITY,
        "B11C_IDENTITY_MISMATCH",
    )
    require(
        prior["decision_record_sha256"] == EXPECTED_B11C_RECORD,
        "B11C_RECORD_HASH_MISMATCH",
    )
    require(
        prior["fq_remediation"] == "DEFERRED"
        and prior["deferral_reason"] == "HISTORICAL_PRIMARY_EVIDENCE_NOT_CURRENTLY_AVAILABLE"
        and prior["unresolved_target_gaps"] == 625
        and prior["accepted_gaps"] == 149
        and prior["primary_evidence_packages"] == 0
        and prior["reclassified_gaps"] == 0
        and prior["material_limitation"] == "RETAINED"
        and prior["outcome_rerun"] == "NOT_AUTHORIZED"
        and prior["order_logic"] == "NOT_APPROVED"
        and prior["phase_c_is_fq_remediation_resumption"] is False,
        "B11C_FROZEN_STATE_MISMATCH",
    )

    strategy = auth["frozen_strategy_boundary"]
    require(strategy["expected_git_blob_sha1"] == EXPECTED_STRATEGY_SHA1, "STRATEGY_SHA1_MISMATCH")
    require(strategy["expected_content_sha256"] == EXPECTED_STRATEGY_SHA256, "STRATEGY_SHA256_MISMATCH")
    require(
        strategy["file_status"] == "UNCHANGED"
        and strategy["modification_authorized"] is False
        and strategy["performance_interpretation_authorized"] is False
        and strategy["strategy_and_parameters"] == "FROZEN"
        and strategy["additional_indicators_authorized"] is False
        and strategy["atr_role"] == "METADATA_ONLY_UNDER_PRIOR_FROZEN_BOUNDARY",
        "STRATEGY_BOUNDARY_MISMATCH",
    )

    dataset = auth["planned_dataset"]
    require(
        dataset["phase"] == "FR_PHASE_C"
        and dataset["dataset_id"] == "FC_2026H1_XMGLOBAL_MT5_2_GOLD_HASH_H1"
        and dataset["purpose"] == "NEW_CLEAN_OBSERVATIONAL_DATASET"
        and dataset["broker"] == "XM"
        and dataset["expected_server"] == "XMGlobal-MT5 2"
        and dataset["expected_symbol"] == "GOLD"
        and dataset["timeframe"] == "H1",
        "PLANNED_DATASET_IDENTITY_MISMATCH",
    )
    require(
        dataset["time_basis"] == "XM_MT5_SERVER_CHART_TIME"
        and dataset["utc_offset"] == "UNKNOWN"
        and dataset["dst_behavior"] == "UNKNOWN",
        "TIME_BASIS_INFERENCE_PROHIBITED",
    )
    require(
        dataset["holdout_status"] == "NOT_CLAIMED"
        and dataset["out_of_sample_status"] == "NOT_CLAIMED"
        and dataset["performance"] == "NOT_EVALUATED"
        and dataset["profitability"] == "NOT_CLAIMED",
        "DATASET_STATUS_CLAIM_MISMATCH",
    )

    windows = auth["frozen_windows"]
    require(
        windows
        == {
            "analysis_start": "2026-01-01T000000",
            "analysis_end": "2026-06-30T235959",
            "requested_raw_export_start": "2026-01-01T000000",
            "requested_raw_export_end": "2026-07-07T235959",
        },
        "FROZEN_WINDOW_MISMATCH",
    )
    buffer_contract = auth["right_buffer_contract"]
    require(
        buffer_contract["minimum_valid_h1_bars"] == 12
        and buffer_contract["buffer_rows_generate_phase_c_events"] is False
        and buffer_contract["missing_calendar_hours_count_as_valid_h1_bars"] is False
        and buffer_contract["synthetic_or_interpolated_bars_may_satisfy"] is False
        and buffer_contract["c0_sufficiency_status"] == "NOT_EVALUATED",
        "RIGHT_BUFFER_CONTRACT_MISMATCH",
    )

    external = auth["external_operator_input_boundary"]
    require(
        external["c0_access"] == "PROHIBITED"
        and external["root_listing_or_scan"] == "PROHIBITED"
        and external["dukascopy_sample"]["phase_c_input"] is False
        and external["dukascopy_sample"]["xm_data"] is False
        and external["dukascopy_sample"]["gold_data"] is False
        and external["dukascopy_sample"]["xm_primary_evidence"] is False
        and external["dukascopy_sample"]["read_parse_hash_copy_register"] == "PROHIBITED"
        and external["dukascopy_sample"]["canonical_identity_effect"] == "NONE"
        and external["future_xm_folder"]["stage"] == "C1_EXPLICIT_AUTHORIZATION_REQUIRED"
        and external["future_xm_folder"]["c0_create_inspect_modify"] == "PROHIBITED",
        "EXTERNAL_OPERATOR_BOUNDARY_MISMATCH",
    )

    raw = auth["future_raw_artifact"]
    require(
        raw["artifact_id"] == "RAW_XM_GOLD_HASH_H1_EXPORT"
        and raw["source_file_count"] == 1
        and raw["multiple_files_require_contract_amendment"] is True
        and raw["original_bytes_immutable"] is True
        and raw["hash_before_parse"] is True
        and all(value is False for value in raw["mutation_authorizations"].values()),
        "RAW_ARTIFACT_POLICY_MISMATCH",
    )
    require(
        auth["expected_logical_columns"]
        == ["DATE", "TIME", "OPEN", "HIGH", "LOW", "CLOSE", "TICKVOL", "VOL", "SPREAD"],
        "COLUMN_CONTRACT_MISMATCH",
    )
    require(
        auth["delimiter_contract"]["permitted"] == ["COMMA", "SEMICOLON", "TAB"]
        and auth["delimiter_contract"]["deterministic_detection_required"] is True
        and auth["delimiter_contract"]["consistent_throughout_file_required"] is True
        and auth["delimiter_contract"]["immutable_artifact_conversion_authorized"] is False,
        "DELIMITER_CONTRACT_MISMATCH",
    )

    separation = auth["dataset_separation"]
    require(
        separation["fj_2023_2025"] == "IMMUTABLE"
        and separation["fq_2020_2022"] == "IMMUTABLE_AND_DEFERRED"
        and separation["pooling_authorized"] is False
        and separation["prior_artifact_access"] == "HASH_BINDING_FOR_SEPARATION_ONLY"
        and separation["phase_c_namespace"] == "NEW_ADDITIVE"
        and separation["clears_or_supersedes_prior_limitations"] is False,
        "DATASET_SEPARATION_MISMATCH",
    )

    operations = auth["operation_authorizations"]
    require(operations["c0_contract_design"] is True, "C0_SCOPE_MISMATCH")
    require(
        all(value is False for key, value in operations.items() if key != "c0_contract_design"),
        "PROHIBITED_OPERATION_AUTHORIZED",
    )
    claims = auth["claims"]
    require(
        claims
        == {
            "holdout": "NOT_CLAIMED",
            "out_of_sample": "NOT_CLAIMED",
            "performance": "NOT_EVALUATED",
            "profitability": "NOT_CLAIMED",
            "strategy_edge": "NOT_ESTABLISHED",
            "robustness": "NOT_ESTABLISHED",
            "readiness": "NOT_CLAIMED",
            "order_logic": "NOT_APPROVED",
        },
        "PROHIBITED_CLAIM_MISMATCH",
    )
    require(
        auth["sensitive_data_policy"]["absolute_runtime_path_in_canonical_identity"] == "PROHIBITED"
        and auth["sensitive_data_policy"]["credentials_in_metadata"] == "PROHIBITED"
        and auth["sensitive_data_policy"]["prohibited_fields"]
        == ["account_number", "login_id", "user_name", "password", "token", "api_key", "credentials"],
        "SENSITIVE_DATA_POLICY_MISMATCH",
    )
    file_boundary = auth["file_creation_boundary"]
    require(file_boundary["allowed_new_files"] == ALLOWED_NEW_FILES, "ALLOWED_FILE_SET_MISMATCH")
    require(file_boundary["existing_file_modification_authorized"] is False, "EXISTING_MODIFICATION_AUTHORIZED")
    require(
        file_boundary["docs_fixtures_raw_staging_operator_input_creation_authorized"] is False,
        "UNAUTHORIZED_CONTENT_CREATION",
    )
    require(file_boundary["pr_creation_authorized"] is False, "PR_CREATION_AUTHORIZED")
    require(absolute_path_count(auth) == 0, "ABSOLUTE_PATH_IN_AUTHORIZATION")


def load_and_validate(root):
    auth = json.loads((root / AUTH.relative_to(ROOT)).read_text(encoding="utf-8"))
    auth_schema = json.loads((root / AUTH_SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))
    jsonschema.validate(auth, auth_schema)
    validate_authorization_values(auth)

    documents = {}
    hashes = {}
    for spec in auth["bound_artifacts"]:
        path = root / spec["path"]
        raw = path.read_bytes()
        actual_sha256 = sha256_bytes(raw)
        require(actual_sha256 == spec["file_sha256"], "BOUND_ARTIFACT_HASH_MISMATCH:" + spec["artifact_id"])
        hashes[spec["artifact_id"]] = actual_sha256
        if "git_blob_sha1" in spec:
            require(git_blob_sha1(raw) == spec["git_blob_sha1"], "BOUND_GIT_BLOB_SHA1_MISMATCH:" + spec["artifact_id"])
        if spec["access"] == "json":
            documents[spec["artifact_id"]] = json.loads(raw)

    b11c = documents["b11c_contract"]
    b11c_schema = documents["b11c_schema"]
    jsonschema.validate(b11c, b11c_schema)
    require(canonical_identity(b11c) == EXPECTED_B11C_IDENTITY, "B11C_RECOMPUTED_IDENTITY_MISMATCH")
    require(b11c["canonical_summary_sha256"] == EXPECTED_B11C_IDENTITY, "B11C_CANONICAL_IDENTITY_MISMATCH")
    require(b11c["decision"] == EXPECTED_B11C_DECISION, "B11C_DECISION_MISMATCH")
    require(b11c["output_hashes"]["decision_record_sha256"] == EXPECTED_B11C_RECORD, "B11C_RECORD_HASH_MISMATCH")
    require(
        b11c["disposition"]["fq_remediation_track"] == "DEFERRED"
        and b11c["disposition"]["deferral_reason"] == "HISTORICAL_PRIMARY_EVIDENCE_NOT_CURRENTLY_AVAILABLE"
        and b11c["disposition"]["unresolved_target_gap_count"] == 625
        and b11c["disposition"]["existing_accepted_gap_count"] == 149
        and b11c["disposition"]["primary_evidence_package_count"] == 0
        and b11c["disposition"]["reclassified_gap_count"] == 0
        and b11c["disposition"]["material_limitation"] == "RETAINED"
        and b11c["conclusions"]["outcome_rerun"] == "NOT_AUTHORIZED"
        and b11c["conclusions"]["order_logic"] == "NOT_APPROVED",
        "B11C_REQUIRED_FROZEN_STATE_MISMATCH",
    )
    return auth, hashes


def future_validation_contract():
    return {
        "decisions": [
            "PASS_DATASET_CLEAN_FOR_FUTURE_RESEARCH",
            "PASS_DATASET_VALIDATED_WITH_LIMITATIONS",
            "FAIL_DATASET_INTAKE",
        ],
        "clean_gate_requires_all": [
            "exact_broker_server_symbol_timeframe",
            "raw_byte_hash_valid",
            "schema_and_header_valid",
            "all_rows_parse_deterministically",
            "chronological_order_valid",
            "duplicate_timestamps_zero",
            "conflicting_timestamps_zero",
            "non_finite_prices_zero",
            "non_positive_prices_zero",
            "ohlc_consistency_errors_zero",
            "negative_volume_values_zero",
            "negative_spread_values_zero",
            "cross_file_overlap_zero",
            "requested_and_observed_boundaries_reported",
            "deterministic_gap_inventory_generated",
            "unverified_internal_analysis_window_gaps_zero",
            "every_accepted_non_trading_interval_has_admissible_exact_same_server_or_official_evidence",
            "at_least_12_valid_right_buffer_h1_bars",
            "no_interpolation_reconstruction_or_synthetic_bars",
            "identity_distinct_from_fj_and_fq",
            "later_independent_audit_passes",
        ],
        "validated_with_limitations_when_structural_identity_passes_but_any_remain": [
            "unverified_gaps",
            "incomplete_session_provenance",
            "incomplete_requested_boundary_coverage",
            "insufficient_right_buffer",
            "broker_history_completeness_not_proven",
        ],
        "validated_with_limitations_authorizations": {
            "detector": False,
            "outcome": False,
            "order": False,
            "description_as_clean": False,
            "all_limitations_must_be_retained": True,
        },
        "fail_gate_any": [
            "wrong_broker_server_symbol_or_timeframe",
            "raw_hash_mismatch",
            "unsupported_or_inconsistent_schema",
            "malformed_timestamps",
            "out_of_order_rows_requiring_mutation",
            "duplicate_or_conflicting_timestamps",
            "non_finite_or_invalid_ohlc",
            "proven_artifact_mutation",
            "missing_mandatory_metadata",
            "sensitive_data_leakage",
            "identity_collision_with_frozen_prior_artifacts",
        ],
    }


def build_contract(auth, bound_hashes):
    prior = copy.deepcopy(auth["prior_phase_binding"])
    strategy = copy.deepcopy(auth["frozen_strategy_boundary"])
    strategy["validated_git_blob_sha1"] = EXPECTED_STRATEGY_SHA1
    strategy["validated_content_sha256"] = EXPECTED_STRATEGY_SHA256

    chronology = {
        "analysis_period_later_than_fj_and_fq": True,
        "chronological_separation": "PLANNED_NOT_YET_PROVEN",
        "dataset_existence": "NOT_PROVEN",
        "dataset_identity": "NOT_YET_PROVEN",
        "dataset_separation": "NOT_PROVEN_UNTIL_IMMUTABLE_ARTIFACT_ACQUIRED_AND_VALIDATED",
        "holdout_label_authorized": False,
        "unseen_label_authorized": False,
        "out_of_sample_label_authorized": False,
    }
    session_policy = {
        "screenshot_may_establish_current_source_identity_only": True,
        "screenshot_automatically_classifies_historical_gaps": False,
        "recurring_timestamp_patterns": "DESCRIPTIVE_ONLY",
        "other_broker_data_proves_xm_closure": False,
        "generic_market_hours_websites_establish_same_server_closure": False,
        "accepted_closure_evidence": "EXACT_SAME_SERVER_OR_OFFICIAL_EVIDENCE_REQUIRED",
        "holiday_gap_evidence": "OFFICIAL_DATED_BROKER_OR_SESSION_NOTICE_MAY_BE_REQUIRED",
    }
    stages = {
        "C0": "CLEAN_DATA_ACQUISITION_CONTRACT_DESIGN_ONLY",
        "C1": "MANUAL_RAW_DATA_ACQUISITION_AND_IMMUTABLE_INTAKE_ONLY",
        "C2": "STRUCTURAL_TIMELINE_AND_GAP_VALIDATION_ONLY",
        "C3": "INDEPENDENT_DATASET_VALIDATION_AUDIT_AND_FREEZE_ONLY",
        "c0_automatically_authorizes_c1": False,
        "future_detector_requirements": [
            "PASS_DATASET_CLEAN_FOR_FUTURE_RESEARCH",
            "COMPLETED_INDEPENDENT_C3_AUDIT",
            "SEPARATE_EXPLICIT_DETECTOR_EXECUTION_AUTHORIZATION",
        ],
    }
    conclusions = {
        "phase_c_acquisition_contract": "FROZEN",
        "prior_fq_remediation": "DEFERRED_AND_NOT_RESUMED",
        "prior_fq_material_limitation": "RETAINED",
        "phase_c_dataset_acquired": False,
        "phase_c_dataset_identity": "NOT_YET_PROVEN",
        "chronology_separation": "PLANNED_NOT_YET_PROVEN",
        "holdout_status": "NOT_CLAIMED",
        "out_of_sample_status": "NOT_CLAIMED",
        "analysis_window": "FROZEN",
        "requested_export_window": "FROZEN",
        "right_buffer_requirement": "FROZEN_AT_12_VALID_H1_BARS",
        "raw_artifact_immutability": "REQUIRED",
        "same_server_source_identity_metadata": "REQUIRED",
        "same_server_session_metadata": "REQUIRED",
        "source_data_acquisition": "NOT_STARTED",
        "dataset_intake": "NOT_STARTED",
        "structural_validation": "NOT_STARTED",
        "gap_inventory": "NOT_STARTED",
        "independent_audit": "NOT_STARTED",
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
        "next_allowed_scope": "FR_PHASE_C1_MANUAL_RAW_DATA_ACQUISITION_AND_IMMUTABLE_INTAKE_ONLY",
    }
    policy_record = {
        "prior_phase_binding": prior,
        "dataset_separation": auth["dataset_separation"],
        "strategy": strategy,
        "planned_dataset": auth["planned_dataset"],
        "chronology": chronology,
        "windows": auth["frozen_windows"],
        "right_buffer": auth["right_buffer_contract"],
        "future_raw_artifact": auth["future_raw_artifact"],
        "future_acquisition_metadata": auth["future_acquisition_metadata"],
        "columns": auth["expected_logical_columns"],
        "headers": auth["permitted_header_profiles"],
        "delimiter": auth["delimiter_contract"],
        "future_source_identity_artifact": auth["future_source_identity_artifact"],
        "session_evidence_policy": session_policy,
        "raw_input_policy": auth["raw_input_policy"],
        "future_validation": future_validation_contract(),
        "stages": stages,
        "conclusions": conclusions,
    }
    record_hash = canonical_digest(policy_record)
    contract = {
        "schema_version": "fr_phase_c0_clean_data_acquisition_contract.v1",
        "checkpoint": "FR_PHASE_C0",
        "execution_status": "PASS",
        "decision": PASS,
        "authorization_scope": "CLEAN_XM_GOLD_H1_DATA_ACQUISITION_CONTRACT_DESIGN_ONLY",
        "preflight": copy.deepcopy(auth["preflight"]),
        "prior_phase_binding": prior,
        "dataset_separation": copy.deepcopy(auth["dataset_separation"]),
        "bound_artifact_hashes": {key: bound_hashes[key] for key in sorted(bound_hashes)},
        "frozen_strategy_boundary": strategy,
        "planned_dataset": copy.deepcopy(auth["planned_dataset"]),
        "chronology_policy": chronology,
        "frozen_windows": copy.deepcopy(auth["frozen_windows"]),
        "right_buffer_contract": copy.deepcopy(auth["right_buffer_contract"]),
        "future_raw_artifact": copy.deepcopy(auth["future_raw_artifact"]),
        "future_acquisition_metadata": copy.deepcopy(auth["future_acquisition_metadata"]),
        "prohibited_metadata": copy.deepcopy(auth["sensitive_data_policy"]["prohibited_fields"]),
        "expected_logical_columns": copy.deepcopy(auth["expected_logical_columns"]),
        "permitted_header_profiles": copy.deepcopy(auth["permitted_header_profiles"]),
        "delimiter_contract": copy.deepcopy(auth["delimiter_contract"]),
        "future_source_identity_artifact": copy.deepcopy(auth["future_source_identity_artifact"]),
        "session_evidence_policy": session_policy,
        "raw_input_policy": copy.deepcopy(auth["raw_input_policy"]),
        "future_validation_contract": future_validation_contract(),
        "stage_separation": stages,
        "conclusions": conclusions,
        "file_creation_boundary": copy.deepcopy(auth["file_creation_boundary"]),
        "determinism": {
            "normal_run_1": "PASS",
            "normal_run_2": "PASS",
            "normal_runs_canonical_records_identical": True,
            "normal_runs_ordering_identical": True,
            "normal_runs_hashes_identical": True,
            "controlled_relocation_run": "PASS",
            "controlled_relocation_canonical_records_identical": True,
            "controlled_relocation_ordering_identical": True,
            "controlled_relocation_hashes_identical": True,
            "absolute_runtime_paths_excluded": True,
            "temporary_artifacts_deleted": True,
        },
        "negative_tests": {
            "test_count": len(NEGATIVE_TEST_NAMES),
            "tests_passed": len(NEGATIVE_TEST_NAMES),
            "results": {name: "PASS" for name in NEGATIVE_TEST_NAMES},
        },
        "mismatch_counters": {
            name: 0
            for name in (
                "branch",
                "baseline_head",
                "remote_baseline",
                "protected_stash",
                "worktree_preflight",
                "upstream_preflight",
                "b11c_artifact_hash",
                "b11c_canonical_identity",
                "b11c_decision",
                "b11c_decision_record",
                "b11c_frozen_state",
                "strategy_git_blob_sha1",
                "strategy_content_sha256",
                "bound_artifacts",
                "schema",
                "determinism",
                "file_creation_boundary",
            )
        },
        "prohibited_counts": {
            name: 0
            for name in (
                "mt5_launch",
                "raw_artifact_reads",
                "external_operator_path_accesses",
                "external_directory_creations",
                "network_access",
                "external_process_execution",
                "detector_execution",
                "events_generated",
                "outcomes_executed",
                "statistics_executed",
                "fq_remediation_actions",
                "prior_data_pooling",
                "strategy_modifications",
                "indicator_additions",
                "parameter_changes",
                "tp_sl_design",
                "lot_sizing_design",
                "cost_cash_pl_order_simulation",
                "demo_live_trading",
                "profitability_edge_robustness_readiness_claims",
                "credentials_leaked",
                "absolute_paths_in_canonical_identity",
                "existing_files_modified",
                "docs_fixtures_raw_staging_content_created",
                "pr_created",
                "prohibited_imports",
            )
        },
        "output_hashes": {"contract_record_sha256": record_hash},
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "sensitive_value_in_canonical_identity_count": 0,
    }
    require(absolute_path_count(contract) == 0, "ABSOLUTE_PATH_IN_CANONICAL_CONTRACT")
    contract["canonical_summary_sha256"] = canonical_identity(contract)
    return contract


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

    check("wrong_branch_or_baseline_head", lambda x: x["preflight"].update(branch="wrong", head="0" * 40))
    check("changed_b11c_identity_decision_or_record_hash", lambda x: x["prior_phase_binding"].update(decision="wrong", canonical_summary_sha256="0" * 64, decision_record_sha256="1" * 64))
    check("protected_stash_changed", lambda x: x["preflight"].update(protected_stash="changed"))
    check("frozen_strategy_hash_changed", lambda x: x["frozen_strategy_boundary"].update(expected_git_blob_sha1="0" * 40, expected_content_sha256="0" * 64))
    check("strategy_modification_attempted", lambda x: x["frozen_strategy_boundary"].update(modification_authorized=True))
    check("analysis_or_export_window_changed", lambda x: x["frozen_windows"].update(analysis_end="2026-07-01T000000"))
    check("right_buffer_removed_or_shortened", lambda x: x["right_buffer_contract"].update(minimum_valid_h1_bars=11))
    check("wrong_broker_server_symbol_or_timeframe_accepted", lambda x: x["planned_dataset"].update(broker="OTHER", expected_server="OTHER", expected_symbol="XAUUSD", timeframe="M1"))
    check("holdout_or_out_of_sample_status_claimed", lambda x: x["planned_dataset"].update(holdout_status="CLAIMED", out_of_sample_status="CLAIMED"))
    check("timezone_or_dst_inferred", lambda x: x["planned_dataset"].update(utc_offset="+02:00", dst_behavior="INFERRED"))
    check("mt5_raw_acquisition_external_path_scan_or_network_attempted", lambda x: x["operation_authorizations"].update(mt5_launch=True, raw_acquisition=True, external_path_scan=True, network_access=True))
    check("dukascopy_read_or_canonical_registration_attempted", lambda x: x["external_operator_input_boundary"]["dukascopy_sample"].update(read_parse_hash_copy_register="AUTHORIZED", canonical_identity_effect="REGISTERED"))
    check("raw_mutation_interpolation_reconstruction_or_deletion_authorized", lambda x: x["future_raw_artifact"]["mutation_authorizations"].update(excel_resave=True, sorting=True, row_deletion=True, deduplication=True, interpolation=True, reconstruction=True))
    check("fq_remediation_resumed", lambda x: x["prior_phase_binding"].update(fq_remediation="RESUMED", phase_c_is_fq_remediation_resumption=True))
    check("fj_or_fq_data_pooling_authorized", lambda x: x["dataset_separation"].update(pooling_authorized=True))
    check("detector_event_outcome_or_statistics_execution_authorized", lambda x: x["operation_authorizations"].update(detector_execution=True, event_generation=True, outcome_execution=True, statistics_execution=True))
    check("tp_sl_lot_cost_cash_pl_or_order_simulation_authorized", lambda x: x["operation_authorizations"].update(tp_sl_design=True, lot_sizing=True, costs_or_cash_pl=True, order_simulation=True))
    check("profitability_edge_robustness_or_readiness_claimed", lambda x: x["claims"].update(profitability="CLAIMED", strategy_edge="ESTABLISHED", robustness="ESTABLISHED", readiness="READY"))
    check("credential_account_token_or_absolute_path_leakage", lambda x: x["sensitive_data_policy"].update(absolute_runtime_path_in_canonical_identity="AUTHORIZED", credentials_in_metadata="AUTHORIZED"))
    check("existing_file_modification_authorized", lambda x: x["file_creation_boundary"].update(existing_file_modification_authorized=True))
    check("docs_raw_or_staging_content_created", lambda x: x["file_creation_boundary"].update(docs_fixtures_raw_staging_operator_input_creation_authorized=True))
    check("pr_creation_authorized", lambda x: x["file_creation_boundary"].update(pr_creation_authorized=True))

    require(list(tests) == NEGATIVE_TEST_NAMES, "NEGATIVE_TEST_ORDER_MISMATCH")
    require(all(value == "PASS" for value in tests.values()), "NEGATIVE_TEST_FAILURE")
    return tests


def validate_script_imports():
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    prohibited = {"MetaTrader5", "requests", "urllib", "http", "socket", "subprocess"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    require(not (imported & prohibited), "PROHIBITED_IMPORT")


def copy_relocation_inputs(auth, relocated):
    paths = [AUTH.relative_to(ROOT), AUTH_SCHEMA.relative_to(ROOT), CONTRACT_SCHEMA.relative_to(ROOT)]
    paths.extend(Path(spec["path"]) for spec in auth["bound_artifacts"])
    for relative in paths:
        destination = relocated / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=MODE)
    args = parser.parse_args()
    require(args.mode == MODE, "MODE_NOT_AUTHORIZED")
    validate_script_imports()
    require(not CONTRACT.exists(), "CONTRACT_ALREADY_EXISTS")
    require(not SUMMARY.exists(), "SUMMARY_ALREADY_EXISTS")
    require(not OUT.exists(), "RESULT_DIRECTORY_ALREADY_EXISTS")

    auth_1, hashes_1 = load_and_validate(ROOT)
    negative_results = run_negative_tests(auth_1)
    contract_1 = build_contract(auth_1, hashes_1)

    auth_2, hashes_2 = load_and_validate(ROOT)
    contract_2 = build_contract(auth_2, hashes_2)
    require(contract_1 == contract_2, "NORMAL_REPEAT_CONTRACT_MISMATCH")
    require(hashes_1 == hashes_2, "NORMAL_REPEAT_HASH_MISMATCH")

    with tempfile.TemporaryDirectory(prefix="fr_phase_c0_") as temporary:
        relocated = Path(temporary) / "relocated_repository"
        copy_relocation_inputs(auth_1, relocated)
        relocated_auth, relocated_hashes = load_and_validate(relocated)
        relocated_contract = build_contract(relocated_auth, relocated_hashes)
        require(relocated_contract == contract_1, "CONTROLLED_RELOCATION_CONTRACT_MISMATCH")
        require(relocated_hashes == hashes_1, "CONTROLLED_RELOCATION_HASH_MISMATCH")

    require(negative_results == contract_1["negative_tests"]["results"], "NEGATIVE_TEST_RECORD_MISMATCH")
    schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(contract_1, schema)
    require(canonical_identity(contract_1) == contract_1["canonical_summary_sha256"], "CANONICAL_IDENTITY_MISMATCH")

    OUT.mkdir(parents=True, exist_ok=False)
    payload = output_bytes(contract_1)
    CONTRACT.write_bytes(payload)
    SUMMARY.write_bytes(payload)
    print(
        json.dumps(
            {
                "canonical_summary_sha256": contract_1["canonical_summary_sha256"],
                "contract_record_sha256": contract_1["output_hashes"]["contract_record_sha256"],
                "decision": PASS,
                "negative_tests": f"{len(negative_results)}/{len(NEGATIVE_TEST_NAMES)}",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
