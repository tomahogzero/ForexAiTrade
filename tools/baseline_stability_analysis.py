#!/usr/bin/env python3
"""Baseline stability and timeframe review reports for ForexAiTrade."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def read_report(path: Path) -> str:
    if not path.exists():
        return ""
    raw = path.read_bytes()
    for enc in ("utf-16", "utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def clean_cell(value: str) -> str:
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(str(value).replace(" ", "").replace(",", ""))
    except (TypeError, ValueError):
        return None


def to_int(value: Any) -> int:
    val = to_float(value)
    return int(val) if val is not None else 0


def parse_deals_by_month(report_path: Path) -> list[dict[str, Any]]:
    text = read_report(report_path)
    idx = text.find("<b>Deals</b>")
    if idx < 0:
        return []
    rows = re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", text[idx:])
    deals = []
    for row in rows:
        cells = [clean_cell(cell) for cell in re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)]
        if len(cells) < 13 or not re.match(r"\d{4}\.\d{2}\.\d{2}", cells[0]):
            continue
        entry = cells[4].lower()
        if entry != "out":
            continue
        profit = to_float(cells[10])
        if profit is None:
            continue
        month = cells[0][:7].replace(".", "-")
        deals.append({
            "month": month,
            "time": cells[0],
            "symbol": cells[2],
            "side": cells[3],
            "volume": to_float(cells[5]),
            "profit": profit,
            "balance": to_float(cells[11]),
            "comment": cells[12],
        })
    return deals


def monthly_rows(case_dir: Path, case: dict[str, Any]) -> list[dict[str, Any]]:
    deals = parse_deals_by_month(case_dir / "mt5_report.htm")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for deal in deals:
        grouped[deal["month"]].append(deal)
    rows = []
    for month, items in sorted(grouped.items()):
        profits = [float(item["profit"]) for item in items]
        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p < 0]
        rows.append({
            "run_id": case.get("run_id"),
            "base_case_id": case.get("base_case_id"),
            "case_id": case.get("case_id"),
            "phase": case.get("phase"),
            "symbol": case.get("actual_symbol"),
            "timeframe": case.get("timeframe"),
            "month": month,
            "closed_trades": len(items),
            "wins": len(wins),
            "losses": len(losses),
            "net_profit": round(sum(profits), 2),
            "gross_profit": round(sum(wins), 2),
            "gross_loss": round(sum(losses), 2),
            "drawdown_by_month": "",
        })
    return rows


def collect_case_rows(run_root: Path, base_case_filter: str | None = None) -> list[dict[str, Any]]:
    rows = []
    for case_dir in sorted(run_root.iterdir()):
        if not case_dir.is_dir() or not (case_dir / "case.json").exists():
            continue
        case = load_json(case_dir / "case.json")
        if base_case_filter and case.get("base_case_id") != base_case_filter:
            continue
        parsed = load_json(case_dir / "parsed_result.json")
        diag = load_json(case_dir / "diagnostics.json")
        rows.append({
            "run_id": case.get("run_id"),
            "base_case_id": case.get("base_case_id"),
            "case_id": case.get("case_id"),
            "phase": case.get("phase"),
            "symbol": case.get("actual_symbol"),
            "timeframe": case.get("timeframe"),
            "net_profit": parsed.get("net_profit"),
            "profit_factor": parsed.get("profit_factor"),
            "relative_drawdown": parsed.get("relative_drawdown"),
            "max_drawdown": parsed.get("max_drawdown"),
            "total_trades": parsed.get("total_trades"),
            "long_trades": parsed.get("long_trades"),
            "short_trades": parsed.get("short_trades"),
            "accepted_signals": diag.get("accepted_signals"),
            "rejected_signals": diag.get("rejected_signals"),
            "losing_streak_blocks": diag.get("losing_streak_blocks"),
            "max_open_order_blocks": diag.get("max_open_order_blocks"),
            "spread_blocks": diag.get("spread_blocks"),
            "unsafe_regime_blocks": diag.get("unsafe_regime_blocks"),
            "broker_minimum_lot_risk_budget_blocks": diag.get("broker_minimum_lot_risk_budget_blocks"),
            "regime_counts_json": json.dumps(diag.get("regime_counts", {}), ensure_ascii=False),
            "blocked_reason_counts_json": json.dumps(diag.get("blocked_reason_counts", {}), ensure_ascii=False),
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def phase_value(rows: list[dict[str, Any]], phase: str, key: str) -> Any:
    for row in rows:
        if row.get("phase") == phase:
            return row.get(key)
    return None


def write_baseline_summary(path: Path, rows: list[dict[str, Any]], monthly: list[dict[str, Any]]) -> None:
    lines = [
        "# Baseline Stability Summary",
        "",
        "Scope: `EURUSD_H1_10000` only. This is diagnostics, not optimization and not profitability proof.",
        "",
        "## Phase Stability",
        "",
        "| Phase | Net Profit | Profit Factor | Trades | Relative DD | Accepted | Rejected | Unsafe Blocks | Spread Blocks | Losing Streak Blocks | Max Open Blocks |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for phase in ("train", "validation", "out_of_sample"):
        row = next((r for r in rows if r.get("phase") == phase), {})
        lines.append(
            f"| {phase} | {row.get('net_profit')} | {row.get('profit_factor')} | {row.get('total_trades')} | "
            f"{row.get('relative_drawdown')} | {row.get('accepted_signals')} | {row.get('rejected_signals')} | "
            f"{row.get('unsafe_regime_blocks')} | {row.get('spread_blocks')} | {row.get('losing_streak_blocks')} | {row.get('max_open_order_blocks')} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "- EURUSD H1 remains `RESEARCH_MORE`, not a strong candidate.",
        "- Validation and out-of-sample are positive, but train is negative and has only 22 trades.",
        "- Low train trade count makes the train period unreliable as a proof of edge.",
        "- Rejected signal counts and losing-streak blocks show that risk gates materially affect results.",
        "",
        "## Monthly Breakdown Availability",
        "",
    ]
    if monthly:
        lines.append("Monthly closed-deal performance was extracted from the MT5 Deals table. Drawdown by month is not available from the exported report and remains blank.")
    else:
        lines.append("Monthly performance could not be extracted. Future runs should log deal close time, close reason, realized profit, balance, and equity after close.")
    active_months = len({row.get("month") or row.get("year_month") for row in monthly if row.get("closed_trades")})
    lines += [
        "",
        "## Trade Activity Warning",
        "",
        f"Trade activity is uneven across periods. Train has only 22 trades across 2 years, validation has 105 trades, and out-of-sample has 62 trades. Monthly results are concentrated in {active_months or 'limited'} reported active months. Positive OOS is not enough for forward/live readiness.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def aggregate_timeframe_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("base_case_id"))].append(row)
    output = []
    for case_id, items in sorted(grouped.items()):
        validation = next((r for r in items if r.get("phase") == "validation"), {})
        oos = next((r for r in items if r.get("phase") == "out_of_sample"), {})
        train = next((r for r in items if r.get("phase") == "train"), {})
        val_profit = to_float(validation.get("net_profit"))
        oos_profit = to_float(oos.get("net_profit"))
        val_trades = to_int(validation.get("total_trades"))
        oos_trades = to_int(oos.get("total_trades"))
        total_val_oos_trades = val_trades + oos_trades
        status = "RESEARCH_MORE"
        if val_profit is None or oos_profit is None:
            status = "INCOMPLETE"
        elif val_profit <= 0 or oos_profit <= 0:
            status = "REJECT_FOR_NOW"
        elif val_trades < 30 or oos_trades < 30:
            status = "LOW_TRADE_COUNT"
        output.append({
            "base_case_id": case_id,
            "timeframe": train.get("timeframe") or validation.get("timeframe") or oos.get("timeframe"),
            "train_net_profit": train.get("net_profit"),
            "validation_net_profit": validation.get("net_profit"),
            "out_of_sample_net_profit": oos.get("net_profit"),
            "train_trades": train.get("total_trades"),
            "validation_trades": val_trades,
            "out_of_sample_trades": oos_trades,
            "validation_profit_factor": validation.get("profit_factor"),
            "out_of_sample_profit_factor": oos.get("profit_factor"),
            "validation_oos_trades": total_val_oos_trades,
            "review_status": status,
        })
    return output


def write_timeframe_summary(path: Path, scores: list[dict[str, Any]]) -> None:
    h1 = next((s for s in scores if s.get("timeframe") == "H1"), {})
    m30 = next((s for s in scores if s.get("timeframe") == "M30"), {})
    h4 = next((s for s in scores if s.get("timeframe") == "H4"), {})
    lines = [
        "# EURUSD Timeframe Review Summary",
        "",
        "This review compares M30/H1/H4 using existing strategy logic and existing conservative settings. It is not optimization.",
        "",
        "| Case | TF | Train Profit | Validation Profit | OOS Profit | Validation Trades | OOS Trades | Status |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in scores:
        lines.append(
            f"| {row.get('base_case_id')} | {row.get('timeframe')} | {row.get('train_net_profit')} | "
            f"{row.get('validation_net_profit')} | {row.get('out_of_sample_net_profit')} | "
            f"{row.get('validation_trades')} | {row.get('out_of_sample_trades')} | {row.get('review_status')} |"
        )
    lines += [
        "",
        "## Questions",
        "",
        "### Does EURUSD H1 remain the best baseline?",
        "",
        f"Yes, for now H1 remains the baseline for further research because validation and out-of-sample are both positive while M30 and H4 fail one or more review checks. H1 is still `{h1.get('review_status')}`, not an approved or live-ready candidate.",
        "",
        "### Does M30 increase trade count without destroying risk?",
        "",
        f"No. M30 validation/OOS trades are {m30.get('validation_trades')}/{m30.get('out_of_sample_trades')}; validation is negative and has too few trades. Review status: `{m30.get('review_status')}`.",
        "",
        "### Does H4 trade too little?",
        "",
        f"Yes. H4 validation/OOS trades are {h4.get('validation_trades')}/{h4.get('out_of_sample_trades')}, with validation and out-of-sample both negative. Low-trade H4 phases should be rejected for candidate selection.",
        "",
        "### Which timeframe should be used as baseline?",
        "",
        f"Use EURUSD H1 as the next baseline for diagnostics-only research. H1 status: `{h1.get('review_status')}`.",
        "",
        "### Should low-trade phases be rejected?",
        "",
        "Yes for candidate selection. They may remain for diagnostics, but should not drive strategy changes or optimization.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-run-root", required=True)
    parser.add_argument("--timeframe-run-root")
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    baseline_root = Path(args.baseline_run_root)
    baseline_rows = collect_case_rows(baseline_root, "EURUSD_H1_10000")
    monthly = []
    for case_dir in sorted(baseline_root.iterdir()):
        if not case_dir.is_dir():
            continue
        case = load_json(case_dir / "case.json")
        if case.get("base_case_id") == "EURUSD_H1_10000":
            monthly.extend(monthly_rows(case_dir, case))

    write_csv(results_root / "baseline_stability_by_phase.csv", baseline_rows)
    write_csv(results_root / "baseline_stability_by_year_or_month.csv", monthly)
    write_baseline_summary(results_root / "baseline_stability_summary.md", baseline_rows, monthly)

    if args.timeframe_run_root:
        tf_rows = collect_case_rows(Path(args.timeframe_run_root))
        tf_scores = aggregate_timeframe_scores(tf_rows)
        write_csv(results_root / "timeframe_review_scores.csv", tf_scores)
        write_timeframe_summary(results_root / "timeframe_review_summary.md", tf_scores)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
