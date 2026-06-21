#!/usr/bin/env python3
"""Build trade-level ledgers from MT5 HTML reports and ForexAiTrade artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any


TRADE_FIELDS = [
    "run_id",
    "case_id",
    "base_case_id",
    "phase",
    "symbol",
    "timeframe",
    "direction",
    "volume",
    "open_time",
    "close_time",
    "duration_minutes",
    "open_price",
    "close_price",
    "sl",
    "tp",
    "profit",
    "commission",
    "swap",
    "total_profit",
    "exit_reason",
    "magic_number",
    "entry_comment",
    "exit_comment",
    "open_deal",
    "close_deal",
]


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-16", "utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def run_is_successful(run_root: Path) -> bool:
    status = load_json(run_root / "run_status.json")
    if not isinstance(status, list):
        return False
    return bool(status) and all(row.get("execution_status") == "PASS" for row in status)


def latest_successful_run_id(runs_root: Path) -> str | None:
    successful = [path.name for path in runs_root.glob("run_*") if path.is_dir() and run_is_successful(path)]
    if successful:
        return sorted(successful)[-1]
    all_runs = [path.name for path in runs_root.glob("run_*") if path.is_dir()]
    return sorted(all_runs)[-1] if all_runs else None


def resolve_run_id(runs_root: Path, run_id: str | None) -> str:
    selected = run_id or latest_successful_run_id(runs_root)
    if not selected:
        raise SystemExit(f"No run directories found under {runs_root}")
    if not (runs_root / selected).exists():
        raise SystemExit(f"RunId not found: {selected}")
    return selected


def report_hash(case_dir: Path) -> str | None:
    report = case_dir / "mt5_report.htm"
    if not report.exists():
        return None
    digest = hashlib.sha256()
    with report.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duplicate_signature(case_dir: Path) -> tuple[str, ...] | None:
    case = load_json(case_dir / "case.json")
    if not isinstance(case, dict) or not case:
        return None
    period = case.get("period") or {}
    return (
        str(case.get("base_case_id") or case.get("case_id") or case_dir.name),
        str(case.get("phase") or ""),
        str(case.get("actual_symbol") or ""),
        str(case.get("canonical_symbol") or ""),
        str(case.get("timeframe") or ""),
        str(period.get("from") or ""),
        str(period.get("to") or ""),
    )


def clean_cell(value: str) -> str:
    value = re.sub(r"(?is)<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def table_after_title(text: str, title: str) -> str:
    match = re.search(rf"(?is)<b>\s*{re.escape(title)}\s*</b>", text)
    if not match:
        return ""
    table_end = text.find("</table>", match.end())
    if table_end == -1:
        return text[match.end():]
    return text[match.end():table_end]


def rows_from_table(table: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in re.findall(r"(?is)<tr\b[^>]*>(.*?)</tr>", table):
        cells = [clean_cell(cell) for cell in re.findall(r"(?is)<t[dh]\b[^>]*>(.*?)</t[dh]>", tr)]
        if cells:
            rows.append(cells)
    return rows


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"[-+]?\d[\d,\s]*\.?\d*", text)
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def fmt_time(value: datetime | None) -> str | None:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


def normalize_exit_reason(comment: str) -> str:
    text = (comment or "").strip().lower()
    if text.startswith("sl"):
        return "SL"
    if text.startswith("tp"):
        return "TP"
    if "stop" in text:
        return "STOP_OR_SL"
    if "take" in text:
        return "TP"
    if text:
        return "OTHER"
    return "UNKNOWN"


def parse_orders(text: str) -> dict[str, dict[str, Any]]:
    orders: dict[str, dict[str, Any]] = {}
    for cells in rows_from_table(table_after_title(text, "Orders")):
        if len(cells) < 11 or cells[0].lower() == "open time":
            continue
        order_id = cells[1]
        volume = parse_number(cells[4].split("/")[0] if len(cells) > 4 else "")
        orders[order_id] = {
            "open_time": cells[0],
            "order": order_id,
            "symbol": cells[2],
            "type": cells[3].lower(),
            "volume": volume,
            "price": parse_number(cells[5]),
            "sl": parse_number(cells[6]),
            "tp": parse_number(cells[7]),
            "time": cells[8],
            "state": cells[9],
            "comment": cells[10],
        }
    return orders


def parse_deals(text: str) -> list[dict[str, Any]]:
    deals: list[dict[str, Any]] = []
    for cells in rows_from_table(table_after_title(text, "Deals")):
        if len(cells) < 13 or cells[0].lower() == "time":
            continue
        deals.append({
            "time": cells[0],
            "deal": cells[1],
            "symbol": cells[2],
            "type": cells[3].lower(),
            "direction": cells[4].lower(),
            "volume": parse_number(cells[5]),
            "price": parse_number(cells[6]),
            "order": cells[7],
            "commission": parse_number(cells[8]) or 0.0,
            "swap": parse_number(cells[9]) or 0.0,
            "profit": parse_number(cells[10]) or 0.0,
            "balance": parse_number(cells[11]),
            "comment": cells[12],
        })
    return deals


def opposite_direction(direction: str) -> str:
    return "sell" if direction == "buy" else "buy"


def build_trades(case_dir: Path) -> tuple[list[dict[str, Any]], list[str]]:
    report = case_dir / "mt5_report.htm"
    if not report.exists():
        return [], ["missing mt5_report.htm"]
    text = read_text(report)
    orders = parse_orders(text)
    deals = parse_deals(text)
    case_data = load_json(case_dir / "case.json")
    parsed_data = load_json(case_dir / "parsed_result.json")
    case = case_data if isinstance(case_data, dict) else {}
    parsed = parsed_data if isinstance(parsed_data, dict) else {}
    warnings: list[str] = []
    open_positions: list[dict[str, Any]] = []
    trades: list[dict[str, Any]] = []

    for deal in deals:
        if deal["type"] == "balance":
            continue
        if deal["direction"] == "in":
            order = orders.get(str(deal.get("order")), {})
            open_positions.append({
                "deal": deal,
                "order": order,
            })
            continue
        if deal["direction"] != "out":
            continue

        match_index = None
        for idx, pos in enumerate(open_positions):
            entry = pos["deal"]
            if entry.get("symbol") == deal.get("symbol") and entry.get("type") == opposite_direction(deal.get("type", "")):
                match_index = idx
                break
        if match_index is None and open_positions:
            match_index = 0
        if match_index is None:
            warnings.append(f"unmatched close deal {deal.get('deal')}")
            continue

        pos = open_positions.pop(match_index)
        entry = pos["deal"]
        order = pos.get("order") or {}
        open_time = parse_time(entry.get("time"))
        close_time = parse_time(deal.get("time"))
        duration_minutes = None
        if open_time and close_time:
            duration_minutes = round((close_time - open_time).total_seconds() / 60.0, 2)
        profit = deal.get("profit") or 0.0
        commission = deal.get("commission") or 0.0
        swap = deal.get("swap") or 0.0
        trades.append({
            "run_id": case.get("run_id") or case_dir.parent.name,
            "case_id": case.get("case_id") or case_dir.name,
            "base_case_id": case.get("base_case_id"),
            "phase": case.get("phase"),
            "symbol": case.get("actual_symbol") or parsed.get("symbol") or deal.get("symbol"),
            "timeframe": case.get("timeframe") or parsed.get("timeframe"),
            "direction": entry.get("type"),
            "volume": entry.get("volume"),
            "open_time": fmt_time(open_time),
            "close_time": fmt_time(close_time),
            "duration_minutes": duration_minutes,
            "open_price": entry.get("price"),
            "close_price": deal.get("price"),
            "sl": order.get("sl"),
            "tp": order.get("tp"),
            "profit": profit,
            "commission": commission,
            "swap": swap,
            "total_profit": round(profit + commission + swap, 2),
            "exit_reason": normalize_exit_reason(deal.get("comment", "")),
            "magic_number": None,
            "entry_comment": entry.get("comment") or order.get("comment"),
            "exit_comment": deal.get("comment"),
            "open_deal": entry.get("deal"),
            "close_deal": deal.get("deal"),
        })

    if open_positions:
        warnings.append(f"{len(open_positions)} open entries were not paired with close deals")
    if trades and all(t.get("magic_number") is None for t in trades):
        warnings.append("magic number is not available in exported MT5 HTML deals/orders tables")
    if trades and all(t.get("sl") is None and t.get("tp") is None for t in trades):
        warnings.append("SL/TP values could not be mapped from Orders table")
    return trades, warnings


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in TRADE_FIELDS})


def safe_mean(values: list[float]) -> float | None:
    return round(mean(values), 4) if values else None


def max_consecutive_losses(trades: list[dict[str, Any]]) -> int:
    best = 0
    current = 0
    for trade in sorted(trades, key=lambda x: x.get("close_time") or ""):
        if (trade.get("total_profit") or 0) < 0:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def summarize_trades(trades: list[dict[str, Any]]) -> dict[str, Any]:
    profits = [float(t.get("total_profit") or 0.0) for t in trades]
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]
    durations = [float(t["duration_minutes"]) for t in trades if t.get("duration_minutes") is not None]
    exit_counts = Counter(str(t.get("exit_reason") or "UNKNOWN") for t in trades)
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    return {
        "trades": len(trades),
        "net_profit": round(sum(profits), 2),
        "win_rate_pct": round((len(wins) / len(trades)) * 100.0, 2) if trades else None,
        "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss > 0 else None,
        "average_win": safe_mean(wins),
        "average_loss": safe_mean(losses),
        "largest_win": max(wins) if wins else None,
        "largest_loss": min(losses) if losses else None,
        "average_holding_minutes": safe_mean(durations),
        "median_holding_minutes": sorted(durations)[len(durations) // 2] if durations else None,
        "quick_trades_under_60m": sum(1 for d in durations if d < 60),
        "long_trades_over_24h": sum(1 for d in durations if d > 1440),
        "max_consecutive_losses": max_consecutive_losses(trades),
        "exit_counts": dict(exit_counts),
    }


def write_case_summary(path: Path, trades: list[dict[str, Any]], warnings: list[str]) -> None:
    summary = summarize_trades(trades)
    lines = [
        f"# Trade Ledger Summary: {trades[0].get('case_id') if trades else path.parent.name}",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in summary.items():
        lines.append(f"| {key} | {json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else value} |")
    lines += [
        "",
        "## Limitations",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- No material parser limitations detected for this case.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def selected_case_dirs(runs_root: Path, run_id: str) -> list[Path]:
    case_dirs: list[Path] = []
    run_root = runs_root / run_id
    if not run_root.exists():
        return case_dirs
    for case_dir in sorted(run_root.iterdir()):
        if not case_dir.is_dir():
            continue
        if (case_dir / "case.json").exists():
            case_dirs.append(case_dir)
    return case_dirs


def detect_duplicates(runs_root: Path, selected_run_id: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for case_dir in sorted(runs_root.glob("run_*/*")):
        if not case_dir.is_dir() or not (case_dir / "case.json").exists():
            continue
        signature = duplicate_signature(case_dir)
        if not signature:
            continue
        grouped[signature].append({
            "run_id": case_dir.parent.name,
            "case_dir": str(case_dir),
            "report_hash": report_hash(case_dir),
            "selected": case_dir.parent.name == selected_run_id,
        })
    duplicates = []
    for signature, sources in sorted(grouped.items()):
        if len(sources) <= 1:
            continue
        duplicates.append({
            "signature": {
                "base_case_id": signature[0],
                "phase": signature[1],
                "actual_symbol": signature[2],
                "canonical_symbol": signature[3],
                "timeframe": signature[4],
                "period_from": signature[5],
                "period_to": signature[6],
            },
            "sources": sources,
        })
    return duplicates


def write_aggregate_summary(path: Path, all_rows: list[dict[str, Any]], case_summaries: list[dict[str, Any]], selected_run_id: str, duplicate_count: int) -> None:
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        by_case[str(row.get("base_case_id"))].append(row)
    lines = [
        "# Trade-Level Diagnostics Summary",
        "",
        f"Selected RunId: `{selected_run_id}`",
        "",
        "This summary uses existing MT5 HTML reports only. No MT5 run was performed. Main tables are scoped to the selected run only.",
        "",
        "| Case | Trades | Net Profit | Win Rate % | PF | Avg Hold Min | Max Consecutive Losses | Exit Counts |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for case_id, trades in sorted(by_case.items()):
        summary = summarize_trades(trades)
        lines.append(
            f"| {case_id} | {summary['trades']} | {summary['net_profit']} | {summary['win_rate_pct']} | "
            f"{summary['profit_factor']} | {summary['average_holding_minutes']} | {summary['max_consecutive_losses']} | "
            f"{json.dumps(summary['exit_counts'], ensure_ascii=False).replace('|', '/')} |"
        )
    lines += [
        "",
        "## Data Limitations",
        "",
        "- MT5 HTML report gives deal/order history, but not a reliable magic-number column.",
        "- Exit reason is inferred from close deal comments such as `sl` and `tp`.",
        "- Trailing stop or breakeven movement is not directly visible unless future EA logs explicitly record position modification events.",
        f"- Duplicate case/phase reports detected outside the selected scope: {duplicate_count}. They are recorded separately in `duplicates_detected.json` and are not merged into this table.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-root", default="research/runs")
    parser.add_argument("--results-root", default="research/results")
    parser.add_argument("--run-id")
    parser.add_argument("--latest-run", action="store_true")
    args = parser.parse_args()

    runs_root = Path(args.runs_root)
    results_root = Path(args.results_root)
    results_root.mkdir(parents=True, exist_ok=True)
    selected_run_id = resolve_run_id(runs_root, None if args.latest_run else args.run_id)
    duplicates = detect_duplicates(runs_root, selected_run_id)
    (results_root / "duplicates_detected.json").write_text(json.dumps({
        "selected_run_id": selected_run_id,
        "duplicates": duplicates,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    all_trades: list[dict[str, Any]] = []
    case_summaries: list[dict[str, Any]] = []

    for case_dir in selected_case_dirs(runs_root, selected_run_id):
        trades, warnings = build_trades(case_dir)
        all_trades.extend(trades)
        case_summaries.append({
            "case_dir": str(case_dir),
            "warnings": warnings,
            **summarize_trades(trades),
        })
        write_csv(case_dir / "trade_ledger.csv", trades)
        (case_dir / "trade_ledger.json").write_text(json.dumps(trades, indent=2, ensure_ascii=False), encoding="utf-8")
        write_case_summary(case_dir / "trade_ledger_summary.md", trades, warnings)

    write_aggregate_summary(results_root / "trade_level_summary.md", all_trades, case_summaries, selected_run_id, len(duplicates))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
