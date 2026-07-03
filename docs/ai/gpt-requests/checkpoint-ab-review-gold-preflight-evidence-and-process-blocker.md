# GPT Review Request: Checkpoint AB Gold Preflight Evidence And Process Blocker

Please review PR for Checkpoint AB.

## Context

The user supplied Gold diagnostic preflight evidence. Codex verified paths and initially found that `terminal64.exe` was still running, despite the user intending to mark `Other MT5 running: no`.

The user then closed MT5. Codex rechecked with `Get-Process terminal64` and found no running process.

Checkpoint AB is documentation/diagnosis only. It must not approve execution.

## Review Checks

Check that:

- this is docs-only / diagnosis-only
- no EA/source code changes are included
- no presets are changed
- no runner behavior is changed
- no MT5 run is performed
- no Strategy Tester run is performed
- no `terminal64.exe` is spawned
- no optimization is approved
- no lot/risk increase is approved
- no profitability claim is made
- user evidence is recorded clearly
- Codex verification is recorded clearly
- the initially running `terminal64.exe` process is correctly treated as a blocker
- the later user-resolved blocker is documented without approving execution
- Codex is not allowed to kill unrelated MT5 processes
- future retry remains blocked until a later explicit approval checkpoint
- missing artifacts remain `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`
- no-trade behavior and baseline fallback absence remain `NOT_PROVEN`

## Expected Output

Output:

- `PASS` or `NEEDS_FIX`
- list issues only if `NEEDS_FIX`
