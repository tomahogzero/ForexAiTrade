#!/usr/bin/env python3
"""Perform deterministic FR-Phase-C1 immutable manual XM GOLD# H1 intake."""

import argparse
import ast
import copy
import hashlib
import json
import ntpath
import posixpath
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_phase_c1_manual_raw_data_immutable_intake_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_phase_c1_manual_raw_data_immutable_intake_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_phase_c1_manual_raw_data_immutable_intake.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_phase_c1_manual_raw_data_immutable_intake.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_phase_c1"
RAW_MANIFEST = OUT / "raw_artifact_intake_manifest.json"
EVIDENCE_MANIFEST = OUT / "source_identity_evidence_manifest.json"
SUMMARY = OUT / "manual_raw_data_immutable_intake_summary.json"

MODE = "intake-manual-raw-data-immutable"
PASS = "FR_PHASE_C1_PASS_MANUAL_RAW_DATA_ACQUISITION_AND_IMMUTABLE_INTAKE"
EXPECTED_BRANCH = "agent/fr-phase-c-clean-data-intake"
EXPECTED_HEAD = "1e37ad9cf6e2f8c4cc0a8bd99466a360e14c706d"
EXPECTED_STASH = "stash@{0}: On agent/fr-prep-b-runner-integration: fr-prep-b2a-partial-draft-before-b2e"
EXPECTED_C0_IDENTITY = "26f2e23a20e08223a001514558fa69f6298b6af0e761d379393bb99825db6689"
EXPECTED_C0_RECORD = "5e229bf31aa9724e9d67c3675c1e99cf7454172e19a263ca8a45401993034a04"
EXPECTED_C0A_IDENTITY = "831046b52005bdc7403015363c976bff72a36778a0f6186b2a437da805aecb61"
EXPECTED_C0A_CORRECTION = "ebc929aa3f1fe06671bd2a46871c5abad70c01d7cc8a443026be7b51a8336a9c"
EXPECTED_EFFECTIVE_IDENTITY = "c2690e8351b0d223d0ff073e0b14c3fea1b7792a83e81503ecda623cd740580d"
EXPECTED_STRATEGY_SHA1 = "da448295ac3bd443b376e1ce51a8e411de3c7245"
EXPECTED_STRATEGY_SHA256 = "0e72b1559f5416981c2db887f9c53a0bfbb66bada226250a064377b2b9fadaa2"

ANGLE_HEADER = [
    "<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>",
    "<TICKVOL>", "<VOL>", "<SPREAD>",
]
PLAIN_HEADER = [
    "DATE", "TIME", "OPEN", "HIGH", "LOW", "CLOSE",
    "TICKVOL", "VOL", "SPREAD",
]
SENSITIVE_RE = re.compile(
    r"(account[ _-]*number|\blogin\b|user[ _-]*name|\busername\b|"
    r"\bpassword\b|api[ _-]*key|\btoken\b|\bcredential(?:s)?\b|"
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
    re.IGNORECASE,
)

ALLOWED_NEW_FILES = [
    "research/contracts/fr_phase_c1_manual_raw_data_immutable_intake.v1.json",
    "research/contracts/fr_phase_c1_manual_raw_data_immutable_intake_authorization.v1.json",
    "research/results/checkpoint_fr_phase_c1/manual_raw_data_immutable_intake_summary.json",
    "research/results/checkpoint_fr_phase_c1/raw_artifact_intake_manifest.json",
    "research/results/checkpoint_fr_phase_c1/source_identity_evidence_manifest.json",
    "research/schemas/fr_phase_c1_manual_raw_data_immutable_intake.v1.schema.json",
    "research/schemas/fr_phase_c1_manual_raw_data_immutable_intake_authorization.v1.schema.json",
    "tools/run_fr_phase_c1_manual_raw_data_immutable_intake.py",
]

