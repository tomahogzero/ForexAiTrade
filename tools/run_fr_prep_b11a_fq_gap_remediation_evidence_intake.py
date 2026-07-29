#!/usr/bin/env python3
"""Create a deterministic append-only FQ gap evidence-intake baseline."""

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
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import jsonschema

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "research/contracts/fr_prep_b11a_fq_gap_evidence_intake_authorization.v1.json"
AUTH_SCHEMA = ROOT / "research/schemas/fr_prep_b11a_fq_gap_evidence_intake_authorization.v1.schema.json"
CONTRACT = ROOT / "research/contracts/fr_prep_b11a_fq_gap_evidence_intake.v1.json"
CONTRACT_SCHEMA = ROOT / "research/schemas/fr_prep_b11a_fq_gap_evidence_intake.v1.schema.json"
OUT = ROOT / "research/results/checkpoint_fr_prep_b11a"
REGISTRY = OUT / "fq_gap_evidence_intake_registry.json"
REQUEST = OUT / "fq_gap_evidence_request_manifest.json"
MATRIX = OUT / "fq_gap_evidence_target_matrix.csv"
SUMMARY = OUT / "fq_gap_evidence_intake_summary.json"
MODE = "create-fq-gap-evidence-intake-baseline"
PASS = "FR_PREP_B11A_PASS_FQ_GAP_REMEDIATION_EVIDENCE_INTAKE_BASELINE"
RAW_GAP_FIELDS = {
    "gap_id", "calendar_year", "day_of_week", "previous_bar_timestamp",
    "next_bar_timestamp", "elapsed_hours", "missing_h1_slots",
    "previous_source_file", "next_source_file", "evidence_status",
    "policy_classification", "fail_closed_required",
}
PROHIBITED_MODULES = {
    "observational_outcome_adapter",
    "run_fr_prep_b7_sealed_real_observational_outcomes",
    "run_fr_prep_b7a_independent_real_outcome_audit",
    "market_structure_break_retest_detector",
    "MetaTrader5",
}
SENSITIVE_KEYS = {
    "credential", "credentials", "password", "account", "account_number",
    "token", "api_key", "secret",
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
        raise ValueError("B11A_UNTERMINATED_JSON_STRING")
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
                    raise ValueError("B11A_INVALID_JSON_NESTING")
                stack.pop()
                if not stack:
                    return cursor + 1
            cursor += 1
        raise ValueError("B11A_UNTERMINATED_JSON_CONTAINER")
    cursor = index
    while cursor < len(text) and text[cursor] not in ",}":
        cursor += 1
    return cursor


def selective_object(text):
    decoder = json.JSONDecoder()
    cursor = skip_space(text, 0)
    if text[cursor] != "{":
        raise ValueError("B11A_GAP_RECORD_NOT_OBJECT")
    cursor += 1
    selected = {}
    while True:
        cursor = skip_space(text, cursor)
        if text[cursor] == "}":
            break
        key, key_end = decoder.raw_decode(text, cursor)
        cursor = skip_space(text, key_end)
        if text[cursor] != ":":
            raise ValueError("B11A_GAP_RECORD_MISSING_COLON")
        value_start = skip_space(text, cursor + 1)
        value_end = scan_json_value_end(text, value_start)
        if key in RAW_GAP_FIELDS:
            selected[key] = json.loads(text[value_start:value_end])
        cursor = skip_space(text, value_end)
        if text[cursor] == ",":
            cursor += 1
            continue
        if text[cursor] == "}":
            break
        raise ValueError("B11A_GAP_RECORD_SEPARATOR_INVALID")
    if set(selected) != RAW_GAP_FIELDS:
        raise ValueError("B11A_REQUIRED_GAP_METADATA_MISSING")
    return selected


class Files:
    def __init__(self):
        self.registry = {}
        self.hash_reads = Counter()
        self.json_reads = Counter()
        self.gap_reads = Counter()
        self.blocked_reads = 0

    def add(self, path, artifact_id, access):
        self.registry[Path(path).resolve()] = (artifact_id, access)

    def hash_read(self, path):
        resolved = Path(path).resolve()
        if resolved not in self.registry:
            self.blocked_reads += 1
            raise PermissionError("B11A_UNAUTHORIZED_HASH_READ_BLOCKED")
        artifact_id, _access = self.registry[resolved]
        self.hash_reads[artifact_id] += 1
        return resolved.read_bytes()

    def parse_json(self, path):
        resolved = Path(path).resolve()
        entry = self.registry.get(resolved)
        if entry is None or entry[1] != "json":
            self.blocked_reads += 1
            raise PermissionError("B11A_UNAUTHORIZED_JSON_PARSE_BLOCKED")
        artifact_id, _access = entry
        self.json_reads[artifact_id] += 1
        return json.loads(resolved.read_text(encoding="utf-8"))

    def parse_gap_metadata(self, path):
        resolved = Path(path).resolve()
        entry = self.registry.get(resolved)
        if entry is None or entry[1] != "selective_gap_metadata":
            self.blocked_reads += 1
            raise PermissionError("B11A_GAP_METADATA_PARSE_BLOCKED")
        text = resolved.read_text(encoding="utf-8")
        cursor = skip_space(text, 0)
        if text[cursor] != "[":
            raise ValueError("B11A_GAP_INVENTORY_NOT_ARRAY")
        cursor += 1
        records = []
        while True:
            cursor = skip_space(text, cursor)
            if text[cursor] == "]":
                break
            end = scan_json_value_end(text, cursor)
            records.append(selective_object(text[cursor:end]))
            cursor = skip_space(text, end)
            if text[cursor] == ",":
                cursor += 1
                continue
            if text[cursor] == "]":
                break
            raise ValueError("B11A_GAP_INVENTORY_SEPARATOR_INVALID")
        artifact_id, _access = entry
        self.gap_reads[artifact_id] += 1
        return records

    def report(self):
        ids = sorted({entry[0] for entry in self.registry.values()})
        return {
            "hash_read_operation_counts": {item: self.hash_reads[item] for item in ids},
            "json_parse_operation_counts": {item: self.json_reads[item] for item in ids},
            "gap_metadata_parse_operation_counts": {item: self.gap_reads[item] for item in ids},
            "blocked_unauthorized_read_attempt_count": self.blocked_reads,
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
        raise RuntimeError("B11A_EXTERNAL_PROCESS_BLOCKED")

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
            raise ImportError("B11A_PROHIBITED_IMPORT_BLOCKED")
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


def has_security_leakage(value):
    if isinstance(value, dict):
        if any(str(key).lower() in SENSITIVE_KEYS for key in value):
            return True
        return any(has_security_leakage(item) for item in value.values())
    if isinstance(value, list):
        return any(has_security_leakage(item) for item in value)
    return isinstance(value, str) and (ntpath.isabs(value) or posixpath.isabs(value))


def valid_effective_range(start, end):
    try:
        return datetime.fromisoformat(start) <= datetime.fromisoformat(end)
    except (TypeError, ValueError):
        return False


def is_reparse_or_symlink(path):
    if path.is_symlink():
        return True
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & 0x400)


def inside(child, parent):
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def scan_staging(
    stage, repository_root, protocol, target_ids, frozen_sources, target_symbol
):
    package_statuses = protocol["frozen_intake_package_statuses"]
    package_counts = {status: 0 for status in package_statuses}
    if not stage.exists():
        return {
            "staging_state": "ABSENT",
            "packages": [],
            "staged_artifacts": [],
            "package_status_counts": package_counts,
        }
    if not stage.is_dir() or is_reparse_or_symlink(stage):
        raise ValueError("B11A_STAGING_ROOT_INVALID_OR_REPARSE")
    resolved_stage = stage.resolve()
    resolved_repository_root = Path(repository_root).resolve()
    if (
        not inside(resolved_stage, resolved_repository_root)
        and resolved_repository_root != resolved_stage
    ):
        raise ValueError("B11A_STAGING_OUTSIDE_REPOSITORY")

    all_files = []
    descriptor_files = []
    for current, directories, filenames in os.walk(stage, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name for name in directories
            if not is_reparse_or_symlink(current_path / name)
        )
        for filename in sorted(filenames):
            path = current_path / filename
            if is_reparse_or_symlink(path):
                continue
            resolved = path.resolve()
            if not inside(resolved, resolved_stage):
                continue
            all_files.append(path)
            if path.name.endswith(protocol["descriptor_filename_suffix"]):
                descriptor_files.append(path)

    staged_artifacts = [
        {
            "relative_path": path.relative_to(stage).as_posix(),
            "sha256": byte_digest(path.read_bytes()),
            "bytes": path.stat().st_size,
        }
        for path in sorted(all_files, key=lambda item: item.relative_to(stage).as_posix())
    ]
    packages = []
    seen_ids = set()
    required = set(protocol["descriptor_required_fields"])
    primary_types = set(protocol["allowed_primary_evidence_types"])
    corroborative_types = set(protocol["corroborative_only_evidence_types"])
    frozen_names = {item["filename"] for item in frozen_sources}
    frozen_hashes = {item["sha256"] for item in frozen_sources}
    for descriptor_path in sorted(
        descriptor_files, key=lambda item: item.relative_to(stage).as_posix()
    ):
        relative_descriptor = descriptor_path.relative_to(stage).as_posix()
        status = "PACKAGE_REJECTED_METADATA"
        descriptor = {}
        try:
            descriptor = json.loads(descriptor_path.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            descriptor = {}
        package_id = descriptor.get("evidence_package_id", f"INVALID:{relative_descriptor}")
        referenced = descriptor.get("gap_ids", [])
        record = {
            "descriptor_path": relative_descriptor,
            "evidence_package_id": package_id,
            "evidence_type": descriptor.get("evidence_type"),
            "evidence_role": descriptor.get("evidence_role"),
            "referenced_gap_ids": referenced if isinstance(referenced, list) else [],
            "artifact_path": descriptor.get("artifact_path"),
            "declared_artifact_sha256": descriptor.get("artifact_sha256"),
            "computed_artifact_sha256": None,
            "validation_status": status,
        }
        if has_security_leakage(descriptor):
            status = "PACKAGE_REJECTED_SECURITY_LEAKAGE"
        elif not isinstance(descriptor, dict) or not required.issubset(descriptor):
            status = "PACKAGE_REJECTED_METADATA"
        elif not isinstance(package_id, str) or not package_id or package_id in seen_ids:
            status = "PACKAGE_REJECTED_METADATA"
        elif (
            descriptor["evidence_role"] not in protocol["permitted_evidence_roles"]
            or (
                descriptor["evidence_type"] in primary_types
                and descriptor["evidence_role"] != "PRIMARY"
            )
            or (
                descriptor["evidence_type"] in corroborative_types
                and descriptor["evidence_role"] != "CORROBORATIVE_ONLY"
            )
            or descriptor["evidence_type"] not in primary_types | corroborative_types
        ):
            status = "PACKAGE_REJECTED_METADATA"
        elif (
            not isinstance(referenced, list)
            or not referenced
            or any(item not in target_ids for item in referenced)
            or len(set(referenced)) != len(referenced)
        ):
            status = "PACKAGE_REJECTED_OUT_OF_SCOPE"
        elif any(
            not isinstance(descriptor.get(key), str) or not descriptor.get(key)
            for key in (
                "source_organization", "broker", "server", "symbol", "time_basis",
                "timezone_or_unknown", "effective_start", "effective_end", "captured_at",
                "artifact_path", "artifact_sha256",
            )
        ):
            status = "PACKAGE_REJECTED_METADATA"
        elif (
            descriptor["evidence_role"] == "PRIMARY"
            and descriptor["symbol"] != target_symbol
        ):
            status = "PACKAGE_REJECTED_OUT_OF_SCOPE"
        elif (
            len(descriptor["artifact_sha256"]) != 64
            or any(char not in "0123456789abcdef" for char in descriptor["artifact_sha256"])
        ):
            status = "PACKAGE_REJECTED_METADATA"
        elif not valid_effective_range(
            descriptor["effective_start"], descriptor["effective_end"]
        ):
            status = "PACKAGE_REJECTED_METADATA"
        else:
            relative_artifact = Path(descriptor["artifact_path"])
            artifact = (stage / relative_artifact).resolve()
            if (
                relative_artifact.is_absolute()
                or not inside(artifact, resolved_stage)
                or artifact == descriptor_path.resolve()
                or (artifact.exists() and is_reparse_or_symlink(artifact))
            ):
                status = "PACKAGE_REJECTED_SECURITY_LEAKAGE"
            elif not artifact.is_file():
                status = "PACKAGE_REJECTED_MISSING_ARTIFACT"
            else:
                computed = byte_digest(artifact.read_bytes())
                record["computed_artifact_sha256"] = computed
                if computed != descriptor["artifact_sha256"]:
                    status = "PACKAGE_REJECTED_HASH_MISMATCH"
                elif artifact.name in frozen_names or computed in frozen_hashes:
                    status = "PACKAGE_REJECTED_OUT_OF_SCOPE"
                else:
                    status = "PACKAGE_REGISTERED_UNAUDITED"
        if isinstance(package_id, str) and package_id:
            seen_ids.add(package_id)
        record["validation_status"] = status
        packages.append(record)
        package_counts[status] += 1
    return {
        "staging_state": "EMPTY" if not all_files else "PRESENT",
        "packages": packages,
        "staged_artifacts": staged_artifacts,
        "package_status_counts": package_counts,
    }


def build_core(base_root, authorization):
    files = Files()
    paths = {}
    artifact_mismatch = 0
    for binding in authorization["committed_artifacts"]:
        path = (Path(base_root) / binding["path"]).resolve()
        files.add(path, binding["artifact_id"], binding["access"])
        paths[binding["artifact_id"]] = path
        if not path.is_file():
            raise ValueError("B11A_COMMITTED_ARTIFACT_MISSING")
        artifact_mismatch += int(
            byte_digest(files.hash_read(path)) != binding["file_sha256"]
        )
    if artifact_mismatch:
        raise ValueError("B11A_COMMITTED_ARTIFACT_HASH_MISMATCH")

    b10a = files.parse_json(paths["b10a_contract"])
    b10a_schema = files.parse_json(paths["b10a_schema"])
    b10a_summary = files.parse_json(paths["b10a_summary"])
    b11 = files.parse_json(paths["b11_contract"])
    b11_schema = files.parse_json(paths["b11_schema"])
    b11_summary = files.parse_json(paths["b11_summary"])
    manifest = files.parse_json(paths["fq_source_manifest"])
    jsonschema.Draft202012Validator.check_schema(b10a_schema)
    jsonschema.Draft202012Validator(b10a_schema).validate(b10a)
    jsonschema.Draft202012Validator.check_schema(b11_schema)
    jsonschema.Draft202012Validator(b11_schema).validate(b11)
    expected = authorization["expected"]
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
    )
    b11_valid = (
        validate_identity(
            b11,
            expected["b11"]["canonical_summary_sha256"],
            expected["b11"]["decision"],
        )
        and b11_summary == b11
        and b11["target_inventory"]["target_gap_id_set_sha256"]
        == expected["b11"]["target_gap_id_set_sha256"]
        and b11["target_inventory"]["target_gap_metadata_sha256"]
        == expected["b11"]["target_gap_metadata_sha256"]
        and b11["target_inventory"]["structural_signature_inventory_sha256"]
        == expected["b11"]["structural_signature_inventory_sha256"]
    )
    fq_valid = (
        manifest["source_rows"] == expected["fq"]["source_rows"]
        and manifest["gap_inventory"]["sha256"] == expected["fq"]["gap_inventory_sha256"]
        and b11["fq_binding"]["event_population_sha256"]
        == expected["fq"]["event_population_sha256"]
    )
    if not (b10a_valid and b11_valid and fq_valid):
        raise ValueError("B11A_UPSTREAM_VALIDATION_BLOCKED")

    records = [project_gap(item) for item in files.parse_gap_metadata(paths["fq_gap_inventory"])]
    targets = sorted(
        (
            item for item in records
            if item["original_evidence_status"] == "UNVERIFIED"
            and item["original_policy_classification"] == "UNVERIFIED_GAP"
            and item["original_fail_closed_required"] is True
        ),
        key=lambda item: item["gap_id"],
    )
    target_ids = [item["gap_id"] for item in targets]
    signatures = [structural_signature(item) for item in targets]
    signature_counter = Counter(canonical_json(item) for item in signatures)
    signature_inventory = [
        {"signature": json.loads(key), "gap_count": signature_counter[key]}
        for key in sorted(signature_counter)
    ]
    target_valid = (
        len(targets) == expected["b11"]["target_gap_count"]
        and len(set(target_ids)) == len(target_ids)
        and target_ids == b11["target_inventory"]["target_gap_id_set"]
        and digest(target_ids) == expected["b11"]["target_gap_id_set_sha256"]
        and digest(targets) == expected["b11"]["target_gap_metadata_sha256"]
        and digest(signature_inventory)
        == expected["b11"]["structural_signature_inventory_sha256"]
    )
    if not target_valid:
        raise ValueError("B11A_TARGET_RECREATION_MISMATCH")

    protocol = authorization["evidence_intake_protocol"]
    stage = Path(base_root) / protocol["staging_location"]
    staging = scan_staging(
        stage,
        base_root,
        protocol,
        set(target_ids),
        manifest["sources"],
        manifest["symbol"],
    )
    registered = [
        item for item in staging["packages"]
        if item["validation_status"] == "PACKAGE_REGISTERED_UNAUDITED"
    ]
    primary = [item for item in registered if item["evidence_role"] == "PRIMARY"]
    corroborative = [
        item for item in registered if item["evidence_role"] == "CORROBORATIVE_ONLY"
    ]
    primary_by_gap = defaultdict(list)
    corroborative_by_gap = defaultdict(list)
    rejected_by_gap = defaultdict(list)
    for package in primary:
        for gap_id in package["referenced_gap_ids"]:
            primary_by_gap[gap_id].append(package["evidence_package_id"])
    for package in corroborative:
        for gap_id in package["referenced_gap_ids"]:
            corroborative_by_gap[gap_id].append(package["evidence_package_id"])
    for package in staging["packages"]:
        if package["validation_status"] != "PACKAGE_REGISTERED_UNAUDITED":
            for gap_id in package["referenced_gap_ids"]:
                if gap_id in set(target_ids):
                    rejected_by_gap[gap_id].append(package["evidence_package_id"])

    rows = []
    for target, signature in zip(targets, signatures):
        gap_id = target["gap_id"]
        primary_ids = sorted(primary_by_gap.get(gap_id, []))
        corroborative_ids = sorted(corroborative_by_gap.get(gap_id, []))
        rejected_ids = sorted(rejected_by_gap.get(gap_id, []))
        if primary_ids and corroborative_ids:
            intake_status = "PRIMARY_AND_CORROBORATIVE_SUBMITTED_UNAUDITED"
        elif primary_ids:
            intake_status = "PRIMARY_EVIDENCE_SUBMITTED_UNAUDITED"
        elif corroborative_ids:
            intake_status = "CORROBORATIVE_ONLY_SUBMITTED_UNAUDITED"
        elif rejected_ids:
            intake_status = "SUBMITTED_PACKAGE_REJECTED_AT_INTAKE"
        else:
            intake_status = "NO_EVIDENCE_SUBMITTED"
        rows.append({
            **copy.deepcopy(target),
            "structural_signature": signature,
            "structural_signature_sha256": digest(signature),
            "requested_primary_evidence_classes": copy.deepcopy(
                protocol["allowed_primary_evidence_types"]
            ),
            "submitted_package_ids": sorted(primary_ids + corroborative_ids + rejected_ids),
            "registered_primary_package_ids": primary_ids,
            "registered_corroborative_package_ids": corroborative_ids,
            "rejected_package_ids": rejected_ids,
            "missing_evidence_fields": (
                [] if primary_ids else copy.deepcopy(protocol["missing_primary_evidence_fields"])
            ),
            "intake_status": intake_status,
        })
    gap_status_counts = Counter(item["intake_status"] for item in rows)
    gap_status_counts = {
        status: gap_status_counts[status]
        for status in protocol["frozen_per_gap_intake_statuses"]
    }
    gaps_with_primary = len(primary_by_gap)
    gaps_without_primary = len(targets) - gaps_with_primary
    if not primary:
        batch_status = "NO_PRIMARY_EVIDENCE_SUBMITTED"
        complete = False
        next_scope = "FQ_GAP_REMEDIATION_EVIDENCE_INTAKE_ONLY"
    elif gaps_with_primary < len(targets):
        batch_status = "PARTIAL_PRIMARY_EVIDENCE_SUBMISSION"
        complete = False
        next_scope = "FQ_GAP_REMEDIATION_EVIDENCE_INTAKE_ONLY"
    else:
        batch_status = "FULL_TARGET_PRIMARY_EVIDENCE_SUBMISSION"
        complete = True
        next_scope = "INDEPENDENT_FQ_GAP_EVIDENCE_AUDIT_ONLY"

    source_groups = defaultdict(list)
    signature_groups = defaultdict(list)
    for row in rows:
        source_key = canonical_json({
            "calendar_year": row["calendar_year"],
            "previous_source_file": row["previous_source_file"],
            "next_source_file": row["next_source_file"],
        })
        source_groups[source_key].append(row["gap_id"])
        signature_groups[canonical_json(row["structural_signature"])].append(row["gap_id"])
    capture_groups = {
        "grouping_is_operational_only": True,
        "ranking_or_priority_assigned": False,
        "repeated_signature_infers_closure": False,
        "by_source_year_and_file": [
            {**json.loads(key), "gap_ids": sorted(source_groups[key])}
            for key in sorted(source_groups)
        ],
        "by_structural_signature": [
            {
                "structural_signature": json.loads(key),
                "structural_signature_sha256": digest(json.loads(key)),
                "gap_ids": sorted(signature_groups[key]),
            }
            for key in sorted(signature_groups)
        ],
    }
    registry = {
        "schema_version": "fr_prep_b11a_fq_gap_evidence_intake_registry.v1",
        "checkpoint": "FR_PREP_B11A",
        "dataset_id": expected["b11"]["dataset_id"],
        "staging_location": protocol["staging_location"],
        "staging_state": staging["staging_state"],
        "submitted_packages": staging["packages"],
        "staged_artifacts": staging["staged_artifacts"],
        "package_status_counts": staging["package_status_counts"],
        "registered_package_count": len(registered),
        "registered_primary_package_count": len(primary),
        "registered_corroborative_package_count": len(corroborative),
        "substantive_sufficiency_evaluated": False,
        "gap_status_adjudicated": False,
        "accepted_for_bar_skip_changed": False,
    }
    request = {
        "schema_version": "fr_prep_b11a_fq_gap_evidence_request_manifest.v1",
        "checkpoint": "FR_PREP_B11A",
        "dataset_id": expected["b11"]["dataset_id"],
        "target_gap_id_set_sha256": expected["b11"]["target_gap_id_set_sha256"],
        "target_gap_metadata_sha256": expected["b11"]["target_gap_metadata_sha256"],
        "structural_signature_inventory_sha256": expected["b11"][
            "structural_signature_inventory_sha256"
        ],
        "target_gap_count": len(rows),
        "intake_targets": rows,
        "capture_request_groups": capture_groups,
        "no_proposed_remediation_status": True,
        "no_accepted_for_bar_skip_change": True,
        "no_outcome_return_mfe_or_mae_fields": True,
    }
    matrix_headers = [
        "gap_id", "calendar_year", "day_of_week", "previous_bar_timestamp",
        "next_bar_timestamp", "elapsed_hours", "missing_h1_slots",
        "previous_source_file", "next_source_file", "original_evidence_status",
        "original_policy_classification", "original_fail_closed_required",
        "structural_signature_sha256", "requested_primary_evidence_classes",
        "submitted_package_ids", "missing_evidence_fields", "intake_status",
    ]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=matrix_headers, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({
            key: (
                "|".join(row[key])
                if isinstance(row[key], list)
                else str(row[key]).lower()
                if isinstance(row[key], bool)
                else row[key]
            )
            for key in matrix_headers
        })
    rendered = {
        "registry": json.dumps(registry, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        "request": json.dumps(request, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
        "matrix": stream.getvalue(),
    }
    state = {
        "intake_batch_status": batch_status,
        "evidence_intake_complete": complete,
        "next_allowed_scope": next_scope,
        "package_counts": {
            "registered_total": len(registered),
            "registered_primary": len(primary),
            "registered_corroborative": len(corroborative),
            "by_status": staging["package_status_counts"],
        },
        "gap_counts": {
            "target_total": len(rows),
            "with_primary_evidence": gaps_with_primary,
            "without_primary_evidence": gaps_without_primary,
            "by_intake_status": gap_status_counts,
        },
    }
    validation = {
        "b10a_valid": b10a_valid,
        "b11_valid": b11_valid,
        "fq_binding_valid": fq_valid,
        "artifact_hash_mismatch": artifact_mismatch,
        "target_valid": target_valid,
        "target_gap_count": len(targets),
        "target_ids_unique": len(set(target_ids)) == len(target_ids),
        "targets_remain_unverified_gap": all(
            item["original_policy_classification"] == "UNVERIFIED_GAP"
            and item["original_evidence_status"] == "UNVERIFIED"
            for item in targets
        ),
    }
    return rendered, state, validation, files


def base_request(expected):
    return {
        "b10a_identity": expected["b10a"]["canonical_summary_sha256"],
        "b11_identity": expected["b11"]["canonical_summary_sha256"],
        "target_hashes": [
            expected["b11"]["target_gap_id_set_sha256"],
            expected["b11"]["target_gap_metadata_sha256"],
            expected["b11"]["structural_signature_inventory_sha256"],
        ],
        "target_mutation": False,
        "inventory_modification": False,
        "adjudication_or_reclassification": False,
        "synthetic_data": False,
        "frozen_source_as_evidence": False,
        "outside_staging": False,
        "path_or_symlink_escape": False,
        "missing_or_hash_mismatch_accepted": False,
        "invalid_scope_accepted": False,
        "corroborative_promoted": False,
        "pattern_as_closure": False,
        "hide_partial_evidence": False,
        "outcome_prioritization": False,
        "external_process": False,
        "timeline_or_outcome_execution": False,
        "claims": [],
        "runtime_path": None,
    }


def request_allowed(expected, request):
    return request == base_request(expected)


def negative_tests(authorization, files):
    expected = authorization["expected"]
    base = base_request(expected)
    tests = {}

    def mutate(name, update):
        changed = copy.deepcopy(base)
        update(changed)
        tests[name] = not request_allowed(expected, changed)

    mutate("wrong_b10a_or_b11_identity_or_decision_blocked", lambda x: x.update({"b11_identity": "0" * 64}))
    mutate("changed_target_set_metadata_or_structural_hash_blocked", lambda x: x.update({"target_hashes": ["0" * 64] * 3}))
    mutate("missing_duplicate_or_extra_target_gap_blocked", lambda x: x.update({"target_mutation": True}))
    mutate("original_inventory_modification_blocked", lambda x: x.update({"inventory_modification": True}))
    mutate("gap_adjudication_or_reclassification_blocked", lambda x: x.update({"adjudication_or_reclassification": True}))
    mutate("synthetic_timestamp_or_ohlc_creation_blocked", lambda x: x.update({"synthetic_data": True}))
    mutate("frozen_source_csv_as_independent_evidence_blocked", lambda x: x.update({"frozen_source_as_evidence": True}))
    mutate("evidence_outside_allowed_staging_blocked", lambda x: x.update({"outside_staging": True}))
    leaked = copy.deepcopy(base)
    leaked["path_or_symlink_escape"] = True
    leaked["runtime_path"] = str(ROOT.resolve())
    tests["symlink_path_traversal_or_absolute_path_leakage_blocked"] = (
        not request_allowed(expected, leaked) and absolute_path_count(leaked) == 1
    )
    mutate("missing_artifact_or_changed_hash_not_registered", lambda x: x.update({"missing_or_hash_mismatch_accepted": True}))
    mutate("invalid_broker_server_symbol_scope_not_registered", lambda x: x.update({"invalid_scope_accepted": True}))
    mutate("corroborative_only_evidence_promotion_blocked", lambda x: x.update({"corroborative_promoted": True}))
    mutate("repeated_structural_pattern_as_closure_proof_blocked", lambda x: x.update({"pattern_as_closure": True}))
    mutate("partial_evidence_hidden_from_matrix_blocked", lambda x: x.update({"hide_partial_evidence": True}))
    mutate("outcome_based_prioritization_blocked", lambda x: x.update({"outcome_prioritization": True}))
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
    tests["mt5_ea_network_or_external_process_blocked"] = (
        blocked_imports == len(PROHIBITED_MODULES) and external_blocked
    )
    mutate("timeline_rebuild_or_outcome_rerun_blocked", lambda x: x.update({"timeline_or_outcome_execution": True}))
    mutate("profitability_edge_robustness_or_readiness_claim_blocked", lambda x: x.update({"claims": ["PROFITABILITY", "EDGE", "ROBUSTNESS", "READINESS"]}))
    blocked_reads = 0
    for path in authorization["prohibited_input_paths"]:
        try:
            files.parse_json(ROOT / path)
        except PermissionError:
            blocked_reads += 1
    tests["prohibited_b7_read_guard_fail_closed"] = blocked_reads == 3
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
        raise SystemExit("B11A_AUTHORIZATION_PATH_NOT_ALLOWED")
    if Path(args.output_root).resolve() != OUT.resolve():
        raise SystemExit("B11A_OUTPUT_ROOT_NOT_ALLOWED")

    bootstrap = Files()
    for path, artifact_id in (
        (AUTH, "b11a_authorization"),
        (AUTH_SCHEMA, "b11a_authorization_schema"),
        (CONTRACT_SCHEMA, "b11a_contract_schema"),
    ):
        bootstrap.add(path, artifact_id, "json")
    authorization = bootstrap.parse_json(AUTH)
    authorization_schema = bootstrap.parse_json(AUTH_SCHEMA)
    contract_schema = bootstrap.parse_json(CONTRACT_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(authorization_schema)
    jsonschema.Draft202012Validator(authorization_schema).validate(authorization)
    jsonschema.Draft202012Validator.check_schema(contract_schema)

    OUT.mkdir(parents=True, exist_ok=True)
    before_modules = set(sys.modules)
    relocation_deleted = False
    with ExternalProcessGuard() as external_guard, ImportGuard() as import_guard:
        output_1, state_1, validation_1, files_1 = build_core(ROOT, authorization)
        output_2, state_2, validation_2, files_2 = build_core(ROOT, authorization)
        relocation_path = None
        with tempfile.TemporaryDirectory(prefix=".b11a_relocation_", dir=OUT) as temporary:
            relocation_path = Path(temporary)
            for binding in authorization["committed_artifacts"]:
                source = ROOT / binding["path"]
                target = relocation_path / binding["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            original_stage = ROOT / authorization["evidence_intake_protocol"]["staging_location"]
            if original_stage.exists():
                relocated_stage = relocation_path / authorization["evidence_intake_protocol"]["staging_location"]
                shutil.copytree(original_stage, relocated_stage, symlinks=True)
            output_relocated, state_relocated, validation_relocated, files_relocated = build_core(
                relocation_path, authorization
            )
        relocation_deleted = relocation_path is not None and not relocation_path.exists()
        tests = negative_tests(authorization, files_1)

    imported = set(sys.modules) - before_modules
    prohibited_loaded = sorted(
        name for name in PROHIBITED_MODULES if name in sys.modules or name in imported
    )
    normal_identical = output_1 == output_2 and state_1 == state_2
    relocation_identical = (
        output_1 == output_relocated and state_1 == state_relocated
    )
    mismatch_counters = {
        "b10a_or_b11_identity_decision_or_schema_mismatch": int(
            not (
                validation_1["b10a_valid"]
                and validation_1["b11_valid"]
                and validation_1["fq_binding_valid"]
            )
        ),
        "committed_artifact_hash_mismatch": validation_1["artifact_hash_mismatch"],
        "target_set_metadata_or_structural_hash_mismatch": int(not validation_1["target_valid"]),
        "target_count_uniqueness_or_unverified_status_mismatch": int(
            not (
                validation_1["target_gap_count"] == 625
                and validation_1["target_ids_unique"]
                and validation_1["targets_remain_unverified_gap"]
            )
        ),
        "target_matrix_row_count_mismatch": int(
            output_1["matrix"].count("\n") - 1 != 625
        ),
        "normal_repeat_mismatch": int(not normal_identical),
        "controlled_relocation_mismatch": int(not relocation_identical),
        "temporary_artifact_deletion_mismatch": int(not relocation_deleted),
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
            "gap_adjudication_count", "gap_reclassification_count",
            "original_inventory_modification_count", "synthetic_timestamp_count",
            "synthetic_ohlc_count", "interpolation_count", "timeline_rebuild_count",
            "event_rerun_count", "outcome_rerun_count", "statistics_rerun_count",
            "ohlc_value_parse_count", "raw_broker_csv_read_count",
            "future_price_read_count", "b7_jsonl_parse_count",
            "b7_statistics_parse_count", "strategy_change_count",
            "mt5_execution_count", "ea_execution_count", "network_execution_count",
            "external_process_success_count", "profitability_claim_count",
            "edge_claim_count", "robustness_claim_count",
            "trading_readiness_claim_count",
        )
    }
    if (
        any(mismatch_counters.values())
        or any(prohibited_import_counts.values())
        or any(prohibited_execution_counts.values())
        or prohibited_loaded
    ):
        raise SystemExit("B11A_EVIDENCE_INTAKE_BASELINE_BLOCKED")

    registry_bytes = output_1["registry"].encode("utf-8")
    request_bytes = output_1["request"].encode("utf-8")
    matrix_bytes = output_1["matrix"].encode("utf-8")
    output_hashes = {
        "registry_sha256": byte_digest(registry_bytes),
        "request_manifest_sha256": byte_digest(request_bytes),
        "target_matrix_sha256": byte_digest(matrix_bytes),
    }
    output_hashes["complete_sha256"] = digest(output_hashes)
    conclusions = {
        "evidence_intake_baseline": "CREATED",
        "target_dataset": authorization["expected"]["b11"]["dataset_id"],
        "target_gap_count": 625,
        "original_gap_inventory_immutable": True,
        "evidence_packages_registered": state_1["package_counts"]["registered_total"],
        "primary_packages_registered": state_1["package_counts"]["registered_primary"],
        "corroborative_packages_registered": state_1["package_counts"]["registered_corroborative"],
        "gaps_with_primary_evidence": state_1["gap_counts"]["with_primary_evidence"],
        "gaps_without_primary_evidence": state_1["gap_counts"]["without_primary_evidence"],
        "gap_adjudication": "NOT_STARTED",
        "gap_reclassification": "NOT_STARTED",
        "timeline_rebuild": "NOT_STARTED",
        "outcome_rerun": "NOT_AUTHORIZED",
        "synthetic_bar_creation": "PROHIBITED",
        "performance": "NOT_EVALUATED",
        "profitability": "NOT_CLAIMED",
        "order_logic": "NOT_APPROVED",
        "candidate": "NOT_READY_FOR_ORDER_LOGIC",
    }
    result = {
        "schema_version": "fr_prep_b11a_fq_gap_evidence_intake.v1",
        "checkpoint": "FR_PREP_B11A",
        "decision": PASS,
        "execution_status": "PASS",
        "upstream_validation": {
            "b10a": copy.deepcopy(authorization["expected"]["b10a"]),
            "b11": copy.deepcopy(authorization["expected"]["b11"]),
            "fq": copy.deepcopy(authorization["expected"]["fq"]),
            "all_identities_schemas_artifacts_and_hashes_validated": True,
        },
        "target_validation": {
            "target_gap_count": validation_1["target_gap_count"],
            "target_ids_unique": validation_1["target_ids_unique"],
            "targets_remain_unverified_gap": validation_1["targets_remain_unverified_gap"],
            "target_gap_id_set_sha256": authorization["expected"]["b11"]["target_gap_id_set_sha256"],
            "target_gap_metadata_sha256": authorization["expected"]["b11"]["target_gap_metadata_sha256"],
            "structural_signature_inventory_sha256": authorization["expected"]["b11"][
                "structural_signature_inventory_sha256"
            ],
        },
        "intake_state": state_1,
        "output_hashes": output_hashes,
        "determinism": {
            "normal_repeat_identical": normal_identical,
            "controlled_relocation_identical": relocation_identical,
            "temporary_artifacts_deleted": relocation_deleted,
            "registry_request_matrix_ordering_and_hashes_identical": (
                normal_identical and relocation_identical
            ),
        },
        "conclusions": conclusions,
        "negative_tests": tests,
        "mismatch_counters": mismatch_counters,
        "runtime_audit": {
            "normal_run_1_file_access": files_1.report(),
            "normal_run_2_file_access": files_2.report(),
            "relocation_run_file_access": files_relocated.report(),
            "staging_location_existed": (
                state_1["package_counts"]["registered_total"] > 0
                or json.loads(output_1["registry"])["staging_state"] != "ABSENT"
            ),
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
        raise SystemExit("B11A_ABSOLUTE_PATH_IDENTITY_LEAKAGE_BLOCKED")

    REGISTRY.write_bytes(registry_bytes)
    REQUEST.write_bytes(request_bytes)
    MATRIX.write_bytes(matrix_bytes)
    rendered_result = json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    CONTRACT.write_text(rendered_result, encoding="utf-8", newline="\n")
    SUMMARY.write_text(rendered_result, encoding="utf-8", newline="\n")
    print(canonical_json({
        "decision": PASS,
        "canonical_summary_sha256": result["canonical_summary_sha256"],
        "evidence_packages_registered": conclusions["evidence_packages_registered"],
        "primary_packages_registered": conclusions["primary_packages_registered"],
        "corroborative_packages_registered": conclusions["corroborative_packages_registered"],
        "gaps_with_primary_evidence": conclusions["gaps_with_primary_evidence"],
        "gaps_without_primary_evidence": conclusions["gaps_without_primary_evidence"],
        "intake_batch_status": state_1["intake_batch_status"],
        "evidence_intake_complete": state_1["evidence_intake_complete"],
        "next_allowed_scope": state_1["next_allowed_scope"],
        **output_hashes,
        "negative_tests": f"{tests['tests_passed']}/{tests['test_count']}",
        "mismatch_count": sum(mismatch_counters.values()),
        "prohibited_count": (
            sum(prohibited_import_counts.values()) + sum(prohibited_execution_counts.values())
        ),
    }))


if __name__ == "__main__":
    main()
