# PAF Shadow Outcome Labeling Specification

This specification defines how future tools should evaluate Price Action/Fibo diagnostic labels without opening orders.

## Guardrail

Shadow outcomes are research labels only. They are not entry signals.

No market order, pending order, position modification, optimization, lot/risk increase, or profitability claim is approved by this specification.

## Input Event

Minimum event schema:

```json
{
  "run_id": "run_20260707_151857",
  "case_id": "GOLD_HASH_H1_PAF_DIAG_AQ_aq_w1_20260101_20260201",
  "time": "2026.01.02 12:00:00",
  "actual_symbol": "GOLD#",
  "canonical_symbol": "GOLD",
  "timeframe": "H1",
  "classification": "POSSIBLE_FIBO_PULLBACK",
  "regime": "trend",
  "spread": 18.0,
  "direction": null,
  "entry_reference_price": null,
  "atr": null,
  "session": null
}
```

If a field is unavailable, keep it null and report the limitation.

## Output Event

Minimum output schema:

```json
{
  "event_id": "stable_hash",
  "outcome_status": "DIRECTION_MISSING",
  "shadow_entry_price": null,
  "shadow_stop_price": null,
  "shadow_target_price": null,
  "lookahead_bars": 24,
  "bars_to_resolution": null,
  "max_favorable_excursion_r": null,
  "max_adverse_excursion_r": null,
  "notes": "direction missing from diagnostic log"
}
```

## Outcome Labels

- `TP_FIRST`: hypothetical target is touched before stop.
- `SL_FIRST`: hypothetical stop is touched before target.
- `BOTH_SAME_BAR`: target and stop are both inside the same OHLC bar.
- `NO_RESOLUTION`: neither target nor stop is touched within lookahead.
- `DIRECTION_MISSING`: direction is unavailable.
- `DATA_MISSING`: price data is unavailable or incomplete.
- `SPREAD_FILTERED`: event excluded by pre-registered spread filter.
- `REGIME_FILTERED`: event excluded by pre-registered regime filter.

## Pre-Registration Requirements

Before any parser run, define:

- allowed classifications
- allowed regimes
- spread bucket thresholds
- lookahead bars
- SL hypothesis
- TP hypothesis
- ambiguous-bar handling
- session bucket mapping

These values must not be selected after seeing outcomes.

## Required Summaries

- outcome count by classification
- outcome count by regime
- outcome count by spread bucket
- outcome count by session
- missing direction count
- data missing count
- ambiguous same-bar count
- average favorable/adverse excursion
- median bars to resolution

## Next Step

Checkpoint AT may implement a parser prototype. It must remain no-order and no-optimization.
