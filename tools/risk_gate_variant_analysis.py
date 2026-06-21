#!/usr/bin/env python3
"""Aggregate Checkpoint J losing-streak risk-gate diagnostic variants.

This reads completed MT5 research artifacts only. It does not run MT5, optimize
parameters, or approve any live/demo candidate.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


PHASES = ("train", "validation", "out_of_sample")
EXIT_CLASSES = ("INITIAL_SL_LOSS", "BREAKEVEN_SL", "TRAILING_SL_PROFIT", "TP_HIT", "UNKNOWN")
LOG_TIME_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) (?P<message>.*)$")


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


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


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


def fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value).replace("|", "/")


def infer_variant(case: dict[str, Any], case_dir: Path) -> str:
    value = case.get("risk_gate_variant")
    if value:
        return str(value)
    lowered = case_dir.name.lower()
    if "no_losing" in lowered:
        return "no_losing_streak_gate"
    if "fixed_cooldown" in lowered:
        return "fixed_cooldown_24bars"
    if "next_day" in lowered:
        return "next_day_reset"
    return "normal"


def parse_log_stats(case_dir: Path) -> dict[str, Any]:
    log_path = case_dir / "ea_mirror.log"
    stats: dict[str, Any] = {
        "accepted_signals": 0,
        "blocked_signals": 0,
        "losing_streak_blocks": 0,
        "losing_streak_trigger_blocks": 0,
        "cooldown_active_blocks": 0,
        "cooldown_or_reset_allowed_events": 0,
        "daily_weekly_drawdown_blocks": 0,
        "max_open_order_blocks": 0,
        "spread_blocks": 0,
        "first_losing_streak_block_time": "",
        "accepted_signals_after_first_losing_block": 0,
    }
    if not log_path.exists():
        return stats

    first_losing_dt: datetime | None = None
    accepted_times: list[datetime] = []
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = LOG_TIME_RE.match(line)
        timestamp = parse_dt(match.group("time")) if match else None
        message = match.group("message") if match else line
        lowered = message.lower()

        if message.startswith("Signal accepted:"):
            stats["accepted_signals"] += 1
            if timestamp:
                accepted_times.append(timestamp)
        if message.startswith("Signal blocked:"):
            stats["blocked_signals"] += 1
        if "losing streak" in lowered:
            stats["losing_streak_blocks"] += 1
            if first_losing_dt is None and timestamp:
                first_losing_dt = timestamp
                stats["first_losing_streak_block_time"] = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            if "trigger" in lowered:
                stats["losing_streak_trigger_blocks"] += 1
            if "active until" in lowered:
                stats["cooldown_active_blocks"] += 1
            if "allowed" in lowered or "ignored losing streak gate" in lowered:
                stats["cooldown_or_reset_allowed_events"] += 1
        if "daily loss" in lowered or "weekly loss" in lowered or "drawdown" in lowered:
            stats["daily_weekly_drawdown_blocks"] += 1
        if "max open orders" in lowered:
            stats["max_open_order_blocks"] += 1
        if "spread above maximum" in lowered or "spread too wide" in lowered:
            stats["spread_blocks"] += 1

    if first_losing_dt:
        stats["accepted_signals_after_first_losing_block"] = len([t for t in accepted_times if t > first_losing_dt])
    return stats


def collect_phase(case_dir: Path) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    status = load_json(case_dir / "status.json")
    parsed = load_json(case_dir / "parsed_result.json")
    telemetry = load_json(case_dir / "exit_telemetry_summary.json")
    by_exit = telemetry.get("by_exit_classification", {}) if isinstance(telemetry, dict) else {}
    log_stats = parse_log_stats(case_dir)

    row: dict[str, Any] = {
        "run_id": case.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or case_dir.name,
        "base_case_id": case.get("base_case_id") or "",
        "phase": case.get("phase") or "",
        "risk_gate_variant": infer_variant(case, case_dir),
        "risk_gate_mode": case.get("risk_gate_mode") or "NORMAL",
        "losing_streak_cooldown_bars": case.get("losing_streak_cooldown_bars"),
        "symbol": case.get("actual_symbol"),
        "timeframe": case.get("timeframe"),
        "deposit": case.get("deposit"),
        "execution_status": status.get("execution_status", "UNKNOWN") if isinstance(status, dict) else "UNKNOWN",
        "net_profit": parsed.get("net_profit") if isinstance(parsed, dict) else None,
        "profit_factor": parsed.get("profit_factor") if isinstance(parsed, dict) else None,
        "relative_drawdown": parsed.get("relative_drawdown") or parsed.get("drawdown_relative") if isinstance(parsed, dict) else None,
        "max_drawdown": parsed.get("max_drawdown") if isinstance(parsed, dict) else None,
        "trade_count": parsed.get("total_trades") if isinstance(parsed, dict) else None,
        "win_rate": parsed.get("win_rate") if isinstance(parsed, dict) else None,
        "max_consecutive_losses": parsed.get("consecutive_losses") if isinstance(parsed, dict) else None,
        "largest_win": parsed.get("largest_win") if isinstance(parsed, dict) else None,
        "largest_loss": parsed.get("largest_loss") if isinstance(parsed, dict) else None,
    }
    for exit_class in EXIT_CLASSES:
        item = by_exit.get(exit_class, {}) if isinstance(by_exit, dict) else {}
        row[f"{exit_class.lower()}_count"] = item.get("count", 0) if isinstance(item, dict) else 0
        row[f"{exit_class.lower()}_avg_r"] = item.get("average_r") if isinstance(item, dict) else None
    row.update(log_stats)
    return row


def collect_rows(run_root: Path) -> list[dict[str, Any]]:
    rows = []
    for case_json in sorted(run_root.glob("*/case.json")):
        case_dir = case_json.parent
        case = load_json(case_json)
        if case.get("risk_gate_variant") or "RISKGATE" in case_dir.name:
            rows.append(collect_phase(case_dir))
    return rows


def by_variant(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        grouped[str(row.get("risk_gate_variant"))][str(row.get("phase"))] = row
    return grouped


def sum_field(phases: dict[str, dict[str, Any]], field: str, names: tuple[str, ...]) -> float:
    return sum(to_float(phases.get(name, {}).get(field)) or 0.0 for name in names)


def max_field(phases: dict[str, dict[str, Any]], field: str, names: tuple[str, ...]) -> float:
    values = [to_float(phases.get(name, {}).get(field)) for name in names]
    values = [value for value in values if value is not None]
    return max(values) if values else 0.0


def classify(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = by_variant(rows)
    baseline = grouped.get("normal", {})
    baseline_val_oos_dd = max_field(baseline, "relative_drawdown", ("validation", "out_of_sample"))
    baseline_val_oos_net = sum_field(baseline, "net_profit", ("validation", "out_of_sample"))
    scores: list[dict[str, Any]] = []

    for variant, phases in sorted(grouped.items()):
        failed: list[str] = []
        train = phases.get("train")
        validation = phases.get("validation")
        oos = phases.get("out_of_sample")

        if variant == "normal":
            classification = "BASELINE_NORMAL"
            failed.append("normal_gate_reference")
        elif any(phases.get(name, {}).get("execution_status") != "PASS" for name in PHASES):
            classification = "EXECUTION_FAILED"
            failed.append("execution_failure")
        elif not validation or not oos:
            classification = "INCOMPLETE_PHASES"
            failed.append("missing_validation_or_oos")
        else:
            val_net = to_float(validation.get("net_profit")) or 0.0
            oos_net = to_float(oos.get("net_profit")) or 0.0
            val_oos_net = val_net + oos_net
            val_oos_dd = max_field(phases, "relative_drawdown", ("validation", "out_of_sample"))
            val_oos_losses = max_field(phases, "max_consecutive_losses", ("validation", "out_of_sample"))
            baseline_losses = max_field(baseline, "max_consecutive_losses", ("validation", "out_of_sample"))

            if val_net <= 0:
                failed.append("validation_not_positive")
            if oos_net <= 0:
                failed.append("out_of_sample_not_positive")
            if baseline_val_oos_dd and val_oos_dd > baseline_val_oos_dd * 1.25:
                failed.append("drawdown_materially_worse_than_normal")
            if baseline_losses and val_oos_losses > baseline_losses:
                failed.append("max_consecutive_losses_worse_than_normal")
            if baseline_val_oos_net and val_oos_net < baseline_val_oos_net:
                failed.append("validation_oos_net_worse_than_normal")

            if variant == "no_losing_streak_gate":
                classification = "RISKY_FOR_LIVE"
                failed.append("protective_gate_removed")
            elif failed:
                classification = "REJECT_FOR_NOW"
            else:
                classification = "RESEARCH_MORE"

        scores.append({
            "risk_gate_variant": variant,
            "classification": classification,
            "failed_gates": ",".join(dict.fromkeys(failed)),
            "train_net_profit": train.get("net_profit") if train else None,
            "validation_net_profit": validation.get("net_profit") if validation else None,
            "out_of_sample_net_profit": oos.get("net_profit") if oos else None,
            "train_trades": train.get("trade_count") if train else None,
            "validation_trades": validation.get("trade_count") if validation else None,
            "out_of_sample_trades": oos.get("trade_count") if oos else None,
            "validation_oos_net_profit": round(sum_field(phases, "net_profit", ("validation", "out_of_sample")), 2),
            "validation_oos_max_relative_drawdown": round(max_field(phases, "relative_drawdown", ("validation", "out_of_sample")), 4),
            "validation_oos_max_consecutive_losses": max_field(phases, "max_consecutive_losses", ("validation", "out_of_sample")),
            "total_losing_streak_blocks": int(sum_field(phases, "losing_streak_blocks", PHASES)),
            "accepted_after_first_losing_block_total": int(sum_field(phases, "accepted_signals_after_first_losing_block", PHASES)),
            "notes": "Diagnostic risk-gate modes are Strategy Tester only and are not live/demo approved.",
        })
    return scores


def write_summary(path: Path, run_id: str, rows: list[dict[str, Any]], scores: list[dict[str, Any]]) -> None:
    lines = [
        "# Checkpoint J Risk-Gate Variant Summary",
        "",
        f"Selected RunId: `{run_id}`",
        "",
        "This is a controlled diagnostic run for losing-streak gate behavior. It is not optimization and does not approve a live/demo candidate.",
        "",
        "## Variant Phase Results",
        "",
        "| Variant | Mode | Phase | Status | Net | PF | Rel DD | Trades | Max Loss Streak | Losing-Streak Blocks | Accepted After First Block | Initial SL | Trailing Profit | TP Hit |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: (str(r.get("risk_gate_variant")), str(r.get("phase")))):
        lines.append(
            f"| {fmt(row.get('risk_gate_variant'))} | {fmt(row.get('risk_gate_mode'))} | {fmt(row.get('phase'))} | "
            f"{fmt(row.get('execution_status'))} | {fmt(row.get('net_profit'))} | {fmt(row.get('profit_factor'))} | "
            f"{fmt(row.get('relative_drawdown'))} | {fmt(row.get('trade_count'))} | {fmt(row.get('max_consecutive_losses'))} | "
            f"{fmt(row.get('losing_streak_blocks'))} | {fmt(row.get('accepted_signals_after_first_losing_block'))} | "
            f"{fmt(row.get('initial_sl_loss_count'))} | {fmt(row.get('trailing_sl_profit_count'))} | {fmt(row.get('tp_hit_count'))} |"
        )

    lines += [
        "",
        "## Variant Classifications",
        "",
        "| Variant | Classification | Failed Gates | Val+OOS Net | Val/OOS Max DD | Val/OOS Max Loss Streak | Accepted After First Block |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for score in sorted(scores, key=lambda r: str(r.get("risk_gate_variant"))):
        lines.append(
            f"| {fmt(score.get('risk_gate_variant'))} | {fmt(score.get('classification'))} | {fmt(score.get('failed_gates'))} | "
            f"{fmt(score.get('validation_oos_net_profit'))} | {fmt(score.get('validation_oos_max_relative_drawdown'))} | "
            f"{fmt(score.get('validation_oos_max_consecutive_losses'))} | {fmt(score.get('accepted_after_first_losing_block_total'))} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "- `NORMAL` remains the baseline reference. It intentionally blocks after the configured losing streak to protect capital.",
        "- Removing or relaxing the gate increased trade count, but validation and out-of-sample results were worse than the normal gate in this run.",
        "- The no-gate variant is marked `RISKY_FOR_LIVE` because it removes a protective capital-preservation gate.",
        "- Cooldown/reset variants are diagnostic only. They should not be used on demo/live without a separate safety review.",
        "",
        "## Safety Notes",
        "",
        "- Diagnostic risk-gate modes are blocked outside Strategy Tester by EA safety gates.",
        "- This checkpoint did not optimize parameters, did not add a new strategy, and did not claim profitability.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommendation(path: Path, run_id: str, scores: list[dict[str, Any]]) -> None:
    lines = [
        "# Checkpoint J Risk-Gate Recommendation",
        "",
        f"Selected RunId: `{run_id}`",
        "",
        "Recommendation: `KEEP_NORMAL_GATE_AS_BASELINE`.",
        "",
        "The diagnostic variants increased trading activity after losing-streak events, but they did not improve validation/out-of-sample robustness. The normal losing-streak gate should remain enabled for the baseline.",
        "",
        "| Variant | Classification | Reason |",
        "|---|---|---|",
    ]
    for score in sorted(scores, key=lambda r: str(r.get("risk_gate_variant"))):
        lines.append(
            f"| {fmt(score.get('risk_gate_variant'))} | {fmt(score.get('classification'))} | {fmt(score.get('failed_gates'))} |"
        )
    lines += [
        "",
        "## Before Any Future Cooldown Research",
        "",
        "- Keep diagnostic modes Strategy Tester only.",
        "- Keep low risk and do not increase lot size to rescue results.",
        "- Compare drawdown, maximum consecutive losses, and trade concentration before looking at net profit.",
        "- Do not start demo forward testing from this checkpoint.",
        "",
        "This is not a profitability claim and not a final candidate selection.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Checkpoint J risk-gate diagnostic variants.")
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    run_root = Path(args.runs_root) / args.run_id
    if not run_root.exists():
        raise SystemExit(f"Run folder not found: {run_root}")
    results_root = Path(args.results_root)
    rows = collect_rows(run_root)
    if not rows:
        raise SystemExit(f"No risk-gate case folders found under: {run_root}")
    scores = classify(rows)
    write_csv(results_root / "risk_gate_variant_results.csv", rows)
    write_csv(results_root / "risk_gate_variant_scores.csv", scores)
    write_summary(results_root / "risk_gate_variant_summary.md", args.run_id, rows, scores)
    write_recommendation(results_root / "checkpoint_j_risk_gate_recommendation.md", args.run_id, scores)
    print(f"Wrote risk-gate analysis for {args.run_id}: {len(rows)} phase rows, {len(scores)} variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
