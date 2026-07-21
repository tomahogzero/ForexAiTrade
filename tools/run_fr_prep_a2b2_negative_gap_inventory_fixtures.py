#!/usr/bin/env python3
"""Run A2b-2 synthetic inventory failures and all frozen A1/A2 regressions."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gap_policy_adapter import (
    A2B1_VALIDATION_CODES, A2B2_VALIDATION_CODES, GapPolicyValidationError,
    canonical_bytes, validate_gap_policy_data,
)
from run_fr_prep_a2_gap_policy_positive_fixtures import (
    A1B1_GOLDEN_SHA256, A1B2_GOLDEN_SHA256, POSITIVE_GOLDEN_SHA256,
    run_a1_regression, run_gap_suite,
)
from run_fr_prep_a2b1_negative_gap_policy_fixtures import run_negative as run_a2b1

A2_GOLDEN_SHA256 = "7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff"
A2B1_GOLDEN_SHA256 = "e12d040363487ac48f972f86a976aacc72305940a08ce92c1d162544a89357a7"


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_failure(code: str | None, expected: str) -> dict:
    status = "UNEXPECTED_PASS" if code is None else (
        "EXPECTED_FAILURE" if code == expected else "WRONG_FAILURE"
    )
    return {
        "status": status,
        "validation_code": code,
        "expected_code": expected,
        "broker_history_completeness": "NOT_PROVEN",
    }


def run_a2b2(cases: dict, positive_root: Path) -> dict:
    base = json.loads((positive_root / cases["base_positive_manifest"]).read_text(encoding="utf-8"))
    outputs = {}
    for case in cases["cases"]:
        manifest = copy.deepcopy(base)
        manifest.update(case["manifest_updates"])
        try:
            validate_gap_policy_data(manifest, positive_root)
        except GapPolicyValidationError as exc:
            outputs[case["name"]] = canonical_failure(exc.code, case["expected_code"])
        else:
            outputs[case["name"]] = canonical_failure(None, case["expected_code"])
    return outputs


def registry_entry_map(registry: dict) -> dict:
    return {entry["code"]: entry for entry in registry["codes"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--positive-root", required=True)
    parser.add_argument("--a2b1-root", required=True)
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--a2b1-registry", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    positive_root = Path(args.positive_root)
    a2b1_root = Path(args.a2b1_root)
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    first, second = run_a2b2(cases, positive_root), run_a2b2(cases, positive_root)
    expected_path = Path(args.expected)
    if args.write_expected:
        expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    known_codes = A2B1_VALIDATION_CODES | A2B2_VALIDATION_CODES
    unexpected_pass_count = sum(item["status"] == "UNEXPECTED_PASS" for item in first.values())
    wrong_code_count = sum(item["status"] == "WRONG_FAILURE" for item in first.values())
    unknown_code_count = sum(item["validation_code"] not in known_codes for item in first.values())
    mismatch_count = 0 if first == expected else 1
    replay_identical = canonical_bytes(first) == canonical_bytes(second)
    encoded = canonical_bytes(first).decode("ascii").lower()
    deterministic_text = all(token not in encoded for token in (
        "traceback", "generated_at", "runtime_timestamp", "run_timestamp",
        "current_timestamp", "errno", "winerror", "no such file", "cannot find",
        "jsondecodeerror", "appdata", "temp", "tmp",
    ))

    complete_registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    prior_registry = json.loads(Path(args.a2b1_registry).read_text(encoding="utf-8"))
    complete_entries = registry_entry_map(complete_registry)
    prior_entries = registry_entry_map(prior_registry)
    prior_registry_unchanged = all(complete_entries.get(code) == entry for code, entry in prior_entries.items())
    case_names = {case["name"] for case in cases["cases"]}
    new_registry_fixtures = set()
    for code in A2B2_VALIDATION_CODES:
        proving = complete_entries[code]["fixture"]
        new_registry_fixtures.update(proving if isinstance(proving, list) else [proving])
    registry_complete = (
        set(complete_entries) == known_codes
        and prior_registry_unchanged
        and new_registry_fixtures == case_names
    )

    a1_first, a1_second = run_a1_regression(repo_root), run_a1_regression(repo_root)
    a1_hashes = {name: digest(value) for name, value in a1_first.items()}
    a1_expected_hashes = {
        "a1a": POSITIVE_GOLDEN_SHA256,
        "a1b1": A1B1_GOLDEN_SHA256,
        "a1b2": A1B2_GOLDEN_SHA256,
    }
    a2_first, a2_second = run_gap_suite(positive_root), run_gap_suite(positive_root)
    a2_expected = json.loads((positive_root / "expected_outputs.json").read_text(encoding="utf-8"))
    a2b1_cases = json.loads((a2b1_root / "negative_cases.json").read_text(encoding="utf-8"))
    a2b1_first = run_a2b1(a2b1_cases, positive_root, a2b1_root)
    a2b1_second = run_a2b1(a2b1_cases, positive_root, a2b1_root)
    a2b1_expected = json.loads((a2b1_root / "expected_failures.json").read_text(encoding="utf-8"))

    checks = (
        not unexpected_pass_count, not wrong_code_count, not unknown_code_count,
        not mismatch_count, replay_identical, deterministic_text, registry_complete,
        len(first) == 20, len(A2B2_VALIDATION_CODES) == 20,
        a1_first == a1_second, a1_hashes == a1_expected_hashes,
        a2_first == a2_second == a2_expected, digest(a2_first) == A2_GOLDEN_SHA256,
        a2_first["A_valid_minimal_generic_accepted"]
        == a2_first["H_valid_runtime_path_relocation"],
        a2b1_first == a2b1_second == a2b1_expected,
        digest(a2b1_first) == A2B1_GOLDEN_SHA256,
        A2B1_VALIDATION_CODES == set(prior_entries),
    )
    if not all(checks):
        raise SystemExit("FR_PREP_A2B2_NEGATIVE_GAP_INVENTORY_VALIDATION_FAILED")

    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A2B2_GAP_VALIDATION_COMPLETE",
        "decision": "FR_PREP_A2B2_PASS_GAP_VALIDATION_COMPLETE",
        "negative_fixture_count": 20,
        "negative_fixtures_passed": 20,
        "a2b1_validation_code_count": len(A2B1_VALIDATION_CODES),
        "a2b2_validation_code_count": len(A2B2_VALIDATION_CODES),
        "complete_a2_validation_code_count": len(known_codes),
        "run_1_sha256": digest(first),
        "run_2_sha256": digest(second),
        "golden_expected_sha256": digest(expected),
        "canonical_outputs_byte_identical": replay_identical,
        "unexpected_pass_count": unexpected_pass_count,
        "wrong_validation_code_count": wrong_code_count,
        "unknown_validation_code_count": unknown_code_count,
        "mismatch_count": mismatch_count,
        "runtime_and_platform_dependent_text_absent": deterministic_text,
        "validation_registry_complete": registry_complete,
        "prior_a2b1_registry_entries_unchanged": prior_registry_unchanged,
        "a1a_positive_fixtures": "4/4 PASS",
        "a1b1_negative_fixtures": "9/9 PASS",
        "a1b2_negative_fixtures": "13/13 PASS",
        "a1a_golden_sha256": a1_hashes["a1a"],
        "a1b1_golden_sha256": a1_hashes["a1b1"],
        "a1b2_golden_sha256": a1_hashes["a1b2"],
        "a1_complete_replay_byte_identical": canonical_bytes(a1_first) == canonical_bytes(a1_second),
        "a2_positive_fixtures": "8/8 PASS",
        "a2_positive_golden_sha256": digest(a2_first),
        "a2_positive_replay_byte_identical": canonical_bytes(a2_first) == canonical_bytes(a2_second),
        "a2_runtime_path_relocation_output_identical": True,
        "a2b1_negative_fixtures": "18/18 PASS",
        "a2b1_golden_sha256": digest(a2b1_first),
        "a2b1_replay_byte_identical": canonical_bytes(a2b1_first) == canonical_bytes(a2b1_second),
        "broker_history_completeness": "NOT_PROVEN",
        "detector_executed": False, "fi_fixtures_executed": False,
        "fj_population_replayed": False, "holdout_preflight_executed": False,
        "real_fq_inventory_loaded": False, "historical_population_created": False,
        "events_created": False, "atr_events_created": False,
        "tp_sl_calculated": False, "outcomes_created": False,
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False, "order_logic_status": "NOT_APPROVED",
        "candidate_status": "NOT_READY_FOR_ORDER_LOGIC",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "checkpoint_fr_prep_a2b2_test_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
