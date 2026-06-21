# Backtest Smoke Test Plan

This phase verifies Strategy Tester behavior only. It is not optimization and it is not profitability proof.

## Purpose

- Confirm the EA compiles and runs inside MT5 Strategy Tester.
- Confirm tester-only presets cannot trade outside Strategy Tester.
- Confirm symbol diagnostics and risk blocks appear in the Journal.
- Confirm no runaway orders occur.
- Confirm lot sizing and safety checks behave as expected.

## Manual MT5 Strategy Tester Steps

1. Open MetaTrader 5.
2. Open Strategy Tester.
3. Select Expert: `ForexAiTrade`.
4. Select Symbol: `GOLDm#`.
5. Select Timeframe: `H1`.
6. Select Model: `Every tick based on real ticks` if available.
7. Select Period: last 3 months first.
8. Set Deposit: a small test amount, for example 1,000 or 10,000 demo currency units.
9. Load tester preset: `presets/tester/GOLDm#_H1_smoke_test.set`.
10. Run the test.
11. Export the report.
12. Check the Journal.
13. Confirm no runaway orders occurred.

## What To Check In Journal

- Symbol diagnostics printed on `OnInit`.
- Actual symbol is `GOLDm#`.
- Canonical symbol is `GOLD`.
- `InpRequireStrategyTester=true`.
- No messages suggesting real-account trading.
- Trade blocks are explicit when they occur.
- Signal logs, if generated, include entry, SL, TP, raw lot, normalized lot, risk money, actual risk money, and block reason.

## No-Trade Sanity Test

Use:

- `presets/sanity/GOLDm#_H1_no_trade_sanity.set`
- `presets/sanity/EURUSD_H1_no_trade_sanity.set`

Expected behavior:

- No orders open.
- Existing positions are not modified.
- Journal prints a safety block such as live trading disabled and position management disabled.

## Pass Conditions

- EA runs in Strategy Tester without platform errors.
- No uncontrolled order bursts occur.
- Tester-only presets are blocked outside Strategy Tester.
- No-trade sanity presets open and modify nothing.
- Risk blocks are understandable.

## Explicit Non-Goals

- Do not optimize parameters in this phase.
- Do not select best parameter sets.
- Do not claim profitability.
- Do not move to live trading based on a smoke test.
