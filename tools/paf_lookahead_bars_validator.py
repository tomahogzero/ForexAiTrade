#!/usr/bin/env python3
"""Validate an offline PAF lookahead OHLC bars CSV.

The validator does not run MT5, does not send orders, and does not calculate
profitability. It only checks whether a supplied bar series is suitable for the
offline PAF lookahead joiner.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = ["time", "open", "high", "low", "close"]
DEFAULT_HORIZON_BARS = 48


def parse_time(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in (
        "%Y.%m.%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y.%m.%d %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y.%m.%d",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        raise SystemExit(f"Missing CSV file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def normalized_column_map(fieldnames: list[str]) -> dict[str, str]:
    return {name.strip().lower(): name for name in fieldnames}


def normalize_bar(row: dict[str, str], column_map: dict[str, str]) -> dict[str, Any] | None:
    time_value = row.get(column_map.get("time", ""))
    bar_time = parse_time(time_value)
    if bar_time is None:
        return None

    values: dict[str, Any] = {"time": bar_time, "time_text": time_value}
    for column in ("open", "high", "low", "close"):
        parsed = to_float(row.get(column_map.get(column, "")))
        if parsed is None:
            return None
        values[column] = parsed
    return values


def load_bars(path: Path) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    fieldnames, rows = read_csv(path)
    column_map = normalized_column_map(fieldnames)
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in column_map]
    bars = []
    invalid_rows = 0
    if not missing_columns:
        for row in rows:
            bar = normalize_bar(row, column_map)
            if bar is None:
                invalid_rows += 1
            else:
                bars.append(bar)
    bars.sort(key=lambda item: item["time"])
    issues = []
    if missing_columns:
        issues.append(f"missing required columns: {', '.join(missing_columns)}")
    if invalid_rows:
        issues.append(f"invalid bar rows: {invalid_rows}")
    return fieldnames, bars, issues


def load_event_times(path: Path) -> list[datetime]:
    fieldnames, rows = read_csv(path)
    column_map = normalized_column_map(fieldnames)
    event_column = column_map.get("event_time")
    if not event_column:
        raise SystemExit("Shadow outcomes CSV must contain event_time column.")
    event_times = []
    for row in rows:
        parsed = parse_time(row.get(event_column))
        if parsed is not None:
            event_times.append(parsed)
    return sorted(set(event_times))


def expected_step_minutes(timeframe: str) -> int | None:
    value = timeframe.strip().upper()
    if value.startswith("M") and value[1:].isdigit():
        return int(value[1:])
    if value.startswith("H") and value[1:].isdigit():
        return int(value[1:]) * 60
    if value == "D1":
        return 1440
    return None


def detect_gap_count(bars: list[dict[str, Any]], step_minutes: int | None) -> int:
    if step_minutes is None or len(bars) < 2:
        return 0
    expected = timedelta(minutes=step_minutes)
    gaps = 0
    for previous, current in zip(bars, bars[1:]):
        delta = current["time"] - previous["time"]
        if delta > expected:
            gaps += 1
    return gaps


def validate(args: argparse.Namespace) -> dict[str, Any]:
    bars_csv = Path(args.bars_csv)
    shadow_csv = Path(args.shadow_outcomes) if args.shadow_outcomes else None
    fieldnames, bars, issues = load_bars(bars_csv)
    step_minutes = expected_step_minutes(args.timeframe)
    event_times = load_event_times(shadow_csv) if shadow_csv else []

    bar_times = {bar["time"] for bar in bars}
    matched_events = [event_time for event_time in event_times if event_time in bar_times]
    missing_events = [event_time for event_time in event_times if event_time not in bar_times]

    coverage_from = bars[0]["time"] if bars else None
    coverage_to = bars[-1]["time"] if bars else None
    required_to = None
    if event_times and step_minutes is not None:
        required_to = max(event_times) + timedelta(minutes=step_minutes * args.horizon_bars)

    if not bars:
        issues.append("no valid bars loaded")
    if missing_events:
        issues.append(f"event timestamps without exact bar match: {len(missing_events)}")
    if required_to is not None and coverage_to is not None and coverage_to < required_to:
        issues.append(f"bar coverage ends before required lookahead horizon: {coverage_to} < {required_to}")
    gap_count = detect_gap_count(bars, step_minutes)
    if gap_count:
        issues.append(f"detected gaps larger than expected timeframe step: {gap_count}")

    verdict = "PASS" if not issues else "FAIL"
    return {
        "verdict": verdict,
        "bars_csv": str(bars_csv),
        "shadow_outcomes": str(shadow_csv) if shadow_csv else "",
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "horizon_bars": args.horizon_bars,
        "fieldnames": fieldnames,
        "bar_count": len(bars),
        "coverage_from": coverage_from.strftime("%Y-%m-%d %H:%M:%S") if coverage_from else "",
        "coverage_to": coverage_to.strftime("%Y-%m-%d %H:%M:%S") if coverage_to else "",
        "event_count": len(event_times),
        "matched_event_count": len(matched_events),
        "missing_event_count": len(missing_events),
        "required_coverage_to": required_to.strftime("%Y-%m-%d %H:%M:%S") if required_to else "",
        "gap_count": gap_count,
        "issues": issues,
        "guardrails": [
            "offline validation only",
            "no MT5 run",
            "no Strategy Tester run",
            "no orders",
            "no optimization",
            "no profitability claim",
        ],
    }


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# PAF Lookahead Bars Validation Summary",
        "",
        "This validation is offline-only. It does not run MT5, does not send orders, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"`{summary['verdict']}`",
        "",
        "## Inputs",
        "",
        f"- Bars CSV: `{summary['bars_csv']}`",
        f"- Shadow outcomes: `{summary['shadow_outcomes']}`",
        f"- Symbol: `{summary['symbol']}`",
        f"- Timeframe: `{summary['timeframe']}`",
        f"- Horizon bars: `{summary['horizon_bars']}`",
        "",
        "## Coverage",
        "",
        f"- Bar count: `{summary['bar_count']}`",
        f"- Coverage from: `{summary['coverage_from']}`",
        f"- Coverage to: `{summary['coverage_to']}`",
        f"- Required coverage to: `{summary['required_coverage_to']}`",
        f"- Event count: `{summary['event_count']}`",
        f"- Matched events: `{summary['matched_event_count']}`",
        f"- Missing events: `{summary['missing_event_count']}`",
        f"- Gap count: `{summary['gap_count']}`",
        "",
        "## Issues",
        "",
    ]
    if summary["issues"]:
        for issue in summary["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines += [
        "",
        "## Guardrails",
        "",
        "- Offline validation only.",
        "- No MT5 run.",
        "- No Strategy Tester run.",
        "- No market orders or pending orders.",
        "- No optimization.",
        "- No profitability claim.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PAF lookahead OHLC bars CSV before offline joining.")
    parser.add_argument("--bars-csv", required=True)
    parser.add_argument("--shadow-outcomes", help="Optional shadow outcomes CSV containing event_time values.")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--symbol", default="GOLD#")
    parser.add_argument("--timeframe", default="H1")
    parser.add_argument("--horizon-bars", type=int, default=DEFAULT_HORIZON_BARS)
    args = parser.parse_args()

    if args.horizon_bars <= 0:
        raise SystemExit("--horizon-bars must be positive")

    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)
    summary = validate(args)
    (results_root / "paf_lookahead_bars_validation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_summary(results_root / "paf_lookahead_bars_validation_summary.md", summary)
    print(f"Validation verdict: {summary['verdict']}")
    print(f"Summary: {results_root / 'paf_lookahead_bars_validation_summary.md'}")
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
