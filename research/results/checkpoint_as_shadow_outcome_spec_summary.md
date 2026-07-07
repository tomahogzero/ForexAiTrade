# Checkpoint AS Shadow Outcome Spec Summary

Checkpoint AS defines a no-order shadow-outcome labeling plan for Price Action/Fibo diagnostics.

## Decision

```text
SHADOW_OUTCOME_SPEC_DEFINED
NO_ORDER_IMPLEMENTATION_APPROVED
NO_OPTIMIZATION_APPROVED
```

## Why This Exists

Checkpoint AQ/AR showed that PAF diagnostic labels appear across multiple `GOLD#` H1 windows and that no-trade guardrails worked.

However, label presence is not outcome evidence. AS defines how to measure hypothetical outcomes before any order implementation is considered.

## Key Requirements

- Do not infer direction from future price movement.
- Use deterministic entry reference rules.
- Pre-register SL/TP/lookahead assumptions before running a parser.
- Treat same-bar TP/SL ambiguity conservatively.
- Split results by classification, regime, spread bucket, volatility bucket, session, and window.
- Report missing data as a limitation instead of guessing.

## Next Safe Step

Checkpoint AT: no-order PAF shadow outcome parser prototype against AQ artifacts.
