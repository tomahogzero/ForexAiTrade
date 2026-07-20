#!/usr/bin/env python3
"""Generic gap-policy adapter only; never executes detector state instructions."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

MANIFEST_VERSION = "gap_policy_manifest.v1"
ENTRY_VERSION = "gap_policy_entry.v1"
GENERIC_CONTRACT = "GENERIC_GAP_POLICY_V1"
EO_FJ_CONTRACT = "EO_FJ_CSV_V1"
FQ_CONTRACT = "FQ_GAP_INVENTORY_V1"
CONTRACT_TYPES = frozenset({GENERIC_CONTRACT, EO_FJ_CONTRACT, FQ_CONTRACT})

ACCEPTED_CLASSIFICATIONS = {
    GENERIC_CONTRACT: frozenset({"ACCEPTED_CLOSURE"}),
    EO_FJ_CONTRACT: frozenset({
        "ACCEPTED_DAILY_BROKER_SESSION_GAP",
        "ACCEPTED_WEEKEND_MARKET_CLOSURE",
    }),
    FQ_CONTRACT: frozenset({
        "ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE",
        "ACCEPTED_ROUTINE_WEEKEND_CLOSURE",
    }),
}
UNVERIFIED_CLASSIFICATIONS = {
    GENERIC_CONTRACT: frozenset({"UNVERIFIED_GAP"}),
    EO_FJ_CONTRACT: frozenset({"BLOCKED_UNCLASSIFIED_GAP"}),
    FQ_CONTRACT: frozenset({"UNVERIFIED_GAP"}),
}
EO_REQUIRED_COLUMNS = (
    "prev_time", "next_time", "delta_hours", "missing_h1_bars_estimate",
    "prev_weekday", "next_weekday", "classification", "policy_status",
)
SEMANTIC_FIELDS = (
    "accepted_for_trading_bar_skip", "fail_closed_required",
    "reset_active_swing_state", "reset_open_break_candidate",
    "reset_retest_confirmation_state", "prohibit_event_crossing",
    "require_fresh_post_gap_warmup",
)
A2B1_VALIDATION_CODES = frozenset({
    "GAP_POLICY_MANIFEST_MISSING", "GAP_POLICY_MANIFEST_MALFORMED",
    "GAP_POLICY_MANIFEST_REQUIRED_FIELD_MISSING",
    "GAP_POLICY_MANIFEST_SCHEMA_VERSION_UNSUPPORTED",
    "GAP_POLICY_ARTIFACT_MISSING", "GAP_POLICY_ARTIFACT_SHA256_MISMATCH",
    "GAP_POLICY_ENTRY_REQUIRED_FIELD_MISSING",
    "GAP_POLICY_PREVIOUS_TIMESTAMP_INVALID", "GAP_POLICY_NEXT_TIMESTAMP_INVALID",
    "GAP_POLICY_TIMESTAMP_ORDER_INVALID", "GAP_POLICY_CLASSIFICATION_MISSING",
    "GAP_POLICY_CLASSIFICATION_NOT_ALLOWLISTED",
    "FQ_ACCEPTED_CLOSURE_BOOLEANS_CONTRADICTORY",
    "FQ_UNVERIFIED_GAP_BOOLEANS_CONTRADICTORY",
    "GAP_POLICY_RESET_BOOLEANS_INVALID",
    "GAP_POLICY_EVENT_CROSSING_BOOLEAN_INVALID",
    "GAP_POLICY_WARMUP_BOOLEAN_INVALID",
})


class GapPolicyValidationError(ValueError):
    """Gap-policy input violates the frozen adapter contract."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def _require(mapping: dict[str, Any], keys: tuple[str, ...], code: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise GapPolicyValidationError(code)


def _timestamp(value: Any, code: str) -> str:
    if not isinstance(value, str):
        raise GapPolicyValidationError(code)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise GapPolicyValidationError(code) from exc
    if parsed.tzinfo is not None:
        raise GapPolicyValidationError(code)
    return parsed.isoformat()


def _semantics(contract: str, classification: str) -> dict[str, Any]:
    if classification in ACCEPTED_CLASSIFICATIONS[contract]:
        accepted = True
    elif classification in UNVERIFIED_CLASSIFICATIONS[contract]:
        accepted = False
    else:
        raise GapPolicyValidationError("GAP_POLICY_CLASSIFICATION_NOT_ALLOWLISTED")
    return {
        "closure_disposition": "ACCEPTED_CLOSURE" if accepted else "UNVERIFIED_GAP",
        "accepted_for_trading_bar_skip": accepted,
        "fail_closed_required": not accepted,
        "reset_active_swing_state": not accepted,
        "reset_open_break_candidate": not accepted,
        "reset_retest_confirmation_state": not accepted,
        "prohibit_event_crossing": not accepted,
        "require_fresh_post_gap_warmup": not accepted,
    }


