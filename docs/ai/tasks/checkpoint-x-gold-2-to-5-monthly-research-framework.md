# Checkpoint X: Gold 2-5% Monthly Research Framework

Created: 2026-07-04

## Purpose

Create a documentation-only research framework for Gold trading ideas with a user-interest target of 2-5% per month, while keeping capital preservation and project guardrails first.

This checkpoint does not approve implementation, optimization, MT5 execution, Strategy Tester execution, demo/live trading, or risk increases.

## Current Context

- PR #14 / Checkpoint W has been merged into `origin/main`.
- Checkpoint W added verified artifact path requirements before any future Strategy Tester retry.
- Checkpoint T remains `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`.
- No-trade behavior remains `NOT_PROVEN`.
- Baseline fallback absence remains `NOT_PROVEN`.
- Retry remains blocked until a new explicit approval with verified artifact paths.

## User Intent Captured

The user wants to research Gold because Gold can move strongly and quickly.

The user is interested in 2-5% monthly performance, but accepts that:

- the system may not reach the target
- some stopped-out months are acceptable
- keeping capital alive matters more than forcing return
- a systematic EA can control emotion better than discretionary trading
- human intuition can help but can also become self-deception

## Scope

Documentation and research planning only:

- summarize common global approaches to Gold trading
- define a risk-first 2-5% monthly research tier
- separate Gold from EURUSD/forex profiles
- define what diagnostics must exist before implementation
- define why no MT5 run or optimization is approved

## Popular Gold Research Directions

- trend following / momentum
- breakout / range expansion
- mean reversion in sideway regimes
- pullback continuation
- multi-timeframe filtering
- session filter research
- macro/event filter research
- ATR / volatility-based sizing
- exit telemetry and R-multiple analysis
- broker-specific risk budget review

## Gold-Specific Safety

Gold must be treated as a separate instrument class:

- actual broker symbol may be `GOLD#` or `GOLDm#`
- do not reuse EURUSD parameters
- do not assume tick/point/contract size
- do not force minimum lot
- respect risk budget before any test
- require broker metadata from actual runtime `_Symbol`

## Risk Target Interpretation

2-5% per month is an aggressive research target, not a promise.

It must not cause:

- lot increase
- risk increase
- martingale
- grid recovery
- recovery lot multiplication
- optimization for historical profit
- live/demo forward testing

## Next Recommended Safe Checkpoint

Checkpoint Y:

`Gold Diagnostic Data Requirements and No-Trade Signal Logging Plan`

Checkpoint Y should still avoid MT5 execution until the verified artifact path process from Checkpoint W is reviewed and a later explicit approval is provided.

