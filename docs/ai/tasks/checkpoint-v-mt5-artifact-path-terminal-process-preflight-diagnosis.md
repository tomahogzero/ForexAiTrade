# Checkpoint V: MT5 Artifact Path and Terminal Process Preflight Diagnosis

Created: 2026-07-02

## Purpose

Checkpoint V diagnoses the failed/inconclusive Checkpoint T artifact production path without rerunning MT5 or Strategy Tester.

This checkpoint is diagnosis/documentation only.

It does not spawn `terminal64.exe`, does not run Strategy Tester, does not change EA/source code, does not change presets, does not optimize, and does not approve demo/live trading.

## Source Context

- PR #12 / Checkpoint U has been merged.
- Checkpoint T RunId: `run_20260702_014627_checkpoint_t_paf_no_trade`
- Checkpoint T status: `FAILED_NO_TESTER_ARTIFACTS` / `INCONCLUSIVE`
- Symbol/timeframe: EURUSD H1
- Approved date range used in the failed attempt: `2026-01-01 to 2026-02-01`
- no-trade behavior: `NOT_PROVEN`
- baseline fallback absence: `NOT_PROVEN`
- Additional user-provided evidence after initial Checkpoint V drafting: a manual MT5 Strategy Tester run produced a Balance/Equity graph successfully.
- Manual visible tester context: XMGlobal-MT5 2 demo account, GOLD,M1 chart/tester context.
- This proves Strategy Tester can run manually on this machine, but it does not prove the automated `/config` handoff works.

## Existing Checkpoint T Artifacts Inspected

Local artifact folder inspected:

`G:\AiServer\Codex\ForexAiTrade\_checkpoint_t_exec_worktree\research\runs\run_20260702_014627_checkpoint_t_paf_no_trade\EURUSD_H1_PAF_DIAG_20260101_20260201`

Files present:

- `generated_tester.ini`
- `effective_config_snapshot.set`
- `process_info.json`
- `runner.log`
- `post_run_guardrail_summary.md`
- `post_run_guardrail_summary.json`
- `status.json`
- `case.json`
- `compile_before_run.log`
- `environment_log_excerpt.log`

Missing artifacts remain:

- Strategy Tester report
- Strategy Tester report/log path for the Checkpoint T run
- tester log excerpt for ForexAiTrade
- EA mirror log
- Price Action / Fibo diagnostic classification summary

## Observed Run Behavior From Artifacts

`process_info.json` shows:

- terminal executable: `C:\Program Files\XM Global MT5\terminal64.exe`
- generated config path: `G:\AiServer\Codex\ForexAiTrade\_checkpoint_t_exec_worktree\research\runs\run_20260702_014627_checkpoint_t_paf_no_trade\EURUSD_H1_PAF_DIAG_20260101_20260201\generated_tester.ini`
- spawned process ID: `51704`
- start time: `2026-07-02T01:48:00+07:00`
- stop policy: only spawned PID may be stopped on timeout

`runner.log` shows:

- spawned PID `51704`
- spawned PID exited with code `0`
- exit occurred approximately two seconds after launch
- artifacts were copied where available, but no report/EA/tester artifacts were produced

`status.json` shows:

- `FAILED_NO_TESTER_ARTIFACTS`
- rerun requires new approval

## Terminal Path Diagnosis

Observed terminal path:

`C:\Program Files\XM Global MT5\terminal64.exe`

File exists.

The path itself appears correct for the installed XM MT5 terminal.

Remaining risk:

- path correctness does not prove this executable used the intended data folder
- path correctness does not prove `/config` entered Strategy Tester mode
- path correctness does not prove an already-running instance did not intercept the request

User-provided manual evidence suggests the manual terminal is also XMGlobal-MT5 2 demo. The automation used the same apparent installed terminal executable path, but the failure mode is still consistent with a command-line handoff problem rather than a broken Strategy Tester installation.

## Generated Tester INI Diagnosis

Observed config file:

`generated_tester.ini`

Important values:

- `Expert=ForexAiTrade\ForexAiTrade.ex5`
- `Symbol=EURUSD`
- `Period=H1`
- `Optimization=0`
- `FromDate=2026.01.01`
- `ToDate=2026.02.01`
- `Report=ForexAiTradeResearch\run_20260702_014627_checkpoint_t_paf_no_trade\EURUSD_H1_PAF_DIAG_20260101_20260201\mt5_report`
- `ReplaceReport=1`
- `ShutdownTerminal=1`

The config appears conceptually aligned with the approval package.

Potential validity risks:

- `Report=` is relative, not absolute.
- MT5 may resolve a relative report path somewhere other than the intended data folder.
- `Expert=ForexAiTrade\ForexAiTrade.ex5` may not be the expected format for this MT5 build/config mode, even though previous scripts used a similar form.
- The config may have been ignored if an existing terminal instance handled the command line.

