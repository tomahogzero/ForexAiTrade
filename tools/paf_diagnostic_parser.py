#!/usr/bin/env python3
"""Parse Price Action/Fibo diagnostic-only logs.

The parser treats ea_mirror.log as the authoritative source when available.
tester_log_excerpt.log is counted separately so repeated terminal excerpts do
not inflate the main diagnostic totals.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any

try:
    from research_report_parser import parse_report
except Exception:  # pragma: no cover - parser can still operate from logs only.
    parse_report = None  # type: ignore[assignment]


DIAG_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) PriceActionFibo diagnostic: (?P<body>.*)$")
NO_TRADE_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) No trade: (?P<body>.*)$")
KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z0-9_]+)=(?P<value>.*?)(?=\s+[A-Za-z0-9_]+=|$)")

FORBIDDEN_MARKERS = (
    "OrderSend",
    "Buy(",
    "Sell(",
    "BuyLimit",
    "SellLimit",
    "BuyStop",
    "SellStop",
    "PositionModify",
    "SIGNAL_BUY",
    "SIGNAL_SELL",
)

BASELINE_FALLBACK_MARKERS = (
    "TrendStrategy",
    "BreakoutStrategy",
    "MeanReversion",
    "Selected strategy",
)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def parse_key_values(body: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for match in KEY_VALUE_RE.finditer(body):
        key = match.group("key").strip()
        value = match.group("value").strip()
        values[key] = value
    return values


def to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def summarize_numbers(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "min": None, "median": None, "average": None, "max": None}
    return {
        "count": len(values),
        "min": min(values),
        "median": median(values),
        "average": mean(values),
        "max": max(values),
    }


def count_marker_hits(text: str, markers: tuple[str, ...]) -> dict[str, int]:
    return {marker: text.count(marker) for marker in markers if text.count(marker) > 0}


def load_report_fallback(case_dir: Path) -> dict[str, Any]:
    if parse_report is None:
        return {}
    for name in ("mt5_report.htm", "mt5_report.html", "mt5_report.xml"):
        path = case_dir / name
        if path.exists():
            try:
                return parse_report(path)
            except Exception:
                return {}
    return {}


def extract_diagnostics(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    diagnostics: list[dict[str, Any]] = []
    no_trades: list[dict[str, Any]] = []
    for line in text.splitlines():
        diag_match = DIAG_RE.match(line.strip())
        if diag_match:
            fields = parse_key_values(diag_match.group("body"))
            diagnostics.append({"time": diag_match.group("time"), **fields})
            continue

        no_trade_match = NO_TRADE_RE.match(line.strip())
        if no_trade_match:
            fields = parse_key_values(no_trade_match.group("body"))
            no_trades.append({"time": no_trade_match.group("time"), **fields})
    return diagnostics, no_trades


def counter_dict(items: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(item) for item in items if item not in (None, "")).items(), key=lambda x: (-x[1], x[0])))


def parse_case_dir(case_dir: Path) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    status = load_json(case_dir / "status.json")
    report = load_json(case_dir / "parsed_result.json")
    if not report:
        report = load_report_fallback(case_dir)
    ea_text = read_text(case_dir / "ea_mirror.log")
    tester_text = read_text(case_dir / "tester_log_excerpt.log")

    source_text = ea_text if ea_text else tester_text
    source_name = "ea_mirror.log" if ea_text else ("tester_log_excerpt.log" if tester_text else "")
    authoritative = bool(ea_text)
    diagnostics, no_trades = extract_diagnostics(source_text)
    tester_diagnostics, tester_no_trades = extract_diagnostics(tester_text)
    ea_diagnostics, ea_no_trades = extract_diagnostics(ea_text)

    spreads = [value for value in (to_float(row.get("spread")) for row in no_trades) if value is not None]
    forbidden_hits = count_marker_hits(source_text, FORBIDDEN_MARKERS)
    fallback_hits = count_marker_hits(source_text, BASELINE_FALLBACK_MARKERS)

    summary: dict[str, Any] = {
        "run_id": case.get("run_id") or status.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or status.get("case_id") or case_dir.name,
        "base_case_id": case.get("base_case_id"),
        "phase": case.get("phase"),
        "actual_symbol": case.get("actual_symbol") or status.get("symbol") or report.get("symbol"),
        "canonical_symbol": case.get("canonical_symbol"),
        "timeframe": case.get("timeframe") or report.get("timeframe"),
        "period_from": (case.get("period") or {}).get("from") if isinstance(case.get("period"), dict) else report.get("report_period_from"),
        "period_to": (case.get("period") or {}).get("to") if isinstance(case.get("period"), dict) else report.get("report_period_to"),
        "execution_status": status.get("execution_status"),
        "report_artifact_status": status.get("report_artifact_status"),
        "total_trades": report.get("total_trades"),
        "total_deals": report.get("total_deals"),
        "authoritative_source": source_name,
        "authoritative_source_is_ea_mirror": authoritative,
        "diagnostic_count": len(diagnostics),
        "no_trade_count": len(no_trades),
        "ea_mirror_diagnostic_count": len(ea_diagnostics),
        "ea_mirror_no_trade_count": len(ea_no_trades),
        "tester_excerpt_diagnostic_count": len(tester_diagnostics),
        "tester_excerpt_no_trade_count": len(tester_no_trades),
        "classification_counts": counter_dict([row.get("classification") for row in diagnostics]),
        "regime_counts": counter_dict([row.get("regime") for row in diagnostics]),
        "no_trade_reason_counts": counter_dict([row.get("reason") for row in no_trades]),
        "spread_stats": summarize_numbers(spreads),
        "forbidden_action_marker_count": sum(forbidden_hits.values()),
        "forbidden_action_markers": forbidden_hits,
        "baseline_fallback_marker_count": sum(fallback_hits.values()),
        "baseline_fallback_markers": fallback_hits,
        "no_trade_confirmation": "PASS_FROM_REPORT_AND_EA_LOGS"
        if report.get("total_trades") == 0 and sum(forbidden_hits.values()) == 0 and len(diagnostics) > 0
        else "NOT_PROVEN",
        "baseline_fallback_confirmation": "PASS_FROM_EA_LOGS" if authoritative and sum(fallback_hits.values()) == 0 else "NOT_PROVEN",
        "duplicate_count_warning": "tester excerpt counted separately; main totals use ea_mirror.log when available"
        if authoritative and len(tester_diagnostics) > 0
        else "",
    }
    return summary


def write_case_outputs(case_dir: Path, summary: dict[str, Any]) -> None:
    (case_dir / "paf_diagnostics.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        f"# PAF Diagnostics: {summary.get('case_id')}",
        "",
        f"RunId: `{summary.get('run_id')}`",
        f"Authoritative source: `{summary.get('authoritative_source')}`",
        f"Diagnostic count: `{summary.get('diagnostic_count')}`",
        f"No-trade count: `{summary.get('no_trade_count')}`",
        f"No-trade confirmation: `{summary.get('no_trade_confirmation')}`",
        f"Baseline fallback confirmation: `{summary.get('baseline_fallback_confirmation')}`",
        "",
        "## Classification Counts",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for name, count in summary.get("classification_counts", {}).items():
        lines.append(f"| `{name}` | {count} |")
    lines += [
        "",
        "## Regime Counts",
        "",
        "| Regime | Count |",
        "|---|---:|",
    ]
    for name, count in summary.get("regime_counts", {}).items():
        lines.append(f"| `{name}` | {count} |")
    lines += [
        "",
        "## No-Trade Reason Counts",
        "",
        "| Reason | Count |",
        "|---|---:|",
    ]
    for name, count in summary.get("no_trade_reason_counts", {}).items():
        lines.append(f"| `{name}` | {count} |")
    lines += [
        "",
        "This is diagnostic-only evidence. It is not profitability proof and does not approve demo/live trading.",
    ]
    (case_dir / "paf_diagnostics_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def find_run_root(args: argparse.Namespace) -> Path | None:
    roots = [Path(args.runs_root), Path(args.artifacts_root)]
    if args.run_id:
        for root in roots:
            candidate = root / args.run_id
            if candidate.exists():
                return candidate
        return None
    if args.latest_run:
        candidates = []
        for root in roots:
            if root.exists():
                candidates.extend([path for path in root.iterdir() if path.is_dir() and path.name.startswith("run_")])
        return max(candidates, key=lambda p: p.stat().st_mtime) if candidates else None
    return None


def case_dirs_from_args(args: argparse.Namespace) -> list[Path]:
    if args.case_dir:
        return [Path(args.case_dir)]
    run_root = find_run_root(args)
    if not run_root:
        return []
    return [path for path in sorted(run_root.iterdir()) if path.is_dir()]


def flatten(summary: dict[str, Any]) -> dict[str, Any]:
    spread = summary.get("spread_stats", {})
    return {
        "run_id": summary.get("run_id"),
        "case_id": summary.get("case_id"),
        "base_case_id": summary.get("base_case_id"),
        "phase": summary.get("phase"),
        "actual_symbol": summary.get("actual_symbol"),
        "canonical_symbol": summary.get("canonical_symbol"),
        "timeframe": summary.get("timeframe"),
        "period_from": summary.get("period_from"),
        "period_to": summary.get("period_to"),
        "execution_status": summary.get("execution_status"),
        "total_trades": summary.get("total_trades"),
        "authoritative_source": summary.get("authoritative_source"),
        "diagnostic_count": summary.get("diagnostic_count"),
        "no_trade_count": summary.get("no_trade_count"),
        "ea_mirror_diagnostic_count": summary.get("ea_mirror_diagnostic_count"),
        "tester_excerpt_diagnostic_count": summary.get("tester_excerpt_diagnostic_count"),
        "spread_min": spread.get("min"),
        "spread_median": spread.get("median"),
        "spread_average": spread.get("average"),
        "spread_max": spread.get("max"),
        "forbidden_action_marker_count": summary.get("forbidden_action_marker_count"),
        "baseline_fallback_marker_count": summary.get("baseline_fallback_marker_count"),
        "no_trade_confirmation": summary.get("no_trade_confirmation"),
        "baseline_fallback_confirmation": summary.get("baseline_fallback_confirmation"),
        "classification_counts": json.dumps(summary.get("classification_counts", {}), ensure_ascii=False),
        "regime_counts": json.dumps(summary.get("regime_counts", {}), ensure_ascii=False),
    }


def write_aggregate_outputs(results_root: Path, summaries: list[dict[str, Any]]) -> None:
    results_root.mkdir(parents=True, exist_ok=True)
    csv_path = results_root / "paf_diagnostics_all_cases.csv"
    rows = [flatten(summary) for summary in summaries]
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    lines = [
        "# Price Action/Fibo Diagnostic Summary",
        "",
        "Main totals use `ea_mirror.log` when available. Tester excerpts are counted separately to avoid duplicate diagnostics.",
        "",
        "| Case | Source | Diagnostics | No-trade | Trades | Forbidden markers | Baseline fallback |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for summary in summaries:
        lines.append(
            f"| `{summary.get('case_id')}` | `{summary.get('authoritative_source')}` | "
            f"{summary.get('diagnostic_count')} | {summary.get('no_trade_count')} | "
            f"{summary.get('total_trades')} | {summary.get('forbidden_action_marker_count')} | "
            f"{summary.get('baseline_fallback_marker_count')} |"
        )
    lines += [
        "",
        "Diagnostic classifications are observation labels only. They are not entry signals and do not approve trading.",
    ]
    (results_root / "paf_diagnostics_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse ForexAiTrade Price Action/Fibo diagnostic logs.")
    parser.add_argument("--case-dir", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--latest-run", action="store_true")
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--artifacts-root", default="mt5_artifacts")
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    case_dirs = case_dirs_from_args(args)
    if not case_dirs:
        parser.error("No case directories found. Provide --case-dir, --run-id, or --latest-run.")

    summaries: list[dict[str, Any]] = []
    for case_dir in case_dirs:
        if not (case_dir / "ea_mirror.log").exists() and not (case_dir / "tester_log_excerpt.log").exists():
            continue
        summary = parse_case_dir(case_dir)
        write_case_outputs(case_dir, summary)
        summaries.append(summary)

    write_aggregate_outputs(Path(args.results_root), summaries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
