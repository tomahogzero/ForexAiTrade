# Checkpoint CS: PAF Direction Explainability Implementation Approval

## Status

Documentation / approval package only.

No MT5 run, no Strategy Tester run, no EA/source change, no preset change, no optimization, no lot/risk increase, and no profitability claim.

## Approved Future Scope

Future Checkpoint CT may implement diagnostics-only fields for explaining the 14 possible-setup direction gaps found by CQ:

- `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING`: 10 rows
- `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING`: 4 rows

## Files Allowed In CT

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `tools/paf_diagnostic_parser.py`
- `docs/`
- `docs/ai/`
- `research/results/` for parser/static validation outputs only

## Files Not Approved For CT

- presets
- risk manager
- trade execution code
- MT5 runner behavior
- lot/risk defaults

## Non-Negotiable Guardrails

CT must not:

- emit `SIGNAL_BUY`
- emit `SIGNAL_SELL`
- send market orders
- send pending orders
- modify positions
- fallback to baseline strategy
- optimize
- increase lot/risk
- force broker minimum lot
- run MT5 without separate approval

## Required Verification

If CT changes MQL5:

- compile active EA
- create `docs/verification/compile_after_checkpoint_CT.log`
- compile result must be `0 errors, 0 warnings`

If CT changes parser:

- run Python syntax check
- keep legacy log compatibility
- missing fields must parse as `null` or `UNKNOWN`

## Required Guardrail Scan

CT must report whether the implementation introduced or touched:

- `SIGNAL_BUY`
- `SIGNAL_SELL`
- `OrderSend`
- `.Buy(`
- `.Sell(`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`

## Future MT5 Validation

Not approved in CS.

Any future Strategy Tester validation must be a separate checkpoint with explicit approval.

## Approval Phrase For CT

`Approved to implement Checkpoint CT diagnostics-only PAF direction explainability fields with compile verification and no MT5 run.`
