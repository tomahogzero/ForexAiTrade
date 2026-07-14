#!/usr/bin/env python3
"""Review merged EU outcomes with the approved unverified-gap interpretation."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


HORIZONS = (6, 12, 24, 48)
OUTCOMES = ("TP_FIRST", "SL_FIRST", "AMBIGUOUS_SAME_BAR", "NO_RESOLUTION")


def main() -> int:
    parser = argparse.ArgumentParser(description="Artifact-only Checkpoint EZ fail-closed review.")
    parser.add_argument("--outcomes-csv", required=True)
    parser.add_argument("--eu-summary-json", required=True)
    parser.add_argument("--results-root", required=True)
    args = parser.parse_args()

    with Path(args.outcomes_csv).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    eu = json.loads(Path(args.eu_summary_json).read_text(encoding="utf-8"))
    if len(rows) != 1600:
        raise SystemExit(f"Expected 1600 EU event rows, got {len(rows)}")
    keys = [(row["run_id"], row["case_id"], row["event_time"]) for row in rows]
    if len(set(keys)) != len(rows):
        raise SystemExit("Event-key conservation failed: duplicate event key")

    horizons: dict[str, object] = {}
    for horizon in HORIZONS:
        prefix = f"h{horizon}"
        included = [row for row in rows if row[f"{prefix}_eligibility"] == "INCLUDED"]
        excluded = [row for row in rows if row[f"{prefix}_eligibility"] == "EXCLUDED"]
        original_reasons = Counter(row[f"{prefix}_exclusion_reason"] for row in excluded)
        if any(reason not in {"BLOCKED_GAP_INSIDE_LOOKAHEAD", ""} for reason in original_reasons):
            raise SystemExit(f"Unexpected EU exclusion reason at H{horizon}: {dict(original_reasons)}")
        if len(included) + len(excluded) != len(rows):
            raise SystemExit(f"Event conservation failed at H{horizon}")
        counts = Counter(row[f"{prefix}_outcome"] for row in included)
        if sum(counts[outcome] for outcome in OUTCOMES) != len(included):
            raise SystemExit(f"Outcome conservation failed at H{horizon}")
        horizons[str(horizon)] = {
            "total_events": len(rows),
            "included_events": len(included),
            "excluded_events": len(excluded),
            "exclusion_rate_pct": round(len(excluded) / len(rows) * 100, 2),
            "exclusion_reasons": {"DATA_INCOMPLETE_GAP": len(excluded)},
            "source_exclusion_reasons": dict(original_reasons),
            "outcomes": {outcome: counts[outcome] for outcome in OUTCOMES},
        }

    result = {
        "execution_status": "PASS",
        "method": "artifact-only interpretation of EU fail-closed exclusions",
        "decision": "PARTIAL_EVIDENCE_ACCEPTED_WITH_FAIL_CLOSED_EXCLUSIONS",
        "broker_history_completeness": "NOT_PROVEN",
        "total_events": len(rows),
        "unique_event_keys": len(set(keys)),
        "horizons": horizons,
        "strategy_performance_status": "NOT_EVALUATED",
        "order_logic_status": "NOT_APPROVED",
        "paf_status": "NOT_READY_FOR_ORDER_LOGIC",
        "profitability_claim": False,
        "guardrails": [
            "unverified gaps remain unverified", "no validator bypass", "no interpolation or gap bridging",
            "excluded event/horizon is DATA_INCOMPLETE_GAP and has no outcome", "offline only",
        ],
    }
    root = Path(args.results_root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "checkpoint_ez_fail_closed_shadow_review.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Checkpoint EZ Fail-Closed Shadow Review", "", "Execution review only; strategy performance is not evaluated.", ""]
    lines.extend(f"- {key}: `{value}`" for key, value in result.items() if key != "horizons")
    for horizon, data in horizons.items():
        lines.append(f"- H{horizon}: `{data}`")
    lines.append("")
    (root / "checkpoint_ez_fail_closed_shadow_review.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
