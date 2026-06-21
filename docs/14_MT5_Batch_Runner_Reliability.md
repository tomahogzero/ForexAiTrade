# MT5 Batch Runner Reliability

## Critical Safety Rule

The batch runner must never close or kill unrelated MT5 terminal instances.

The old unsafe pattern is prohibited:

```powershell
Get-Process terminal64 | Stop-Process
```

## Current Runner Safety

The runner uses:

```powershell
Start-Process -PassThru
```

It records the spawned process ID in:

```text
process_info.json
```

If a timeout occurs, it stops only that exact spawned process ID.

## Dedicated Research Terminal

Recommended usage is a separate MT5 installation or portable terminal dedicated to research.

Supported parameters:

- `-DedicatedTerminalExe`
- `-DedicatedDataFolder`
- `-UsePortableMode`
- `-TerminalExe`
- `-TerminalDataFolder`
- `-TesterRootFolder`

Do not run batch research against an MT5 terminal used for live trading.

## Completion Detection

A case should be treated as complete only after:

- the spawned process exits or tester completion is detected;
- the unique report file exists;
- the report becomes stable;
- the report can be parsed;
- parsed metadata matches the requested case.

Statuses:

- `PASS`
- `FAILED`
- `TIMEOUT`
- `NO_REPORT`
- `PARSE_ERROR`
- `CONFIG_MISMATCH`
- `PROCESS_ERROR`

## Integration Test

Run the short integration set:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mt5_research_batch.ps1 -IntegrationOnly -DedicatedTerminalExe "C:\Path\To\ResearchMT5\terminal64.exe" -UsePortableMode
```

This test validates isolation and artifacts only. It is not a profitability test.
