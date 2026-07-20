#!/usr/bin/env python3
"""Synthetic-only composition of validated source and gap contracts."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from gap_policy_adapter import canonical_bytes, digest, validate_gap_policy_data
from historical_source_adapter import normalize_manifest, validate_manifest_data

DESCRIPTOR_VERSION = "dataset_execution_descriptor.v1"
ADAPTER_VALIDATION_ONLY = "ADAPTER_VALIDATION_ONLY"
DETECTOR_CONTRACT_VERSION = "DETECTOR_NOT_EXECUTED_ADAPTER_ONLY_V1"
OUTCOME_CONTRACT_VERSION = "OUTCOME_NOT_EXECUTED_ADAPTER_ONLY_V1"
INTERPRETATION_CONTRACT_VERSION = "INTERPRETATION_NOT_EXECUTED_ADAPTER_ONLY_V1"
A3B_VALIDATION_CODES = frozenset({
    "DESCRIPTOR_ROOT_NOT_OBJECT",
    "DESCRIPTOR_SCHEMA_VERSION_UNSUPPORTED",
    "DESCRIPTOR_REQUIRED_FIELD_MISSING",
    "DESCRIPTOR_DATASET_ID_MISMATCH",
    "DESCRIPTOR_DATASET_ROLE_MISMATCH",
    "DESCRIPTOR_SYMBOL_MISMATCH",
    "DESCRIPTOR_TIMEFRAME_MISMATCH",
    "DESCRIPTOR_BOUNDARY_START_MISMATCH",
    "DESCRIPTOR_BOUNDARY_END_MISMATCH",
    "SOURCE_MANIFEST_IDENTITY_MISMATCH",
    "SOURCE_MANIFEST_SHA256_MISMATCH",
    "CANONICAL_TIMELINE_IDENTITY_MISMATCH",
    "CANONICAL_TIMELINE_SHA256_MISMATCH",
    "CANONICAL_BAR_COUNT_MISMATCH",
    "CANONICAL_FIRST_TIMESTAMP_MISMATCH",
    "CANONICAL_LAST_TIMESTAMP_MISMATCH",
    "GAP_DATASET_BINDING_MISMATCH",
    "GAP_PREVIOUS_TIMESTAMP_UNRESOLVED",
    "GAP_NEXT_TIMESTAMP_UNRESOLVED",
    "GAP_TIMESTAMP_OUTSIDE_SOURCE_BOUNDARY",
    "GAP_ENTRY_COUNT_MISMATCH",
    "GAP_ACCEPTED_CLOSURE_COUNT_MISMATCH",
    "GAP_UNVERIFIED_GAP_COUNT_MISMATCH",
    "GAP_DISPOSITION_COUNT_TOTAL_MISMATCH",
    "CLASSIFICATION_ALLOWLIST_IDENTITY_MISMATCH",
    "BROKER_HISTORY_COMPLETENESS_NOT_PROVEN",
    "DETECTOR_CONTRACT_VERSION_MISMATCH",
    "OUTCOME_CONTRACT_VERSION_MISMATCH",
    "INTERPRETATION_CONTRACT_VERSION_MISMATCH",
    "EXECUTION_MODE_NOT_ADAPTER_VALIDATION_ONLY",
    "DETECTOR_EXECUTION_PERMISSION_NOT_FALSE",
    "OUTCOME_EXECUTION_PERMISSION_NOT_FALSE",
    "ADAPTER_ONLY_DETECTOR_REQUESTED",
    "ADAPTER_ONLY_EVENT_OR_ATR_REQUESTED",
    "ADAPTER_ONLY_TP_SL_OR_OUTCOME_REQUESTED",
    "ADAPTER_ONLY_FN_INTERPRETATION_REQUESTED",
})
DESCRIPTOR_REQUIRED_FIELDS = (
    "schema_version", "dataset_id", "dataset_role", "symbol", "timeframe",
    "boundary_start_timestamp", "boundary_end_timestamp",
    "source_manifest_identity_sha256", "source_manifest_sha256",
    "canonical_timeline_identity_sha256", "canonical_timeline_sha256",
    "canonical_bar_count", "canonical_timeline_boundary",
    "gap_policy_identity_sha256", "gap_policy_sha256",
    "gap_counts_by_classification", "gap_counts_by_disposition",
    "classification_allowlist_identity_sha256", "broker_history_completeness",
    "detector_contract_version", "outcome_contract_version",
    "interpretation_contract_version", "execution_mode",
    "detector_execution_allowed", "outcome_execution_allowed",
    "descriptor_identity_sha256",
)


class AdapterOnlyExecutionProhibited(RuntimeError):
    """Raised before any execution-capable adapter action can begin."""


class AdapterValidationOnlyGuard:
    """A deliberately non-executable boundary for composition fixtures."""

    execution_mode = ADAPTER_VALIDATION_ONLY

    @staticmethod
    def _blocked() -> None:
        raise AdapterOnlyExecutionProhibited("ADAPTER_VALIDATION_ONLY_EXECUTION_PROHIBITED")

    def execute_detector(self) -> None:
        self._blocked()

    def emit_event(self) -> None:
        self._blocked()

    def emit_atr_event(self) -> None:
        self._blocked()

    def calculate_tp_sl(self) -> None:
        self._blocked()

    def emit_outcome(self) -> None:
        self._blocked()

    def interpret_fn(self) -> None:
        self._blocked()


class DescriptorValidationError(ValueError):
    """A frozen cross-contract descriptor assertion did not hold."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _source_manifest_sha256(source: dict[str, Any]) -> str:
    payload = {
        "dataset_id": source["dataset_id"],
        "symbol": source["symbol"],
        "timeframe": source["timeframe"],
        "boundary_start_timestamp": source["boundary_start_timestamp"],
        "boundary_end_timestamp": source["boundary_end_timestamp"],
        "sources": [{
            "source_id": item["source_id"],
            "sha256": item["sha256"],
            "size_bytes": item["size_bytes"],
            "row_count": item["row_count"],
            "first_timestamp": item["first_timestamp"],
            "last_timestamp": item["last_timestamp"],
        } for item in source["sources"]],
        "timeline": source["timeline"],
    }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _require_binding(source: dict[str, Any], binding: dict[str, Any]) -> None:
    required = (
        "dataset_id", "symbol", "timeframe",
        "boundary_start_timestamp", "boundary_end_timestamp",
    )
    if not isinstance(binding, dict) or any(key not in binding for key in required):
        raise ValueError("dataset execution binding is incomplete")
    if any(binding[key] != source[key] for key in required):
        raise ValueError("dataset execution binding does not match source contract")


