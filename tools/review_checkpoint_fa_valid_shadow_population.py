#!/usr/bin/env python3
"""Artifact-only coverage interpretation for the EZ valid shadow population."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ez-summary", required=True)
    parser.add_argument("--results-root", required=True)
    args = parser.parse_args()
    source = json.loads(Path(args.ez_summary).read_text(encoding="utf-8"))
    if source["total_events"] != source["unique_event_keys"]:
        raise SystemExit("event-key conservation failed")
    rows = []
    for horizon in ("6", "12", "24", "48"):
        data = source["horizons"][horizon]
        outcomes = data["outcomes"]
        if data["included_events"] + data["excluded_events"] != source["total_events"]:
            raise SystemExit(f"population conservation failed at H{horizon}")
        if sum(outcomes.values()) != data["included_events"]:
            raise SystemExit(f"outcome conservation failed at H{horizon}")
        rows.append({"horizon": f"H{horizon}", **data})
    result = {
        "execution_status": "PASS",
        "method": "artifact-only valid-population coverage interpretation",
        "total_events": source["total_events"],
        "event_key_conservation": "PASS",
        "broker_history_completeness": "NOT_PROVEN",
        "horizons": rows,
        "interpretation": [
            "Each horizon retains a large but non-identical valid population; comparisons across horizons are not like-for-like.",
            "Exclusion increases with lookahead because more windows intersect unverified gaps.",
            "TP_FIRST/SL_FIRST/AMBIGUOUS_SAME_BAR/NO_RESOLUTION are diagnostic labels only, not trading performance or profitability evidence.",
        ],
        "strategy_performance_status": "NOT_EVALUATED",
        "order_logic_status": "NOT_APPROVED",
        "paf_status": "NOT_READY_FOR_ORDER_LOGIC",
        "profitability_claim": False,
    }
    root = Path(args.results_root); root.mkdir(parents=True, exist_ok=True)
    (root / "checkpoint_fa_valid_shadow_population_review.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = ["# Checkpoint FA Valid Shadow Population Review", "", "Diagnostic interpretation only; no strategy-performance conclusion.", ""]
    lines.extend(f"- {key}: `{value}`" for key, value in result.items() if key not in {"horizons", "interpretation"})
    lines.extend(f"- {item}" for item in result["interpretation"])
    lines.extend(f"- {row['horizon']}: `{row}`" for row in rows)
    (root / "checkpoint_fa_valid_shadow_population_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
