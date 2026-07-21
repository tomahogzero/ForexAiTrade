#!/usr/bin/env python3
"""Run only FR-Prep-A1a positive source-adapter fixtures."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from historical_source_adapter import canonical_bytes, validate_manifest

FIXTURES = {
    "A_valid_minimal_generic_manifest": "A_valid_minimal_generic_manifest.json",
    "B_valid_fp_style_mapping": "B_valid_fp_style_mapping.json",
    "C_valid_fj_style_mapping": "C_valid_fj_style_mapping.json",
    "D_valid_runtime_path_relocation": "D_valid_runtime_path_relocation.json",
}


def digest(value) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def run_suite(root: Path) -> dict:
    return {name: validate_manifest(root / relative) for name, relative in FIXTURES.items()}


def has_runtime_timestamp(value) -> bool:
    if isinstance(value, dict):
        forbidden = {"generated_at", "runtime_timestamp", "run_timestamp", "current_timestamp"}
        return bool(forbidden.intersection(value)) or any(has_runtime_timestamp(item) for item in value.values())
    if isinstance(value, list):
        return any(has_runtime_timestamp(item) for item in value)
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-root", required=True)
    parser.add_argument("--expected", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    root = Path(args.fixture_root)
    expected_path = Path(args.expected)
    first = run_suite(root)
    second = run_suite(root)
    byte_identical = canonical_bytes(first) == canonical_bytes(second)
    relocation_equal = (
        first["A_valid_minimal_generic_manifest"]
        == first["D_valid_runtime_path_relocation"]
    )
    runtime_absent = not has_runtime_timestamp(first)
    if args.write_expected:
        expected_path.write_text(json.dumps(first, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    mismatch_count = 0 if first == expected else 1
    if not byte_identical or not relocation_equal or not runtime_absent or mismatch_count:
        raise SystemExit("FR_PREP_A1A_FIXTURE_VALIDATION_FAILED")
    summary = {
        "execution_status": "PASS",
        "checkpoint_status": "FR_PREP_A1A_SOURCE_ADAPTER_CORE",
        "fixture_count": len(FIXTURES),
        "fixtures_passed": len(FIXTURES),
        "fixture_names": list(FIXTURES),
        "run_1_sha256": digest(first),
        "run_2_sha256": digest(second),
        "golden_expected_sha256": digest(expected),
        "canonical_outputs_byte_identical": byte_identical,
        "runtime_path_relocation_output_identical": relocation_equal,
        "runtime_timestamps_absent": runtime_absent,
        "mismatch_count": mismatch_count,
        "detector_executed": False, "events_created": False,
        "outcomes_created": False, "broker_history_completeness": "NOT_PROVEN",
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False, "order_logic_status": "NOT_APPROVED",
    }
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "checkpoint_fr_prep_a1a_test_summary.json"
    output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
