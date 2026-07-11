#!/usr/bin/env python3
"""Exact-join EH eligible Fibo rows to entry/ATR from original DZ logs."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paf_diagnostic_parser import extract_diagnostics, load_json, read_text


RUN_IDS = ("run_20260711_145612", "run_20260711_152017", "run_20260711_153941")
JOIN_FIELDS = ("run_id", "case_id", "event_time")
OUTPUT_NAME = "checkpoint_em_paf_fibo_entry_atr.csv"
SUMMARY_NAME = "checkpoint_em_paf_fibo_entry_atr_summary.json"


def exact_key(row: dict[str, str]) -> tuple[str, str, str]:
    return tuple(str(row.get(field, "")) for field in JOIN_FIELDS)  # type: ignore[return-value]


def valid_positive_number(value: object) -> bool:
    try:
        number = float(str(value))
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0.0


def load_eligible_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("candidate_outcome") == "ELIGIBLE_DIAGNOSTIC_ROW"]
    return rows


def build_source_index(source_root: Path) -> tuple[dict[tuple[str, str, str], dict[str, str]], dict[str, object]]:
    index: dict[tuple[str, str, str], dict[str, str]] = {}
    missing: list[str] = []
    duplicate_keys: list[tuple[str, str, str]] = []
    source_log_count = 0
    fibo_diagnostic_count = 0

    for run_id in RUN_IDS:
        run_dir = source_root / run_id
        if not run_dir.is_dir():
            missing.append(run_id)
            continue
        case_dirs = sorted(path for path in run_dir.iterdir() if path.is_dir())
        for case_dir in case_dirs:
            log_path = case_dir / "ea_mirror.log"
            case_path = case_dir / "case.json"
            if not log_path.is_file():
                missing.append(f"{run_id}/{case_dir.name}/ea_mirror.log")
                continue
            if not case_path.is_file():
                missing.append(f"{run_id}/{case_dir.name}/case.json")
                continue

            case = load_json(case_path)
            case_id = str(case.get("case_id") or case_dir.name)
            source_log_count += 1
            diagnostics, _ = extract_diagnostics(read_text(log_path))
            for diagnostic in diagnostics:
                if diagnostic.get("classification") != "POSSIBLE_FIBO_PULLBACK":
                    continue
                fibo_diagnostic_count += 1
                source = {
                    "run_id": run_id,
                    "case_id": case_id,
                    "event_time": str(diagnostic.get("time", "")),
                    "classification": str(diagnostic.get("classification", "")),
                    "paf_candidate_direction": str(diagnostic.get("paf_candidate_direction", "")),
                    "entry_reference_price": str(diagnostic.get("entry_reference_price", "")),
                    "atr": str(diagnostic.get("atr", "")),
                    "source_log": log_path.relative_to(source_root).as_posix(),
                }
                key = exact_key(source)
                if key in index:
                    duplicate_keys.append(key)
                else:
                    index[key] = source

    audit = {
        "missing_sources": missing,
        "duplicate_source_key_count": len(duplicate_keys),
        "duplicate_source_keys_sample": [list(key) for key in duplicate_keys[:10]],
        "source_log_count": source_log_count,
        "source_fibo_diagnostic_count": fibo_diagnostic_count,
    }
    return index, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--eh-input", required=True)
    parser.add_argument("--output-root", default="research/results")
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    eh_input = Path(args.eh_input).resolve()
    output_root = Path(args.output_root)
    eligible = load_eligible_rows(eh_input)
    source_index, source_audit = build_source_index(source_root)

    eligible_key_counts = Counter(exact_key(row) for row in eligible)
    duplicate_eligible_keys = [key for key, count in eligible_key_counts.items() if count != 1]
    enriched: list[dict[str, str]] = []
    unmatched: list[tuple[str, str, str]] = []
    provenance_conflicts: list[tuple[str, str, str]] = []
    invalid_values: list[tuple[str, str, str]] = []

    for row in eligible:
        key = exact_key(row)
        source = source_index.get(key)
        if source is None:
            unmatched.append(key)
            continue
        if source["classification"] != row.get("classification") or source["paf_candidate_direction"] != row.get("paf_candidate_direction"):
            provenance_conflicts.append(key)
            continue
        if not valid_positive_number(source["entry_reference_price"]) or not valid_positive_number(source["atr"]):
            invalid_values.append(key)
            continue
        enriched.append({
            **row,
            "entry_reference_price": source["entry_reference_price"],
            "atr": source["atr"],
            "entry_atr_authoritative_source": "ea_mirror.log",
            "entry_atr_source_log": source["source_log"],
            "entry_atr_join_key": "+".join(JOIN_FIELDS),
        })

    exact_match_pass = (
        len(eligible) == 1600
        and len(enriched) == 1600
        and not duplicate_eligible_keys
        and not source_audit["missing_sources"]
        and source_audit["duplicate_source_key_count"] == 0
        and not unmatched
        and not provenance_conflicts
        and not invalid_values
    )
    summary = {
        "execution_status": "PASS" if exact_match_pass else "BLOCKED_EXACT_MATCH_FAILED",
        "source_runs": list(RUN_IDS),
        "eh_input": eh_input.name,
        "eh_eligible_rows": len(eligible),
        "exact_matched_rows": len(enriched),
        "required_exact_matches": 1600,
        "exact_match_pass": exact_match_pass,
        **source_audit,
        "duplicate_eligible_key_count": len(duplicate_eligible_keys),
        "unmatched_count": len(unmatched),
        "provenance_conflict_count": len(provenance_conflicts),
        "invalid_entry_or_atr_count": len(invalid_values),
        "no_mt5_run": True,
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False,
    }
    print(json.dumps(summary, indent=2))
    if not exact_match_pass:
        return 2

    output_root.mkdir(parents=True, exist_ok=True)
    with (output_root / OUTPUT_NAME).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=enriched[0].keys())
        writer.writeheader()
        writer.writerows(enriched)
    (output_root / SUMMARY_NAME).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
