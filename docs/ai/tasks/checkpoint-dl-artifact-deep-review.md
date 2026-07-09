# Checkpoint DL Task: Artifact-Only Deep Review

Status: documentation/artifact review complete

## Scope

Checkpoint DL reviews committed artifacts after Checkpoint DK.

Allowed:

- Review committed DF row-level CSV
- Review committed DI and DJ summaries
- Update Thai checkpoint document under `docs/`
- Update AI current status

Not allowed:

- Run MT5
- Run Strategy Tester
- Change EA/MQL5
- Change presets
- Optimize
- Add order logic
- Increase lot/risk
- Start demo/live forward test
- Claim profitability

## Findings

- Weak windows remain: `CY-W3`, `DB-W1`, and `DI-W3`.
- Weak windows account for `19 / 242` Fibo rows and `8 / 184` usable Fibo rows.
- `CY-W3` and `DB-W1` remain a consecutive weak pair.
- DF weak pair gaps are all `PRICE_BETWEEN_EMAS`.
- Combined usable Fibo direction is SELL-heavy: `141` SELL vs `43` BUY.
- DI is the main driver of the stronger SELL skew, but DI committed data is summary-level only.
- BUY sample remains small.
- Fibo gap attribution remains material: `PRICE_BETWEEN_EMAS=40`, `TREND_ALIGNMENT_CONFLICT=18`.

## Gate Decisions

- Window count >= `12`: `PASS`
- Fibo usable first-touch rows >= `150`: `PASS`
- Total usable direction rows >= `300`: `FAIL`
- Low-window weakness: `FAIL`
- Rule-candidate gate: `FAIL`
- Order-logic gate: `FAIL`

## Verdicts

- `DL_ARTIFACT_DEEP_REVIEW_COMPLETE`
- `NO_MT5_RUN`
- `NO_STRATEGY_TESTER_RUN`
- `NO_EA_OR_PRESET_CHANGE`
- `LOW_WINDOW_WEAKNESS_REVIEWED_STILL_FAIL`
- `SELL_HEAVY_DISTRIBUTION_REVIEWED_NOT_APPROVED`
- `BUY_SAMPLE_STILL_SMALL`
- `FIBO_GAPS_REVIEWED_STILL_MATERIAL`
- `TOTAL_USABLE_DIRECTION_GATE_FAIL`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_OPTIMIZATION_PERFORMED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

