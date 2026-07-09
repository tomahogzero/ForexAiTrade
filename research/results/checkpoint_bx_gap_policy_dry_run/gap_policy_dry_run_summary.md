# PAF Gap Policy Dry-Run Summary

This is an offline policy dry-run. It does not run MT5, does not run Strategy Tester, does not change the validator, does not run the joiner, and does not prove profitability.

## Verdict

`PASS`

## Inputs

- Symbol: `GOLD#`
- Timeframe: `H1`
- Gap CSV: `research\results\checkpoint_bx_gap_policy_dry_run\evidence_gap_attribution.csv`
- Policy JSON: `research\policies\paf_gold_h1_gap_policy_draft.json`
- Policy status: `draft_daily_session_gap_enabled_for_dry_run_only`

## Counts

- Gap count: `9`
- Accepted count: `9`
- Blocking/review count: `0`
- Joiner status: `allowed_by_gap_policy`

## Status Counts

- `ACCEPTED_DAILY_BROKER_SESSION_GAP`: `8`
- `ACCEPTED_WEEKEND_MARKET_CLOSURE`: `1`

## Gap Decisions

| Previous time | Next time | Delta hours | Source classification | Policy status |
|---|---|---:|---|---|
| 2026-03-02 23:00:00 | 2026-03-03 01:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-03 23:00:00 | 2026-03-04 01:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-04 23:00:00 | 2026-03-05 01:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-05 23:00:00 | 2026-03-06 01:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-06 23:00:00 | 2026-03-09 00:00:00 | 49 | `WEEKEND_MARKET_CLOSURE` | `ACCEPTED_WEEKEND_MARKET_CLOSURE` |
| 2026-03-09 22:00:00 | 2026-03-10 00:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-10 22:00:00 | 2026-03-11 00:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-11 22:00:00 | 2026-03-12 00:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |
| 2026-03-12 22:00:00 | 2026-03-13 00:00:00 | 2 | `SHORT_SESSION_OR_HISTORY_GAP` | `ACCEPTED_DAILY_BROKER_SESSION_GAP` |

## Guardrails

- Offline gap policy dry-run only.
- No MT5 run.
- No Strategy Tester run.
- No market orders or pending orders.
- No validator implementation change.
- No joiner run.
- No optimization.
- No profitability claim.
