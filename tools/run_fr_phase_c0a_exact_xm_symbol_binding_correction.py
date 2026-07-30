#!/usr/bin/env python3
"""Freeze the additive FR-Phase-C0a exact XM GOLD# symbol correction."""

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
AUTH = ROOT / "research/contracts/fr_phase_c0a_exact_xm_symbol_binding_correction_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_phase_c0a_exact_xm_symbol_binding_correction_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_phase_c0a_exact_xm_symbol_binding_correction.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_phase_c0a_exact_xm_symbol_binding_correction.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_phase_c0a"
SUMMARY = OUT / "exact_xm_symbol_binding_correction_summary.json"

MODE = "freeze-exact-xm-symbol-binding-correction"
PASS = "FR_PHASE_C0A_PASS_EXACT_XM_GOLD_HASH_SYMBOL_BINDING_CORRECTED"
EXPECTED_BRANCH = "agent/fr-phase-c-clean-data-intake"
EXPECTED_HEAD = "feb0bf29220538feed8738d2788696019cfd0800"
EXPECTED_STASH = "stash@{0}: On agent/fr-prep-b-runner-integration: fr-prep-b2a-partial-draft-before-b2e"
EXPECTED_C0_DECISION = "FR_PHASE_C0_PASS_CLEAN_DATA_ACQUISITION_CONTRACT_FROZEN"
EXPECTED_C0_IDENTITY = "26f2e23a20e08223a001514558fa69f6298b6af0e761d379393bb99825db6689"
EXPECTED_C0_RECORD = "5e229bf31aa9724e9d67c3675c1e99cf7454172e19a263ca8a45401993034a04"
EXPECTED_STRATEGY_SHA1 = "da448295ac3bd443b376e1ce51a8e411de3c7245"
EXPECTED_STRATEGY_SHA256 = "0e72b1559f5416981c2db887f9c53a0bfbb66bada226250a064377b2b9fadaa2"
ORIGINAL_SYMBOL = "GOLD"
CORRECTED_SYMBOL = "GOLD#"
CORRECTED_UTF8_HEX = "474f4c4423"
CORRECTED_CODE_POINTS = [71, 79, 76, 68, 35]

ALLOWED_NEW_FILES = [
    "research/contracts/fr_phase_c0a_exact_xm_symbol_binding_correction.v1.json",
    "research/contracts/fr_phase_c0a_exact_xm_symbol_binding_correction_authorization.v1.json",
    "research/results/checkpoint_fr_phase_c0a/exact_xm_symbol_binding_correction_summary.json",
    "research/schemas/fr_phase_c0a_exact_xm_symbol_binding_correction.v1.schema.json",
    "research/schemas/fr_phase_c0a_exact_xm_symbol_binding_correction_authorization.v1.schema.json",
    "tools/run_fr_phase_c0a_exact_xm_symbol_binding_correction.py",
]

