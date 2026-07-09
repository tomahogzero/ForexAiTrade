#!/usr/bin/env python3
"""Offline first-touch relabeling for PAF diagnostics.

This tool reads Checkpoint CC ATR-enriched PAF diagnostic rows and existing
offline H1 bars, then relabels hypothetical first-touch outcomes. It does not
run MT5, does not send orders, does not optimize parameters, and does not prove
profitability.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


BUY = "BUY_CONTEXT"
SELL = "SELL_CONTEXT"
DEFAULT_HORIZONS = [6, 12, 24, 48]
DEFAULT_TP_ATR_MULTIPLE = 1.5
DEFAULT_SL_ATR_MULTIPLE = 1.0
REQUIRED_ATR_COLUMN = "offline_atr_14"


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
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
    }


def load_bars(path: Path) -> list[dict[str, Any]]:
    bars = [bar for row in read_csv(path) if (bar := normalize_bar(row)) is not None]
    bars.sort(key=lambda item: item["time"])
    if not bars:
        raise SystemExit("SCHEMA_MISMATCH: no valid bars found; expected time,open,high,low,close")
    return bars


def find_event_bar_index(bar_index: dict[datetime, int], event_time: datetime) -> int | None:
    return bar_index.get(event_time)


def first_touch_label(
    direction: str,
    entry: float,
    atr: float | None,
    future_bars: list[dict[str, Any]],
    tp_atr: float,
    sl_atr: float,
) -> tuple[str, int | str, str, float | str, float | str]:
    if direction not in {BUY, SELL}:
        return "DIRECTION_MISSING", "", "direction_context is missing or unknown", "", ""
    if atr is None or atr <= 0:
        return "DATA_MISSING", "", "offline_atr_14 is missing or invalid", "", ""
    if not future_bars:
        return "DATA_MISSING", "", "no future bars available for horizon", "", ""

    if direction == BUY:
        tp_price = entry + atr * tp_atr
        sl_price = entry - atr * sl_atr
        for offset, bar in enumerate(future_bars, start=1):
            tp_hit = bar["high"] >= tp_price
            sl_hit = bar["low"] <= sl_price
            if tp_hit and sl_hit:
                return "AMBIGUOUS_SAME_BAR", offset, "tp and sl touched in the same future bar", round(tp_price, 5), round(sl_price, 5)
            if sl_hit:
                return "SL_FIRST", offset, "hypothetical sl touched first", round(tp_price, 5), round(sl_price, 5)
            if tp_hit:
                return "TP_FIRST", offset, "hypothetical tp touched first", round(tp_price, 5), round(sl_price, 5)
    else:
        tp_price = entry - atr * tp_atr
        sl_price = entry + atr * sl_atr
        for offset, bar in enumerate(future_bars, start=1):
            tp_hit = bar["low"] <= tp_price
            sl_hit = bar["high"] >= sl_price
            if tp_hit and sl_hit:
                return "AMBIGUOUS_SAME_BAR", offset, "tp and sl touched in the same future bar", round(tp_price, 5), round(sl_price, 5)
            if sl_hit:
                return "SL_FIRST", offset, "hypothetical sl touched first", round(tp_price, 5), round(sl_price, 5)
            if tp_hit:
                return "TP_FIRST", offset, "hypothetical tp touched first", round(tp_price, 5), round(sl_price, 5)

    return "NO_RESOLUTION", "", "neither hypothetical tp nor sl touched inside horizon", round(tp_price, 5), round(sl_price, 5)


def relabel_row(
    row: dict[str, str],
    bars: list[dict[str, Any]],
    bar_index: dict[datetime, int],
    horizons: list[int],
    tp_atr: float,
    sl_atr: float,
) -> dict[str, Any]:
    output: dict[str, Any] = dict(row)
    event_time = parse_time(row.get("event_time"))
    direction = (row.get("direction") or "").strip()
    entry = to_float(row.get("entry_reference_price"))
    atr_status = (row.get("offline_atr_status") or "").strip()
    atr = to_float(row.get(REQUIRED_ATR_COLUMN))

    base_status = "RELABEL_READY"
    base_reason = ""
    event_index: int | None = None
    if direction not in {BUY, SELL}:
        base_status = "DIRECTION_MISSING"
        base_reason = "direction_context is missing or unknown"
    elif atr_status != "ATR_READY":
        base_status = "DATA_MISSING"
        base_reason = f"offline_atr_status is {atr_status or 'missing'}"
    elif atr is None or atr <= 0:
        base_status = "DATA_MISSING"
        base_reason = "offline_atr_14 is missing or invalid"
    elif event_time is None:
        base_status = "DATA_MISSING"
        base_reason = "event_time could not be parsed"
    elif entry is None:
        base_status = "DATA_MISSING"
        base_reason = "entry_reference_price is missing"
    else:
        event_index = find_event_bar_index(bar_index, event_time)
        if event_index is None:
            base_status = "DATA_MISSING"
            base_reason = "event_time does not match an exported bar timestamp"

    output["ce_relabel_status"] = base_status
    output["ce_relabel_reason"] = base_reason
    output["ce_required_atr_column"] = REQUIRED_ATR_COLUMN
    output["ce_tp_atr_multiple"] = DEFAULT_TP_ATR_MULTIPLE
    output["ce_sl_atr_multiple"] = DEFAULT_SL_ATR_MULTIPLE
    output["ce_alignment_rule"] = "future bars strictly after event bar; offline_atr_14 from completed bars before event bar"

    for horizon in horizons:
        prefix = f"ce_h{horizon}"
        if base_status == "DIRECTION_MISSING":
            output[f"{prefix}_outcome_label"] = "DIRECTION_MISSING"
            output[f"{prefix}_touch_bar"] = ""
            output[f"{prefix}_outcome_reason"] = base_reason
            output[f"{prefix}_bars_available"] = ""
            output[f"{prefix}_tp_price"] = ""
            output[f"{prefix}_sl_price"] = ""
            continue
        if base_status != "RELABEL_READY" or event_index is None:
            output[f"{prefix}_outcome_label"] = "DATA_MISSING"
            output[f"{prefix}_touch_bar"] = ""
            output[f"{prefix}_outcome_reason"] = base_reason
            output[f"{prefix}_bars_available"] = ""
            output[f"{prefix}_tp_price"] = ""
            output[f"{prefix}_sl_price"] = ""
            continue
        future_bars = bars[event_index + 1 : event_index + 1 + horizon]
        output[f"{prefix}_bars_available"] = len(future_bars)
        label, touch_bar, reason, tp_price, sl_price = first_touch_label(direction, entry or 0.0, atr, future_bars, tp_atr, sl_atr)
        output[f"{prefix}_outcome_label"] = label
        output[f"{prefix}_touch_bar"] = touch_bar
        output[f"{prefix}_outcome_reason"] = reason
        output[f"{prefix}_tp_price"] = tp_price
        output[f"{prefix}_sl_price"] = sl_price

    return output


def fieldnames_for(rows: list[dict[str, str]], horizons: list[int]) -> list[str]:
    names = list(rows[0].keys()) if rows else []
    extra = [
        "ce_relabel_status",
        "ce_relabel_reason",
        "ce_required_atr_column",
        "ce_tp_atr_multiple",
        "ce_sl_atr_multiple",
        "ce_alignment_rule",
    ]
    for horizon in horizons:
        prefix = f"ce_h{horizon}"
        extra.extend(
            [
                f"{prefix}_bars_available",
                f"{prefix}_outcome_label",
                f"{prefix}_touch_bar",
                f"{prefix}_outcome_reason",
                f"{prefix}_tp_price",
                f"{prefix}_sl_price",
            ]
        )
    for name in extra:
        if name not in names:
            names.append(name)
    return names


def build_by_horizon(rows: list[dict[str, Any]], horizons: list[int]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for horizon in horizons:
        key = f"ce_h{horizon}_outcome_label"
        counts = counter_dict([row.get(key) for row in rows])
        for label, count in counts.items():
            output.append({"horizon": horizon, "outcome_label": label, "count": count})
    return output


def write_summary_md(path: Path, summary: dict[str, Any], horizons: list[int]) -> None:
    lines = [
        "# Checkpoint CE: PAF Offline First-Touch Relabel Summary",
        "",
        "This is an offline diagnostic artifact. It does not run MT5, does not send orders, does not optimize parameters, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"- Status: `{summary['status']}`",
        f"- Required ATR column: `{summary['required_atr_column']}`",
        f"- TP ATR multiple: `{summary['tp_atr_multiple']}`",
        f"- SL ATR multiple: `{summary['sl_atr_multiple']}`",
        f"- Horizons: `{','.join(str(item) for item in horizons)}`",
        "",
        "## Counts",
        "",
        f"- Rows read: `{summary['rows_read']}`",
        f"- Relabel-ready rows: `{summary['relabel_ready_rows']}`",
        f"- Data-missing rows: `{summary['data_missing_rows']}`",
        f"- Direction-missing rows: `{summary['direction_missing_rows']}`",
        "",
        "## Outcome Labels By Horizon",
        "",
    ]
    for horizon in horizons:
        lines += [
            f"### Horizon {horizon}",
            "",
            "| Label | Count |",
            "|---|---:|",
        ]
        for label, count in summary["outcome_counts_by_horizon"].get(str(horizon), {}).items():
            lines.append(f"| `{label}` | {count} |")
        lines.append("")
    lines += [
        "## Guardrails",
        "",
    ]
    for guardrail in summary["guardrails"]:
        lines.append(f"- {guardrail}")
    lines += [
        "",
        "## Limitations",
        "",
        "- Labels are hypothetical shadow diagnostics, not real orders.",
        "- OHLC bars cannot prove tick order inside the same bar.",
        "- `AMBIGUOUS_SAME_BAR` is used when TP and SL touch in the same bar.",
        "- This summary is not a profitability assessment.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_md(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Checkpoint CE Guardrail Summary",
        "",
        "| Guardrail | Status |",
        "|---|---|",
        "| MT5 run | `NO` |",
        "| Strategy Tester run | `NO` |",
        "| EA/source changed | `NO` |",
        "| Presets changed | `NO` |",
        "| Order action generated | `NO` |",
        "| Optimization | `NO` |",
        "| Profitability claim | `NO` |",
        f"| Required ATR column | `{summary['required_atr_column']}` |",
        f"| TP/SL multiples fixed | `{summary['tp_atr_multiple']} / {summary['sl_atr_multiple']}` |",
        "",
        "These labels are offline observations only and must not be converted into orders.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_horizons(value: str) -> list[int]:
    horizons: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if item:
            horizons.append(int(item))
    if horizons != DEFAULT_HORIZONS:
        raise argparse.ArgumentTypeError("Checkpoint CE requires horizons 6,12,24,48")
    return horizons


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Relabel PAF first-touch outcomes using offline_atr_14.")
    parser.add_argument("--events-csv", default="research/results/checkpoint_cc_offline_atr_enrichment/paf_shadow_outcomes_atr_enriched.csv")
    parser.add_argument("--bars-csv", default="research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv")
    parser.add_argument("--results-root", default="research/results/checkpoint_ce_paf_first_touch_relabel")
    parser.add_argument("--horizons", type=parse_horizons, default=DEFAULT_HORIZONS)
    parser.add_argument("--tp-atr-multiple", type=float, default=DEFAULT_TP_ATR_MULTIPLE)
    parser.add_argument("--sl-atr-multiple", type=float, default=DEFAULT_SL_ATR_MULTIPLE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.tp_atr_multiple != DEFAULT_TP_ATR_MULTIPLE or args.sl_atr_multiple != DEFAULT_SL_ATR_MULTIPLE:
        raise SystemExit("NO_OPTIMIZATION_APPROVED: TP/SL multiples must remain 1.5 / 1.0 for Checkpoint CE")

    events_path = Path(args.events_csv)
    bars_path = Path(args.bars_csv)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    events = read_csv(events_path)
    if not events:
        raise SystemExit(f"INPUT_MISSING: no event rows found in {events_path}")
    if REQUIRED_ATR_COLUMN not in events[0]:
        raise SystemExit(f"SCHEMA_MISMATCH: required ATR column missing: {REQUIRED_ATR_COLUMN}")

    bars = load_bars(bars_path)
    bar_index = {bar["time"]: index for index, bar in enumerate(bars)}
    relabeled = [
        relabel_row(row, bars, bar_index, args.horizons, args.tp_atr_multiple, args.sl_atr_multiple)
        for row in events
    ]

    by_horizon = build_by_horizon(relabeled, args.horizons)
    outcome_counts_by_horizon = {
        str(horizon): counter_dict([row.get(f"ce_h{horizon}_outcome_label") for row in relabeled])
        for horizon in args.horizons
    }
    status_counts = counter_dict([row.get("ce_relabel_status") for row in relabeled])

    output_csv = results_root / "paf_shadow_outcomes_first_touch_relabel.csv"
    summary_json = results_root / "first_touch_relabel_summary.json"
    summary_md = results_root / "first_touch_relabel_summary.md"
    by_horizon_csv = results_root / "first_touch_relabel_by_horizon.csv"
    guardrail_md = results_root / "first_touch_relabel_guardrail_summary.md"

    write_csv(output_csv, relabeled, fieldnames_for(events, args.horizons))
    write_csv(by_horizon_csv, by_horizon, ["horizon", "outcome_label", "count"])

    summary = {
        "checkpoint": "CE",
        "status": "PASS_OFFLINE_FIRST_TOUCH_RELABEL",
        "events_csv": str(events_path),
        "bars_csv": str(bars_path),
        "rows_read": len(events),
        "relabel_ready_rows": status_counts.get("RELABEL_READY", 0),
        "data_missing_rows": status_counts.get("DATA_MISSING", 0),
        "direction_missing_rows": status_counts.get("DIRECTION_MISSING", 0),
        "relabel_status_counts": status_counts,
        "required_atr_column": REQUIRED_ATR_COLUMN,
        "tp_atr_multiple": args.tp_atr_multiple,
        "sl_atr_multiple": args.sl_atr_multiple,
        "horizons": args.horizons,
        "outcome_counts_by_horizon": outcome_counts_by_horizon,
        "outputs": {
            "relabeled_csv": str(output_csv),
            "summary_json": str(summary_json),
            "summary_md": str(summary_md),
            "by_horizon_csv": str(by_horizon_csv),
            "guardrail_md": str(guardrail_md),
        },
        "guardrails": [
            "offline files only",
            "no MT5 run",
            "no Strategy Tester run",
            "no EA/source changes",
            "no preset changes",
            "no orders",
            "no optimization",
            "no profitability claim",
        ],
    }
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary_md(summary_md, summary, args.horizons)
    write_guardrail_md(guardrail_md, summary)

    print(f"Wrote relabeled rows: {output_csv}")
    print(f"Wrote summary: {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
