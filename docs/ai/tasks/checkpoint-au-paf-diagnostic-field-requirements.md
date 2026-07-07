# Checkpoint AU: PAF Diagnostic Field Requirements

## Status

Completed as documentation / research-plan only.

## Scope

Checkpoint AU defines the diagnostic fields required before Price Action/Fibo shadow outcome labeling can become meaningful.

It does not implement logging, trading, presets, or runner changes.

## Guardrails Confirmed

- No MT5 run.
- No Strategy Tester run.
- No `terminal64.exe` spawn.
- No EA/source code changes.
- No preset changes.
- No script/tool code changes.
- No optimization.
- No lot/risk increase.
- No market orders.
- No pending orders.
- No position modification.
- No profitability claim.

## Source Finding

Checkpoint AT parsed AQ artifacts and found:

- diagnostic events: `954`
- possible setup rows: `267`
- all possible setup rows: `DIRECTION_MISSING`

This means future work needs richer diagnostics before TP/SL shadow outcomes can be measured.

## Required Future Fields

Future diagnostic logging should include:

- `direction_context`
- `direction_reason`
- `entry_reference_price`
- diagnostic bar OHLC
- ATR / volatility context
- optional EMA / BB / swing / zone / fibo context
- exported lookahead OHLC data for no-order shadow outcome labeling

## Decision

`PAF_DIAGNOSTIC_FIELD_REQUIREMENTS_DEFINED`

`ORDER_PATH_STILL_BLOCKED`

`NO_OPTIMIZATION_APPROVED`

`NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint AV may request a narrow EA/source change to add diagnostic logging fields only.

Checkpoint AV must still prohibit:

- market orders
- pending orders
- position modification
- optimization
- lot/risk increase
- demo/live trading
- profitability claims