## Effective Config Diagnosis

`effective_config_snapshot.set` confirms the intended no-trade diagnostic settings:

- `InpEnablePriceActionFibo=true`
- `InpPriceActionFiboDiagnosticsOnly=true`
- `InpPAFUsePendingOrders=false`
- `InpPAFMaxPendingOrders=0`
- `InpManageExistingPositions=false`
- `InpRequireStrategyTester=true`
- `InpPAFLogOnlyOnNewBar=true`

This snapshot is correct as an intended config.

It does not prove MT5 actually loaded or applied it because no tester/EA logs were produced.

## Report Path Diagnosis

Intended terminal-side report folder:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05\ForexAiTradeResearch\run_20260702_014627_checkpoint_t_paf_no_trade\EURUSD_H1_PAF_DIAG_20260101_20260201`

Observed:

- folder exists
- folder was empty after the attempt
- no `mt5_report`, `mt5_report.htm`, `mt5_report.html`, or `mt5_report.xml` was produced there

Likely implication:

- MT5 did not execute the tester job, or
- MT5 resolved the relative report path somewhere else, or
- the config was ignored/intercepted before report creation

## Log Path Diagnosis

Likely terminal log folder:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05\logs`

Likely tester agent log folder:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Tester\BB16F565FAAA6B23A20C26C49416FF05\Agent-127.0.0.1-3000\logs`

Likely EA common file log folder:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\Common\Files`

Observed:

- terminal log folder exists
- tester agent log folder exists
- EA common files folder exists
- no Checkpoint T `ForexAiTrade` EA mirror log was found
- terminal log excerpt showed normal terminal login/sync activity, not a Checkpoint T Strategy Tester run
- tester agent log content around that day included unrelated `EA_ScalperM5M15` / `GOLD#` tests, not the Checkpoint T ForexAiTrade EURUSD H1 run

Manual Strategy Tester evidence changes the interpretation of these paths:

- Strategy Tester can generate visible results manually.
- The tester log root is therefore likely usable in general.
- The missing ForexAiTrade artifacts are more likely caused by automation/config handoff, report path resolution, or active-terminal interception than by a globally broken Strategy Tester.
- Future preflight must identify the exact log/report files created by a manual run and compare them with the expected automated run paths before any retry.

## Already-Running Terminal Diagnosis

Read-only process inspection found an existing `terminal64.exe` process:

- process path: `C:\Program Files\XM Global MT5\terminal64.exe`
- observed start time: `2026-07-02 01:35:45`

Checkpoint T spawned its process at approximately `01:48:00`.

This is a strong likely root cause:

- an already-running MT5 terminal may have intercepted the `/config` request
- the spawned process may have handed off to the existing terminal and exited with code 0
- the existing terminal may have ignored the config or opened UI focus only
- Strategy Tester mode may never have started

This matches the observed behavior:

- spawned PID exited quickly with code 0
- no tester report was produced
- no EA mirror log was produced
- no ForexAiTrade tester agent log was found

Manual Strategy Tester comparison:

- Manual testing occurs inside the already-open interactive terminal instance.
- Checkpoint T launched a second `terminal64.exe` process using `/config`.
- If MT5 allows only one active instance for a data folder, the second process may simply signal or hand off to the already-running instance and exit successfully.
- In that case, exit code 0 means the process launch/handoff succeeded, not that Strategy Tester executed the requested config.
- This is currently the strongest hypothesis because manual tester worked while the automation produced no tester artifacts.

## Portable Mode / Data Folder Diagnosis

Checkpoint T did not use a clearly isolated portable terminal mode.

Risk:

- the terminal may have used the default data folder
- an existing default-data-folder terminal may have taken precedence
- report/log paths may have been redirected to the active terminal instance or not processed at all

Future retry should not rely on default terminal instance behavior.

Manual terminal data folder evidence:

- The known MT5 data folder used by previous installation/testing is `C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05`.
- User reports the manual terminal is XMGlobal-MT5 2 demo, matching the visible account context previously used by this project.
- Future preflight must explicitly confirm the manual terminal data folder from MT5 `File > Open Data Folder` and compare it to the automation's intended data folder before any retry.

## Account / Login / Server / History Diagnosis

Existing terminal logs show the XM terminal had account authorization and synchronization around the same date.

This suggests account/login was probably available, but it does not prove the tester job started.

Manual Strategy Tester graph evidence strongly suggests:

- the terminal can authenticate sufficiently for manual tester use
- at least one symbol/timeframe/date context can run manually
- MT5 Strategy Tester itself is not globally blocked on this machine

Unknowns:

- whether Strategy Tester could access EURUSD H1 for `2026-01-01 to 2026-02-01`
- whether local history for EURUSD H1 was synchronized
- whether the tester rejected the symbol/date silently due config handoff failure

These cannot be resolved without a reviewed preflight and future explicit retry approval.

