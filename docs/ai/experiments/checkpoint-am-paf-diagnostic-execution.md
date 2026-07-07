# Checkpoint AM: PAF Diagnostic Execution

## Approval

User explicitly approved:

```text
Approved to execute Checkpoint AM one-run PAF diagnostic with symbol GOLD# timeframe H1 date range 2026-06-01 to 2026-07-01 using official AK runner/parser workflow.
```

## Execution

- RunId: `run_20260707_121145`
- Case: `GOLD_HASH_H1_PAF_DIAG_AM_20260601_20260701_diagnostic_window`
- Symbol: `GOLD#`
- Timeframe: `H1`
- Date range: `2026-06-01` to `2026-07-01`
- Source commit: `f958e65a4c59f10ee773b385889e42c0912f0112`
- Process ID started by runner: `31400`
- MT5 run count: exactly one Strategy Tester execution

## Artifact Folder

```text
G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260707_121145\GOLD_HASH_H1_PAF_DIAG_AM_20260601_20260701_diagnostic_window
```

## Result

- Execution status: `PASS`
- Report artifact status: `FOUND`
- Total trades: `0`
- PAF diagnostic count: `417`
- No-trade count: `502`
- Forbidden action marker count: `0`
- Baseline fallback marker count: `0`
- No-trade confirmation: `PASS_FROM_REPORT_AND_EA_LOGS`
- Baseline fallback confirmation: `PASS_FROM_EA_LOGS`

## Classification Counts

- `NO_SETUP`: 304
- `POSSIBLE_FIBO_PULLBACK`: 57
- `POSSIBLE_ZONE_REJECTION`: 41
- `POSSIBLE_BREAK_RETEST`: 15

## Guardrails

Confirmed:

- No optimization
- No market order
- No pending order
- No position modification
- No source/preset change
- No lot/risk increase
- No profitability claim
- No demo/live approval

## Next Step

Checkpoint AN should review the Checkpoint AM artifact set. It should not run MT5 automatically.

