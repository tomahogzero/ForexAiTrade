#!/usr/bin/env python3
"""Normalize offline PAF lookahead OHLC bar CSV schema.

This tool does not run MT5, does not run Strategy Tester, does not send
orders, and does not prove profitability. It only converts an exported OHLC
CSV into the strict schema expected by the offline PAF lookahead validator:

time,open,high,low,close
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


OUTPUT_COLUMNS = ["time", "open", "high", "low", "close"]
TIME_FORMATS = (
    "%Y.%m.%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y.%m.%d %H:%M",
    "%Y-%m-%d %H:%M",
    "%Y.%m.%d",
    "%Y-%m-%d",
)
DATE_FORMATS = ("%Y.%m.%d", "%Y-%m-%d")
TIME_ONLY_FORMATS = ("%H:%M:%S", "%H:%M")


def clean_column_name(value: str) -> str:
    text = (value or "").strip().lower()
    text = text.strip("<>")
    for token in (" ", "_", "-", "."):
        text = text.replace(token, "")
    return text


def detect_dialect(path: Path, delimiter: str) -> csv.Dialect:
    if delimiter != "auto":
        class ExplicitDialect(csv.excel):
            pass

        ExplicitDialect.delimiter = delimiter
        return ExplicitDialect

    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:8192]
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        return csv.excel


def read_csv(path: Path, delimiter: str) -> tuple[list[str], list[dict[str, str]], str]:
    if not path.exists():
        raise SystemExit(f"Missing raw CSV file: {path}")
    dialect = detect_dialect(path, delimiter)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, dialect=dialect)
        return list(reader.fieldnames or []), list(reader), dialect.delimiter


def normalize_column_map(fieldnames: list[str]) -> dict[str, str]:
    return {clean_column_name(name): name for name in fieldnames}


def pick_column(column_map: dict[str, str], explicit: str | None, candidates: list[str]) -> str | None:
    if explicit:
        key = clean_column_name(explicit)
        if key in column_map:
            return column_map[key]
        raise SystemExit(f"Requested column not found: {explicit}")

    for candidate in candidates:
        key = clean_column_name(candidate)
        if key in column_map:
            return column_map[key]
    return None


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_date_and_time(date_value: Any, time_value: Any) -> datetime | None:
    if date_value in (None, "") or time_value in (None, ""):
        return None
    date_text = str(date_value).strip()
    time_text = str(time_value).strip()
    for date_fmt in DATE_FORMATS:
        for time_fmt in TIME_ONLY_FORMATS:
            try:
                parsed_date = datetime.strptime(date_text, date_fmt)
                parsed_time = datetime.strptime(time_text, time_fmt)
                return datetime(
                    parsed_date.year,
                    parsed_date.month,
                    parsed_date.day,
                    parsed_time.hour,
                    parsed_time.minute,
                    parsed_time.second,
                )
            except ValueError:
                continue
    return parse_datetime(f"{date_text} {time_text}")


def validate_price(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    try:
        float(text)
    except ValueError:
        return None
    return text


def resolve_columns(args: argparse.Namespace, fieldnames: list[str]) -> dict[str, str | None]:
    column_map = normalize_column_map(fieldnames)
    date_column = pick_column(column_map, args.date_column, ["date", "<date>"])
    time_only_column = pick_column(column_map, args.time_only_column, ["time", "<time>"])
    time_column = pick_column(
        column_map,
        args.time_column,
        ["datetime", "date time", "date_time", "<date><time>"],
    )
    if args.time_column:
        time_column = pick_column(column_map, args.time_column, ["time"])
        date_column = None
        time_only_column = None
    elif date_column and time_only_column:
        time_column = None

    return {
        "time": time_column,
        "date": date_column,
        "time_only": time_only_column,
        "open": pick_column(column_map, args.open_column, ["open", "<open>"]),
        "high": pick_column(column_map, args.high_column, ["high", "<high>"]),
        "low": pick_column(column_map, args.low_column, ["low", "<low>"]),
        "close": pick_column(column_map, args.close_column, ["close", "<close>"]),
    }


def normalize_rows(
    rows: list[dict[str, str]],
    columns: dict[str, str | None],
) -> tuple[list[dict[str, str]], list[str], int]:
    missing = [name for name in ("open", "high", "low", "close") if not columns.get(name)]
    if not columns.get("time") and not (columns.get("date") and columns.get("time_only")):
        missing.append("time or date+time")
    if missing:
        return [], [f"missing required source columns: {', '.join(missing)}"], 0

    normalized: list[dict[str, str]] = []
    issues: list[str] = []
    invalid_rows = 0

    for row_index, row in enumerate(rows, start=2):
        if columns.get("time"):
            parsed_time = parse_datetime(row.get(columns["time"] or ""))
        else:
            parsed_time = parse_date_and_time(row.get(columns["date"] or ""), row.get(columns["time_only"] or ""))
        if parsed_time is None:
            invalid_rows += 1
            issues.append(f"row {row_index}: timestamp could not be parsed")
            continue

        output = {"time": parsed_time.strftime("%Y.%m.%d %H:%M:%S")}
        valid_prices = True
        for price_column in ("open", "high", "low", "close"):
            price = validate_price(row.get(columns[price_column] or ""))
            if price is None:
                valid_prices = False
                issues.append(f"row {row_index}: {price_column} could not be parsed as numeric")
                break
            output[price_column] = price
        if not valid_prices:
            invalid_rows += 1
            continue
        normalized.append(output)

    normalized.sort(key=lambda item: item["time"])
    if invalid_rows:
        issues.append(f"invalid rows detected: {invalid_rows}")
    if not normalized:
        issues.append("no normalized bars produced")
    return normalized, issues, invalid_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in OUTPUT_COLUMNS})


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# PAF Bars Schema Normalization Summary",
        "",
        "This is an offline schema-normalization summary. It does not run MT5, does not send orders, and does not prove profitability.",
        "",
        "## Verdict",
        "",
        f"`{summary['verdict']}`",
        "",
        "## Inputs",
        "",
        f"- Raw CSV: `{summary['raw_csv']}`",
        f"- Normalized CSV: `{summary['normalized_csv']}`",
        f"- Raw preserved copy: `{summary['raw_preserved_copy']}`",
        f"- Source symbol: `{summary['source_symbol']}`",
        f"- Source timeframe: `{summary['source_timeframe']}`",
        f"- Broker comparable: `{summary['broker_comparable']}`",
        "",
        "## Columns",
        "",
        f"- Input columns: `{', '.join(summary['input_columns'])}`",
        f"- Output columns: `{', '.join(summary['output_columns'])}`",
        f"- Delimiter detected: `{summary['delimiter_detected']}`",
        f"- Column mapping: `{json.dumps(summary['column_mapping'], ensure_ascii=False)}`",
        "",
        "## Rows",
        "",
        f"- Rows before: `{summary['row_count_before']}`",
        f"- Rows after: `{summary['row_count_after']}`",
        f"- Invalid rows: `{summary['invalid_rows']}`",
        "",
        "## Issues",
        "",
    ]
    if summary["issues"]:
        for issue in summary["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines += [
        "",
        "## Guardrails",
        "",
        "- Offline normalization only.",
        "- No MT5 run.",
        "- No Strategy Tester run.",
        "- No market orders or pending orders.",
        "- No OHLC price editing.",
        "- No missing-bar filling.",
        "- No optimization.",
        "- No profitability claim.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize(args: argparse.Namespace) -> dict[str, Any]:
    raw_csv = Path(args.raw_csv)
    output_csv = Path(args.output_csv)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)

    fieldnames, rows, delimiter_detected = read_csv(raw_csv, args.delimiter)
    columns = resolve_columns(args, fieldnames)
    normalized, issues, invalid_rows = normalize_rows(rows, columns)

    raw_copy = results_root / "paf_lookahead_bars_raw.csv"
    if raw_csv.resolve() != raw_copy.resolve():
        shutil.copyfile(raw_csv, raw_copy)

    if normalized and not issues:
        write_csv(output_csv, normalized)

    if args.source_symbol != "GOLD#" or args.source_timeframe.upper() != "H1":
        issues.append("source symbol/timeframe is not the expected GOLD# H1")
    if args.non_broker_comparable:
        issues.append("source data marked NON_BROKER_COMPARABLE")

    verdict = "PASS" if not issues else "FAIL"
    summary = {
        "verdict": verdict,
        "raw_csv": str(raw_csv),
        "normalized_csv": str(output_csv),
        "raw_preserved_copy": str(raw_copy),
        "source_symbol": args.source_symbol,
        "source_timeframe": args.source_timeframe,
        "broker_comparable": not args.non_broker_comparable,
        "input_columns": fieldnames,
        "output_columns": OUTPUT_COLUMNS,
        "delimiter_detected": delimiter_detected,
        "column_mapping": columns,
        "row_count_before": len(rows),
        "row_count_after": len(normalized) if verdict == "PASS" else 0,
        "invalid_rows": invalid_rows,
        "issues": issues,
        "guardrails": [
            "offline normalization only",
            "no MT5 run",
            "no Strategy Tester run",
            "no orders",
            "no OHLC price editing",
            "no missing-bar filling",
            "no optimization",
            "no profitability claim",
        ],
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize an offline PAF lookahead OHLC bars CSV schema.")
    parser.add_argument("--raw-csv", required=True)
    parser.add_argument("--output-csv", default="research/results/paf_lookahead_bars.csv")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--delimiter", default="auto", help="auto, comma, semicolon, tab, or a literal delimiter")
    parser.add_argument("--source-symbol", default="GOLD#")
    parser.add_argument("--source-timeframe", default="H1")
    parser.add_argument("--non-broker-comparable", action="store_true")
    parser.add_argument("--time-column")
    parser.add_argument("--date-column")
    parser.add_argument("--time-only-column")
    parser.add_argument("--open-column")
    parser.add_argument("--high-column")
    parser.add_argument("--low-column")
    parser.add_argument("--close-column")
    args = parser.parse_args()

    delimiter_aliases = {"comma": ",", "semicolon": ";", "tab": "\t"}
    args.delimiter = delimiter_aliases.get(args.delimiter.lower(), args.delimiter)

    summary = normalize(args)
    results_root = Path(args.results_root)
    (results_root / "paf_bars_schema_normalization_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_summary(results_root / "paf_bars_schema_normalization_summary.md", summary)

    print(f"Normalization verdict: {summary['verdict']}")
    print(f"Summary: {results_root / 'paf_bars_schema_normalization_summary.md'}")
    return 0 if summary["verdict"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
