#!/usr/bin/env python3
"""Verify frozen gaps against user-supplied yearly MT5 GOLD# H1 CSV exports."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path


RAW_COLUMNS = ("<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>", "<CLOSE>")
RAW_TIME_FORMAT = "%Y.%m.%d %H:%M:%S"
GAP_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_raw(path: Path) -> tuple[dict[datetime, Path], dict[str, object]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = tuple(reader.fieldnames or ())
        missing = [column for column in RAW_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"{path.name}: missing required raw MT5 columns: {', '.join(missing)}")
        bars: dict[datetime, Path] = {}
        for index, row in enumerate(reader, start=2):
            try:
                time = datetime.strptime(f"{row['<DATE>']} {row['<TIME>']}", RAW_TIME_FORMAT)
            except ValueError as error:
                raise ValueError(f"{path.name}: invalid timestamp at row {index}") from error
            for column in RAW_COLUMNS[2:]:
                try:
                    float(row[column])
                except (TypeError, ValueError) as error:
                    raise ValueError(f"{path.name}: invalid {column} at row {index}") from error
            if time in bars:
                raise ValueError(f"{path.name}: duplicate timestamp {time:%Y-%m-%d %H:%M:%S}")
            bars[time] = path
    if not bars:
        raise ValueError(f"{path.name}: no valid bars")
    ordered = sorted(bars)
    return bars, {
        "file": path.name,
        "sha256": sha256(path),
        "row_count": len(bars),
        "coverage_from": ordered[0].strftime(GAP_TIME_FORMAT),
        "coverage_to": ordered[-1].strftime(GAP_TIME_FORMAT),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline intake for yearly MT5 GOLD# H1 exports.")
    parser.add_argument("--raw-csv", action="append", required=True)
    parser.add_argument("--gaps-csv", required=True)
    parser.add_argument("--results-root", required=True)
    args = parser.parse_args()

    if len(args.raw_csv) != 3:
        raise SystemExit("Exactly three yearly raw CSV files are required for 2023-2025 intake.")
    combined: dict[datetime, Path] = {}
    files: list[dict[str, object]] = []
    for raw in args.raw_csv:
        bars, file_summary = load_raw(Path(raw))
        overlap = set(combined).intersection(bars)
        if overlap:
            raise SystemExit(f"duplicate timestamps across yearly files: {len(overlap)}")
        combined.update(bars)
        files.append(file_summary)

    with Path(args.gaps_csv).open(encoding="utf-8-sig", newline="") as handle:
        gaps = list(csv.DictReader(handle))
    if len(gaps) != 28:
        raise SystemExit(f"frozen gap count must be 28, got {len(gaps)}")

    output_rows: list[dict[str, object]] = []
    confirmed = 0
    all_times = sorted(combined)
    for gap in gaps:
        previous = datetime.strptime(gap["prev_time"], GAP_TIME_FORMAT)
        following = datetime.strptime(gap["next_time"], GAP_TIME_FORMAT)
        expected_delta = float(gap["delta_hours"])
        actual_delta = (following - previous).total_seconds() / 3600.0
        interior_count = sum(1 for time in all_times if previous < time < following)
        previous_present = previous in combined
        following_present = following in combined
        exact = previous_present and following_present and actual_delta == expected_delta and interior_count == 0
        confirmed += int(exact)
        source_files = sorted({combined[time].name for time in (previous, following) if time in combined})
        output_rows.append({
            "prev_time": gap["prev_time"],
            "next_time": gap["next_time"],
            "delta_hours": gap["delta_hours"],
            "previous_bar_present": str(previous_present).lower(),
            "next_bar_present": str(following_present).lower(),
            "interior_h1_bars": interior_count,
            "csv_gap_confirmed": str(exact).lower(),
            "source_files": ";".join(source_files),
            "eq_layer_a_complete": "false",
            "eq_layer_b_complete": "false",
            "acceptance_state": "CONTEXT_ONLY",
            "limitation": "missing per-gap screenshot, fresh-refresh manifest, and exact XM schedule/session provenance",
        })

    results = Path(args.results_root)
    results.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0])
    with (results / "yearly_csv_gap_intake.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    summary = {
        "execution_status": "PASS" if confirmed == 28 else "FAIL_GAP_CONFIRMATION",
        "frozen_gap_count": len(gaps),
        "yearly_raw_file_count": len(files),
        "yearly_files": files,
        "csv_confirmed_gaps": confirmed,
        "eq_layer_a_complete": 0,
        "eq_layer_b_complete": 0,
        "exact_broker_evidence_complete": 0,
        "acceptance_state_counts": {"CONTEXT_ONLY": len(output_rows)},
        "policy_change_approved": False,
        "mt5_opened": False,
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False,
    }
    (results / "yearly_csv_gap_intake_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = ["# Checkpoint ET Yearly CSV Intake", ""] + [f"- {key}: `{value}`" for key, value in summary.items()] + [""]
    (results / "yearly_csv_gap_intake_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if confirmed == 28 else 2


if __name__ == "__main__":
    raise SystemExit(main())
