# Checkpoint AE: MT5 Report Path Compatibility Preflight and Runner Plan

Created: 2026-07-06

## Purpose

Define a safe report-path compatibility preflight and runner plan before any future retry of the Gold no-trade diagnostic.

This checkpoint is documentation and runner-plan only.

It does not run MT5, does not run Strategy Tester, does not spawn `terminal64.exe`, does not change EA/source code, does not change presets, does not optimize, does not increase lot/risk, and does not claim profitability.

## Context

PR #21 / Checkpoint AD has been merged.

Checkpoint AD diagnosed that Checkpoint AC produced Strategy Tester and EA diagnostic logs, but the MT5 report artifact was missing.

Current unresolved status:

- Checkpoint AC RunId: `run_20260704_014343_checkpoint_ac_gold_no_trade`
- Checkpoint AC status: `PARTIAL_TESTER_PASS_REPORT_MISSING`
- Tester log: produced
- EA mirror log: produced
- MT5 report artifact: missing
- Retry: blocked

## Historical Evidence Reviewed

Checked-in successful research reports show this pattern:

- 52 PASS examples used `Report=ForexAiTradeResearch\...\mt5_report`
- MT5 output was copied back as `mt5_report.htm`
- These report requests are relative to the terminal data folder, not absolute repo/artifact paths

Representative successful examples:

```text
research\runs\run_20260619_221606\GOLD_HASH_H4_10000_out_of_sample
Report=ForexAiTradeResearch\run_20260619_221606\GOLD_HASH_H4_10000_out_of_sample\mt5_report
status.report_path=...\mt5_report.htm
```

```text
research\runs\run_20260621_173616\GOLD_HASH_H4_30000_validation
Report=ForexAiTradeResearch\run_20260621_173616\GOLD_HASH_H4_30000_validation\mt5_report
status.report_path=...\mt5_report.htm
```

Checkpoint AC used:

```text
Report=G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701\mt5_report
```

and did not produce the report artifact.

## Compatibility Conclusion

Do not treat absolute `G:\...` report paths as the safe default.

The safest next plan is to use the historically successful pattern:

```text
Report=ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report
```

with the search base:

```text
<TerminalDataFolder>\ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report
```

This is not proof that all future runs will produce reports. It is only the lowest-risk path based on checked-in evidence.

## Runner Plan

If a later checkpoint changes runner behavior, it should be runner-only and should not touch EA/source code or presets.

Required runner behavior:

1. Require `TerminalDataFolder` for automated report-producing MT5 runs.
2. Generate `Report=ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report`.
3. Pre-create `<TerminalDataFolder>\ForexAiTradeResearch\<RunId>\<CaseId>\`.
4. Write a harmless marker file before execution.
5. Record the marker path and timestamp.
6. Search for `mt5_report*` only after run start time.
7. Search for `.htm`, `.html`, `.xml`, no-extension base file, and companion graph images.
8. Copy report and companion files back to the case artifact folder.
9. Record both terminal-side and copied artifact paths in `status.json`.
10. If tester/EA logs exist but report is missing, classify as `PARTIAL_TESTER_PASS_REPORT_MISSING`.
11. If tester/EA logs and report are missing, classify as `FAILED_NO_TESTER_ARTIFACTS`.
12. Never convert a missing-report result into a full pass.

## Suggested Future Status Fields

A future runner-only change may add these fields to `status.json`:

- `terminal_report_base_path`
- `terminal_report_path`
- `copied_report_path`
- `report_artifact_status`
- `report_companion_files`
- `report_search_locations`
- `report_preflight_marker_path`
- `report_preflight_marker_timestamp`
- `report_found_after_run_start`
- `stale_report_detected`

## Required Search Matrix

Future artifact collection should check:

```text
<base>
<base>.htm
<base>.html
<base>.xml
<base>.png
<base>-hst.png
<base>-mfemae.png
<base>-holding.png
```

Where `<base>` is:

```text
<TerminalDataFolder>\ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report
```

Optional debug-only search locations:

- case artifact folder
- terminal data folder root
- terminal logs folder
- tester agent logs folder
- terminal common files folder

Debug search locations must not be used to accept stale report files as proof.

## Preflight Evidence Required Before Any Future Retry

Before a future retry, document:

- exact `terminal64.exe`
- exact `TerminalDataFolder`
- no unrelated running `terminal64.exe` that can intercept `/config`
- source commit
- `MQL5/` and `presets/` drift status
- exact generated tester config path
- exact terminal-side report folder
- marker file write success
- stale report file inventory
- expected terminal log folder
- expected tester log folder
- expected EA mirror log folder
- approved symbol/timeframe/date range
- `Optimization=0`

## Explicit Non-Goals

Checkpoint AE does not approve:

- MT5 retry
- Strategy Tester run
- terminal spawn
- source code change
- preset change
- strategy tuning
- optimization
- lot/risk increase
- demo/live trading
- profitability interpretation

## Recommended Next Checkpoint

Recommended next checkpoint:

`Checkpoint AF: MT5 Report Path Runner-Only Hardening`

Checkpoint AF may implement runner-only report artifact hardening if GPT review passes this AE plan.

If no code change is needed, Checkpoint AF may instead be a reviewed one-run retry approval package that explicitly requires `TerminalDataFolder` and terminal-data-folder-relative `Report=`.

In either path, no MT5 execution is allowed without a separate explicit user approval.

