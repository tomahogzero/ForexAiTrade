from __future__ import annotations

from dataclasses import dataclass

from mt5_report_parser import BacktestMetrics


@dataclass
class ScoreWeights:
    profit_factor: float = 22.0
    sharpe: float = 12.0
    net_profit: float = 12.0
    trade_count: float = 14.0
    drawdown_penalty: float = 22.0
    losing_streak_penalty: float = 10.0
    low_win_rate_penalty: float = 8.0


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def robustness_score(metrics: BacktestMetrics, weights: ScoreWeights | None = None) -> float:
    weights = weights or ScoreWeights()
    score = 0.0

    score += weights.profit_factor * clamp((metrics.profit_factor - 1.0) / 1.0, 0.0, 1.0)
    score += weights.sharpe * clamp(metrics.sharpe_ratio / 2.0, 0.0, 1.0)
    score += weights.net_profit if metrics.net_profit > 0 else -weights.net_profit
    score += weights.trade_count * clamp(metrics.trades / 250.0, 0.0, 1.0)

    dd = max(metrics.balance_drawdown_percent, metrics.equity_drawdown_percent)
    score -= weights.drawdown_penalty * clamp(dd / 25.0, 0.0, 1.5)
    score -= weights.losing_streak_penalty * clamp(metrics.consecutive_losses / 8.0, 0.0, 1.5)

    if metrics.win_rate_percent < 35.0:
        score -= weights.low_win_rate_penalty * clamp((35.0 - metrics.win_rate_percent) / 20.0, 0.0, 1.0)

    if metrics.trades < 100:
        score -= 15.0
    if dd > 20.0:
        score -= 15.0
    if metrics.profit_factor < 1.15:
        score -= 20.0

    return round(score, 2)
