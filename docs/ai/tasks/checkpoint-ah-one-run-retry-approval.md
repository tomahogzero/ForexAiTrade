# Checkpoint AH: One-Run Retry Approval Package

## Status

Approval package only. No execution.

## Current Context

Checkpoint AG was merged on main as commit `f0d8a6b`, adding MT5 report artifact hardening to the research batch runner.

Checkpoint AC remains `PARTIAL_TESTER_PASS_REPORT_MISSING` because tester and EA logs were produced but the MT5 report artifact was missing.

Checkpoint AH prepares a narrow future retry approval for the same Gold no-trade diagnostic window so the team can test artifact production after the runner hardening.

## Guardrails

- Do not run MT5.
- Do not run Strategy Tester.
- Do not spawn `terminal64.exe`.
- Do not change EA/source code.
- Do not change presets.
- Do not optimize.
- Do not increase lot/risk.
- Do not claim profitability.
- Do not approve demo/live trading.

## Proposed Future Retry

- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-06-01` to `2026-07-01`
- Strategy Tester only
- One run only
- Diagnostic-only Price Action/Fibo path
- No market orders
- No pending orders
- No position modification

## Approved Source Baseline

Approved runner/source baseline for the future retry:

`f0d8a6b Merge pull request #25 from tomahogzero/research/checkpoint-ag-mt5-report-runner-hardening`

If a newer commit is used, execution must be blocked unless Codex proves and documents that `MQL5/`, `presets/`, and MT5 runner behavior have not drifted from the approved baseline. If they changed, a new review checkpoint is required.

## Required Report Path Mode

Future retry must use:

`Report=ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report`

The runner must pre-create:

`<TerminalDataFolder>\ForexAiTradeResearch\<RunId>\<CaseId>\`

and copy fresh report artifacts back to:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\<RunId>\<CaseId>\`

## Required User Approval Phrase

Execution remains blocked until the user explicitly says:

`Approved to execute Checkpoint AI one-run Gold no-trade diagnostic retry with symbol GOLD# timeframe H1 date range 2026-06-01 to 2026-07-01 using runner-hardened relative MT5 report paths.`

## Review Classification

This is docs-only / approval-package-only and is eligible for Codex self-review. It does not execute anything.

