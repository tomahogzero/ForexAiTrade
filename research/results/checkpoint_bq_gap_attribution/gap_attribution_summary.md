# PAF H1 Gap Attribution Summary

This is an offline gap attribution summary. It does not run MT5, does not run Strategy Tester, does not send orders, and does not prove profitability.

## Inputs

- Bars CSV: `research\results\checkpoint_bp_real_csv_pipeline\paf_lookahead_bars.csv`
- Bar count: `139`
- Coverage from: `2026-03-02 01:00:00`
- Coverage to: `2026-03-10 00:00:00`

## Gap Counts

- Total gaps > 1 hour: `6`
- SHORT_SESSION_OR_HISTORY_GAP: `5`
- WEEKEND_MARKET_CLOSURE: `1`

## Gap Details

| Prev time | Next time | Delta hours | Missing H1 bars est. | Prev weekday | Next weekday | Classification |
|---|---|---:|---:|---|---|---|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2.0 | 1 | Monday | Tuesday | SHORT_SESSION_OR_HISTORY_GAP |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2.0 | 1 | Tuesday | Wednesday | SHORT_SESSION_OR_HISTORY_GAP |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2.0 | 1 | Wednesday | Thursday | SHORT_SESSION_OR_HISTORY_GAP |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2.0 | 1 | Thursday | Friday | SHORT_SESSION_OR_HISTORY_GAP |
| 2026-03-06 23:00:00 | 2026-03-09 00:00:00 | 49.0 | 48 | Friday | Monday | WEEKEND_MARKET_CLOSURE |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2.0 | 1 | Monday | Tuesday | SHORT_SESSION_OR_HISTORY_GAP |

## Interpretation

Some detected gaps may not be normal Friday-to-Monday closures. Review is required before changing validator behavior or running the joiner.

## Decision

- `GAPS_REQUIRE_MANUAL_REVIEW`
- `JOINER_NOT_RUN`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`
