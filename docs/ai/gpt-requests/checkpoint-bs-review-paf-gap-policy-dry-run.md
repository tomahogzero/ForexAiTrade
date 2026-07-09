# GPT Review Request: Checkpoint BS PAF Gap Policy Dry-Run

## Request

Please review Checkpoint BS for safety and consistency before any later joiner rerun.

## Scope to Review

Checkpoint BS adds:

- `tools/paf_gap_policy_dry_run.py`
- `research/policies/paf_gold_h1_gap_policy_draft.json`
- `research/results/checkpoint_bs_gap_policy_dry_run/`
- `docs/85_Checkpoint_BS_PAF_Gap_Policy_Dry_Run_TH.md`
- `docs/ai/tasks/checkpoint-bs-paf-gap-policy-dry-run.md`

## Guardrails

Confirm:

- no MT5 run
- no Strategy Tester run
- no EA/source code changes
- no preset changes
- no production validator change
- no joiner run
- no optimization
- no profitability claim
- no lot/risk increase

## Specific Questions

1. Is the dry-run tool conservative enough?
2. Does it correctly keep daily broker-session gaps as `REVIEW_REQUIRED` instead of auto-accepting them?
3. Is it safe that the joiner remains blocked while verdict is `REVIEW_REQUIRED`?
4. Is the policy draft correctly scoped to `GOLD#` H1?
5. Should Checkpoint BT review/approve daily broker-session gap handling before any joiner rerun?

## Expected Review Output

Return:

- `PASS` if safe to merge
- `NEEDS_FIX` with exact issues if not
