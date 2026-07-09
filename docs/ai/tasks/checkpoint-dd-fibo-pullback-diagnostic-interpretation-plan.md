# Checkpoint DD: Fibo Pullback Diagnostic Interpretation Plan

## Scope

Documentation/review-only plan.

Do not run MT5.
Do not run Strategy Tester.
Do not change EA/source code.
Do not change presets.
Do not optimize.
Do not increase lot/risk.
Do not claim profitability.
Do not add order logic.

## Reason

Checkpoint DC found:

- combined usable direction rows: 106
- diagnostic interpretation gate 100: PASS_LOW_MARGIN
- rule-candidate gate 300: FAIL
- Possible Fibo Pullback: 128 of 174 possible setups

Fibo Pullback is the first diagnostic focus because it is the dominant setup family, not because it is approved as a trading rule.

## Interpretation Plan

Future artifact review should slice Fibo Pullback rows by:

- candidate direction
- direction source
- direction confidence
- first-touch usability
- EMA slope state
- price vs EMA state
- trend alignment state
- Fibo direction gap reason
- window/date distribution
- spread distribution
- regime distribution

## Minimum Gates Before Rule Candidate

- Fibo usable direction rows >= 150
- Total usable direction rows >= 300
- At least 12 windows of diagnostic coverage
- No repeated low-window weakness
- BUY/SELL distribution reviewed
- Gap attribution reviewed
- total trades = 0 in diagnostic runs
- forbidden markers = 0
- baseline fallback markers = 0

## Decision

`FIBO_PULLBACK_DIAGNOSTIC_FOCUS_APPROVED`

`RULE_CANDIDATE_NOT_APPROVED`

`ORDER_LOGIC_NOT_APPROVED`

`PAF_NOT_READY_FOR_ORDER_LOGIC`

## Recommended Next Checkpoint

Checkpoint DE should generate a Fibo Pullback diagnostic slice report from existing CV + CY + DB artifacts only.

DE should not run MT5 and should not change EA/source code or presets.
