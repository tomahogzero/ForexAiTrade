from __future__ import annotations

import argparse
import csv
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SmokeMetrics:
    source: str
    actual_symbol: str = ""
    canonical_symbol: str = ""
    timeframe: str = ""
    period: str = ""
    deposit: str = ""
    spread_mode: str = ""
    trades: str = ""
    profit_factor: str = ""
    max_drawdown: str = ""
    max_consecutive_losses: str = ""
    largest_loss: str = ""
    largest_win: str = ""
    parse_warning: str = ""


def canonical_symbol(actual: str) -> str:
    symbol = actual.strip()
    upper = symbol.upper()
    if upper.startswith("GOLD") or upper.startswith("XAU"):
        return "GOLD"
    if upper.endswith("#"):
        upper = upper[:-1]
    if len(upper) == 6 and upper.isalpha():
        return upper
    return upper


def clean_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</tr>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def first_match(text: str, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            return match.group(1).strip()
    return ""


def read_text(path: Path) -> str:
    for encoding in ("utf-16", "utf-8", "cp1252"):
        try:
            text = path.read_text(encoding=encoding, errors="ignore")
            if len(text.strip()) > 20:
                return text
        except OSError:
            pass
    return ""


def parse_html_or_text(path: Path) -> SmokeMetrics:
    raw = read_text(path)
    text = clean_html(raw)
    metrics = SmokeMetrics(source=str(path))

    metrics.actual_symbol = first_match(text, [r"Symbol\s+([A-Z0-9._#-]+)"])
    metrics.canonical_symbol = canonical_symbol(metrics.actual_symbol) if metrics.actual_symbol else ""
    metrics.timeframe = first_match(text, [r"Period\s+([A-Z0-9]+)", r"Timeframe\s+([A-Z0-9]+)"])
    metrics.deposit = first_match(text, [r"Initial Deposit\s+([-\d.,\s]+)", r"Deposit\s+([-\d.,\s]+)"])
    metrics.trades = first_match(text, [r"Total Trades\s+(\d+)", r"Trades\s+(\d+)"])
    metrics.profit_factor = first_match(text, [r"Profit Factor\s+([-\d.,\s]+)"])
    metrics.max_drawdown = first_match(text, [
        r"Equity Drawdown Relative\s+([-\d.,\s%()]+)",
        r"Balance Drawdown Relative\s+([-\d.,\s%()]+)",
        r"Maximal Drawdown\s+([-\d.,\s%()]+)",
    ])
    metrics.max_consecutive_losses = first_match(text, [
        r"Maximum consecutive losses\s+(\d+)",
        r"Max consecutive losses\s+(\d+)",
    ])
    metrics.largest_loss = first_match(text, [r"Largest loss trade\s+([-\d.,\s]+)"])
    metrics.largest_win = first_match(text, [r"Largest profit trade\s+([-\d.,\s]+)"])

    if not any([metrics.actual_symbol, metrics.trades, metrics.profit_factor]):
        metrics.parse_warning = "Could not identify standard MT5 report fields. Export MT5 Strategy Tester report as HTML/XML/CSV."

    return metrics


def parse_csv(path: Path) -> SmokeMetrics:
    metrics = SmokeMetrics(source=str(path))
    with path.open("r", encoding="utf-8-sig", newline="", errors="ignore") as handle:
        rows = list(csv.reader(handle))

    flat = " ".join(" ".join(row) for row in rows)
    parsed = parse_html_or_text_from_text(path, flat)
    return parsed


def parse_html_or_text_from_text(path: Path, raw: str) -> SmokeMetrics:
    text = clean_html(raw)
    temp = SmokeMetrics(source=str(path))
    temp.actual_symbol = first_match(text, [r"Symbol\s+([A-Z0-9._#-]+)"])
    temp.canonical_symbol = canonical_symbol(temp.actual_symbol) if temp.actual_symbol else ""
    temp.timeframe = first_match(text, [r"Period\s+([A-Z0-9]+)", r"Timeframe\s+([A-Z0-9]+)"])
    temp.trades = first_match(text, [r"Total Trades\s+(\d+)", r"Trades\s+(\d+)"])
    temp.profit_factor = first_match(text, [r"Profit Factor\s+([-\d.,\s]+)"])
    temp.max_drawdown = first_match(text, [r"Drawdown\s+([-\d.,\s%()]+)"])
    if not any([temp.actual_symbol, temp.trades, temp.profit_factor]):
        temp.parse_warning = "CSV did not contain recognizable MT5 summary labels."
    return temp


def parse_xml(path: Path) -> SmokeMetrics:
    metrics = SmokeMetrics(source=str(path))
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        metrics.parse_warning = f"XML parse failed: {exc}"
        return metrics

    text = " ".join(node.text or "" for node in root.iter())
    parsed = parse_html_or_text_from_text(path, text)
    return parsed


def parse_report(path: Path) -> SmokeMetrics:
    suffix = path.suffix.lower()
    if suffix == ".xml":
        return parse_xml(path)
    if suffix == ".csv":
        return parse_csv(path)
    if suffix in {".html", ".htm", ".txt"}:
        return parse_html_or_text(path)
    metrics = SmokeMetrics(source=str(path))
    metrics.parse_warning = "Unsupported file extension. Expected .html, .htm, .xml, .csv, or .txt."
    return metrics


def write_markdown(metrics: SmokeMetrics, output: Path) -> None:
    lines = [
        "# Backtest Smoke Report",
        "",
        "This summary is for behavior verification only. It is not optimization and not profitability proof.",
        "",
        "## Parsed Metrics",
        "",
        f"- Source: `{metrics.source}`",
        f"- Actual symbol: {metrics.actual_symbol or 'UNKNOWN'}",
        f"- Canonical symbol: {metrics.canonical_symbol or 'UNKNOWN'}",
        f"- Timeframe: {metrics.timeframe or 'UNKNOWN'}",
        f"- Period: {metrics.period or 'UNKNOWN'}",
        f"- Deposit: {metrics.deposit or 'UNKNOWN'}",
        f"- Spread mode: {metrics.spread_mode or 'UNKNOWN'}",
        f"- Number of trades: {metrics.trades or 'UNKNOWN'}",
        f"- Profit factor: {metrics.profit_factor or 'UNKNOWN'}",
        f"- Max drawdown: {metrics.max_drawdown or 'UNKNOWN'}",
        f"- Max consecutive losses: {metrics.max_consecutive_losses or 'UNKNOWN'}",
        f"- Largest loss: {metrics.largest_loss or 'UNKNOWN'}",
        f"- Largest win: {metrics.largest_win or 'UNKNOWN'}",
        "",
        "## Manual Review Required",
        "",
        "- Check Journal for symbol diagnostics.",
        "- Check Journal for tester-only gate behavior.",
        "- Check Journal for risk block reasons.",
        "- Confirm no runaway orders.",
        "- Confirm lot sizing did not exceed configured risk.",
        "",
        "## Verdict",
        "",
        "Verdict: PASS / FAIL",
        "",
    ]

    if metrics.parse_warning:
        lines.extend(["## Parse Warning", "", metrics.parse_warning, ""])

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown smoke-test summary from an exported MT5 report.")
    parser.add_argument("report", type=Path)
    parser.add_argument("--output", type=Path, default=Path("reports/backtest_smoke_report.md"))
    args = parser.parse_args()

    metrics = parse_report(args.report)
    write_markdown(metrics, args.output)
    print(f"Wrote {args.output}")
    if metrics.parse_warning:
        print(metrics.parse_warning)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