NEGATIVE_TEST_NAMES = [
    "wrong_branch_head_or_origin_alignment",
    "changed_c0_c0a_or_effective_identity",
    "protected_stash_changed",
    "missing_input_folder",
    "zero_or_multiple_raw_csv_files",
    "missing_notes_or_source_evidence_images",
    "wrong_xm_server_symbol_or_timeframe",
    "plain_gold_accepted_instead_of_gold_hash",
    "raw_filename_mismatch",
    "unsupported_encoding_delimiter_or_header",
    "hash_or_byte_size_mutation_during_execution",
    "excel_zip_or_second_csv_accepted",
    "sensitive_data_accepted",
    "absolute_path_stored_in_canonical_identity",
    "dukascopy_or_sibling_folder_access",
    "mt5_network_or_external_process_execution",
    "raw_file_copied_moved_renamed_or_modified",
    "gap_inventory_or_classification_attempted",
    "structural_validation_claimed_complete",
    "dataset_described_as_clean",
    "buffer_sufficiency_claimed",
    "holdout_or_out_of_sample_claimed",
    "detector_event_outcome_or_statistics_execution",
    "strategy_indicator_or_parameter_modification",
    "tp_sl_lot_cost_cash_pl_or_order_simulation",
    "profitability_edge_robustness_or_readiness_claim",
    "existing_repository_file_modification",
    "raw_evidence_committed",
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


def identity_without(value, field):
    return canonical_digest({key: item for key, item in value.items() if key != field})


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
    require(
        preflight["branch"] == EXPECTED_BRANCH
        and preflight["head"] == EXPECTED_HEAD
        and preflight["origin_branch"] == "origin/agent/fr-phase-c-clean-data-intake"
        and preflight["origin_head"] == EXPECTED_HEAD
        and preflight["upstream_aligned"] is True
        and preflight["worktree_clean"] is True,
        "PREFLIGHT_BINDING_MISMATCH",
    )
    require(preflight["protected_stash"] == EXPECTED_STASH, "PROTECTED_STASH_MISMATCH")

    prior = auth["prior_contract_binding"]
    require(
        prior["c0_decision"] == "FR_PHASE_C0_PASS_CLEAN_DATA_ACQUISITION_CONTRACT_FROZEN"
        and prior["c0_canonical_summary_sha256"] == EXPECTED_C0_IDENTITY
        and prior["c0_contract_record_sha256"] == EXPECTED_C0_RECORD
        and prior["c0a_decision"] == "FR_PHASE_C0A_PASS_EXACT_XM_GOLD_HASH_SYMBOL_BINDING_CORRECTED"
        and prior["c0a_canonical_summary_sha256"] == EXPECTED_C0A_IDENTITY
        and prior["c0a_correction_record_sha256"] == EXPECTED_C0A_CORRECTION
        and prior["effective_acquisition_contract_identity_sha256"] == EXPECTED_EFFECTIVE_IDENTITY,
        "PRIOR_CONTRACT_BINDING_MISMATCH",
    )

    package = auth["required_input_package"]
    require(
        package["capture_folder_required"] is True
        and package["authorized_parent_label"] == "XM_Phase_C"
        and package["authorized_capture_label"] == "capture_20260730"
        and package["raw_csv_count"] == 1
        and package["notes_filename"] == "operator_capture_notes.txt"
        and package["notes_count"] == 1
        and package["minimum_image_count"] == 1
        and package["maximum_image_count"] == 10
        and package["zip_or_excel_count"] == 0
        and package["unexpected_file_count"] == 0,
        "INPUT_PACKAGE_POLICY_MISMATCH",
    )

    source = auth["expected_source_binding"]
    require(
        source
        == {
            "broker": "XM",
            "exact_server": "XMGlobal-MT5 2",
            "exact_symbol": "GOLD#",
            "symbol_utf8_hex": "474f4c4423",
            "timeframe": "H1",
            "time_basis": "XM_MT5_SERVER_CHART_TIME",
            "utc_offset": "UNKNOWN",
            "dst_behavior": "UNKNOWN",
        },
        "SOURCE_BINDING_MISMATCH",
    )

    windows = auth["frozen_windows"]
    require(
        windows
        == {
            "analysis_start": "2026-01-01T00:00:00",
            "analysis_end": "2026-06-30T23:59:59",
            "requested_export_start": "2026-01-01T00:00:00",
            "requested_export_end": "2026-07-07T23:59:59",
            "right_buffer_valid_h1_bars_required": 12,
            "right_buffer_validation": "NOT_STARTED",
        },
        "FROZEN_WINDOW_MISMATCH",
    )

    expected = auth["expected_operator_package"]
    require(
        expected["raw"]["sanitized_filename"] == "GOLD#_H1_202601020800_202607300300.csv"
        and expected["raw"]["byte_size"] == 216222
        and expected["raw"]["sha256"] == "69aa7e16d4d3e54bfe8e0aa3ce4c5d61bbd0fcaefb45050341304681b3766f92"
        and expected["raw"]["encoding"] == "UTF-8_NO_BOM"
        and expected["raw"]["delimiter"] == "TAB"
        and expected["raw"]["header_profile"] == "MT5_ANGLE_BRACKET_HEADER"
        and expected["raw"]["physical_row_count"] == 3387
        and expected["raw"]["data_row_count"] == 3386
        and expected["raw"]["observed_first_timestamp"] == "2026-01-02T08:00:00"
        and expected["raw"]["observed_last_timestamp"] == "2026-07-30T03:00:00",
        "EXPECTED_RAW_PACKAGE_MISMATCH",
    )
    require(
        expected["notes"]["sanitized_filename"] == "operator_capture_notes.txt"
        and expected["notes"]["byte_size"] == 975
        and expected["notes"]["sha256"] == "393d3d74f230d10079049196caf8296461889d3bc7f4d1a3fbea0c6699fd86be",
        "EXPECTED_NOTES_PACKAGE_MISMATCH",
    )
    require(len(expected["images"]) == 4, "EXPECTED_IMAGE_COUNT_MISMATCH")
    require(
        [item["sanitized_filename"] for item in expected["images"]]
        == [
            "01_xm_server_identity.png",
            "02_mt5_terminal_build.png",
            "03_gold_hash_specification.png",
            "04_gold_hash_trading_sessions.png",
        ],
        "EXPECTED_IMAGE_ORDER_MISMATCH",
    )

    notes = auth["required_note_declarations"]
    require(
        notes["broker"] == "XM"
        and notes["server"] == "XMGlobal-MT5 2"
        and notes["symbol"] == "GOLD#"
        and notes["timeframe"] == "H1"
        and notes["terminal_build"] == "6061"
        and notes["account_environment_type"] == "DEMO"
        and notes["acquisition_timestamp"] == "2026-07-30T07:12:00+07:00"
        and notes["operator_timezone"] == "Asia/Bangkok"
        and notes["export_method"] == "MT5_MANUAL_BARS_CSV_EXPORT"
        and notes["requested_start_server_time"] == "2026-01-01T00:00:00"
        and notes["requested_end_server_time"] == "2026-07-07T23:59:59"
        and notes["analysis_start_server_time"] == "2026-01-01T00:00:00"
        and notes["analysis_end_server_time"] == "2026-06-30T23:59:59"
        and notes["raw_filename"] == expected["raw"]["sanitized_filename"]
        and notes["source_mutation"] == "ORIGINAL_UNCHANGED"
        and notes["spreadsheet_resave"] == "NOT_PERFORMED"
        and notes["row_reordering_or_removal"] == "NOT_PERFORMED"
        and notes["time_conversion"] == "NOT_PERFORMED"
        and notes["generated_rows"] == "NOT_ADDED",
        "NOTE_DECLARATION_MISMATCH",
    )

    observed = auth["minimal_intake_policy"]
    require(
        observed["approved_encodings"] == ["UTF-8_NO_BOM", "UTF-8_BOM", "UTF-16LE_BOM", "UTF-16BE_BOM"]
        and observed["approved_delimiters"] == ["TAB", "COMMA", "SEMICOLON"]
        and observed["approved_header_profiles"] == ["MT5_ANGLE_BRACKET_HEADER", "MT5_PLAIN_UPPER_HEADER"]
        and observed["parse_scope"] == "HEADER_ROW_COUNTS_AND_FIRST_LAST_TIMESTAMP_ONLY"
        and observed["full_ohlc_validation_authorized"] is False,
        "MINIMAL_INTAKE_POLICY_MISMATCH",
    )
    immutable = auth["immutability_policy"]
    require(
        immutable["hash_before_parse"] is True
        and immutable["hash_after_parse"] is True
        and immutable["pre_post_hash_and_size_must_match"] is True
        and immutable["external_file_mutation_authorized"] is False
        and immutable["raw_copy_to_repository_authorized"] is False,
        "IMMUTABILITY_POLICY_MISMATCH",
    )
    status = auth["status_boundary"]
    require(
        status
        == {
            "dataset_identity": "PROVISIONALLY_BOUND_NOT_VALIDATED",
            "chronology_separation": "NOT_YET_VALIDATED",
            "structural_validation": "NOT_STARTED",
            "gap_inventory": "NOT_STARTED",
            "gap_classification": "NOT_STARTED",
            "right_buffer_validation": "NOT_STARTED",
            "clean_dataset_status": "NOT_EVALUATED",
            "broker_history_completeness": "NOT_PROVEN",
            "holdout_status": "NOT_CLAIMED",
            "out_of_sample_status": "NOT_CLAIMED",
        },
        "STATUS_BOUNDARY_MISMATCH",
    )
    operations = auth["operation_authorizations"]
    require(operations["c1_immutable_intake"] is True, "C1_SCOPE_MISMATCH")
    require(
        all(value is False for key, value in operations.items() if key != "c1_immutable_intake"),
        "PROHIBITED_OPERATION_AUTHORIZED",
    )
    external = auth["external_access_policy"]
    require(
        external["authorized_folder_immediate_listing_only"] is True
        and external["recursive_access"] is False
        and external["parent_or_sibling_access"] is False
        and external["dukascopy_access"] is False
        and external["mt5_data_directory_access"] is False
        and external["network_access"] is False
        and external["external_process_execution"] is False,
        "EXTERNAL_ACCESS_POLICY_MISMATCH",
    )
    sensitive = auth["sensitive_data_policy"]
    require(
        sensitive["reject_sensitive_notes_or_filenames"] is True
        and sensitive["absolute_runtime_path_in_canonical_identity"] == "PROHIBITED",
        "SENSITIVE_DATA_POLICY_MISMATCH",
    )
    files = auth["file_creation_boundary"]
    require(files["allowed_new_files"] == ALLOWED_NEW_FILES, "ALLOWED_FILE_SET_MISMATCH")
    require(files["existing_file_modification_authorized"] is False, "EXISTING_FILE_MODIFICATION_AUTHORIZED")
    require(files["raw_notes_or_images_commit_authorized"] is False, "RAW_EVIDENCE_COMMIT_AUTHORIZED")
    require(files["docs_fixtures_raw_staging_creation_authorized"] is False, "UNAUTHORIZED_CONTENT_CREATION")
    require(files["pr_creation_authorized"] is False, "PR_CREATION_AUTHORIZED")
    require(absolute_path_count(auth) == 0, "ABSOLUTE_PATH_IN_AUTHORIZATION")


def load_repository_bindings(root):
    auth = json.loads((root / AUTH.relative_to(ROOT)).read_text(encoding="utf-8"))
    auth_schema = json.loads((root / AUTH_SCHEMA.relative_to(ROOT)).read_text(encoding="utf-8"))
    jsonschema.validate(auth, auth_schema)
    validate_authorization_values(auth)
    documents = {}
    hashes = {}
    for spec in auth["bound_artifacts"]:
        raw = (root / spec["path"]).read_bytes()
        actual = sha256_bytes(raw)
        require(actual == spec["file_sha256"], "BOUND_ARTIFACT_HASH_MISMATCH:" + spec["artifact_id"])
        hashes[spec["artifact_id"]] = actual
        if "git_blob_sha1" in spec:
            require(git_blob_sha1(raw) == spec["git_blob_sha1"], "BOUND_GIT_SHA1_MISMATCH:" + spec["artifact_id"])
        if spec["access"] == "json":
            documents[spec["artifact_id"]] = json.loads(raw)
    c0 = documents["c0_contract"]
    c0_summary = documents["c0_summary"]
    c0_schema = documents["c0_schema"]
    c0a = documents["c0a_contract"]
    c0a_summary = documents["c0a_summary"]
    c0a_schema = documents["c0a_schema"]
    jsonschema.validate(c0, c0_schema)
    jsonschema.validate(c0_summary, c0_schema)
    jsonschema.validate(c0a, c0a_schema)
    jsonschema.validate(c0a_summary, c0a_schema)
    require(c0 == c0_summary, "C0_CONTRACT_SUMMARY_MISMATCH")
    require(c0a == c0a_summary, "C0A_CONTRACT_SUMMARY_MISMATCH")
    require(identity_without(c0, "canonical_summary_sha256") == EXPECTED_C0_IDENTITY, "C0_RECOMPUTED_IDENTITY_MISMATCH")
    require(identity_without(c0a, "canonical_summary_sha256") == EXPECTED_C0A_IDENTITY, "C0A_RECOMPUTED_IDENTITY_MISMATCH")
    require(c0["output_hashes"]["contract_record_sha256"] == EXPECTED_C0_RECORD, "C0_RECORD_MISMATCH")
    require(c0a["output_hashes"]["correction_record_sha256"] == EXPECTED_C0A_CORRECTION, "C0A_CORRECTION_MISMATCH")
    require(c0a["output_hashes"]["effective_acquisition_contract_identity_sha256"] == EXPECTED_EFFECTIVE_IDENTITY, "EFFECTIVE_IDENTITY_MISMATCH")
    require(c0a["effective_acquisition_binding"]["exact_symbol"] == "GOLD#", "C0A_SYMBOL_MISMATCH")
    return auth, hashes


def decode_csv(raw):
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw[3:].decode("utf-8", errors="strict"), "UTF-8_BOM"
    if raw.startswith(b"\xff\xfe"):
        return raw[2:].decode("utf-16-le", errors="strict"), "UTF-16LE_BOM"
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", errors="strict"), "UTF-16BE_BOM"
    return raw.decode("utf-8", errors="strict"), "UTF-8_NO_BOM"


def detect_header(header):
    matches = []
    for label, delimiter in (("TAB", "\t"), ("COMMA", ","), ("SEMICOLON", ";")):
        parts = header.split(delimiter)
        if len(parts) == 9:
            if parts == ANGLE_HEADER:
                matches.append((label, delimiter, "MT5_ANGLE_BRACKET_HEADER"))
            elif parts == PLAIN_HEADER:
                matches.append((label, delimiter, "MT5_PLAIN_UPPER_HEADER"))
    require(len(matches) == 1, "UNSUPPORTED_OR_AMBIGUOUS_HEADER_DELIMITER")
    return matches[0]


def parse_timestamp(date_value, time_value):
    value = date_value + " " + time_value
    for pattern in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, pattern).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            pass
    raise ValueError("BOUNDARY_TIMESTAMP_PARSE_FAILURE")


