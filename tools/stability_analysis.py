from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean, pstdev


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def analyze_stability(input_csv: Path, output_csv: Path, score_column: str, group_columns: list[str]) -> None:
    with input_csv.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit("No rows found.")

    groups: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in rows:
        key = tuple(row.get(column, "") for column in group_columns)
        groups.setdefault(key, []).append(row)

    output_rows = []
    for key, grouped_rows in groups.items():
        scores = [_as_float(row.get(score_column)) for row in grouped_rows]
        avg_score = mean(scores)
        dispersion = pstdev(scores) if len(scores) > 1 else 0.0
        best_score = max(scores)
        stability_penalty = min(30.0, dispersion + max(0.0, best_score - avg_score) * 0.35)

        representative = max(grouped_rows, key=lambda row: _as_float(row.get(score_column)))
        result = dict(representative)
        result["group_size"] = len(grouped_rows)
        result["group_average_score"] = round(avg_score, 2)
        result["group_score_dispersion"] = round(dispersion, 2)
        result["stability_penalty"] = round(stability_penalty, 2)
        result["stability_adjusted_score"] = round(best_score - stability_penalty, 2)

        for column, value in zip(group_columns, key):
            result[f"group_{column}"] = value

        output_rows.append(result)

    output_rows.sort(key=lambda row: _as_float(row.get("stability_adjusted_score")), reverse=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames: list[str] = []
    for row in output_rows:
        for field in row.keys():
            if field not in fieldnames:
                fieldnames.append(field)

    with output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Penalize unstable optimization neighborhoods.")
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/stability_adjusted_parameter_sets.csv"))
    parser.add_argument("--score-column", default="robustness_score")
    parser.add_argument(
        "--group-columns",
        nargs="+",
        required=True,
        help="Parameter columns that define a neighborhood, for example symbol timeframe risk_bucket.",
    )
    args = parser.parse_args()
    analyze_stability(args.input_csv, args.output, args.score_column, args.group_columns)
    print(f"Wrote {args.output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
