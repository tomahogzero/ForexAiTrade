#!/usr/bin/env python3
"""Generate research CSV and Markdown summaries from isolated run artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any


FAILED_INFRA_STATUSES = {"NO_REPORT", "PARSE_ERROR", "CONFIG_MISMATCH", "PROCESS_ERROR", "TIMEOUT", "FAILED"}


def parse_bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def collect_results(runs_root: Path) -> list[dict[str, Any]]:
    rows = []
    for case_dir in sorted(runs_root.glob("run_*/*")):
        if not case_dir.is_dir():
            continue
        case = load_json(case_dir / "case.json") or {}
        status = load_json(case_dir / "status.json") or {}
        parsed = load_json(case_dir / "parsed_result.json") or {}
        run_id = case.get("run_id") or case_dir.parent.name
        rows.append({
            "run_id": run_id,
            "case_id": case.get("case_id", case_dir.name),
            "base_case_id": case.get("base_case_id"),
            "phase": case.get("phase"),
            "symbol": case.get("actual_symbol"),
            "canonical_symbol": case.get("canonical_symbol"),
            "timeframe": case.get("timeframe") or parsed.get("timeframe"),
            "deposit": case.get("deposit"),
            "execution_status": status.get("execution_status", "UNKNOWN"),
            "message": status.get("message", ""),
            "net_profit": parsed.get("net_profit"),
            "profit_factor": parsed.get("profit_factor"),
            "expected_payoff": parsed.get("expected_payoff"),
            "max_drawdown": parsed.get("max_drawdown"),
            "relative_drawdown": parsed.get("relative_drawdown"),
            "total_trades": parsed.get("total_trades"),
            "win_rate": parsed.get("win_rate"),
            "largest_win": parsed.get("largest_win"),
            "largest_loss": parsed.get("largest_loss"),
            "consecutive_losses": parsed.get("consecutive_losses"),
            "report_period_from": parsed.get("report_period_from"),
            "report_period_to": parsed.get("report_period_to"),
            "case_dir": str(case_dir),
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({k for row in rows for k in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_scores(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def latest_successful_run_id(rows: list[dict[str, Any]]) -> str | None:
    successful = {r.get("run_id") for r in rows if r.get("execution_status") == "PASS" and r.get("run_id")}
    if successful:
        return sorted(successful)[-1]
    all_runs = {r.get("run_id") for r in rows if r.get("run_id")}
    return sorted(all_runs)[-1] if all_runs else None


def select_rows(rows: list[dict[str, Any]], run_id: str | None, include_failed_debug_runs: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str | None]:
    selected_run_id = run_id or latest_successful_run_id(rows)
    main_rows = [r for r in rows if r.get("run_id") == selected_run_id]
    debug_rows = [r for r in rows if r.get("run_id") != selected_run_id and r.get("execution_status") in FAILED_INFRA_STATUSES]
    if include_failed_debug_runs:
        main_rows = rows
        debug_rows = []
    return main_rows, debug_rows, selected_run_id


def filter_scores(scores: list[dict[str, str]], run_id: str | None, include_failed_debug_runs: bool) -> list[dict[str, str]]:
    if include_failed_debug_runs or not run_id:
        return scores
    return [s for s in scores if s.get("run_id") == run_id]


def fmt(value: Any) -> str:
    if value is None or value == "":
        return ""
    return str(value).replace("|", "/")


def generate_markdown(
    main_rows: list[dict[str, Any]],
    debug_rows: list[dict[str, Any]],
    scores: list[dict[str, str]],
    selected_run_id: str | None,
) -> str:
    lines = []
    lines.append("# ForexAiTrade Research Summary")
    lines.append("")
    lines.append("This summary separates MT5 execution status from strategy performance. Results are not proof of future profitability.")
    lines.append("")
    lines.append(f"Selected RunId: `{selected_run_id or 'none'}`")
    lines.append("")

    case_level: dict[str, dict[str, str]] = {}
    for s in scores:
        key = s.get("base_case_id") or s.get("case_id") or ""
        if key and key not in case_level:
            case_level[key] = s

    lines.append("## Case-Level Summary")
    lines.append("")
    if case_level:
        lines.append("| Case | Classification | Failed Gates |")
        lines.append("|---|---|---|")
        for case_id, row in sorted(case_level.items()):
            lines.append(f"| {fmt(case_id)} | {fmt(row.get('case_level_classification'))} | {fmt(row.get('case_failed_gates'))} |")
    else:
        lines.append("No case-level rows available.")
    lines.append("")

    lines.append("## Phase Results")
    lines.append("")
    if main_rows:
        lines.append("| Case | Phase | Symbol | TF | Status | Net Profit | PF | DD | Trades |")
        lines.append("|---|---|---|---|---|---:|---:|---:|---:|")
        for r in main_rows:
            lines.append(
                f"| {fmt(r.get('base_case_id') or r.get('case_id'))} | {fmt(r.get('phase'))} | "
                f"{fmt(r.get('symbol'))} | {fmt(r.get('timeframe'))} | {fmt(r.get('execution_status'))} | "
                f"{fmt(r.get('net_profit'))} | {fmt(r.get('profit_factor'))} | "
                f"{fmt(r.get('relative_drawdown') if r.get('relative_drawdown') is not None else r.get('max_drawdown'))} | "
                f"{fmt(r.get('total_trades'))} |"
            )
    else:
        lines.append("No rows found for the selected run.")
    lines.append("")

    lines.append("## Phase Classifications")
    lines.append("")
    if scores:
        lines.append("| Case | Phase | Phase Classification | Risk-Adjusted | Annualized | Calmar | Score | Failed Gates |")
        lines.append("|---|---|---|---|---:|---:|---:|---|")
        for s in scores:
            lines.append(
                f"| {fmt(s.get('base_case_id') or s.get('case_id'))} | {fmt(s.get('phase'))} | "
                f"{fmt(s.get('phase_classification') or s.get('research_classification'))} | "
                f"{fmt(s.get('risk_adjusted_classification'))} | "
                f"{fmt(s.get('annualized_return_percent'))} | {fmt(s.get('calmar_ratio'))} | "
                f"{fmt(s.get('score'))} | {fmt(s.get('failed_gates'))} |"
            )
    else:
        lines.append("No score rows available.")
    lines.append("")

    lines.append("## Failed Gates")
    lines.append("")
    failed_rows = [s for s in scores if s.get("failed_gates") or s.get("case_failed_gates")]
    if failed_rows:
        lines.append("| Case | Phase | Phase Gates | Case Gates |")
        lines.append("|---|---|---|---|")
        for s in failed_rows:
            lines.append(
                f"| {fmt(s.get('base_case_id') or s.get('case_id'))} | {fmt(s.get('phase'))} | "
                f"{fmt(s.get('failed_gates'))} | {fmt(s.get('case_failed_gates'))} |"
            )
    else:
        lines.append("No failed gates recorded for the selected run.")
    lines.append("")

    provisional = [row for row in case_level.values() if row.get("case_level_classification") == "PROVISIONAL_RESEARCH_CANDIDATE"]
    lines.append("## Provisional Candidate Ranking")
    lines.append("")
    if provisional:
        lines.append("| Case | OOS Score |")
        lines.append("|---|---:|")
        for s in sorted(provisional, key=lambda x: float(x.get("score") or 0), reverse=True):
            lines.append(f"| {fmt(s.get('base_case_id') or s.get('case_id'))} | {fmt(s.get('score'))} |")
    else:
        lines.append("No provisional research candidates yet. No final candidate label is used in this checkpoint.")
    lines.append("")

    lines.append("## Warnings")
    lines.append("")
    lines.append("| Warning | Detail |")
    lines.append("|---|---|")
    lines.append("| Not Profit Proof | Backtest results do not prove future profitability. |")
    lines.append("| No Optimization | This run uses controlled existing parameters only. |")
    lines.append("| Annualization Caution | Annualized return and CAGR are informational when the period is short or trade count is low. |")
    lines.append("| No Live Readiness | Demo forward testing has not started and should not start from this checkpoint alone. |")
    for case_id, row in sorted(case_level.items()):
        if row.get("case_level_classification") == "TRAIN_FAILED_VALIDATION_OOS_PASS":
            lines.append(f"| Train Warning | {fmt(case_id)} has validation/OOS pass but train is negative or insufficient. |")
    lines.append("")

    lines.append("## Debug / Infrastructure Failed Runs")
    lines.append("")
    if debug_rows:
        lines.append("| RunId | Case | Status | Message |")
        lines.append("|---|---|---|---|")
        for r in debug_rows:
            lines.append(f"| {fmt(r.get('run_id'))} | {fmt(r.get('case_id'))} | {fmt(r.get('execution_status'))} | {fmt(r.get('message'))} |")
    else:
        lines.append("No debug infrastructure failures outside the selected run.")
    lines.append("")

    lines.append("## Explicit Warning")
    lines.append("")
    lines.append("Backtest and smoke-test results are research artifacts only. They do not prove future profitability and must be followed by validation, out-of-sample checks, and demo forward testing.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--run-id")
    parser.add_argument("--latest-run", action="store_true")
    parser.add_argument("--include-failed-debug-runs", default="false")
    parser.add_argument("--summary-output")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    include_failed_debug_runs = parse_bool(args.include_failed_debug_runs)
    rows = collect_results(runs_root)
    all_results = results_root / "all_results.csv"
    all_scores = results_root / "all_scores.csv"
    summary = Path(args.summary_output) if args.summary_output else results_root / "research_summary.md"

    write_csv(all_results, rows)

    subprocess.run([
        "python",
        str(Path(__file__).with_name("research_score.py")),
        "--runs-root",
        str(runs_root),
        "--output",
        str(all_scores),
    ], check=False)

    scores = read_scores(all_scores)
    selected_run = None if args.latest_run else args.run_id
    main_rows, debug_rows, selected_run_id = select_rows(rows, selected_run, include_failed_debug_runs)
    selected_scores = filter_scores(scores, selected_run_id, include_failed_debug_runs)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(generate_markdown(main_rows, debug_rows, selected_scores, selected_run_id), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
