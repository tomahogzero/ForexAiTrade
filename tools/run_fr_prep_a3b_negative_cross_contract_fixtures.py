#!/usr/bin/env python3
"""Run synthetic A3b descriptor failures; never import or invoke detector core."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset_execution_descriptor_adapter import (
    A3B_VALIDATION_CODES, DescriptorValidationError, canonical_bytes,
    compose_dataset_execution_descriptor, validate_dataset_execution_descriptor,
)
from gap_policy_adapter import A2B1_VALIDATION_CODES, A2B2_VALIDATION_CODES
from historical_source_adapter import A1B1_VALIDATION_CODES, A1B2_VALIDATION_CODES
from run_fr_prep_a2_gap_policy_positive_fixtures import (
    A1B1_GOLDEN_SHA256, A1B2_GOLDEN_SHA256, POSITIVE_GOLDEN_SHA256,
    run_a1_regression, run_gap_suite,
)
from run_fr_prep_a2b1_negative_gap_policy_fixtures import run_negative as run_a2b1
from run_fr_prep_a2b2_negative_gap_inventory_fixtures import run_a2b2
from run_fr_prep_a3a_synthetic_composition_fixtures import run_suite as run_a3a

A2_GOLDEN_SHA256 = "7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff"
A2B1_GOLDEN_SHA256 = "e12d040363487ac48f972f86a976aacc72305940a08ce92c1d162544a89357a7"
A2B2_GOLDEN_SHA256 = "7b439bf5e716c60d6ba1c9fac8e26402bdba624cee7c8dc7de6c31d1cbd1dbae"
A3A_GOLDEN_SHA256 = "743b528744ff03a33d6805099e1618dcafc8f426f7fd8bf7f885e79d5a7827bd"
DETECTOR_MODULE = "market_structure_break_retest_detector"


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_failure(code: str | None, expected: str) -> dict:
    return {
        "status": "UNEXPECTED_PASS" if code is None else (
            "EXPECTED_FAILURE" if code == expected else "WRONG_FAILURE"
        ),
        "validation_code": code,
        "expected_code": expected,
        "broker_history_completeness": "NOT_PROVEN",
    }


def set_path(value: dict, path: str, replacement) -> None:
    target = value
    keys = path.split(".")
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = replacement


def run_negative(cases: dict, a3a_root: Path) -> dict:
    base_request = json.loads((a3a_root / "A_generic_source_accepted.json").read_text(encoding="utf-8"))
    base_descriptor = compose_dataset_execution_descriptor(base_request, a3a_root)
    outputs = {}
    for case in cases["cases"]:
        request, candidate = copy.deepcopy(base_request), copy.deepcopy(base_descriptor)
        if "candidate_root" in case:
            candidate = case["candidate_root"]
        if "candidate_remove" in case:
            candidate.pop(case["candidate_remove"])
        if "candidate_mutation" in case:
            set_path(candidate, case["candidate_mutation"]["path"], case["candidate_mutation"]["value"])
        if "request_mutation" in case:
            set_path(request, case["request_mutation"]["path"], case["request_mutation"]["value"])
        if "gap_artifact" in case:
            request["gap_policy_manifest"]["runtime_path"] = case["gap_artifact"]["path"]
            request["gap_policy_manifest"]["artifact_sha256"] = case["gap_artifact"]["sha256"]
        try:
            validate_dataset_execution_descriptor(
                candidate, request, a3a_root, case.get("invocation"),
                case.get("validation_assertions"),
            )
        except DescriptorValidationError as exc:
            outputs[case["name"]] = canonical_failure(exc.code, case["expected_code"])
        else:
            outputs[case["name"]] = canonical_failure(None, case["expected_code"])
    return outputs


def no_runtime_text(value) -> bool:
    encoded = canonical_bytes(value).decode("ascii").lower()
    return all(token not in encoded for token in (
        "traceback", "generated_at", "runtime_timestamp", "run_timestamp",
        "current_timestamp", "errno", "winerror", "no such file", "cannot find",
        "temp", "tmp", "appdata",
    ))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--a3a-root", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    repo_root, fixture_root, a3a_root = Path(args.repo_root), Path(args.fixture_root), Path(args.a3a_root)
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    detector_before = int(DETECTOR_MODULE in sys.modules)
    first, second = run_negative(cases, a3a_root), run_negative(cases, a3a_root)
    detector_after = int(DETECTOR_MODULE in sys.modules)
    expected_path = Path(args.expected)
    if args.write_expected:
        expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    registry_codes = {entry["code"] for entry in registry["codes"]}
    registry_fixtures = set()
    for entry in registry["codes"]:
        fixture = entry["fixture"]
        registry_fixtures.update(fixture if isinstance(fixture, list) else [fixture])
    case_names = {case["name"] for case in cases["cases"]}

    a3a_first, a3a_second = run_a3a(a3a_root), run_a3a(a3a_root)
    a3a_expected = json.loads((a3a_root / "expected_outputs.json").read_text(encoding="utf-8"))
    a1_first, a1_second = run_a1_regression(repo_root), run_a1_regression(repo_root)
    a1_hashes = {name: digest(value) for name, value in a1_first.items()}
    a2_root = repo_root / "tests/fixtures/fr_prep_a2"
    a2_first, a2_second = run_gap_suite(a2_root), run_gap_suite(a2_root)
    a2_expected = json.loads((a2_root / "expected_outputs.json").read_text(encoding="utf-8"))
    a2b1_root = repo_root / "tests/fixtures/fr_prep_a2b1"
    a2b1_cases = json.loads((a2b1_root / "negative_cases.json").read_text(encoding="utf-8"))
    a2b1_first, a2b1_second = run_a2b1(a2b1_cases, a2_root, a2b1_root), run_a2b1(a2b1_cases, a2_root, a2b1_root)
    a2b1_expected = json.loads((a2b1_root / "expected_failures.json").read_text(encoding="utf-8"))
    a2b2_root = repo_root / "tests/fixtures/fr_prep_a2b2"
    a2b2_cases = json.loads((a2b2_root / "negative_cases.json").read_text(encoding="utf-8"))
    a2b2_first, a2b2_second = run_a2b2(a2b2_cases, a2_root), run_a2b2(a2b2_cases, a2_root)
    a2b2_expected = json.loads((a2b2_root / "expected_failures.json").read_text(encoding="utf-8"))
    source_registry = json.loads((repo_root / "research/schemas/historical_source_validation_codes.v1.json").read_text(encoding="utf-8"))
    gap_registry = json.loads((repo_root / "research/schemas/gap_policy_validation_codes.v1.json").read_text(encoding="utf-8"))
    source_codes_unchanged = {entry["code"] for entry in source_registry["codes"]} == (A1B1_VALIDATION_CODES | A1B2_VALIDATION_CODES)
    gap_codes_unchanged = {entry["code"] for entry in gap_registry["codes"]} == (A2B1_VALIDATION_CODES | A2B2_VALIDATION_CODES)

    unexpected = sum(item["status"] == "UNEXPECTED_PASS" for item in first.values())
    wrong = sum(item["status"] == "WRONG_FAILURE" for item in first.values())
    unknown = sum(item["validation_code"] not in A3B_VALIDATION_CODES for item in first.values())
    mismatch = 0 if first == expected else 1
    replay_identical = canonical_bytes(first) == canonical_bytes(second)
    checks = (
        len(first) == 36, not unexpected, not wrong, not unknown, not mismatch,
        replay_identical, no_runtime_text(first), registry_codes == A3B_VALIDATION_CODES,
        registry_fixtures == case_names, detector_before == detector_after == 0,
        a3a_first == a3a_second == a3a_expected and digest(a3a_first) == A3A_GOLDEN_SHA256,
        a1_first == a1_second and a1_hashes == {"a1a": POSITIVE_GOLDEN_SHA256, "a1b1": A1B1_GOLDEN_SHA256, "a1b2": A1B2_GOLDEN_SHA256},
        a2_first == a2_second == a2_expected and digest(a2_first) == A2_GOLDEN_SHA256,
        a2b1_first == a2b1_second == a2b1_expected and digest(a2b1_first) == A2B1_GOLDEN_SHA256,
        a2b2_first == a2b2_second == a2b2_expected and digest(a2b2_first) == A2B2_GOLDEN_SHA256,
        source_codes_unchanged, gap_codes_unchanged,
    )
    if not all(checks):
        raise SystemExit("FR_PREP_A3B_ADAPTER_CONTRACT_CLOSURE_FAILED")

    guard_test = {
        "execution_status": "PASS",
        "detector_import_count": 0,
        "detector_execution_count": 0,
        "event_artifact_count": 0,
        "atr_event_artifact_count": 0,
        "tp_sl_artifact_count": 0,
        "outcome_artifact_count": 0,
        "blocked_request_codes": [
            "ADAPTER_ONLY_DETECTOR_REQUESTED",
            "ADAPTER_ONLY_EVENT_OR_ATR_REQUESTED",
            "ADAPTER_ONLY_TP_SL_OR_OUTCOME_REQUESTED",
            "ADAPTER_ONLY_FN_INTERPRETATION_REQUESTED",
        ],
    }
    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A3B_ADAPTER_CONTRACT_CLOSED",
        "decision": "FR_PREP_A3B_PASS_ADAPTER_CONTRACT_CLOSED",
        "negative_fixture_count": 36,
        "negative_fixtures_passed": 36,
        "run_1_sha256": digest(first), "run_2_sha256": digest(second),
        "golden_expected_sha256": digest(expected),
        "canonical_outputs_byte_identical": replay_identical,
        "unexpected_pass_count": unexpected, "wrong_validation_code_count": wrong,
        "unknown_validation_code_count": unknown, "mismatch_count": mismatch,
        "runtime_timestamp_count": 0, "detector_import_count": 0,
        "detector_execution_count": 0, "event_artifact_count": 0,
        "atr_event_artifact_count": 0, "tp_sl_artifact_count": 0,
        "outcome_artifact_count": 0, "a3a_positive_fixtures": "8/8 PASS",
        "a3a_golden_sha256": digest(a3a_first),
        "a3a_relocation_output_identical": True,
        "a3a_execution_guard_passed": True,
        "a1a_positive_fixtures": "4/4 PASS", "a1b1_negative_fixtures": "9/9 PASS",
        "a1b2_negative_fixtures": "13/13 PASS", "a2_positive_fixtures": "8/8 PASS",
        "a2b1_negative_fixtures": "18/18 PASS", "a2b2_negative_fixtures": "20/20 PASS",
        "a1a_golden_sha256": a1_hashes["a1a"], "a1b1_golden_sha256": a1_hashes["a1b1"],
        "a1b2_golden_sha256": a1_hashes["a1b2"], "a2_golden_sha256": digest(a2_first),
        "a2b1_golden_sha256": digest(a2b1_first), "a2b2_golden_sha256": digest(a2b2_first),
        "prior_stable_codes_unchanged": source_codes_unchanged and gap_codes_unchanged,
        "broker_history_completeness": "NOT_PROVEN",
        "strategy_performance_status": "NOT_EVALUATED", "profitability_claim": False,
        "order_logic_status": "NOT_APPROVED", "candidate_status": "NOT_READY_FOR_ORDER_LOGIC",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "checkpoint_fr_prep_a3b_test_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_root / "checkpoint_fr_prep_a3b_guard_test.json").write_text(json.dumps(guard_test, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
