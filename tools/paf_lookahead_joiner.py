#!/usr/bin/env python3
"""Offline PAF lookahead joiner.

This tool joins Price Action/Fibo diagnostic shadow rows with an exported OHLC
bar series. It does not run MT5, does not send orders, and must not be used by
the EA trading decision path.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_HORIZONS = [6, 12, 24, 48]
BUY = "BUY_CONTEXT"
SELL = "SELL_CONTEXT"


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
        raise SystemExit(f"Missing CSV file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def normalize_bar(row: dict[str, str]) -> dict[str, Any] | None:
    time_value = row.get("time") or row.get("Time") or row.get("datetime") or row.get("DateTime")
    bar_time = parse_time(time_value)
    if bar_time is None:
        return None

    open_price = to_float(row.get("open") or row.get("Open"))
    high = to_float(row.get("high") or row.get("High"))
    low = to_float(row.get("low") or row.get("Low"))
    close = to_float(row.get("close") or row.get("Close"))
    if None in (open_price, high, low, close):
        return None

    return {
        "time": bar_time,
        "time_text": time_value,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
    }


def load_bars(path: Path) -> list[dict[str, Any]]:
    bars = [bar for row in read_csv(path) if (bar := normalize_bar(row)) is not None]
    bars.sort(key=lambda item: item["time"])
    if not bars:
        raise SystemExit(
            "No valid bars found. Expected columns: time, open, high, low, close "
            "(case-insensitive Time/Open/High/Low/Close also accepted)."
        )
    return bars


def find_event_bar_index(bars: list[dict[str, Any]], event_time: datetime) -> int | None:
    for index, bar in enumerate(bars):
        if bar["time"] == event_time:
            return index
    return None


def price_excursions(direction: str, entry: float, future_bars: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    if not future_bars:
        return None, None
    if direction == BUY:
        mfe = max(bar["high"] - entry for bar in future_bars)
        mae = max(entry - bar["low"] for bar in future_bars)
    elif direction == SELL:
        mfe = max(entry - bar["low"] for bar in future_bars)
        mae = max(bar["high"] - entry for bar in future_bars)
    else:
        return None, None
    return round(mfe, 5), round(mae, 5)


def first_touch_label(
    direction: str,
    entry: float,
    atr: float | None,
    future_bars: list[dict[str, Any]],
    tp_atr: float,
    sl_atr: float,
) -> tuple[str, int | str, str]:
    if direction not in {BUY, SELL}:
        return "DIRECTION_MISSING", "", "direction_context is missing or unknown"
    if atr is None or atr <= 0:
        return "DATA_MISSING", "", "atr is missing or invalid"
    if not future_bars:
        return "DATA_MISSING", "", "no future bars available for horizon"

    if direction == BUY:
        tp_price = entry + atr * tp_atr
        sl_price = entry - atr * sl_atr
        for offset, bar in enumerate(future_bars, start=1):
            tp_hit = bar["high"] >= tp_price
            sl_hit = bar["low"] <= sl_price
            if tp_hit and sl_hit:
                return "AMBIGUOUS_SAME_BAR", offset, "tp and sl touched in the same future bar"
            if sl_hit:
                return "SL_FIRST", offset, "hypothetical sl touched first"
            if tp_hit:
                return "TP_FIRST", offset, "hypothetical tp touched first"
    else:
        tp_price = entry - atr * tp_atr
        sl_price = entry + atr * sl_atr
        for offset, bar in enumerate(future_bars, start=1):
            tp_hit = bar["low"] <= tp_price
            sl_hit = bar["high"] >= sl_price
            if tp_hit and sl_hit:
                return "AMBIGUOUS_SAME_BAR", offset, "tp and sl touched in the same future bar"
            if sl_hit:
                return "SL_FIRST", offset, "hypothetical sl touched first"
            if tp_hit:
                return "TP_FIRST", offset, "hypothetical tp touched first"

    return "NO_RESOLUTION", "", "neither hypothetical tp nor sl touched inside horizon"


def enrich_row(
    row: dict[str, str],
    bars: list[dict[str, Any]],
    horizons: list[int],
    tp_atr: float,
    sl_atr: float,
) -> dict[str, Any]:
    enriched: dict[str, Any] = dict(row)
    event_time = parse_time(row.get("event_time"))
    direction = (row.get("direction") or "").strip()
    entry = to_float(row.get("entry_reference_price"))
    atr = to_float(row.get("atr"))

    if atr is None:
        # Older shadow rows may not carry ATR; keep the explicit limitation.
        atr = to_float(row.get("diagnostic_atr"))

    if direction not in {BUY, SELL}:
        enriched["lookahead_status"] = "DIRECTION_MISSING"
        enriched["lookahead_limitation"] = "direction_context is missing or unknown"
        return enriched
    if event_time is None:
        enriched["lookahead_status"] = "DATA_MISSING"
        enriched["lookahead_limitation"] = "event_time could not be parsed"
        return enriched
    if entry is None:
        enriched["lookahead_status"] = "DATA_MISSING"
        enriched["lookahead_limitation"] = "entry_reference_price is missing"
        return enriched

    event_index = find_event_bar_index(bars, event_time)
    if event_index is None:
        enriched["lookahead_status"] = "DATA_MISSING"
        enriched["lookahead_limitation"] = "event_time does not match an exported bar timestamp"
        return enriched

    enriched["lookahead_status"] = "JOINED"
    enriched["lookahead_alignment_rule"] = "exact event_time match; future bars strictly after event bar"
    enriched["lookahead_bar_time"] = bars[event_index]["time"].strftime("%Y-%m-%d %H:%M:%S")

    for horizon in horizons:
        future_bars = bars[event_index + 1 : event_index + 1 + horizon]
        prefix = f"h{horizon}"
        enriched[f"{prefix}_bars_available"] = len(future_bars)
        if not future_bars:
            enriched[f"{prefix}_outcome_label"] = "DATA_MISSING"
            enriched[f"{prefix}_outcome_reason"] = "no future bars available"
            continue

        mfe, mae = price_excursions(direction, entry, future_bars)
        enriched[f"{prefix}_mfe"] = mfe
        enriched[f"{prefix}_mae"] = mae
        enriched[f"{prefix}_future_high"] = round(max(bar["high"] for bar in future_bars), 5)
        enriched[f"{prefix}_future_low"] = round(min(bar["low"] for bar in future_bars), 5)
        enriched[f"{prefix}_future_close"] = round(future_bars[-1]["close"], 5)
        label, touch_bar, reason = first_touch_label(direction, entry, atr, future_bars, tp_atr, sl_atr)
        enriched[f"{prefix}_outcome_label"] = label
        enriched[f"{prefix}_touch_bar"] = touch_bar
        enriched[f"{prefix}_outcome_reason"] = reason

    return enriched


def counter_dict(items: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(item) for item in items if item not in (None, "")).items(), key=lambda item: (-item[1], item[0])))


def write_summary(path: Path, rows: list[dict[str, Any]], horizons: list[int], args: argparse.Namespace) -> None:
    joined = [row for row in rows if row.get("lookahead_status") == "JOINED"]
    lines = [
        "# PAF Lookahead Join Summary",
        "",
        "This is an offline diagnostic summary. It does not run MT5, does not send orders, and does not prove profitability.",
        "",
        "## Inputs",
        "",
        f"- Shadow outcomes CSV: `{args.shadow_outcomes}`",
        f"- Bars CSV: `{args.bars_csv}`",
        f"- TP ATR multiple: `{args.tp_atr_multiple}`",
        f"- SL ATR multiple: `{args.sl_atr_multiple}`",
        f"- Horizons: `{','.join(str(h) for h in horizons)}`",
        "",
        "## Join Status",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for key, value in counter_dict(row.get("lookahead_status") for row in rows).items():
        lines.append(f"| `{key}` | {value} |")

    lines += [
        "",
        "## Outcome Labels By Horizon",
        "",
    ]
    for horizon in horizons:
        key = f"h{horizon}_outcome_label"
        lines += [
            f"### Horizon {horizon} Bars",
            "",
            "| Outcome | Count |",
            "|---|---:|",
        ]
        for label, count in counter_dict(row.get(key) for row in joined).items():
            lines.append(f"| `{label}` | {count} |")
        if not joined:
            lines.append("| n/a | 0 |")
        lines.append("")

    lines += [
        "## Guardrails",
        "",
        "- Lookahead data is used only after diagnostic events have been logged.",
        "- The output is for offline research only.",
        "- No market orders, pending orders, or position modifications are generated.",
        "- This is not an optimization result and not a profitability claim.",
        "",
        "## Limitations",
        "",
        "- Bar OHLC cannot prove tick order inside a bar.",
        "- Same-bar TP/SL ambiguity is labeled conservatively as `AMBIGUOUS_SAME_BAR`.",
        "- Missing timestamps or missing ATR keep rows in `DATA_MISSING` rather than guessing.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_fieldnames(input_rows: list[dict[str, str]], horizons: list[int]) -> list[str]:
    names = list(input_rows[0].keys()) if input_rows else []
    extra = ["lookahead_status", "lookahead_limitation", "lookahead_alignment_rule", "lookahead_bar_time"]
    for horizon in horizons:
        prefix = f"h{horizon}"
        extra.extend(
            [
                f"{prefix}_bars_available",
                f"{prefix}_mfe",
                f"{prefix}_mae",
                f"{prefix}_future_high",
                f"{prefix}_future_low",
                f"{prefix}_future_close",
                f"{prefix}_outcome_label",
                f"{prefix}_touch_bar",
                f"{prefix}_outcome_reason",
            ]
        )
    for name in extra:
        if name not in names:
            names.append(name)
    return names


def parse_horizons(value: str) -> list[int]:
    horizons = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        horizon = int(item)
        if horizon <= 0:
            raise argparse.ArgumentTypeError("horizons must be positive integers")
        horizons.append(horizon)
    if not horizons:
        raise argparse.ArgumentTypeError("at least one horizon is required")
    return horizons


def main() -> int:
    parser = argparse.ArgumentParser(description="Join PAF diagnostic shadow rows with offline OHLC lookahead bars.")
    parser.add_argument("--shadow-outcomes", default="research/results/paf_shadow_outcomes_all_cases.csv")
    parser.add_argument("--bars-csv", required=True, help="CSV with time, open, high, low, close columns.")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--horizons", type=parse_horizons, default=DEFAULT_HORIZONS, help="Comma-separated future bar horizons.")
    parser.add_argument("--tp-atr-multiple", type=float, default=1.5)
    parser.add_argument("--sl-atr-multiple", type=float, default=1.0)
    args = parser.parse_args()

    if args.tp_atr_multiple <= 0 or args.sl_atr_multiple <= 0:
        raise SystemExit("TP/SL ATR multiples must be positive.")

    shadow_path = Path(args.shadow_outcomes)
    bars_path = Path(args.bars_csv)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    shadow_rows = read_csv(shadow_path)
    if not shadow_rows:
        raise SystemExit(f"No shadow outcome rows found in {shadow_path}")
    bars = load_bars(bars_path)

    enriched = [enrich_row(row, bars, args.horizons, args.tp_atr_multiple, args.sl_atr_multiple) for row in shadow_rows]
    output_csv = results_root / "paf_shadow_outcomes_enriched.csv"
    output_json = results_root / "paf_lookahead_join_summary.json"
    output_md = results_root / "paf_lookahead_join_summary.md"

    write_csv(output_csv, enriched, output_fieldnames(shadow_rows, args.horizons))
    summary = {
        "shadow_outcomes": str(shadow_path),
        "bars_csv": str(bars_path),
        "rows": len(enriched),
        "join_status_counts": counter_dict(row.get("lookahead_status") for row in enriched),
        "horizons": args.horizons,
        "tp_atr_multiple": args.tp_atr_multiple,
        "sl_atr_multiple": args.sl_atr_multiple,
        "guardrails": [
            "offline diagnostic analysis only",
            "no MT5 run",
            "no orders",
            "no optimization",
            "no profitability claim",
        ],
    }
    output_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary(output_md, enriched, args.horizons, args)

    print(f"Wrote enriched rows: {output_csv}")
    print(f"Wrote summary: {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
