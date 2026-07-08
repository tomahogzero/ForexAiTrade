# PAF Lookahead Bars Validation Summary

This validation is offline-only. It does not run MT5, does not send orders, and does not prove profitability.

## Verdict

`FAIL`

## Inputs

- Bars CSV: `research\results\checkpoint_bp_real_csv_pipeline\paf_lookahead_bars.csv`
- Shadow outcomes: `research\results\paf_shadow_outcomes_all_cases.csv`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Horizon bars: `48`

## Coverage

- Bar count: `139`
- Coverage from: `2026-03-02 01:00:00`
- Coverage to: `2026-03-10 00:00:00`
- Required coverage to: `2026-03-08 22:00:00`
- Event count: `33`
- Matched events: `33`
- Missing events: `0`
- Gap count: `6`

## Issues

- detected gaps larger than expected timeframe step: 6

## Guardrails

- Offline validation only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No optimization.
- No profitability claim.
