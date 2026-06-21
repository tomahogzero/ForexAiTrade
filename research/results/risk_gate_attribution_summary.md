# Risk Gate Attribution Summary

Scope: `EURUSD_H1_EXIT_BASELINE_10000` from `run_20260621_205032`.

This is diagnostic attribution only. It does not change risk settings or strategy behavior.

## Phase Summary

| phase | total_trades | net_profit | accepted_signals | losing_streak_blocks | first_losing_streak_block | last_losing_streak_block | accepted_trades_before_first_losing_block | accepted_trades_after_first_losing_block | losing_streak_gate_recovered | losing_streak_blocks_until_end | consecutive_losses_before_trigger |
|---|---|---|---|---|---|---|---|---|---|---|---|
| train | 22 | -40.96 | 22 | 1558 | 2023-01-30 13:00:00 | 2024-12-24 14:00:00 | 22 | 0 | False | False | 4 |
| validation | 105 | 61.38 | 105 | 467 | 2025-05-15 18:00:00 | 2025-12-29 10:00:00 | 105 | 0 | False | False | 4 |
| out_of_sample | 62 | 41.03 | 62 | 143 | 2026-03-31 17:00:00 | 2026-06-16 18:00:00 | 62 | 0 | False | False | 4 |

## Code Review: Losing Streak Logic

- `CRiskManager::ConsecutiveLosses()` scans MT5 closed deal history from newest to oldest.
- It filters by current `_Symbol` and `InpMagicNumber`.
- Only `DEAL_ENTRY_OUT` and `DEAL_ENTRY_OUT_BY` closed deals are counted.
- Negative closed profit increments the streak.
- A positive closed profit stops the scan, effectively resetting the streak.
- If the streak is greater than or equal to `InpMaxLosingStreak`, `CanOpenNewTrade()` rejects new entries.
- Because rejected entries do not create new closed winning deals, the streak cannot recover while the EA is fully locked out by this gate.
- This is intentional capital-preservation behavior, but it is also a research limitation because a backtest phase can become long-term locked after a short loss cluster.

## Interpretation

A long losing-streak lockout means the phase result is risk-gated performance, not raw strategy performance. It protects capital, but it can make train/validation/OOS comparisons harder.
