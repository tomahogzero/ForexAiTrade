# Checkpoint A: Process Safety And Research Matrix

Date: 2026-06-19

This checkpoint is intentionally small. It does not optimize parameters, does not claim profitability, and does not change strategy entry or exit logic for profit.

## What Changed

### MT5 Batch Runner Process Safety

`scripts/run_mt5_research_batch.ps1` was reviewed and constrained so it controls only the MT5 process it starts.

Safety behavior:

- Starts MT5 with `Start-Process -PassThru`.
- Stores the spawned process ID in each case artifact folder.
- On timeout, stops only that exact spawned process ID.
- Does not bulk kill `terminal64`.
- Fails safely if a dedicated spawned process cannot be identified.
- Prints a strong warning that the runner should use a dedicated research MT5 instance, not a live trading terminal.

Supported checkpoint parameters:

- `-TerminalExe`
- `-TerminalDataFolder`
- `-UsePortableMode`
- `-CaseTimeoutMinutes`
- `-RetryCount`
- `-OutputRoot`

### EA Position Management Timing

The EA now has:

```text
InpManagePositionsOnlyOnNewBar=false
```

Position management is controlled separately from new entry generation:

- Existing safety gates are preserved.
- Existing position management still requires `InpManageExistingPositions=true`.
- Real-account/demo/tester/live-disabled safety gates remain active.
- New entries still obey `InpTradeOnlyOnNewBar`.
- Existing positions can be managed on every tick unless `InpManagePositionsOnlyOnNewBar=true`.

No strategy entry or exit profitability logic was changed in this checkpoint.

### Research Matrix

Created:

```text
research/research_matrix.json
```

The matrix defines:

- Symbols: `EURUSD`, `USDJPY#`, `GOLD#`
- Timeframes: `H1`, `H4`
- Periods:
  - train: `2023-01-01` to `2024-12-31`
  - validation: `2025-01-01` to `2025-12-31`
  - out_of_sample: `2026-01-01` to `2026-06-18`
- Gold deposit cases:
  - `10000`
  - `30000`

Broker symbols are explicit per case through `actual_symbol`. The matrix does not assume `GOLDm#`; the current XM tester symbol can remain `GOLD#`.

## Why Bulk Killing MT5 Is Prohibited

Bulk commands such as `Get-Process terminal64 | Stop-Process` are prohibited because they can close unrelated terminals, including manual trading sessions, demo forward tests, live charts, or another research run.

The runner must only stop the process ID that it created for the current case. If that process ID is not known, the correct behavior is to fail safely and leave other terminals untouched.

## How To Run Safely

Use a dedicated MT5 research installation or portable copy. Do not run this against a terminal used for live trading.

Example:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mt5_research_batch.ps1 `
  -TerminalExe "C:\Program Files\XM Global MT5\terminal64.exe" `
  -TerminalDataFolder "C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05" `
  -CaseTimeoutMinutes 10 `
  -RetryCount 0 `
  -OutputRoot "research\runs"
```

For a portable dedicated instance, add:

```powershell
-UsePortableMode
```

## Research Matrix Structure

Top-level keys:

- `version`: matrix schema version.
- `description`: human-readable purpose.
- `periods`: train, validation, and out-of-sample date windows.
- `defaults`: shared tester defaults.
- `cases`: per-symbol, per-timeframe, per-deposit case definitions.
- `integration_cases`: small case list for smoke/integration checks.

Each case contains:

- `case_id`
- `enabled`
- `actual_symbol`
- `canonical_symbol`
- `timeframe`
- `deposit`
- `risk_percent`
- `base_preset`

## Compile Verification

Because MQL5 timing logic was changed, the active EA must compile with:

```text
0 errors, 0 warnings
```

Verification log:

```text
docs/verification/compile_after_checkpoint_A.log
```

## Remaining Work For Next Checkpoint

- Add fuller artifact isolation per case.
- Add robust MT5 report collection and parsing.
- Add survival-first scoring.
- Add generated research summaries.
- Run controlled integration tests.
- Keep optimization disabled until the research pipeline is reliable.

