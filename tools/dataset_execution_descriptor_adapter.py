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
