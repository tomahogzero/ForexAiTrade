# Checkpoint BR Gap Policy Review

This file records the policy review for Checkpoint BQ gaps. It does not run MT5, does not run Strategy Tester, does not modify source code, does not run the joiner, and does not prove profitability.

## Source Evidence

- Source gap file: `research/results/checkpoint_bq_gap_attribution/gap_attribution.csv`
- Total gaps: `6`
- `WEEKEND_MARKET_CLOSURE`: `1`
- `SHORT_SESSION_OR_HISTORY_GAP`: `5`

## Policy Proposal

### Weekend Market Closure

The Friday-to-Monday gap can be treated as a market-closure candidate for review. It should not be used as a general-purpose validator bypass.

### Daily Broker Session Gap

The repeated daily gaps around `23:00 -> 01:00` and `22:00 -> 00:00` are candidates for broker-session or maintenance gaps, but they are not automatically approved. A future validator policy must explicitly scope allowed daily session gaps by symbol, timeframe, time window, and maximum duration.

### True Missing Data

Unknown or irregular gaps remain blockers. The joiner must not run if true missing data is present.

## Decision

- `GAP_POLICY_REVIEW_DONE`
- `DAILY_SESSION_GAPS_NOT_AUTO_APPROVED`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Recommended Follow-up

Checkpoint BS should define or implement a dry-run validator gap policy report. The report should classify each gap and stop before joiner unless all gaps are explicitly accounted for by reviewed policy.
