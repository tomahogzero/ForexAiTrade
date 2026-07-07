# ForexAiTrade Current Status

Last updated: 2026-07-07

## Repository State Observed

This AI memory has been refreshed during Checkpoint AK PAF diagnostic runner/parser integration:

- `origin/main`: `b02318c` (`Merge pull request #28 from tomahogzero/research/checkpoint-aj-gold-diagnostic-artifact-review`)
- PR #4 / Checkpoint N Price Action / Fibo diagnostics is merged.
- PR #5 / Javis Codex project memory is merged.
- PR #11 / Checkpoint T-Prep Fix is merged.
- PR #14 / Checkpoint W retry approval package with verified artifact paths is merged.
- PR #15 / Checkpoint X Gold 2-5% Monthly Research Framework is merged.
- PR #16 / Checkpoint Y Gold Diagnostic Data Requirements is merged.
- PR #17 / Checkpoint Z Gold no-trade diagnostic approval pack is merged.
- PR #18 / Checkpoint AA Gold diagnostic user evidence checklist is merged.
- PR #20 / Checkpoint AC Gold no-trade diagnostic run is merged.
- PR #21 / Checkpoint AD MT5 report artifact generation diagnosis is merged.
- PR #22 / Checkpoint AE MT5 report path compatibility preflight is merged.
- PR #23 / Checkpoint AF Codex-only self-review workflow is merged.
- PR #24 was a duplicate Codex-only workflow PR and was closed as superseded by PR #23.
- PR #25 / Checkpoint AG MT5 report runner hardening is merged.
- PR #26 / Checkpoint AH one-run retry approval package is merged.
- PR #27 / Checkpoint AI Gold no-trade diagnostic retry result is merged.
- PR #28 / Checkpoint AJ Gold diagnostic artifact review is merged.
- User requested a Codex-only self-review workflow so low-risk docs/planning checkpoints can proceed without GPT browser review.
- Checkpoint AF defines Codex-first / GPT-optional workflow.
- After Checkpoint AF is merged, Codex may self-review and auto-merge Tier 0/Tier 1 docs-only or runner-plan-only PRs when all guardrails pass.
- GPT review remains optional for low-risk docs/planning PRs and should be used only when requested or when Codex is unsure.
- Checkpoint AG is merged and adds runner-only hardening for MT5 report artifact collection.
- Checkpoint AH is a docs-only approval package for a future one-run Gold no-trade diagnostic retry. It does not run MT5.
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
- Checkpoint AB captured user-provided Gold preflight evidence.
- Verified Gold symbol: `GOLD#`.
- Verified MT5 Data Folder exists: `C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05`.
- Verified terminal executable exists: `C:\Program Files\XM Global MT5\terminal64.exe`.
- Verified report folder is writable: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts`.
- Process preflight initially found `terminal64.exe` still running.
- User then closed MT5 and Codex rechecked with `Get-Process terminal64`.
- Latest process preflight: no running `terminal64.exe` found.
- Current process blocker: `RESOLVED_BY_USER`.
- Checkpoint AC executed exactly one approved Gold no-trade diagnostic Strategy Tester run.
- Checkpoint AC RunId: `run_20260704_014343_checkpoint_ac_gold_no_trade`.
- Checkpoint AC result: `PARTIAL_TESTER_PASS_REPORT_MISSING`.
- Strategy Tester and EA mirror logs were produced.
- MT5 report artifact is missing.
- PriceActionFibo diagnostic lines: 552.
- No forbidden action markers found in available logs.
- No baseline fallback markers found in available logs.
- No-trade confirmation is based on tester/EA logs only, with report missing.
- Do not interpret Checkpoint AC as profitability evidence or a complete backtest report.
- Checkpoint AD diagnoses the missing MT5 report artifact without rerunning MT5.
- Checkpoint AD finding: AC narrowed the issue to report generation because tester/EA logs exist, but `mt5_report.htm` was not created.
- Likely root-cause areas include absolute `Report=` path compatibility, relative vs absolute report path behavior, report extension handling, search location mismatch, and report flush/wait behavior.
- Checkpoint AD does not approve a retry.
- Checkpoint AE defines a report-path compatibility preflight and runner plan without running MT5.
- Checkpoint AE historical finding: checked-in PASS reports use `Report=ForexAiTradeResearch\...\mt5_report` under the terminal data folder and produce `mt5_report.htm`.
- Checkpoint AE recommendation: do not use absolute `G:\...\mt5_artifacts\...\mt5_report` as the default report request until proven compatible.
- Checkpoint AE does not approve a retry.
- Checkpoint AF does not approve MT5 execution or source/preset changes; it only defines Codex self-review and low-risk auto-merge governance.
- Checkpoint AG updates the research batch runner to use terminal-data-folder relative report paths, detect fresh report artifacts only, copy MT5 report companion files, and separate `PARTIAL_TESTER_PASS_REPORT_MISSING` from `FAILED_NO_TESTER_ARTIFACTS`.
- Checkpoint AG does not approve MT5 execution and does not prove report generation until a later explicitly approved run.
- Checkpoint AH defines the future retry approval constraints for `GOLD#` H1, date range `2026-06-01` to `2026-07-01`, using runner-hardened relative MT5 report paths.
- Checkpoint AI executed the approved one-run Gold no-trade diagnostic retry with runner-hardened relative MT5 report paths.
- Checkpoint AI RunId: `run_20260707_020500_checkpoint_ai_gold_no_trade_retry`.
- Checkpoint AI result: `PASS_ARTIFACTS_COLLECTED`.
- Checkpoint AI created and copied `mt5_report.htm` plus companion graph files.
- Checkpoint AI no-trade confirmation: `PASS_FROM_TESTER_AND_EA_LOGS`.
- Checkpoint AI baseline fallback confirmation: `PASS_FROM_EA_LOGS`.
- Checkpoint AI forbidden action marker count: `0`.
- Checkpoint AI Price Action/Fibo diagnostic lines: `601`.
- Checkpoint AI is not profitability evidence and does not approve demo/live trading.
- Checkpoint AJ reviewed the Checkpoint AI artifacts without rerunning MT5.
- Checkpoint AJ finding: `mt5_report.htm` confirms `Total Trades=0` and `Total Deals=0`.
- Checkpoint AJ finding: authoritative EA mirror diagnostic count is `418`; the combined `601` count includes duplicate tester excerpt lines and should not be used as the main research count.
- Checkpoint AJ finding: EA mirror no-trade lines count is `502`.
- Checkpoint AJ finding: no forbidden order/pending/modify markers and no baseline fallback markers were found.
- Checkpoint AJ finding: `scripts/run_mt5_research_batch.ps1` still needs official PAF diagnostic case support before repeating this as a reusable matrix workflow.
- Checkpoint AK is in progress to add official PAF diagnostic runner/parser support without rerunning MT5.
- Checkpoint AK scope is runner/parser/research-template/docs only; it does not change EA/source code or presets.
- Checkpoint AK parser must treat `ea_mirror.log` as the authoritative PAF diagnostic source and count `tester_log_excerpt.log` separately to avoid duplicate totals.
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
4. Review Checkpoint AC result and missing report issue.
5. Do not rerun strategy diagnostics automatically.
6. After Checkpoint AK, the next safe step is Checkpoint AL: review or approval planning for a future one-run diagnostic execution using the official PAF runner/parser workflow. Do not run MT5 again until a new checkpoint explicitly approves it.
