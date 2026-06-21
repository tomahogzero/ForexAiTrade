#!/usr/bin/env python3
"""Parse MT5 research reports into normalized JSON.

The parser is deliberately tolerant: unknown/localized labels become nulls
instead of hard failures. It validates metadata against case.json when present.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


FIELD_ALIASES = {
    "symbol": ["symbol", "สัญลักษณ์"],
    "timeframe": ["period", "timeframe", "ระยะเวลา"],
    "deposit": ["initial deposit", "deposit", "เงินฝาก"],
    "net_profit": ["total net profit", "net profit", "profit", "กำไรสุทธิ"],
    "profit_factor": ["profit factor"],
    "expected_payoff": ["expected payoff"],
    "absolute_drawdown": ["absolute drawdown"],
    "max_drawdown": ["maximal drawdown", "max drawdown", "equity drawdown maximal"],
    "relative_drawdown": ["relative drawdown", "equity drawdown relative"],
    "total_trades": ["total trades", "trades total"],
    "long_trades": ["long trades"],
    "short_trades": ["short trades"],
    "win_rate": ["profit trades", "win rate"],
    "largest_win": ["largest profit trade", "largest win"],
    "largest_loss": ["largest loss trade", "largest loss"],
    "consecutive_losses": ["max consecutive losses", "consecutive loss", "maximum consecutive losses"],
}


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-16", "utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def normalize_key(value: str) -> str:
    value = html.unescape(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" :\t\r\n")
    return value


def parse_number(value: str | None) -> float | int | None:
    if value is None:
        return None
    text = html.unescape(str(value)).strip()
    if not text:
        return None
    pct = "%" in text
    text = re.sub(r"\([^)]*\)", "", text)
    text = text.replace("%", "")
    match = re.search(r"[-+]?\d[\d,\s]*\.?\d*", text)
    if not match:
        return None
    number = match.group(0).replace(",", "").replace(" ", "")
    try:
        val = float(number)
    except ValueError:
        return None
    if not pct and val.is_integer():
        return int(val)
    return val


def strip_tags(text: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</tr>", "\n", text)
    text = re.sub(r"(?is)</td>", "\t", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    return html.unescape(text)


def td_cells_from_html(text: str) -> list[str]:
    cells: list[str] = []
    for match in re.finditer(r"(?is)<td\b[^>]*>(.*?)</td>", text):
        value = re.sub(r"(?is)<(script|style).*?</\1>", " ", match.group(1))
        value = re.sub(r"(?is)<[^>]+>", " ", value)
        value = html.unescape(value)
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            cells.append(value)
    return cells


def pairs_from_html_cells(text: str) -> dict[str, str]:
    cells = td_cells_from_html(text)
    pairs: dict[str, str] = {}
    for i, cell in enumerate(cells[:-1]):
        if not cell.strip().endswith(":"):
            continue
        key = normalize_key(cell)
        value = cells[i + 1].strip()
        if value and normalize_key(value) != key:
            pairs.setdefault(key, value)
    return pairs


def pairs_from_text(text: str) -> dict[str, str]:
    clean = strip_tags(text) if "<" in text and ">" in text else html.unescape(text)
    pairs: dict[str, str] = {}
    for line in clean.splitlines():
        parts = [p.strip() for p in re.split(r"\t{1,}| {2,}", line) if p.strip()]
        if len(parts) >= 2:
            for i in range(0, len(parts) - 1, 2):
                key = normalize_key(parts[i])
                if key and key not in pairs:
                    pairs[key] = parts[i + 1].strip()
        else:
            m = re.match(r"^\s*([^:]{2,80})\s*:\s*(.+?)\s*$", line)
            if m:
                key = normalize_key(m.group(1))
                pairs.setdefault(key, m.group(2).strip())
    return pairs


def pairs_from_xml(text: str) -> dict[str, str]:
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return {}
    pairs: dict[str, str] = {}
    for elem in root.iter():
        children = list(elem)
        if len(children) >= 2:
            key_text = "".join(children[0].itertext()).strip()
            val_text = "".join(children[1].itertext()).strip()
            if key_text and val_text:
                pairs.setdefault(normalize_key(key_text), val_text)
        if elem.attrib:
            for k, v in elem.attrib.items():
                pairs.setdefault(normalize_key(k), v)
    return pairs


def extract_field(pairs: dict[str, str], canonical: str) -> Any:
    aliases = FIELD_ALIASES[canonical]
    for key, value in pairs.items():
        if any(alias in key for alias in aliases):
            if canonical in {"symbol", "timeframe"}:
                return value
            return parse_number(value)
    return None


def normalize_timeframe_and_period(result: dict[str, Any]) -> None:
    timeframe = result.get("timeframe")
    result["report_period_from"] = None
    result["report_period_to"] = None
    if not timeframe:
        return

    text = str(timeframe).strip()
    match = re.match(r"^([A-Za-z0-9]+)\s*\((\d{4})[.\-](\d{2})[.\-](\d{2})\s*-\s*(\d{4})[.\-](\d{2})[.\-](\d{2})\)", text)
    if match:
        result["timeframe"] = match.group(1).upper()
        result["report_period_from"] = f"{match.group(2)}-{match.group(3)}-{match.group(4)}"
        result["report_period_to"] = f"{match.group(5)}-{match.group(6)}-{match.group(7)}"
        return

    clean = re.match(r"^([A-Za-z0-9]+)", text)
    if clean:
        result["timeframe"] = clean.group(1).upper()


def parse_report(report_path: Path) -> dict[str, Any]:
    text = read_text(report_path)
    pairs = pairs_from_xml(text) if report_path.suffix.lower() == ".xml" else {}
    pairs.update(pairs_from_text(text))
    if "<td" in text.lower():
        pairs.update(pairs_from_html_cells(text))
    result = {field: extract_field(pairs, field) for field in FIELD_ALIASES}
    if result.get("relative_drawdown") is None:
        relative_values: list[float] = []
        for label in ("Balance Drawdown Relative", "Equity Drawdown Relative", "Relative Drawdown"):
            pattern = rf"{re.escape(label)}\s*:?\s*(?:</td>\s*<td[^>]*>\s*)?(?:<b>)?\s*([-+]?\d[\d,\s]*\.?\d*)\s*%"
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                value = parse_number(match.group(1) + "%")
                if isinstance(value, (int, float)):
                    relative_values.append(float(value))
        if relative_values:
            result["relative_drawdown"] = max(relative_values)
    result["drawdown_relative"] = result.get("relative_drawdown")
    normalize_timeframe_and_period(result)
    result["source_report"] = str(report_path)
    result["raw_pair_count"] = len(pairs)
    return result


def validate_metadata(parsed: dict[str, Any], case: dict[str, Any] | None) -> tuple[bool | None, list[str]]:
    if not case:
        return None, []
    mismatches: list[str] = []
    symbol = parsed.get("symbol")
    timeframe = parsed.get("timeframe")
    if symbol and str(case.get("actual_symbol", "")).lower() not in str(symbol).lower():
        mismatches.append(f"symbol report={symbol} expected={case.get('actual_symbol')}")
    if timeframe and str(case.get("timeframe", "")).lower() not in str(timeframe).lower():
        mismatches.append(f"timeframe report={timeframe} expected={case.get('timeframe')}")
    return len(mismatches) == 0, mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--case")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        return 2

    parsed = parse_report(report_path)
    case = None
    if args.case:
        case = json.loads(Path(args.case).read_text(encoding="utf-8-sig"))
    metadata_match, mismatches = validate_metadata(parsed, case)
    parsed["metadata_match"] = metadata_match
    parsed["metadata_mismatches"] = mismatches
    parsed["case"] = case

    Path(args.output).write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
