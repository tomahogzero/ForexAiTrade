# Checkpoint AD: MT5 Report Artifact Generation Diagnosis

Created: 2026-07-06

## Purpose

Diagnose why Checkpoint AC produced Strategy Tester and EA diagnostic logs but did not produce the required MT5 report artifact.

This checkpoint is documentation and diagnosis only.

It does not rerun MT5, does not run Strategy Tester, does not spawn `terminal64.exe`, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Source Context

PR #20 / Checkpoint AC has been merged.

Checkpoint AC:

- RunId: `run_20260704_014343_checkpoint_ac_gold_no_trade`
- Case: `GOLD_HASH_H1_PAF_DIAG_20260601_20260701`
- Symbol/timeframe: `GOLD#` H1
- Date range: `2026-06-01` to `2026-07-01`
- Result: `PARTIAL_TESTER_PASS_REPORT_MISSING`

Checkpoint AC was exactly one approved no-trade diagnostic Strategy Tester execution.

## What Changed From Checkpoint T

Checkpoint T failed with almost no useful tester artifacts:

- no required Strategy Tester report/log path
- no tester log excerpt
- no EA mirror log
- no Price Action / Fibo diagnostic classification summary

Checkpoint AC narrowed the failure:

- Strategy Tester log was produced
- EA mirror log was produced
- Price Action / Fibo diagnostic classifications were produced
- no forbidden action markers were found in available logs
- no baseline fallback markers were found in available logs
- MT5 report artifact was still missing

Therefore the current diagnosis target is report generation, not strategy behavior.

## Existing AC Artifacts Inspected

Artifact folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701`

Observed files:

- `generated_tester.ini`
- `effective_config_snapshot.set`
- `case.json`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `forbidden_action_grep_summary.txt`
- `status.json`
- `post_run_guardrail_summary.md`
- `write_marker.txt`

Missing:

- `mt5_report`
- `mt5_report.htm`
- `mt5_report.html`
- `mt5_report.xml`

## Relevant Config Evidence

Checkpoint AC `generated_tester.ini` contains:

```ini
[Tester]
Expert=ForexAiTrade\ForexAiTrade.ex5
Symbol=GOLD#
Period=H1
Optimization=0
Model=0
FromDate=2026.06.01
ToDate=2026.07.01
Report=G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701\mt5_report
ReplaceReport=1
ShutdownTerminal=1
```

`process_info.json` confirms:

- terminal executable: `C:\Program Files\XM Global MT5\terminal64.exe`
- spawned process ID: `51132`
- portable mode: `false`
- exactly one spawn: `true`

`runner.log` confirms:

- config was generated
- expected report base was the absolute `G:\...mt5_report` path
- MT5 process exited with code 0
- status was initially marked `FAILED_NO_TESTER_ARTIFACTS`, later refined to `PARTIAL_TESTER_PASS_REPORT_MISSING` after tester/EA logs were confirmed

## Current Finding

The AC failure is not a global Strategy Tester failure.

It is also not the same as Checkpoint T.

Current finding:

`MT5 Strategy Tester executed and EA diagnostics ran, but command-line report generation did not create the requested report file at the expected path.`

## Likely Root Cause Areas

### Report Path Compatibility

Checkpoint AC requested an absolute report base path outside the MT5 terminal data folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\...\mt5_report`

This path was writable by Codex/PowerShell, but it is not yet proven that MT5 accepts it for Strategy Tester `Report=`.

### Relative vs Absolute Report Path

Historical successful runs in `research/runs/` include reports such as:

- `mt5_report.htm`
- `mt5_report.html`

Several successful generated tester configs used a relative `Report=` form:

```ini
Report=ForexAiTradeResearch\run_xxx\case_xxx\mt5_report
```

This suggests the next diagnosis should compare:

- absolute `G:\...` report paths
- relative terminal-data-folder report paths
- report names with extension
- report names without extension

No conclusion should be treated as final without a reviewed preflight.

### Search Location Mismatch

The report may have been written somewhere other than the expected artifact folder, such as:

- MT5 terminal data folder
- Strategy Tester agent folder
- terminal working directory
- a normalized path under `MQL5\Files` or terminal common files

The next plan should define a deterministic search map before any retry.

### Extension Handling

Checkpoint AC requested `Report=...\mt5_report` without extension.

Previous artifacts show MT5 may create `.htm`, `.html`, and companion graph images.

A future runner plan should check all expected extensions and companion files:

- base path with no extension
- `.htm`
- `.html`
- `.xml`
- `.png`
- `-hst.png`
- `-mfemae.png`
- `-holding.png`

### Flush / Wait Timing

Because the tester and EA logs existed, report generation may have failed independently or report flush timing may have been missed.

The current evidence does not show companion graph files either, so timing alone is not the leading hypothesis, but a future runner should still wait for stable report and companion files.

## What Must Not Be Done Yet

Do not:

- rerun MT5
- run Strategy Tester again
- change strategy logic
- change Price Action / Fibo signal behavior
- optimize parameters
- increase lot or risk
- infer profitability
- start demo/live forward testing

## Recommended Next Checkpoint

Recommended next checkpoint:

`Checkpoint AE: MT5 Report Path Compatibility Preflight and Runner Plan`

Checkpoint AE should remain no-trade and should not run MT5 unless explicitly approved later.

It should define:

1. historical successful report pattern comparison
2. allowed `Report=` path candidates
3. expected MT5 write locations
4. stale artifact guard
5. exact report search matrix
6. stop conditions if report is missing
7. whether a runner-only fix is needed before another diagnostic execution

## Current Status After AD

Retry remains blocked.

No new MT5 execution is approved by this checkpoint.

Checkpoint AC remains `PARTIAL_TESTER_PASS_REPORT_MISSING`.

No-trade evidence from AC available logs remains useful but incomplete without the MT5 report artifact.

