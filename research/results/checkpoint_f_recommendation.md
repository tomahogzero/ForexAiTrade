# Checkpoint F Recommendation

Selected RunId: `run_20260621_183001`

Next action: `NEEDS_EXIT_RESEARCH`

EURUSD H1 remains `RESEARCH_MORE`. This checkpoint does not approve live/demo forward testing and does not prove profitability.

## Rationale

- Previous Checkpoint F aggregate diagnostics included repeated runs and inflated total trade counts. F2 fixes this by scoping diagnostics to a selected RunId.
- Trade-level rows are available from existing MT5 reports.
- Session and exit diagnostics are now available for baseline review.
- H1 remains the baseline, but exit diagnostics show SL-heavy exits (`SL=160`, `TP=29`) and max consecutive losses of `7`.
- Exit research means additional diagnosis and logging design first, not changing exit logic in this checkpoint.
- M30 and H4 remain rejected for now from Checkpoint E2.

## Before Adding MicroTrend or Fibo Zone

The following must be understood first:

- session weakness
- trade-level distribution
- exit behavior
- drawdown concentration
- spread/slippage sensitivity

## Guardrails

- Do not optimize from a small number of trades.
- Do not add a new strategy until reporting and diagnostics explain the current baseline.
- Do not claim profitability from this checkpoint.
