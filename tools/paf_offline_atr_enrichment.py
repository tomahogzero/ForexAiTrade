#!/usr/bin/env python3
"""Offline ATR enrichment for PAF diagnostic artifacts.

This tool reads existing offline GOLD# H1 bars and PAF diagnostic shadow rows,
adds an offline-computed ATR column, and writes data-completeness artifacts.
It does not run MT5, does not send orders, does not optimize parameters, and
does not prove profitability.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


BUY = "BUY_CONTEXT"
SELL = "SELL_CONTEXT"
DEFAULT_ATR_PERIOD = 14
DEFAULT_OUTPUT_COLUMN = "offline_atr_14"


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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"INPUT_MISSING: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def counter_dict(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values if value not in (None, "")).items()))


def normalize_bar(row: dict[str, str]) -> dict[str, Any] | None:
    bar_time = parse_time(row.get("time") or row.get("Time"))
    open_price = to_float(row.get("open") or row.get("Open"))
    high = to_float(row.get("high") or row.get("High"))
    low = to_float(row.get("low") or row.get("Low"))
    close = to_float(row.get("close") or row.get("Close"))
    if bar_time is None or None in (open_price, high, low, close):
        return None
    return {
        "time": bar_time,
        "time_text": bar_time.strftime("%Y.%m.%d %H:%M:%S"),
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
    }


def load_bars(path: Path) -> list[dict[str, Any]]:
    rows = read_csv(path)
    bars = [bar for row in rows if (bar := normalize_bar(row)) is not None]
    bars.sort(key=lambda item: item["time"])
    if not bars:
        raise SystemExit("SCHEMA_MISMATCH: no valid bars found; expected time,open,high,low,close")
    return bars


def classify_gap(previous_time: datetime, current_time: datetime) -> str:
    delta = current_time - previous_time
    if delta == timedelta(hours=1):
        return "EXPECTED_H1"
    if previous_time.weekday() == 4 and current_time.weekday() == 0:
        return "WEEKEND_GAP"
    if timedelta(hours=1) < delta <= timedelta(hours=4) and previous_time.hour >= 21 and current_time.hour <= 2:
        return "DAILY_SESSION_GAP"
    return "UNKNOWN_IRREGULAR_GAP"


def validate_bars(bars: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    issues: list[str] = []
    gaps: list[dict[str, Any]] = []
    seen: set[datetime] = set()
    previous: dict[str, Any] | None = None
    for index, bar in enumerate(bars):
        bar_time = bar["time"]
        if bar_time in seen:
            issues.append(f"duplicate bar timestamp: {bar_time:%Y-%m-%d %H:%M:%S}")
        seen.add(bar_time)
        if previous and bar_time <= previous["time"]:
            issues.append("bars are not strictly sorted by time")
        if previous:
            gap_type = classify_gap(previous["time"], bar_time)
            if gap_type != "EXPECTED_H1":
                gaps.append(
                    {
                        "from": previous["time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "to": bar_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "hours": round((bar_time - previous["time"]).total_seconds() / 3600, 2),
                        "classification": gap_type,
                    }
                )
                if gap_type == "UNKNOWN_IRREGULAR_GAP":
                    issues.append(
                        "unknown irregular gap: "
                        f"{previous['time']:%Y-%m-%d %H:%M:%S} -> {bar_time:%Y-%m-%d %H:%M:%S}"
                    )
        previous = bar
    return gaps, issues


def true_ranges(bars: list[dict[str, Any]]) -> list[float]:
    ranges: list[float] = []
    previous_close: float | None = None
    for bar in bars:
        high = bar["high"]
        low = bar["low"]
        if previous_close is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - previous_close), abs(low - previous_close))
        ranges.append(round(tr, 5))
        previous_close = bar["close"]
    return ranges


def compute_simple_atr_by_bar(bars: list[dict[str, Any]], period: int) -> dict[datetime, dict[str, Any]]:
    ranges = true_ranges(bars)
    atr_by_bar: dict[datetime, dict[str, Any]] = {}
    for index, bar in enumerate(bars):
        # Conservative alignment: an event at bar T uses completed H1 bars
        # strictly before T, avoiding current-forming-bar high/low leakage.
        end_index = index - 1
        start_index = end_index - period + 1
        if start_index < 0:
            atr_by_bar[bar["time"]] = {
                "atr": None,
                "reason": f"only {max(0, end_index + 1)} completed bars available before event; need {period}",
                "source_start": "",
                "source_end": "",
                "bars_used": max(0, end_index + 1),
            }
            continue
        window = ranges[start_index : end_index + 1]
        atr_by_bar[bar["time"]] = {
            "atr": round(sum(window) / period, 5),
            "reason": "",
            "source_start": bars[start_index]["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "source_end": bars[end_index]["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "bars_used": period,
        }
    return atr_by_bar


def enrich_events(
    events: list[dict[str, str]],
    bars: list[dict[str, Any]],
    atr_by_bar: dict[datetime, dict[str, Any]],
    output_column: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bar_times = {bar["time"] for bar in bars}
    enriched: list[dict[str, Any]] = []
    completeness: list[dict[str, Any]] = []
    for row in events:
        output: dict[str, Any] = dict(row)
        event_time = parse_time(row.get("event_time"))
        direction = (row.get("direction") or "").strip()
        entry = to_float(row.get("entry_reference_price"))
        status = "ATR_READY"
        reason = ""
        atr_payload: dict[str, Any] | None = None

        if direction not in {BUY, SELL}:
            status = "DIRECTION_MISSING"
            reason = "direction_context is missing or unknown"
        elif event_time is None:
            status = "DATA_MISSING"
            reason = "event_time could not be parsed"
        elif event_time not in bar_times:
            status = "DATA_MISSING"
            reason = "event_time does not match an exported bar timestamp"
        elif entry is None:
            status = "DATA_MISSING"
            reason = "entry_reference_price is missing"
        else:
            atr_payload = atr_by_bar.get(event_time)
            if not atr_payload or atr_payload.get("atr") in (None, ""):
                status = "ATR_MISSING"
                reason = (atr_payload or {}).get("reason", "offline ATR could not be computed")

        atr_value = "" if not atr_payload or atr_payload.get("atr") is None else atr_payload["atr"]
        output[output_column] = atr_value
        output["offline_atr_status"] = status
        output["offline_atr_reason"] = reason
        output["offline_atr_period"] = DEFAULT_ATR_PERIOD
        output["offline_atr_method"] = "simple_average_true_range"
        output["offline_atr_alignment_rule"] = "completed H1 bars strictly before event bar"
        output["offline_atr_source_start"] = (atr_payload or {}).get("source_start", "")
        output["offline_atr_source_end"] = (atr_payload or {}).get("source_end", "")
        output["offline_atr_bars_used"] = (atr_payload or {}).get("bars_used", "")
        enriched.append(output)
        completeness.append(
            {
                "event_time": row.get("event_time", ""),
                "classification": row.get("classification", ""),
                "direction": direction,
                "entry_reference_price": row.get("entry_reference_price", ""),
                output_column: atr_value,
                "offline_atr_status": status,
                "offline_atr_reason": reason,
                "lookahead_status": row.get("lookahead_status", ""),
            }
        )
    return enriched, completeness


def fieldnames_for(events: list[dict[str, str]], extra: list[str]) -> list[str]:
    names = list(events[0].keys()) if events else []
    for name in extra:
        if name not in names:
            names.append(name)
    return names


def write_summary_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Checkpoint CC: Offline ATR Enrichment Summary",
        "",
        "This is an offline diagnostic artifact. It does not run MT5, does not send orders, does not optimize parameters, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"- Status: `{summary['status']}`",
        f"- ATR column: `{summary['output_column']}`",
        f"- ATR period: `{summary['atr_period']}`",
        f"- ATR method: `{summary['atr_method']}`",
        f"- ATR alignment: `{summary['atr_alignment_rule']}`",
        "",
        "## Counts",
        "",
        f"- Bars read: `{summary['bars_read']}`",
        f"- Events read: `{summary['events_read']}`",
        f"- Events with valid offline ATR: `{summary['events_with_valid_atr']}`",
        f"- Events missing ATR: `{summary['events_missing_atr']}`",
        f"- Direction-missing rows: `{summary['direction_missing_rows']}`",
        "",
        "## Offline ATR Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for status, count in summary["offline_atr_status_counts"].items():
        lines.append(f"| `{status}` | {count} |")
    lines += [
        "",
        "## Gap Policy Check",
        "",
        f"- Gaps detected: `{summary['gaps_detected']}`",
        f"- Unknown irregular gaps: `{summary['unknown_irregular_gaps']}`",
        "",
        "## Guardrails",
        "",
    ]
    for guardrail in summary["guardrails"]:
        lines.append(f"- {guardrail}")
    lines += [
        "",
        "## Remaining Limitations",
        "",
        "- This checkpoint does not rerun first-touch labels.",
        "- `offline_atr_14` is not runtime EA ATR.",
        "- First-touch interpretation remains blocked until a separate reviewed checkpoint uses ATR-enriched rows.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Checkpoint CC Guardrail Summary",
        "",
        "| Guardrail | Status |",
        "|---|---|",
        "| MT5 run | `NO` |",
        "| Strategy Tester run | `NO` |",
        "| EA/source changed | `NO` |",
        "| Presets changed | `NO` |",
        "| Joiner rerun | `NO` |",
        "| First-touch labels recomputed | `NO` |",
        "| ATR period optimized | `NO` |",
        "| Profitability claim | `NO` |",
        f"| Unknown irregular gaps | `{summary['unknown_irregular_gaps']}` |",
        "",
        "If unknown irregular gaps are greater than zero, the enrichment must not be used for outcome interpretation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich PAF diagnostic rows with offline ATR from H1 bars.")
    parser.add_argument("--bars-csv", default="research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv")
    parser.add_argument("--events-csv", default="research/results/checkpoint_bz_offline_joiner_run/paf_shadow_outcomes_enriched.csv")
    parser.add_argument("--results-root", default="research/results/checkpoint_cc_offline_atr_enrichment")
    parser.add_argument("--atr-period", type=int, default=DEFAULT_ATR_PERIOD)
    parser.add_argument("--output-column", default=DEFAULT_OUTPUT_COLUMN)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.atr_period != DEFAULT_ATR_PERIOD:
        raise SystemExit("NO_ATR_OPTIMIZATION_APPROVED: atr period must remain 14 for Checkpoint CC")
    if args.output_column != DEFAULT_OUTPUT_COLUMN:
        raise SystemExit("SCHEMA_MISMATCH: output column must remain offline_atr_14 for Checkpoint CC")

    bars_path = Path(args.bars_csv)
    events_path = Path(args.events_csv)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    bars = load_bars(bars_path)
    gaps, issues = validate_bars(bars)
    unknown_gaps = [gap for gap in gaps if gap["classification"] == "UNKNOWN_IRREGULAR_GAP"]
    if issues:
        raise SystemExit("BAR_VALIDATION_FAILED: " + "; ".join(issues[:5]))

    events = read_csv(events_path)
    if not events:
        raise SystemExit(f"INPUT_MISSING: no event rows found in {events_path}")

    atr_by_bar = compute_simple_atr_by_bar(bars, args.atr_period)
    enriched, completeness = enrich_events(events, bars, atr_by_bar, args.output_column)
    status_counts = counter_dict([row.get("offline_atr_status") for row in enriched])
    valid_atr = sum(1 for row in enriched if row.get("offline_atr_status") == "ATR_READY")
    missing_atr = sum(1 for row in enriched if row.get("offline_atr_status") == "ATR_MISSING")
    direction_missing = sum(1 for row in enriched if row.get("offline_atr_status") == "DIRECTION_MISSING")

    enriched_csv = results_root / "paf_shadow_outcomes_atr_enriched.csv"
    completeness_csv = results_root / "offline_atr_data_completeness.csv"
    summary_json = results_root / "offline_atr_enrichment_summary.json"
    summary_md = results_root / "offline_atr_enrichment_summary.md"
    guardrail_md = results_root / "offline_atr_guardrail_summary.md"

    extra_fields = [
        args.output_column,
        "offline_atr_status",
        "offline_atr_reason",
        "offline_atr_period",
        "offline_atr_method",
        "offline_atr_alignment_rule",
        "offline_atr_source_start",
        "offline_atr_source_end",
        "offline_atr_bars_used",
    ]
    write_csv(enriched_csv, enriched, fieldnames_for(events, extra_fields))
    write_csv(
        completeness_csv,
        completeness,
        [
            "event_time",
            "classification",
            "direction",
            "entry_reference_price",
            args.output_column,
            "offline_atr_status",
            "offline_atr_reason",
            "lookahead_status",
        ],
    )

    summary = {
        "checkpoint": "CC",
        "status": "PASS_OFFLINE_ATR_ENRICHMENT",
        "bars_csv": str(bars_path),
        "events_csv": str(events_path),
        "bars_read": len(bars),
        "events_read": len(events),
        "atr_period": args.atr_period,
        "output_column": args.output_column,
        "atr_method": "simple_average_true_range",
        "atr_alignment_rule": "completed H1 bars strictly before event bar",
        "events_with_valid_atr": valid_atr,
        "events_missing_atr": missing_atr,
        "direction_missing_rows": direction_missing,
        "offline_atr_status_counts": status_counts,
        "gaps_detected": len(gaps),
        "gap_counts": counter_dict([gap["classification"] for gap in gaps]),
        "unknown_irregular_gaps": len(unknown_gaps),
        "outputs": {
            "enriched_csv": str(enriched_csv),
            "summary_json": str(summary_json),
            "summary_md": str(summary_md),
            "completeness_csv": str(completeness_csv),
            "guardrail_md": str(guardrail_md),
        },
        "guardrails": [
            "offline files only",
            "no MT5 run",
            "no Strategy Tester run",
            "no EA/source changes",
            "no preset changes",
            "no joiner rerun",
            "no first-touch labels recomputed",
            "no optimization",
            "no profitability claim",
        ],
    }

    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary_md(summary_md, summary)
    write_guardrail_md(guardrail_md, summary)

    print(f"Wrote ATR-enriched rows: {enriched_csv}")
    print(f"Wrote summary: {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
