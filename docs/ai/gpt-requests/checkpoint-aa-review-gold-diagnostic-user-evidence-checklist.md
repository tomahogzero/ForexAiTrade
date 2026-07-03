# GPT Review Request: Checkpoint AA Gold Diagnostic User Evidence Checklist

Please review PR for Checkpoint AA.

## Review Scope

Checkpoint AA is documentation/preflight checklist only. It should not approve MT5 execution.

Check that:

- the checkpoint is docs-only / preflight-only
- no EA/source code changes are introduced
- no presets are changed
- no runner behavior is changed
- no MT5/Strategy Tester execution is approved
- no optimization is approved
- no lot/risk increase is approved
- no profitability claim is made
- Gold remains separate from EURUSD and other forex pairs
- actual broker Gold symbol must be verified as `GOLD#` or `GOLDm#`
- H1 history availability must be proven before future retry
- date range must be concrete and no longer than 1 month
- terminal64.exe path and MT5 Data Folder must be known
- report/log/artifact paths must be absolute and writable
- stale artifacts cannot be reused as proof
- source/preset drift guard is preserved
- missing artifacts remain `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`
- future execution remains blocked until a later explicit approval checkpoint

## Expected Output

Output:

- `PASS` or `NEEDS_FIX`
- list issues only if `NEEDS_FIX`