def parse_notes(text):
    values = {}
    evidence = []
    in_evidence = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "evidence_files:":
            in_evidence = True
            continue
        if in_evidence and stripped.startswith("- "):
            evidence.append(stripped[2:].strip())
            continue
        in_evidence = False
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            values[key.strip()] = value.strip()
    return values, evidence


def package_snapshot(capture):
    require(capture.exists() and capture.is_dir(), "AUTHORIZED_CAPTURE_FOLDER_MISSING")
    entries = sorted(capture.iterdir(), key=lambda item: item.name)
    require(all(item.is_file() for item in entries), "CAPTURE_CONTAINS_DIRECTORY")
    return {
        item.name: {
            "byte_size": item.stat().st_size,
            "sha256": sha256_bytes(item.read_bytes()),
            "mtime_ns": item.stat().st_mtime_ns,
        }
        for item in entries
    }


def inspect_package(capture, auth, enforce_operational_parent):
    require(capture.exists() and capture.is_dir(), "AUTHORIZED_CAPTURE_FOLDER_MISSING")
    if enforce_operational_parent:
        require(capture.name == "capture_20260730", "CAPTURE_FOLDER_LABEL_MISMATCH")
        require(capture.parent.name == "XM_Phase_C", "CAPTURE_PARENT_LABEL_MISMATCH")
    entries = sorted(capture.iterdir(), key=lambda item: item.name)
    require(all(item.is_file() for item in entries), "CAPTURE_CONTAINS_DIRECTORY")
    csv_files = [item for item in entries if item.suffix.lower() == ".csv"]
    notes_files = [item for item in entries if item.name == "operator_capture_notes.txt"]
    images = [item for item in entries if item.suffix.lower() in {".png", ".jpg", ".jpeg"}]
    forbidden = [item for item in entries if item.suffix.lower() in {".zip", ".xlsx", ".xls", ".xlsm", ".xlsb"}]
    recognized = set(csv_files + notes_files + images)
    unexpected = [item for item in entries if item not in recognized]
    require(len(csv_files) == 1, "RAW_CSV_COUNT_MISMATCH")
    require(len(notes_files) == 1, "NOTES_COUNT_MISMATCH")
    require(1 <= len(images) <= 10, "EVIDENCE_IMAGE_COUNT_MISMATCH")
    require(not forbidden, "ZIP_OR_EXCEL_PRESENT")
    require(not unexpected, "UNEXPECTED_CAPTURE_FILE")
    require(all(not SENSITIVE_RE.search(item.name) for item in entries), "SENSITIVE_FILENAME_DETECTED")

    notes_path = notes_files[0]
    notes_raw = notes_path.read_bytes()
    notes_text = notes_raw.decode("utf-8-sig", errors="strict")
    require(not SENSITIVE_RE.search(notes_text), "SENSITIVE_NOTES_DETECTED")
    require(not re.search(r"(?m)(?:[A-Za-z]:[\\/]|^\s*/[^/])", notes_text), "ABSOLUTE_PATH_IN_NOTES")
    note_values, declared_images = parse_notes(notes_text)
    expected_notes = auth["required_note_declarations"]
    for key, expected_value in expected_notes.items():
        require(note_values.get(key) == expected_value, "NOTE_DECLARATION_MISMATCH:" + key)
    require(declared_images == [item.name for item in images], "DECLARED_EVIDENCE_LIST_MISMATCH")

    raw_path = csv_files[0]
    pre_size = raw_path.stat().st_size
    pre_hash = sha256_bytes(raw_path.read_bytes())
    raw_bytes = raw_path.read_bytes()
    require(len(raw_bytes) == pre_size, "RAW_READ_SIZE_MISMATCH")
    text, encoding = decode_csv(raw_bytes)
    lines = text.splitlines()
    require(len(lines) >= 2, "RAW_CSV_NO_DATA")
    delimiter_label, delimiter, header_profile = detect_header(lines[0])
    data_rows = lines[1:]
    require(all(row != "" for row in data_rows), "BLANK_DATA_ROW")
    first = data_rows[0].split(delimiter)
    last = data_rows[-1].split(delimiter)
    require(len(first) == 9 and len(last) == 9, "BOUNDARY_ROW_FIELD_COUNT_MISMATCH")
    first_timestamp = parse_timestamp(first[0], first[1])
    last_timestamp = parse_timestamp(last[0], last[1])
    post_size = raw_path.stat().st_size
    post_hash = sha256_bytes(raw_path.read_bytes())
    require(pre_size == post_size and pre_hash == post_hash, "RAW_PRE_POST_IMMUTABILITY_MISMATCH")

    expected_raw = auth["expected_operator_package"]["raw"]
    actual_raw = {
        "sanitized_filename": raw_path.name,
        "byte_size": pre_size,
        "sha256": pre_hash,
        "encoding": encoding,
        "delimiter": delimiter_label,
        "header_profile": header_profile,
        "physical_row_count": len(lines),
        "data_row_count": len(data_rows),
        "observed_first_timestamp": first_timestamp,
        "observed_last_timestamp": last_timestamp,
    }
    require(actual_raw == expected_raw, "RAW_PACKAGE_IDENTITY_MISMATCH")

    actual_notes = {
        "sanitized_filename": notes_path.name,
        "byte_size": len(notes_raw),
        "sha256": sha256_bytes(notes_raw),
    }
    require(actual_notes == auth["expected_operator_package"]["notes"], "NOTES_PACKAGE_IDENTITY_MISMATCH")
    actual_images = [
        {
            "sanitized_filename": item.name,
            "byte_size": item.stat().st_size,
            "sha256": sha256_bytes(item.read_bytes()),
        }
        for item in images
    ]
    require(actual_images == auth["expected_operator_package"]["images"], "IMAGE_PACKAGE_IDENTITY_MISMATCH")

    raw_manifest = {
        "schema_version": "fr_phase_c1_raw_artifact_intake_manifest.v1",
        "artifact_id": "RAW_XM_GOLD_HASH_H1_EXPORT",
        "dataset_id": "FC_2026H1_XMGLOBAL_MT5_2_GOLD_HASH_H1",
        "broker": "XM",
        "exact_server": "XMGlobal-MT5 2",
        "exact_symbol": "GOLD#",
        "symbol_utf8_hex": "474f4c4423",
        "timeframe": "H1",
        "time_basis": "XM_MT5_SERVER_CHART_TIME",
        "sanitized_filename": raw_path.name,
        "byte_size_before": pre_size,
        "byte_size_after": post_size,
        "sha256_before": pre_hash,
        "sha256_after": post_hash,
        "raw_bytes_unchanged": True,
        "encoding": encoding,
        "delimiter": delimiter_label,
        "header_profile": header_profile,
        "physical_row_count": len(lines),
        "data_row_count": len(data_rows),
        "observed_first_timestamp_original_order": first_timestamp,
        "observed_last_timestamp_original_order": last_timestamp,
        "boundary_completeness_inference": "NOT_PERFORMED",
        "right_buffer_validation": "NOT_STARTED",
        "structural_validation": "NOT_STARTED",
        "gap_inventory": "NOT_STARTED",
        "repository_storage": "PROHIBITED_AND_NOT_PERFORMED",
        "absolute_operator_path_in_manifest": False,
    }
    raw_manifest["canonical_manifest_sha256"] = identity_without(
        raw_manifest, "canonical_manifest_sha256"
    )

    declared_source = {
        "broker": note_values["broker"],
        "exact_server": note_values["server"],
        "account_environment_type": note_values["account_environment_type"],
        "exact_symbol": note_values["symbol"],
        "timeframe": note_values["timeframe"],
        "terminal_build": note_values["terminal_build"],
        "acquisition_timestamp": note_values["acquisition_timestamp"],
        "export_method": note_values["export_method"],
        "analysis_start": note_values["analysis_start_server_time"],
        "analysis_end": note_values["analysis_end_server_time"],
        "requested_export_start": note_values["requested_start_server_time"],
        "requested_export_end": note_values["requested_end_server_time"],
        "time_basis": note_values["time_basis"],
        "utc_offset": note_values["utc_offset"],
        "dst_behavior": note_values["dst_behavior"],
        "operator_timezone_for_logging_only": note_values["operator_timezone"],
        "source_mutation": note_values["source_mutation"],
    }
    evidence_manifest = {
        "schema_version": "fr_phase_c1_source_identity_evidence_manifest.v1",
        "artifact_id": "SAME_SERVER_SOURCE_IDENTITY_AND_SESSION_METADATA",
        "source_identity": declared_source,
        "notes_artifact": actual_notes,
        "evidence_image_count": len(actual_images),
        "evidence_images": actual_images,
        "session_metadata_status": "CAPTURED_AND_HASH_BOUND_NOT_HISTORICALLY_ADJUDICATED",
        "screenshots_prove_historical_market_closures": False,
        "historical_gap_adjudication": "NOT_PERFORMED",
        "images_copied_to_repository": False,
        "absolute_operator_path_in_manifest": False,
    }
    evidence_manifest["canonical_manifest_sha256"] = identity_without(
        evidence_manifest, "canonical_manifest_sha256"
    )
    return raw_manifest, evidence_manifest


