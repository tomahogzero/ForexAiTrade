#!/usr/bin/env python3
"""Parse ForexAiTrade exit telemetry CSV files into case and aggregate summaries."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


CLASSIFICATIONS = [
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


def to_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def average(values: list[float]) -> float | None:
    return round(mean(values), 6) if values else None


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
    run_id = None if args.latest_run else args.run_id
    selected = run_id or latest_successful_run_id(runs_root)
    if not selected:
        raise SystemExit(f"No run directories found under {runs_root}")
    run_root = runs_root / selected
    if not run_root.exists():
        raise SystemExit(f"RunId not found: {selected}")
    return run_root


def summarize_case(case_dir: Path) -> dict[str, Any]:
    loaded_case = load_json(case_dir / "case.json")
    case = loaded_case if isinstance(loaded_case, dict) else {}
    telemetry_path = case_dir / "exit_telemetry.csv"
    trade_ledger_path = case_dir / "trade_ledger.csv"
    rows = read_csv(telemetry_path)
    close_rows = [row for row in rows if row.get("event") == "CLOSE"]
    modify_rows = [row for row in rows if row.get("event") == "MODIFY"]
    open_rows = [row for row in rows if row.get("event") == "OPEN"]
    ledger_rows = read_csv(trade_ledger_path)

    by_class: dict[str, dict[str, Any]] = {}
    for classification in CLASSIFICATIONS:
        items = [row for row in close_rows if (row.get("exit_classification") or "UNKNOWN") == classification]
        profits = [v for v in (to_float(row.get("profit")) for row in items) if v is not None]
        r_values = [v for v in (to_float(row.get("realized_r")) for row in items) if v is not None]
        durations = [v for v in (to_float(row.get("duration_seconds")) for row in items) if v is not None]
        by_class[classification] = {
            "count": len(items),
            "net_profit": round(sum(profits), 2),
            "average_r": average(r_values),
            "average_duration_seconds": average(durations),
        }

    warnings: list[str] = []
    if not telemetry_path.exists():
        warnings.append("exit_telemetry.csv is missing")
    if ledger_rows and len(close_rows) != len(ledger_rows):
        warnings.append(f"telemetry close count {len(close_rows)} does not match trade ledger count {len(ledger_rows)}")
    if not close_rows:
        warnings.append("no CLOSE telemetry rows found")

    summary = {
        "run_id": case.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or case_dir.name,
        "base_case_id": case.get("base_case_id"),
        "phase": case.get("phase"),
        "actual_symbol": case.get("actual_symbol"),
        "canonical_symbol": case.get("canonical_symbol"),
        "timeframe": case.get("timeframe"),
        "telemetry_rows": len(rows),
        "open_events": len(open_rows),
        "modify_events": len(modify_rows),
        "close_events": len(close_rows),
        "trade_ledger_rows": len(ledger_rows),
        "by_exit_classification": by_class,
        "breakeven_exits": by_class["BREAKEVEN_SL"]["count"],
        "trailing_profit_exits": by_class["TRAILING_SL_PROFIT"]["count"],
        "initial_sl_loss_exits": by_class["INITIAL_SL_LOSS"]["count"],
        "tp_hit_exits": by_class["TP_HIT"]["count"],
        "unknown_exits": by_class["UNKNOWN"]["count"],
        "warnings": warnings,
    }
    return summary


def write_case_outputs(case_dir: Path, summary: dict[str, Any]) -> None:
    (case_dir / "exit_telemetry_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        f"# Exit Telemetry Summary: {summary.get('case_id')}",
        "",
        f"- RunId: `{summary.get('run_id')}`",
        f"- Phase: `{summary.get('phase')}`",
        f"- Close events: `{summary.get('close_events')}`",
        f"- Modify events: `{summary.get('modify_events')}`",
        "",
        "| Classification | Count | Net Profit | Avg R | Avg Duration Seconds |",
        "|---|---:|---:|---:|---:|",
    ]
    for classification, row in summary["by_exit_classification"].items():
        lines.append(
            f"| {classification} | {row['count']} | {row['net_profit']} | {row['average_r']} | {row['average_duration_seconds']} |"
        )
    lines += ["", "## Warnings", ""]
    if summary["warnings"]:
        lines.extend(f"- {warning}" for warning in summary["warnings"])
    else:
        lines.append("- None")
    (case_dir / "exit_telemetry_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def aggregate(summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for summary in summaries:
        for classification, row in summary["by_exit_classification"].items():
            output.append({
                "run_id": summary.get("run_id"),
                "case_id": summary.get("case_id"),
                "base_case_id": summary.get("base_case_id"),
                "phase": summary.get("phase"),
                "symbol": summary.get("actual_symbol"),
                "timeframe": summary.get("timeframe"),
                "exit_classification": classification,
                **row,
                "close_events": summary.get("close_events"),
                "modify_events": summary.get("modify_events"),
                "warnings": "; ".join(summary.get("warnings") or []),
            })
    return output


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_aggregate_summary(path: Path, run_id: str, summaries: list[dict[str, Any]]) -> None:
    combined: dict[str, Counter[str]] = defaultdict(Counter)
    warning_lines: list[str] = []
    for summary in summaries:
        key = str(summary.get("base_case_id"))
        for classification, row in summary["by_exit_classification"].items():
            combined[key][classification] += int(row["count"])
        for warning in summary.get("warnings") or []:
            warning_lines.append(f"{summary.get('case_id')}: {warning}")

    lines = [
        "# Exit Telemetry Aggregate Summary",
        "",
        f"Selected RunId: `{run_id}`",
        "",
        "Telemetry is diagnostic-only. It does not prove profitability and does not change strategy behavior.",
        "",
        "| Case | Initial SL Loss | Breakeven SL | Trailing SL Profit | TP Hit | Other Close | Unknown |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for case_id, counter in sorted(combined.items()):
        lines.append(
            f"| {case_id} | {counter['INITIAL_SL_LOSS']} | {counter['BREAKEVEN_SL']} | "
            f"{counter['TRAILING_SL_PROFIT']} | {counter['TP_HIT']} | {counter['OTHER_CLOSE']} | {counter['UNKNOWN']} |"
        )
    lines += ["", "## Warnings", ""]
    if warning_lines:
        lines.extend(f"- {warning}" for warning in warning_lines)
    else:
        lines.append("- None")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    summaries: list[dict[str, Any]] = []
    for case_dir in sorted(run_root.iterdir()):
        if not case_dir.is_dir() or not (case_dir / "case.json").exists():
            continue
        summary = summarize_case(case_dir)
        summaries.append(summary)
        write_case_outputs(case_dir, summary)

    rows = aggregate(summaries)
    write_csv(results_root / "exit_telemetry_all_cases.csv", rows)
    write_aggregate_summary(results_root / "exit_telemetry_summary.md", run_root.name, summaries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
