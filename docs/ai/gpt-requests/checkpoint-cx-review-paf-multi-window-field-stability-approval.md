# GPT Review Request: Checkpoint CX PAF Multi-Window Field Stability Approval

Please review whether Checkpoint CX is a safe and complete approval package for a future multi-window diagnostic-only run.

## Scope

Checkpoint CX does not execute MT5 and does not change EA/source code or presets.

It proposes a future Checkpoint CY diagnostic-only execution:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Windows:
  - `2026-03-08` to `2026-03-15`
  - `2026-03-15` to `2026-03-22`
  - `2026-03-22` to `2026-03-29`
- Strategy Tester only
- No optimization
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Files to Review

- `docs/116_Checkpoint_CX_PAF_Multi_Window_Field_Stability_Approval_TH.md`
- `docs/ai/tasks/checkpoint-cx-paf-multi-window-field-stability-approval.md`
- `docs/ai/current-status.md`

## Review Questions

1. Does the approval package keep execution blocked until explicit user approval?
2. Are the proposed windows narrow and non-optimization?
3. Are no-trade / no-order / no-modification guardrails clear enough?
4. Are required CT field-presence checks complete?
5. Are pass/fail/inconclusive criteria auditable?
6. Does the package avoid profitability claims and order-logic approval?

## Expected Verdict

Return:

- `PASS`
- `NEEDS_FIX`

If `NEEDS_FIX`, list exact file sections to improve.
