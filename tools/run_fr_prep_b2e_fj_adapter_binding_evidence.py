#!/usr/bin/env python3
"""Projection-only FR-Prep-B2e evidence runner; real binding fails closed."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import ntpath
import posixpath
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from fr_prep_b2e_fj_metadata_projection import (
    FjMetadataTimestampValidationError,
    canonicalize_fj_metadata_timestamp,
)


FORMAT_PATTERNS = (
    ("ISO_DATE_T", re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")),
    ("ISO_DATE_SPACE", re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")),
    ("MT5_DOTTED_DATE_T", re.compile(r"^\d{4}\.\d{2}\.\d{2}T\d{2}:\d{2}:\d{2}$")),
    ("MT5_DOTTED_DATE_SPACE", re.compile(r"^\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}$")),
)
CANONICAL_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
PROHIBITED_MODULES = frozenset(
    {
        "historical_source_adapter",
        "gap_policy_adapter",
        "dataset_execution_descriptor_adapter",
        "market_structure_break_retest_detector",
        "run_checkpoint_fi_detector_fixtures",
        "run_checkpoint_fj_historical_event_population",
        "run_checkpoint_fq_holdout_gap_boundary",
    }
)
SAFETY_COUNTER_NAMES = (
    "real_fj_source_open_count",
    "real_fq_source_open_count",
    "fq_gap_inventory_open_count",
    "adapter_import_count",
    "detector_import_count",
    "detector_execution_count",
    "fi_execution_count",
    "legacy_runner_import_count",
    "legacy_runner_execution_count",
    "event_population_emit_count",
    "outcome_emit_count",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _imported_prohibited_modules() -> list[str]:
    return sorted(
        module_name
        for module_name in sys.modules
        if module_name.split(".")[-1] in PROHIBITED_MODULES
    )


def _safety_counters() -> dict[str, int]:
    imported = {name.split(".")[-1] for name in _imported_prohibited_modules()}
    counters = {name: 0 for name in SAFETY_COUNTER_NAMES}
    counters["adapter_import_count"] = len(
        imported
        & {
            "historical_source_adapter",
            "gap_policy_adapter",
            "dataset_execution_descriptor_adapter",
        }
    )
    counters["detector_import_count"] = int(
        "market_structure_break_retest_detector" in imported
    )
    counters["legacy_runner_import_count"] = int(
        "run_checkpoint_fj_historical_event_population" in imported
    )
    return counters


def _accepted_format_id(value: str) -> str:
    for format_id, pattern in FORMAT_PATTERNS:
        if pattern.fullmatch(value):
            return format_id
    raise AssertionError("validated timestamp did not match an accepted format")


def _project_timestamp(
    container: dict[str, Any],
    key: str,
    field_name: str,
    evidence_source: str,
    audit: list[dict[str, str]],
) -> None:
    original_value = container[key]
    canonical_value = canonicalize_fj_metadata_timestamp(original_value, field_name)
    accepted_format_id = _accepted_format_id(original_value)
    container[key] = canonical_value
    audit.append(
        {
            "accepted_format_id": accepted_format_id,
            "canonical_value": canonical_value,
            "evidence_source": evidence_source,
            "field_name": field_name,
            "original_value": original_value,
        }
    )


def _canonical_identity_payload(projected: Mapping[str, Any]) -> dict[str, Any]:
    dataset_context = projected["dataset_context"]
    stable_sources = []
    for source in projected["provenance"]["sources"]:
        source_identity = source.get("source_id") or source.get("file_name")
        if not isinstance(source_identity, str) or not source_identity:
            raise ValueError("each source requires a source_id or stable file_name")
        stable_sources.append(
            {
                "first_timestamp": source["first_timestamp"],
                "last_timestamp": source["last_timestamp"],
                "source_identity": source_identity,
            }
        )
    stable_sources.sort(key=lambda item: item["source_identity"])
    return {
        "boundary_end_timestamp": dataset_context["boundary_end_timestamp"],
        "boundary_start_timestamp": dataset_context["boundary_start_timestamp"],
        "dataset_id": dataset_context["dataset_id"],
        "expected_timeline": {
            "first_timestamp": dataset_context["expected_timeline"]["first_timestamp"],
            "last_timestamp": dataset_context["expected_timeline"]["last_timestamp"],
        },
        "sources": stable_sources,
        "symbol": dataset_context["symbol"],
        "timeframe": dataset_context["timeframe"],
    }


def project_fj_manifest_metadata(
    raw: Mapping[str, Any], evidence_source: str
) -> dict[str, Any]:
    """Project required in-memory metadata timestamps without source or repo access."""

    if not isinstance(raw, Mapping):
        raise TypeError("raw must be an in-memory mapping")
    if not isinstance(evidence_source, str) or not evidence_source:
        raise ValueError("evidence_source must be a non-empty string")

    caller_snapshot = copy.deepcopy(raw)
    projected = copy.deepcopy(dict(raw))
    audit: list[dict[str, str]] = []
    dataset_context = projected["dataset_context"]
    expected_timeline = dataset_context["expected_timeline"]

    for key in ("boundary_start_timestamp", "boundary_end_timestamp"):
        _project_timestamp(
            dataset_context,
            key,
            f"dataset_context.{key}",
            evidence_source,
            audit,
        )
    for key in ("first_timestamp", "last_timestamp"):
        _project_timestamp(
            expected_timeline,
            key,
            f"dataset_context.expected_timeline.{key}",
            evidence_source,
            audit,
        )
    for source_index, source in enumerate(projected["provenance"]["sources"]):
        for key in ("first_timestamp", "last_timestamp"):
            _project_timestamp(
                source,
                key,
                f"provenance.sources[{source_index}].{key}",
                evidence_source,
                audit,
            )

    audit.sort(key=lambda entry: entry["field_name"])
    identity_payload = _canonical_identity_payload(projected)
    identity_sha256 = hashlib.sha256(
        _canonical_json(identity_payload).encode("utf-8")
    ).hexdigest()
    return {
        "canonical_projection_identity_sha256": identity_sha256,
        "input_mutated": raw != caller_snapshot,
        "projected_metadata": projected,
        "projection_audit": audit,
        "safety_counters": _safety_counters(),
    }


def _lookup_projected_timestamp(projected: Mapping[str, Any], field_name: str) -> Any:
    if field_name.startswith("dataset_context.expected_timeline."):
        key = field_name.rsplit(".", 1)[1]
        return projected["dataset_context"]["expected_timeline"][key]
    if field_name.startswith("dataset_context."):
        key = field_name.rsplit(".", 1)[1]
        return projected["dataset_context"][key]
    source_match = re.fullmatch(
        r"provenance\.sources\[(\d+)\]\.(first_timestamp|last_timestamp)",
        field_name,
    )
    if source_match is None:
        raise KeyError(field_name)
    return projected["provenance"]["sources"][int(source_match.group(1))][
        source_match.group(2)
    ]


def _audit_mismatches(
    result: Mapping[str, Any],
    expected_field_names: list[str],
    expected_format_ids: Mapping[str, str],
    expected_count: int,
) -> int:
    audit = result["projection_audit"]
    mismatch_count = int(len(audit) != expected_count)
    actual_names = [entry["field_name"] for entry in audit]
    mismatch_count += int(actual_names != sorted(expected_field_names))
    required_keys = {
        "accepted_format_id",
        "canonical_value",
        "evidence_source",
        "field_name",
        "original_value",
    }
    for entry in audit:
        mismatch_count += int(set(entry) != required_keys)
        mismatch_count += int(
            entry["accepted_format_id"]
            != expected_format_ids.get(entry["field_name"])
        )
    return mismatch_count


def _canonical_timestamp_mismatches(result: Mapping[str, Any]) -> int:
    projected = result["projected_metadata"]
    mismatches = 0
    for entry in result["projection_audit"]:
        canonical_value = entry["canonical_value"]
        mismatches += int(CANONICAL_PATTERN.fullmatch(canonical_value) is None)
        mismatches += int(
            _lookup_projected_timestamp(projected, entry["field_name"])
            != canonical_value
        )
    return mismatches


def _absolute_runtime_values(value: Any, parent_key: str = "") -> list[str]:
    values: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            values.extend(_absolute_runtime_values(nested, str(key)))
    elif isinstance(value, list):
        for nested in value:
            values.extend(_absolute_runtime_values(nested, parent_key))
    elif (
        isinstance(value, str)
        and "path" in parent_key.lower()
        and (ntpath.isabs(value) or posixpath.isabs(value))
    ):
        values.append(value)
    return values


def _run_projection_fixture(fixture: Mapping[str, Any]) -> dict[str, Any]:
    expected = fixture["expected"]
    view_names = ("legacy_view", "iso_view")
    original_views = {
        view_name: copy.deepcopy(fixture["views"][view_name])
        for view_name in view_names
    }
    first_results: dict[str, dict[str, Any]] = {}
    repeated_results: dict[str, dict[str, Any]] = {}
    input_mutation_count = 0

    for view_name in view_names:
        raw_view = fixture["views"][view_name]
        first_results[view_name] = project_fj_manifest_metadata(
            raw_view, f"{view_name}_synthetic_fixture"
        )
        input_mutation_count += int(raw_view != original_views[view_name])
        input_mutation_count += int(first_results[view_name]["input_mutated"])
        repeated_results[view_name] = project_fj_manifest_metadata(
            raw_view, f"{view_name}_synthetic_fixture"
        )
        input_mutation_count += int(raw_view != original_views[view_name])
        input_mutation_count += int(repeated_results[view_name]["input_mutated"])

    deterministic_mismatch_count = sum(
        _canonical_json(first_results[view_name])
        != _canonical_json(repeated_results[view_name])
        for view_name in view_names
    )
    identities = {
        view_name: first_results[view_name][
            "canonical_projection_identity_sha256"
        ]
        for view_name in view_names
    }
    identity_match = identities["legacy_view"] == identities["iso_view"]

    audit_mismatch_count = sum(
        _audit_mismatches(
            first_results[view_name],
            expected["audit_field_names"],
            expected["accepted_format_ids"][view_name],
            expected["audit_entry_count"],
        )
        for view_name in view_names
    )
    canonical_timestamp_mismatch_count = sum(
        _canonical_timestamp_mismatches(first_results[view_name])
        for view_name in view_names
    )

    absolute_runtime_path_in_identity_count = 0
    for view_name in view_names:
        raw_view = fixture["views"][view_name]
        identity_json = _canonical_json(
            _canonical_identity_payload(
                first_results[view_name]["projected_metadata"]
            )
        )
        absolute_runtime_path_in_identity_count += sum(
            runtime_value in identity_json
            for runtime_value in _absolute_runtime_values(raw_view)
        )

    imported_prohibited_modules = _imported_prohibited_modules()
    safety_counters = first_results["legacy_view"]["safety_counters"]
    safety_mismatch_count = sum(
        result["safety_counters"] != safety_counters
        or any(result["safety_counters"].values())
        for result in (
            first_results["legacy_view"],
            first_results["iso_view"],
            repeated_results["legacy_view"],
            repeated_results["iso_view"],
        )
    )

    passed = (
        identity_match
        and input_mutation_count == 0
        and audit_mismatch_count == 0
        and canonical_timestamp_mismatch_count == 0
        and deterministic_mismatch_count == 0
        and absolute_runtime_path_in_identity_count == 0
        and safety_mismatch_count == 0
        and not imported_prohibited_modules
        and all(value == 0 for value in safety_counters.values())
    )
    summary_core = {
        "absolute_runtime_path_in_canonical_identity_count": absolute_runtime_path_in_identity_count,
        "audit_mismatch_count": audit_mismatch_count,
        "canonical_projection_identities": identities,
        "canonical_timestamp_mismatch_count": canonical_timestamp_mismatch_count,
        "deterministic_mismatch_count": deterministic_mismatch_count,
        "equivalent_representation_identity_match": identity_match,
        "execution_status": "PASS" if passed else "FAIL",
        "imported_prohibited_modules": imported_prohibited_modules,
        "input_mutation_count": input_mutation_count,
        "projection_integration_cases": "PASS" if passed else "FAIL",
        "safety_counters": safety_counters,
        "safety_mismatch_count": safety_mismatch_count,
    }
    deterministic_summary_sha256 = hashlib.sha256(
        _canonical_json(summary_core).encode("utf-8")
    ).hexdigest()
    return {
        **summary_core,
        "deterministic_summary_sha256": deterministic_summary_sha256,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FR-Prep-B2e evidence runner with fail-closed explicit modes"
    )
    parser.add_argument(
        "--projection-only-fixture",
        type=Path,
        help="run only the supplied synthetic timestamp projection fixture",
    )
    args = parser.parse_args()
    if args.projection_only_fixture is None:
        parser.error(
            "fail closed: an explicit mode is required; real FJ binding is unavailable"
        )
    return args


def main() -> int:
    args = _parse_args()
    with args.projection_only_fixture.open("r", encoding="utf-8") as fixture_file:
        fixture = json.load(fixture_file)
    summary = _run_projection_fixture(fixture)
    print(_canonical_json(summary))
    return 0 if summary["execution_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