## Symbol / Timeframe / Date Range Diagnosis

Approved request:

- Symbol: EURUSD
- Timeframe: H1
- Date range: `2026-01-01 to 2026-02-01`

Config request:

- `Symbol=EURUSD`
- `Period=H1`
- `FromDate=2026.01.01`
- `ToDate=2026.02.01`

The config matches the approved scope.

Potential issue:

- broker Market Watch includes both suffix and non-suffix symbols in previous screenshots, but availability at tester time was not proven by artifact logs.
- future preflight should verify symbol availability and history without running a strategy test, if possible.

Manual tester context difference:

- manual run visible context: GOLD,M1
- failed automation target: EURUSD,H1

The manual GOLD,M1 success proves tester functionality, but it does not prove EURUSD,H1 history availability for `2026-01-01 to 2026-02-01`.

Future retry preflight must confirm EURUSD exists in the target terminal and that EURUSD H1 history for the approved date range is available or can be synchronized before any strategy execution.

## Manual Tester vs Automation Comparison

Manual run:

- user started or controlled Strategy Tester through the interactive MT5 UI
- visible tester graph was produced
- context observed by user: GOLD,M1
- proves local MT5 Strategy Tester can execute at least one manual test

Checkpoint T automation:

- spawned `C:\Program Files\XM Global MT5\terminal64.exe`
- passed `/config` pointing to generated tester config
- spawned process exited quickly with code 0
- no report was written
- no EA mirror log was written
- no ForexAiTrade tester log lines were found
- existing terminal process was already open before the spawn

Most important difference:

- manual tester used the already-running interactive terminal successfully
- automation attempted a command-line config handoff while another terminal instance was already running

This supports the hypothesis that the automation path failed before Strategy Tester execution.

## Exact Preflight Evidence Needed Before Retry

Before Checkpoint W can approve a retry, collect and document:

- screenshot or copied path from MT5 `File > Open Data Folder` for the manual terminal
- exact `terminal64.exe` path of the manual terminal
- currently running `terminal64.exe` process list before retry planning
- whether any terminal using the target data folder is already running
- exact terminal log folder for the manual terminal
- exact tester agent log folder that receives manual run logs
- exact report path behavior from a manual export or previous manual tester result
- whether `Report=` must be absolute or relative for this MT5 build
- whether `/config:<path>` requires portable mode, quoted path syntax changes, or terminal shutdown before launch
- whether `Expert=ForexAiTrade\ForexAiTrade.ex5` or `Expert=ForexAiTrade.ex5` is expected by this MT5 command-line tester mode
- whether EURUSD H1 history exists for `2026-01-01 to 2026-02-01`
- whether a pre-created report folder can receive a harmless write marker before retry
- how to prove stale logs/reports are not being mistaken for the retry artifacts

## Likely Root Causes

Most likely:

1. Existing MT5 terminal intercepted or ignored `/config`, causing the spawned process to exit quickly without entering Strategy Tester mode.
2. Relative `Report=` path may not have resolved to the intended output folder.
3. The config handoff was not proven; `/config` may not have been accepted as intended.

Secondary possible causes:

4. `Expert=` path format may not match what this MT5 build expects in command-line tester mode.
5. EURUSD/H1/date history may not have been available or synchronized, but no tester log proves this.
6. Logs may have been written to another data folder, but no matching ForexAiTrade logs were found in the expected common locations.

Manual Strategy Tester success reduces the likelihood that MT5 Strategy Tester is generally broken. It increases the likelihood that the failure is specific to automated process/config handoff, report path resolution, or target symbol/history mismatch.

## Checkpoint W Recommendation

Recommended next checkpoint:

`Checkpoint W: One-Run Retry Approval Package with Verified Artifact Paths`

Checkpoint W should still be approval/preflight only unless the user explicitly authorizes execution.

It should require:

- dedicated research terminal or isolated portable mode
- no already-running MT5 instance using the same data folder
- explicit comparison between manual terminal data folder and automation data folder
- proof that `/config` will not be intercepted by an existing terminal instance
- absolute report path or a proven MT5-supported report path
- pre-created report folder
- preflight write marker in report folder
- known tester agent log folder
- known terminal log folder
- known EA common files folder
- proven manual tester log/report location from the same terminal installation
- EURUSD H1 history availability check for the approved date range
- verification that stale artifacts cannot be confused with new artifacts
- explicit one-run-only approval phrase

## Retry Block

Retry remains blocked.

No MT5 or Strategy Tester retry is allowed until:

- GPT reviews this diagnosis
- a new Checkpoint W retry approval package is created and reviewed
- the user gives explicit approval for exactly one retry

## Guardrails

No strategy/trading logic changes are proposed.

No preset changes are proposed.

No optimization is proposed.

No lot/risk increase is proposed.

No profitability interpretation is allowed.

No demo/live trading is approved.
