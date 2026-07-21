#!/usr/bin/env python3
"""Run only FR-Prep-A2 positive gap-adapter fixtures and A1 regressions."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gap_policy_adapter import canonical_bytes, validate_gap_policy
from historical_source_adapter import A1B1_VALIDATION_CODES, A1B2_VALIDATION_CODES
from run_fr_prep_a1a_source_adapter_fixtures import run_suite as run_a1a
from run_fr_prep_a1b1_negative_source_fixtures import run_negative as run_a1b1
from run_fr_prep_a1b2_remaining_source_fixtures import run_a1b2

POSITIVE_GOLDEN_SHA256 = "717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b"
A1B1_GOLDEN_SHA256 = "97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8"
A1B2_GOLDEN_SHA256 = "5bde1d04d27c67a089103c344ff17918a795d9dc14176fae6dffc58782b242a4"
A1B1_FROZEN_CODES = frozenset({
    "SOURCE_PATH_MISSING", "SOURCE_SHA256_MISMATCH", "SOURCE_SIZE_MISMATCH",
    "MT5_TSV_SCHEMA_INVALID", "SOURCE_TIMESTAMP_UNPARSEABLE",
    "OHLC_NON_FINITE_OR_NON_POSITIVE", "OHLC_INCONSISTENT",
    "SOURCE_NOT_CHRONOLOGICAL", "SOURCE_ROW_COUNT_MISMATCH",
})
A1B2_FROZEN_CODES = frozenset({
    "SOURCE_FIRST_TIMESTAMP_MISMATCH", "SOURCE_LAST_TIMESTAMP_MISMATCH",
    "SOURCE_ROW_BEFORE_BOUNDARY", "SOURCE_ROW_AFTER_BOUNDARY",
    "DUPLICATE_SOURCE_ID", "AGGREGATE_DUPLICATE_TIMESTAMP",
    "AGGREGATE_TIMESTAMP_OHLC_CONFLICT", "AGGREGATE_SOURCE_COUNT_MISMATCH",
    "AGGREGATE_TOTAL_ROW_COUNT_MISMATCH", "AGGREGATE_FIRST_TIMESTAMP_MISMATCH",
    "AGGREGATE_LAST_TIMESTAMP_MISMATCH", "AGGREGATE_TIMELINE_RANGE_MISMATCH",
    "CANONICAL_TIMELINE_SHA256_MISMATCH",
})
FIXTURES = {
    "A_valid_minimal_generic_accepted": "A_valid_minimal_generic_accepted.json",
    "B_valid_minimal_generic_unverified": "B_valid_minimal_generic_unverified.json",
    "C_valid_eo_fj_accepted_mapping": "C_valid_eo_fj_accepted_mapping.json",
    "D_valid_eo_fj_unverified_mapping": "D_valid_eo_fj_unverified_mapping.json",
    "E_valid_fq_accepted_mapping": "E_valid_fq_accepted_mapping.json",
    "F_valid_fq_unverified_mapping": "F_valid_fq_unverified_mapping.json",
    "G_valid_mixed_ordered_inventory": "G_valid_mixed_ordered_inventory.json",
    "H_valid_runtime_path_relocation": "H_valid_runtime_path_relocation.json",
}


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def run_gap_suite(root: Path) -> dict:
    return {name: validate_gap_policy(root / relative) for name, relative in FIXTURES.items()}


def has_runtime_timestamp(value) -> bool:
    if isinstance(value, dict):
        forbidden = {"generated_at", "runtime_timestamp", "run_timestamp", "current_timestamp"}
        return bool(forbidden.intersection(value)) or any(has_runtime_timestamp(item) for item in value.values())
    if isinstance(value, list):
        return any(has_runtime_timestamp(item) for item in value)
    return False


def has_runtime_path(value) -> bool:
    if isinstance(value, dict):
        return "runtime_path" in value or any(has_runtime_path(item) for item in value.values())
    if isinstance(value, list):
        return any(has_runtime_path(item) for item in value)
    return False


def run_a1_regression(repo_root: Path) -> dict:
    positive_root = repo_root / "tests/fixtures/fr_prep_a1a"
    a1a = run_a1a(positive_root)
    a1b1_cases = json.loads((repo_root / "tests/fixtures/fr_prep_a1b1/negative_cases.json").read_text(encoding="utf-8"))
    a1b2_cases = json.loads((repo_root / "tests/fixtures/fr_prep_a1b2/negative_cases.json").read_text(encoding="utf-8"))
    a1b1 = run_a1b1(a1b1_cases, positive_root)
    a1b2 = run_a1b2(a1b2_cases, positive_root)
    return {"a1a": a1a, "a1b1": a1b1, "a1b2": a1b2}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    fixture_root = Path(args.fixture_root)
    first, second = run_gap_suite(fixture_root), run_gap_suite(fixture_root)
    expected_path = Path(args.expected)
    if args.write_expected:
        expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    gap_hash = digest(first)
    gap_replay_identical = canonical_bytes(first) == canonical_bytes(second)
    mismatch_count = 0 if first == expected else 1
    relocation_identical = (
        first["A_valid_minimal_generic_accepted"]
        == first["H_valid_runtime_path_relocation"]
    )
    entries_ordered = all(
        output["entries"] == sorted(output["entries"], key=lambda item: (
            item["previous_bar_timestamp"], item["next_bar_timestamp"],
            item["gap_id"], item["source_record_identity"],
        ))
        for output in first.values()
    )
    runtime_timestamps_absent = not has_runtime_timestamp(first)
    runtime_paths_absent = not has_runtime_path(first)

    a1_first, a1_second = run_a1_regression(repo_root), run_a1_regression(repo_root)
    a1_replay_identical = canonical_bytes(a1_first) == canonical_bytes(a1_second)
    a1_hashes = {name: digest(value) for name, value in a1_first.items()}
    a1_expected = {
        "a1a": POSITIVE_GOLDEN_SHA256,
        "a1b1": A1B1_GOLDEN_SHA256,
        "a1b2": A1B2_GOLDEN_SHA256,
    }
    a1_codes_unchanged = (
        A1B1_VALIDATION_CODES == A1B1_FROZEN_CODES
        and A1B2_VALIDATION_CODES == A1B2_FROZEN_CODES
    )
    if not all((
        gap_replay_identical, not mismatch_count, relocation_identical,
        entries_ordered, runtime_timestamps_absent, runtime_paths_absent,
        a1_replay_identical, a1_hashes == a1_expected, a1_codes_unchanged,
    )):
        raise SystemExit("FR_PREP_A2_GAP_ADAPTER_POSITIVE_FAILED")

    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A2_GAP_POLICY_ADAPTER_POSITIVE",
        "decision": "FR_PREP_A2_PASS_GAP_ADAPTER_POSITIVE",
        "positive_fixture_count": len(first),
        "positive_fixtures_passed": len(first),
        "fixture_names": list(FIXTURES),
        "run_1_sha256": gap_hash,
        "run_2_sha256": digest(second),
        "golden_expected_sha256": digest(expected),
        "canonical_outputs_byte_identical": gap_replay_identical,
        "mismatch_count": mismatch_count,
        "runtime_path_relocation_output_identical": relocation_identical,
        "normalized_entries_deterministically_ordered": entries_ordered,
        "runtime_timestamps_absent": runtime_timestamps_absent,
        "canonical_runtime_paths_absent": runtime_paths_absent,
        "a1a_positive_fixtures": "4/4 PASS",
        "a1b1_negative_fixtures": "9/9 PASS",
        "a1b2_negative_fixtures": "13/13 PASS",
        "a1a_golden_sha256": a1_hashes["a1a"],
        "a1b1_golden_sha256": a1_hashes["a1b1"],
        "a1b2_golden_sha256": a1_hashes["a1b2"],
        "a1_complete_run_1_sha256": digest(a1_first),
        "a1_complete_run_2_sha256": digest(a1_second),
        "a1_complete_replay_byte_identical": a1_replay_identical,
        "a1_validation_codes_unchanged": a1_codes_unchanged,
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
    output_path = output_root / "checkpoint_fr_prep_a2_test_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
