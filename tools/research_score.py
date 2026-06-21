#!/usr/bin/env python3
"""Score ForexAiTrade research runs with survival-first phase and case gates."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PASSING_INFRA = {"PASS"}
REQUIRED_PHASES = {"train", "validation", "out_of_sample"}


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
    }

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


def apply_case_level_classifications(rows: list[dict[str, Any]]) -> None:
    by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row.get("run_id")), str(row.get("base_case_id") or row.get("case_id")))
        by_key.setdefault(key, []).append(row)

    for group in by_key.values():
        classification, failed_gates = classify_case(group)
        for row in group:
            row["case_level_classification"] = classification
            row["case_failed_gates"] = failed_gates


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
