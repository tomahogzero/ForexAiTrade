# GPT Review Request: Checkpoint CO PAF Direction Context Diagnostic Validation Approval

Please review Checkpoint CO for ForexAiTrade.

## Files to Review

- `docs/107_Checkpoint_CO_PAF_Direction_Context_Diagnostic_Validation_Approval_TH.md`
- `docs/ai/tasks/checkpoint-co-paf-direction-context-diagnostic-validation-approval.md`
- `docs/106_Checkpoint_CN_PAF_Direction_Context_Diagnostics_Implementation_TH.md`

## Review Questions

1. Is Checkpoint CO clearly approval-package only?
2. Does it keep MT5 / Strategy Tester execution blocked until explicit user approval?
3. Are the future run constraints narrow enough?
4. Does it require Strategy Tester only, no optimization, no demo/live/forward test?
5. Does it prohibit market orders, pending orders, and position modification?
6. Does it require checking the new CN `paf_*` fields?
7. Does it avoid profitability claims and lot/risk increases?
8. Is the approval phrase clear enough for future execution?

## Expected Review Result

Return:

- `PASS` if this is safe as a future one-run diagnostic validation approval package.
- `NEEDS_FIX` if any execution, trading behavior, optimization, or profitability ambiguity exists.
