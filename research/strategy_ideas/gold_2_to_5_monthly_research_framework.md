# Gold 2-5% Monthly Research Framework

Created: 2026-07-04

## Research status

Status: `RESEARCH_IDEA_ONLY`

This file stores research ideas only. It does not implement a trading strategy and does not approve MT5 execution.

## Research hypothesis

Gold may deserve a separate research track because:

- it can trend and break out strongly
- it reacts quickly to macro and political events
- liquidity is deep but volatility can expand suddenly
- broker-specific contract metadata and minimum lot rules can dominate risk sizing

The working hypothesis is not "Gold can make 2-5% monthly safely."

The safer hypothesis is:

> Gold may offer enough movement to research 2-5% monthly scenarios, but only if risk gates, session filters, volatility sizing, and broker metadata keep drawdown and forced-lot risk under control.

## Popular method families to evaluate

| Method family | What to measure first | Main risk |
| --- | --- | --- |
| Trend following | trend duration, ADX, EMA slope, R multiple by trend regime | late entry and giveback |
| Breakout | range size, false breakout rate, session, spread | whipsaw and slippage |
| Mean reversion | sideway regime quality, Bollinger/VWAP deviation | getting trapped in trend |
| Pullback continuation | structure pullback quality, momentum restart | catching falling/rising knives |
| Session filter | Asia/London/NY/overlap attribution | overfitting session windows |
| Macro/event filter | CPI/NFP/FOMC impact, spread and gap behavior | news spikes and stop slippage |
| Exit research | SL/TP/trailing/breakeven realized R | profitable entries ruined by exits |

## Required diagnostics before implementation

- accepted/rejected signal counts
- no-signal bars
- regime distribution
- session distribution
- spread/slippage blocks
- broker minimum lot / risk-budget blocks
- risk gate blocks
- trade-level ledger
- exit telemetry
- realized R by exit type
- drawdown concentration
- profit concentration
- monthly/quarterly stability
- event-window behavior

## Gold research gates

Before any future Gold backtest:

- actual symbol must be explicit (`GOLD#` or `GOLDm#`)
- canonical symbol may be `GOLD`
- broker metadata must be logged
- risk percent must remain low
- no forced minimum lot
- deposit assumption must be justified by broker min lot and SL distance
- train/validation/out-of-sample must be separate
- execution status must remain separate from performance

## Aggressive monthly target handling

2-5% monthly can only be treated as a research target if:

- max monthly loss is capped
- max drawdown is capped
- trade count is sufficient
- performance is not caused by one or two trades
- validation and OOS both pass
- drawdown does not cluster in a few days
- no risk budget violation occurs

If the only way to approach 2-5% monthly is by increasing lot/risk, the idea must be rejected or downgraded.

## Forbidden paths

- martingale
- uncontrolled grid
- recovery lot multiplication
- no-stop-loss holding
- forced broker minimum lot
- increasing risk after losses
- optimizing only for net profit
- using OOS as a tuning set

## Proposed next checkpoint

Checkpoint Y should define Gold diagnostic logging requirements before any Gold trading strategy implementation.

