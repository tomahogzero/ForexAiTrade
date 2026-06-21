# ForexAiTrade

ForexAiTrade is a MetaTrader 5 research project for adaptive forex trading with a capital-preservation-first design. The project focuses on robust EA architecture, broker-safe symbol handling, Strategy Tester safety gates, risk controls, and repeatable research artifacts.

## Current Research Status

Current baseline:

- `EURUSD H1`
- Status: `RESEARCH_MORE`
- Current checkpoint recommendation: `KEEP_NORMAL_GATE_AS_BASELINE`
- Current annual target classification: `BELOW_FOREX_RISK_PREMIUM`

Checkpoint J showed that removing or relaxing the losing-streak gate increased trade count but worsened validation and out-of-sample performance. Checkpoint K adds an annual target and risk-adjusted viability framework so future work can compare results against Forex risk, not just positive net profit.

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
- evaluate annualized return, drawdown, Calmar ratio, profit factor, and trade count when performance improvement is claimed
- document results under `docs/`
- generate focused research outputs under `research/results/`
- avoid optimization unless explicitly allowed
- avoid profitability claims
- package a clean review zip without binaries, caches, nested zips, or machine-specific state

See [docs/31_GitHub_Workflow_TH.md](docs/31_GitHub_Workflow_TH.md) for GitHub workflow guidance.
