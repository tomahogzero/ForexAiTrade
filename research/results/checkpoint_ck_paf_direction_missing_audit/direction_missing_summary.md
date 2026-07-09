# Checkpoint CK: PAF Direction Missing Root-Cause Audit

This is an offline root-cause audit. It does not run MT5, does not run Strategy Tester, does not change EA/source code, and does not approve order logic.

## Verdict

- Status: `PASS_OFFLINE_DIRECTION_MISSING_AUDIT`
- Classification: `DIRECTION_COMPLETENESS_FAIL`
- Rows read: `33`
- Direction-missing rows: `14` (`42.42%`)

## Root Cause Buckets

| Root cause | Rows | Share % | Recommended fix |
| --- | --- | --- | --- |
| FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING | 10 | 71.43 | Add diagnostics-only fields for EMA slope/context and candidate direction; do not infer order direction from classification alone. |
| ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING | 4 | 28.57 | Add diagnostics-only candle rejection direction fields such as rejection side, candle body direction, wick side, and zone side. |

## Direction Reason Counts

| Direction reason | Rows | Share % |
| --- | --- | --- |
| fibo_pullback_without_clear_ema_direction_context | 10 | 71.43 |
| zone_rejection_without_directional_candle_context | 4 | 28.57 |

## Missing Direction by Classification

| Classification | Rows | Share % |
| --- | --- | --- |
| POSSIBLE_FIBO_PULLBACK | 10 | 71.43 |
| POSSIBLE_ZONE_REJECTION | 4 | 28.57 |

## Missing Direction by Session

| Session | Rows | Share % |
| --- | --- | --- |
| LONDON | 5 | 35.71 |
| NEW_YORK | 5 | 35.71 |
| OTHER | 3 | 21.43 |
| OVERLAP | 1 | 7.14 |

## Interpretation

- Direction missing is not caused by a blank CSV field alone; the rows contain `DIRECTION_UNKNOWN` and explicit diagnostic reasons.
- The dominant issue is missing directional context in Fibo Pullback diagnostics.
- Zone Rejection also lacks directional candle context in a smaller set of rows.
- This should be fixed with diagnostics-only metadata before any first-touch result is used for order logic.

## Guardrails

- No MT5 run.
- No Strategy Tester run.
- No EA/source code changes.
- No preset changes.
- No order logic approved.
- No optimization.
- No profitability claim.
