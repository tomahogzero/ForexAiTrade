# ForexAiTrade

ForexAiTrade is a MetaTrader 5 research project for adaptive forex trading with a capital-preservation-first design. The project focuses on robust EA architecture, broker-safe symbol handling, Strategy Tester safety gates, risk controls, and repeatable research artifacts.

## Current Research Status

Current baseline:

- `EURUSD H1`
- Status: `RESEARCH_MORE`
- Current checkpoint recommendation: `NEEDS_LOSING_STREAK_COOLDOWN_RESEARCH`

Checkpoint I2 showed that the EURUSD H1 train phase is heavily affected by losing-streak risk-gate lockout. Future research must separate raw strategy behavior from risk-gated behavior before any demo/live consideration.

## Safety Disclaimer

This is a trading research system, not a guaranteed-profit bot. Backtests, Strategy Tester runs, and research summaries are not proof of future profitability.

Do not use this EA on a live account. Live trading is not enabled by default and no demo/live forward test is approved unless a future checkpoint explicitly says so.

## Folder Structure

- `MQL5/` - MT5 EA source and include files
- `presets/` - safe, tester, sanity, and research presets
- `scripts/` - installation, artifact collection, and batch runner helpers
- `tools/` - Python parsers, scorers, and research analysis tools
- `docs/` - Thai/English checkpoint and workflow documentation
- `research/` - controlled matrices, runs, and selected research summaries

## Checkpoint Review Flow

Each checkpoint should:

- keep execution status separate from strategy performance
- document results under `docs/`
- generate focused research outputs under `research/results/`
- avoid optimization unless explicitly allowed
- avoid profitability claims
- package a clean review zip without binaries, caches, nested zips, or machine-specific state

See [docs/31_GitHub_Workflow_TH.md](docs/31_GitHub_Workflow_TH.md) for GitHub workflow guidance.
