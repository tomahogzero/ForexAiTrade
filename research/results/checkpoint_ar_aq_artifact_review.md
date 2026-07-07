# Checkpoint AR AQ Artifact Review

RunId: `run_20260707_151857`

This review reads Checkpoint AQ artifacts only. It does not rerun MT5 and does not interpret profit.

## Safety Result

| Window | Execution | Report | Metadata Match | Trades | Forbidden | Baseline Fallback |
|---|---|---|---|---:|---:|---:|
| AQ-W1 | PASS | FOUND | true | 0 | 0 | 0 |
| AQ-W2 | PASS | FOUND | true | 0 | 0 | 0 |
| AQ-W3 | PASS | FOUND | true | 0 | 0 | 0 |

## Classification Totals

| Label | Count |
|---|---:|
| NO_SETUP | 687 |
| POSSIBLE_FIBO_PULLBACK | 145 |
| POSSIBLE_ZONE_REJECTION | 85 |
| POSSIBLE_BREAK_RETEST | 37 |

Total diagnostics: `954`

Possible setup labels: `267`

Possible setup share: `28.0%`

## Window Comparison

| Window | Diagnostics | Possible Labels | Possible Share | Trend Share | Median Spread | Max Spread |
|---|---:|---:|---:|---:|---:|---:|
| AQ-W1 | 386 | 105 | 27.2% | 91.5% | 17.0 | 40.0 |
| AQ-W2 | 267 | 66 | 24.7% | 69.3% | 18.0 | 78.0 |
| AQ-W3 | 301 | 96 | 31.9% | 82.4% | 28.0 | 109.0 |

## Review Decision

```text
PAF_DIAGNOSTIC_WORKFLOW_PASS
SHADOW_OUTCOME_SPEC_READY
NOT_READY_FOR_ORDER_IMPLEMENTATION
```

## Reasoning

- The workflow is safe and repeatable across multiple windows.
- PAF labels appear across all windows.
- No order behavior was observed.
- AQ-W3 spread is materially higher than W1/W2.
- Label presence does not prove setup quality.
- The next step should measure hypothetical outcomes, not place orders.

## Next Recommended Checkpoint

Checkpoint AS: PAF Shadow Outcome Labeling Specification.

Do not implement market orders, pending orders, or optimization from this result alone.
