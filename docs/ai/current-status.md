# ForexAiTrade Current Status

Last updated: 2026-07-04

## Repository State Observed

This AI memory has been refreshed after Checkpoint Y planning from the latest fetched `origin/main`:

- `origin/main`: `d19bcc0ed7a4b3ac264026de79d2b157eec44165`
- PR #4 / Checkpoint N Price Action / Fibo diagnostics is merged.
- PR #5 / Javis Codex project memory is merged.
- PR #11 / Checkpoint T-Prep Fix is merged.
- PR #14 / Checkpoint W retry approval package with verified artifact paths is merged.
- PR #15 / Checkpoint X Gold 2-5% Monthly Research Framework is merged.
- This includes Checkpoints M through T-Prep Fix merged into main.

The root local checkout may still contain unrelated dirty files from older research outputs. Do not clean, revert, delete, or stash those files without explicit user approval. Use an isolated worktree from `origin/main` for new checkpoint work.

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
- Gold 2-5% monthly research is an aggressive research target only, not a promise and not approval to increase lot/risk.
- Gold must remain a separate instrument class from EURUSD and other forex pairs.
- Price Action / Fibo diagnostics are merged, but they remain diagnostic-only and must not be treated as active trade signals.
- Price Action / Fibo diagnostic classifications must not be converted into market orders, pending orders, or position modification.
- Checkpoint T attempted exactly one no-trade Strategy Tester diagnostic execution.
- Checkpoint T result is `FAILED_NO_TESTER_ARTIFACTS` / `INCONCLUSIVE`.
- Checkpoint T RunId: `run_20260702_014627_checkpoint_t_paf_no_trade`.
- Checkpoint T did not produce the required Strategy Tester report/log path, tester log excerpt, EA mirror log, or Price Action / Fibo diagnostic classification summary.
- Checkpoint T no-trade behavior is `NOT_PROVEN`.
- Checkpoint T baseline fallback absence is `NOT_PROVEN`.
- Do not treat Checkpoint T as a successful diagnostic run.
- Do not rerun Checkpoint T automatically.
- Retry is blocked until a new reviewed checkpoint and explicit approval.
- Local working tree may contain old uncommitted files from previous checkpoints.

## Current Safe Recommendation

Do not optimize.
Do not run MT5 Strategy Tester.
Do not start demo/live forward testing.
Do not increase lot/risk.

Recommended next action:

1. Keep Checkpoint T as failed/inconclusive until verified artifacts exist.
2. Do not rerun MT5 or Strategy Tester without a new explicit approval.
3. For Gold research, require documentation and diagnostic requirements before any implementation.
4. Recommended next Gold step after Checkpoint Y review: Checkpoint Z, `Gold No-Trade Diagnostic Execution Approval Pack`.
