# ForexAiTrade AI Context

Last updated: 2026-07-01

## Repository Purpose

ForexAiTrade is a MetaTrader 5 research project for adaptive forex trading with a capital-preservation-first design.

The repository contains:

- an MT5 Expert Advisor under `MQL5/`
- broker-safe symbol handling for XM-style symbols such as `GOLD#`, `GOLDm#`, `USDJPY#`, and standard forex symbols
- risk controls and execution safety gates
- safe/demo-first presets under `presets/`
- PowerShell helpers for MT5 installation, smoke tests, artifact collection, and controlled research batch runs
- Python tools for parsing MT5 reports, scoring robustness, aggregating diagnostics, annual target assessment, and research summaries
- checkpoint documentation under `docs/`
- controlled research matrices, runs, and selected summaries under `research/`

This is a trading research system, not a guaranteed-profit bot.

## Current Strategy Baseline

Current baseline from the checked-in repository:

- Symbol/timeframe: `EURUSD H1`
- Recommendation: `KEEP_NORMAL_GATE_AS_BASELINE`
- Research status: `RESEARCH_MORE`
- Annual target classification: `BELOW_FOREX_RISK_PREMIUM`

The baseline has positive validation and out-of-sample results in the selected research summaries, but the annualized return is still too small for the project's forex risk premium target. This is not a reason to increase lot size or risk.

## Current Strategy Branches

Implemented baseline strategy modules:

- `TrendFollowing.mqh`
- `Breakout.mqh`
- `MeanReversion.mqh`

Price Action / Fibo status in current `main`:

- Checkpoint L added specification-only research documents.
- Checkpoint M added a safe skeleton module.
- The skeleton is default disabled.
- It returns `SIGNAL_NONE`.
- It does not place market orders.
- It does not place pending orders.
- It does not modify positions.

## Core Safety Philosophy

Capital preservation comes first.

The system must avoid:

- live trading enabled by default
- parameter optimization unless explicitly allowed
- lot/risk increases to make metrics look better
- martingale
- uncontrolled grid recovery
- recovery lot multiplication
- RiskManager bypass
- forced broker minimum lot when it violates risk budget
- demo/live forward testing before explicit approval
- profitability claims from backtests

## Important Broker Context

The target broker/platform is XM MT5. Symbols may be broker-specific:

- `GOLD#` or `GOLDm#` instead of `XAUUSD`
- `USDJPY#`
- `EURUSD#`
- cash/index symbols such as `US100Cash`

EA code and tools should use runtime symbols from `_Symbol` and should preserve both actual broker symbols and canonical reporting symbols.

Gold must be treated as a separate broker-specific instrument class with risk-budget review. Do not reuse EURUSD parameters directly for Gold.

## How To Recover Context In A New Codex Chat

Start by reading these files in order:

1. `docs/ai/context.md`
2. `docs/ai/current-status.md`
3. `docs/ai/working-rules.md`
4. `README.md`
5. `docs/31_GitHub_Workflow_TH.md`
6. latest relevant checkpoint docs under `docs/`
7. `research/results/research_summary.md`
8. `research/results/annual_target_assessment.md`

Then inspect the active branch and local cleanliness:

```powershell
git status
git branch --show-current
git remote -v
```

If `main` is dirty, do not clean or revert unrelated user files. Use an isolated worktree from latest `origin/main` for new checkpoint work.

## Next Recommended Safe Step

Do not run backtests yet from this onboarding checkpoint.

The next safe step is a review-only pass of this AI project memory, then decide whether Checkpoint N diagnostics are already merged or still pending. If diagnostics are not merged, review and merge them before any further Price Action / Fibo research run.
