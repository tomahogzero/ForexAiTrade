# ForexAiTrade Current Status

Last updated: 2026-07-01

## Repository State Observed

This AI memory was created from the latest fetched `origin/main` available during onboarding:

- `origin/main`: `2c1ce2114a54ae612d8679fba6fdad07a7f934b4`
- This includes Checkpoint M merged into main.
- Checkpoint N diagnostics were not present in this `main` snapshot.

The root local checkout had unrelated dirty files before onboarding. The onboarding work was therefore performed in an isolated worktree to avoid mixing old local state into the PR.

## Current Build / Compile Tools Found

MT5 / MetaEditor:

- XM MetaEditor found at `C:\Program Files\XM Global MT5\MetaEditor64.exe`
- Past compile logs exist under `docs/verification/`
- Active EA path: `MQL5/Experts/ForexAiTrade/ForexAiTrade.mq5`

PowerShell scripts:

- `scripts/install_to_mt5.ps1`
- `scripts/collect_smoke_test_artifacts.ps1`
- `scripts/collect_ea_file_logs.ps1`
- `scripts/install_tester_profiles.ps1`
- `scripts/run_mt5_smoke_test.ps1`
- `scripts/run_mt5_research_batch.ps1`

Python research tools:

- `tools/research_report_parser.py`
- `tools/generate_research_summary.py`
- `tools/research_score.py`
- `tools/research_diagnostics.py`
- `tools/trade_ledger_parser.py`
- `tools/session_diagnostics.py`
- `tools/exit_telemetry_parser.py`
- `tools/exit_variant_analysis.py`
- `tools/risk_gate_attribution.py`
- `tools/risk_gate_variant_analysis.py`
- `tools/baseline_attribution_analysis.py`
- `tools/baseline_stability_analysis.py`
- `tools/annual_target_assessment.py`

## Current Backtest / Research Tools Found

Research matrices:

- `research/research_matrix.json`
- `research/exit_variant_matrix.json`
- `research/risk_gate_matrix.json`
- `research/target_profile.json`

Selected result summaries:

- `research/results/research_summary.md`
- `research/results/annual_target_assessment.md`
- `research/results/risk_gate_variant_summary.md`
- `research/results/checkpoint_j_risk_gate_recommendation.md`
- `research/results/baseline_stability_summary.md`
- `research/results/baseline_attribution_summary.md`

Known selected run:

- `run_20260621_214917`

## Current Known Risks

- Backtests are research artifacts only and do not prove future profitability.
- Current EURUSD H1 baseline remains `RESEARCH_MORE`, not demo/live ready.
- Annual target classification is `BELOW_FOREX_RISK_PREMIUM`.
- Train phase for baseline has negative or insufficient behavior.
- Trade count and period concentration can make annualized metrics misleading.
- Relaxing the losing-streak gate worsened validation and out-of-sample performance in Checkpoint J.
- Gold symbols require separate broker-specific risk-budget review.
- Price Action / Fibo is skeleton-only in current main and must not be treated as an active strategy.
- Local working tree may contain old uncommitted files from previous checkpoints.

## Current Safe Recommendation

Do not optimize.
Do not run MT5 Strategy Tester.
Do not start demo/live forward testing.
Do not increase lot/risk.

Recommended next action:

1. Review this AI memory PR.
2. Confirm whether Checkpoint N diagnostics should be merged after review.
3. Only after diagnostic code is reviewed and merged, consider a diagnostic-only run with `InpEnablePriceActionFibo=true` and all no-trade guardrails intact.
