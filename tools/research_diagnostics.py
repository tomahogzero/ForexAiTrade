#!/usr/bin/env python3
"""Extract research diagnostics from ForexAiTrade run artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any


SIGNAL_RE = re.compile(r"Signal (?P<kind>accepted|blocked): (?P<body>.*)$")
NO_TRADE_RE = re.compile(r"No trade: (?P<body>.*)$")
SYMBOL_RE = re.compile(r"Symbol diagnostics: (?P<body>.*)$")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


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


def resolve_run_root(args: argparse.Namespace) -> Path:
    if args.run_root:
        return Path(args.run_root)
    runs_root = Path(args.runs_root)
    selected = None if args.latest_run else args.run_id
    run_id = selected or latest_successful_run_id(runs_root)
    if not run_id:
        raise SystemExit(f"No run directories found under {runs_root}")
    run_root = runs_root / run_id
    if not run_root.exists():
        raise SystemExit(f"RunId not found: {run_id}")
    return run_root


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            return None
        return val
    except (TypeError, ValueError):
        return None


def parse_kv(body: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for match in re.finditer(r"([A-Za-z_]+)=([^=]*?)(?=\s+[A-Za-z_]+=|$)", body):
        key = match.group(1).strip()
        value = match.group(2).strip()
        pairs[key] = value
    return pairs


def avg(values: list[float]) -> float | None:
    return round(mean(values), 6) if values else None


def med(values: list[float]) -> float | None:
    return round(median(values), 6) if values else None


def pct(part: int, whole: int) -> float | None:
    if whole <= 0:
        return None
    return round((part / whole) * 100.0, 2)


def count_reason(counter: Counter[str], reason: str) -> None:
    text = reason.lower()
    if "spread too wide" in text or "spread too high" in text:
        counter["spread_blocks"] += 1
    if "max open" in text:
        counter["max_open_order_blocks"] += 1
    if "losing streak" in text:
        counter["losing_streak_blocks"] += 1
    if "daily" in text:
        counter["daily_loss_blocks"] += 1
    if "weekly" in text:
        counter["weekly_loss_blocks"] += 1
    if "drawdown" in text or "equity kill" in text:
        counter["drawdown_blocks"] += 1
    if "margin" in text:
        counter["margin_blocks"] += 1
    if "stops" in text:
        counter["stops_level_blocks"] += 1
    if "freeze" in text:
        counter["freeze_level_blocks"] += 1
    if "broker minimum lot" in text or "risk budget" in text:
        counter["broker_minimum_lot_risk_budget_blocks"] += 1


def classify_recommendation(diag: dict[str, Any]) -> str:
    case_level = diag.get("case_level_classification")
    symbol = diag.get("symbol")
    timeframe = diag.get("timeframe")
    accepted = diag.get("accepted_signals") or 0
    risk_blocks = diag.get("broker_minimum_lot_risk_budget_blocks") or 0
    trades = diag.get("report_total_trades") or 0
    net = to_float(diag.get("report_net_profit"))

    if risk_blocks > 0 and accepted == 0:
        return "NEEDS_RISK_BUDGET_REVIEW"
    if case_level == "TRAIN_FAILED_VALIDATION_OOS_PASS":
        return "RESEARCH_MORE"
    if case_level == "VALIDATION_OOS_PASS":
        return "RESEARCH_MORE"
    if case_level == "PROVISIONAL_RESEARCH_CANDIDATE":
        return "KEEP_FOR_BASELINE"
    if trades < 30 and symbol in {"USDJPY#", "GOLD#"}:
        return "NEEDS_TIMEFRAME_REVIEW"
    if net is not None and net < 0:
        return "REJECT_FOR_NOW"
    if timeframe in {"H1", "H4"} and accepted > 0:
        return "RESEARCH_MORE"
    return "REJECT_FOR_NOW"


def phase_row(rows: list[dict[str, Any]], phase: str) -> dict[str, Any]:
    return next((row for row in rows if row.get("phase") == phase), {})


def phase_net(row: dict[str, Any]) -> float | None:
    return to_float(row.get("report_net_profit"))


def phase_trades(row: dict[str, Any]) -> int:
    try:
        return int(float(row.get("report_total_trades") or 0))
    except (TypeError, ValueError):
        return 0


def classify_case_recommendation(case_id: str, rows: list[dict[str, Any]]) -> tuple[str, str]:
    train = phase_row(rows, "train")
    validation = phase_row(rows, "validation")
    oos = phase_row(rows, "out_of_sample")

    total_risk_blocks = sum(int(row.get("broker_minimum_lot_risk_budget_blocks") or 0) for row in rows)
    total_accepted = sum(int(row.get("accepted_signals") or 0) for row in rows)
    if "GOLD" in case_id and total_risk_blocks > 0 and total_accepted == 0:
        return "NEEDS_RISK_BUDGET_REVIEW", "Broker minimum lot / risk-budget blocks prevented executable signals under current risk settings."

    if not validation or not oos:
        return "REJECT_FOR_NOW", "Missing validation or out-of-sample diagnostics; keep out of candidate selection."

    validation_net = phase_net(validation)
    oos_net = phase_net(oos)
    train_net = phase_net(train)
    validation_trades = phase_trades(validation)
    oos_trades = phase_trades(oos)
    train_trades = phase_trades(train)

    if validation_net is None or oos_net is None:
        return "REJECT_FOR_NOW", "Validation or out-of-sample net profit is unavailable."
    if validation_net < 0:
        return "REJECT_FOR_NOW", f"Validation is negative ({validation_net}) and validation trades are {validation_trades}."
    if oos_net < 0:
        return "REJECT_FOR_NOW", f"Out-of-sample is negative ({oos_net}) and OOS trades are {oos_trades}."
    if validation_trades < 30:
        return "REJECT_FOR_NOW", f"Validation trades are extremely low ({validation_trades}); positive OOS alone is not enough."
    if oos_trades < 30:
        return "REJECT_FOR_NOW", f"Out-of-sample trades are extremely low ({oos_trades}); evidence is too thin."

    train_weak = (train_net is None or train_net < 0 or train_trades < 30)
    if train_weak:
        return (
            "RESEARCH_MORE",
            f"Validation and OOS are positive with acceptable trade counts, but train is weak (net={train_net}, trades={train_trades}).",
        )

    return "KEEP_FOR_BASELINE", "Train, validation, and OOS are positive enough for baseline tracking only; this is not live readiness."


def diagnose_case(case_dir: Path, score_rows: list[dict[str, str]]) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    status = load_json(case_dir / "status.json")
    parsed = load_json(case_dir / "parsed_result.json")
    ea_log = case_dir / "ea_mirror.log"
    lines = ea_log.read_text(encoding="utf-8", errors="ignore").splitlines() if ea_log.exists() else []

    score = next(
        (
            row for row in score_rows
            if row.get("run_id") == case.get("run_id")
            and row.get("case_id") == case.get("case_id", case_dir.name)
        ),
        {},
    )

    counts: Counter[str] = Counter()
    direction_counts: Counter[str] = Counter()
    regime_counts: Counter[str] = Counter()
    accepted_regime_counts: Counter[str] = Counter()
    blocked_reason_counts: Counter[str] = Counter()
    no_trade_reason_counts: Counter[str] = Counter()
    symbol_meta: dict[str, Any] = {}

    sl_distances: list[float] = []
    tp_distances: list[float] = []
    raw_lots: list[float] = []
    normalized_lots: list[float] = []
    actual_risks: list[float] = []
    logged_spreads: list[float] = []
    signal_spreads: list[float] = []
    blocked_raw_lots: list[float] = []
    blocked_risk_money: list[float] = []
    blocked_sl_distances: list[float] = []

    for line in lines:
        symbol_match = SYMBOL_RE.search(line)
        if symbol_match:
            meta = parse_kv(symbol_match.group("body"))
            for key, value in meta.items():
                symbol_meta[key] = to_float(value) if re.match(r"^-?\d+(\.\d+)?$", value) else value

        no_trade_match = NO_TRADE_RE.search(line)
        if no_trade_match:
            counts["no_trade_bars"] += 1
            data = parse_kv(no_trade_match.group("body"))
            reason = data.get("reason", "")
            regime = data.get("regime", "")
            if regime:
                regime_counts[regime] += 1
            if reason == "no strategy signal":
                counts["no_signal_bars"] += 1
            if regime == "unsafe" or reason.startswith("unsafe regime"):
                counts["unsafe_regime_blocks"] += 1
            no_trade_reason_counts[reason] += 1
            count_reason(counts, reason)
            spread = to_float(data.get("spread"))
            if spread is not None:
                logged_spreads.append(spread)
            continue

        signal_match = SIGNAL_RE.search(line)
        if signal_match:
            kind = signal_match.group("kind")
            data = parse_kv(signal_match.group("body"))
            reason = data.get("reason", "")
            regime = data.get("regime", "")
            direction = data.get("direction", "")
            if kind == "accepted":
                counts["accepted_signals"] += 1
                if regime:
                    accepted_regime_counts[regime] += 1
            else:
                counts["rejected_signals"] += 1
                blocked_reason_counts[reason] += 1
                count_reason(counts, reason)
            if regime:
                regime_counts[regime] += 1
            if direction:
                direction_counts[direction] += 1

            entry = to_float(data.get("entry"))
            sl = to_float(data.get("sl"))
            tp = to_float(data.get("tp"))
            raw_lot = to_float(data.get("raw_lot"))
            normalized_lot = to_float(data.get("normalized_lot"))
            actual_risk = to_float(data.get("actual_risk_money"))
            risk_money = to_float(data.get("risk_money"))
            spread = to_float(data.get("spread"))
            if entry and sl:
                dist = abs(entry - sl)
                if kind == "accepted":
                    sl_distances.append(dist)
                else:
                    blocked_sl_distances.append(dist)
            if entry and tp and kind == "accepted":
                tp_distances.append(abs(tp - entry))
            if raw_lot is not None:
                if kind == "accepted":
                    raw_lots.append(raw_lot)
                else:
                    blocked_raw_lots.append(raw_lot)
            if normalized_lot is not None and kind == "accepted":
                normalized_lots.append(normalized_lot)
            if actual_risk is not None and kind == "accepted":
                actual_risks.append(actual_risk)
            if risk_money is not None and kind == "blocked":
                blocked_risk_money.append(risk_money)
            if spread is not None:
                signal_spreads.append(spread)
                logged_spreads.append(spread)

    risk_percent = to_float(case.get("risk_percent"))
    deposit = to_float(case.get("deposit"))
    min_lot = to_float(symbol_meta.get("min_lot"))
    typical_blocked_raw_lot = med([v for v in blocked_raw_lots if v and v > 0])
    typical_blocked_risk_money = med([v for v in blocked_risk_money if v and v > 0])
    typical_sl_distance = med(blocked_sl_distances) or avg(sl_distances)
    estimated_minimum_deposit = None
    if deposit and min_lot and typical_blocked_raw_lot and typical_blocked_raw_lot > 0:
        estimated_minimum_deposit = round(deposit * (min_lot / typical_blocked_raw_lot), 2)
    elif min_lot and risk_percent and typical_blocked_risk_money and typical_blocked_raw_lot:
        actual_risk_for_min_lot = typical_blocked_risk_money * (min_lot / typical_blocked_raw_lot)
        estimated_minimum_deposit = round(actual_risk_for_min_lot / (risk_percent / 100.0), 2)

    suggested_deposit = None
    if estimated_minimum_deposit:
        if estimated_minimum_deposit <= 50_000:
            suggested_deposit = 50_000
        elif estimated_minimum_deposit <= 100_000:
            suggested_deposit = 100_000
        else:
            suggested_deposit = math.ceil(estimated_minimum_deposit / 50_000.0) * 50_000

    total_signal_opportunities = counts["accepted_signals"] + counts["rejected_signals"]
    diag: dict[str, Any] = {
        "run_id": case.get("run_id"),
        "case_id": case.get("case_id", case_dir.name),
        "base_case_id": case.get("base_case_id"),
        "phase": case.get("phase"),
        "symbol": case.get("actual_symbol") or parsed.get("symbol"),
        "canonical_symbol": case.get("canonical_symbol"),
        "timeframe": case.get("timeframe") or parsed.get("timeframe"),
        "execution_status": status.get("execution_status"),
        "phase_classification": score.get("phase_classification") or score.get("research_classification"),
        "case_level_classification": score.get("case_level_classification"),
        "case_failed_gates": score.get("case_failed_gates"),
        "report_net_profit": parsed.get("net_profit"),
        "report_profit_factor": parsed.get("profit_factor"),
        "report_relative_drawdown": parsed.get("relative_drawdown"),
        "report_total_trades": parsed.get("total_trades"),
        "accepted_signals": counts["accepted_signals"],
        "rejected_signals": counts["rejected_signals"],
        "signal_acceptance_rate_pct": pct(counts["accepted_signals"], total_signal_opportunities),
        "no_trade_bars": counts["no_trade_bars"],
        "no_signal_bars": counts["no_signal_bars"],
        "unsafe_regime_blocks": counts["unsafe_regime_blocks"],
        "spread_blocks": counts["spread_blocks"],
        "max_open_order_blocks": counts["max_open_order_blocks"],
        "losing_streak_blocks": counts["losing_streak_blocks"],
        "daily_loss_blocks": counts["daily_loss_blocks"],
        "weekly_loss_blocks": counts["weekly_loss_blocks"],
        "drawdown_blocks": counts["drawdown_blocks"],
        "margin_blocks": counts["margin_blocks"],
        "stops_level_blocks": counts["stops_level_blocks"],
        "freeze_level_blocks": counts["freeze_level_blocks"],
        "broker_minimum_lot_risk_budget_blocks": counts["broker_minimum_lot_risk_budget_blocks"],
        "buy_count": direction_counts["buy"],
        "sell_count": direction_counts["sell"],
        "regime_counts": dict(regime_counts),
        "accepted_regime_counts": dict(accepted_regime_counts),
        "blocked_reason_counts": dict(blocked_reason_counts),
        "no_trade_reason_counts": dict(no_trade_reason_counts),
        "average_sl_distance": avg(sl_distances),
        "average_tp_distance": avg(tp_distances),
        "average_raw_lot": avg(raw_lots),
        "average_normalized_lot": avg(normalized_lots),
        "average_actual_risk_money": avg(actual_risks),
        "average_spread_at_signal_time": avg(signal_spreads),
        "average_logged_spread": avg(logged_spreads),
        "symbol_min_lot": min_lot,
        "symbol_lot_step": symbol_meta.get("lot_step"),
        "symbol_tick_size": symbol_meta.get("tick_size"),
        "symbol_tick_value": symbol_meta.get("tick_value"),
        "symbol_contract_size": symbol_meta.get("contract_size"),
        "risk_percent": risk_percent,
        "deposit": deposit,
        "typical_blocked_raw_lot": typical_blocked_raw_lot,
        "typical_blocked_sl_distance": typical_sl_distance,
        "estimated_minimum_deposit_for_min_lot": estimated_minimum_deposit,
        "current_deposit_insufficient_for_min_lot": bool(estimated_minimum_deposit and deposit and estimated_minimum_deposit > deposit),
        "suggested_next_deposit_assumption_research_only": suggested_deposit,
    }
    diag["recommendation"] = classify_recommendation(diag)
    return diag


def write_case_markdown(path: Path, diag: dict[str, Any]) -> None:
    lines = [
        f"# Diagnostics: {diag.get('case_id')}",
        "",
        f"- Symbol: `{diag.get('symbol')}`",
        f"- Timeframe: `{diag.get('timeframe')}`",
        f"- Phase: `{diag.get('phase')}`",
        f"- Execution: `{diag.get('execution_status')}`",
        f"- Phase classification: `{diag.get('phase_classification')}`",
        f"- Case classification: `{diag.get('case_level_classification')}`",
        f"- Recommendation: `{diag.get('recommendation')}`",
        "",
        "## Signal Diagnostics",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in [
        "accepted_signals", "rejected_signals", "signal_acceptance_rate_pct", "no_signal_bars",
        "unsafe_regime_blocks", "spread_blocks", "max_open_order_blocks", "losing_streak_blocks",
        "broker_minimum_lot_risk_budget_blocks", "buy_count", "sell_count",
        "average_sl_distance", "average_tp_distance", "average_raw_lot",
        "average_normalized_lot", "average_actual_risk_money", "average_logged_spread",
    ]:
        lines.append(f"| {key} | {diag.get(key)} |")
    lines += [
        "",
        "## GOLD / Risk Budget Review",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| risk_percent | {diag.get('risk_percent')} |",
        f"| deposit | {diag.get('deposit')} |",
        f"| symbol_min_lot | {diag.get('symbol_min_lot')} |",
        f"| typical_blocked_raw_lot | {diag.get('typical_blocked_raw_lot')} |",
        f"| typical_blocked_sl_distance | {diag.get('typical_blocked_sl_distance')} |",
        f"| estimated_minimum_deposit_for_min_lot | {diag.get('estimated_minimum_deposit_for_min_lot')} |",
        f"| current_deposit_insufficient_for_min_lot | {diag.get('current_deposit_insufficient_for_min_lot')} |",
        f"| suggested_next_deposit_assumption_research_only | {diag.get('suggested_next_deposit_assumption_research_only')} |",
        "",
        "This diagnostic is not an instruction to force minimum lot or increase risk.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def flatten_for_csv(diag: dict[str, Any]) -> dict[str, Any]:
    row = {k: v for k, v in diag.items() if not isinstance(v, (dict, list))}
    row["regime_counts_json"] = json.dumps(diag.get("regime_counts", {}), ensure_ascii=False)
    row["blocked_reason_counts_json"] = json.dumps(diag.get("blocked_reason_counts", {}), ensure_ascii=False)
    return row


def group_by_case(diags: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for diag in diags:
        grouped[str(diag.get("base_case_id") or diag.get("case_id"))].append(diag)
    return grouped


def summarize_case(case_id: str, rows: list[dict[str, Any]]) -> str:
    total_accepted = sum(int(r.get("accepted_signals") or 0) for r in rows)
    total_rejected = sum(int(r.get("rejected_signals") or 0) for r in rows)
    total_risk_blocks = sum(int(r.get("broker_minimum_lot_risk_budget_blocks") or 0) for r in rows)
    total_losing_blocks = sum(int(r.get("losing_streak_blocks") or 0) for r in rows)
    total_max_open = sum(int(r.get("max_open_order_blocks") or 0) for r in rows)
    profits = {r.get("phase"): to_float(r.get("report_net_profit")) for r in rows}
    trades = {r.get("phase"): r.get("report_total_trades") for r in rows}
    recommendation, reason = classify_case_recommendation(case_id, rows)
    if "GOLD" in case_id:
        if total_risk_blocks:
            return f"{case_id}: blocked mainly by risk budget/minimum lot ({total_risk_blocks} blocks). Train traded, but validation/OOS did not get executable size under current risk."
        return f"{case_id}: gold case needs more risk-budget review; no direct strategy conclusion."
    if "USDJPY" in case_id:
        return f"{case_id}: weak across phases. Net profits={profits}, trades={trades}, accepted={total_accepted}, rejected={total_rejected}; do not optimize blindly."
    if "EURUSD" in case_id:
        return f"{case_id}: {recommendation}. {reason} Net profits={profits}, trades={trades}; not a strong candidate."
    return f"{case_id}: recommendation={recommendation}, reason={reason}, accepted={total_accepted}, rejected={total_rejected}, losing_streak_blocks={total_losing_blocks}, max_open_blocks={total_max_open}."


def write_aggregate_summary(path: Path, diags: list[dict[str, Any]]) -> None:
    grouped = group_by_case(diags)
    lines = [
        "# ForexAiTrade Diagnostics Summary",
        "",
        "Diagnostics are based on EA mirror logs and MT5 reports. They are not profitability proof.",
        "",
        "## Case Diagnoses",
        "",
        "| Case | Diagnosis |",
        "|---|---|",
    ]
    for case_id, rows in sorted(grouped.items()):
        lines.append(f"| {case_id} | {summarize_case(case_id, rows).replace('|', '/')} |")

    gold_rows = [row for row in diags if row.get("canonical_symbol") == "GOLD"]
    if gold_rows:
        lines += [
            "",
            "## GOLD# Risk Budget Review",
            "",
            "| Case | Phase | Risk % | Deposit | Broker Min Lot | Typical SL Distance | Estimated Min Deposit | 30000 Insufficient | Research-Only Next Deposit Assumption |",
            "|---|---|---:|---:|---:|---:|---:|---|---:|",
        ]
        for row in gold_rows:
            lines.append(
                f"| {row.get('base_case_id')} | {row.get('phase')} | {row.get('risk_percent')} | "
                f"{row.get('deposit')} | {row.get('symbol_min_lot')} | {row.get('typical_blocked_sl_distance')} | "
                f"{row.get('estimated_minimum_deposit_for_min_lot')} | {row.get('current_deposit_insufficient_for_min_lot')} | "
                f"{row.get('suggested_next_deposit_assumption_research_only')} |"
            )

    lines += [
        "",
        "## Direct Answers",
        "",
        "### Why does EURUSD H1 remain RESEARCH_MORE?",
        "",
        "EURUSD H1 had negative train performance and only 22 train trades, while validation and out-of-sample were positive with acceptable trade counts. This is interesting enough for diagnostics, but it is not a strong candidate or forward/live-ready result.",
        "",
        "### Why is EURUSD M30 rejected for now?",
        "",
        "EURUSD M30 has positive out-of-sample, but validation is negative and validation trades are extremely low. Positive OOS alone is not enough for forward/live readiness.",
        "",
        "### Why is EURUSD H4 rejected for now?",
        "",
        "EURUSD H4 has negative validation and out-of-sample results, and validation/OOS trade counts are low. It should not drive strategy changes or optimization.",
        "",
        "### What if GOLD# appears in this run?",
        "",
        "GOLD# cases with broker minimum lot / risk-budget blocks should remain NEEDS_RISK_BUDGET_REVIEW. That condition is not automatically a strategy-entry failure, and the EA must not force minimum lot or increase risk automatically.",
        "",
        "### Which symbol/timeframe deserves further research from this checkpoint?",
        "",
        "EURUSD H1 deserves baseline tracking and further diagnostics only. M30 and H4 should be rejected for now.",
        "",
        "### Which cases should be rejected for now?",
        "",
        "EURUSD M30 and EURUSD H4 should be rejected for now. Low-trade phases should not be used to justify optimization or new strategy work.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_recommendations(path: Path, diags: list[dict[str, Any]]) -> None:
    grouped = group_by_case(diags)
    lines = [
        "# Next Research Recommendation",
        "",
        "No parameter values are proposed here. No optimization is performed.",
        "",
        "| Case | Recommendation | Reason |",
        "|---|---|---|",
    ]
    for case_id, rows in sorted(grouped.items()):
        rec, reason = classify_case_recommendation(case_id, rows)
        lines.append(f"| {case_id} | {rec} | {reason.replace('|', '/')} {summarize_case(case_id, rows).replace('|', '/')} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_scores(results_root: Path) -> list[dict[str, str]]:
    score_path = results_root / "all_scores.csv"
    if not score_path.exists() or score_path.stat().st_size == 0:
        return []
    with score_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root")
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--run-id")
    parser.add_argument("--latest-run", action="store_true")
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    run_root = resolve_run_root(args)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)
    score_rows = read_scores(results_root)

    diagnostics: list[dict[str, Any]] = []
    for case_dir in sorted(run_root.iterdir()):
        if not case_dir.is_dir() or not (case_dir / "case.json").exists():
            continue
        diag = diagnose_case(case_dir, score_rows)
        diagnostics.append(diag)
        (case_dir / "diagnostics.json").write_text(json.dumps(diag, indent=2, ensure_ascii=False), encoding="utf-8")
        write_case_markdown(case_dir / "diagnostics_summary.md", diag)

    csv_path = results_root / "diagnostics_all_cases.csv"
    rows = [flatten_for_csv(diag) for diag in diagnostics]
    fields = sorted({key for row in rows for key in row.keys()})
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    write_aggregate_summary(results_root / "diagnostics_summary.md", diagnostics)
    write_recommendations(results_root / "next_research_recommendation.md", diagnostics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
