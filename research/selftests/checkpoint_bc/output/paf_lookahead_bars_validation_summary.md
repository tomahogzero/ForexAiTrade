# PAF Lookahead Bars Validation Summary

This validation is offline-only. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`PASS`

## Inputs

- Bars CSV: `research\selftests\checkpoint_bb\paf_lookahead_bars_fixture.csv`
- Shadow outcomes: `research\selftests\checkpoint_bb\paf_shadow_outcomes_fixture.csv`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Horizon bars: `4`

## Coverage

- Bar count: `20`
- Coverage from: `2026-03-01 00:00:00`
- Coverage to: `2026-03-01 19:00:00`
- Required coverage to: `2026-03-01 19:00:00`
- Event count: `4`
- Matched events: `4`
- Missing events: `0`
- Gap count: `0`

## Issues

- None

## Guardrails

- Offline validation only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No optimization.
- No profitability claim.
