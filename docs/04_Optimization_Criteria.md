# Optimization Criteria

Optimization must prefer robust and stable parameters over maximum historical profit.

## Primary Gates

- Profit factor at least 1.15.
- Maximum drawdown no higher than 20%.
- At least 100 trades over the test window.
- Maximum consecutive losses no higher than 8.
- Positive net profit.

## Robustness Score

The Python scoring pipeline rewards:

- Profit factor.
- Sharpe ratio.
- Positive net profit.
- Sufficient trade count.

It penalizes:

- High drawdown.
- Low trade count.
- Long losing streaks.
- Profit factor below the survival threshold.
- Low win rate.

## Stability Checks

Do not accept a parameter set just because it is the best row in a single optimization run. Prefer broad neighborhoods where nearby settings remain acceptable.

Use `tools/stability_analysis.py` on optimizer exports or ranked result CSV files to penalize groups where the best setting is much better than nearby settings. A sharp isolated peak is treated as fragile even when the single backtest looks profitable.
