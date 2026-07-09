# Checkpoint DD Fibo Pullback Diagnostic Plan Summary

## Scope

Documentation/review-only. No MT5 run. No Strategy Tester run. No source change. No preset change. No optimization. No profitability claim.

## Inputs

Checkpoint DC combined CV + CY + DB:

- diagnostic rows: 621
- possible setup rows: 174
- usable direction rows: 106
- diagnostic interpretation gate 100: PASS_LOW_MARGIN
- rule-candidate gate 300: FAIL

## Why Fibo Pullback

Possible Fibo Pullback is the dominant setup family:

- Possible Fibo Pullback: 128
- Possible Zone Rejection: 33
- Possible Break Retest: 13

This makes Fibo Pullback the first diagnostic focus only.

## Required Future Slice

Future DE should slice Fibo Pullback diagnostics by:

- direction
- direction source
- confidence
- first-touch usability
- EMA slope
- price vs EMA
- trend alignment
- gap reason
- window distribution
- spread
- regime

## Gates Before Rule Candidate

- Fibo usable direction rows >= 150
- Total usable direction rows >= 300
- At least 12 windows
- No repeated low-window weakness
- BUY/SELL distribution reviewed
- Gap attribution reviewed
- No-trade diagnostic safety remains intact

## Verdict

`FIBO_PULLBACK_DIAGNOSTIC_FOCUS_APPROVED`

`RULE_CANDIDATE_NOT_APPROVED`

`ORDER_LOGIC_NOT_APPROVED`

`PAF_NOT_READY_FOR_ORDER_LOGIC`
