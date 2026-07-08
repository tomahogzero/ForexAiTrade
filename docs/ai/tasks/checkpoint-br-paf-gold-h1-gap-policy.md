# Checkpoint BR: PAF Gold H1 Gap Policy Review

## Status

`DONE_FOR_REVIEW`

## Scope

Checkpoint BR reviews how the offline PAF pipeline should treat `GOLD#` H1 gaps discovered in Checkpoint BP/BQ.

This checkpoint is documentation/research-policy only:

- no MT5 run
- no Strategy Tester run
- no EA/source change
- no preset change
- no validator implementation change
- no joiner run
- no optimization
- no profitability interpretation

## Inputs

- Checkpoint BP normalized bars and validation failure
- Checkpoint BQ gap attribution
- Gap count: `6`
- Weekend closure candidate: `1`
- Daily short session/history gaps: `5`

## Policy Conclusion

Weekend gaps may be acceptable as market-closure candidates after review.

Daily two-hour gaps around `22:00/23:00 -> 00:00/01:00` are broker-session gap candidates, not automatically approved. They require explicit symbol/timeframe-scoped policy before the validator or joiner can proceed.

True missing data remains a hard blocker.

## Decision

- `GAP_POLICY_REVIEW_DONE`
- `WEEKEND_GAP_POLICY_CANDIDATE_DEFINED`
- `DAILY_SESSION_GAP_POLICY_CANDIDATE_DEFINED`
- `DAILY_SESSION_GAPS_NOT_AUTO_APPROVED`
- `TRUE_MISSING_DATA_REMAINS_BLOCKER`
- `VALIDATOR_NOT_CHANGED`
- `JOINER_STILL_BLOCKED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## Next Safe Step

Checkpoint BS should add or specify a validator dry-run policy mechanism that classifies gaps without bypassing validation globally. The first acceptable scope should be limited to `GOLD#` H1 and must preserve a hard blocker for unknown or unclassified gaps.