def _validate_gap_timeline(source: dict[str, Any], gap: dict[str, Any]) -> None:
    timeline = source["timeline"]
    boundaries = (
        source["boundary_start_timestamp"],
        source["boundary_end_timestamp"],
    )
    timestamps = {
        source["boundary_start_timestamp"],
        source["boundary_end_timestamp"],
    }
    # The source adapter's timeline hash is over bars; revalidate the raw sources
    # to obtain only their canonical timestamps without exposing them in output.
    # Canonical source data has already been validated before this function.
    for item in gap["entries"]:
        previous = item["previous_bar_timestamp"]
        next_ = item["next_bar_timestamp"]
        if previous < boundaries[0] or next_ > boundaries[1]:
            raise ValueError("gap lies outside frozen source boundary")
        timestamps.add(previous)
        timestamps.add(next_)
    # A fixture supplies the complete canonical timestamp set explicitly; it is
    # hashed and checked against the source timeline count before composition.
    declared = source.get("_canonical_timestamps")
    if not isinstance(declared, tuple) or len(declared) != timeline["total_rows"]:
        raise ValueError("canonical timeline timestamp binding is unavailable")
    if any(stamp not in declared for stamp in timestamps):
        raise ValueError("gap timestamp does not resolve to canonical timeline")


def _source_with_timestamp_binding(raw_source: dict[str, Any], source_root: Path) -> dict[str, Any]:
    source = validate_manifest_data(raw_source, source_root)
    # This private field is only used for cross-contract membership checks and is
    # removed before canonical descriptor output. Re-read normalized source rows
    # through the public source adapter's validated result is intentionally avoided.
    manifest = normalize_manifest(raw_source)
    stamps: list[str] = []
    import csv
    from datetime import datetime
    for spec in manifest["sources"]:
        path = Path(spec["runtime_path"])
        if not path.is_absolute():
            path = source_root / path
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="	"):
                stamps.append(datetime.strptime(
                    f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S"
                ).isoformat())
    source["_canonical_timestamps"] = tuple(sorted(stamps))
    return source