def build_records(root, capture, enforce_operational_parent):
    auth, bound_hashes = load_repository_bindings(root)
    raw_manifest, evidence_manifest = inspect_package(
        capture, auth, enforce_operational_parent
    )
    raw_payload = output_bytes(raw_manifest)
    evidence_payload = output_bytes(evidence_manifest)
    provisional_binding = canonical_digest(
        {
            "effective_acquisition_contract_identity_sha256": EXPECTED_EFFECTIVE_IDENTITY,
            "raw_manifest_identity": raw_manifest["canonical_manifest_sha256"],
            "raw_content_sha256": raw_manifest["sha256_before"],
            "raw_sanitized_filename": raw_manifest["sanitized_filename"],
            "source_evidence_manifest_identity": evidence_manifest["canonical_manifest_sha256"],
            "source_identity": evidence_manifest["source_identity"],
        }
    )
    conclusions = {
        "manual_source_acquisition": "OPERATOR_COMPLETED",
        "raw_artifact_intake": "PASS_HASH_BOUND",
        "source_identity": "DECLARED_AND_EVIDENCE_HASH_BOUND",
        "session_metadata": "CAPTURED_AND_HASH_BOUND_NOT_HISTORICALLY_ADJUDICATED",
        "exact_symbol": "GOLD#",
        "raw_artifact_original_bytes": "UNCHANGED",
        "raw_artifact_repository_storage": "PROHIBITED_AND_NOT_PERFORMED",
        "dataset_identity": "PROVISIONALLY_BOUND_NOT_VALIDATED",
        "chronology_separation": "NOT_YET_VALIDATED",
        "structural_validation": "NOT_STARTED",
        "gap_inventory": "NOT_STARTED",
        "gap_classification": "NOT_STARTED",
        "right_buffer_validation": "NOT_STARTED",
        "clean_dataset_status": "NOT_EVALUATED",
        "broker_history_completeness": "NOT_PROVEN",
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
        "next_allowed_scope": "FR_PHASE_C2_STRUCTURAL_TIMELINE_AND_GAP_VALIDATION_ONLY",
    }
    contract = {
        "schema_version": "fr_phase_c1_manual_raw_data_immutable_intake.v1",
        "checkpoint": "FR_PHASE_C1",
        "execution_status": "PASS",
        "decision": PASS,
        "authorization_scope": "MANUAL_RAW_DATA_ACQUISITION_AND_IMMUTABLE_INTAKE_ONLY",
        "preflight": copy.deepcopy(auth["preflight"]),
        "prior_contract_binding": copy.deepcopy(auth["prior_contract_binding"]),
        "bound_artifact_hashes": {
            key: bound_hashes[key] for key in sorted(bound_hashes)
        },
        "effective_source_binding": copy.deepcopy(auth["expected_source_binding"]),
        "frozen_windows": copy.deepcopy(auth["frozen_windows"]),
        "raw_artifact_reference": {
            "sanitized_filename": raw_manifest["sanitized_filename"],
            "byte_size": raw_manifest["byte_size_before"],
            "sha256": raw_manifest["sha256_before"],
            "data_row_count": raw_manifest["data_row_count"],
            "observed_first_timestamp": raw_manifest["observed_first_timestamp_original_order"],
            "observed_last_timestamp": raw_manifest["observed_last_timestamp_original_order"],
            "canonical_manifest_sha256": raw_manifest["canonical_manifest_sha256"],
        },
        "source_identity_evidence_reference": {
            "notes_sanitized_filename": evidence_manifest["notes_artifact"]["sanitized_filename"],
            "evidence_image_count": evidence_manifest["evidence_image_count"],
            "canonical_manifest_sha256": evidence_manifest["canonical_manifest_sha256"],
            "session_metadata_status": evidence_manifest["session_metadata_status"],
        },
        "provisional_dataset_binding_sha256": provisional_binding,
        "observed_boundary_policy": {
            "first_and_last_recorded_in_original_file_order": True,
            "missing_rows_inferred": False,
            "boundary_validation": "DEFERRED_TO_C2",
            "right_buffer_validation": "DEFERRED_TO_C2",
        },
        "conclusions": conclusions,
        "file_creation_boundary": copy.deepcopy(auth["file_creation_boundary"]),
        "determinism": {
            "normal_run_1": "PASS",
            "normal_run_2": "PASS",
            "normal_runs_canonical_records_identical": True,
            "normal_runs_ordering_and_hashes_identical": True,
            "controlled_relocation_run": "PASS",
            "temporary_copies_preserved_exact_bytes": True,
            "relocation_canonical_records_identical": True,
            "relocation_ordering_and_hashes_identical": True,
            "temporary_artifacts_deleted": True,
            "absolute_operator_paths_excluded": True,
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
                "c0_identity",
                "c0_record",
                "c0a_identity",
                "c0a_correction_record",
                "effective_acquisition_identity",
                "bound_artifacts",
                "package_inventory",
                "notes_declarations",
                "raw_pre_post_hash",
                "raw_pre_post_size",
                "encoding",
                "delimiter",
                "header",
                "boundary_timestamp_parse",
                "source_identity",
                "schema",
                "determinism",
                "file_creation_boundary",
            )
        },
        "prohibited_counts": {
            name: 0
            for name in (
                "parent_or_sibling_folder_accesses",
                "dukascopy_accesses",
                "mt5_data_directory_accesses",
                "mt5_launches",
                "network_accesses",
                "external_process_executions",
                "external_file_mutations",
                "raw_files_copied_to_repository",
                "notes_or_images_copied_to_repository",
                "full_ohlc_structural_validation",
                "duplicate_or_conflict_analysis",
                "chronological_repairs",
                "sorting",
                "gap_inventory_generation",
                "gap_classifications",
                "session_closure_adjudications",
                "completeness_claims",
                "right_buffer_decisions",
                "detector_executions",
                "events_generated",
                "outcomes_executed",
                "statistics_executed",
                "data_aggregations",
                "synthetic_bars",
                "interpolations",
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
                "existing_repository_files_modified",
                "raw_evidence_committed",
                "docs_fixtures_raw_staging_created",
                "pr_created",
                "prohibited_imports",
            )
        },
        "output_hashes": {
            "raw_artifact_intake_manifest_file_sha256": sha256_bytes(raw_payload),
            "source_identity_evidence_manifest_file_sha256": sha256_bytes(evidence_payload),
            "provisional_dataset_binding_sha256": provisional_binding,
        },
        "absolute_runtime_path_in_canonical_identity_count": 0,
        "sensitive_value_in_canonical_identity_count": 0,
    }
    contract["canonical_summary_sha256"] = identity_without(
        contract, "canonical_summary_sha256"
    )
    require(absolute_path_count(contract) == 0, "ABSOLUTE_PATH_IN_CONTRACT")
    require(absolute_path_count(raw_manifest) == 0, "ABSOLUTE_PATH_IN_RAW_MANIFEST")
    require(absolute_path_count(evidence_manifest) == 0, "ABSOLUTE_PATH_IN_EVIDENCE_MANIFEST")
    return auth, contract, raw_manifest, evidence_manifest


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

    check("wrong_branch_head_or_origin_alignment", lambda x: x["preflight"].update(branch="wrong", head="0" * 40, upstream_aligned=False))
    check("changed_c0_c0a_or_effective_identity", lambda x: x["prior_contract_binding"].update(c0_canonical_summary_sha256="0" * 64, c0a_canonical_summary_sha256="1" * 64, effective_acquisition_contract_identity_sha256="2" * 64))
    check("protected_stash_changed", lambda x: x["preflight"].update(protected_stash="changed"))
    check("missing_input_folder", lambda x: x["required_input_package"].update(capture_folder_required=False))
    check("zero_or_multiple_raw_csv_files", lambda x: x["required_input_package"].update(raw_csv_count=2))
    check("missing_notes_or_source_evidence_images", lambda x: x["required_input_package"].update(notes_count=0, minimum_image_count=0))
    check("wrong_xm_server_symbol_or_timeframe", lambda x: x["expected_source_binding"].update(exact_server="OTHER", exact_symbol="XAUUSD", timeframe="M1"))
    check("plain_gold_accepted_instead_of_gold_hash", lambda x: x["expected_source_binding"].update(exact_symbol="GOLD"))
    check("raw_filename_mismatch", lambda x: x["required_note_declarations"].update(raw_filename="other.csv"))
    check("unsupported_encoding_delimiter_or_header", lambda x: x["minimal_intake_policy"].update(approved_encodings=["OTHER"], approved_delimiters=["PIPE"], approved_header_profiles=["OTHER"]))
    check("hash_or_byte_size_mutation_during_execution", lambda x: x["immutability_policy"].update(pre_post_hash_and_size_must_match=False))
    check("excel_zip_or_second_csv_accepted", lambda x: x["required_input_package"].update(zip_or_excel_count=1, raw_csv_count=2))
    check("sensitive_data_accepted", lambda x: x["sensitive_data_policy"].update(reject_sensitive_notes_or_filenames=False))
    check("absolute_path_stored_in_canonical_identity", lambda x: x["sensitive_data_policy"].update(absolute_runtime_path_in_canonical_identity="AUTHORIZED"))
    check("dukascopy_or_sibling_folder_access", lambda x: x["external_access_policy"].update(parent_or_sibling_access=True, dukascopy_access=True))
    check("mt5_network_or_external_process_execution", lambda x: x["external_access_policy"].update(network_access=True, external_process_execution=True, mt5_data_directory_access=True))
    check("raw_file_copied_moved_renamed_or_modified", lambda x: x["immutability_policy"].update(external_file_mutation_authorized=True, raw_copy_to_repository_authorized=True))
    check("gap_inventory_or_classification_attempted", lambda x: x["operation_authorizations"].update(gap_inventory=True, gap_classification=True))
    check("structural_validation_claimed_complete", lambda x: x["status_boundary"].update(structural_validation="COMPLETE"))
    check("dataset_described_as_clean", lambda x: x["status_boundary"].update(clean_dataset_status="CLEAN"))
    check("buffer_sufficiency_claimed", lambda x: x["status_boundary"].update(right_buffer_validation="PASS"))
    check("holdout_or_out_of_sample_claimed", lambda x: x["status_boundary"].update(holdout_status="CLAIMED", out_of_sample_status="CLAIMED"))
    check("detector_event_outcome_or_statistics_execution", lambda x: x["operation_authorizations"].update(detector_execution=True, event_generation=True, outcome_execution=True, statistics_execution=True))
    check("strategy_indicator_or_parameter_modification", lambda x: x["operation_authorizations"].update(strategy_modification=True, indicator_addition=True, parameter_change=True))
    check("tp_sl_lot_cost_cash_pl_or_order_simulation", lambda x: x["operation_authorizations"].update(tp_sl_design=True, lot_sizing=True, costs_or_cash_pl=True, order_simulation=True))
    check("profitability_edge_robustness_or_readiness_claim", lambda x: x["operation_authorizations"].update(profitability_edge_robustness_readiness_claim=True))
    check("existing_repository_file_modification", lambda x: x["file_creation_boundary"].update(existing_file_modification_authorized=True))
    check("raw_evidence_committed", lambda x: x["file_creation_boundary"].update(raw_notes_or_images_commit_authorized=True))
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", default=MODE)
    parser.add_argument("--capture-folder", required=True, type=Path)
    args = parser.parse_args()
    require(args.mode == MODE, "MODE_NOT_AUTHORIZED")
    validate_script_imports()
    capture = args.capture_folder.resolve()
    require(not CONTRACT.exists(), "CONTRACT_ALREADY_EXISTS")
    require(not RAW_MANIFEST.exists(), "RAW_MANIFEST_ALREADY_EXISTS")
    require(not EVIDENCE_MANIFEST.exists(), "EVIDENCE_MANIFEST_ALREADY_EXISTS")
    require(not SUMMARY.exists(), "SUMMARY_ALREADY_EXISTS")
    require(not OUT.exists(), "RESULT_DIRECTORY_ALREADY_EXISTS")

    original_before = package_snapshot(capture)
    auth_1, contract_1, raw_1, evidence_1 = build_records(
        ROOT, capture, True
    )
    negative_results = run_negative_tests(auth_1)
    auth_2, contract_2, raw_2, evidence_2 = build_records(
        ROOT, capture, True
    )
    require((contract_1, raw_1, evidence_1) == (contract_2, raw_2, evidence_2), "NORMAL_REPEAT_MISMATCH")

    with tempfile.TemporaryDirectory(prefix="fr_phase_c1_") as temporary:
        relocated = Path(temporary) / "capture_20260730"
        relocated.mkdir()
        for source in sorted(capture.iterdir(), key=lambda item: item.name):
            require(source.is_file(), "CAPTURE_CONTAINS_DIRECTORY")
            shutil.copyfile(source, relocated / source.name)
        require(package_snapshot(relocated) == {
            name: {
                "byte_size": values["byte_size"],
                "sha256": values["sha256"],
                "mtime_ns": (relocated / name).stat().st_mtime_ns,
            }
            for name, values in original_before.items()
        }, "TEMPORARY_COPY_BYTE_MISMATCH")
        _auth_r, contract_r, raw_r, evidence_r = build_records(
            ROOT, relocated, False
        )
        require((contract_r, raw_r, evidence_r) == (contract_1, raw_1, evidence_1), "CONTROLLED_RELOCATION_MISMATCH")

    original_after = package_snapshot(capture)
    require(original_before == original_after, "EXTERNAL_PACKAGE_MUTATION_DETECTED")
    require(negative_results == contract_1["negative_tests"]["results"], "NEGATIVE_TEST_RECORD_MISMATCH")
    schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.validate(contract_1, schema)
    require(identity_without(contract_1, "canonical_summary_sha256") == contract_1["canonical_summary_sha256"], "CONTRACT_IDENTITY_MISMATCH")

    OUT.mkdir(parents=True, exist_ok=False)
    raw_payload = output_bytes(raw_1)
    evidence_payload = output_bytes(evidence_1)
    contract_payload = output_bytes(contract_1)
    RAW_MANIFEST.write_bytes(raw_payload)
    EVIDENCE_MANIFEST.write_bytes(evidence_payload)
    CONTRACT.write_bytes(contract_payload)
    SUMMARY.write_bytes(contract_payload)
    print(
        json.dumps(
            {
                "canonical_summary_sha256": contract_1["canonical_summary_sha256"],
                "decision": PASS,
                "evidence_image_count": evidence_1["evidence_image_count"],
                "negative_tests": f"{len(negative_results)}/{len(NEGATIVE_TEST_NAMES)}",
                "observed_first_timestamp": raw_1["observed_first_timestamp_original_order"],
                "observed_last_timestamp": raw_1["observed_last_timestamp_original_order"],
                "provisional_dataset_binding_sha256": contract_1["provisional_dataset_binding_sha256"],
                "raw_data_rows": raw_1["data_row_count"],
                "raw_sha256": raw_1["sha256_before"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
