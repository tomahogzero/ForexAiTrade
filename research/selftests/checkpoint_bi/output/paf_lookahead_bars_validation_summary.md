# PAF Lookahead Bars Validation Summary

This validation is offline-only. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`PASS`

## Inputs

- Bars CSV: `research\selftests\checkpoint_bi\output\paf_lookahead_bars.csv`
- Shadow outcomes: `research\selftests\checkpoint_bi\paf_shadow_outcomes_fixture.csv`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Horizon bars: `1`

## Coverage

- Bar count: `4`
- Coverage from: `2026-03-01 00:00:00`
- Coverage to: `2026-03-01 03:00:00`
- Required coverage to: `2026-03-01 02:00:00`
- Event count: `2`
- Matched events: `2`
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
