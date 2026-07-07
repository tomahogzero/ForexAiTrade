# Checkpoint AO: PAF Diagnostic Coverage Plan

## Objective

Plan the next safe diagnostic coverage step after Checkpoint AM/AN without running MT5 and without changing trading logic.

## Scope

In scope:

- Identify current diagnostic coverage gaps.
- Define additional no-trade diagnostic windows as a future approval concept.
- Define required config assertions and stop conditions.
- Define decision gates before any PAF implementation.
- Update progress estimate.

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

## Current Evidence

The latest Gold PAF diagnostic evidence is one month only:

- Symbol/timeframe: `GOLD#` H1
- Window: `2026-06-01` to `2026-07-01`
- Diagnostics: `417`
- Total trades: `0`
- Forbidden markers: `0`
- Baseline fallback markers: `0`

## Recommendation

Do not implement PAF entries yet.

Plan Checkpoint AP as a future approval package for 3 no-trade diagnostic windows, each no longer than 1 month, using the official AK runner/parser workflow.

## Progress Estimate

- Research-system readiness: about `47%`
- Real-money bot readiness: about `10-15%`

## Next Safe Step

Checkpoint AP should be approval-only for multi-window no-trade diagnostics. It should still not implement orders.

