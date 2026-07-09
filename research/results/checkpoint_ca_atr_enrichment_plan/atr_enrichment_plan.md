# Checkpoint CA ATR Enrichment Plan

This is a planning artifact only. It does not run MT5, does not run Strategy Tester, does not change source code, does not rerun joiner, and does not prove profitability.

## Source Limitation

Checkpoint BZ produced offline joiner output, but first-touch labels remain unavailable:

- Joined rows: `19`
- Direction missing rows: `14`
- Outcome labels: `DATA_MISSING`
- Reason: `atr is missing or invalid`

## Recommended Plan

Use offline ATR enrichment in a future checkpoint:

- Input bars: `research/results/checkpoint_bz_offline_joiner_run/paf_lookahead_bars.csv`
- Input enriched rows: `research/results/checkpoint_bz_offline_joiner_run/paf_shadow_outcomes_enriched.csv`
- ATR method: offline diagnostic ATR from H1 bars
- ATR period: fixed diagnostic period, proposed `14`
- Output column: `offline_atr_14`
- No future bars may be used for event ATR
- No ATR period optimization

## Gate Status

- First-touch interpretation: `BLOCKED_UNTIL_ATR_AVAILABLE`
- Profitability interpretation: `BLOCKED`
- MT5/Strategy Tester: `BLOCKED`
- EA/source changes: `BLOCKED`
- Optimization: `BLOCKED`

## Next Step

Checkpoint CB should create an approval package for offline ATR enrichment.
