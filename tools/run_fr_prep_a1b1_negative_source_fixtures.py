#!/usr/bin/env python3
"""Run only FR-Prep-A1b-1 negative source validation and A1a regression."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from historical_source_adapter import (
    A1B1_VALIDATION_CODES, AdapterValidationError, canonical_bytes,
    validate_manifest_data,
)
from run_fr_prep_a1a_source_adapter_fixtures import run_suite

POSITIVE_GOLDEN_SHA256 = "717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b"


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def run_negative(cases: dict, positive_root: Path) -> dict:
    base = json.loads((positive_root / cases["base_positive_manifest"]).read_text(encoding="utf-8"))
    outputs = {}
    for case in cases["cases"]:
        manifest = copy.deepcopy(base)
        manifest["sources"][0].update(case["source_updates"])
        try:
            validate_manifest_data(manifest, positive_root)
        except AdapterValidationError as exc:
            outputs[case["name"]] = {
                "status": "EXPECTED_FAILURE" if exc.code == case["expected_code"] else "WRONG_FAILURE",
                "validation_code": exc.code,
                "expected_code": case["expected_code"],
                "broker_history_completeness": "NOT_PROVEN",
            }
        else:
            outputs[case["name"]] = {
                "status": "UNEXPECTED_PASS", "validation_code": None,
                "expected_code": case["expected_code"],
                "broker_history_completeness": "NOT_PROVEN",
            }
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-root", required=True)
    parser.add_argument("--positive-expected", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--negative-expected", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    positive_root = Path(args.positive_root)
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    first = run_negative(cases, positive_root)
    second = run_negative(cases, positive_root)
    negative_expected_path = Path(args.negative_expected)
    if args.write_expected:
        negative_expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    negative_expected = json.loads(negative_expected_path.read_text(encoding="utf-8"))
    negative_mismatch_count = 0 if first == negative_expected else 1
    negative_replay_identical = canonical_bytes(first) == canonical_bytes(second)
    unexpected_pass_count = sum(item["status"] == "UNEXPECTED_PASS" for item in first.values())
    wrong_failure_count = sum(item["status"] == "WRONG_FAILURE" for item in first.values())
    unknown_code_count = sum(item["validation_code"] not in A1B1_VALIDATION_CODES for item in first.values())
    positive = run_suite(positive_root)
    positive_expected = json.loads(Path(args.positive_expected).read_text(encoding="utf-8"))
    positive_hash = digest(positive)
    positive_mismatch_count = 0 if positive == positive_expected else 1
    relocation_identical = (
        positive["A_valid_minimal_generic_manifest"]
        == positive["D_valid_runtime_path_relocation"]
    )
    encoded_failures = canonical_bytes(first).decode("ascii").lower()
    tracebacks_absent = "traceback" not in encoded_failures
    runtime_timestamps_absent = all(
        token not in encoded_failures
        for token in ("generated_at", "runtime_timestamp", "run_timestamp", "current_timestamp")
    )
    paths_absent = all(
        set(item) == {"status", "validation_code", "expected_code", "broker_history_completeness"}
        for item in first.values()
    )
    if any((
        negative_mismatch_count, not negative_replay_identical, unexpected_pass_count,
        wrong_failure_count, unknown_code_count, positive_mismatch_count,
        positive_hash != POSITIVE_GOLDEN_SHA256, not relocation_identical,
        not tracebacks_absent, not runtime_timestamps_absent, not paths_absent,
    )):
        raise SystemExit("FR_PREP_A1B1_FIXTURE_VALIDATION_FAILED")
    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A1B1_NEGATIVE_SOURCE_VALIDATION",
        "negative_fixture_count": len(first),
        "negative_fixtures_passed": len(first) - wrong_failure_count - unexpected_pass_count,
        "negative_run_1_sha256": digest(first),
        "negative_run_2_sha256": digest(second),
        "negative_golden_sha256": digest(negative_expected),
        "failure_outputs_byte_identical": negative_replay_identical,
        "unexpected_pass_count": unexpected_pass_count,
        "wrong_failure_count": wrong_failure_count,
        "unknown_validation_code_count": unknown_code_count,
        "mismatch_count": negative_mismatch_count,
        "canonical_tracebacks_absent": tracebacks_absent,
        "runtime_timestamps_absent": runtime_timestamps_absent,
        "canonical_paths_absent": paths_absent,
        "positive_fixture_count": len(positive),
        "positive_fixtures_passed": len(positive) if not positive_mismatch_count else 0,
        "positive_golden_sha256": positive_hash,
        "positive_mismatch_count": positive_mismatch_count,
        "runtime_path_relocation_output_identical": relocation_identical,
        "broker_history_completeness": "NOT_PROVEN",
        "detector_executed": False, "events_created": False, "outcomes_created": False,
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False, "order_logic_status": "NOT_APPROVED",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "checkpoint_fr_prep_a1b1_test_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
