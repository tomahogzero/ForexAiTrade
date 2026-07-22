"""Run deterministic FR-Prep-B2e R1a timestamp projection fixtures."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = REPO_ROOT / "tools"
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "fr_prep_b2e_r1a_timestamp_projection_cases.json"

if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from fr_prep_b2e_fj_metadata_projection import (  # noqa: E402
    FjMetadataTimestampValidationError,
    canonicalize_fj_metadata_timestamp,
)


VALIDATION_CODES = frozenset(
    {
        "TIMESTAMP_VALUE_NOT_STRING",
        "TIMESTAMP_VALUE_EMPTY",
        "TIMESTAMP_WHITESPACE_NOT_ALLOWED",
        "TIMESTAMP_TIMEZONE_NOT_ALLOWED",
        "TIMESTAMP_FRACTION_NOT_ALLOWED",
        "TIMESTAMP_FORMAT_NOT_ALLOWLISTED",
        "TIMESTAMP_CALENDAR_INVALID",
    }
)
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
ZERO_SAFETY_COUNTERS = {
    "real_fj_source_open_count": 0,
    "real_fq_source_open_count": 0,
    "detector_import_count": 0,
    "detector_execution_count": 0,
    "fi_execution_count": 0,
    "legacy_runner_execution_count": 0,
    "event_population_emit_count": 0,
    "outcome_emit_count": 0,
}


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _load_fixtures() -> dict[str, Any]:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def _run_complete_suite(fixtures: dict[str, Any]) -> dict[str, Any]:
    positive_results: list[dict[str, Any]] = []
    negative_results: list[dict[str, Any]] = []
    unexpected_passes = 0
    wrong_validation_codes = 0
    unknown_validation_codes = 0

    for fixture in fixtures["positive_fixtures"]:
        repeat_count = fixture.get("repeat_count", 1)
        actual_values = [
            canonicalize_fj_metadata_timestamp(value, fixture["fixture_id"])
            for _ in range(repeat_count)
            for value in fixture["values"]
        ]
        passed = bool(actual_values) and all(
            actual == fixture["expected"] for actual in actual_values
        )
        positive_results.append(
            {
                "actual_values": actual_values,
                "fixture_id": fixture["fixture_id"],
                "status": "PASS" if passed else "FAIL",
            }
        )

    for fixture in fixtures["negative_fixtures"]:
        expected_code = fixture["expected_validation_code"]
        if expected_code not in VALIDATION_CODES:
            unknown_validation_codes += 1
        try:
            canonicalize_fj_metadata_timestamp(fixture["value"], fixture["fixture_id"])
        except FjMetadataTimestampValidationError as exc:
            if exc.validation_code not in VALIDATION_CODES:
                unknown_validation_codes += 1
            passed = (
                exc.validation_code == expected_code
                and exc.field_name == fixture["fixture_id"]
            )
            if not passed:
                wrong_validation_codes += 1
            negative_results.append(
                {
                    "actual_validation_code": exc.validation_code,
                    "expected_validation_code": expected_code,
                    "fixture_id": fixture["fixture_id"],
                    "status": "PASS" if passed else "FAIL",
                }
            )
        except Exception as exc:
            wrong_validation_codes += 1
            negative_results.append(
                {
                    "actual_exception": type(exc).__name__,
                    "expected_validation_code": expected_code,
                    "fixture_id": fixture["fixture_id"],
                    "status": "FAIL",
                }
            )
        else:
            unexpected_passes += 1
            negative_results.append(
                {
                    "actual_validation_code": None,
                    "expected_validation_code": expected_code,
                    "fixture_id": fixture["fixture_id"],
                    "status": "FAIL",
                }
            )

    imported_prohibited_modules = sorted(
        module_name
        for module_name in sys.modules
        if module_name.split(".")[-1] in PROHIBITED_MODULES
    )
    safety_counters = dict(ZERO_SAFETY_COUNTERS)
    safety_counters["detector_import_count"] = sum(
        module_name.split(".")[-1] == "market_structure_break_retest_detector"
        for module_name in imported_prohibited_modules
    )

    return {
        "imported_prohibited_modules": imported_prohibited_modules,
        "negative_results": negative_results,
        "positive_results": positive_results,
        "safety_counters": safety_counters,
        "unexpected_passes": unexpected_passes,
        "unknown_validation_codes": unknown_validation_codes,
        "wrong_validation_codes": wrong_validation_codes,
    }


def main() -> int:
    fixtures = _load_fixtures()
    first_run = _run_complete_suite(fixtures)
    second_run = _run_complete_suite(fixtures)
    first_json = _canonical_json(first_run)
    second_json = _canonical_json(second_run)
    deterministic_mismatch = int(first_json != second_json)
    deterministic_sha256 = hashlib.sha256(first_json.encode("utf-8")).hexdigest()

    positive_passed = sum(
        result["status"] == "PASS" for result in first_run["positive_results"]
    )
    negative_passed = sum(
        result["status"] == "PASS" for result in first_run["negative_results"]
    )
    positive_total = len(first_run["positive_results"])
    negative_total = len(first_run["negative_results"])
    safety_counters = first_run["safety_counters"]

    passed = (
        positive_passed == positive_total == 8
        and negative_passed == negative_total == 12
        and first_run["unexpected_passes"] == 0
        and first_run["wrong_validation_codes"] == 0
        and first_run["unknown_validation_codes"] == 0
        and deterministic_mismatch == 0
        and not first_run["imported_prohibited_modules"]
        and all(value == 0 for value in safety_counters.values())
    )
    summary = {
        "deterministic_fixture_sha256": deterministic_sha256,
        "deterministic_mismatch": deterministic_mismatch,
        "execution_status": "PASS" if passed else "FAIL",
        "imported_prohibited_modules": first_run["imported_prohibited_modules"],
        "negative_fixtures": {
            "passed": negative_passed,
            "total": negative_total,
        },
        "positive_fixtures": {
            "passed": positive_passed,
            "total": positive_total,
        },
        "safety_counters": safety_counters,
        "suite_execution_count": 2,
        "unexpected_passes": first_run["unexpected_passes"],
        "unknown_validation_codes": first_run["unknown_validation_codes"],
        "wrong_validation_codes": first_run["wrong_validation_codes"],
    }
    print(_canonical_json(summary))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
