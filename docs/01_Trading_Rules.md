# Trading Rules

ForexAiTrade trades only when the market regime and risk manager both permit action.

## Regime-Based Strategy Selection

- Trend regime: use trend following.
- Breakout regime: use breakout strategy.
- Sideway regime: use mean reversion.
- Unsafe or mixed regime: do not trade.

## Trend Following

The trend strategy requires fast EMA and slow EMA alignment, a meaningful EMA slope, and a pullback toward the pullback EMA. Stops and targets are ATR-based.

## Breakout

The breakout strategy requires a close beyond the recent range plus an ATR buffer. Stops and targets are ATR-based.

## Mean Reversion

The mean reversion strategy works only in sideway conditions. It looks for Bollinger Band extremes confirmed by RSI. Stops and targets are ATR-based.

## Execution Rules

- Trade only on a new signal timeframe bar by default.
- Allow only one open EA position per symbol by default.
- Block trading when spread exceeds the configured limit.
- Never trade on real accounts while demo-safe mode is enabled.
