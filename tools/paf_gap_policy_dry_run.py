#!/usr/bin/env python3
"""Dry-run a reviewed gap policy against PAF lookahead bar gaps.

This tool does not run MT5, does not run Strategy Tester, does not send orders,
does not modify the main validator, and does not run the joiner. It only
classifies already-detected gaps so reviewers can decide whether the data is
safe enough for a later validator-policy implementation.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing gap CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_policy(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing policy JSON: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def weekday_allowed(value: str, allowed_values: list[str]) -> bool:
    return value.strip().lower() in {item.strip().lower() for item in allowed_values}


def classify_weekend_gap(row: dict[str, str], policy: dict[str, Any]) -> str | None:
    weekend_policy = policy.get("allowed_weekend_market_closure", {})
    if not weekend_policy.get("enabled", False):
        return None
    if row.get("classification") != "WEEKEND_MARKET_CLOSURE":
        return None

    max_delta = to_float(weekend_policy.get("max_delta_hours"), 0.0)
    delta = to_float(row.get("delta_hours"), 0.0)
    if max_delta and delta > max_delta:
        return "BLOCKED_WEEKEND_GAP_TOO_LONG"

    if not weekday_allowed(row.get("prev_weekday", ""), weekend_policy.get("allowed_prev_weekdays", [])):
        return "BLOCKED_WEEKEND_PREV_WEEKDAY_MISMATCH"
    if not weekday_allowed(row.get("next_weekday", ""), weekend_policy.get("allowed_next_weekdays", [])):
        return "BLOCKED_WEEKEND_NEXT_WEEKDAY_MISMATCH"
    return "ACCEPTED_WEEKEND_MARKET_CLOSURE"


def classify_daily_session_gap(row: dict[str, str], policy: dict[str, Any]) -> str | None:
    if row.get("classification") != "SHORT_SESSION_OR_HISTORY_GAP":
        return None

    delta = to_float(row.get("delta_hours"), 0.0)
    prev_time = row.get("prev_time", "")
    next_time = row.get("next_time", "")
    prev_clock = prev_time[-8:] if len(prev_time) >= 8 else ""
    next_clock = next_time[-8:] if len(next_time) >= 8 else ""

    for rule in policy.get("daily_session_gap_rules", []):
        if delta > to_float(rule.get("max_delta_hours"), 0.0):
            continue
        if prev_clock not in rule.get("allowed_prev_times", []):
            continue
        if next_clock not in rule.get("allowed_next_times", []):
            continue
        if rule.get("enabled", False):
            return "ACCEPTED_DAILY_BROKER_SESSION_GAP"
        if rule.get("review_required", True):
            return "REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP"
    return None


def classify_gap(row: dict[str, str], policy: dict[str, Any]) -> str:
    weekend_status = classify_weekend_gap(row, policy)
    if weekend_status is not None:
        return weekend_status
    daily_status = classify_daily_session_gap(row, policy)
    if daily_status is not None:
        return daily_status
    return "BLOCKED_UNCLASSIFIED_GAP"


def summarize(classified_rows: list[dict[str, str]], args: argparse.Namespace, policy: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for row in classified_rows:
        status = row["policy_status"]
        counts[status] = counts.get(status, 0) + 1

    blocking_count = sum(
        count
        for status, count in counts.items()
        if status.startswith("BLOCKED") or status.startswith("REVIEW_REQUIRED")
    )
    accepted_count = sum(count for status, count in counts.items() if status.startswith("ACCEPTED"))
    verdict = "PASS" if blocking_count == 0 else "REVIEW_REQUIRED"
    return {
        "verdict": verdict,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "gap_csv": args.gap_csv,
        "policy_json": args.policy_json,
        "policy_status": policy.get("policy_status", ""),
        "gap_count": len(classified_rows),
        "accepted_count": accepted_count,
        "blocking_or_review_count": blocking_count,
        "status_counts": counts,
        "joiner_status": "allowed_by_gap_policy" if verdict == "PASS" else "blocked_by_gap_policy",
        "guardrails": [
            "offline gap policy dry-run only",
            "no MT5 run",
            "no Strategy Tester run",
            "no orders",
            "no validator implementation change",
            "no joiner run",
            "no optimization",
            "no profitability claim",
        ],
    }


def write_classified_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "prev_time",
        "next_time",
        "delta_hours",
        "missing_h1_bars_estimate",
        "prev_weekday",
        "next_weekday",
        "classification",
        "policy_status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    lines = [
        "# PAF Gap Policy Dry-Run Summary",
        "",
        "This is an offline policy dry-run. It does not run MT5, does not run Strategy Tester, does not change the validator, does not run the joiner, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"`{summary['verdict']}`",
        "",
        "## Inputs",
        "",
        f"- Symbol: `{summary['symbol']}`",
        f"- Timeframe: `{summary['timeframe']}`",
        f"- Gap CSV: `{summary['gap_csv']}`",
        f"- Policy JSON: `{summary['policy_json']}`",
        f"- Policy status: `{summary['policy_status']}`",
        "",
        "## Counts",
        "",
        f"- Gap count: `{summary['gap_count']}`",
        f"- Accepted count: `{summary['accepted_count']}`",
        f"- Blocking/review count: `{summary['blocking_or_review_count']}`",
        f"- Joiner status: `{summary['joiner_status']}`",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(summary["status_counts"].items()):
        lines.append(f"- `{status}`: `{count}`")

    lines += [
        "",
        "## Gap Decisions",
        "",
        "| Previous time | Next time | Delta hours | Source classification | Policy status |",
        "|---|---|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {prev_time} | {next_time} | {delta_hours} | `{classification}` | `{policy_status}` |".format(
                **row
            )
        )

    lines += [
        "",
        "## Guardrails",
        "",
        "- Offline gap policy dry-run only.",
        "- No MT5 run.",
        "- No Strategy Tester run.",
        "- No market orders or pending orders.",
        "- No validator implementation change.",
        "- No joiner run.",
        "- No optimization.",
        "- No profitability claim.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run a PAF gap policy against an attributed gap CSV.")
    parser.add_argument("--gap-csv", required=True)
    parser.add_argument("--policy-json", required=True)
    parser.add_argument("--results-root", default="research/results/paf_gap_policy_dry_run")
    parser.add_argument("--symbol", default="GOLD#")
    parser.add_argument("--timeframe", default="H1")
    args = parser.parse_args()

    rows = read_csv(Path(args.gap_csv))
    policy = load_policy(Path(args.policy_json))
    classified_rows = []
    for row in rows:
        updated = dict(row)
        updated["policy_status"] = classify_gap(row, policy)
        classified_rows.append(updated)

    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)
    summary = summarize(classified_rows, args, policy)
    (results_root / "gap_policy_dry_run_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_classified_csv(results_root / "gap_policy_dry_run.csv", classified_rows)
    write_markdown(results_root / "gap_policy_dry_run_summary.md", summary, classified_rows)
    print(f"Gap policy dry-run verdict: {summary['verdict']}")
    print(f"Summary: {results_root / 'gap_policy_dry_run_summary.md'}")
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
