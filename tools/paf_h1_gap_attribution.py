#!/usr/bin/env python3
"""Attribute H1 gaps in an offline normalized bars CSV without filling data."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path


TIME_FORMAT = "%Y.%m.%d %H:%M:%S"


def parse_time(value: str) -> datetime:
    return datetime.strptime(value.strip(), TIME_FORMAT)


def classify(previous: datetime, current: datetime) -> str:
    if previous.strftime("%A") == "Friday" and current.strftime("%A") == "Monday":
        return "WEEKEND_MARKET_CLOSURE"
    return "SHORT_SESSION_OR_HISTORY_GAP"


def main() -> int:
    parser = argparse.ArgumentParser(description="Attribute gaps in normalized GOLD# H1 bars.")
    parser.add_argument("--bars-csv", required=True)
    parser.add_argument("--from-time", required=True)
    parser.add_argument("--to-time", required=True)
    parser.add_argument("--results-root", required=True)
    parser.add_argument("--symbol", default="GOLD#")
    parser.add_argument("--timeframe", default="H1")
    args = parser.parse_args()

    if args.symbol != "GOLD#" or args.timeframe.upper() != "H1":
        raise SystemExit("This attribution contract is limited to GOLD# H1.")

    start = datetime.fromisoformat(args.from_time)
    end = datetime.fromisoformat(args.to_time)
    if start >= end:
        raise SystemExit("--from-time must be earlier than --to-time")

    with Path(args.bars_csv).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    times = sorted(parse_time(row["time"]) for row in rows if start <= parse_time(row["time"]) <= end)
    if len(times) < 2:
        raise SystemExit("Fewer than two bars are available in the requested range.")
    if len(times) != len(set(times)):
        raise SystemExit("Duplicate bar timestamps detected in the requested range.")

    gaps: list[dict[str, str | int | float]] = []
    for previous, current in zip(times, times[1:]):
        delta_hours = (current - previous).total_seconds() / 3600.0
        if delta_hours <= 1.0:
            continue
        gaps.append({
            "prev_time": previous.strftime("%Y-%m-%d %H:%M:%S"),
            "next_time": current.strftime("%Y-%m-%d %H:%M:%S"),
            "delta_hours": int(delta_hours) if delta_hours.is_integer() else delta_hours,
            "missing_h1_bars_estimate": max(0, int(delta_hours) - 1),
            "prev_weekday": previous.strftime("%A"),
            "next_weekday": current.strftime("%A"),
            "classification": classify(previous, current),
        })

    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)
    output_csv = results_root / "gap_attribution.csv"
    fields = ["prev_time", "next_time", "delta_hours", "missing_h1_bars_estimate", "prev_weekday", "next_weekday", "classification"]
    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(gaps)

    counts = Counter(str(row["classification"]) for row in gaps)
    summary = {
        "execution_status": "PASS",
        "symbol": args.symbol,
        "timeframe": args.timeframe.upper(),
        "requested_from": start.strftime("%Y-%m-%d %H:%M:%S"),
        "requested_to": end.strftime("%Y-%m-%d %H:%M:%S"),
        "coverage_from": times[0].strftime("%Y-%m-%d %H:%M:%S"),
        "coverage_to": times[-1].strftime("%Y-%m-%d %H:%M:%S"),
        "bar_count": len(times),
        "gap_count": len(gaps),
        "classification_counts": dict(sorted(counts.items())),
        "missing_bars_estimate": sum(int(row["missing_h1_bars_estimate"]) for row in gaps),
        "prices_modified": False,
        "missing_bars_filled": False,
        "strategy_performance_status": "NOT_EVALUATED",
        "profitability_claim": False,
    }
    (results_root / "gap_attribution_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    markdown = [
        "# GOLD# H1 Gap Attribution Summary",
        "",
        "Offline attribution only. No bars were filled or prices modified.",
        "",
        *[f"- {key}: `{value}`" for key, value in summary.items()],
        "",
    ]
    (results_root / "gap_attribution_summary.md").write_text("\n".join(markdown), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
