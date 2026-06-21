from __future__ import annotations

import argparse
import csv
from pathlib import Path


def generate_markdown(ranked_csv: Path, output: Path, top_n: int) -> None:
    with ranked_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    accepted = [row for row in rows if row.get("accepted_for_forward_test") == "True"]
    lines = [
        "# ForexAiTrade Optimization Summary",
        "",
        "This report ranks parameter sets by robustness, not by raw historical profit.",
        "",
        "## Acceptance Rules",
        "",
        "- Net profit must be positive.",
        "- Profit factor must be at least 1.15.",
        "- Drawdown must be 20% or lower.",
        "- Trade count must be at least 100.",
        "- Maximum consecutive losses must be 8 or lower.",
        "",
        "## Top Ranked Sets",
        "",
        "| Rank | Score | Actual Symbol | Canonical Symbol | Source | Net Profit | PF | DD % | Trades | Loss Streak | Forward? |",
        "| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for idx, row in enumerate(rows[:top_n], start=1):
        dd = max(float(row.get("balance_drawdown_percent") or 0), float(row.get("equity_drawdown_percent") or 0))
        lines.append(
            f"| {idx} | {row.get('robustness_score')} | {row.get('actual_symbol', row.get('symbol', ''))} | "
            f"{row.get('canonical_symbol', row.get('symbol', ''))} | {Path(row.get('source', '')).name} | "
            f"{row.get('net_profit')} | {row.get('profit_factor')} | {dd:.2f} | "
            f"{row.get('trades')} | {row.get('consecutive_losses')} | {row.get('accepted_for_forward_test')} |"
        )

    lines.extend([
        "",
        "## Forward Test Candidates",
        "",
    ])

    if accepted:
        for row in accepted[:top_n]:
            lines.append(f"- `{Path(row.get('source', '')).name}` score `{row.get('robustness_score')}`")
    else:
        lines.append("- No parameter sets passed the current robustness gate.")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate markdown summary from ranked MT5 reports.")
    parser.add_argument("ranked_csv", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/optimization_summary.md"))
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()
    generate_markdown(args.ranked_csv, args.output, args.top)
    print(f"Wrote {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
