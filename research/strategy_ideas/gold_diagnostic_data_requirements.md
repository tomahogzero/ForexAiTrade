# Gold Diagnostic Data Requirements

Created: 2026-07-04

Status: `DIAGNOSTIC_REQUIREMENTS_ONLY`

## Required data before strategy work

Gold research must not begin by tuning entries. It must begin by proving that diagnostic data is available and trustworthy.

## Symbol metadata

Required fields:

- actual_symbol
- canonical_symbol
- digits
- point
- tick_size
- tick_value
- contract_size
- volume_min
- volume_max
- volume_step
- stops_level
- freeze_level
- spread

## Signal diagnostics

Required fields:

- bar_time
- session
- regime
- strategy_family_candidate
- classification
- no_trade_reason
- direction_candidate
- reference_price
- invalidation_level
- hypothetical_sl_distance
- hypothetical_tp_distance
- atr
- adx
- ema_slope
- bollinger_width
- spread_points
- reject_reason

## Risk diagnostics

Required fields:

- risk_percent
- risk_money
- raw_lot
- normalized_lot
- min_lot
- actual_risk_money
- min_lot_risk_violation
- estimated_minimum_deposit
- margin_check_result

## Session/regime/event diagnostics

Gold must support aggregation by:

- Asia
- London
- New York
- Overlap
- Other
- trend
- breakout
- sideway
- mixed
- unsafe
- known high-impact event windows

## Execution artifact requirements

Any future Gold diagnostic run must include:

- source commit
- terminal path
- data folder
- tester config
- effective config
- report path
- terminal log
- tester log
- EA/mirror log
- stale artifact inventory
- forbidden action scan

## Forbidden outcome

If a run produces performance numbers but not diagnostic artifacts, it is not useful for Gold research and must be classified as inconclusive.

