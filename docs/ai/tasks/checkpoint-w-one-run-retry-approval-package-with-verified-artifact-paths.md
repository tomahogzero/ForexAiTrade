# Checkpoint W: One-Run Retry Approval Package With Verified Artifact Paths

Created: 2026-07-02

## Purpose

Checkpoint W defines the approval and preflight requirements for a future one-run retry of the Price Action / Fibo no-trade Strategy Tester diagnostic.

This checkpoint is documentation and approval-package work only.

It does not rerun MT5, does not run Strategy Tester, does not spawn `terminal64.exe`, does not change EA/source code, does not change presets, does not optimize, and does not approve demo/live trading.

## Context

Checkpoint T attempted one approved no-trade Strategy Tester diagnostic run.

Result:

`FAILED_NO_TESTER_ARTIFACTS` / `INCONCLUSIVE`

Important status:

- no-trade behavior: `NOT_PROVEN`
- baseline fallback absence: `NOT_PROVEN`
- Price Action / Fibo diagnostic classification output: `NOT_PROVEN`
- Strategy Tester artifact production: failed / inconclusive

Checkpoint V added investigation evidence:

- manual MT5 Strategy Tester can run on this machine
- manual tester produced a Balance/Equity graph
- manual visible context was GOLD,M1
- this proves manual Strategy Tester works in some context
- this does not prove command-line `/config` handoff works
- this does not prove EURUSD,H1 diagnostic path
- this does not prove no-trade behavior
- this does not prove no baseline fallback

## Approval Boundary

Checkpoint W does not approve a retry execution.

Retry remains blocked until:

- Checkpoint W is reviewed
- required preflight evidence is collected
- a later explicit user approval is provided

## Required Future Approval Phrase

The recommended future approval phrase is:

`Approved to execute Checkpoint W retry one-run diagnostic with date range YYYY-MM-DD to YYYY-MM-DD using verified artifact paths.`

Without this explicit approval phrase, concrete dates, and completed verified artifact paths, do not run MT5 or Strategy Tester.

## Retry Scope Constraints

Any future retry must remain exactly:

- one run only
- Symbol: EURUSD only
- Timeframe: H1 only
- date range must not exceed 1 month
- Strategy Tester only
- no optimization
- no demo/live/forward test
- no market orders
- no pending orders
- no position modification
- no lot/risk increase
- no profitability interpretation

## Required Preflight Evidence

Before any future retry approval can become executable, the following evidence must be documented.

### Terminal Executable

Required:

- exact `terminal64.exe` path
- proof the path is the same terminal installation used by the successful manual Strategy Tester run
- proof the executable exists

Current suspected path:

`C:\Program Files\XM Global MT5\terminal64.exe`

This must be re-confirmed before retry.

### Manual MT5 Data Folder

Required:

- manual MT5 data folder path copied from MT5 `File > Open Data Folder`
- confirmation that this is the XMGlobal-MT5 2 demo terminal used for the manual Strategy Tester graph
- comparison between manual data folder and automation target data folder

Known project data folder candidate:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05`

This must not be assumed. It must be verified again before retry.

### Portable Mode / Data Folder Mode

Required:

- explicitly state whether portable mode is used
- if portable mode is not used, explain how already-running terminal interception is prevented
- document whether spawned MT5 will use the same data folder or an isolated data folder
- if using an isolated data folder, document how EA source, compiled `.ex5`, account availability, symbol history, and logs are prepared there

### Running Terminal Process State

Required:

- read-only process list for `terminal64.exe` before retry planning
- determine whether another MT5 instance is already running
- determine whether it uses the same data folder as the intended retry
- if an already-running MT5 instance may intercept `/config` and cannot be controlled, retry must be blocked

The future retry plan must not bulk-kill terminal processes.

If any process is stopped, it must be an explicit, user-approved, dedicated research terminal process only.

### Absolute Strategy Tester Report Path

Required:

- absolute Strategy Tester report path
- no relative `Report=` path unless a reviewed preflight proves MT5 resolves it correctly
- exact expected report base path
- exact expected report extensions checked, such as `.htm`, `.html`, `.xml`

The Checkpoint T failure used a relative `Report=` path. A future retry should prefer an absolute path or document why absolute report paths are not supported by this MT5 build.

### Pre-Created Report Folder

Required:

- report folder exists before retry
- report folder is empty or stale files are cataloged
- retry RunId-specific report folder is unique
- no old artifacts can be mistaken as retry output

### Write Marker In Report Folder

Required:

- create a harmless preflight write marker before retry
- record marker filename, timestamp, and path
- delete marker only if a reviewed plan says to do so
- do not treat marker existence as Strategy Tester success

### Expected Terminal Log Folder

Required:

- exact terminal log folder for the retry terminal
- proof folder exists
- baseline timestamp before retry
- expected log filename for retry date

Candidate:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05\logs`

### Expected Tester Log Folder

Required:

