#!/usr/bin/env python3
"""Aggregate controlled exit-variant research results for Checkpoint H."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


EXIT_CLASSES = [
    "INITIAL_SL_LOSS",
    "BREAKEVEN_SL",
    "TRAILING_SL_PROFIT",
    "TP_HIT",
    "OTHER_CLOSE",
    "UNKNOWN",
]


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int:
    value_float = to_float(value)
    return int(value_float) if value_float is not None else 0


def avg(values: list[float]) -> float | None:
    return round(mean(values), 6) if values else None


def fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value).replace("|", "/")


def collect_phase_row(case_dir: Path) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    status = load_json(case_dir / "status.json")
    parsed = load_json(case_dir / "parsed_result.json")
    trade_ledger = load_json(case_dir / "trade_ledger.json")
    telemetry_rows = read_csv(case_dir / "exit_telemetry.csv")
    close_rows = [row for row in telemetry_rows if row.get("event") == "CLOSE"]
    ledger_rows = trade_ledger if isinstance(trade_ledger, list) else []
    ledger_profit_values = [to_float(row.get("total_profit")) for row in ledger_rows if isinstance(row, dict)]
    ledger_profit_values = [value for value in ledger_profit_values if value is not None]
    win_rate_pct = None
    if ledger_profit_values:
        wins = len([value for value in ledger_profit_values if value > 0.0])
        win_rate_pct = round((wins / len(ledger_profit_values)) * 100.0, 2)

    class_counts: dict[str, int] = {}
    class_avg_r: dict[str, float | None] = {}
    total_realized_r = 0.0
    for exit_class in EXIT_CLASSES:
        rows = [row for row in close_rows if (row.get("exit_classification") or "UNKNOWN") == exit_class]
        r_values = [v for v in (to_float(row.get("realized_r")) for row in rows) if v is not None]
        class_counts[exit_class] = len(rows)
        class_avg_r[exit_class] = avg(r_values)
        total_realized_r += sum(r_values)

    variant = case.get("exit_variant") or infer_variant(str(case.get("base_case_id") or case.get("case_id") or ""))
    row: dict[str, Any] = {
        "run_id": case.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or case_dir.name,
        "base_case_id": case.get("base_case_id"),
        "exit_variant": variant,
        "phase": case.get("phase"),
        "symbol": case.get("actual_symbol"),
        "timeframe": case.get("timeframe"),
        "deposit": case.get("deposit"),
        "use_trailing_stop": case.get("use_trailing_stop"),
        "trailing_atr_multiplier": case.get("trailing_atr_multiplier"),
        "execution_status": status.get("execution_status", "UNKNOWN") if isinstance(status, dict) else "UNKNOWN",
        "net_profit": parsed.get("net_profit") if isinstance(parsed, dict) else None,
        "profit_factor": parsed.get("profit_factor") if isinstance(parsed, dict) else None,
        "drawdown": parsed.get("relative_drawdown") if isinstance(parsed, dict) else None,
        "max_drawdown": parsed.get("max_drawdown") if isinstance(parsed, dict) else None,
        "trade_count": parsed.get("total_trades") if isinstance(parsed, dict) else None,
        "win_rate": win_rate_pct,
        "max_consecutive_losses": parsed.get("consecutive_losses") if isinstance(parsed, dict) else None,
        "largest_win": parsed.get("largest_win") if isinstance(parsed, dict) else None,
        "largest_loss": parsed.get("largest_loss") if isinstance(parsed, dict) else None,
        "telemetry_close_events": len(close_rows),
        "total_realized_r": round(total_realized_r, 6),
    }
    for exit_class in EXIT_CLASSES:
        key = exit_class.lower()
        row[f"{key}_count"] = class_counts[exit_class]
        row[f"{key}_avg_r"] = class_avg_r[exit_class]
    return row


def infer_variant(case_id: str) -> str:
    lowered = case_id.lower()
    if "no_trailing" in lowered:
        return "no_trailing"
    if "tighter" in lowered:
        return "trailing_tighter"
    if "looser" in lowered:
        return "trailing_looser"
    return "baseline"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def phase_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[str(row.get("exit_variant"))][str(row.get("phase"))] = row
    return grouped


def positive_phase(row: dict[str, Any] | None, min_trades: int) -> bool:
    if not row or row.get("execution_status") != "PASS":
        return False
    return (to_float(row.get("net_profit")) or 0.0) > 0.0 and to_int(row.get("trade_count")) >= min_trades


def sum_for_phases(phases: dict[str, dict[str, Any]], field: str, names: tuple[str, ...]) -> float:
    return sum(to_float(phases.get(name, {}).get(field)) or 0.0 for name in names)


def classify_variants(rows: list[dict[str, Any]], min_trades: int = 50) -> list[dict[str, Any]]:
    grouped = phase_map(rows)
    baseline = grouped.get("baseline", {})
    baseline_val_oos_sl = sum_for_phases(baseline, "initial_sl_loss_count", ("validation", "out_of_sample"))
    baseline_val_oos_dd = max((to_float(baseline.get(name, {}).get("drawdown")) or 0.0) for name in ("validation", "out_of_sample"))
    baseline_train_net = to_float(baseline.get("train", {}).get("net_profit")) or 0.0

    output: list[dict[str, Any]] = []
    for variant, phases in sorted(grouped.items()):
        train = phases.get("train")
        validation = phases.get("validation")
        oos = phases.get("out_of_sample")
        failed = []

        if variant == "baseline":
            classification = "BASELINE_REFERENCE"
        elif any((phases.get(name, {}).get("execution_status") != "PASS") for name in ("train", "validation", "out_of_sample")):
            classification = "REJECT_FOR_NOW"
            failed.append("execution_status")
        elif not validation or not oos:
            classification = "REJECT_FOR_NOW"
            failed.append("missing_validation_or_oos")
        elif to_int(validation.get("trade_count")) < min_trades or to_int(oos.get("trade_count")) < min_trades:
            classification = "INSUFFICIENT_TRADES"
            failed.append("validation_or_oos_trade_count")
        elif not positive_phase(validation, min_trades) or not positive_phase(oos, min_trades):
            classification = "REJECT_FOR_NOW"
            failed.append("validation_or_oos_not_positive")
        else:
            val_oos_sl = sum_for_phases(phases, "initial_sl_loss_count", ("validation", "out_of_sample"))
            val_oos_dd = max((to_float(phases.get(name, {}).get("drawdown")) or 0.0) for name in ("validation", "out_of_sample"))
            train_net = to_float(train.get("net_profit")) if train else None
            val_oos_net = sum_for_phases(phases, "net_profit", ("validation", "out_of_sample"))
            largest_win = max((to_float(phases.get(name, {}).get("largest_win")) or 0.0) for name in ("validation", "out_of_sample"))
            drawdown_worse = baseline_val_oos_dd > 0 and val_oos_dd > baseline_val_oos_dd * 1.25
            sl_worse = baseline_val_oos_sl > 0 and val_oos_sl > baseline_val_oos_sl * 1.20
            train_danger = train_net is not None and train_net < baseline_train_net - 100.0
            concentrated = val_oos_net > 0 and largest_win * 2.0 >= val_oos_net

            if drawdown_worse:
                failed.append("drawdown_materially_worse_vs_baseline")
            if sl_worse:
                failed.append("initial_sl_losses_materially_worse_vs_baseline")
            if train_danger:
                failed.append("train_dangerously_worse_than_baseline")
            if concentrated:
                failed.append("performance_may_be_concentrated")

            if drawdown_worse or sl_worse or train_danger:
                classification = "EXIT_VARIANT_RISKY"
            elif concentrated:
                classification = "RESEARCH_MORE"
            else:
                classification = "EXIT_VARIANT_PROMISING"

        output.append({
            "exit_variant": variant,
            "classification": classification,
            "failed_gates": ",".join(failed),
            "train_net_profit": train.get("net_profit") if train else None,
            "validation_net_profit": validation.get("net_profit") if validation else None,
            "out_of_sample_net_profit": oos.get("net_profit") if oos else None,
            "validation_trades": validation.get("trade_count") if validation else None,
            "out_of_sample_trades": oos.get("trade_count") if oos else None,
            "validation_oos_initial_sl_losses": sum_for_phases(phases, "initial_sl_loss_count", ("validation", "out_of_sample")),
            "validation_oos_trailing_profit_exits": sum_for_phases(phases, "trailing_sl_profit_count", ("validation", "out_of_sample")),
            "validation_oos_tp_hits": sum_for_phases(phases, "tp_hit_count", ("validation", "out_of_sample")),
            "validation_oos_total_realized_r": round(sum_for_phases(phases, "total_realized_r", ("validation", "out_of_sample")), 6),
            "notes": "No final candidate approval in Checkpoint H.",
        })
    return output


def write_markdown(path: Path, run_id: str, rows: list[dict[str, Any]], scores: list[dict[str, Any]]) -> None:
    lines = [
        "# Checkpoint H Exit Variant Telemetry Summary",
        "",
        f"Selected RunId: `{run_id}`",
        "",
        "This is a controlled, pre-registered diagnostic comparison. It is not optimization and does not approve a final candidate.",
        "",
        "## Variant Phase Results",
        "",
        "| Variant | Phase | Status | Net | PF | DD | Trades | Initial SL Loss | Breakeven | Trailing Profit | TP Hit | Total R |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: (str(r.get("exit_variant")), str(r.get("phase")))):
        lines.append(
            f"| {fmt(row.get('exit_variant'))} | {fmt(row.get('phase'))} | {fmt(row.get('execution_status'))} | "
            f"{fmt(row.get('net_profit'))} | {fmt(row.get('profit_factor'))} | {fmt(row.get('drawdown'))} | "
            f"{fmt(row.get('trade_count'))} | {fmt(row.get('initial_sl_loss_count'))} | "
            f"{fmt(row.get('breakeven_sl_count'))} | {fmt(row.get('trailing_sl_profit_count'))} | "
            f"{fmt(row.get('tp_hit_count'))} | {fmt(row.get('total_realized_r'))} |"
        )

    lines += [
        "",
        "## Variant Classifications",
        "",
        "| Variant | Classification | Failed Gates | Validation Net | OOS Net | Validation/OOS Initial SL | Validation/OOS Trailing Profit | Validation/OOS TP |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(scores, key=lambda r: str(r.get("exit_variant"))):
        lines.append(
            f"| {fmt(row.get('exit_variant'))} | {fmt(row.get('classification'))} | {fmt(row.get('failed_gates'))} | "
            f"{fmt(row.get('validation_net_profit'))} | {fmt(row.get('out_of_sample_net_profit'))} | "
            f"{fmt(row.get('validation_oos_initial_sl_losses'))} | {fmt(row.get('validation_oos_trailing_profit_exits'))} | "
            f"{fmt(row.get('validation_oos_tp_hits'))} |"
        )

    lines += [
        "",
        "## Interpretation Guardrails",
        "",
        "- `EXIT_VARIANT_PROMISING` is still not final approval.",
        "- OOS is used only as a diagnostic check, not for overfitting.",
        "- No parameter values should be optimized from this checkpoint alone.",
        "- Demo forward testing remains blocked until later review.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommendation(path: Path, run_id: str, scores: list[dict[str, Any]]) -> None:
    promising = [row for row in scores if row.get("classification") == "EXIT_VARIANT_PROMISING"]
    risky = [row for row in scores if row.get("classification") == "EXIT_VARIANT_RISKY"]
    rejected = [row for row in scores if row.get("classification") in {"REJECT_FOR_NOW", "INSUFFICIENT_TRADES"}]
    lines = [
        "# Checkpoint H Exit Variant Recommendation",
        "",
        f"Selected RunId: `{run_id}`",
        "",
        "No final candidate is approved in this checkpoint.",
        "",
        "## Summary",
        "",
        "| Variant | Classification | Notes |",
        "|---|---|---|",
    ]
    for row in sorted(scores, key=lambda r: str(r.get("exit_variant"))):
        lines.append(f"| {fmt(row.get('exit_variant'))} | {fmt(row.get('classification'))} | {fmt(row.get('failed_gates') or row.get('notes'))} |")

    lines += [
        "",
        "## Recommendation",
        "",
    ]
    if promising:
        names = ", ".join(str(row.get("exit_variant")) for row in promising)
        lines.append(f"`RESEARCH_MORE`: {names} can be researched further, but only as exit diagnostics. This is not final approval.")
    elif risky:
        names = ", ".join(str(row.get("exit_variant")) for row in risky)
        lines.append(f"`NEEDS_EXIT_RESEARCH`: risky variants detected ({names}). Do not promote a variant without additional diagnostics.")
    elif rejected:
        lines.append("`KEEP_BASELINE_NO_CHANGE`: tested variants did not justify replacing the baseline in this checkpoint.")
    else:
        lines.append("`KEEP_BASELINE_NO_CHANGE`: keep the baseline as the reference until more diagnostics are available.")

    lines += [
        "",
        "## Guardrails",
        "",
        "- This was a pre-registered four-variant comparison, not an optimization sweep.",
        "- No strategy entry logic was changed.",
        "- No new strategy was added.",
        "- OOS results are diagnostic evidence only and must not be used to curve-fit.",
        "- No demo forward test should start from this checkpoint alone.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    run_root = Path(args.runs_root) / args.run_id
    if not run_root.exists():
        raise SystemExit(f"RunId not found: {args.run_id}")
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    rows = [collect_phase_row(case_dir) for case_dir in sorted(run_root.iterdir()) if (case_dir / "case.json").exists()]
    scores = classify_variants(rows)
    write_csv(results_root / "exit_variant_results.csv", rows)
    write_csv(results_root / "exit_variant_scores.csv", scores)
    write_markdown(results_root / "exit_variant_telemetry_summary.md", args.run_id, rows, scores)
    write_recommendation(results_root / "checkpoint_h_exit_variant_recommendation.md", args.run_id, scores)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
