# Checkpoint AK: PAF Diagnostic Runner / Parser Integration

## Objective

Make the Price Action/Fibo diagnostic workflow reusable by adding official runner/parser support without running MT5 and without changing EA/source code or presets.

## Scope

In scope:

- Add runner support for PAF diagnostic-only case metadata.
- Add a parser that treats `ea_mirror.log` as the authoritative diagnostic source.
- Count `tester_log_excerpt.log` separately to prevent duplicate diagnostic totals.
- Add a PAF diagnostic matrix template for future reviewed runs.
- Document the workflow and remaining guardrails.

Out of scope:

- MT5 execution.
- Strategy Tester execution.
- EA/source changes.
- Preset changes.
- Trading logic changes.
- Optimization.
- Lot/risk increase.
- Profitability interpretation.

## Implementation Notes

Runner case metadata:

- `enable_price_action_fibo`
- `price_action_fibo_diagnostics_only`
- `paf_use_pending_orders`
- `paf_max_pending_orders`
- `paf_log_only_on_new_bar`
- `paf_entry_timeframe`
- `paf_higher_timeframe`
- `manage_existing_positions`
- `diagnostic_only`

Parser outputs:

- per-case `paf_diagnostics.json`
- per-case `paf_diagnostics_summary.md`
- aggregate `research/results/paf_diagnostics_all_cases.csv`
- aggregate `research/results/paf_diagnostics_summary.md`

## Safety Interpretation

Diagnostic classifications remain observation labels only. They are not entry signals.

This checkpoint does not approve market orders, pending orders, position modification, demo forward testing, or live trading.

## Next Safe Step

Checkpoint AL should review this runner/parser integration and decide whether a future one-run diagnostic execution should be approved.

