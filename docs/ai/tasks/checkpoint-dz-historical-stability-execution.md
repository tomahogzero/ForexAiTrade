# Checkpoint DZ Historical Stability Execution

Date: 2026-07-11

## Scope

Executed the exact DY-approved diagnostic-only `GOLD#` H1 historical stability backtest across all 156 consecutive weekly windows from 2023-01-01 through 2025-12-28 using the official AK runner/parser workflow.

No optimization, demo/live forward test, EA/preset change, order logic, lot/risk increase, or profitability interpretation was included.

## Execution

- DZ-B1: `run_20260711_145612`, w001-w052, PASS
- DZ-B2: `run_20260711_152017`, w053-w104, PASS
- DZ-B3: `run_20260711_153941`, w105-w156, PASS
- reports and diagnostics: 156/156 found and fresh
- total trades: 0
- forbidden action markers: 0
- baseline fallback markers: 0
- runner stopped only spawned PIDs

## Frozen Results

- Fibo rows: 2353
- Fibo usable first-touch rows: 1600
- Fibo direction gaps: 753, fully attributed
- weak/watch/normal: 23/22/111
- weak share: 14.74%
- maximum consecutive weak run: 2
- annual weak windows: 6, 8, 9
- median usable: 9.5
- average usable: 10.2564

All frozen DY long-horizon criteria passed.

## Decision

- three-year long-horizon stability gate: `PASS`
- existing 20-window historical gate: `FAIL_REPORTED_SEPARATELY`
- later artifact-only rule-candidate readiness review: allowed
- rule candidate: not approved in DZ
- order logic: not approved
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

Next safe checkpoint: EA artifact-only rule-candidate readiness review. Do not run MT5, optimize, change EA/presets, add order logic, run demo/live tests, or claim profitability.
