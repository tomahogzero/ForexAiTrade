#!/usr/bin/env python3
"""Score ForexAiTrade research runs with survival-first phase and case gates."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


PASSING_INFRA = {"PASS"}
REQUIRED_PHASES = {"train", "validation", "out_of_sample"}
MIN_ANNUALIZATION_DAYS = 180
MIN_ANNUALIZATION_TRADES = 50


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    text = str(value).strip()
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


def risk_adjusted_metrics(parsed: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    deposit = to_float(parsed.get("deposit")) or to_float(case.get("deposit"))
    net_profit = to_float(parsed.get("net_profit"))
    rel_dd = to_float(parsed.get("relative_drawdown"))
    if rel_dd is None:
        rel_dd = to_float(parsed.get("drawdown_relative"))
    days = period_days(parsed, case)
    trades = to_int(parsed.get("total_trades")) or 0
    warnings = []

    result: dict[str, Any] = {
        "test_period_days": days,
        "annualized_return_percent": None,
        "cagr_approx_percent": None,
        "max_relative_drawdown_percent": rel_dd,
        "calmar_ratio": None,
        "return_to_drawdown_ratio": None,
        "monthly_return_estimate": None,
        "annualized_return_informational_only": False,
        "annualized_return_warning": "",
    }

    if deposit is None or deposit <= 0 or net_profit is None or days is None or days <= 0:
        result["annualized_return_warning"] = "missing_deposit_profit_or_period"
        return result

    period_return_pct = (net_profit / deposit) * 100.0
    annualized = period_return_pct * 365.0 / days
    cagr = ((1.0 + net_profit / deposit) ** (365.0 / days) - 1.0) * 100.0 if (1.0 + net_profit / deposit) > 0 else None
    result["annualized_return_percent"] = round(annualized, 4)
    result["cagr_approx_percent"] = round(cagr, 4) if cagr is not None else None
    result["monthly_return_estimate"] = round(annualized / 12.0, 4)

    if rel_dd is not None and rel_dd > 0:
        result["calmar_ratio"] = round(annualized / rel_dd, 4)
        result["return_to_drawdown_ratio"] = round(period_return_pct / rel_dd, 4)

    if days < MIN_ANNUALIZATION_DAYS:
        warnings.append("short_test_period")
    if trades < MIN_ANNUALIZATION_TRADES:
        warnings.append("low_trade_count")
    if warnings:
        result["annualized_return_informational_only"] = True
        result["annualized_return_warning"] = ",".join(warnings)
    return result


def classify_phase(case_dir: Path, min_trades: int, max_drawdown_pct: float) -> dict[str, Any]:
    status = load_json(case_dir / "status.json") or {}
    parsed = load_json(case_dir / "parsed_result.json") or {}
    case = load_json(case_dir / "case.json") or {}
    ea_log = case_dir / "ea_mirror.log"
    ea_text = ea_log.read_text(encoding="utf-8", errors="ignore") if ea_log.exists() else ""

    execution_status = status.get("execution_status", "FAILED")
    row: dict[str, Any] = {
        "run_id": case.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id", case_dir.name),
        "base_case_id": case.get("base_case_id"),
        "phase": case.get("phase"),
        "symbol": case.get("actual_symbol"),
        "canonical_symbol": case.get("canonical_symbol"),
        "timeframe": case.get("timeframe"),
        "deposit": parsed.get("deposit") or case.get("deposit"),
        "execution_status": execution_status,
        "phase_classification": None,
        "research_classification": None,
        "case_level_classification": None,
        "case_failed_gates": "",
        "score": None,
        "failed_gates": "",
        "net_profit": parsed.get("net_profit"),
        "profit_factor": parsed.get("profit_factor"),
        "max_drawdown": parsed.get("max_drawdown"),
        "relative_drawdown": parsed.get("relative_drawdown"),
        "total_trades": parsed.get("total_trades"),
        "consecutive_losses": parsed.get("consecutive_losses"),
        "largest_win": parsed.get("largest_win"),
        "largest_loss": parsed.get("largest_loss"),
        "test_period_days": None,
        "annualized_return_percent": None,
        "cagr_approx_percent": None,
        "max_relative_drawdown_percent": None,
        "calmar_ratio": None,
        "return_to_drawdown_ratio": None,
        "monthly_return_estimate": None,
        "annualized_return_informational_only": False,
        "annualized_return_warning": "",
        "risk_adjusted_classification": None,
    }
    row.update(risk_adjusted_metrics(parsed, case))

    if execution_status not in PASSING_INFRA:
        row["phase_classification"] = "EXECUTION_FAILED"
        row["failed_gates"] = execution_status
        row["research_classification"] = row["phase_classification"]
        return row

    trades = to_int(parsed.get("total_trades"))
    net_profit = to_float(parsed.get("net_profit"))
    rel_dd = to_float(parsed.get("relative_drawdown"))
    if rel_dd is None:
        rel_dd = to_float(parsed.get("max_drawdown"))

    if "broker minimum lot exceeds configured risk budget" in ea_text and "Signal accepted" not in ea_text:
        row["phase_classification"] = "NO_RISK_BUDGET"
        row["failed_gates"] = "broker_min_lot_exceeds_risk_budget"
        row["research_classification"] = row["phase_classification"]
        return row

    if trades in (None, 0):
        row["phase_classification"] = "NO_TRADES" if "Signal accepted" not in ea_text else "RISK_GATE_FAILED"
        row["research_classification"] = row["phase_classification"]
        return row

    failed = []
    if trades < min_trades:
        failed.append("insufficient_trades")
    if rel_dd is not None and rel_dd > max_drawdown_pct:
        failed.append("drawdown")

    if failed:
        row["phase_classification"] = "INSUFFICIENT_TRADES" if "insufficient_trades" in failed else "RISK_GATE_FAILED"
        row["failed_gates"] = ",".join(failed)
        row["research_classification"] = row["phase_classification"]
        return row

    row["phase_classification"] = "VALID_RESULT"
    row["research_classification"] = row["phase_classification"]
    if net_profit is None:
        row["failed_gates"] = "missing_net_profit"
        return row

    pf = to_float(parsed.get("profit_factor")) or 1.0
    dd_penalty = rel_dd or 0.0
    row["score"] = round(net_profit + (pf * 10.0) - (dd_penalty * 5.0), 4)
    return row


def positive_valid(row: dict[str, Any]) -> bool:
    net = to_float(row.get("net_profit"))
    return row.get("execution_status") == "PASS" and row.get("phase_classification") == "VALID_RESULT" and net is not None and net > 0


def train_failed_or_insufficient(row: dict[str, Any] | None) -> bool:
    if row is None:
        return True
    net = to_float(row.get("net_profit"))
    if net is not None and net < 0:
        return True
    return row.get("phase_classification") in {"INSUFFICIENT_TRADES", "NO_TRADES", "NO_RISK_BUDGET", "RISK_GATE_FAILED", "EXECUTION_FAILED"}


def classify_case(group: list[dict[str, Any]]) -> tuple[str, str]:
    phases = {str(row.get("phase")): row for row in group if row.get("phase")}
    missing = sorted(REQUIRED_PHASES - set(phases))
    if missing:
        return "INCOMPLETE_PHASES", "missing_" + ",".join(missing)

    if any(row.get("execution_status") != "PASS" for row in phases.values()):
        return "EXECUTION_FAILED", "infrastructure_failure"

    if all(row.get("phase_classification") == "NO_RISK_BUDGET" for row in phases.values()):
        return "NO_RISK_BUDGET", "broker_min_lot_exceeds_risk_budget"

    train = phases["train"]
    validation = phases["validation"]
    out_of_sample = phases["out_of_sample"]
    validation_oos_positive = positive_valid(validation) and positive_valid(out_of_sample)

    if not validation_oos_positive:
        return "REJECTED", "validation_or_oos_not_positive_valid"

    if train_failed_or_insufficient(train):
        return "TRAIN_FAILED_VALIDATION_OOS_PASS", "train_negative_or_insufficient"

    validation_trades = to_int(validation.get("total_trades")) or 0
    oos_trades = to_int(out_of_sample.get("total_trades")) or 0
    total_validation_oos_trades = validation_trades + oos_trades
    if total_validation_oos_trades < 150 or validation_trades < 50 or oos_trades < 50:
        return "INSUFFICIENT_TOTAL_TRADES", "validation_oos_trade_count"

    failed = []
    for phase_name, row in (("validation", validation), ("out_of_sample", out_of_sample)):
        rel_dd = to_float(row.get("relative_drawdown"))
        pf = to_float(row.get("profit_factor"))
        if rel_dd is not None and rel_dd > 20.0:
            failed.append(f"{phase_name}_drawdown")
        if pf is None or pf < 1.10:
            failed.append(f"{phase_name}_profit_factor")
    if failed:
        return "VALIDATION_OOS_PASS", ",".join(failed)

    return "PROVISIONAL_RESEARCH_CANDIDATE", ""


def combined_validation_oos_metrics(phases: dict[str, dict[str, Any]]) -> dict[str, Any]:
    validation = phases.get("validation", {})
    out_of_sample = phases.get("out_of_sample", {})
    deposit = to_float(validation.get("deposit")) or to_float(out_of_sample.get("deposit"))
    net_profit = (to_float(validation.get("net_profit")) or 0.0) + (to_float(out_of_sample.get("net_profit")) or 0.0)
    days = (to_int(validation.get("test_period_days")) or 0) + (to_int(out_of_sample.get("test_period_days")) or 0)
    trades = (to_int(validation.get("total_trades")) or 0) + (to_int(out_of_sample.get("total_trades")) or 0)
    rel_dd = max(to_float(validation.get("max_relative_drawdown_percent")) or 0.0,
                 to_float(out_of_sample.get("max_relative_drawdown_percent")) or 0.0)
    pf_values = [to_float(validation.get("profit_factor")), to_float(out_of_sample.get("profit_factor"))]
    pf_values = [value for value in pf_values if value is not None]
    min_pf = min(pf_values) if pf_values else None

    annualized = None
    cagr = None
    calmar = None
    if deposit and deposit > 0 and days > 0:
        period_return_pct = (net_profit / deposit) * 100.0
        annualized = period_return_pct * 365.0 / days
        if (1.0 + net_profit / deposit) > 0:
            cagr = ((1.0 + net_profit / deposit) ** (365.0 / days) - 1.0) * 100.0
        if rel_dd > 0:
            calmar = annualized / rel_dd

    return {
        "validation_oos_net_profit": round(net_profit, 2),
        "validation_oos_days": days,
        "validation_oos_trades": trades,
        "validation_oos_min_profit_factor": round(min_pf, 4) if min_pf is not None else None,
        "validation_oos_max_relative_drawdown": round(rel_dd, 4),
        "validation_oos_annualized_return_percent": round(annualized, 4) if annualized is not None else None,
        "validation_oos_cagr_approx_percent": round(cagr, 4) if cagr is not None else None,
        "validation_oos_calmar_ratio": round(calmar, 4) if calmar is not None else None,
    }


def classify_risk_adjusted_case(case_classification: str, phases: dict[str, dict[str, Any]]) -> str:
    validation = phases.get("validation")
    out_of_sample = phases.get("out_of_sample")
    if case_classification in {"EXECUTION_FAILED", "INCOMPLETE_PHASES", "NO_RISK_BUDGET"}:
        return "NOT_VIABLE"
    if validation is None or out_of_sample is None:
        return "NOT_VIABLE"
    if not positive_valid(validation) or not positive_valid(out_of_sample):
        return "SURVIVAL_ONLY" if case_classification != "REJECTED" else "NOT_VIABLE"

    metrics = combined_validation_oos_metrics(phases)
    trades = to_int(metrics.get("validation_oos_trades")) or 0
    annualized = to_float(metrics.get("validation_oos_annualized_return_percent"))
    cagr = to_float(metrics.get("validation_oos_cagr_approx_percent"))
    dd = to_float(metrics.get("validation_oos_max_relative_drawdown"))
    calmar = to_float(metrics.get("validation_oos_calmar_ratio"))
    min_pf = to_float(metrics.get("validation_oos_min_profit_factor"))

    if trades < 150:
        return "SURVIVAL_ONLY"
    if annualized is None or cagr is None or dd is None:
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


def apply_case_level_classifications(rows: list[dict[str, Any]]) -> None:
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row.get("run_id")), str(row.get("base_case_id") or row.get("case_id")))
        by_key.setdefault(key, []).append(row)

    for group in by_key.values():
        classification, failed_gates = classify_case(group)
        phases = {str(row.get("phase")): row for row in group if row.get("phase")}
        risk_adjusted = classify_risk_adjusted_case(classification, phases)
        for row in group:
            row["case_level_classification"] = classification
            row["case_failed_gates"] = failed_gates
            row["risk_adjusted_classification"] = risk_adjusted


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--output", default="research/results/all_scores.csv")
    parser.add_argument("--min-trades", type=int, default=30)
    parser.add_argument("--max-drawdown-pct", type=float, default=20.0)
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    rows = []
    for case_dir in runs_root.glob("run_*/*"):
        if case_dir.is_dir():
            rows.append(classify_phase(case_dir, args.min_trades, args.max_drawdown_pct))
    apply_case_level_classifications(rows)
    write_csv(Path(args.output), rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
