#!/usr/bin/env python3
"""Baseline attribution analysis for Checkpoint I.

This tool analyzes the EURUSD H1 baseline reference from an existing MT5
research run. It does not run MT5 and does not optimize parameters.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


BASELINE_CASE_ID = "EURUSD_H1_EXIT_BASELINE_10000"
PHASE_ORDER = {"train": 0, "validation": 1, "out_of_sample": 2}


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


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y.%m.%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value).replace("|", "/")


def avg(values: list[float]) -> float | None:
    return round(mean(values), 6) if values else None


def profit_factor(profits: list[float]) -> float | None:
    gains = sum(value for value in profits if value > 0)
    losses = abs(sum(value for value in profits if value < 0))
    if losses == 0:
        return None if gains == 0 else 999.0
    return round(gains / losses, 4)


def max_consecutive_losses(profits: list[float]) -> int:
    current = 0
    best = 0
    for value in profits:
        if value < 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def session_bucket(dt: datetime | None) -> str:
    if dt is None:
        return "Other/Unknown"
    hour = dt.hour
    if 0 <= hour <= 6:
        return "Asia"
    if 7 <= hour <= 12:
        return "London"
    if 13 <= hour <= 16:
        return "London/New York overlap"
    if 17 <= hour <= 21:
        return "New York"
    return "Other/Unknown"


def spread_bucket(spread: float | None) -> str:
    if spread is None:
        return "Unknown"
    if spread <= 10:
        return "<=10"
    if spread <= 15:
        return "11-15"
    if spread <= 20:
        return "16-20"
    if spread <= 25:
        return "21-25"
    return ">25"


def month_bucket(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m") if dt else "Unknown"


def merge_trade_and_telemetry(case_dir: Path) -> list[dict[str, Any]]:
    ledger_rows = read_csv(case_dir / "trade_ledger.csv")
    telemetry_rows = read_csv(case_dir / "exit_telemetry.csv")
    close_by_deal = {row.get("deal_id"): row for row in telemetry_rows if row.get("event") == "CLOSE" and row.get("deal_id")}
    close_rows = [row for row in telemetry_rows if row.get("event") == "CLOSE"]
    case = load_json(case_dir / "case.json")

    trades: list[dict[str, Any]] = []
    for index, ledger in enumerate(ledger_rows):
        telemetry = close_by_deal.get(ledger.get("close_deal")) or (close_rows[index] if index < len(close_rows) else {})
        open_time = parse_time(ledger.get("open_time"))
        close_time = parse_time(ledger.get("close_time"))
        profit = to_float(ledger.get("total_profit")) or to_float(ledger.get("profit")) or 0.0
        realized_r = to_float(telemetry.get("realized_r"))
        spread = to_float(telemetry.get("spread_at_entry"))
        exit_class = telemetry.get("exit_classification") or "UNKNOWN"
        direction = (ledger.get("direction") or telemetry.get("direction") or "unknown").lower()
        strategy = telemetry.get("strategy") or ledger.get("entry_comment") or "Unknown"
        regime = telemetry.get("regime") or "Unknown"

        trades.append({
            "run_id": case.get("run_id") or case_dir.parent.name,
            "case_id": case.get("case_id") or case_dir.name,
            "base_case_id": case.get("base_case_id") or BASELINE_CASE_ID,
            "phase": case.get("phase"),
            "symbol": case.get("actual_symbol") or ledger.get("symbol"),
            "timeframe": case.get("timeframe") or ledger.get("timeframe"),
            "open_time": ledger.get("open_time"),
            "close_time": ledger.get("close_time"),
            "open_month": month_bucket(open_time),
            "session": session_bucket(open_time),
            "direction": direction,
            "strategy": strategy,
            "regime": regime,
            "spread_at_entry": spread,
            "spread_bucket": spread_bucket(spread),
            "exit_type": exit_class,
            "profit": round(profit, 2),
            "realized_r": realized_r,
            "volume": to_float(ledger.get("volume")),
            "duration_minutes": to_float(ledger.get("duration_minutes")),
            "largest_loss_marker": profit,
            "largest_win_marker": profit,
            "close_deal": ledger.get("close_deal"),
            "telemetry_deal_id": telemetry.get("deal_id"),
        })
    return trades


def summarize_group(trades: list[dict[str, Any]], group_fields: tuple[str, ...]) -> list[dict[str, Any]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        key = tuple(trade.get(field) for field in group_fields)
        grouped[key].append(trade)

    rows: list[dict[str, Any]] = []
    for key, items in grouped.items():
        profits = [float(item.get("profit") or 0.0) for item in items]
        r_values = [value for value in (to_float(item.get("realized_r")) for item in items) if value is not None]
        wins = [value for value in profits if value > 0]
        row: dict[str, Any] = {field: key[index] for index, field in enumerate(group_fields)}
        row.update({
            "trades": len(items),
            "net_profit": round(sum(profits), 2),
            "win_rate": round((len(wins) / len(items)) * 100.0, 2) if items else None,
            "profit_factor": profit_factor(profits),
            "average_r": avg(r_values),
            "initial_sl_losses": len([item for item in items if item.get("exit_type") == "INITIAL_SL_LOSS"]),
            "breakeven_exits": len([item for item in items if item.get("exit_type") == "BREAKEVEN_SL"]),
            "trailing_profit_exits": len([item for item in items if item.get("exit_type") == "TRAILING_SL_PROFIT"]),
            "tp_hits": len([item for item in items if item.get("exit_type") == "TP_HIT"]),
            "max_consecutive_losses": max_consecutive_losses(profits),
            "largest_loss": round(min(profits), 2) if profits else None,
            "largest_win": round(max(profits), 2) if profits else None,
        })
        rows.append(row)
    return sorted(rows, key=lambda row: tuple(str(row.get(field)) for field in group_fields))


def drawdown_rows(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for phase in sorted({str(trade.get("phase")) for trade in trades}, key=lambda p: PHASE_ORDER.get(p, 99)):
        phase_trades = [trade for trade in trades if trade.get("phase") == phase]
        phase_trades.sort(key=lambda trade: trade.get("close_time") or "")
        equity = 0.0
        peak = 0.0
        max_dd = 0.0
        worst_month = ""
        monthly_profit: dict[str, float] = defaultdict(float)
        for trade in phase_trades:
            profit = float(trade.get("profit") or 0.0)
            equity += profit
            peak = max(peak, equity)
            dd = peak - equity
            if dd > max_dd:
                max_dd = dd
                worst_month = str(trade.get("open_month"))
            monthly_profit[str(trade.get("open_month"))] += profit
        for month, value in sorted(monthly_profit.items()):
            rows.append({
                "phase": phase,
                "month": month,
                "monthly_net_profit": round(value, 2),
                "phase_max_trade_sequence_drawdown": round(max_dd, 2),
                "phase_worst_drawdown_month": worst_month,
            })
    return rows


def consistency_warning(rows: list[dict[str, Any]], group_name: str, group_field: str) -> list[str]:
    warnings: list[str] = []
    by_key: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        by_key[str(row.get(group_field))][str(row.get("phase"))] = row
    for key, phases in by_key.items():
        validation = phases.get("validation")
        oos = phases.get("out_of_sample")
        if not validation or not oos:
            continue
        validation_trades = to_int(validation.get("trades"))
        oos_trades = to_int(oos.get("trades"))
        validation_net = to_float(validation.get("net_profit")) or 0.0
        oos_net = to_float(oos.get("net_profit")) or 0.0
        if validation_trades < 30 or oos_trades < 30:
            warnings.append(f"{group_name} `{key}` has small validation/OOS sample ({validation_trades}/{oos_trades}); avoid filter decisions.")
        elif validation_net < 0 and oos_net < 0:
            warnings.append(f"{group_name} `{key}` is negative in both validation and OOS; research filter attribution further before any change.")
    return warnings


def classify_recommendation(
    session_rows: list[dict[str, Any]],
    direction_rows: list[dict[str, Any]],
    regime_rows: list[dict[str, Any]],
    spread_rows: list[dict[str, Any]],
    warnings: list[str],
) -> str:
    def consistent_negative(rows: list[dict[str, Any]], field: str) -> bool:
        by_key: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
        for row in rows:
            by_key[str(row.get(field))][str(row.get("phase"))] = row
        for phases in by_key.values():
            validation = phases.get("validation")
            oos = phases.get("out_of_sample")
            if not validation or not oos:
                continue
            if to_int(validation.get("trades")) >= 30 and to_int(oos.get("trades")) >= 30:
                if (to_float(validation.get("net_profit")) or 0.0) < 0 and (to_float(oos.get("net_profit")) or 0.0) < 0:
                    return True
        return False

    if consistent_negative(direction_rows, "direction"):
        return "NEEDS_DIRECTION_FILTER_RESEARCH"
    if consistent_negative(session_rows, "session"):
        return "NEEDS_SESSION_FILTER_RESEARCH"
    if consistent_negative(regime_rows, "regime"):
        return "NEEDS_REGIME_FILTER_RESEARCH"
    if consistent_negative(spread_rows, "spread_bucket"):
        return "NEEDS_SPREAD_FILTER_RESEARCH"
    if any("data missing" in warning.lower() or "no trade rows" in warning.lower() for warning in warnings):
        return "NEEDS_MORE_LOGGING"
    return "KEEP_BASELINE_RESEARCH_MORE"


def markdown_table(rows: list[dict[str, Any]], fields: list[str], max_rows: int = 30) -> list[str]:
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows[:max_rows]:
        lines.append("| " + " | ".join(fmt(row.get(field)) for field in fields) + " |")
    return lines


def write_summary(
    path: Path,
    run_id: str,
    by_phase: list[dict[str, Any]],
    by_session: list[dict[str, Any]],
    by_direction: list[dict[str, Any]],
    by_exit: list[dict[str, Any]],
    by_regime: list[dict[str, Any]],
    by_spread: list[dict[str, Any]],
    by_month: list[dict[str, Any]],
    recommendation: str,
) -> None:
    lines = [
        "# Baseline Attribution Summary",
        "",
        f"Selected RunId: `{run_id}`",
        "",
        "Scope: `EURUSD_H1_EXIT_BASELINE_10000` only. This is attribution analysis, not optimization.",
        "",
        f"Recommendation: `{recommendation}`",
        "",
        "## By Phase",
        "",
    ]
    lines += markdown_table(by_phase, ["phase", "trades", "net_profit", "win_rate", "profit_factor", "average_r", "initial_sl_losses", "trailing_profit_exits", "tp_hits", "max_consecutive_losses"])
    lines += ["", "## By Session", ""]
    lines += markdown_table(by_session, ["phase", "session", "trades", "net_profit", "win_rate", "profit_factor", "average_r", "initial_sl_losses", "trailing_profit_exits", "tp_hits"])
    lines += ["", "## By Direction", ""]
    lines += markdown_table(by_direction, ["phase", "direction", "trades", "net_profit", "win_rate", "profit_factor", "average_r", "initial_sl_losses", "trailing_profit_exits", "tp_hits"])
    lines += ["", "## By Exit Type", ""]
    lines += markdown_table(by_exit, ["phase", "exit_type", "trades", "net_profit", "win_rate", "profit_factor", "average_r"])
    lines += ["", "## By Regime", ""]
    lines += markdown_table(by_regime, ["phase", "regime", "trades", "net_profit", "win_rate", "profit_factor", "average_r"])
    lines += ["", "## By Spread Bucket", ""]
    lines += markdown_table(by_spread, ["phase", "spread_bucket", "trades", "net_profit", "win_rate", "profit_factor", "average_r"])
    lines += ["", "## Monthly / Drawdown Concentration", ""]
    lines += markdown_table(by_month, ["phase", "month", "monthly_net_profit", "phase_max_trade_sequence_drawdown", "phase_worst_drawdown_month"], max_rows=80)
    lines += [
        "",
        "## Guardrail",
        "",
        "Do not recommend filters from OOS alone. A filter hypothesis requires consistent validation and OOS evidence with enough trades.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_warnings(path: Path, warnings: list[str]) -> None:
    lines = [
        "# Baseline Attribution Warnings",
        "",
        "These warnings are diagnostic guardrails. They are not trading instructions.",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No critical attribution warnings. Continue research without changing live/demo settings.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommendation(path: Path, recommendation: str, warnings: list[str]) -> None:
    lines = [
        "# Checkpoint I Recommendation",
        "",
        f"Classification: `{recommendation}`",
        "",
        "No live/demo setting change is approved. No final candidate is approved.",
        "",
        "## Rationale",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings[:12])
    else:
        lines.append("- No consistent validation/OOS weakness with sufficient sample size was strong enough to justify a filter recommendation.")
    lines += [
        "",
        "## Guardrails",
        "",
        "- No optimization was performed.",
        "- No strategy entry logic was changed.",
        "- No exit behavior was changed.",
        "- No new strategy branch was added.",
        "- Demo forward testing remains blocked.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", default="research/runs/run_20260621_205032")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--case-id", default=BASELINE_CASE_ID)
    args = parser.parse_args()

    run_root = Path(args.run_root)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    case_dirs = [
        path for path in sorted(run_root.iterdir())
        if path.is_dir() and path.name.startswith(args.case_id + "_") and (path / "trade_ledger.csv").exists()
    ]
    if not case_dirs:
        raise SystemExit(f"No baseline case folders found under {run_root}")

    trades: list[dict[str, Any]] = []
    warnings: list[str] = []
    for case_dir in case_dirs:
        case_trades = merge_trade_and_telemetry(case_dir)
        if not case_trades:
            warnings.append(f"No trade rows parsed for {case_dir.name}")
        if any(trade.get("regime") == "Unknown" for trade in case_trades):
            warnings.append(f"Regime data missing for at least one trade in {case_dir.name}")
        if any(trade.get("spread_at_entry") is None for trade in case_trades):
            warnings.append(f"Spread-at-entry data missing for at least one trade in {case_dir.name}")
        trades.extend(case_trades)

    by_phase = summarize_group(trades, ("phase",))
    by_session = summarize_group(trades, ("phase", "session"))
    by_direction = summarize_group(trades, ("phase", "direction"))
    by_exit = summarize_group(trades, ("phase", "exit_type"))
    by_regime = summarize_group(trades, ("phase", "regime"))
    by_strategy = summarize_group(trades, ("phase", "strategy"))
    by_spread = summarize_group(trades, ("phase", "spread_bucket"))
    by_month = drawdown_rows(trades)

    warnings.extend(consistency_warning(by_session, "Session", "session"))
    warnings.extend(consistency_warning(by_direction, "Direction", "direction"))
    warnings.extend(consistency_warning(by_regime, "Regime", "regime"))
    warnings.extend(consistency_warning(by_spread, "Spread bucket", "spread_bucket"))

    recommendation = classify_recommendation(by_session, by_direction, by_regime, by_spread, warnings)

    write_csv(results_root / "baseline_attribution_by_phase.csv", by_phase)
    write_csv(results_root / "baseline_attribution_by_session.csv", by_session)
    write_csv(results_root / "baseline_attribution_by_direction.csv", by_direction)
    write_csv(results_root / "baseline_attribution_by_exit_type.csv", by_exit)
    write_csv(results_root / "baseline_attribution_by_regime.csv", by_regime)
    write_csv(results_root / "baseline_attribution_by_strategy.csv", by_strategy)
    write_csv(results_root / "baseline_attribution_by_spread.csv", by_spread)
    write_csv(results_root / "baseline_attribution_by_month.csv", by_month)
    write_summary(results_root / "baseline_attribution_summary.md", run_root.name, by_phase, by_session, by_direction, by_exit, by_regime, by_spread, by_month, recommendation)
    write_warnings(results_root / "baseline_attribution_warnings.md", warnings)
    write_recommendation(results_root / "checkpoint_i_recommendation.md", recommendation, warnings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
