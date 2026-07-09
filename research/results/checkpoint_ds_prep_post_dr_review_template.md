# Checkpoint DS-Prep Post-DR Review Template

Date: 2026-07-09

Checkpoint DS-Prep is documentation-only. It prepares the artifact-only review gate that would be used after a future Checkpoint DR execution, if DR is explicitly approved and executed later.

DS-Prep does not run MT5, does not run Strategy Tester, does not review DR artifacts, does not change EA/MQL5 source, does not change presets, does not optimize, and does not approve order logic.

## Current Baseline

| Metric | Current |
|---|---:|
| Diagnostic windows | 18 |
| Diagnostic rows | 1589 |
| Possible setup rows | 451 |
| Total usable direction rows | 290 |
| Total usable direction gate | 300 |
| Shortfall | 10 |
| Fibo usable first-touch rows | 210 |

Future DR remains blocked until the exact approval phrase from Checkpoint DQ is provided.

## Required Future DS Inputs

- DR research matrix used for execution
- DR runner log
- DR per-window MT5 reports
- DR parsed execution summary
- DR PAF diagnostics presence check
- DR forbidden action marker scan
- DR baseline fallback marker scan
- combined CV + CY + DB + DI + DM + DR summary

## Future DS Gate Decisions

| Gate | Requirement |
|---|---|
| DR execution safety | PASS |
| Total trades | 0 for every DR window |
| PAF diagnostics | FOUND for every DR window |
| Total usable direction rows | >= 300 |
| Fibo usable first-touch rows | >= 150 |
| Weak-window status | no repeated/consecutive low-window issue |
| Distribution/gap review | reviewed but not converted to bias/filter |

`RULE_CANDIDATE_REVIEW_ALLOWED_NEXT` is possible only if all pre-rule gates pass. It is not order-logic approval.

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
