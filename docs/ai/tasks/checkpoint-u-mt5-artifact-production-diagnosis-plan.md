# Checkpoint U: MT5 Artifact Production Diagnosis Plan

Created: 2026-07-02

## Purpose

Checkpoint U documents the failed/inconclusive Checkpoint T attempt and defines a safe diagnosis plan for why MT5 exited with code 0 without producing Strategy Tester artifacts.

This checkpoint does not rerun MT5, does not rerun Strategy Tester, does not change EA/source code, does not change presets, does not optimize, and does not approve demo/live trading.

## Checkpoint T Failure Summary

- RunId: `run_20260702_014627_checkpoint_t_paf_no_trade`
- Result: `FAILED_NO_TESTER_ARTIFACTS` / `INCONCLUSIVE`
- Symbol/timeframe: EURUSD H1
- Date range: `2026-01-01 to 2026-02-01`
- Observed behavior: spawned MT5 process exited quickly with exit code 0
- Required Strategy Tester artifacts were not produced

## What Is Not Proven

- no-trade behavior is `NOT_PROVEN`
- absence of baseline fallback is `NOT_PROVEN`
- Price Action / Fibo diagnostic classification output is `NOT_PROVEN`
- Strategy Tester execution path is `NOT_PROVEN`

## Diagnosis Questions

The next investigation must answer why the spawned terminal exited without producing required artifacts.

Areas to inspect:

- `terminal64.exe` path correctness
- MT5 data folder selection
- portable mode behavior
- whether `/config` was accepted by the terminal
- whether the generated `generated_tester.ini` file was valid for this MT5 build
- report path permissions
- whether the spawned terminal actually entered Strategy Tester mode
- whether an already-running MT5 terminal intercepted or ignored the config
- whether account/login/server/history availability blocked tester execution
- whether EA path was accepted
- whether symbol `EURUSD` was accepted by the broker/tester
- whether timeframe `H1` was accepted
- whether date range `2026-01-01 to 2026-02-01` was accepted
- where terminal logs, tester agent logs, and report files were written

## Required Log Locations To Collect Before Any Retry

Before a future retry is approved, identify and document the expected log/report paths:

- MT5 terminal log folder under the selected data folder
- Strategy Tester agent log folder under `%APPDATA%\MetaQuotes\Tester`
- report output folder requested by the tester config
- EA common file log folder under `%APPDATA%\MetaQuotes\Terminal\Common\Files`
- generated config path
- effective config snapshot path

The future retry plan must prove that these locations are writable and observable before execution.

## Artifact Path Preflight Requirements

A future retry must include a preflight that verifies:

- report directory exists
- report directory is writable
- generated tester config file exists
- tester config references the intended report path
- terminal data folder is the intended folder
- Strategy Tester agent log root exists or can be created
- EA mirror log target folder exists or can be written
- no stale report/log artifact will be mistaken for the new run

## Config Handoff Diagnosis

The diagnosis must determine whether:

- `/config:<path>` syntax was accepted
- relative vs absolute report path behavior is correct
- `Expert=ForexAiTrade\ForexAiTrade.ex5` resolves correctly
- the compiled `.ex5` exists in the expected MT5 data folder
- `Symbol=EURUSD` maps to an available broker symbol
- `Period=H1` is accepted
- `Optimization=0` is present and effective
- `FromDate` and `ToDate` are accepted by the tester

## Already-Running Terminal Risk

The diagnosis must check whether an already-running MT5 instance can:

- intercept the config request
- ignore the config request
- start the UI without running Strategy Tester
- close immediately without generating tester artifacts
- write logs to a different data folder

If this risk is confirmed or unresolved, the future retry must use a dedicated research terminal/process plan.

## Strict Retry Guardrails

No retry is allowed without a new explicit Checkpoint V approval.

Any retry must:

- be one run only
- use EURUSD H1 only unless a new reviewed checkpoint changes scope
- use a short approved diagnostic date range only
- include artifact path preflight
- prove tester log/report location before execution
- capture effective config before execution
- not change strategy/trading logic
- not change presets unless explicitly reviewed
- not optimize
- not increase lot/risk
- not claim profitability
- not approve demo/live/forward trading
- stop immediately if config, artifact path, or environment guardrails fail

## What Checkpoint U Does Not Approve

Checkpoint U does not approve:

- rerunning MT5
- rerunning Strategy Tester
- changing EA/source code
- changing presets
- optimization
- demo/live/forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability interpretation

## Next Safe Step

Send this diagnosis plan to GPT for review.

Only after GPT review and user approval should a separate Checkpoint V retry approval package be prepared.