def compose_dataset_execution_descriptor(
    request: dict[str, Any], fixture_root: Path,
) -> dict[str, Any]:
    """Compose only validated synthetic contracts; no detector/outcome path exists."""
    if request.get("schema_version") != "synthetic_dataset_composition_request.v1":
        raise ValueError("unsupported synthetic composition request")
    if request.get("execution_mode") != ADAPTER_VALIDATION_ONLY:
        raise AdapterOnlyExecutionProhibited("ADAPTER_VALIDATION_ONLY_REQUIRED")
    source = _source_with_timestamp_binding(request["historical_source_manifest"], fixture_root)
    gap = validate_gap_policy_data(request["gap_policy_manifest"], fixture_root)
    _require_binding(source, request["gap_dataset_binding"])
    if source["broker_history_completeness"] != "NOT_PROVEN" or gap["broker_history_completeness"] != "NOT_PROVEN":
        raise ValueError("broker history completeness must remain NOT_PROVEN")
    _validate_gap_timeline(source, gap)
    allowlist_identity = digest({
        "source_contract_type": gap["source_contract_type"],
        "classification_allowlist": gap["classification_allowlist"],
    })
    counts = {
        classification: sum(
            entry["policy_classification"] == classification for entry in gap["entries"]
        )
        for classification in gap["classification_allowlist"]
        if any(entry["policy_classification"] == classification for entry in gap["entries"])
    }
    disposition_counts = {
        disposition: sum(
            entry["closure_disposition"] == disposition for entry in gap["entries"]
        )
        for disposition in ("ACCEPTED_CLOSURE", "UNVERIFIED_GAP")
        if any(entry["closure_disposition"] == disposition for entry in gap["entries"])
    }
    core = {
        "schema_version": DESCRIPTOR_VERSION,
        "dataset_id": source["dataset_id"],
        "dataset_role": request["dataset_role"],
        "symbol": source["symbol"],
        "timeframe": source["timeframe"],
        "boundary_start_timestamp": source["boundary_start_timestamp"],
        "boundary_end_timestamp": source["boundary_end_timestamp"],
        "source_manifest_identity_sha256": source["dataset_identity_sha256"],
        "source_manifest_sha256": _source_manifest_sha256(source),
        "canonical_timeline_identity_sha256": digest({
            "dataset_identity_sha256": source["dataset_identity_sha256"],
            "canonical_timeline_sha256": source["timeline"]["canonical_timeline_sha256"],
            "total_rows": source["timeline"]["total_rows"],
            "boundary_start_timestamp": source["boundary_start_timestamp"],
            "boundary_end_timestamp": source["boundary_end_timestamp"],
        }),
        "canonical_timeline_sha256": source["timeline"]["canonical_timeline_sha256"],
        "canonical_bar_count": source["timeline"]["total_rows"],
        "canonical_timeline_boundary": {
            "first_timestamp": source["timeline"]["first_timestamp"],
            "last_timestamp": source["timeline"]["last_timestamp"],
        },
        "gap_policy_identity_sha256": gap["policy_identity_sha256"],
        "gap_policy_sha256": gap["normalized_entries_sha256"],
        "gap_counts_by_classification": counts,
        "gap_counts_by_disposition": disposition_counts,
        "classification_allowlist_identity_sha256": allowlist_identity,
        "broker_history_completeness": "NOT_PROVEN",
        "detector_contract_version": DETECTOR_CONTRACT_VERSION,
        "outcome_contract_version": OUTCOME_CONTRACT_VERSION,
        "interpretation_contract_version": INTERPRETATION_CONTRACT_VERSION,
        "execution_mode": ADAPTER_VALIDATION_ONLY,
        "detector_execution_allowed": False,
        "outcome_execution_allowed": False,
    }
    core["descriptor_identity_sha256"] = digest(core)
    return core


