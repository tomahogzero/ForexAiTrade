# Checkpoint AG: MT5 Report Runner Hardening

## Status

Implemented as a runner-only hardening checkpoint.

## Scope

This checkpoint updates only MT5 research batch runner report-artifact handling and supporting documentation.

No MT5 execution was performed.
No Strategy Tester execution was performed.
No EA/source code was changed.
No presets were changed.
No optimization was performed.
No profitability claim is made.

## Background

Checkpoint AC produced tester and EA mirror logs but did not produce or collect the required MT5 report file. Checkpoints AD and AE diagnosed report artifact generation and found that historical successful reports used terminal-data-folder relative report paths such as:

`ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report`

MT5 may then produce `mt5_report.htm` plus companion graph images.

## Runner Requirements Added

- Prefer terminal-data-folder relative `Report=` paths when `-TerminalDataFolder` is provided.
- Pre-create the expected terminal report folder.
- Write a report preflight marker in the terminal report folder.
- Search for MT5 report variants:
  - no extension
  - `.htm`
  - `.html`
  - `.xml`
  - companion `.png` chart files
- Accept only report artifacts written after the current run start time.
- Copy report and companion artifacts back into the case artifact folder.
- Record status fields for terminal report path, copied report path, companion files, stale artifact detection, and marker path.
- Preserve separation between execution infrastructure and strategy performance.

## New Execution Statuses

- `PARTIAL_TESTER_PASS_REPORT_MISSING`: tester or EA logs exist, but no report was created after the run start.
- `FAILED_NO_TESTER_ARTIFACTS`: no fresh report and no tester/EA artifact confirms execution.

These are infrastructure statuses only and do not say anything about strategy quality.

## Guardrails

- Do not run MT5 without explicit approval.
- Do not optimize.
- Do not change strategy logic.
- Do not change presets.
- Do not increase risk or lot size.
- Do not treat missing reports as strategy failure.
- Do not treat successful artifact collection as profitability proof.

## Next Safe Step

Review this runner-only PR. Because it changes execution tooling rather than docs only, it should receive user review before merge. A later checkpoint can request explicit approval for one retry with verified artifact paths.

