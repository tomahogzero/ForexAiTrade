# Backtest Plan

Backtests should use at least five years of history. Prefer eight to ten years where quality data is available.

## Data Quality

- Use real tick or high-quality tick mode where possible.
- Include realistic spread assumptions.
- Include slippage assumptions.
- Test symbols individually before considering portfolio behavior.

## Split

- Train and optimization period: discover candidate parameter areas.
- Validation period: reject fragile and overfit candidates.
- Out-of-sample period: estimate unseen performance.
- Demo forward test: verify behavior in current market conditions.

## Required Symbols

- EURUSD H1
- GBPUSD H1
- USDJPY H1
- XAUUSD H1

## Minimum Review

Every accepted parameter set must have positive net profit, acceptable drawdown, sufficient trade count, reasonable losing streaks, and stable behavior across validation and out-of-sample periods.
