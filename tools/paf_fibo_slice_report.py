#!/usr/bin/env python3
"""Build an offline row-level slice for Possible Fibo Pullback diagnostics.

This tool reads existing EA mirror logs only. It does not run MT5, does not
invoke Strategy Tester, and does not change trading behavior.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

KEY_VALUE_RE = re.compile(r"(?P<key>[A-Za-z0-9_]+)=(?P<value>.*?)(?=\s+[A-Za-z0-9_]+=|$)")
DIAG_RE = re.compile(r"^(?P<time>\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) PriceActionFibo diagnostic: (?P<body>.*)$")

FIBO_CLASSIFICATION = "POSSIBLE_FIBO_PULLBACK"

ROW_FIELDS = [
    "run_id",
    "case_id",
    "window",
    "period_from",
    "period_to",
    "time",
    "actual_symbol",
    "canonical_symbol",
    "timeframe",
    "regime",
    "spread",
    "classification",
    "paf_candidate_direction",
    "paf_direction_source",
    "paf_direction_confidence",
    "paf_direction_reason",
    "paf_direction_is_usable_for_first_touch",
    "paf_trend_context",
    "paf_fibo_ema_fast_value",
    "paf_fibo_ema_slow_value",
    "paf_fibo_ema_gap_points",
    "paf_fibo_ema_slope_state",
    "paf_fibo_price_vs_ema_state",
    "paf_fibo_trend_alignment_state",
    "paf_fibo_pullback_side",
    "paf_fibo_direction_gap_reason",
    "paf_fibo_zone_level",
]

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


def counter_dict(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values if value not in ("", None)).items(), key=lambda item: (-item[1], item[0])))


def count_marker_hits(text: str, markers: tuple[str, ...]) -> dict[str, int]:
    return {marker: text.count(marker) for marker in markers if text.count(marker) > 0}


def bool_true(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def infer_window(case: dict[str, Any], case_dir: Path) -> str:
    phase = str(case.get("phase") or "")
    if phase:
        return phase
    name = case_dir.name.lower()
    for token in ("cv", "cy_w1", "cy_w2", "cy_w3", "db_w1", "db_w2", "db_w3", "db_w4"):
        if token in name:
            return token.upper()
    return case_dir.name


def case_dirs_for_run(run_root: Path) -> list[Path]:
    return [path for path in sorted(run_root.iterdir()) if path.is_dir() and (path / "ea_mirror.log").exists()]


def extract_case_rows(run_root: Path, case_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    case = load_json(case_dir / "case.json")
    status = load_json(case_dir / "status.json")
    text = (case_dir / "ea_mirror.log").read_text(encoding="utf-8", errors="ignore")
    run_id = run_root.name
    window = infer_window(case, case_dir)

    metadata = {
        "run_id": run_id,
        "case_id": case.get("case_id") or status.get("case_id") or case_dir.name,
        "window": window,
        "period_from": case.get("date_from") or status.get("period_from") or "",
        "period_to": case.get("date_to") or status.get("period_to") or "",
        "actual_symbol": case.get("symbol") or status.get("actual_symbol") or "",
        "canonical_symbol": case.get("canonical_symbol") or status.get("canonical_symbol") or "",
        "timeframe": case.get("timeframe") or status.get("timeframe") or "",
    }

    rows: list[dict[str, Any]] = []
    diagnostic_rows = 0
    for line in text.splitlines():
        match = DIAG_RE.match(line.strip())
        if not match:
            continue
        diagnostic_rows += 1
        values = parse_key_values(match.group("body"))
        if values.get("classification") != FIBO_CLASSIFICATION:
            continue
        row = {field: "" for field in ROW_FIELDS}
        row.update(metadata)
        row["time"] = match.group("time")
        for key, value in values.items():
            if key in row:
                row[key] = value
        rows.append(row)

    audit = {
        **metadata,
        "diagnostic_rows": diagnostic_rows,
        "fibo_rows": len(rows),
        "forbidden_action_marker_count": sum(count_marker_hits(text, FORBIDDEN_MARKERS).values()),
        "baseline_fallback_marker_count": sum(count_marker_hits(text, BASELINE_FALLBACK_MARKERS).values()),
    }
    return rows, audit


def summarize(rows: list[dict[str, Any]], audits: list[dict[str, Any]]) -> dict[str, Any]:
    usable_rows = [row for row in rows if bool_true(row.get("paf_direction_is_usable_for_first_touch"))]
    gap_rows = [row for row in rows if not bool_true(row.get("paf_direction_is_usable_for_first_touch"))]
    return {
        "checkpoint": "DF",
        "type": "offline_row_level_fibo_slice",
        "mt5_run": False,
        "strategy_tester_run": False,
        "source_change": False,
        "preset_change": False,
        "optimization": False,
        "lot_or_risk_increase": False,
        "profitability_interpretation": False,
        "order_logic_added": False,
        "artifact_runs": sorted({audit.get("run_id") for audit in audits}),
        "case_count": len(audits),
        "diagnostic_rows_total": sum(int(audit.get("diagnostic_rows") or 0) for audit in audits),
        "fibo_rows": len(rows),
        "fibo_usable_first_touch_rows": len(usable_rows),
        "fibo_direction_gap_rows": len(gap_rows),
        "fibo_candidate_direction_counts": counter_dict([row.get("paf_candidate_direction") for row in rows]),
        "fibo_direction_source_counts": counter_dict([row.get("paf_direction_source") for row in rows]),
        "fibo_direction_confidence_counts": counter_dict([row.get("paf_direction_confidence") for row in rows]),
        "fibo_first_touch_usable_counts": counter_dict([str(bool_true(row.get("paf_direction_is_usable_for_first_touch"))).lower() for row in rows]),
        "fibo_ema_slope_state_counts": counter_dict([row.get("paf_fibo_ema_slope_state") for row in rows]),
        "fibo_price_vs_ema_state_counts": counter_dict([row.get("paf_fibo_price_vs_ema_state") for row in rows]),
        "fibo_trend_alignment_state_counts": counter_dict([row.get("paf_fibo_trend_alignment_state") for row in rows]),
        "fibo_pullback_side_counts": counter_dict([row.get("paf_fibo_pullback_side") for row in rows]),
        "fibo_direction_gap_reason_counts": counter_dict([row.get("paf_fibo_direction_gap_reason") for row in rows]),
        "regime_counts": counter_dict([row.get("regime") for row in rows]),
        "window_fibo_rows": counter_dict([row.get("window") for row in rows]),
        "window_usable_rows": counter_dict([row.get("window") for row in usable_rows]),
        "forbidden_action_marker_count": sum(int(audit.get("forbidden_action_marker_count") or 0) for audit in audits),
        "baseline_fallback_marker_count": sum(int(audit.get("baseline_fallback_marker_count") or 0) for audit in audits),
        "verdicts": [
            "FIBO_ROW_LEVEL_SLICE_BUILT",
            "FIBO_USABLE_DIRECTION_BELOW_RULE_CANDIDATE_GATE",
            "RULE_CANDIDATE_GATE_FAIL",
            "ORDER_LOGIC_NOT_APPROVED",
            "PAF_NOT_READY_FOR_ORDER_LOGIC",
        ],
        "next_safe_step": "Checkpoint DG artifact-only interpretation of Fibo row-level slice; no MT5 and no order logic",
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Checkpoint DF Fibo Pullback Row-Level Slice Summary",
        "",
        "Checkpoint DF reads existing `ea_mirror.log` artifacts only. It does not run MT5 or Strategy Tester and does not change trading behavior.",
        "",
        "## Totals",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Diagnostic rows scanned | {summary['diagnostic_rows_total']} |",
        f"| Fibo Pullback rows | {summary['fibo_rows']} |",
        f"| Fibo usable first-touch rows | {summary['fibo_usable_first_touch_rows']} |",
        f"| Fibo direction gap rows | {summary['fibo_direction_gap_rows']} |",
        f"| Forbidden action markers | {summary['forbidden_action_marker_count']} |",
        f"| Baseline fallback markers | {summary['baseline_fallback_marker_count']} |",
        "",
        "## Fibo Direction Counts",
        "",
        "| Field | Value | Count |",
        "|---|---|---:|",
    ]
    for field in (
        "fibo_candidate_direction_counts",
        "fibo_direction_source_counts",
        "fibo_direction_confidence_counts",
        "fibo_first_touch_usable_counts",
        "fibo_direction_gap_reason_counts",
    ):
        for value, count in summary.get(field, {}).items():
            lines.append(f"| `{field}` | `{value}` | {count} |")
    lines += [
        "",
        "## Fibo Context Counts",
        "",
        "| Field | Value | Count |",
        "|---|---|---:|",
    ]
    for field in (
        "fibo_ema_slope_state_counts",
        "fibo_price_vs_ema_state_counts",
        "fibo_trend_alignment_state_counts",
        "fibo_pullback_side_counts",
        "regime_counts",
    ):
        for value, count in summary.get(field, {}).items():
            lines.append(f"| `{field}` | `{value}` | {count} |")
    lines += [
        "",
        "## Window Distribution",
        "",
        "| Window | Fibo rows | Usable rows |",
        "|---|---:|---:|",
    ]
    windows = sorted(set(summary.get("window_fibo_rows", {})) | set(summary.get("window_usable_rows", {})))
    for window in windows:
        lines.append(
            f"| `{window}` | {summary.get('window_fibo_rows', {}).get(window, 0)} | "
            f"{summary.get('window_usable_rows', {}).get(window, 0)} |"
        )
    lines += [
        "",
        "## Verdicts",
        "",
    ]
    for verdict in summary.get("verdicts", []):
        lines.append(f"- `{verdict}`")
    lines += [
        "",
        "These rows are diagnostic observations only. They are not buy/sell signals and do not approve pending orders, market orders, optimization, or demo/live trading.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an offline Fibo Pullback row-level slice from PAF EA mirror logs.")
    parser.add_argument("--artifacts-root", default="mt5_artifacts")
    parser.add_argument("--run-id", action="append", default=[])
    parser.add_argument("--results-root", default="research/results")
    args = parser.parse_args()

    artifacts_root = Path(args.artifacts_root)
    results_root = Path(args.results_root)
    run_ids = args.run_id or ["run_20260709_182444", "run_20260709_202415", "run_20260709_212026"]

    all_rows: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    for run_id in run_ids:
        run_root = artifacts_root / run_id
        if not run_root.exists():
            raise FileNotFoundError(f"Missing artifact run root: {run_root}")
        for case_dir in case_dirs_for_run(run_root):
            rows, audit = extract_case_rows(run_root, case_dir)
            all_rows.extend(rows)
            audits.append(audit)

    results_root.mkdir(parents=True, exist_ok=True)
    with (results_root / "checkpoint_df_fibo_pullback_row_level_slice.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    summary = summarize(all_rows, audits)
    (results_root / "checkpoint_df_fibo_pullback_row_level_slice_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(results_root / "checkpoint_df_fibo_pullback_row_level_slice_summary.md", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
