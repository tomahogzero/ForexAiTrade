#!/usr/bin/env python3
"""Prototype no-order shadow outcome labeler for Price Action/Fibo diagnostics.

This tool intentionally does not infer trade direction or profitability. It reads
existing diagnostic-only artifacts, labels what can be measured, and reports
missing data limitations before any future order implementation is considered.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


DIAG_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) PriceActionFibo diagnostic: (?P<body>.*)$")
NO_TRADE_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) No trade: (?P<body>.*)$")
KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z0-9_]+)=(?P<value>.*?)(?=\s+[A-Za-z0-9_]+=|$)")

POSSIBLE_SETUP_LABELS = {
    "POSSIBLE_FIBO_PULLBACK",
    "POSSIBLE_ZONE_REJECTION",
    "POSSIBLE_BREAK_RETEST",
}

OUTCOME_LABELS = {
    "TP_FIRST",
    "SL_FIRST",
    "BOTH_SAME_BAR",
    "NO_RESOLUTION",
    "DIRECTION_MISSING",
    "DATA_MISSING",
    "SPREAD_FILTERED",
    "REGIME_FILTERED",
}

SPREAD_BUCKET_THRESHOLDS = {
    "LOW_SPREAD_MAX": 20.0,
    "NORMAL_SPREAD_MAX": 50.0,
    "HIGH_SPREAD_MAX": 100.0,
}


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
        values[match.group("key").strip()] = match.group("value").strip()
    return values


def to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def spread_bucket(spread: float | None) -> str:
    if spread is None:
        return "SPREAD_UNKNOWN"
    if spread <= SPREAD_BUCKET_THRESHOLDS["LOW_SPREAD_MAX"]:
        return "LOW_SPREAD"
    if spread <= SPREAD_BUCKET_THRESHOLDS["NORMAL_SPREAD_MAX"]:
        return "NORMAL_SPREAD"
    if spread <= SPREAD_BUCKET_THRESHOLDS["HIGH_SPREAD_MAX"]:
        return "HIGH_SPREAD"
    return "EXTREME_SPREAD"


def session_bucket(server_time: str) -> str:
    """Bucket by broker/server hour only; this is not Thai local time."""
    try:
        hour = int(server_time[11:13])
    except Exception:
        return "UNKNOWN"
    if 0 <= hour <= 7:
        return "ASIA"
    if 8 <= hour <= 12:
        return "LONDON"
    if 13 <= hour <= 16:
        return "OVERLAP"
    if 17 <= hour <= 21:
        return "NEW_YORK"
    return "OTHER"


def extract_diagnostic_events(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw_line in text.splitlines():
        match = DIAG_RE.match(raw_line.strip())
        if not match:
            continue
        fields = parse_key_values(match.group("body"))
        events.append({"time": match.group("time"), **fields})
    return events


def extract_no_trade_spreads(text: str) -> dict[str, float]:
    spreads: dict[str, float] = {}
    for raw_line in text.splitlines():
        match = NO_TRADE_RE.match(raw_line.strip())
        if not match:
            continue
        fields = parse_key_values(match.group("body"))
        spread = to_float(fields.get("spread"))
        if spread is not None:
            spreads[match.group("time")] = spread
    return spreads


def find_run_root(args: argparse.Namespace) -> Path:
    roots = [Path(args.runs_root), Path(args.artifacts_root)]
    if args.run_id:
        for root in roots:
            candidate = root / args.run_id
            if candidate.exists():
                return candidate
        raise SystemExit(f"RunId not found under configured roots: {args.run_id}")

    if args.latest_run:
        candidates: list[Path] = []
        for root in roots:
            if root.exists():
                candidates.extend(path for path in root.iterdir() if path.is_dir() and path.name.startswith("run_"))
        if candidates:
            return max(candidates, key=lambda path: path.stat().st_mtime)
        raise SystemExit("No run_* folders found for --latest-run")

    raise SystemExit("Provide --run-id or --latest-run")


def infer_case_metadata(case_dir: Path) -> dict[str, Any]:
    case = load_json(case_dir / "case.json")
    status = load_json(case_dir / "status.json")
    diagnostics = load_json(case_dir / "paf_diagnostics.json")
    return {
        "run_id": case.get("run_id") or status.get("run_id") or diagnostics.get("run_id") or case_dir.parent.name,
        "case_id": case.get("case_id") or status.get("case_id") or diagnostics.get("case_id") or case_dir.name,
        "base_case_id": case.get("base_case_id") or diagnostics.get("base_case_id"),
        "phase": case.get("phase") or diagnostics.get("phase"),
        "actual_symbol": case.get("actual_symbol") or diagnostics.get("actual_symbol"),
        "canonical_symbol": case.get("canonical_symbol") or diagnostics.get("canonical_symbol"),
        "timeframe": case.get("timeframe") or diagnostics.get("timeframe"),
        "period_from": (case.get("period") or {}).get("from") if isinstance(case.get("period"), dict) else diagnostics.get("period_from"),
        "period_to": (case.get("period") or {}).get("to") if isinstance(case.get("period"), dict) else diagnostics.get("period_to"),
        "execution_status": status.get("execution_status") or diagnostics.get("execution_status"),
        "report_artifact_status": status.get("report_artifact_status") or diagnostics.get("report_artifact_status"),
        "total_trades": diagnostics.get("total_trades"),
    }


def label_shadow_event(event: dict[str, Any]) -> tuple[str, str]:
    classification = str(event.get("classification") or "")
    if classification not in POSSIBLE_SETUP_LABELS:
        return "REGIME_FILTERED", "not a possible setup classification"

    direction = direction_context(event)
    if not direction:
        return "DIRECTION_MISSING", "diagnostic log has no direction field"
    if direction == "DIRECTION_UNKNOWN":
        return "DIRECTION_MISSING", "diagnostic log direction context is unknown"

    entry_price = event.get("entry_reference_price") or event.get("close_price") or event.get("close")
    if to_float(entry_price) is None:
        return "DATA_MISSING", "entry reference price is missing"

    return "DATA_MISSING", "OHLC/tick lookahead data is not available in the current artifact"


def direction_context(event: dict[str, Any]) -> str:
    return str(event.get("direction_context") or event.get("direction") or event.get("dir") or "").strip()


def parse_case(case_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metadata = infer_case_metadata(case_dir)
    ea_text = read_text(case_dir / "ea_mirror.log")
    tester_text = read_text(case_dir / "tester_log_excerpt.log")
    source_text = ea_text if ea_text else tester_text
    source_file = "ea_mirror.log" if ea_text else ("tester_log_excerpt.log" if tester_text else "")
    diagnostic_events = extract_diagnostic_events(source_text)
    spread_by_time = extract_no_trade_spreads(source_text)

    rows: list[dict[str, Any]] = []
    skipped_no_setup = 0
    skipped_other = 0
    for event in diagnostic_events:
        classification = str(event.get("classification") or "")
        if classification == "NO_SETUP":
            skipped_no_setup += 1
            continue
        if classification not in POSSIBLE_SETUP_LABELS:
            skipped_other += 1
            continue

        spread = to_float(event.get("spread"))
        if spread is None:
            spread = spread_by_time.get(str(event.get("time") or ""))
        outcome, limitation = label_shadow_event(event)
        if outcome not in OUTCOME_LABELS:
            outcome = "DATA_MISSING"

        row = {
            **metadata,
            "event_time": event.get("time"),
            "classification": classification,
            "regime": event.get("regime"),
            "spread": spread,
            "spread_bucket": spread_bucket(spread),
            "session_bucket": session_bucket(str(event.get("time") or "")),
            "direction": direction_context(event),
            "direction_reason": event.get("direction_reason") or "",
            "entry_reference_price": event.get("entry_reference_price") or event.get("close_price") or event.get("close") or "",
            "outcome_label": outcome,
            "limitation": limitation,
            "source_file": source_file,
        }
        rows.append(row)

    summary = {
        **metadata,
        "case_dir": str(case_dir),
        "authoritative_source": source_file,
        "diagnostic_event_count": len(diagnostic_events),
        "possible_setup_event_count": len(rows),
        "skipped_no_setup_count": skipped_no_setup,
        "skipped_other_classification_count": skipped_other,
        "outcome_counts": counter_dict(row["outcome_label"] for row in rows),
        "classification_counts": counter_dict(row["classification"] for row in rows),
        "regime_counts": counter_dict(row["regime"] for row in rows),
        "spread_bucket_counts": counter_dict(row["spread_bucket"] for row in rows),
        "session_bucket_counts": counter_dict(row["session_bucket"] for row in rows),
        "limitations": sorted(set(row["limitation"] for row in rows)),
        "shadow_outcome_readiness": "BLOCKED_BY_MISSING_DIRECTION" if rows else "NO_ELIGIBLE_SETUP_EVENTS",
    }
    return rows, summary


def counter_dict(items: Any) -> dict[str, int]:
    return dict(sorted(Counter(str(item) for item in items if item not in (None, "")).items(), key=lambda item: (-item[1], item[0])))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_id",
        "case_id",
        "base_case_id",
        "phase",
        "actual_symbol",
        "canonical_symbol",
        "timeframe",
        "period_from",
        "period_to",
        "execution_status",
        "report_artifact_status",
        "total_trades",
        "event_time",
        "classification",
        "regime",
        "spread",
        "spread_bucket",
        "session_bucket",
        "direction",
        "direction_reason",
        "entry_reference_price",
        "outcome_label",
        "limitation",
        "source_file",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def markdown_table(counter: dict[str, int], label: str) -> list[str]:
    lines = [f"### {label}", "", "| Value | Count |", "|---|---:|"]
    if not counter:
        lines.append("| n/a | 0 |")
    else:
        for key, value in counter.items():
            lines.append(f"| `{key}` | {value} |")
    lines.append("")
    return lines


def write_case_outputs(case_dir: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    write_csv(case_dir / "paf_shadow_outcomes.csv", rows)
    (case_dir / "paf_shadow_outcome_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# PAF Shadow Outcome Prototype: {summary.get('case_id')}",
        "",
        f"RunId: `{summary.get('run_id')}`",
        f"Source: `{summary.get('authoritative_source')}`",
        f"Diagnostic events: `{summary.get('diagnostic_event_count')}`",
        f"Possible setup events: `{summary.get('possible_setup_event_count')}`",
        f"Skipped NO_SETUP events: `{summary.get('skipped_no_setup_count')}`",
        f"Readiness: `{summary.get('shadow_outcome_readiness')}`",
        "",
        "This prototype does not open or simulate orders. It only reports whether current diagnostics contain enough data for future no-order shadow outcome labeling.",
        "",
    ]
    lines += markdown_table(summary.get("outcome_counts", {}), "Outcome Labels")
    lines += markdown_table(summary.get("classification_counts", {}), "Possible Setup Classifications")
    lines += markdown_table(summary.get("spread_bucket_counts", {}), "Spread Buckets")
    lines += markdown_table(summary.get("session_bucket_counts", {}), "Server-Time Session Buckets")
    lines += [
        "## Limitations",
        "",
    ]
    for limitation in summary.get("limitations", []):
        lines.append(f"- {limitation}")
    if not summary.get("limitations"):
        lines.append("- No limitations detected by the prototype.")
    lines += [
        "",
        "This is not profitability evidence and does not approve market orders, pending orders, demo/live trading, optimization, or risk increases.",
    ]
    (case_dir / "paf_shadow_outcome_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_aggregate_outputs(results_root: Path, run_id: str, rows: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> None:
    results_root.mkdir(parents=True, exist_ok=True)
    write_csv(results_root / "paf_shadow_outcomes_all_cases.csv", rows)
    (results_root / "paf_shadow_outcome_summary.json").write_text(
        json.dumps({"run_id": run_id, "cases": summaries}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    outcome_counts = counter_dict(row["outcome_label"] for row in rows)
    classification_counts = counter_dict(row["classification"] for row in rows)
    spread_counts = counter_dict(row["spread_bucket"] for row in rows)
    session_counts = counter_dict(row["session_bucket"] for row in rows)

    lines = [
        "# PAF Shadow Outcome Prototype Summary",
        "",
        f"RunId: `{run_id}`",
        "",
        "Checkpoint AT reads existing AQ no-trade diagnostics only. It does not run MT5, does not send orders, and does not optimize parameters.",
        "",
        "## Case Summary",
        "",
        "| Case | Diagnostics | Possible setups | NO_SETUP skipped | Readiness |",
        "|---|---:|---:|---:|---|",
    ]
    for summary in summaries:
        lines.append(
            "| `{case}` | {diag} | {possible} | {skipped} | `{ready}` |".format(
                case=summary.get("case_id"),
                diag=summary.get("diagnostic_event_count"),
                possible=summary.get("possible_setup_event_count"),
                skipped=summary.get("skipped_no_setup_count"),
                ready=summary.get("shadow_outcome_readiness"),
            )
        )
    lines += [
        "",
        "## Aggregate Counts",
        "",
        f"- Possible setup rows written: `{len(rows)}`",
        f"- Total diagnostic events seen: `{sum(int(s.get('diagnostic_event_count') or 0) for s in summaries)}`",
        f"- Total NO_SETUP skipped: `{sum(int(s.get('skipped_no_setup_count') or 0) for s in summaries)}`",
        "",
    ]
    lines += markdown_table(outcome_counts, "Outcome Labels")
    lines += markdown_table(classification_counts, "Possible Setup Classifications")
    lines += markdown_table(spread_counts, "Spread Buckets")
    lines += markdown_table(session_counts, "Server-Time Session Buckets")
    lines += [
        "## Interpretation",
        "",
        "- Current AQ diagnostics contain possible setup labels, but they do not include a direction field.",
        "- Because direction is missing, the prototype correctly marks possible setups as `DIRECTION_MISSING` instead of guessing buy/sell context.",
        "- No TP/SL, R-multiple, or profitability interpretation is possible from these artifacts.",
        "- The next safe step is to add richer diagnostic logging or exported OHLC context in a later reviewed checkpoint before any order-path implementation.",
        "",
    ]
    lines += [
        "## Guardrails",
        "",
        "- No MT5 run was performed by this parser.",
        "- No EA/source code was changed by this parser.",
        "- No presets were changed by this parser.",
        "- No market orders, pending orders, or position modifications were generated.",
        "- This is not proof of profitability and not approval for demo/live trading.",
    ]
    summary_md = "\n".join(lines) + "\n"
    (results_root / "paf_shadow_outcome_summary.md").write_text(summary_md, encoding="utf-8")
    (results_root / "checkpoint_at_shadow_outcome_parser_summary.md").write_text(summary_md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prototype no-order PAF shadow outcome labeler.")
    parser.add_argument("--run-id", help="Specific run id to parse.")
    parser.add_argument("--latest-run", action="store_true", help="Parse latest run_* folder under configured roots.")
    parser.add_argument("--runs-root", default="research/runs", help="Primary run root.")
    parser.add_argument("--artifacts-root", default="mt5_artifacts", help="Artifact root containing run_* folders.")
    parser.add_argument("--results-root", default="research/results", help="Where aggregate outputs are written.")
    args = parser.parse_args()

    run_root = find_run_root(args)
    case_dirs = sorted(path for path in run_root.iterdir() if path.is_dir())
    if not case_dirs:
        raise SystemExit(f"No case folders found under {run_root}")

    all_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for case_dir in case_dirs:
        rows, summary = parse_case(case_dir)
        all_rows.extend(rows)
        summaries.append(summary)
        write_case_outputs(case_dir, rows, summary)

    write_aggregate_outputs(Path(args.results_root), run_root.name, all_rows, summaries)
    print(f"Parsed {len(case_dirs)} cases from {run_root}")
    print(f"Wrote {len(all_rows)} possible setup rows")
    print(f"Aggregate summary: {Path(args.results_root) / 'paf_shadow_outcome_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