def _entry(
    contract: str, gap_id: str, previous: Any, next_: Any,
    classification: str, source_record_identity: str,
) -> dict[str, Any]:
    previous_timestamp = _timestamp(previous, "GAP_POLICY_PREVIOUS_TIMESTAMP_INVALID")
    next_timestamp = _timestamp(next_, "GAP_POLICY_NEXT_TIMESTAMP_INVALID")
    if datetime.fromisoformat(previous_timestamp) >= datetime.fromisoformat(next_timestamp):
        raise GapPolicyValidationError("GAP_POLICY_TIMESTAMP_ORDER_INVALID")
    if not all(isinstance(value, str) and value for value in (gap_id, source_record_identity)):
        raise GapPolicyValidationError("GAP_POLICY_ENTRY_REQUIRED_FIELD_MISSING")
    if not isinstance(classification, str) or not classification:
        raise GapPolicyValidationError("GAP_POLICY_CLASSIFICATION_MISSING")
    return {
        "schema_version": ENTRY_VERSION,
        "gap_id": gap_id,
        "previous_bar_timestamp": previous_timestamp,
        "next_bar_timestamp": next_timestamp,
        "policy_classification": classification,
        **_semantics(contract, classification),
        "source_contract_type": contract,
        "source_record_identity": source_record_identity,
    }


