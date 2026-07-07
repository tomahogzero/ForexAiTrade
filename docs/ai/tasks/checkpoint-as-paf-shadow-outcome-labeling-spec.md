# Checkpoint AS: PAF Shadow Outcome Labeling Specification

## Objective

Define a no-order shadow-outcome labeling specification for Price Action/Fibo diagnostic labels.

## Scope

In scope:

- Define event inputs.
- Define deterministic shadow entry references.
- Define direction handling.
- Define hypothetical SL/TP outcome labels.
- Define bucketing and metrics.
- Define evidence gates before any order implementation.

Out of scope:

- MT5 execution.
- Strategy Tester execution.
- EA/source changes.
- Preset changes.
- Script/tool changes.
- Optimization.
- Market orders.
- Pending orders.
- Position modification.
- Profitability interpretation.

## Required Outcome Labels

- `TP_FIRST`
- `SL_FIRST`
- `BOTH_SAME_BAR`
- `NO_RESOLUTION`
- `DIRECTION_MISSING`
- `DATA_MISSING`
- `SPREAD_FILTERED`
- `REGIME_FILTERED`

## Conservative Ambiguity Rule

If both hypothetical TP and SL are inside the same bar and tick path is unavailable, do not assume TP-first.

Use either:

- `BOTH_SAME_BAR`, or
- stop-first in a separate conservative sensitivity table.

## Required Buckets

- classification
- regime
- spread bucket
- volatility bucket
- session bucket
- month/window
- direction

## Decision

```text
SHADOW_OUTCOME_SPEC_DEFINED
NO_ORDER_IMPLEMENTATION_APPROVED
NO_OPTIMIZATION_APPROVED
```

## Next Safe Step

Checkpoint AT should prototype a no-order shadow outcome parser against AQ artifacts only.

If direction/OHLC fields are missing, AT must report limitations instead of inferring future-looking labels.