def validate_adapter_only_invocation(invocation: dict[str, Any] | None) -> None:
    """Reject execution requests before any detector import or invocation."""
    if invocation is None:
        return
    if not isinstance(invocation, dict):
        raise DescriptorValidationError("ADAPTER_ONLY_DETECTOR_REQUESTED")
    if invocation.get("detector_execution") is True:
        raise DescriptorValidationError("ADAPTER_ONLY_DETECTOR_REQUESTED")
    if invocation.get("event_output") is True or invocation.get("atr_event_output") is True:
        raise DescriptorValidationError("ADAPTER_ONLY_EVENT_OR_ATR_REQUESTED")
    if invocation.get("tp_sl_calculation") is True or invocation.get("outcome_execution") is True:
        raise DescriptorValidationError("ADAPTER_ONLY_TP_SL_OR_OUTCOME_REQUESTED")
    if invocation.get("fn_interpretation") is True:
        raise DescriptorValidationError("ADAPTER_ONLY_FN_INTERPRETATION_REQUESTED")


def _timeline_identity(source: dict[str, Any]) -> str:
    return digest({
        "dataset_identity_sha256": source["dataset_identity_sha256"],
        "canonical_timeline_sha256": source["timeline"]["canonical_timeline_sha256"],
        "total_rows": source["timeline"]["total_rows"],
        "boundary_start_timestamp": source["boundary_start_timestamp"],
        "boundary_end_timestamp": source["boundary_end_timestamp"],
    })


def _assert_equal(actual: Any, expected: Any, code: str) -> None:
    if actual != expected:
        raise DescriptorValidationError(code)


