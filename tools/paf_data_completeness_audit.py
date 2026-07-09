#!/usr/bin/env python3
"""
Checkpoint CJ: offline PAF data completeness audit.

This tool reads the Checkpoint CE first-touch relabel CSV and reports whether
each row has enough diagnostic context for first-touch interpretation. It does
not run MT5, does not call Strategy Tester, and does not alter trading logic.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


DEFAULT_INPUT = Path(
    "research/results/checkpoint_ce_paf_first_touch_relabel/"
    "paf_shadow_outcomes_first_touch_relabel.csv"
)
DEFAULT_RESULTS_ROOT = Path("research/results/checkpoint_cj_paf_data_completeness")
HORIZONS = (6, 12, 24, 48)

REQUIRED_FIELDS = {
    "signal_time": ("event_time",),
    "symbol": ("actual_symbol", "canonical_symbol"),
    "timeframe": ("timeframe",),
    "classification": ("classification",),
    "direction": ("direction",),
    "entry_reference_price": ("entry_reference_price",),
    "source_run_id": ("run_id",),
    "source_file": ("source_file",),
}

RECOMMENDED_FIELDS = {
    "session_bucket": ("session_bucket",),
    "spread_bucket": ("spread_bucket",),
    "regime": ("regime",),
    "offline_atr_14": ("offline_atr_14",),
}


def is_blank(value: object) -> bool:
    if value is None:
        return True
    return str(value).strip() == ""


def first_present(row: Dict[str, str], candidates: Sequence[str]) -> str:
    for name in candidates:
        if not is_blank(row.get(name)):
            return str(row.get(name)).strip()
    return ""


def missing_logical_fields(row: Dict[str, str], field_map: Dict[str, Sequence[str]]) -> List[str]:
    missing: List[str] = []
    for logical_name, candidates in field_map.items():
        if not first_present(row, candidates):
            missing.append(logical_name)
    return missing


def horizon_missing(row: Dict[str, str], horizon: int) -> List[str]:
    missing: List[str] = []
    prefix = f"ce_h{horizon}"
    for suffix in ("bars_available", "outcome_label", "tp_price", "sl_price"):
        name = f"{prefix}_{suffix}"
        if is_blank(row.get(name)):
            missing.append(name)
    return missing


def row_status(row: Dict[str, str]) -> Dict[str, object]:
    missing_required = missing_logical_fields(row, REQUIRED_FIELDS)
    missing_recommended = missing_logical_fields(row, RECOMMENDED_FIELDS)
    missing_by_horizon = {str(h): horizon_missing(row, h) for h in HORIZONS}

    direction = first_present(row, REQUIRED_FIELDS["direction"])
    ce_status = row.get("ce_relabel_status", "").strip()
    ce_reason = row.get("ce_relabel_reason", "").strip()

    has_any_complete_horizon = any(not missing_by_horizon[str(h)] for h in HORIZONS)
    has_all_complete_horizons = all(not missing_by_horizon[str(h)] for h in HORIZONS)

    if ce_status == "RELABEL_READY" and not missing_required and has_all_complete_horizons:
        readiness_status = "RELABEL_READY"
        readiness_reason = "required fields and all horizon TP/SL labels are complete"
    elif ce_status == "DIRECTION_MISSING" or "direction" in missing_required or direction == "DIRECTION_MISSING":
        readiness_status = "DIRECTION_MISSING"
        readiness_reason = ce_reason or "direction is missing or unusable"
    elif ce_status == "DATA_MISSING":
        readiness_status = "DATA_MISSING"
        readiness_reason = ce_reason or "required market data or ATR context is missing"
    elif not has_any_complete_horizon:
        readiness_status = "HORIZON_CONTEXT_MISSING"
        readiness_reason = "no horizon has complete bars/outcome/TP/SL fields"
    elif missing_required:
        readiness_status = "REQUIRED_FIELDS_MISSING"
        readiness_reason = "missing required fields: " + ", ".join(missing_required)
    else:
        readiness_status = "PARTIAL_HORIZON_CONTEXT"
        readiness_reason = "some horizon fields are incomplete"

    return {
        "missing_required_fields": missing_required,
        "missing_recommended_fields": missing_recommended,
        "missing_by_horizon": missing_by_horizon,
        "readiness_status": readiness_status,
        "readiness_reason": readiness_reason,
        "has_any_complete_horizon": has_any_complete_horizon,
        "has_all_complete_horizons": has_all_complete_horizons,
    }


def pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100.0, 2)


def sorted_counter(counter: Counter) -> Dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def ensure_results_root(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_missing_rows(path: Path, rows: List[Dict[str, str]], statuses: List[Dict[str, object]]) -> None:
    fieldnames = [
        "row_index",
        "run_id",
        "case_id",
        "event_time",
        "classification",
        "session_bucket",
        "spread_bucket",
        "regime",
        "direction",
        "ce_relabel_status",
        "readiness_status",
        "readiness_reason",
        "missing_required_fields",
        "missing_recommended_fields",
        "missing_h6_fields",
        "missing_h12_fields",
        "missing_h24_fields",
        "missing_h48_fields",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, (row, status) in enumerate(zip(rows, statuses), start=1):
            missing_by_horizon = status["missing_by_horizon"]
            writer.writerow(
                {
                    "row_index": index,
                    "run_id": row.get("run_id", ""),
                    "case_id": row.get("case_id", ""),
                    "event_time": row.get("event_time", ""),
                    "classification": row.get("classification", ""),
                    "session_bucket": row.get("session_bucket", ""),
                    "spread_bucket": row.get("spread_bucket", ""),
                    "regime": row.get("regime", ""),
                    "direction": row.get("direction", ""),
                    "ce_relabel_status": row.get("ce_relabel_status", ""),
                    "readiness_status": status["readiness_status"],
                    "readiness_reason": status["readiness_reason"],
                    "missing_required_fields": ";".join(status["missing_required_fields"]),
                    "missing_recommended_fields": ";".join(status["missing_recommended_fields"]),
                    "missing_h6_fields": ";".join(missing_by_horizon["6"]),
                    "missing_h12_fields": ";".join(missing_by_horizon["12"]),
                    "missing_h24_fields": ";".join(missing_by_horizon["24"]),
                    "missing_h48_fields": ";".join(missing_by_horizon["48"]),
                }
            )


def write_readiness_by_dimension(
    path: Path,
    rows: List[Dict[str, str]],
    statuses: List[Dict[str, object]],
    dimension: str,
) -> None:
    bucket: Dict[str, Counter] = defaultdict(Counter)
    for row, status in zip(rows, statuses):
        key = row.get(dimension, "").strip() or "UNKNOWN"
        bucket[key]["rows"] += 1
        bucket[key][str(status["readiness_status"])] += 1
        if status["readiness_status"] == "RELABEL_READY":
            bucket[key]["relabel_ready_rows"] += 1
        if status["missing_required_fields"]:
            bucket[key]["rows_with_missing_required"] += 1
        if status["missing_recommended_fields"]:
            bucket[key]["rows_with_missing_recommended"] += 1

    fieldnames = [
        dimension,
        "rows",
        "relabel_ready_rows",
        "direction_missing_rows",
        "data_missing_rows",
        "horizon_context_missing_rows",
        "partial_horizon_context_rows",
        "required_fields_missing_rows",
        "rows_with_missing_required",
        "rows_with_missing_recommended",
        "relabel_ready_rate_percent",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for key, counts in sorted(bucket.items(), key=lambda item: (-item[1]["rows"], item[0])):
            rows_count = counts["rows"]
            writer.writerow(
                {
                    dimension: key,
                    "rows": rows_count,
                    "relabel_ready_rows": counts["relabel_ready_rows"],
                    "direction_missing_rows": counts["DIRECTION_MISSING"],
                    "data_missing_rows": counts["DATA_MISSING"],
                    "horizon_context_missing_rows": counts["HORIZON_CONTEXT_MISSING"],
                    "partial_horizon_context_rows": counts["PARTIAL_HORIZON_CONTEXT"],
                    "required_fields_missing_rows": counts["REQUIRED_FIELDS_MISSING"],
                    "rows_with_missing_required": counts["rows_with_missing_required"],
                    "rows_with_missing_recommended": counts["rows_with_missing_recommended"],
                    "relabel_ready_rate_percent": pct(counts["relabel_ready_rows"], rows_count),
                }
            )


def summarize(rows: List[Dict[str, str]], statuses: List[Dict[str, object]]) -> Dict[str, object]:
    total = len(rows)
    status_counts = Counter(str(status["readiness_status"]) for status in statuses)
    missing_required = Counter()
    missing_recommended = Counter()
    missing_horizon = Counter()
    ce_status_counts = Counter(row.get("ce_relabel_status", "").strip() or "UNKNOWN" for row in rows)

    for status in statuses:
        missing_required.update(status["missing_required_fields"])
        missing_recommended.update(status["missing_recommended_fields"])
        for horizon, fields in status["missing_by_horizon"].items():
            if fields:
                missing_horizon[f"h{horizon}"] += 1
                missing_horizon.update(fields)

    relabel_ready = status_counts["RELABEL_READY"]
    direction_missing = status_counts["DIRECTION_MISSING"]
    data_missing = status_counts["DATA_MISSING"]
    data_missing_rate = pct(data_missing, total)
    direction_missing_rate = pct(direction_missing, total)
    relabel_ready_rate = pct(relabel_ready, total)

    diagnostic_gate_results = {
        "direction_missing_rate_lte_10_percent": direction_missing_rate <= 10.0,
        "data_missing_rate_lte_5_percent": data_missing_rate <= 5.0,
        "relabel_ready_rows_gte_100": relabel_ready >= 100,
        "relabel_ready_rows_gte_300": relabel_ready >= 300,
    }

    if all(diagnostic_gate_results.values()):
        classification = "DATA_COMPLETENESS_GATE_PASS"
    elif relabel_ready >= 100 and direction_missing_rate <= 10.0:
        classification = "DIAGNOSTIC_INTERPRETATION_READY_NOT_RULE_READY"
    else:
        classification = "DATA_COMPLETENESS_GATE_FAIL"

    return {
        "checkpoint": "CJ",
        "status": "PASS_OFFLINE_COMPLETENESS_AUDIT",
        "rows_read": total,
        "readiness_counts": sorted_counter(status_counts),
        "ce_relabel_status_counts": sorted_counter(ce_status_counts),
        "relabel_ready_rows": relabel_ready,
        "direction_missing_rows": direction_missing,
        "data_missing_rows": data_missing,
        "relabel_ready_rate_percent": relabel_ready_rate,
        "direction_missing_rate_percent": direction_missing_rate,
        "data_missing_rate_percent": data_missing_rate,
        "missing_required_field_counts": sorted_counter(missing_required),
        "missing_recommended_field_counts": sorted_counter(missing_recommended),
        "missing_horizon_field_counts": sorted_counter(missing_horizon),
        "diagnostic_gate_results": diagnostic_gate_results,
        "classification": classification,
        "guardrails": [
            "offline files only",
            "MT5 not run",
            "Strategy Tester not run",
            "EA source not changed",
            "presets not changed",
            "order logic not approved",
            "optimization not performed",
            "profitability not claimed",
        ],
    }


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_summary_md(path: Path, summary: Dict[str, object]) -> None:
    readiness_counts = summary["readiness_counts"]
    gates = summary["diagnostic_gate_results"]

    readiness_rows = [(key, value) for key, value in readiness_counts.items()]
    gate_rows = [(key, "PASS" if value else "FAIL") for key, value in gates.items()]

    content = [
        "# Checkpoint CJ: PAF Data Completeness Audit Summary",
        "",
        "This is an offline data completeness audit. It does not run MT5, does not run Strategy Tester, does not change EA/source code, and does not approve order logic.",
        "",
        "## Verdict",
        "",
        f"- Status: `{summary['status']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Rows read: `{summary['rows_read']}`",
        f"- Relabel-ready rows: `{summary['relabel_ready_rows']}` (`{summary['relabel_ready_rate_percent']}%`)",
        f"- Direction-missing rows: `{summary['direction_missing_rows']}` (`{summary['direction_missing_rate_percent']}%`)",
        f"- Data-missing rows: `{summary['data_missing_rows']}` (`{summary['data_missing_rate_percent']}%`)",
        "",
        "## Readiness Counts",
        "",
        markdown_table(["Readiness status", "Rows"], readiness_rows),
        "",
        "## Diagnostic Gates",
        "",
        markdown_table(["Gate", "Result"], gate_rows),
        "",
        "## Missing Required Fields",
        "",
        markdown_table(
            ["Field", "Rows"],
            [(key, value) for key, value in summary["missing_required_field_counts"].items()] or [("None", 0)],
        ),
        "",
        "## Missing Recommended Fields",
        "",
        markdown_table(
            ["Field", "Rows"],
            [(key, value) for key, value in summary["missing_recommended_field_counts"].items()] or [("None", 0)],
        ),
        "",
        "## Interpretation",
        "",
        "- Current data does not pass the CI gates for order logic.",
        "- Direction missing remains too high.",
        "- Relabel-ready sample size remains too small.",
        "- This result is a data-quality diagnosis, not a trading-performance result.",
        "",
        "## Guardrails",
        "",
        "- No MT5 run.",
        "- No Strategy Tester run.",
        "- No EA/source code changes.",
        "- No preset changes.",
        "- No order logic approved.",
        "- No optimization.",
        "- No profitability claim.",
        "",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def write_guardrail_md(path: Path, summary: Dict[str, object]) -> None:
    content = [
        "# Checkpoint CJ Guardrail Summary",
        "",
        "- `MT5_NOT_RUN`",
        "- `STRATEGY_TESTER_NOT_RUN`",
        "- `EA_SOURCE_NOT_CHANGED`",
        "- `PRESETS_NOT_CHANGED`",
        "- `ORDER_LOGIC_NOT_APPROVED`",
        "- `OPTIMIZATION_NOT_PERFORMED`",
        "- `LOT_RISK_NOT_INCREASED`",
        "- `PROFITABILITY_NOT_CLAIMED`",
        f"- Final classification: `{summary['classification']}`",
        "",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit PAF data completeness from offline CSV artifacts.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input PAF first-touch relabel CSV.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT, help="Output folder.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_results_root(args.results_root)
    rows = read_rows(args.input)
    statuses = [row_status(row) for row in rows]
    summary = summarize(rows, statuses)
    summary["input_csv"] = str(args.input)
    summary["outputs"] = {
        "summary_json": str(args.results_root / "completeness_summary.json"),
        "summary_md": str(args.results_root / "completeness_summary.md"),
        "missing_fields_by_row": str(args.results_root / "missing_fields_by_row.csv"),
        "readiness_by_classification": str(args.results_root / "readiness_by_classification.csv"),
        "readiness_by_session": str(args.results_root / "readiness_by_session.csv"),
        "readiness_by_regime": str(args.results_root / "readiness_by_regime.csv"),
        "guardrail_summary": str(args.results_root / "completeness_guardrail_summary.md"),
    }

    write_missing_rows(args.results_root / "missing_fields_by_row.csv", rows, statuses)
    write_readiness_by_dimension(args.results_root / "readiness_by_classification.csv", rows, statuses, "classification")
    write_readiness_by_dimension(args.results_root / "readiness_by_session.csv", rows, statuses, "session_bucket")
    write_readiness_by_dimension(args.results_root / "readiness_by_regime.csv", rows, statuses, "regime")

    (args.results_root / "completeness_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_summary_md(args.results_root / "completeness_summary.md", summary)
    write_guardrail_md(args.results_root / "completeness_guardrail_summary.md", summary)

    print(f"Wrote completeness summary: {args.results_root / 'completeness_summary.md'}")
    print(f"Classification: {summary['classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