NEGATIVE_TEST_NAMES = [
    "wrong_branch_or_head",
    "changed_c0_decision",
    "changed_c0_canonical_summary_hash",
    "changed_c0_contract_record_hash",
    "original_c0_file_modification_attempted",
    "corrected_symbol_set_to_gold",
    "corrected_symbol_set_to_goldm_hash",
    "corrected_symbol_set_to_goldm",
    "corrected_symbol_set_to_xauusd_or_xau_slash_usd",
    "corrected_symbol_missing_final_hash",
    "symbol_whitespace_case_change_or_alias_accepted",
    "utf8_hex_not_474f4c4423",
    "character_length_not_five",
    "server_or_timeframe_changed",
    "analysis_or_export_window_changed",
    "right_buffer_requirement_changed",
    "raw_acquisition_external_scan_or_mt5_launch_attempted",
    "fq_remediation_resumed",
    "detector_event_outcome_or_statistics_execution_authorized",
    "strategy_indicator_or_parameter_modification_authorized",
    "tp_sl_lot_cost_cash_pl_or_order_simulation_authorized",
    "profitability_edge_robustness_or_readiness_claimed",
    "credential_account_token_or_absolute_path_leakage",
    "existing_file_modified",
    "pr_creation",
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


def expected_symbol_identity():
    return {
        "exact_literal": CORRECTED_SYMBOL,
        "json_escaped_representation": "GOLD\\u0023",
        "utf8_hex": CORRECTED_UTF8_HEX,
        "ascii_code_points": CORRECTED_CODE_POINTS,
        "character_length": 5,
        "final_character": "#",
        "encoding": "UTF-8",
    }


def expected_exact_comparison_policy():
    return {
        "case_sensitive": True,
        "comparison": "BYTE_EXACT_AFTER_UTF8_DECODING",
        "trim": "PROHIBITED",
        "normalize": "PROHIBITED",
        "alias": "PROHIBITED",
        "map": "PROHIBITED",
        "substitute": "PROHIBITED",
        "hash_character_is_symbol_identity": True,
        "non_equivalent_literals": ["GOLD", "GOLDm#", "GOLDm", "XAUUSD", "XAU/USD"],
        "prefix_suffix_or_whitespace": "IDENTITY_MISMATCH",
        "shell_or_markdown_comment_interpretation_may_remove_hash": False,
        "future_cli_quoted_literal": "\"GOLD#\"",
    }


def validate_authorization_values(auth):
    preflight = auth["preflight"]
    require(preflight["branch"] == EXPECTED_BRANCH, "BRANCH_MISMATCH")
    require(preflight["head"] == EXPECTED_HEAD, "HEAD_MISMATCH")
    require(
        preflight["origin_branch"] == "origin/agent/fr-phase-c-clean-data-intake"
        and preflight["origin_head"] == EXPECTED_HEAD
        and preflight["upstream_aligned"] is True,
        "ORIGIN_ALIGNMENT_MISMATCH",
    )
    require(preflight["worktree_clean"] is True, "WORKTREE_PREFLIGHT_MISMATCH")
    require(preflight["protected_stash"] == EXPECTED_STASH, "PROTECTED_STASH_MISMATCH")

    c0 = auth["c0_binding"]
    require(c0["decision"] == EXPECTED_C0_DECISION, "C0_DECISION_MISMATCH")
    require(c0["canonical_summary_sha256"] == EXPECTED_C0_IDENTITY, "C0_IDENTITY_MISMATCH")
    require(c0["contract_record_sha256"] == EXPECTED_C0_RECORD, "C0_RECORD_MISMATCH")
    require(c0["commit"] == EXPECTED_HEAD, "C0_COMMIT_MISMATCH")
    require(
        c0["original_exact_symbol"] == ORIGINAL_SYMBOL
        and c0["expected_server"] == "XMGlobal-MT5 2"
        and c0["timeframe"] == "H1"
        and c0["analysis_start"] == "2026-01-01T000000"
        and c0["analysis_end"] == "2026-06-30T235959"
        and c0["requested_export_start"] == "2026-01-01T000000"
        and c0["requested_export_end"] == "2026-07-07T235959"
        and c0["right_buffer_valid_h1_bars"] == 12
        and c0["original_files"] == "IMMUTABLE",
        "C0_FROZEN_BINDING_MISMATCH",
    )

    correction = auth["correction"]
    require(correction["reason_code"] == "C0_EXACT_SYMBOL_LITERAL_BINDING_DEFECT", "CORRECTION_REASON_MISMATCH")
    require(correction["type"] == "ADDITIVE_SUPPLEMENT", "CORRECTION_TYPE_MISMATCH")
    require(correction["superseded_field"] == "C0.future_raw_artifact.exact_symbol", "SUPERSEDED_FIELD_MISMATCH")
    require(correction["only_this_field_is_superseded"] is True, "CORRECTION_SCOPE_MISMATCH")
    require(correction["original_exact_symbol"] == ORIGINAL_SYMBOL, "ORIGINAL_SYMBOL_MISMATCH")
    require(correction["corrected_symbol_identity"] == expected_symbol_identity(), "CORRECTED_SYMBOL_IDENTITY_MISMATCH")
    require(correction["exact_comparison_policy"] == expected_exact_comparison_policy(), "EXACT_COMPARISON_POLICY_MISMATCH")

    dataset = auth["dataset_identity_policy"]
    require(dataset["dataset_id"] == "FC_2026H1_XMGLOBAL_MT5_2_GOLD_HASH_H1", "DATASET_ID_MISMATCH")
    require(
        dataset["gold_hash_token_meaning"] == "FILESYSTEM_SAFE_TOKEN_FOR_EXACT_LITERAL_GOLD_HASH"
        and dataset["dataset_id_change_authorized"] is False
        and dataset["dataset_id_implies_plain_gold"] is False,
        "DATASET_TOKEN_POLICY_MISMATCH",
    )

    effective = auth["effective_acquisition_binding"]
    require(
        effective["broker"] == "XM"
        and effective["exact_server"] == "XMGlobal-MT5 2"
        and effective["exact_symbol"] == CORRECTED_SYMBOL
        and effective["timeframe"] == "H1"
        and effective["time_basis"] == "XM_MT5_SERVER_CHART_TIME"
        and effective["utc_offset"] == "UNKNOWN"
        and effective["dst_behavior"] == "UNKNOWN"
        and effective["holdout"] == "NOT_CLAIMED"
        and effective["out_of_sample"] == "NOT_CLAIMED",
        "EFFECTIVE_ACQUISITION_BINDING_MISMATCH",
    )

    invariants = auth["unchanged_invariants"]
    require(
        invariants["analysis_start"] == "2026-01-01T000000"
        and invariants["analysis_end"] == "2026-06-30T235959"
        and invariants["requested_export_start"] == "2026-01-01T000000"
        and invariants["requested_export_end"] == "2026-07-07T235959"
        and invariants["right_buffer_valid_h1_bars"] == 12
        and invariants["strategy_file"] == "UNCHANGED"
        and invariants["strategy_and_parameters"] == "FROZEN"
        and invariants["additional_indicators_authorized"] is False
        and invariants["fq_remediation"] == "DEFERRED_AND_NOT_RESUMED"
        and invariants["phase_c_dataset_acquisition"] == "NOT_STARTED",
        "UNCHANGED_INVARIANT_MISMATCH",
    )

    operations = auth["operation_authorizations"]
    require(operations["c0a_correction_design"] is True, "C0A_SCOPE_MISMATCH")
    require(
        all(value is False for key, value in operations.items() if key != "c0a_correction_design"),
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
        "CLAIM_BOUNDARY_MISMATCH",
    )
    require(
        auth["external_operator_input_boundary"]["c0a_access"] == "PROHIBITED"
        and auth["external_operator_input_boundary"]["directory_create_list_scan_open_parse_hash_copy_modify"] == "PROHIBITED",
        "EXTERNAL_INPUT_BOUNDARY_MISMATCH",
    )
    require(
        auth["sensitive_data_policy"]["absolute_runtime_path_in_canonical_identity"] == "PROHIBITED"
        and auth["sensitive_data_policy"]["credentials_account_or_token"] == "PROHIBITED",
        "SENSITIVE_DATA_POLICY_MISMATCH",
    )
    files = auth["file_creation_boundary"]
    require(files["allowed_new_files"] == ALLOWED_NEW_FILES, "ALLOWED_NEW_FILE_SET_MISMATCH")
    require(files["existing_file_modification_authorized"] is False, "EXISTING_FILE_MODIFICATION_AUTHORIZED")
    require(files["docs_fixtures_raw_staging_or_input_creation_authorized"] is False, "UNAUTHORIZED_CONTENT_CREATION")
    require(files["pr_creation_authorized"] is False, "PR_CREATION_AUTHORIZED")
    require(absolute_path_count(auth) == 0, "ABSOLUTE_PATH_IN_AUTHORIZATION")


def load_and_validate(root):
    auth = json.loads((root / AUTH.relative_to(ROOT)).read_text(encoding="utf-8"))
    auth_schema = json.loads((root / AUTH_SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))
    jsonschema.validate(auth, auth_schema)
    validate_authorization_values(auth)

    documents = {}
    hashes = {}
    for spec in auth["bound_artifacts"]:
        raw = (root / spec["path"]).read_bytes()
        actual_sha256 = sha256_bytes(raw)
        require(
            actual_sha256 == spec["file_sha256"],
            "BOUND_ARTIFACT_HASH_MISMATCH:" + spec["artifact_id"],
        )
        hashes[spec["artifact_id"]] = actual_sha256
        if "git_blob_sha1" in spec:
            require(
                git_blob_sha1(raw) == spec["git_blob_sha1"],
                "BOUND_GIT_BLOB_SHA1_MISMATCH:" + spec["artifact_id"],
            )
        if spec["access"] == "json":
            documents[spec["artifact_id"]] = json.loads(raw)

    c0_contract = documents["c0_contract"]
    c0_summary = documents["c0_summary"]
    c0_schema = documents["c0_schema"]
    jsonschema.validate(c0_contract, c0_schema)
    jsonschema.validate(c0_summary, c0_schema)
    require(c0_contract == c0_summary, "C0_CONTRACT_SUMMARY_MISMATCH")
    require(canonical_identity(c0_contract) == EXPECTED_C0_IDENTITY, "C0_RECOMPUTED_IDENTITY_MISMATCH")
    require(c0_contract["canonical_summary_sha256"] == EXPECTED_C0_IDENTITY, "C0_CANONICAL_IDENTITY_MISMATCH")
    require(c0_contract["decision"] == EXPECTED_C0_DECISION, "C0_DECISION_MISMATCH")
    require(c0_contract["output_hashes"]["contract_record_sha256"] == EXPECTED_C0_RECORD, "C0_RECORD_MISMATCH")
    require(c0_contract["future_raw_artifact"]["exact_symbol"] == ORIGINAL_SYMBOL, "C0_ORIGINAL_SYMBOL_MISMATCH")
    require(
        c0_contract["planned_dataset"]["expected_server"] == "XMGlobal-MT5 2"
        and c0_contract["planned_dataset"]["timeframe"] == "H1"
        and c0_contract["frozen_windows"] == {
            "analysis_end": "2026-06-30T235959",
            "analysis_start": "2026-01-01T000000",
            "requested_raw_export_end": "2026-07-07T235959",
            "requested_raw_export_start": "2026-01-01T000000",
        }
        and c0_contract["right_buffer_contract"]["minimum_valid_h1_bars"] == 12,
        "C0_UNCHANGED_FIELD_MISMATCH",
    )
    require(
        c0_contract["prior_phase_binding"]["fq_remediation"] == "DEFERRED"
        and c0_contract["prior_phase_binding"]["material_limitation"] == "RETAINED",
        "C0_FQ_BINDING_MISMATCH",
    )
    return auth, hashes, c0_contract


def build_contract(auth, bound_hashes):
    correction_record = {
        "reason_code": "C0_EXACT_SYMBOL_LITERAL_BINDING_DEFECT",
        "correction_type": "ADDITIVE_SUPPLEMENT",
        "superseded_field": "C0.future_raw_artifact.exact_symbol",
        "only_field_superseded": True,
        "original_exact_symbol": ORIGINAL_SYMBOL,
        "corrected_symbol_identity": expected_symbol_identity(),
        "exact_comparison_policy": expected_exact_comparison_policy(),
        "c0_immutability": "REQUIRED",
        "other_c0_fields_superseded": [],
    }
    correction_record_sha256 = canonical_digest(correction_record)
    effective_identity_payload = {
        "c0_canonical_summary_sha256": EXPECTED_C0_IDENTITY,
        "c0_contract_record_sha256": EXPECTED_C0_RECORD,
        "c0a_correction_record": correction_record,
        "corrected_exact_symbol_utf8_identity": expected_symbol_identity(),
    }
    effective_identity = canonical_digest(effective_identity_payload)
    conclusions = {
        "original_c0_contract": "IMMUTABLE",
        "original_c0_symbol_binding": ORIGINAL_SYMBOL,
        "original_c0_symbol_binding_status": "DEFECT_CONFIRMED",
        "correction_type": "ADDITIVE_SUPPLEMENT",
        "corrected_exact_symbol": CORRECTED_SYMBOL,
        "corrected_exact_symbol_utf8_hex": CORRECTED_UTF8_HEX,
        "corrected_exact_symbol_character_length": 5,
        "symbol_aliasing": "PROHIBITED",
        "effective_phase_c_symbol_binding": "FROZEN",
        "server_binding": "UNCHANGED_XMGLOBAL_MT5_2",
        "timeframe_binding": "UNCHANGED_H1",
        "analysis_window": "UNCHANGED",
        "requested_export_window": "UNCHANGED",
        "right_buffer_requirement": "UNCHANGED_12_VALID_H1_BARS",
        "strategy_file": "UNCHANGED",
        "prior_fq_remediation": "DEFERRED_AND_NOT_RESUMED",
        "phase_c_dataset_acquired": False,
        "dataset_intake": "NOT_STARTED",
        "detector_execution": "NOT_AUTHORIZED",
        "event_generation": "NOT_AUTHORIZED",
        "outcome_execution": "NOT_AUTHORIZED",
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "next_allowed_scope": "FR_PHASE_C1_MANUAL_RAW_DATA_ACQUISITION_AND_IMMUTABLE_INTAKE_ONLY",
    }
    contract = {
        "schema_version": "fr_phase_c0a_exact_xm_symbol_binding_correction.v1",
        "checkpoint": "FR_PHASE_C0A",
        "execution_status": "PASS",
        "decision": PASS,
        "authorization_scope": "ADDITIVE_EXACT_XM_GOLD_HASH_SYMBOL_BINDING_CORRECTION_ONLY",
        "preflight": copy.deepcopy(auth["preflight"]),
        "c0_binding": copy.deepcopy(auth["c0_binding"]),
        "bound_artifact_hashes": {
            key: bound_hashes[key] for key in sorted(bound_hashes)
        },
        "correction_record": correction_record,
        "dataset_identity_policy": copy.deepcopy(auth["dataset_identity_policy"]),
        "effective_acquisition_binding": copy.deepcopy(auth["effective_acquisition_binding"]),
        "unchanged_invariants": copy.deepcopy(auth["unchanged_invariants"]),
        "effective_identity_components": {
            "c0_canonical_summary_sha256": EXPECTED_C0_IDENTITY,
            "c0_contract_record_sha256": EXPECTED_C0_RECORD,
            "c0a_correction_record_sha256": correction_record_sha256,
            "corrected_exact_symbol_utf8_identity": expected_symbol_identity(),
            "required_by_future_checkpoints": ["C1", "C2", "C3"],
        },
        "conclusions": conclusions,
        "file_creation_boundary": copy.deepcopy(auth["file_creation_boundary"]),
        "determinism": {
            "normal_run_1": "PASS",
            "normal_run_2": "PASS",
            "normal_runs_canonical_correction_record_identical": True,
            "normal_runs_effective_identity_identical": True,
            "normal_runs_ordering_and_hashes_identical": True,
            "controlled_relocation_run": "PASS",
            "relocation_canonical_correction_record_identical": True,
            "relocation_effective_identity_identical": True,
            "relocation_ordering_and_hashes_identical": True,
            "temporary_artifacts_deleted": True,
            "absolute_runtime_paths_excluded": True,
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
                "head",
                "origin_alignment",
                "protected_stash",
                "worktree_preflight",
                "c0_decision",
                "c0_canonical_identity",
                "c0_contract_record",
                "c0_commit",
                "c0_artifact_hash",
                "c0_contract_summary",
                "c0_original_symbol",
                "c0_unchanged_fields",
                "strategy_git_blob_sha1",
                "strategy_content_sha256",
                "schema",
                "determinism",
                "file_creation_boundary",
            )
        },
        "prohibited_counts": {
            name: 0
            for name in (
                "c0_files_modified",
                "existing_files_modified",
                "raw_artifact_reads",
                "external_operator_path_accesses",
                "external_directory_creations",
                "mt5_launch",
                "network_access",
                "external_process_execution",
                "fq_remediation_actions",
                "detector_execution",
                "events_generated",
                "outcomes_executed",
                "statistics_executed",
                "strategy_modifications",
                "indicator_additions",
                "parameter_changes",
                "tp_sl_design",
                "lot_sizing_design",
                "cost_cash_pl_order_simulation",
                "profitability_edge_robustness_readiness_claims",
                "credentials_leaked",
                "absolute_paths_in_canonical_identity",
                "docs_fixtures_raw_staging_input_content_created",
                "pr_created",
                "prohibited_imports",
            )
        },
        "output_hashes": {
            "correction_record_sha256": correction_record_sha256,
            "effective_acquisition_contract_identity_sha256": effective_identity,
        },
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

    check("wrong_branch_or_head", lambda x: x["preflight"].update(branch="wrong", head="0" * 40))
    check("changed_c0_decision", lambda x: x["c0_binding"].update(decision="wrong"))
    check("changed_c0_canonical_summary_hash", lambda x: x["c0_binding"].update(canonical_summary_sha256="0" * 64))
    check("changed_c0_contract_record_hash", lambda x: x["c0_binding"].update(contract_record_sha256="1" * 64))
    check("original_c0_file_modification_attempted", lambda x: x["c0_binding"].update(original_files="MODIFICATION_AUTHORIZED"))
    check("corrected_symbol_set_to_gold", lambda x: x["correction"]["corrected_symbol_identity"].update(exact_literal="GOLD"))
    check("corrected_symbol_set_to_goldm_hash", lambda x: x["correction"]["corrected_symbol_identity"].update(exact_literal="GOLDm#"))
    check("corrected_symbol_set_to_goldm", lambda x: x["correction"]["corrected_symbol_identity"].update(exact_literal="GOLDm"))
    check("corrected_symbol_set_to_xauusd_or_xau_slash_usd", lambda x: x["correction"]["corrected_symbol_identity"].update(exact_literal="XAU/USD"))
    check("corrected_symbol_missing_final_hash", lambda x: x["correction"]["corrected_symbol_identity"].update(exact_literal=CORRECTED_SYMBOL[:-1]))
    check("symbol_whitespace_case_change_or_alias_accepted", lambda x: x["correction"]["exact_comparison_policy"].update(case_sensitive=False, trim="AUTHORIZED", alias="AUTHORIZED"))
    check("utf8_hex_not_474f4c4423", lambda x: x["correction"]["corrected_symbol_identity"].update(utf8_hex="474f4c44"))
    check("character_length_not_five", lambda x: x["correction"]["corrected_symbol_identity"].update(character_length=4))
    check("server_or_timeframe_changed", lambda x: x["effective_acquisition_binding"].update(exact_server="OTHER", timeframe="M1"))
    check("analysis_or_export_window_changed", lambda x: x["unchanged_invariants"].update(analysis_end="2026-07-01T000000", requested_export_end="2026-07-08T235959"))
    check("right_buffer_requirement_changed", lambda x: x["unchanged_invariants"].update(right_buffer_valid_h1_bars=11))
    check("raw_acquisition_external_scan_or_mt5_launch_attempted", lambda x: x["operation_authorizations"].update(raw_acquisition=True, external_directory_scan=True, mt5_launch=True))
    check("fq_remediation_resumed", lambda x: x["unchanged_invariants"].update(fq_remediation="RESUMED"))
    check("detector_event_outcome_or_statistics_execution_authorized", lambda x: x["operation_authorizations"].update(detector_execution=True, event_generation=True, outcome_execution=True, statistics_execution=True))
    check("strategy_indicator_or_parameter_modification_authorized", lambda x: x["operation_authorizations"].update(strategy_modification=True, indicator_addition=True, parameter_change=True))
    check("tp_sl_lot_cost_cash_pl_or_order_simulation_authorized", lambda x: x["operation_authorizations"].update(tp_sl_design=True, lot_sizing=True, costs_or_cash_pl=True, order_simulation=True))
    check("profitability_edge_robustness_or_readiness_claimed", lambda x: x["claims"].update(profitability="CLAIMED", strategy_edge="ESTABLISHED", robustness="ESTABLISHED", readiness="READY"))
    check("credential_account_token_or_absolute_path_leakage", lambda x: x["sensitive_data_policy"].update(absolute_runtime_path_in_canonical_identity="AUTHORIZED", credentials_account_or_token="AUTHORIZED"))
    check("existing_file_modified", lambda x: x["file_creation_boundary"].update(existing_file_modification_authorized=True))
    check("pr_creation", lambda x: x["file_creation_boundary"].update(pr_creation_authorized=True))

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
    paths = [
        AUTH.relative_to(ROOT),
        AUTH_SCHEMA.relative_to(ROOT),
        CONTRACT_SCHEMA.relative_to(ROOT),
    ]
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

    auth_1, hashes_1, _c0_1 = load_and_validate(ROOT)
    negative_results = run_negative_tests(auth_1)
    contract_1 = build_contract(auth_1, hashes_1)

    auth_2, hashes_2, _c0_2 = load_and_validate(ROOT)
    contract_2 = build_contract(auth_2, hashes_2)
    require(contract_1 == contract_2, "NORMAL_REPEAT_CONTRACT_MISMATCH")
    require(hashes_1 == hashes_2, "NORMAL_REPEAT_HASH_MISMATCH")

    with tempfile.TemporaryDirectory(prefix="fr_phase_c0a_") as temporary:
        relocated = Path(temporary) / "relocated_repository"
        copy_relocation_inputs(auth_1, relocated)
        relocated_auth, relocated_hashes, _relocated_c0 = load_and_validate(relocated)
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
                "correction_record_sha256": contract_1["output_hashes"]["correction_record_sha256"],
                "decision": PASS,
                "effective_acquisition_contract_identity_sha256": contract_1["output_hashes"]["effective_acquisition_contract_identity_sha256"],
                "negative_tests": f"{len(negative_results)}/{len(NEGATIVE_TEST_NAMES)}",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
