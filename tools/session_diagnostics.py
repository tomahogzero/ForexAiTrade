#!/usr/bin/env python3
"""Generate session and exit diagnostics from trade ledgers."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return []


def run_is_successful(run_root: Path) -> bool:
    status = load_json(run_root / "run_status.json")
    if not isinstance(status, list):
        return False
    return bool(status) and all(row.get("execution_status") == "PASS" for row in status)


def latest_successful_run_id(runs_root: Path) -> str | None:
    successful = [path.name for path in runs_root.glob("run_*") if path.is_dir() and run_is_successful(path)]
    if successful:
        return sorted(successful)[-1]
    all_runs = [path.name for path in runs_root.glob("run_*") if path.is_dir()]
    return sorted(all_runs)[-1] if all_runs else None


def resolve_run_id(runs_root: Path, run_id: str | None) -> str:
    selected = run_id or latest_successful_run_id(runs_root)
    if not selected:
        raise SystemExit(f"No run directories found under {runs_root}")
    if not (runs_root / selected).exists():
        raise SystemExit(f"RunId not found: {selected}")
    return selected


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def session_bucket(dt: datetime | None) -> str:
    if dt is None:
        return "Other / Unknown"
    hour = dt.hour
    # Broker/server time from MT5 report. No Thai local-time conversion is applied.
    if 0 <= hour < 7:
        return "Asia"
    if 7 <= hour < 13:
        return "London"
    if 13 <= hour < 17:
        return "Overlap"
    if 17 <= hour < 22:
        return "New York"
    return "Other / Unknown"


def safe_mean(values: list[float]) -> float | None:
    return round(mean(values), 4) if values else None


def profit_factor(profits: list[float]) -> float | None:
    gross_profit = sum(p for p in profits if p > 0)
    gross_loss = abs(sum(p for p in profits if p < 0))
    if gross_loss <= 0:
        return None
    return round(gross_profit / gross_loss, 4)


def max_consecutive_losses(trades: list[dict[str, Any]]) -> int:
    best = 0
    current = 0
    for trade in sorted(trades, key=lambda x: x.get("close_time") or ""):
        if float(trade.get("total_profit") or 0) < 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def summarize_group(trades: list[dict[str, Any]]) -> dict[str, Any]:
    profits = [float(t.get("total_profit") or 0) for t in trades]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]
    durations = [float(t.get("duration_minutes")) for t in trades if t.get("duration_minutes") is not None]
    total_loss = abs(sum(losses))
    largest_loss = min(losses) if losses else None
    loss_concentration_pct = None
    if total_loss > 0 and largest_loss is not None:
        loss_concentration_pct = round(abs(largest_loss) / total_loss * 100.0, 2)
    return {
        "trades": len(trades),
        "net_profit": round(sum(profits), 2),
        "win_rate_pct": round(len(wins) / len(trades) * 100.0, 2) if trades else None,
        "profit_factor": profit_factor(profits),
        "average_profit_loss": safe_mean(profits),
        "largest_loss": largest_loss,
        "largest_win": max(wins) if wins else None,
        "average_win": safe_mean(wins),
        "average_loss": safe_mean(losses),
        "win_loss_ratio": round(abs(safe_mean(wins) / safe_mean(losses)), 4) if wins and losses and safe_mean(losses) else None,
        "average_holding_minutes": safe_mean(durations),
        "quick_trades_under_60m": sum(1 for d in durations if d < 60),
        "long_trades_over_24h": sum(1 for d in durations if d > 1440),
        "max_consecutive_losses": max_consecutive_losses(trades),
        "loss_concentration_pct_largest_loss": loss_concentration_pct,
        "exit_counts": dict(Counter(str(t.get("exit_reason") or "UNKNOWN") for t in trades)),
    }


def selected_ledgers(runs_root: Path, run_id: str) -> list[Path]:
    run_root = runs_root / run_id
    if not run_root.exists():
        return []
    return sorted(run_root.glob("*/trade_ledger.json"))


def write_session_outputs(results_root: Path, all_trades: list[dict[str, Any]], selected_run_id: str) -> None:
    rows: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for trade in all_trades:
        bucket = session_bucket(parse_time(trade.get("open_time")))
        trade["session"] = bucket
        grouped[(str(trade.get("base_case_id")), bucket)].append(trade)

    for (case_id, session), trades in sorted(grouped.items()):
        rows.append({"case": case_id, "session": session, **summarize_group(trades)})

    csv_path = results_root / "session_diagnostics_by_case.csv"
    fields = sorted({key for row in rows for key in row})
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Session Diagnostics Summary",
        "",
        f"Selected RunId: `{selected_run_id}`",
        "",
        "Session buckets use MT5 broker/server time from the report. No Thai local-time conversion is applied.",
        "",
        "| Case | Session | Trades | Net Profit | Win Rate % | PF | Avg P/L | Largest Loss | Largest Win | Max Consecutive Losses |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['case']} | {row['session']} | {row['trades']} | {row['net_profit']} | {row['win_rate_pct']} | "
            f"{row['profit_factor']} | {row['average_profit_loss']} | {row['largest_loss']} | {row['largest_win']} | {row['max_consecutive_losses']} |"
        )
    lines += [
        "",
        "## Interpretation Guardrail",
        "",
        "Small session samples should not be optimized directly. Use this only to identify where future logging or controlled session-filter research may be needed.",
    ]
    (results_root / "session_diagnostics_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_exit_outputs(results_root: Path, all_trades: list[dict[str, Any]], selected_run_id: str) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for trade in all_trades:
        grouped[str(trade.get("base_case_id"))].append(trade)

    lines = [
        "# Exit Diagnostics Summary",
        "",
        f"Selected RunId: `{selected_run_id}`",
        "",
        "Exit diagnostics are inferred from MT5 close deal comments. No exit logic was changed.",
        "",
        "| Case | Trades | SL | TP | Other/Unknown | Avg Win | Avg Loss | Win/Loss Ratio | Avg Hold Min | Quick <60m | Long >24h | Largest Loss % of Total Loss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for case_id, trades in sorted(grouped.items()):
        summary = summarize_group(trades)
        exits = summary["exit_counts"]
        other_unknown = sum(v for k, v in exits.items() if k not in {"SL", "TP"})
        lines.append(
            f"| {case_id} | {summary['trades']} | {exits.get('SL', 0)} | {exits.get('TP', 0)} | {other_unknown} | "
            f"{summary['average_win']} | {summary['average_loss']} | {summary['win_loss_ratio']} | "
            f"{summary['average_holding_minutes']} | {summary['quick_trades_under_60m']} | {summary['long_trades_over_24h']} | "
            f"{summary['loss_concentration_pct_largest_loss']} |"
        )
    h1_trades = [trade for trade in all_trades if trade.get("base_case_id") == "EURUSD_H1_10000"]
    if h1_trades:
        lines += [
            "",
            "## EURUSD H1 Phase-Level Exit Diagnostics",
            "",
            "| Phase | Trades | SL | TP | Avg Win | Avg Loss | Win/Loss Ratio | Avg Hold Min | Max Consecutive Losses | Net Profit |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        phase_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for trade in h1_trades:
            phase_groups[str(trade.get("phase"))].append(trade)
        for phase in ("train", "validation", "out_of_sample"):
            trades = phase_groups.get(phase, [])
            summary = summarize_group(trades)
            exits = summary["exit_counts"]
            lines.append(
                f"| {phase} | {summary['trades']} | {exits.get('SL', 0)} | {exits.get('TP', 0)} | "
                f"{summary['average_win']} | {summary['average_loss']} | {summary['win_loss_ratio']} | "
                f"{summary['average_holding_minutes']} | {summary['max_consecutive_losses']} | {summary['net_profit']} |"
            )
    lines += [
        "",
        "## Trailing / Breakeven Visibility",
        "",
        "The current reports do not reliably show trailing-stop or breakeven modifications. Future EA logging should record every position modification with old/new SL, old/new TP, reason, and timestamp before exit research is implemented.",
    ]
    (results_root / "exit_diagnostics_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def recommendation_from_summaries(all_trades: list[dict[str, Any]]) -> str:
    if not all_trades:
        return "NEEDS_MORE_LOGGING"
    h1 = [t for t in all_trades if t.get("base_case_id") == "EURUSD_H1_10000"]
    if not h1:
        return "NEEDS_MORE_LOGGING"
    exits = Counter(str(t.get("exit_reason") or "UNKNOWN") for t in h1)
    unknown_ratio = exits.get("UNKNOWN", 0) / max(len(h1), 1)
    if unknown_ratio > 0.25:
        return "NEEDS_MORE_LOGGING"
    h1_summary = summarize_group(h1)
    sl_count = exits.get("SL", 0)
    tp_count = exits.get("TP", 0)
    avg_win = h1_summary.get("average_win")
    avg_loss = h1_summary.get("average_loss")
    if sl_count > (tp_count * 3) or h1_summary.get("max_consecutive_losses", 0) >= 8:
        return "NEEDS_EXIT_RESEARCH"
    if avg_win is not None and avg_loss is not None and abs(avg_loss) > avg_win:
        return "NEEDS_EXIT_RESEARCH"
    return "KEEP_BASELINE_NO_CHANGE"


def write_recommendation(results_root: Path, all_trades: list[dict[str, Any]], selected_run_id: str) -> None:
    action = recommendation_from_summaries(all_trades)
    h1 = [t for t in all_trades if t.get("base_case_id") == "EURUSD_H1_10000"]
    h1_summary = summarize_group(h1) if h1 else {}
    h1_exits = h1_summary.get("exit_counts", {}) if h1_summary else {}
    lines = [
        "# Checkpoint F Recommendation",
        "",
        f"Selected RunId: `{selected_run_id}`",
        "",
        f"Next action: `{action}`",
        "",
        "EURUSD H1 remains `RESEARCH_MORE`. This checkpoint does not approve live/demo forward testing and does not prove profitability.",
        "",
        "## Rationale",
        "",
        "- Previous Checkpoint F aggregate diagnostics included repeated runs and inflated total trade counts. F2 fixes this by scoping diagnostics to a selected RunId.",
        "- Trade-level rows are available from existing MT5 reports.",
        "- Session and exit diagnostics are now available for baseline review.",
        f"- H1 remains the baseline, but exit diagnostics show SL-heavy exits (`SL={h1_exits.get('SL', 0)}`, `TP={h1_exits.get('TP', 0)}`) and max consecutive losses of `{h1_summary.get('max_consecutive_losses')}`.",
        "- Exit research means additional diagnosis and logging design first, not changing exit logic in this checkpoint.",
        "- M30 and H4 remain rejected for now from Checkpoint E2.",
        "",
        "## Before Adding MicroTrend or Fibo Zone",
        "",
        "The following must be understood first:",
        "",
        "- session weakness",
        "- trade-level distribution",
        "- exit behavior",
        "- drawdown concentration",
        "- spread/slippage sensitivity",
        "",
        "## Guardrails",
        "",
        "- Do not optimize from a small number of trades.",
        "- Do not add a new strategy until reporting and diagnostics explain the current baseline.",
        "- Do not claim profitability from this checkpoint.",
    ]
    (results_root / "checkpoint_f_recommendation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--run-id")
    parser.add_argument("--latest-run", action="store_true")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)
    selected_run_id = resolve_run_id(runs_root, None if args.latest_run else args.run_id)
    all_trades: list[dict[str, Any]] = []
    for ledger in selected_ledgers(runs_root, selected_run_id):
        data = load_json(ledger)
        if isinstance(data, list):
            all_trades.extend(data)
    write_session_outputs(results_root, all_trades, selected_run_id)
    write_exit_outputs(results_root, all_trades, selected_run_id)
    write_recommendation(results_root, all_trades, selected_run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
