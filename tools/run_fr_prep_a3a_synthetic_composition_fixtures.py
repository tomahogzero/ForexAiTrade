#!/usr/bin/env python3
"""Run only synthetic A3a composition fixtures and frozen A1/A2 regressions."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset_execution_descriptor_adapter import (
    AdapterOnlyExecutionProhibited, AdapterValidationOnlyGuard, canonical_bytes,
    compose_dataset_execution_descriptor,
)
from run_fr_prep_a2_gap_policy_positive_fixtures import (
    A1B1_GOLDEN_SHA256, A1B2_GOLDEN_SHA256, POSITIVE_GOLDEN_SHA256,
    run_a1_regression, run_gap_suite,
)
from run_fr_prep_a2b1_negative_gap_policy_fixtures import run_negative as run_a2b1
from run_fr_prep_a2b2_negative_gap_inventory_fixtures import run_a2b2

A2_GOLDEN_SHA256 = "7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff"
A2B1_GOLDEN_SHA256 = "e12d040363487ac48f972f86a976aacc72305940a08ce92c1d162544a89357a7"
A2B2_GOLDEN_SHA256 = "7b439bf5e716c60d6ba1c9fac8e26402bdba624cee7c8dc7de6c31d1cbd1dbae"
FIXTURES = {
    "A_generic_source_accepted": "A_generic_source_accepted.json",
    "B_generic_source_unverified": "B_generic_source_unverified.json",
    "C_fp_source_fq_gaps": "C_fp_source_fq_gaps.json",
    "D_fj_source_eo_fj_gaps": "D_fj_source_eo_fj_gaps.json",
    "E_multiple_sources_mixed_gaps": "E_multiple_sources_mixed_gaps.json",
    "F_runtime_path_relocation": "F_runtime_path_relocation.json",
    "G_eo_fq_equivalent_semantics": "G_eo_fq_equivalent_semantics.json",
    "H_repeated_deterministic_composition": "H_repeated_deterministic_composition.json",
}


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def guard_result() -> dict:
    guard = AdapterValidationOnlyGuard()
    blocked = []
    for name in (
        "execute_detector", "emit_event", "emit_atr_event",
        "calculate_tp_sl", "emit_outcome",
    ):
        try:
            getattr(guard, name)()
        except AdapterOnlyExecutionProhibited as exc:
            if str(exc) == "ADAPTER_VALIDATION_ONLY_EXECUTION_PROHIBITED":
                blocked.append(name)
    return {
        "execution_mode": guard.execution_mode,
        "blocked_actions": blocked,
        "detector_execution_allowed": False,
        "outcome_execution_allowed": False,
    }


def run_suite(root: Path) -> dict:
    outputs = {}
    for name, relative in FIXTURES.items():
        request = json.loads((root / relative).read_text(encoding="utf-8"))
        descriptor = compose_dataset_execution_descriptor(request, root)
        output = {"descriptor": descriptor, "adapter_validation_only_guard": guard_result()}
        if name == "G_eo_fq_equivalent_semantics":
            equivalent = dict(request)
            equivalent["gap_policy_manifest"] = request["equivalent_gap_policy_manifest"]
            other = compose_dataset_execution_descriptor(equivalent, root)
            output["equivalent_semantics"] = (
                descriptor["gap_counts_by_disposition"]
                == other["gap_counts_by_disposition"]
            )
        if name == "H_repeated_deterministic_composition":
            output["repeated_descriptor_byte_identical"] = (
                canonical_bytes(descriptor)
                == canonical_bytes(compose_dataset_execution_descriptor(request, root))
            )
        outputs[name] = output
    return outputs


def has_forbidden_runtime_value(value) -> bool:
    forbidden = {
        "runtime_path", "generated_at", "runtime_timestamp", "run_timestamp",
        "current_timestamp", "traceback",
    }
    if isinstance(value, dict):
        return bool(forbidden.intersection(value)) or any(
            has_forbidden_runtime_value(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(has_forbidden_runtime_value(item) for item in value)
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    repo_root, root = Path(args.repo_root), Path(args.fixture_root)
    first, second = run_suite(root), run_suite(root)
    expected_path = Path(args.expected)
    if args.write_expected:
        expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    a1_first, a1_second = run_a1_regression(repo_root), run_a1_regression(repo_root)
    a1_hashes = {name: digest(value) for name, value in a1_first.items()}
    a2_root = repo_root / "tests/fixtures/fr_prep_a2"
    a2_first, a2_second = run_gap_suite(a2_root), run_gap_suite(a2_root)
    a2_expected = json.loads((a2_root / "expected_outputs.json").read_text(encoding="utf-8"))
    a2b1_root = repo_root / "tests/fixtures/fr_prep_a2b1"
    a2b1_cases = json.loads((a2b1_root / "negative_cases.json").read_text(encoding="utf-8"))
    a2b1_first = run_a2b1(a2b1_cases, a2_root, a2b1_root)
    a2b1_second = run_a2b1(a2b1_cases, a2_root, a2b1_root)
    a2b1_expected = json.loads((a2b1_root / "expected_failures.json").read_text(encoding="utf-8"))
    a2b2_root = repo_root / "tests/fixtures/fr_prep_a2b2"
    a2b2_cases = json.loads((a2b2_root / "negative_cases.json").read_text(encoding="utf-8"))
    a2b2_first = run_a2b2(a2b2_cases, a2_root)
    a2b2_second = run_a2b2(a2b2_cases, a2_root)
    a2b2_expected = json.loads((a2b2_root / "expected_failures.json").read_text(encoding="utf-8"))

    replay_identical = canonical_bytes(first) == canonical_bytes(second)
    relocation_identical = (
        first["A_generic_source_accepted"]["descriptor"]
        == first["F_runtime_path_relocation"]["descriptor"]
    )
    guard_pass = all(
        item["adapter_validation_only_guard"]["blocked_actions"] == [
            "execute_detector", "emit_event", "emit_atr_event",
            "calculate_tp_sl", "emit_outcome",
        ]
        for item in first.values()
    )
    checks = (
        len(first) == 8, first == expected, replay_identical, relocation_identical,
        guard_pass, not has_forbidden_runtime_value(first),
        first["G_eo_fq_equivalent_semantics"]["equivalent_semantics"] is True,
        first["H_repeated_deterministic_composition"]["repeated_descriptor_byte_identical"] is True,
        a1_first == a1_second,
        a1_hashes == {"a1a": POSITIVE_GOLDEN_SHA256, "a1b1": A1B1_GOLDEN_SHA256, "a1b2": A1B2_GOLDEN_SHA256},
        a2_first == a2_second == a2_expected and digest(a2_first) == A2_GOLDEN_SHA256,
        a2b1_first == a2b1_second == a2b1_expected and digest(a2b1_first) == A2B1_GOLDEN_SHA256,
        a2b2_first == a2b2_second == a2b2_expected and digest(a2b2_first) == A2B2_GOLDEN_SHA256,
    )
    if not all(checks):
        raise SystemExit("FR_PREP_A3A_SYNTHETIC_COMPOSITION_FAILED")
    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A3A_SYNTHETIC_COMPOSITION",
        "decision": "FR_PREP_A3A_PASS_SYNTHETIC_COMPOSITION",
        "positive_fixture_count": 8,
        "positive_fixtures_passed": 8,
        "run_1_sha256": digest(first),
        "run_2_sha256": digest(second),
        "golden_expected_sha256": digest(expected),
        "canonical_outputs_byte_identical": replay_identical,
        "runtime_path_relocation_output_identical": relocation_identical,
        "eo_fq_equivalent_semantics": True,
        "repeated_composition_byte_identical": True,
        "adapter_validation_only_guard_passed": guard_pass,
        "detector_executed": False, "events_created": False,
        "atr_events_created": False, "tp_sl_calculated": False,
        "outcomes_created": False, "broker_history_completeness": "NOT_PROVEN",
        "a1a_positive_fixtures": "4/4 PASS",
        "a1b1_negative_fixtures": "9/9 PASS",
        "a1b2_negative_fixtures": "13/13 PASS",
        "a2_positive_fixtures": "8/8 PASS",
        "a2b1_negative_fixtures": "18/18 PASS",
        "a2b2_negative_fixtures": "20/20 PASS",
        "a1a_golden_sha256": a1_hashes["a1a"],
        "a1b1_golden_sha256": a1_hashes["a1b1"],
        "a1b2_golden_sha256": a1_hashes["a1b2"],
        "a2_golden_sha256": digest(a2_first),
        "a2b1_golden_sha256": digest(a2b1_first),
        "a2b2_golden_sha256": digest(a2b2_first),
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False, "order_logic_status": "NOT_APPROVED",
        "candidate_status": "NOT_READY_FOR_ORDER_LOGIC",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "checkpoint_fr_prep_a3a_test_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
