# Checkpoint AB: Gold Preflight Evidence And Process Blocker

Created: 2026-07-04

## Purpose

Record the user's Gold diagnostic preflight evidence and the process-level blocker found before any execution attempt.

This checkpoint is diagnosis/documentation only.

## Scope

- no EA/source changes
- no preset changes
- no runner changes
- no MT5 run
- no Strategy Tester run
- no terminal64.exe spawn
- no optimization
- no lot/risk increase
- no profitability claim
- no demo/live approval

## User Evidence Received

```text
MT5 Data Folder:
C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05

Terminal64:
C:\Program Files\XM Global MT5

Gold Symbol:
GOLD#

Gold H1 history:
yes

Report folder:
G:\AiServer\Codex\ForexAiTrade\mt5_artifacts

Other MT5 running:
no
```

## Codex Verification

Filesystem-only checks:

- Data Folder exists: true
- `C:\Program Files\XM Global MT5\terminal64.exe` exists: true
- Report folder writable marker created: true

Initial process-only check:

- `Get-Process terminal64` found one running MT5 process
- Path: `C:\Program Files\XM Global MT5\terminal64.exe`

Follow-up process-only check after the user reported closing MT5:

- `Get-Process terminal64` returned no running process
- blocker status changed from `TERMINAL64_ALREADY_RUNNING` to `RESOLVED_BY_USER`

## Result

The evidence is mostly usable. A terminal process blocker was detected, then resolved after the user closed MT5.

Operational status:

```text
Gold preflight evidence: MOSTLY_READY
Process blocker: RESOLVED_BY_USER
Retry status: BLOCKED
MT5 run: NOT_RUN
Strategy Tester run: NOT_RUN
No-trade behavior: NOT_PROVEN
Baseline fallback absence: NOT_PROVEN
```

## Why This Blocks Retry

Checkpoint T already showed that MT5 can exit with code 0 without producing tester artifacts. A pre-existing terminal instance can intercept or ignore `/config` handoff. Therefore a future retry must start from a clean process state.

## Required Before Future Execution Approval

- Codex must confirm `Get-Process terminal64` returns no running process immediately before any future execution starts
- exact symbol remains `GOLD#`
- timeframe remains H1
- date range is concrete and <= 1 month
- artifact folder is still writable
- source/preset drift remains clean
- explicit approval phrase is provided

## Future Stop Condition

If `terminal64.exe` is found before the future execution starts, execution must be blocked again.

Codex must not kill unrelated MT5 processes.

If the user explicitly asks Codex to close MT5, Codex may only do so after a separate clear approval and must not kill unrelated terminals unless the process identity is verified.

## Next Safe Checkpoint

Checkpoint AC may become a one-run approval checkpoint only after GPT reviews the approval package.
