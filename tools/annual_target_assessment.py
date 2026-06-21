#!/usr/bin/env python3
"""Assess current ForexAiTrade baseline against annual target tiers.

This is a reporting tool only. It does not run MT5, optimize parameters, change
lot sizing, or approve live/demo readiness.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


PHASES = ("train", "validation", "out_of_sample")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


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


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value)
    for fmt in ("%Y-%m-%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def period_days(parsed: dict[str, Any], case: dict[str, Any]) -> int | None:
    start = parse_date(parsed.get("report_period_from"))
    end = parse_date(parsed.get("report_period_to"))
    period = case.get("period") if isinstance(case.get("period"), dict) else {}
    if start is None:
        start = parse_date(period.get("from"))
    if end is None:
        end = parse_date(period.get("to"))
    if start is None or end is None or end < start:
        return None
    return (end - start).days + 1


def phase_metrics(case_dir: Path) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    parsed = load_json(case_dir / "parsed_result.json")
    status = load_json(case_dir / "status.json")
    deposit = to_float(parsed.get("deposit")) or to_float(case.get("deposit")) or 0.0
    net_profit = to_float(parsed.get("net_profit")) or 0.0
    days = period_days(parsed, case)
    trades = to_int(parsed.get("total_trades"))
    rel_dd = to_float(parsed.get("relative_drawdown"))
    if rel_dd is None:
        rel_dd = to_float(parsed.get("drawdown_relative"))

    annualized = None
    cagr = None
    calmar = None
    monthly = None
    if deposit > 0 and days and days > 0:
        period_return_pct = net_profit / deposit * 100.0
        annualized = period_return_pct * 365.0 / days
        monthly = annualized / 12.0
        if 1.0 + net_profit / deposit > 0:
            cagr = ((1.0 + net_profit / deposit) ** (365.0 / days) - 1.0) * 100.0
        if rel_dd and rel_dd > 0:
            calmar = annualized / rel_dd

    warning = []
    if days is not None and days < 180:
        warning.append("short_period")
    if trades < 50:
        warning.append("low_trade_count")

    return {
        "run_id": case.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or case_dir.name,
        "base_case_id": case.get("base_case_id"),
        "phase": case.get("phase"),
        "symbol": case.get("actual_symbol") or parsed.get("symbol"),
        "timeframe": case.get("timeframe") or parsed.get("timeframe"),
        "deposit": deposit,
        "execution_status": status.get("execution_status", "UNKNOWN"),
        "net_profit": round(net_profit, 2),
        "profit_factor": parsed.get("profit_factor"),
        "relative_drawdown": rel_dd,
        "total_trades": trades,
        "test_period_days": days,
        "annualized_return_percent": round(annualized, 4) if annualized is not None else None,
        "cagr_approx_percent": round(cagr, 4) if cagr is not None else None,
        "calmar_ratio": round(calmar, 4) if calmar is not None else None,
        "monthly_return_estimate": round(monthly, 4) if monthly is not None else None,
        "annualized_return_informational_only": bool(warning),
        "warning": ",".join(warning),
    }


def combined_validation_oos(rows: list[dict[str, Any]]) -> dict[str, Any]:
    phases = {row["phase"]: row for row in rows}
    validation = phases.get("validation", {})
    oos = phases.get("out_of_sample", {})
    deposit = to_float(validation.get("deposit")) or to_float(oos.get("deposit")) or 0.0
    net_profit = (to_float(validation.get("net_profit")) or 0.0) + (to_float(oos.get("net_profit")) or 0.0)
    days = to_int(validation.get("test_period_days")) + to_int(oos.get("test_period_days"))
    trades = to_int(validation.get("total_trades")) + to_int(oos.get("total_trades"))
    dd = max(to_float(validation.get("relative_drawdown")) or 0.0, to_float(oos.get("relative_drawdown")) or 0.0)
    min_pf_values = [to_float(validation.get("profit_factor")), to_float(oos.get("profit_factor"))]
    min_pf_values = [v for v in min_pf_values if v is not None]
    min_pf = min(min_pf_values) if min_pf_values else None

    annualized = None
    cagr = None
    calmar = None
    if deposit > 0 and days > 0:
        period_return_pct = net_profit / deposit * 100.0
        annualized = period_return_pct * 365.0 / days
        if 1.0 + net_profit / deposit > 0:
            cagr = ((1.0 + net_profit / deposit) ** (365.0 / days) - 1.0) * 100.0
        if dd > 0:
            calmar = annualized / dd

    classification = classify_viability(annualized, cagr, dd, calmar, min_pf, trades, rows)
    return {
        "run_id": validation.get("run_id") or oos.get("run_id"),
        "case_id": validation.get("base_case_id") or oos.get("base_case_id"),
        "phase": "validation_plus_out_of_sample",
        "symbol": validation.get("symbol") or oos.get("symbol"),
        "timeframe": validation.get("timeframe") or oos.get("timeframe"),
        "deposit": deposit,
        "net_profit": round(net_profit, 2),
        "profit_factor": round(min_pf, 4) if min_pf is not None else None,
        "relative_drawdown": round(dd, 4),
        "total_trades": trades,
        "test_period_days": days,
        "annualized_return_percent": round(annualized, 4) if annualized is not None else None,
        "cagr_approx_percent": round(cagr, 4) if cagr is not None else None,
        "calmar_ratio": round(calmar, 4) if calmar is not None else None,
        "monthly_return_estimate": round(annualized / 12.0, 4) if annualized is not None else None,
        "risk_adjusted_classification": classification,
        "annualized_return_informational_only": trades < 150,
        "warning": "insufficient_total_trades" if trades < 150 else "",
    }


def classify_viability(
    annualized: float | None,
    cagr: float | None,
    dd: float,
    calmar: float | None,
    min_pf: float | None,
    trades: int,
    rows: list[dict[str, Any]],
) -> str:
    phases = {row["phase"]: row for row in rows}
    validation = phases.get("validation", {})
    oos = phases.get("out_of_sample", {})
    if (to_float(validation.get("net_profit")) or 0.0) <= 0 or (to_float(oos.get("net_profit")) or 0.0) <= 0:
        return "NOT_VIABLE"
    if trades < 150:
        return "SURVIVAL_ONLY"
    if annualized is None or cagr is None:
        return "NOT_VIABLE"
    if annualized < 12.0:
        return "BELOW_FOREX_RISK_PREMIUM"
    if dd > 30.0 or (calmar is not None and calmar < 0.5):
        return "AGGRESSIVE_RESEARCH_ONLY"
    if cagr >= 100.0 and dd <= 30.0:
        return "CHALLENGE_ONLY_NOT_BASELINE"
    if cagr >= 35.0 and dd <= 25.0 and (calmar or 0.0) >= 1.2 and (min_pf or 0.0) >= 1.25:
        return "AGGRESSIVE_RESEARCH_ONLY"
    if cagr >= 20.0 and dd <= 15.0 and (calmar or 0.0) >= 1.0 and (min_pf or 0.0) >= 1.20:
        return "MEETS_BALANCED_TARGET"
    if cagr >= 12.0 and dd <= 15.0 and (calmar or 0.0) >= 0.8 and (min_pf or 0.0) >= 1.15:
        return "MEETS_CONSERVATIVE_FOREX_TARGET"
    return "BELOW_FOREX_RISK_PREMIUM"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value).replace("|", "/")


def write_markdown(path: Path, target_profile: dict[str, Any], rows: list[dict[str, Any]], combined: dict[str, Any]) -> None:
    lines = [
        "# Annual Target Assessment",
        "",
        "This assessment is a risk-adjusted research frame, not a profitability claim and not live/demo readiness.",
        "",
        f"Default target profile: `{target_profile.get('default_target_profile', 'Balanced Worth-The-Risk')}`",
        "",
        "## Target Tiers",
        "",
        "| Tier | Min CAGR | Max DD | Min Calmar | Min PF | Notes |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for tier in target_profile.get("target_tiers", []):
        notes = []
        if tier.get("purpose"):
            notes.append(str(tier["purpose"]))
        if tier.get("demo_or_research_only"):
            notes.append("demo/research only")
        if tier.get("research_only"):
            notes.append("research only")
        if tier.get("not_allowed_as_baseline"):
            notes.append("not baseline")
        lines.append(
            f"| {fmt(tier.get('name'))} | {fmt(tier.get('min_cagr'))} | {fmt(tier.get('max_drawdown'))} | "
            f"{fmt(tier.get('min_calmar'))} | {fmt(tier.get('min_profit_factor'))} | {fmt(', '.join(notes))} |"
        )

    lines += [
        "",
        "## Current Baseline: EURUSD H1 Normal Gate",
        "",
        "| Phase | Net | PF | Rel DD | Trades | Days | Annualized | CAGR Approx | Calmar | Warning |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {fmt(row.get('phase'))} | {fmt(row.get('net_profit'))} | {fmt(row.get('profit_factor'))} | "
            f"{fmt(row.get('relative_drawdown'))} | {fmt(row.get('total_trades'))} | {fmt(row.get('test_period_days'))} | "
            f"{fmt(row.get('annualized_return_percent'))} | {fmt(row.get('cagr_approx_percent'))} | "
            f"{fmt(row.get('calmar_ratio'))} | {fmt(row.get('warning'))} |"
        )

    lines += [
        "",
        "## Validation + OOS Assessment",
        "",
        "| Net | Min PF | Max Rel DD | Trades | Days | Annualized | CAGR Approx | Calmar | Classification |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        f"| {fmt(combined.get('net_profit'))} | {fmt(combined.get('profit_factor'))} | {fmt(combined.get('relative_drawdown'))} | "
        f"{fmt(combined.get('total_trades'))} | {fmt(combined.get('test_period_days'))} | "
        f"{fmt(combined.get('annualized_return_percent'))} | {fmt(combined.get('cagr_approx_percent'))} | "
        f"{fmt(combined.get('calmar_ratio'))} | {fmt(combined.get('risk_adjusted_classification'))} |",
        "",
        "## Interpretation",
        "",
        "- Validation and out-of-sample are positive, but the absolute return is still small on a 10000 deposit.",
        "- The baseline remains `RESEARCH_MORE`; it is not demo-forward ready and not a final candidate.",
        "- The current result is not a reason to increase lot size or risk. Edge quality should improve before exposure size.",
        "- Normal losing-streak gate remains the baseline after Checkpoint J.",
        "- Annualized numbers can look attractive when drawdown is tiny, but they are still informational when trade count is limited or test windows are short.",
        "",
        "## Verdict",
        "",
    ]
    if combined.get("risk_adjusted_classification") in {"MEETS_CONSERVATIVE_FOREX_TARGET", "MEETS_BALANCED_TARGET"}:
        lines.append("The current baseline may meet a numeric target, but no live/demo readiness is assigned in this checkpoint.")
    elif combined.get("risk_adjusted_classification") == "BELOW_FOREX_RISK_PREMIUM":
        lines.append("The current baseline does not yet meet the minimum Forex risk premium target.")
    else:
        lines.append("The current baseline is still a research baseline only and should not be treated as worth-the-risk yet.")
    lines.append("")
    lines.append("No optimization, lot increase, new strategy, or profitability claim was made.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="run_20260621_214917")
    parser.add_argument("--case-id", default="EURUSD_H1_RISKGATE_NORMAL_10000")
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--target-profile", default="research/target_profile.json")
    args = parser.parse_args()

    run_root = Path(args.runs_root) / args.run_id
    rows = []
    for phase in PHASES:
        case_dir = run_root / f"{args.case_id}_{phase}"
        if case_dir.exists():
            rows.append(phase_metrics(case_dir))
    if len(rows) != 3:
        raise SystemExit(f"Expected 3 phase folders for {args.case_id} in {run_root}, found {len(rows)}")

    combined = combined_validation_oos(rows)
    all_rows = rows + [combined]
    results_root = Path(args.results_root)
    write_csv(results_root / "annual_target_scores.csv", all_rows)
    write_markdown(
        results_root / "annual_target_assessment.md",
        load_json(Path(args.target_profile)),
        rows,
        combined,
    )
    print(f"Wrote annual target assessment for {args.run_id}/{args.case_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
