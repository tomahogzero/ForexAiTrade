#!/usr/bin/env python3
"""Generic historical-source adapter. No gap, detector, or outcome logic."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

MANIFEST_VERSION = "historical_source_manifest.v1"
SOURCE_VERSION = "source_file_descriptor.v1"
FORMAT_PROFILE = "MT5_TSV_OHLC_V1"
REQUIRED_COLUMNS = ("<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>")
A1B1_VALIDATION_CODES = frozenset({
    "SOURCE_PATH_MISSING", "SOURCE_SHA256_MISMATCH", "SOURCE_SIZE_MISMATCH",
    "MT5_TSV_SCHEMA_INVALID", "SOURCE_TIMESTAMP_UNPARSEABLE",
    "OHLC_NON_FINITE_OR_NON_POSITIVE", "OHLC_INCONSISTENT",
    "SOURCE_NOT_CHRONOLOGICAL", "SOURCE_ROW_COUNT_MISMATCH",
})


class AdapterValidationError(ValueError):
    """Frozen source expectation was not satisfied."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require(mapping: dict[str, Any], keys: tuple[str, ...], label: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise AdapterValidationError(f"{label} missing fields: {','.join(missing)}")


def _timestamp(value: str, label: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise AdapterValidationError(f"invalid {label}: {value}") from exc
    if parsed.tzinfo is not None:
        raise AdapterValidationError(f"timezone-aware {label} is not allowed")
    return parsed


def _mapped_source(spec: dict[str, Any], identity: dict[str, Any], style: str) -> dict[str, Any]:
    row_field = "rows" if style == "FP_SOURCE_CONTRACT_V1" else "row_count"
    return {
        "schema_version": SOURCE_VERSION,
        "source_id": identity["source_id"],
        "file_name": identity["file_name"],
        "runtime_path": identity.get("runtime_path", spec["path"]),
        "sha256": spec["sha256"].lower(),
        "size_bytes": spec.get("size_bytes"),
        "row_count": spec[row_field],
        "first_timestamp": spec["first_timestamp"],
        "last_timestamp": spec["last_timestamp"],
        "format": FORMAT_PROFILE,
    }


def normalize_manifest(raw: dict[str, Any]) -> dict[str, Any]:
    """Map generic, FP-contract, or FJ-provenance input to the v1 model."""
    if raw.get("schema_version") == MANIFEST_VERSION:
        return json.loads(json.dumps(raw))
    profile = raw.get("mapping_profile")
    if profile not in {"FP_SOURCE_CONTRACT_V1", "FJ_SOURCE_PROVENANCE_V1"}:
        raise AdapterValidationError("unsupported manifest or mapping profile")
    context = raw["dataset_context"]
    payload = raw["contract"] if profile == "FP_SOURCE_CONTRACT_V1" else raw["provenance"]
    specs = payload["source_files"] if profile == "FP_SOURCE_CONTRACT_V1" else payload["sources"]
    identities = raw["source_identities"]
    if len(specs) != len(identities):
        raise AdapterValidationError("source identity count mismatch")
    source = payload if profile == "FP_SOURCE_CONTRACT_V1" else context
    return {
        "schema_version": MANIFEST_VERSION,
        "dataset_id": context["dataset_id"],
        "symbol": source["symbol"],
        "timeframe": source["timeframe"],
        "boundary_start_timestamp": source["boundary_start_timestamp"],
        "boundary_end_timestamp": source["boundary_end_timestamp"],
        "broker_history_completeness": payload.get("broker_history_completeness", context.get("broker_history_completeness")),
        "raw_broker_csv_committed": payload.get("raw_broker_csv_committed", False),
        "sources": [_mapped_source(spec, identity, profile) for spec, identity in zip(specs, identities)],
        "expected_timeline": context["expected_timeline"],
    }


def _validate_manifest_shape(manifest: dict[str, Any]) -> None:
    _require(manifest, ("schema_version", "dataset_id", "symbol", "timeframe",
        "boundary_start_timestamp", "boundary_end_timestamp", "sources",
        "expected_timeline", "broker_history_completeness", "raw_broker_csv_committed"), "manifest")
    if manifest["schema_version"] != MANIFEST_VERSION:
        raise AdapterValidationError("manifest schema version mismatch")
    if not all(isinstance(manifest[key], str) and manifest[key] for key in ("dataset_id", "symbol", "timeframe")):
        raise AdapterValidationError("dataset_id, symbol, and timeframe must be explicit")
    if manifest["broker_history_completeness"] != "NOT_PROVEN":
        raise AdapterValidationError("broker history completeness must remain NOT_PROVEN")
    if manifest["raw_broker_csv_committed"] is not False:
        raise AdapterValidationError("raw broker CSV must remain outside Git")
    if not isinstance(manifest["sources"], list) or not manifest["sources"]:
        raise AdapterValidationError("manifest requires at least one source")


def _ohlc(row: dict[str, str], label: str) -> tuple[str, str, str, str]:
    try:
        values = tuple(Decimal(row[column]) for column in REQUIRED_COLUMNS[2:])
    except (InvalidOperation, KeyError) as exc:
        raise AdapterValidationError(f"invalid OHLC at {label}") from exc
    if not all(value.is_finite() and value > 0 for value in values):
        raise AdapterValidationError("OHLC_NON_FINITE_OR_NON_POSITIVE")
    op, high, low, close = values
    if high < max(op, close) or low > min(op, close) or high < low:
        raise AdapterValidationError("OHLC_INCONSISTENT")
    return tuple(format(value.normalize(), "f") for value in values)


def _read_source(spec: dict[str, Any], root: Path, start: datetime, end: datetime):
    _require(spec, ("schema_version", "source_id", "file_name", "runtime_path",
        "sha256", "row_count", "first_timestamp", "last_timestamp", "format"), "source")
    if spec["schema_version"] != SOURCE_VERSION or spec["format"] != FORMAT_PROFILE:
        raise AdapterValidationError("source schema or format profile mismatch")
    path = Path(spec["runtime_path"])
    if not path.is_absolute():
        path = root / path
    if not path.is_file():
        raise AdapterValidationError("SOURCE_PATH_MISSING")
    if sha256_file(path) != spec["sha256"].lower():
        raise AdapterValidationError("SOURCE_SHA256_MISMATCH")
    if spec.get("size_bytes") is not None and path.stat().st_size != spec["size_bytes"]:
        raise AdapterValidationError("SOURCE_SIZE_MISMATCH")
    bars: list[dict[str, str]] = []
    times: list[datetime] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not set(REQUIRED_COLUMNS).issubset(reader.fieldnames):
            raise AdapterValidationError("MT5_TSV_SCHEMA_INVALID")
        for line, row in enumerate(reader, start=2):
            try:
                stamp = datetime.strptime(f"{row['<DATE>']} {row['<TIME>']}", "%Y.%m.%d %H:%M:%S")
            except (TypeError, ValueError) as exc:
                raise AdapterValidationError("SOURCE_TIMESTAMP_UNPARSEABLE") from exc
            op, high, low, close = _ohlc(row, f"{spec['source_id']}:{line}")
            if stamp < start or stamp > end:
                raise AdapterValidationError(f"source row outside boundary: {spec['source_id']}:{line}")
            times.append(stamp)
            bars.append({"timestamp": stamp.isoformat(), "source_id": spec["source_id"],
                "source_row_key": f"{spec['source_id']}:{line}", "open": op,
                "high": high, "low": low, "close": close})
    if not bars:
        raise AdapterValidationError(f"empty source: {spec['source_id']}")
    if any(left >= right for left, right in zip(times, times[1:])):
        raise AdapterValidationError("SOURCE_NOT_CHRONOLOGICAL")
    if len(bars) != spec["row_count"]:
        raise AdapterValidationError("SOURCE_ROW_COUNT_MISMATCH")
    if times[0] != _timestamp(spec["first_timestamp"], "source first timestamp"):
        raise AdapterValidationError(f"source first timestamp mismatch: {spec['source_id']}")
    if times[-1] != _timestamp(spec["last_timestamp"], "source last timestamp"):
        raise AdapterValidationError(f"source last timestamp mismatch: {spec['source_id']}")
    source_result = {
        "source_id": spec["source_id"], "file_name": spec["file_name"],
        "sha256": spec["sha256"].lower(), "size_bytes": path.stat().st_size,
        "row_count": len(bars), "first_timestamp": times[0].isoformat(),
        "last_timestamp": times[-1].isoformat(), "chronological": True,
        "ohlc_integrity": "PASS",
    }
    return source_result, bars


def validate_manifest_data(raw: dict[str, Any], manifest_root: Path) -> dict[str, Any]:
    """Validate in-memory manifest data relative to an explicit runtime root."""
    manifest = normalize_manifest(raw)
    _validate_manifest_shape(manifest)
    start = _timestamp(manifest["boundary_start_timestamp"], "boundary start")
    end = _timestamp(manifest["boundary_end_timestamp"], "boundary end")
    if start > end:
        raise AdapterValidationError("manifest boundary is reversed")
    source_results, bars = [], []
    for spec in manifest["sources"]:
        result, source_bars = _read_source(spec, manifest_root, start, end)
        source_results.append(result)
        bars.extend(source_bars)
    source_ids = [item["source_id"] for item in source_results]
    if len(source_ids) != len(set(source_ids)):
        raise AdapterValidationError("duplicate source_id")
    bars.sort(key=lambda item: (item["timestamp"], item["source_row_key"]))
    timestamps = [item["timestamp"] for item in bars]
    duplicates = len(timestamps) - len(set(timestamps))
    if duplicates:
        raise AdapterValidationError("duplicate aggregate timestamps")
    timeline_hash = hashlib.sha256(canonical_bytes(bars)).hexdigest()
    expected = manifest["expected_timeline"]
    _require(expected, ("source_count", "total_rows", "first_timestamp",
        "last_timestamp", "duplicate_timestamps", "canonical_timeline_sha256"), "expected timeline")
    observed = {
        "source_count": len(source_results), "total_rows": len(bars),
        "first_timestamp": timestamps[0], "last_timestamp": timestamps[-1],
        "duplicate_timestamps": duplicates, "canonical_timeline_sha256": timeline_hash,
    }
    for key, value in observed.items():
        declared = expected[key]
        if key.endswith("timestamp"):
            declared = _timestamp(declared, key).isoformat()
        if declared != value:
            raise AdapterValidationError(f"aggregate {key} mismatch")
    identity_payload = {
        "dataset_id": manifest["dataset_id"], "symbol": manifest["symbol"],
        "timeframe": manifest["timeframe"],
        "boundary_start_timestamp": start.isoformat(),
        "boundary_end_timestamp": end.isoformat(),
        "sources": [{"source_id": item["source_id"], "sha256": item["sha256"]} for item in source_results],
    }
    return {
        "schema_version": MANIFEST_VERSION,
        "dataset_id": manifest["dataset_id"],
        "dataset_identity_sha256": hashlib.sha256(canonical_bytes(identity_payload)).hexdigest(),
        "symbol": manifest["symbol"], "timeframe": manifest["timeframe"],
        "boundary_start_timestamp": start.isoformat(),
        "boundary_end_timestamp": end.isoformat(),
        "broker_history_completeness": "NOT_PROVEN",
        "raw_broker_csv_committed": False,
        "sources": source_results,
        "timeline": observed,
    }


def validate_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load, normalize, and validate a manifest from disk."""
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    return validate_manifest_data(raw, manifest_path.parent)
