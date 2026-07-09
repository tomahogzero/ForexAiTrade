# PAF Gap Policy Dry-Run Summary

This is an offline policy dry-run. It does not run MT5, does not run Strategy Tester, does not change the validator, does not run the joiner, and does not prove profitability.

## Verdict

`REVIEW_REQUIRED`

## Inputs

- Symbol: `GOLD#`
- Timeframe: `H1`
- Gap CSV: `research\results\checkpoint_bq_gap_attribution\gap_attribution.csv`
- Policy JSON: `research\policies\paf_gold_h1_gap_policy_draft.json`
- Policy status: `draft_review_required`

## Counts

- Gap count: `6`
- Accepted count: `1`
- Blocking/review count: `5`
- Joiner status: `blocked_by_gap_policy`

## Status Counts

- `ACCEPTED_WEEKEND_MARKET_CLOSURE`: `1`
- `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP`: `5`

## Gap Decisions

| Previous time | Next time | Delta hours | Source classification | Policy status |
|---|---|---:|---|---|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-06 23:00:00 | 2026-03-09 00:00:00 | 49.0 | `WEEKEND_MARKET_CLOSURE` | `ACCEPTED_WEEKEND_MARKET_CLOSURE` |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2.0 | `SHORT_SESSION_OR_HISTORY_GAP` | `REVIEW_REQUIRED_DAILY_BROKER_SESSION_GAP` |

## Guardrails

- Offline gap policy dry-run only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No validator implementation change.
- No joiner run.
- No optimization.
- No profitability claim.
