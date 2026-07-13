#!/usr/bin/env python3
"""Run the offline fail-closed Checkpoint EU first-touch diagnostic."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path


HORIZONS = (6, 12, 24, 48)
TP_MULT = 1.5
SL_MULT = 1.0


def parse_time(value: str) -> datetime:
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            pass
    raise ValueError(value)


def load_bars(paths: list[Path]) -> tuple[list[dict[str, object]], int]:
    bars: list[dict[str, object]] = []
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                bars.append({
                    "time": parse_time(f"{row['<DATE>']} {row['<TIME>']}"),
                    "open": float(row["<OPEN>"]),
                    "high": float(row["<HIGH>"]),
                    "low": float(row["<LOW>"]),
                    "close": float(row["<CLOSE>"]),
                    "source_file": path.name,
                })
    bars.sort(key=lambda row: row["time"])
    unique: list[dict[str, object]] = []
    seen: dict[datetime, dict[str, object]] = {}
    duplicates = 0
    for bar in bars:
        time = bar["time"]
        assert isinstance(time, datetime)
        if time in seen:
            duplicates += 1
            if any(seen[time][field] != bar[field] for field in ("open", "high", "low", "close")):
                raise ValueError(f"conflicting duplicate bar timestamp: {time:%Y-%m-%d %H:%M:%S}")
            continue
        seen[time] = bar
        unique.append(bar)
    return unique, duplicates


def first_touch(direction: str, entry: float, atr: float, bars: list[dict[str, object]]) -> tuple[str, int | str]:
    if direction == "BUY":
        tp, sl = entry + TP_MULT * atr, entry - SL_MULT * atr
    else:
        tp, sl = entry - TP_MULT * atr, entry + SL_MULT * atr
    for number, bar in enumerate(bars, start=1):
        high, low = float(bar["high"]), float(bar["low"])
        tp_hit = high >= tp if direction == "BUY" else low <= tp
        sl_hit = low <= sl if direction == "BUY" else high >= sl
        if tp_hit and sl_hit:
            return "AMBIGUOUS_SAME_BAR", number
        if sl_hit:
            return "SL_FIRST", number
        if tp_hit:
            return "TP_FIRST", number
    return "NO_RESOLUTION", ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline fail-closed EU shadow diagnostic.")
    parser.add_argument("--events-csv", required=True)
    parser.add_argument("--gap-policy-csv", required=True)
    parser.add_argument("--raw-bars-csv", action="append", required=True)
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    raw_paths = [Path(path) for path in args.raw_bars_csv]
    if len(raw_paths) != 3:
        raise SystemExit("Checkpoint EU requires exactly three yearly raw H1 CSV files.")
    bars, duplicates = load_bars(raw_paths)
    if not bars:
        raise SystemExit("No bars loaded.")
    index = {bar["time"]: number for number, bar in enumerate(bars)}

    with Path(args.gap_policy_csv).open(encoding="utf-8-sig", newline="") as handle:
        policy_rows = list(csv.DictReader(handle))
    blocked = {
        (parse_time(row["prev_time"]), parse_time(row["next_time"]))
        for row in policy_rows
        if row["policy_status"].startswith("BLOCKED")
    }
    accepted = {
        (parse_time(row["prev_time"]), parse_time(row["next_time"]))
        for row in policy_rows
        if row["policy_status"].startswith("ACCEPTED")
    }
    with Path(args.events_csv).open(encoding="utf-8-sig", newline="") as handle:
        events = list(csv.DictReader(handle))
    if len(events) != 1600:
        raise SystemExit(f"Checkpoint EU requires 1600 EM eligible events, got {len(events)}.")

    output: list[dict[str, object]] = []
    for event in events:
        row: dict[str, object] = dict(event)
        event_time = parse_time(event["event_time"])
        direction = event["paf_candidate_direction"].strip().upper()
        if direction not in {"BUY", "SELL"}:
            raise SystemExit(f"Invalid frozen direction: {direction}")
        entry, atr = float(event["entry_reference_price"]), float(event["atr"])
        event_index = index.get(event_time)
        row["shadow_event_status"] = "EVENT_MATCHED" if event_index is not None else "DATA_INCOMPLETE_EVENT_BAR_MISSING"
        for horizon in HORIZONS:
            prefix = f"h{horizon}"
            if event_index is None:
                row.update({
                    f"{prefix}_bars_available": "0",
                    f"{prefix}_eligibility": "EXCLUDED",
                    f"{prefix}_exclusion_reason": "EVENT_BAR_MISSING",
                    f"{prefix}_outcome": "",
                    f"{prefix}_touch_bar": "",
                })
                continue
            sequence = bars[event_index + 1:event_index + 1 + horizon]
            row[f"{prefix}_bars_available"] = str(len(sequence))
            if len(sequence) < horizon:
                row.update({
                    f"{prefix}_eligibility": "EXCLUDED",
                    f"{prefix}_exclusion_reason": "INSUFFICIENT_FUTURE_BARS",
                    f"{prefix}_outcome": "",
                    f"{prefix}_touch_bar": "",
                })
                continue
            previous = bars[event_index]
            traversed: list[tuple[datetime, datetime]] = []
            blocked_detail = ""
            for bar in sequence:
                previous_time, current_time = previous["time"], bar["time"]
                assert isinstance(previous_time, datetime) and isinstance(current_time, datetime)
                if current_time - previous_time > timedelta(hours=1):
                    pair = (previous_time, current_time)
                    traversed.append(pair)
                    if pair in blocked:
                        blocked_detail = f"{previous_time:%Y-%m-%d %H:%M:%S}->{current_time:%Y-%m-%d %H:%M:%S}"
                        break
                    if pair not in accepted:
                        blocked_detail = f"UNREGISTERED:{previous_time:%Y-%m-%d %H:%M:%S}->{current_time:%Y-%m-%d %H:%M:%S}"
                        break
                previous = bar
            row[f"{prefix}_accepted_closures_crossed"] = str(len(traversed))
            if blocked_detail:
                row.update({
                    f"{prefix}_eligibility": "EXCLUDED",
                    f"{prefix}_exclusion_reason": "BLOCKED_GAP_INSIDE_LOOKAHEAD",
                    f"{prefix}_gap_detail": blocked_detail,
                    f"{prefix}_outcome": "",
                    f"{prefix}_touch_bar": "",
                })
                continue
            outcome, touch = first_touch(direction, entry, atr, sequence)
            row.update({
                f"{prefix}_eligibility": "INCLUDED",
                f"{prefix}_exclusion_reason": "",
                f"{prefix}_outcome": outcome,
                f"{prefix}_touch_bar": touch,
                f"{prefix}_future_high": max(float(bar["high"]) for bar in sequence),
                f"{prefix}_future_low": min(float(bar["low"]) for bar in sequence),
                f"{prefix}_future_close": float(sequence[-1]["close"]),
            })
        output.append(row)

    results = Path(args.results_root)
    results.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in output:
        for field in row:
            if field not in fields:
                fields.append(field)
    outcomes_path = results / "checkpoint_eu_fail_closed_shadow_outcomes.csv"
    with outcomes_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)

    summary: dict[str, object] = {
        "execution_status": "PASS",
        "method": "offline fail-closed event/horizon exclusion",
        "events_total": len(output),
        "bars_total": len(bars),
        "bars_from": bars[0]["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "bars_to": bars[-1]["time"].strftime("%Y-%m-%d %H:%M:%S"),
        "duplicate_bar_timestamps_ignored": duplicates,
        "input_files": [path.name for path in raw_paths],
        "gap_policy": "EO accepted daily/weekend gaps allowed; 28 blocked gaps excluded",
        "accepted_gap_count": len(accepted),
        "blocked_gap_count": len(blocked),
        "tp_atr_multiple": TP_MULT,
        "sl_atr_multiple": SL_MULT,
        "horizons": {},
        "strategy_performance_status": "NOT_EVALUATED",
        "order_logic_status": "NOT_APPROVED",
        "paf_status": "NOT_READY_FOR_ORDER_LOGIC",
        "profitability_claim": False,
        "guardrails": [
            "offline only", "no MT5 or Strategy Tester", "no price filling/interpolation",
            "no gap bridging", "no order logic", "no optimization", "no profitability claim",
        ],
    }
    horizons = summary["horizons"]
    assert isinstance(horizons, dict)
    for horizon in HORIZONS:
        included = [row for row in output if row[f"h{horizon}_eligibility"] == "INCLUDED"]
        excluded = [row for row in output if row[f"h{horizon}_eligibility"] == "EXCLUDED"]
        horizons[str(horizon)] = {
            "included": len(included),
            "excluded": len(excluded),
            "inclusion_rate_pct": round(len(included) / len(output) * 100, 2),
            "exclusion_rate_pct": round(len(excluded) / len(output) * 100, 2),
            "outcomes": dict(Counter(str(row[f"h{horizon}_outcome"]) for row in included)),
            "exclusion_reasons": dict(Counter(str(row[f"h{horizon}_exclusion_reason"]) for row in excluded)),
        }
    (results / "checkpoint_eu_fail_closed_shadow_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    markdown = ["# Checkpoint EU Fail-Closed Shadow Analysis", "", "Offline diagnostic only. Strategy performance is not evaluated.", ""]
    markdown.extend(f"- {key}: `{value}`" for key, value in summary.items() if key != "horizons")
    (results / "checkpoint_eu_fail_closed_shadow_summary.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
