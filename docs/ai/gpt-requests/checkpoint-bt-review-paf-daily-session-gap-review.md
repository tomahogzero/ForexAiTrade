# GPT Review Request: Checkpoint BT PAF Daily Session Gap Review

## Request

Please review Checkpoint BT for safety and research integrity.

## Scope

Checkpoint BT does not approve daily broker-session gaps yet. It documents why more evidence is required before allowing the offline joiner to proceed.

## Files to Review

- `docs/86_Checkpoint_BT_PAF_Daily_Session_Gap_Review_TH.md`
- `docs/ai/tasks/checkpoint-bt-paf-daily-session-gap-review.md`
- `research/results/checkpoint_bt_daily_session_gap_review/daily_session_gap_review.md`
- `research/results/checkpoint_bt_daily_session_gap_review/daily_session_gap_review.json`

## Questions

1. Is it correct to keep daily session gaps unapproved until manual MT5/broker-session evidence exists?
2. Are the approval criteria strict enough?
3. Is it correct to keep joiner blocked while the dry-run verdict is `REVIEW_REQUIRED`?
4. Does this avoid bypassing the validator too broadly?
5. Is Checkpoint BU as a manual evidence collection guide the safest next step?

## Expected Output

Return:

- `PASS` if this is safe and consistent
- `NEEDS_FIX` with exact required changes if not
