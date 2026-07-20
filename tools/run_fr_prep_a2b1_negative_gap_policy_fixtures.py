#!/usr/bin/env python3
"""Run A2b-1 negative gap-contract fixtures plus frozen A1/A2 regressions."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gap_policy_adapter import (
    A2B1_VALIDATION_CODES, GapPolicyValidationError, canonical_bytes,
    validate_gap_policy, validate_gap_policy_data,
)
from historical_source_adapter import A1B1_VALIDATION_CODES, A1B2_VALIDATION_CODES
from run_fr_prep_a2_gap_policy_positive_fixtures import (
    A1B1_FROZEN_CODES, A1B2_FROZEN_CODES, A1B1_GOLDEN_SHA256,
    A1B2_GOLDEN_SHA256, POSITIVE_GOLDEN_SHA256, run_a1_regression,
    run_gap_suite,
)

A2_POSITIVE_GOLDEN_SHA256 = "7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff"


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


def run_negative(
    cases: dict, positive_root: Path, negative_root: Path,
) -> dict:
    base = json.loads((positive_root / cases["base_positive_manifest"]).read_text(encoding="utf-8"))
    outputs = {}
    for case in cases["cases"]:
        try:
            if case["mode"] == "manifest_path":
                validate_gap_policy(negative_root / case["manifest_path"])
            else:
                manifest = copy.deepcopy(base)
                manifest.update(case.get("manifest_updates", {}))
                for field in case.get("remove_manifest_fields", []):
                    manifest.pop(field, None)
                validate_gap_policy_data(manifest, positive_root)
        except GapPolicyValidationError as exc:
            outputs[case["name"]] = canonical_failure(exc.code, case["expected_code"])
        else:
            outputs[case["name"]] = canonical_failure(None, case["expected_code"])
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--positive-root", required=True)
    parser.add_argument("--negative-root", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    positive_root = Path(args.positive_root)
    negative_root = Path(args.negative_root)
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    first = run_negative(cases, positive_root, negative_root)
    second = run_negative(cases, positive_root, negative_root)
    expected_path = Path(args.expected)
    if args.write_expected:
        expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    encoded = canonical_bytes(first).decode("ascii").lower()
    unexpected_pass_count = sum(item["status"] == "UNEXPECTED_PASS" for item in first.values())
    wrong_code_count = sum(item["status"] == "WRONG_FAILURE" for item in first.values())
    unknown_code_count = sum(
        item["validation_code"] not in A2B1_VALIDATION_CODES for item in first.values()
    )
    mismatch_count = 0 if first == expected else 1
    replay_identical = canonical_bytes(first) == canonical_bytes(second)
    canonical_fields_only = all(set(item) == {
        "status", "validation_code", "expected_code", "broker_history_completeness",
    } for item in first.values())
    tracebacks_absent = "traceback" not in encoded
    runtime_timestamps_absent = all(token not in encoded for token in (
        "generated_at", "runtime_timestamp", "run_timestamp", "current_timestamp",
    ))
    platform_text_absent = all(token not in encoded for token in (
        "errno", "winerror", "no such file", "cannot find", "jsondecodeerror",
    ))

    registry_codes = {item["code"] for item in registry["codes"]}
    registry_fixtures = set()
    for item in registry["codes"]:
        fixtures = item["fixture"] if isinstance(item["fixture"], list) else [item["fixture"]]
        registry_fixtures.update(fixtures)
    case_names = {case["name"] for case in cases["cases"]}

    a2_first, a2_second = run_gap_suite(positive_root), run_gap_suite(positive_root)
    a2_expected = json.loads((positive_root / "expected_outputs.json").read_text(encoding="utf-8"))
    a1_first, a1_second = run_a1_regression(repo_root), run_a1_regression(repo_root)
    a1_hashes = {name: digest(value) for name, value in a1_first.items()}
    expected_a1_hashes = {
        "a1a": POSITIVE_GOLDEN_SHA256,
        "a1b1": A1B1_GOLDEN_SHA256,
        "a1b2": A1B2_GOLDEN_SHA256,
    }
    existing_codes_unchanged = (
        A1B1_VALIDATION_CODES == A1B1_FROZEN_CODES
        and A1B2_VALIDATION_CODES == A1B2_FROZEN_CODES
    )
    checks = (
        not unexpected_pass_count, not wrong_code_count, not unknown_code_count,
        not mismatch_count, replay_identical, canonical_fields_only,
        tracebacks_absent, runtime_timestamps_absent, platform_text_absent,
        registry_codes == A2B1_VALIDATION_CODES,
        registry_fixtures == case_names,
        a2_first == a2_expected, a2_first == a2_second,
        digest(a2_first) == A2_POSITIVE_GOLDEN_SHA256,
        a2_first["A_valid_minimal_generic_accepted"]
        == a2_first["H_valid_runtime_path_relocation"],
        a1_first == a1_second, a1_hashes == expected_a1_hashes,
        existing_codes_unchanged,
    )
    if not all(checks):
        raise SystemExit("FR_PREP_A2B1_NEGATIVE_GAP_CONTRACT_VALIDATION_FAILED")

    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A2B1_NEGATIVE_GAP_CONTRACT_VALIDATION",
        "decision": "FR_PREP_A2B1_PASS_NEGATIVE_GAP_CONTRACT_VALIDATION",
        "negative_fixture_count": len(first),
        "negative_fixtures_passed": len(first),
        "validation_code_count": len(A2B1_VALIDATION_CODES),
        "run_1_sha256": digest(first),
        "run_2_sha256": digest(second),
        "golden_expected_sha256": digest(expected),
        "canonical_outputs_byte_identical": replay_identical,
        "unexpected_pass_count": unexpected_pass_count,
        "wrong_validation_code_count": wrong_code_count,
        "unknown_validation_code_count": unknown_code_count,
        "mismatch_count": mismatch_count,
        "canonical_fields_only": canonical_fields_only,
        "canonical_tracebacks_absent": tracebacks_absent,
        "runtime_timestamps_absent": runtime_timestamps_absent,
        "platform_dependent_exception_text_absent": platform_text_absent,
        "validation_registry_complete": True,
        "a1a_positive_fixtures": "4/4 PASS",
        "a1b1_negative_fixtures": "9/9 PASS",
        "a1b2_negative_fixtures": "13/13 PASS",
        "a1a_golden_sha256": a1_hashes["a1a"],
        "a1b1_golden_sha256": a1_hashes["a1b1"],
        "a1b2_golden_sha256": a1_hashes["a1b2"],
        "a1_validation_codes_unchanged": existing_codes_unchanged,
        "a2_positive_fixtures": "8/8 PASS",
        "a2_positive_golden_sha256": digest(a2_first),
        "a2_positive_replay_byte_identical": canonical_bytes(a2_first) == canonical_bytes(a2_second),
        "a2_runtime_path_relocation_output_identical": True,
        "broker_history_completeness": "NOT_PROVEN",
        "detector_executed": False, "fi_fixtures_executed": False,
        "fj_population_replayed": False, "holdout_preflight_executed": False,
        "historical_population_created": False, "events_created": False,
        "atr_events_created": False, "tp_sl_calculated": False,
        "outcomes_created": False, "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False, "order_logic_status": "NOT_APPROVED",
        "candidate_status": "NOT_READY_FOR_ORDER_LOGIC",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "checkpoint_fr_prep_a2b1_test_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
