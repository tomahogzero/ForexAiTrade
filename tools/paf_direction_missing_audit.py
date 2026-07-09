#!/usr/bin/env python3
"""
Checkpoint CK: offline root-cause audit for PAF DIRECTION_MISSING rows.

This tool inspects existing offline artifacts only. It does not run MT5,
does not call Strategy Tester, and does not change strategy behavior.
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
DEFAULT_RESULTS_ROOT = Path("research/results/checkpoint_ck_paf_direction_missing_audit")


def is_missing_direction(row: Dict[str, str]) -> bool:
    status = row.get("ce_relabel_status", "").strip()
    direction = row.get("direction", "").strip()
    outcome = row.get("outcome_label", "").strip()
    return status == "DIRECTION_MISSING" or direction in {"", "DIRECTION_UNKNOWN"} or outcome == "DIRECTION_MISSING"


def root_cause_bucket(row: Dict[str, str]) -> str:
    reason = row.get("direction_reason", "").strip()
    classification = row.get("classification", "").strip()
    direction = row.get("direction", "").strip()

    if direction not in {"", "DIRECTION_UNKNOWN"} and row.get("ce_relabel_status", "").strip() != "DIRECTION_MISSING":
        return "NOT_DIRECTION_MISSING"
    if reason == "fibo_pullback_without_clear_ema_direction_context":
        return "FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING"
    if reason == "zone_rejection_without_directional_candle_context":
        return "ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING"
    if classification == "POSSIBLE_FIBO_PULLBACK":
        return "FIBO_PULLBACK_DIRECTION_UNRESOLVED"
    if classification == "POSSIBLE_ZONE_REJECTION":
        return "ZONE_REJECTION_DIRECTION_UNRESOLVED"
    if not reason:
        return "DIRECTION_REASON_MISSING"
    return "OTHER_DIRECTION_CONTEXT_MISSING"


def recommended_fix(bucket: str) -> str:
    fixes = {
        "FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING": (
            "Add diagnostics-only fields for EMA slope/context and candidate direction; do not infer order direction from classification alone."
        ),
        "ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING": (
            "Add diagnostics-only candle rejection direction fields such as rejection side, candle body direction, wick side, and zone side."
        ),
        "FIBO_PULLBACK_DIRECTION_UNRESOLVED": (
            "Audit Fibo pullback parser rules and require explicit candidate direction metadata before first-touch labeling."
        ),
        "ZONE_REJECTION_DIRECTION_UNRESOLVED": (
            "Audit zone rejection parser rules and require explicit directional candle context before first-touch labeling."
        ),
        "DIRECTION_REASON_MISSING": (
            "Improve parser/reporting to emit a precise direction_missing_reason for every missing-direction row."
        ),
        "OTHER_DIRECTION_CONTEXT_MISSING": (
            "Inspect the original diagnostic log line and add explicit diagnostics-only direction context if needed."
        ),
        "NOT_DIRECTION_MISSING": "No action needed for direction missing.",
    }
    return fixes.get(bucket, "Inspect source row manually.")


def pct(part: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((part / total) * 100.0, 2)


def read_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input CSV not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sorted_counter(counter: Counter) -> Dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def write_rows(path: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "row_index",
        "event_time",
        "classification",
        "session_bucket",
        "spread_bucket",
        "regime",
        "direction",
        "direction_reason",
        "ce_relabel_status",
        "ce_relabel_reason",
        "root_cause_bucket",
        "recommended_fix",
        "source_file",
        "case_id",
        "run_id",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def write_group_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def analyze(rows: List[Dict[str, str]]) -> Dict[str, object]:
    total = len(rows)
    missing_rows: List[Dict[str, str]] = []
    all_bucket_counts: Counter = Counter()
    missing_by_reason: Counter = Counter()
    missing_by_classification: Counter = Counter()
    missing_by_session: Counter = Counter()
    missing_by_regime: Counter = Counter()
    missing_by_day: Counter = Counter()

    for index, row in enumerate(rows, start=1):
        bucket = root_cause_bucket(row)
        all_bucket_counts[bucket] += 1
        if not is_missing_direction(row):
            continue

        event_time = row.get("event_time", "")
        day = event_time[:10] if len(event_time) >= 10 else "UNKNOWN"
        enriched = dict(row)
        enriched["row_index"] = str(index)
        enriched["root_cause_bucket"] = bucket
        enriched["recommended_fix"] = recommended_fix(bucket)
        missing_rows.append(enriched)

        missing_by_reason[row.get("direction_reason", "").strip() or "DIRECTION_REASON_MISSING"] += 1
        missing_by_classification[row.get("classification", "").strip() or "UNKNOWN"] += 1
        missing_by_session[row.get("session_bucket", "").strip() or "UNKNOWN"] += 1
        missing_by_regime[row.get("regime", "").strip() or "UNKNOWN"] += 1
        missing_by_day[day] += 1

    missing_count = len(missing_rows)
    root_cause_counts = Counter(row["root_cause_bucket"] for row in missing_rows)

    if missing_count == 0:
        classification = "DIRECTION_COMPLETENESS_PASS"
    elif pct(missing_count, total) <= 10.0:
        classification = "DIRECTION_COMPLETENESS_NEEDS_MONITORING"
    else:
        classification = "DIRECTION_COMPLETENESS_FAIL"

    return {
        "checkpoint": "CK",
        "status": "PASS_OFFLINE_DIRECTION_MISSING_AUDIT",
        "rows_read": total,
        "direction_missing_rows": missing_count,
        "direction_missing_rate_percent": pct(missing_count, total),
        "root_cause_counts": sorted_counter(root_cause_counts),
        "direction_reason_counts": sorted_counter(missing_by_reason),
        "classification_counts": sorted_counter(missing_by_classification),
        "session_counts": sorted_counter(missing_by_session),
        "regime_counts": sorted_counter(missing_by_regime),
        "day_counts": sorted_counter(missing_by_day),
        "all_direction_bucket_counts": sorted_counter(all_bucket_counts),
        "classification": classification,
        "recommended_next_step": (
            "Create a diagnostics-only field plan for explicit PAF candidate direction metadata before changing EA/source."
        ),
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
        "missing_rows": missing_rows,
    }


def build_group_rows(counts: Dict[str, int], total_missing: int, key_name: str) -> List[Dict[str, object]]:
    return [
        {
            key_name: key,
            "direction_missing_rows": value,
            "share_of_missing_percent": pct(value, total_missing),
        }
        for key, value in counts.items()
    ]


def write_summary_md(path: Path, summary: Dict[str, object]) -> None:
    total_missing = int(summary["direction_missing_rows"])
    root_rows = [
        (key, value, pct(value, total_missing), recommended_fix(key))
        for key, value in summary["root_cause_counts"].items()
    ]
    reason_rows = [
        (key, value, pct(value, total_missing))
        for key, value in summary["direction_reason_counts"].items()
    ]
    class_rows = [
        (key, value, pct(value, total_missing))
        for key, value in summary["classification_counts"].items()
    ]
    session_rows = [
        (key, value, pct(value, total_missing))
        for key, value in summary["session_counts"].items()
    ]

    content = [
        "# Checkpoint CK: PAF Direction Missing Root-Cause Audit",
        "",
        "This is an offline root-cause audit. It does not run MT5, does not run Strategy Tester, does not change EA/source code, and does not approve order logic.",
        "",
        "## Verdict",
        "",
        f"- Status: `{summary['status']}`",
        f"- Classification: `{summary['classification']}`",
        f"- Rows read: `{summary['rows_read']}`",
        f"- Direction-missing rows: `{summary['direction_missing_rows']}` (`{summary['direction_missing_rate_percent']}%`)",
        "",
        "## Root Cause Buckets",
        "",
        markdown_table(["Root cause", "Rows", "Share %", "Recommended fix"], root_rows),
        "",
        "## Direction Reason Counts",
        "",
        markdown_table(["Direction reason", "Rows", "Share %"], reason_rows),
        "",
        "## Missing Direction by Classification",
        "",
        markdown_table(["Classification", "Rows", "Share %"], class_rows),
        "",
        "## Missing Direction by Session",
        "",
        markdown_table(["Session", "Rows", "Share %"], session_rows),
        "",
        "## Interpretation",
        "",
        "- Direction missing is not caused by a blank CSV field alone; the rows contain `DIRECTION_UNKNOWN` and explicit diagnostic reasons.",
        "- The dominant issue is missing directional context in Fibo Pullback diagnostics.",
        "- Zone Rejection also lacks directional candle context in a smaller set of rows.",
        "- This should be fixed with diagnostics-only metadata before any first-touch result is used for order logic.",
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
    path.write_text(
        "\n".join(
            [
                "# Checkpoint CK Guardrail Summary",
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
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit root causes for PAF direction-missing rows.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input PAF first-touch relabel CSV.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT, help="Output folder.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.results_root.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.input)
    summary = analyze(rows)
    missing_rows = summary.pop("missing_rows")
    summary["input_csv"] = str(args.input)
    summary["outputs"] = {
        "summary_json": str(args.results_root / "direction_missing_summary.json"),
        "summary_md": str(args.results_root / "direction_missing_summary.md"),
        "missing_rows_csv": str(args.results_root / "direction_missing_rows.csv"),
        "root_cause_counts_csv": str(args.results_root / "direction_missing_root_cause_counts.csv"),
        "classification_counts_csv": str(args.results_root / "direction_missing_by_classification.csv"),
        "session_counts_csv": str(args.results_root / "direction_missing_by_session.csv"),
        "guardrail_summary": str(args.results_root / "direction_missing_guardrail_summary.md"),
    }

    write_rows(args.results_root / "direction_missing_rows.csv", missing_rows)

    total_missing = int(summary["direction_missing_rows"])
    write_group_csv(
        args.results_root / "direction_missing_root_cause_counts.csv",
        build_group_rows(summary["root_cause_counts"], total_missing, "root_cause_bucket"),
        ["root_cause_bucket", "direction_missing_rows", "share_of_missing_percent"],
    )
    write_group_csv(
        args.results_root / "direction_missing_by_classification.csv",
        build_group_rows(summary["classification_counts"], total_missing, "classification"),
        ["classification", "direction_missing_rows", "share_of_missing_percent"],
    )
    write_group_csv(
        args.results_root / "direction_missing_by_session.csv",
        build_group_rows(summary["session_counts"], total_missing, "session_bucket"),
        ["session_bucket", "direction_missing_rows", "share_of_missing_percent"],
    )

    (args.results_root / "direction_missing_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_summary_md(args.results_root / "direction_missing_summary.md", summary)
    write_guardrail_md(args.results_root / "direction_missing_guardrail_summary.md", summary)

    print(f"Wrote direction missing summary: {args.results_root / 'direction_missing_summary.md'}")
    print(f"Classification: {summary['classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