- exact Strategy Tester agent log folder
- proof folder exists or can be observed
- expected log filename for retry date
- method for distinguishing retry log lines from older manual runs

Candidate:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Tester\BB16F565FAAA6B23A20C26C49416FF05\Agent-127.0.0.1-3000\logs`

### Expected EA / Mirror Log Folder

Required:

- exact EA mirror/common file folder
- proof folder exists
- exact expected EA mirror log filename
- method for proving the file was created by the retry

Candidate:

`C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\Common\Files`

### EURUSD H1 History Availability

Required:

- verify EURUSD exists in the intended terminal
- verify EURUSD H1 history availability for the approved date range
- if history availability cannot be proven without running Strategy Tester, document the limitation and require extra log checks after retry

Manual GOLD,M1 success is not enough to prove EURUSD,H1 availability.

### Tester Config Path

Required:

- exact generated tester config file path
- config file must be unique for the retry RunId
- config file must include `Optimization=0`
- config file must include approved symbol/timeframe/date range
- config file must include exact report path
- config file must be captured as an artifact before retry

### Effective Config / Generated `.set` Path

Required:

- exact effective config snapshot path
- exact generated `.set` or tester input snapshot path, if used
- required diagnostic inputs must match:
  - `InpEnablePriceActionFibo=true`
  - `InpPriceActionFiboDiagnosticsOnly=true`
  - `InpPAFUsePendingOrders=false`
  - `InpPAFMaxPendingOrders=0`
  - `InpManageExistingPositions=false`
  - `InpRequireStrategyTester=true`
  - `InpPAFLogOnlyOnNewBar=true`

### Exact Source / Preset Drift Guard

Required:

- future retry must record the exact source branch and commit before execution
- future retry artifacts must include the exact source branch and commit used
- Checkpoint W does not approve an execution source commit by itself
- the later retry approval checkpoint must name the reviewed execution target commit
- if the execution commit differs from the reviewed/approved target commit, Codex must prove and document that `MQL5/` and `presets/` have not changed
- if `MQL5/` or `presets/` changed from the approved target, retry remains blocked
- source or preset drift requires a new GPT review and a new explicit approval checkpoint before execution
- generated tester config and effective config artifacts must be traceable to the recorded source branch and commit

This guard prevents a retry from accidentally using a different EA source or preset set than the one reviewed for no-trade diagnostic execution.

### Stale Artifact Guard

Required:

- record pre-existing files in report folder
- record pre-existing EA mirror logs matching the planned pattern
- record pre-existing tester logs for the retry date
- compare timestamps after retry
- no old artifact may be reused as proof

## Explicit Stop Conditions

Block retry execution if any of these occur:

- terminal path unknown
- manual MT5 data folder unknown
- report folder not writable
- `/config` handoff not proven or not controlled
- already-running MT5 may intercept config and cannot be controlled
- EURUSD H1 history unavailable
- effective config mismatch
- missing artifact path preflight
- optimization enabled
- demo/live/forward environment detected
- date range exceeds 1 month
- symbol differs from EURUSD
- timeframe differs from H1
- retry would be more than one run
- strategy/trading logic changed without a new review
- presets changed without a new review
- exact source branch or commit is unknown
- execution commit differs from the reviewed target and `MQL5/` plus `presets/` drift has not been proven clean
- `MQL5/` or `presets/` changed from the approved target without a new GPT review and approval checkpoint

## Future Retry Required Artifacts

If a future retry is later approved and executed, collect:

- RunId
- exact source branch and commit
- exact terminal executable path
- exact terminal data folder
- process info for the spawned process
- generated tester config
- effective config snapshot
- report folder preflight marker evidence
- Strategy Tester report path
- terminal log excerpt
- tester log excerpt
- EA mirror log
- forbidden marker grep/check summary
- Price Action / Fibo diagnostic classification summary
- no-trade confirmation
- no baseline fallback confirmation

## Forbidden Marker Checks

Future retry artifact checks must inspect terminal/tester/EA logs and generated artifacts for:

- `OrderSend`
- `Buy`
- `Sell`
- `BuyLimit`
- `SellLimit`
- `BuyStop`
- `SellStop`
- `PositionModify`
- `SIGNAL_BUY`
- `SIGNAL_SELL`

Diagnostic text must be distinguished from actual trade-action attempts.

If ambiguous, the retry must not be classified as passed.

## What Checkpoint W Does Not Approve

Checkpoint W does not approve:

- running MT5
- running Strategy Tester
- spawning `terminal64.exe`
- changing EA/source code
- changing trading logic
- changing presets
- optimization
- demo/live/forward testing
- market orders
- pending orders
- position modification
- lot/risk increase
- profitability interpretation

## Recommended Next Step

Send this approval package to GPT for review.

If GPT passes the package, the next step may be a separate Checkpoint W execution approval with the exact phrase:

`Approved to execute Checkpoint W retry one-run diagnostic with date range YYYY-MM-DD to YYYY-MM-DD using verified artifact paths.`

Until then, retry remains blocked.