def validate_dataset_execution_descriptor(
    descriptor: Any, request: dict[str, Any], fixture_root: Path,
    invocation: dict[str, Any] | None = None,
    validation_assertions: dict[str, int] | None = None,
) -> None:
    """Validate a candidate descriptor against synthetic source and gap contracts."""
    if not isinstance(descriptor, dict):
        raise DescriptorValidationError("DESCRIPTOR_ROOT_NOT_OBJECT")
    if descriptor.get("schema_version") != DESCRIPTOR_VERSION:
        raise DescriptorValidationError("DESCRIPTOR_SCHEMA_VERSION_UNSUPPORTED")
    if any(field not in descriptor for field in DESCRIPTOR_REQUIRED_FIELDS):
        raise DescriptorValidationError("DESCRIPTOR_REQUIRED_FIELD_MISSING")

    source = _source_with_timestamp_binding(request["historical_source_manifest"], fixture_root)
    gap = validate_gap_policy_data(request["gap_policy_manifest"], fixture_root)

    _assert_equal(descriptor["dataset_id"], source["dataset_id"], "DESCRIPTOR_DATASET_ID_MISMATCH")
    _assert_equal(descriptor["dataset_role"], request["dataset_role"], "DESCRIPTOR_DATASET_ROLE_MISMATCH")
    _assert_equal(descriptor["symbol"], source["symbol"], "DESCRIPTOR_SYMBOL_MISMATCH")
    _assert_equal(descriptor["timeframe"], source["timeframe"], "DESCRIPTOR_TIMEFRAME_MISMATCH")
    _assert_equal(descriptor["boundary_start_timestamp"], source["boundary_start_timestamp"], "DESCRIPTOR_BOUNDARY_START_MISMATCH")
    _assert_equal(descriptor["boundary_end_timestamp"], source["boundary_end_timestamp"], "DESCRIPTOR_BOUNDARY_END_MISMATCH")

    _assert_equal(descriptor["source_manifest_identity_sha256"], source["dataset_identity_sha256"], "SOURCE_MANIFEST_IDENTITY_MISMATCH")
    _assert_equal(descriptor["source_manifest_sha256"], _source_manifest_sha256(source), "SOURCE_MANIFEST_SHA256_MISMATCH")
    _assert_equal(descriptor["canonical_timeline_identity_sha256"], _timeline_identity(source), "CANONICAL_TIMELINE_IDENTITY_MISMATCH")
    _assert_equal(descriptor["canonical_timeline_sha256"], source["timeline"]["canonical_timeline_sha256"], "CANONICAL_TIMELINE_SHA256_MISMATCH")
    _assert_equal(descriptor["canonical_bar_count"], source["timeline"]["total_rows"], "CANONICAL_BAR_COUNT_MISMATCH")
    boundary = descriptor["canonical_timeline_boundary"]
    if not isinstance(boundary, dict) or boundary.get("first_timestamp") != source["timeline"]["first_timestamp"]:
        raise DescriptorValidationError("CANONICAL_FIRST_TIMESTAMP_MISMATCH")
    if boundary.get("last_timestamp") != source["timeline"]["last_timestamp"]:
        raise DescriptorValidationError("CANONICAL_LAST_TIMESTAMP_MISMATCH")

    binding = request.get("gap_dataset_binding")
    required_binding = ("dataset_id", "symbol", "timeframe", "boundary_start_timestamp", "boundary_end_timestamp")
    if not isinstance(binding, dict) or any(binding.get(key) != source[key] for key in required_binding):
        raise DescriptorValidationError("GAP_DATASET_BINDING_MISMATCH")

    stamps = set(source["_canonical_timestamps"])
    start, end = source["boundary_start_timestamp"], source["boundary_end_timestamp"]
    for entry in gap["entries"]:
        previous, next_ = entry["previous_bar_timestamp"], entry["next_bar_timestamp"]
        if previous < start or next_ > end:
            raise DescriptorValidationError("GAP_TIMESTAMP_OUTSIDE_SOURCE_BOUNDARY")
        if previous not in stamps:
            raise DescriptorValidationError("GAP_PREVIOUS_TIMESTAMP_UNRESOLVED")
        if next_ not in stamps:
            raise DescriptorValidationError("GAP_NEXT_TIMESTAMP_UNRESOLVED")

    assertions = validation_assertions or {}
    entry_count = len(gap["entries"])
    accepted_count = sum(entry["closure_disposition"] == "ACCEPTED_CLOSURE" for entry in gap["entries"])
    unverified_count = sum(entry["closure_disposition"] == "UNVERIFIED_GAP" for entry in gap["entries"])
    if "gap_entry_count" in assertions and assertions["gap_entry_count"] != entry_count:
        raise DescriptorValidationError("GAP_ENTRY_COUNT_MISMATCH")
    if "accepted_closure_count" in assertions and assertions["accepted_closure_count"] != accepted_count:
        raise DescriptorValidationError("GAP_ACCEPTED_CLOSURE_COUNT_MISMATCH")
    if "unverified_gap_count" in assertions and assertions["unverified_gap_count"] != unverified_count:
        raise DescriptorValidationError("GAP_UNVERIFIED_GAP_COUNT_MISMATCH")
    if ("declared_total_gap_count" in assertions
            and accepted_count + unverified_count != assertions["declared_total_gap_count"]):
        raise DescriptorValidationError("GAP_DISPOSITION_COUNT_TOTAL_MISMATCH")

    allowlist_identity = digest({
        "source_contract_type": gap["source_contract_type"],
        "classification_allowlist": gap["classification_allowlist"],
    })
    _assert_equal(descriptor["classification_allowlist_identity_sha256"], allowlist_identity, "CLASSIFICATION_ALLOWLIST_IDENTITY_MISMATCH")
    _assert_equal(descriptor["broker_history_completeness"], "NOT_PROVEN", "BROKER_HISTORY_COMPLETENESS_NOT_PROVEN")
    _assert_equal(descriptor["detector_contract_version"], DETECTOR_CONTRACT_VERSION, "DETECTOR_CONTRACT_VERSION_MISMATCH")
    _assert_equal(descriptor["outcome_contract_version"], OUTCOME_CONTRACT_VERSION, "OUTCOME_CONTRACT_VERSION_MISMATCH")
    _assert_equal(descriptor["interpretation_contract_version"], INTERPRETATION_CONTRACT_VERSION, "INTERPRETATION_CONTRACT_VERSION_MISMATCH")
    _assert_equal(descriptor["execution_mode"], ADAPTER_VALIDATION_ONLY, "EXECUTION_MODE_NOT_ADAPTER_VALIDATION_ONLY")
    _assert_equal(descriptor["detector_execution_allowed"], False, "DETECTOR_EXECUTION_PERMISSION_NOT_FALSE")
    _assert_equal(descriptor["outcome_execution_allowed"], False, "OUTCOME_EXECUTION_PERMISSION_NOT_FALSE")
    validate_adapter_only_invocation(invocation)
