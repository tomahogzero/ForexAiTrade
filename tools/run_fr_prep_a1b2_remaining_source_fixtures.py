#!/usr/bin/env python3
"""Run FR-Prep-A1b-2 failures and the complete deterministic A1 regression."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from historical_source_adapter import (
    A1_VALIDATION_CODES, A1B1_VALIDATION_CODES, A1B2_VALIDATION_CODES,
    AdapterValidationError, canonical_bytes, validate_manifest_data,
)
from run_fr_prep_a1a_source_adapter_fixtures import run_suite
from run_fr_prep_a1b1_negative_source_fixtures import run_negative as run_a1b1

POSITIVE_GOLDEN_SHA256 = "717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b"
A1B1_GOLDEN_SHA256 = "97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8"
A1B1_FROZEN_CODES = frozenset({
    "SOURCE_PATH_MISSING", "SOURCE_SHA256_MISMATCH", "SOURCE_SIZE_MISMATCH",
    "MT5_TSV_SCHEMA_INVALID", "SOURCE_TIMESTAMP_UNPARSEABLE",
    "OHLC_NON_FINITE_OR_NON_POSITIVE", "OHLC_INCONSISTENT",
    "SOURCE_NOT_CHRONOLOGICAL", "SOURCE_ROW_COUNT_MISMATCH",
})


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_failure(code: str | None, expected: str) -> dict:
    status = "UNEXPECTED_PASS" if code is None else (
        "EXPECTED_FAILURE" if code == expected else "WRONG_FAILURE"
    )
    return {
        "status": status, "validation_code": code, "expected_code": expected,
        "broker_history_completeness": "NOT_PROVEN",
    }


def run_a1b2(cases: dict, positive_root: Path) -> dict:
    base = json.loads((positive_root / cases["base_positive_manifest"]).read_text(encoding="utf-8"))
    outputs = {}
    for case in cases["cases"]:
        manifest = copy.deepcopy(base)
        manifest.update(case.get("manifest_updates", {}))
        manifest["expected_timeline"].update(case.get("expected_timeline_updates", {}))
        for index, updates in case.get("source_updates", {}).items():
            manifest["sources"][int(index)].update(updates)
        manifest["sources"].extend(copy.deepcopy(case.get("append_sources", [])))
        try:
            validate_manifest_data(manifest, positive_root)
        except AdapterValidationError as exc:
            outputs[case["name"]] = canonical_failure(exc.code, case["expected_code"])
        else:
            outputs[case["name"]] = canonical_failure(None, case["expected_code"])
    return outputs


def failure_metrics(outputs: dict, known_codes: frozenset[str]) -> dict:
    encoded = canonical_bytes(outputs).decode("ascii").lower()
    return {
        "unexpected_pass_count": sum(item["status"] == "UNEXPECTED_PASS" for item in outputs.values()),
        "wrong_validation_code_count": sum(item["status"] == "WRONG_FAILURE" for item in outputs.values()),
        "unknown_validation_code_count": sum(item["validation_code"] not in known_codes for item in outputs.values()),
        "canonical_tracebacks_absent": "traceback" not in encoded,
        "runtime_timestamps_absent": all(token not in encoded for token in (
            "generated_at", "runtime_timestamp", "run_timestamp", "current_timestamp")),
        "canonical_paths_absent": all(set(item) == {
            "status", "validation_code", "expected_code", "broker_history_completeness"
        } for item in outputs.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-root", required=True)
    parser.add_argument("--positive-expected", required=True)
    parser.add_argument("--a1b1-cases", required=True)
    parser.add_argument("--a1b1-expected", required=True)
    parser.add_argument("--a1b2-cases", required=True)
    parser.add_argument("--a1b2-expected", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()

    positive_root = Path(args.positive_root)
    positive_expected = json.loads(Path(args.positive_expected).read_text(encoding="utf-8"))
    a1b1_cases = json.loads(Path(args.a1b1_cases).read_text(encoding="utf-8"))
    a1b1_expected = json.loads(Path(args.a1b1_expected).read_text(encoding="utf-8"))
    a1b2_cases = json.loads(Path(args.a1b2_cases).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))

    positive_1, positive_2 = run_suite(positive_root), run_suite(positive_root)
    a1b1_1, a1b1_2 = run_a1b1(a1b1_cases, positive_root), run_a1b1(a1b1_cases, positive_root)
    a1b2_1, a1b2_2 = run_a1b2(a1b2_cases, positive_root), run_a1b2(a1b2_cases, positive_root)
    a1b2_expected_path = Path(args.a1b2_expected)
    if args.write_expected:
        a1b2_expected_path.write_text(json.dumps(a1b2_1, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    a1b2_expected = json.loads(a1b2_expected_path.read_text(encoding="utf-8"))

    positive_hash = digest(positive_1)
    a1b1_hash = digest(a1b1_1)
    a1b2_hash = digest(a1b2_1)
    complete_1 = {"positive": positive_1, "a1b1": a1b1_1, "a1b2": a1b2_1}
    complete_2 = {"positive": positive_2, "a1b1": a1b1_2, "a1b2": a1b2_2}
    a1b2_metrics = failure_metrics(a1b2_1, A1B2_VALIDATION_CODES)
    registry_codes = {item["code"] for item in registry["codes"]}
    registry_fixtures = {item["fixture_proving_the_code"] for item in registry["codes"]}
    expected_registry_fixtures = {
        *(f"A1b-1/{item['name']}" for item in a1b1_cases["cases"]),
        *(f"A1b-2/{item['name']}" for item in a1b2_cases["cases"]),
    }
    checks = (
        positive_1 == positive_expected, positive_1 == positive_2,
        positive_hash == POSITIVE_GOLDEN_SHA256,
        positive_1["A_valid_minimal_generic_manifest"] == positive_1["D_valid_runtime_path_relocation"],
        a1b1_1 == a1b1_expected, a1b1_1 == a1b1_2,
        a1b1_hash == A1B1_GOLDEN_SHA256, A1B1_VALIDATION_CODES == A1B1_FROZEN_CODES,
        a1b2_1 == a1b2_expected, a1b2_1 == a1b2_2,
        all(value == 0 for key, value in a1b2_metrics.items() if key.endswith("count")),
        all(value for key, value in a1b2_metrics.items() if not key.endswith("count")),
        canonical_bytes(complete_1) == canonical_bytes(complete_2),
        registry_codes == A1_VALIDATION_CODES,
        registry_fixtures == expected_registry_fixtures,
        len({item["precedence"] for item in registry["codes"]}) == len(registry["codes"]),
    )
    if not all(checks):
        raise SystemExit("FR_PREP_A1B2_FIXTURE_VALIDATION_FAILED")

    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A1B2_SOURCE_VALIDATION_COMPLETE",
        "positive_fixture_count": len(positive_1), "positive_fixtures_passed": len(positive_1),
        "positive_golden_sha256": positive_hash, "positive_mismatch_count": 0,
        "runtime_path_relocation_output_identical": True,
        "a1b1_fixture_count": len(a1b1_1), "a1b1_fixtures_passed": len(a1b1_1),
        "a1b1_golden_sha256": a1b1_hash, "a1b1_mismatch_count": 0,
        "a1b1_validation_codes_unchanged": True,
        "a1b2_fixture_count": len(a1b2_1), "a1b2_fixtures_passed": len(a1b2_1),
        "a1b2_run_1_sha256": a1b2_hash, "a1b2_run_2_sha256": digest(a1b2_2),
        "a1b2_golden_sha256": digest(a1b2_expected), "a1b2_mismatch_count": 0,
        "a1b2_failure_outputs_byte_identical": True, **a1b2_metrics,
        "complete_a1_run_1_sha256": digest(complete_1),
        "complete_a1_run_2_sha256": digest(complete_2),
        "complete_a1_replay_byte_identical": True,
        "validation_code_count": len(A1_VALIDATION_CODES), "validation_registry_complete": True,
        "broker_history_completeness": "NOT_PROVEN",
        "detector_executed": False, "population_created": False,
        "events_created": False, "atr_events_created": False, "outcomes_created": False,
        "holdout_preflight_executed": False, "gap_policy_executed": False,
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False, "order_logic_status": "NOT_APPROVED",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "checkpoint_fr_prep_a1b2_test_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