def _read_generic(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "gap_policy_entries.v1":
        raise GapPolicyValidationError("generic gap artifact schema mismatch")
    records = payload.get("entries")
    if not isinstance(records, list) or not records:
        raise GapPolicyValidationError("generic gap artifact requires entries")
    entries = []
    for record in records:
        _require(record, (
            "gap_id", "previous_bar_timestamp", "next_bar_timestamp",
            "source_record_identity", *SEMANTIC_FIELDS,
        ), "GAP_POLICY_ENTRY_REQUIRED_FIELD_MISSING")
        normalized = _entry(
            GENERIC_CONTRACT, record["gap_id"], record["previous_bar_timestamp"],
            record["next_bar_timestamp"], record.get("policy_classification"),
            record["source_record_identity"],
        )
        if any(record[field] != normalized[field] for field in (
            "accepted_for_trading_bar_skip", "fail_closed_required",
        )):
            raise GapPolicyValidationError("generic semantic booleans conflict with classification")
        if any(record[field] != normalized[field] for field in (
            "reset_active_swing_state", "reset_open_break_candidate",
            "reset_retest_confirmation_state",
        )):
            raise GapPolicyValidationError("GAP_POLICY_RESET_BOOLEANS_INVALID")
        if record["prohibit_event_crossing"] != normalized["prohibit_event_crossing"]:
            raise GapPolicyValidationError("GAP_POLICY_EVENT_CROSSING_BOOLEAN_INVALID")
        if record["require_fresh_post_gap_warmup"] != normalized["require_fresh_post_gap_warmup"]:
            raise GapPolicyValidationError("GAP_POLICY_WARMUP_BOOLEAN_INVALID")
        entries.append(normalized)
    return entries


def _eo_gap_id(policy_id: str, row_number: int, row: dict[str, str]) -> str:
    payload = {
        "policy_id": policy_id, "row_number": row_number,
        "previous_bar_timestamp": row["prev_time"],
        "next_bar_timestamp": row["next_time"],
        "policy_classification": row["policy_status"],
    }
    return "EOFJ-" + digest(payload)[:16].upper()


def _read_eo_fj(path: Path, policy_id: str) -> list[dict[str, Any]]:
    entries = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not set(EO_REQUIRED_COLUMNS).issubset(reader.fieldnames):
            raise GapPolicyValidationError("EO/FJ gap CSV schema mismatch")
        for row_number, row in enumerate(reader, start=2):
            source_identity = f"{EO_FJ_CONTRACT}:{policy_id}:ROW:{row_number:06d}"
            entries.append(_entry(
                EO_FJ_CONTRACT, _eo_gap_id(policy_id, row_number, row),
                row["prev_time"], row["next_time"], row["policy_status"],
                source_identity,
            ))
    if not entries:
        raise GapPolicyValidationError("EO/FJ gap CSV requires rows")
    return entries


def _read_fq(path: Path) -> list[dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list) or not records:
        raise GapPolicyValidationError("FQ gap inventory requires rows")
    entries = []
    for record in records:
        _require(record, (
            "gap_id", "previous_bar_timestamp", "next_bar_timestamp",
            "accepted_for_trading_bar_skip",
            "fail_closed_required",
        ), "GAP_POLICY_ENTRY_REQUIRED_FIELD_MISSING")
        normalized = _entry(
            FQ_CONTRACT, record["gap_id"], record["previous_bar_timestamp"],
            record["next_bar_timestamp"], record.get("policy_classification"),
            record.get("source_record_identity", f"{FQ_CONTRACT}:{record['gap_id']}"),
        )
        if any(record[field] != normalized[field] for field in (
            "accepted_for_trading_bar_skip", "fail_closed_required",
        )):
            code = (
                "FQ_ACCEPTED_CLOSURE_BOOLEANS_CONTRADICTORY"
                if normalized["closure_disposition"] == "ACCEPTED_CLOSURE"
                else "FQ_UNVERIFIED_GAP_BOOLEANS_CONTRADICTORY"
            )
            raise GapPolicyValidationError(code)
        entries.append(normalized)
    return entries


def validate_gap_policy_data(manifest: dict[str, Any], manifest_root: Path) -> dict[str, Any]:
    _require(manifest, (
        "schema_version", "policy_id", "source_contract_type", "runtime_path",
        "artifact_sha256", "classification_allowlist", "expected_entry_count",
        "broker_history_completeness",
    ), "GAP_POLICY_MANIFEST_REQUIRED_FIELD_MISSING")
    if manifest["schema_version"] != MANIFEST_VERSION:
        raise GapPolicyValidationError("GAP_POLICY_MANIFEST_SCHEMA_VERSION_UNSUPPORTED")
    contract = manifest["source_contract_type"]
    if contract not in CONTRACT_TYPES:
        raise GapPolicyValidationError("unsupported source contract type")
    if manifest["broker_history_completeness"] != "NOT_PROVEN":
        raise GapPolicyValidationError("broker history completeness must remain NOT_PROVEN")
    exact_allowlist = sorted(ACCEPTED_CLASSIFICATIONS[contract] | UNVERIFIED_CLASSIFICATIONS[contract])
    if manifest["classification_allowlist"] != exact_allowlist:
        raise GapPolicyValidationError("declared classification allowlist is not exact")
    path = Path(manifest["runtime_path"])
    if not path.is_absolute():
        path = manifest_root / path
    if not path.is_file():
        raise GapPolicyValidationError("GAP_POLICY_ARTIFACT_MISSING")
    if sha256_file(path) != manifest["artifact_sha256"].lower():
        raise GapPolicyValidationError("GAP_POLICY_ARTIFACT_SHA256_MISMATCH")
    if contract == GENERIC_CONTRACT:
        entries = _read_generic(path)
    elif contract == EO_FJ_CONTRACT:
        entries = _read_eo_fj(path, manifest["policy_id"])
    else:
        entries = _read_fq(path)
    entries.sort(key=lambda item: (
        item["previous_bar_timestamp"], item["next_bar_timestamp"],
        item["gap_id"], item["source_record_identity"],
    ))
    if len(entries) != manifest["expected_entry_count"]:
        raise GapPolicyValidationError("gap policy entry count mismatch")
    for field in ("gap_id", "source_record_identity"):
        values = [entry[field] for entry in entries]
        if len(values) != len(set(values)):
            raise GapPolicyValidationError(f"duplicate normalized {field}")
    pairs = [(entry["previous_bar_timestamp"], entry["next_bar_timestamp"]) for entry in entries]
    if len(pairs) != len(set(pairs)):
        raise GapPolicyValidationError("duplicate normalized gap timestamp pair")
    entries_sha256 = digest(entries)
    identity_payload = {
        "schema_version": MANIFEST_VERSION,
        "policy_id": manifest["policy_id"],
        "source_contract_type": contract,
        "artifact_sha256": manifest["artifact_sha256"].lower(),
        "classification_allowlist": exact_allowlist,
        "normalized_entries_sha256": entries_sha256,
    }
    return {
        "schema_version": MANIFEST_VERSION,
        "policy_id": manifest["policy_id"],
        "policy_identity_sha256": digest(identity_payload),
        "source_contract_type": contract,
        "artifact_sha256": manifest["artifact_sha256"].lower(),
        "classification_allowlist": exact_allowlist,
        "broker_history_completeness": "NOT_PROVEN",
        "entry_count": len(entries),
        "normalized_entries_sha256": entries_sha256,
        "entries": entries,
    }


def validate_gap_policy(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.is_file():
        raise GapPolicyValidationError("GAP_POLICY_MANIFEST_MISSING")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise GapPolicyValidationError("GAP_POLICY_MANIFEST_MALFORMED") from exc
    if not isinstance(manifest, dict):
        raise GapPolicyValidationError("GAP_POLICY_MANIFEST_MALFORMED")
    return validate_gap_policy_data(manifest, manifest_path.parent)
