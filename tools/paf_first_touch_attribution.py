#!/usr/bin/env python3
"""Offline first-touch attribution for PAF diagnostics.

This tool summarizes Checkpoint CE shadow first-touch labels by diagnostic
dimensions such as classification, session, spread bucket, and regime. It does
not run MT5, does not generate orders, does not optimize parameters, and does
not prove profitability.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_HORIZONS = [6, 12, 24, 48]
DEFAULT_DIMENSIONS = ["classification", "session_bucket", "spread_bucket", "regime"]
LABELS = ["TP_FIRST", "SL_FIRST", "NO_RESOLUTION", "AMBIGUOUS_SAME_BAR", "DATA_MISSING", "DIRECTION_MISSING"]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"INPUT_MISSING: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def counter_dict(values: list[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values if value not in (None, "")).items()))


def parse_horizons(value: str) -> list[int]:
    horizons: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if item:
            horizons.append(int(item))
    if horizons != DEFAULT_HORIZONS:
        raise argparse.ArgumentTypeError("Checkpoint CG requires horizons 6,12,24,48")
    return horizons


def dimension_value(row: dict[str, str], dimension: str) -> str:
    value = (row.get(dimension) or "").strip()
    return value or "UNKNOWN"


def label_for(row: dict[str, str], horizon: int) -> str:
    value = (row.get(f"ce_h{horizon}_outcome_label") or "").strip()
    return value or "UNKNOWN"


def build_attribution(rows: list[dict[str, str]], horizons: list[int], dimensions: list[str]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for horizon in horizons:
        for dimension in dimensions:
            buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
            for row in rows:
                buckets[dimension_value(row, dimension)].append(row)
            for value, bucket_rows in sorted(buckets.items()):
                counts = Counter(label_for(row, horizon) for row in bucket_rows)
                row_count = len(bucket_rows)
                ready_rows = sum(1 for row in bucket_rows if (row.get("ce_relabel_status") or "").strip() == "RELABEL_READY")
                blocked_rows = row_count - ready_rows
                tp = counts.get("TP_FIRST", 0)
                sl = counts.get("SL_FIRST", 0)
                ambiguous = counts.get("AMBIGUOUS_SAME_BAR", 0)
                no_resolution = counts.get("NO_RESOLUTION", 0)
                evaluable = tp + sl + ambiguous + no_resolution
                output.append(
                    {
                        "horizon": horizon,
                        "dimension": dimension,
                        "value": value,
                        "rows": row_count,
                        "relabel_ready_rows": ready_rows,
                        "blocked_rows": blocked_rows,
                        "tp_first": tp,
                        "sl_first": sl,
                        "no_resolution": no_resolution,
                        "ambiguous_same_bar": ambiguous,
                        "data_missing": counts.get("DATA_MISSING", 0),
                        "direction_missing": counts.get("DIRECTION_MISSING", 0),
                        "evaluable_rows": evaluable,
                        "sl_minus_tp": sl - tp,
                        "diagnostic_bias": diagnostic_bias(tp, sl, ambiguous, no_resolution),
                    }
                )
    return output


def diagnostic_bias(tp: int, sl: int, ambiguous: int, no_resolution: int) -> str:
    evaluable = tp + sl + ambiguous + no_resolution
    if evaluable == 0:
        return "NO_EVALUABLE_ROWS"
    if sl > tp:
        return "SL_FIRST_DOMINANT"
    if tp > sl:
        return "TP_FIRST_DOMINANT"
    return "BALANCED_OR_UNRESOLVED"


def summarize_findings(attribution: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [row for row in attribution if int(row["evaluable_rows"]) > 0]
    rows.sort(key=lambda row: (int(row["sl_minus_tp"]), int(row["evaluable_rows"])), reverse=True)
    return rows[:12]


def write_summary_md(path: Path, summary: dict[str, Any], top_findings: list[dict[str, Any]]) -> None:
    lines = [
        "# Checkpoint CG: PAF First-Touch Attribution Summary",
        "",
        "This is an offline diagnostic summary. It does not run MT5, does not send orders, does not optimize parameters, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"- Status: `{summary['status']}`",
        f"- Rows read: `{summary['rows_read']}`",
        f"- Relabel-ready rows: `{summary['relabel_ready_rows']}`",
        f"- Direction-missing rows: `{summary['direction_missing_rows']}`",
        f"- Data-missing rows: `{summary['data_missing_rows']}`",
        "",
        "## Overall Label Counts",
        "",
    ]
    for horizon, counts in summary["overall_counts_by_horizon"].items():
        lines += [
            f"### Horizon {horizon}",
            "",
            "| Label | Count |",
            "|---|---:|",
        ]
        for label in LABELS:
            lines.append(f"| `{label}` | {counts.get(label, 0)} |")
        lines.append("")

    lines += [
        "## Top SL-FIRST Diagnostic Concentrations",
        "",
        "| Horizon | Dimension | Value | Rows | Ready | TP_FIRST | SL_FIRST | Bias |",
        "|---:|---|---|---:|---:|---:|---:|---|",
    ]
    for row in top_findings:
        lines.append(
            "| {horizon} | `{dimension}` | `{value}` | {rows} | {ready} | {tp} | {sl} | `{bias}` |".format(
                horizon=row["horizon"],
                dimension=row["dimension"],
                value=row["value"],
                rows=row["rows"],
                ready=row["relabel_ready_rows"],
                tp=row["tp_first"],
                sl=row["sl_first"],
                bias=row["diagnostic_bias"],
            )
        )

    lines += [
        "",
        "## Interpretation Guardrails",
        "",
        "- These are shadow diagnostic labels, not real trades.",
        "- SL_FIRST dominance is a research warning, not proof of loss.",
        "- No parameter or order logic may be changed from this checkpoint.",
        "- Small sample size and direction missing remain major blockers.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_guardrail_md(path: Path) -> None:
    lines = [
        "# Checkpoint CG Guardrail Summary",
        "",
        "| Guardrail | Status |",
        "|---|---|",
        "| MT5 run | `NO` |",
        "| Strategy Tester run | `NO` |",
        "| EA/source changed | `NO` |",
        "| Presets changed | `NO` |",
        "| Order action generated | `NO` |",
        "| First-touch labels rerun | `NO` |",
        "| Optimization | `NO` |",
        "| Profitability claim | `NO` |",
        "",
        "Attribution output is diagnostic-only and must not be converted into trading rules without a later reviewed checkpoint.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Attribute PAF first-touch labels by diagnostic dimensions.")
    parser.add_argument("--relabeled-csv", default="research/results/checkpoint_ce_paf_first_touch_relabel/paf_shadow_outcomes_first_touch_relabel.csv")
    parser.add_argument("--results-root", default="research/results/checkpoint_cg_first_touch_attribution")
    parser.add_argument("--horizons", type=parse_horizons, default=DEFAULT_HORIZONS)
    parser.add_argument("--dimensions", default=",".join(DEFAULT_DIMENSIONS))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.relabeled_csv)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    rows = read_csv(path)
    if not rows:
        raise SystemExit(f"INPUT_MISSING: no relabeled rows found in {path}")

    dimensions = [item.strip() for item in args.dimensions.split(",") if item.strip()]
    if dimensions != DEFAULT_DIMENSIONS:
        raise SystemExit("NO_ATTRIBUTION_SCOPE_CHANGE_APPROVED: dimensions must remain classification,session_bucket,spread_bucket,regime")

    required_columns = {"ce_relabel_status", "classification", "session_bucket", "spread_bucket", "regime"}
    for horizon in args.horizons:
        required_columns.add(f"ce_h{horizon}_outcome_label")
    missing = sorted(column for column in required_columns if column not in rows[0])
    if missing:
        raise SystemExit(f"SCHEMA_MISMATCH: missing columns: {', '.join(missing)}")

    attribution = build_attribution(rows, args.horizons, dimensions)
    top_findings = summarize_findings(attribution)
    overall_counts_by_horizon = {
        str(horizon): counter_dict([label_for(row, horizon) for row in rows])
        for horizon in args.horizons
    }
    relabel_status_counts = counter_dict([row.get("ce_relabel_status") for row in rows])

    output_csv = results_root / "first_touch_attribution_by_dimension.csv"
    summary_json = results_root / "first_touch_attribution_summary.json"
    summary_md = results_root / "first_touch_attribution_summary.md"
    guardrail_md = results_root / "first_touch_attribution_guardrail_summary.md"

    fieldnames = [
        "horizon",
        "dimension",
        "value",
        "rows",
        "relabel_ready_rows",
        "blocked_rows",
        "tp_first",
        "sl_first",
        "no_resolution",
        "ambiguous_same_bar",
        "data_missing",
        "direction_missing",
        "evaluable_rows",
        "sl_minus_tp",
        "diagnostic_bias",
    ]
    write_csv(output_csv, attribution, fieldnames)

    summary = {
        "checkpoint": "CG",
        "status": "PASS_OFFLINE_FIRST_TOUCH_ATTRIBUTION",
        "relabeled_csv": str(path),
        "rows_read": len(rows),
        "relabel_ready_rows": relabel_status_counts.get("RELABEL_READY", 0),
        "data_missing_rows": relabel_status_counts.get("DATA_MISSING", 0),
        "direction_missing_rows": relabel_status_counts.get("DIRECTION_MISSING", 0),
        "dimensions": dimensions,
        "horizons": args.horizons,
        "overall_counts_by_horizon": overall_counts_by_horizon,
        "top_sl_first_concentrations": top_findings,
        "classification": "NOT_READY_FOR_ORDER_LOGIC",
        "guardrails": [
            "offline files only",
            "no MT5 run",
            "no Strategy Tester run",
            "no EA/source changes",
            "no preset changes",
            "no orders",
            "no optimization",
            "no profitability claim",
        ],
        "outputs": {
            "attribution_csv": str(output_csv),
            "summary_json": str(summary_json),
            "summary_md": str(summary_md),
            "guardrail_md": str(guardrail_md),
        },
    }
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary_md(summary_md, summary, top_findings)
    write_guardrail_md(guardrail_md)

    print(f"Wrote attribution: {output_csv}")
    print(f"Wrote summary: {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
