from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class BacktestMetrics:
    source: str
    actual_symbol: str = ""
    canonical_symbol: str = ""
    symbol: str = ""
    timeframe: str = ""
    net_profit: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0
    balance_drawdown_percent: float = 0.0
    equity_drawdown_percent: float = 0.0
    trades: int = 0
    win_rate_percent: float = 0.0
    consecutive_losses: int = 0
    sharpe_ratio: float = 0.0


NUMBER_RE = re.compile(r"[-+]?\d+(?:[,\s]\d{3})*(?:\.\d+)?|[-+]?\d+(?:\.\d+)?")


def canonical_symbol(
    actual_symbol: str,
    broker_suffix: str = "#",
    broker_gold_symbol: str = "GOLDm#",
    gold_canonical: str = "GOLD",
) -> str:
    actual = actual_symbol.strip()
    upper = actual.upper()
    gold = broker_gold_symbol.strip().upper()
    canonical_gold = gold_canonical.strip().upper() or "GOLD"

    if gold and upper == gold:
        return canonical_gold
    if upper.startswith("GOLD") or upper.startswith("XAU"):
        return canonical_gold
    if broker_suffix and actual.endswith(broker_suffix):
        actual = actual[: -len(broker_suffix)]
    if actual.endswith("#"):
        actual = actual[:-1]
    if len(actual) == 6 and actual.isalpha():
        return actual.upper()
    return upper


def _number(value: str) -> float:
    match = NUMBER_RE.search(value.replace("&nbsp;", " "))
    if not match:
        return 0.0
    return float(match.group(0).replace(",", "").replace(" ", ""))


def _clean_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</tr>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text)


def parse_report(path: Path) -> BacktestMetrics:
    raw = path.read_text(encoding="utf-16", errors="ignore")
    if len(raw.strip()) < 20:
        raw = path.read_text(encoding="utf-8", errors="ignore")
    text = _clean_html(raw)
    metrics = BacktestMetrics(source=str(path))

    patterns = {
        "net_profit": r"Total Net Profit\s+([-\d.,\s]+)",
        "gross_profit": r"Gross Profit\s+([-\d.,\s]+)",
        "gross_loss": r"Gross Loss\s+([-\d.,\s]+)",
        "profit_factor": r"Profit Factor\s+([-\d.,\s]+)",
        "expected_payoff": r"Expected Payoff\s+([-\d.,\s]+)",
        "balance_drawdown_percent": r"Balance Drawdown Relative\s+[-\d.,\s]+\s+\(([-\d.,\s]+)%",
        "equity_drawdown_percent": r"Equity Drawdown Relative\s+[-\d.,\s]+\s+\(([-\d.,\s]+)%",
        "trades": r"Total Trades\s+(\d+)",
        "win_rate_percent": r"Profit Trades\s+\d+\s+\(([-\d.,\s]+)%",
        "consecutive_losses": r"Maximum consecutive losses\s+\d+\s+\([-\d.,\s]+\)\s+(\d+)",
        "sharpe_ratio": r"Sharpe Ratio\s+([-\d.,\s]+)",
    }

    for field, pattern in patterns.items():
        match = re.search(pattern, text, flags=re.I)
        if not match:
            continue
        value = _number(match.group(1))
        if field in {"trades", "consecutive_losses"}:
            setattr(metrics, field, int(value))
        else:
            setattr(metrics, field, value)

    symbol_match = re.search(r"Symbol\s+([A-Z0-9._#-]+)", text, flags=re.I)
    if symbol_match:
        metrics.actual_symbol = symbol_match.group(1)
        metrics.canonical_symbol = canonical_symbol(metrics.actual_symbol)
        metrics.symbol = metrics.canonical_symbol
    period_match = re.search(r"Period\s+([A-Z0-9]+)", text, flags=re.I)
    if period_match:
        metrics.timeframe = period_match.group(1)

    return metrics


def parse_many(paths: Iterable[Path]) -> list[BacktestMetrics]:
    return [parse_report(path) for path in paths]


def write_csv(metrics: list[BacktestMetrics], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(metrics[0]).keys()))
        writer.writeheader()
        for row in metrics:
            writer.writerow(asdict(row))


def write_json(metrics: list[BacktestMetrics], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps([asdict(row) for row in metrics], indent=2), encoding="utf-8")
