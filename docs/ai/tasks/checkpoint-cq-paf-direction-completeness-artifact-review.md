# Checkpoint CQ: PAF Direction Completeness Artifact Review

## Purpose

Review Checkpoint CP artifacts and determine whether `DIRECTION_UNKNOWN` is a true blocker or mostly expected `NO_SETUP` behavior.

## Scope

- Artifact review only.
- No MT5 rerun.
- No Strategy Tester rerun.
- No EA/source code changes.
- No preset changes.
- No optimization.
- No lot/risk increase.
- No profitability claim.

## Input

- RunId: `run_20260709_155948`
- Case: `GOLD_HASH_H1_PAF_DIRECTION_CONTEXT_CP_cp_direction_validate_20260301_20260308`
- Source: `ea_mirror.log`
- Diagnostic rows: `97`

## Result

| Bucket | Count |
|---|---:|
| `USABLE_DIRECTION` | 19 |
| `NO_SETUP_DIRECTION_NOT_REQUIRED` | 64 |
| `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING` | 10 |
| `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING` | 4 |

## Conclusion

The true direction completeness gap is `14` possible-setup rows, not all `78` `DIRECTION_UNKNOWN` rows.

Most `DIRECTION_UNKNOWN` rows are `NO_SETUP` rows where direction is not required.

Order logic remains blocked.

## Next Safe Step

Checkpoint CR should be a diagnostics-only design or approval package focused on the 14 possible-setup direction gaps.
