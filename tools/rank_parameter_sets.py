from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path

from mt5_report_parser import BacktestMetrics, parse_many
from robustness_score import robustness_score


def rank_reports(report_paths: list[Path]) -> list[dict[str, object]]:
    rows = []
    for metrics in parse_many(report_paths):
        row = asdict(metrics)
        row["robustness_score"] = robustness_score(metrics)
        row["accepted_for_forward_test"] = (
            metrics.net_profit > 0
            and metrics.profit_factor >= 1.15
            and max(metrics.balance_drawdown_percent, metrics.equity_drawdown_percent) <= 20.0
            and metrics.trades >= 100
            and metrics.consecutive_losses <= 8
        )
        rows.append(row)
    return sorted(rows, key=lambda item: float(item["robustness_score"]), reverse=True)


def write_ranked_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank MT5 backtest reports by robustness.")
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/ranked_parameter_sets.csv"))
    args = parser.parse_args()

    rows = rank_reports(args.reports)
    if not rows:
        raise SystemExit("No reports parsed.")
    write_ranked_csv(rows, args.output)
    print(f"Wrote {args.output} with {len(rows)} ranked rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
