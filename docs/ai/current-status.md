# ForexAiTrade Current Status

Last updated: 2026-07-08

## Repository State Observed

This AI memory has been refreshed during Checkpoint BM PAF offline result review plan:

- `origin/main`: `cb495fa` (`checkpoint-bl-prep: document real csv handoff`)
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
- PR #29 / Checkpoint AK PAF diagnostic runner/parser integration is merged.
- PR #30 / Checkpoint AL PAF diagnostic one-run approval package is merged.
- PR #31 / Checkpoint AM PAF diagnostic execution result is merged.
- PR #32 / Checkpoint AN PAF diagnostic artifact review is merged.
- PR #33 / Checkpoint AO PAF diagnostic coverage plan is merged.
- PR #34 / Checkpoint AP multi-window PAF no-trade diagnostic approval is merged.
- PR #35 / Checkpoint AQ multi-window PAF no-trade diagnostic result is merged.
- PR #36 / Checkpoint AR AQ PAF diagnostic artifact review is merged.
- PR #37 / Checkpoint AS PAF shadow-outcome labeling specification is merged.
- PR #46 / Checkpoint BC PAF lookahead bars validator is merged.
- PR #47 / Checkpoint BD PAF lookahead bars export approval is merged.
- PR #48 / Checkpoint BE PAF lookahead bars manual export guide is merged.
- PR #49 / Checkpoint BF PAF lookahead bars CSV intake validation is merged.
- PR #50 / Checkpoint BG PAF bars schema normalization plan is merged.
- PR #51 / Checkpoint BH PAF bars schema normalizer is merged.
- PR #52 / Checkpoint BI PAF offline pipeline self-test is merged.
- PR #53 / Checkpoint BJ PAF offline pipeline runner is merged.
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
- Checkpoint AK added official PAF diagnostic runner/parser support without rerunning MT5.
- Checkpoint AK scope is runner/parser/research-template/docs only; it does not change EA/source code or presets.
- Checkpoint AK parser must treat `ea_mirror.log` as the authoritative PAF diagnostic source and count `tester_log_excerpt.log` separately to avoid duplicate totals.
- Checkpoint AL is an approval-package-only checkpoint for a future one-run PAF diagnostic using the official AK workflow.
- Checkpoint AL does not run MT5 and does not approve execution by itself.
- User provided the exact Checkpoint AM approval phrase with date range `2026-06-01` to `2026-07-01`.
- Checkpoint AM executed exactly one Strategy Tester diagnostic run using the official AK runner/parser workflow.
- Checkpoint AM RunId: `run_20260707_121145`.
- Checkpoint AM case: `GOLD_HASH_H1_PAF_DIAG_AM_20260601_20260701_diagnostic_window`.
- Checkpoint AM result: `PASS`.
- Checkpoint AM report artifact status: `FOUND`.
- Checkpoint AM total trades: `0`.
- Checkpoint AM PAF diagnostic count from authoritative `ea_mirror.log`: `417`.
- Checkpoint AM no-trade lines: `502`.
- Checkpoint AM forbidden action marker count: `0`.
- Checkpoint AM baseline fallback marker count: `0`.
- Checkpoint AM no-trade confirmation: `PASS_FROM_REPORT_AND_EA_LOGS`.
- Checkpoint AM baseline fallback confirmation: `PASS_FROM_EA_LOGS`.
- Checkpoint AM is diagnostic-only evidence and does not approve demo/live trading, pending orders, market orders, or lot/risk increase.
- Checkpoint AN reviewed Checkpoint AM artifacts without rerunning MT5.
- Checkpoint AN finding: AM `417` vs AJ `418` diagnostic count differs only at `2026.06.29 01:00:00`.
- Checkpoint AN finding: AM classified that hour as `unsafe regime: spread too wide` with spread `115.0`, while AI/AJ logged a PAF `NO_SETUP` diagnostic for the same hour.
- Checkpoint AN finding: the one-line difference is a safety/filter classification difference, not order behavior.
- Checkpoint AN confirms AM safety review: total trades `0`, forbidden action markers `0`, baseline fallback markers `0`.
- Checkpoint AO is a planning-only checkpoint for future no-trade diagnostic coverage.
- Checkpoint AO recommendation: do not implement PAF entries or pending orders yet.
- Checkpoint AO proposed next step: Checkpoint AP approval package for 3 no-trade diagnostic windows, each no longer than 1 month.
- Checkpoint AP is an approval-package-only checkpoint for a future Checkpoint AQ multi-window PAF no-trade diagnostic run.
- Checkpoint AP does not run MT5, does not change EA/source, does not change presets, and does not approve order execution.
- Future Checkpoint AQ remains blocked until the user provides concrete date windows in the required approval phrase.
- User provided explicit approval for Checkpoint AQ with windows `2026-01-01` to `2026-02-01`, `2026-02-01` to `2026-03-01`, and `2026-03-01` to `2026-04-01`.
- Checkpoint AQ executed exactly 3 `GOLD#` H1 PAF no-trade diagnostic windows using the official AK runner/parser workflow.
- Checkpoint AQ RunId: `run_20260707_151857`.
- Checkpoint AQ result: all 3 windows `PASS`, report artifacts `FOUND`, total trades `0`, forbidden action markers `0`, baseline fallback markers `0`.
- Checkpoint AQ PAF diagnostic counts: W1 `386`, W2 `267`, W3 `301`.
- Checkpoint AQ no-trade line counts: W1 `474`, W2 `458`, W3 `506`.
- Checkpoint AQ artifact root: `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260707_151857`.
- Checkpoint AQ does not prove profitability and does not approve demo/live trading, market orders, pending orders, or lot/risk increase.
- Checkpoint AR reviewed Checkpoint AQ artifacts without rerunning MT5.
- Checkpoint AR classification: `PAF_DIAGNOSTIC_WORKFLOW_PASS`, `SHADOW_OUTCOME_SPEC_READY`, `NOT_READY_FOR_ORDER_IMPLEMENTATION`.
- Checkpoint AR finding: PAF labels appear across all 3 windows, but labels are not outcome evidence.
- Checkpoint AR finding: AQ-W3 has materially higher spread than W1/W2 and needs spread attribution before strategy-quality conclusions.
- Checkpoint AR recommendation: Checkpoint AS should define PAF shadow-outcome labeling before any order implementation.
- Checkpoint AS defines a no-order PAF shadow-outcome labeling specification.
- Checkpoint AS decision: `SHADOW_OUTCOME_SPEC_DEFINED`, `NO_ORDER_IMPLEMENTATION_APPROVED`, `NO_OPTIMIZATION_APPROVED`.
- Checkpoint AS requires deterministic entry references, explicit direction handling, pre-registered SL/TP/lookahead hypotheses, conservative same-bar ambiguity handling, and bucketed summaries by classification/regime/spread/volatility/session/window.
- Checkpoint AS does not implement a parser and does not run MT5.
- Checkpoint AT adds a no-order PAF shadow-outcome parser prototype that reads existing AQ artifacts only.
- Checkpoint AT does not run MT5, does not change EA/source code, and does not change presets.
- Checkpoint AT RunId parsed: `run_20260707_151857`.
- Checkpoint AT possible setup rows written: `267`.
- Checkpoint AT outcome labels: all `DIRECTION_MISSING`.
- Checkpoint AT finding: AQ diagnostics contain possible setup labels but lack direction context, entry reference price, and OHLC/tick lookahead needed for TP/SL shadow outcome labeling.
- Checkpoint AT decision: `PAF_SHADOW_OUTCOME_PARSER_PROTOTYPE_CREATED`, `AQ_SHADOW_OUTCOME_BLOCKED_BY_MISSING_DIRECTION`, `NO_ORDER_IMPLEMENTATION_APPROVED`, `NO_OPTIMIZATION_APPROVED`.
- Checkpoint AT recommendation: do not implement market orders or pending orders yet; first prepare a reviewed checkpoint to add richer diagnostic fields.
- Checkpoint AU defines the required diagnostic fields before shadow TP/SL outcome labeling can become meaningful.
- Checkpoint AU is documentation/research-plan only and does not change EA/source code, presets, scripts, or tools.
- Checkpoint AU required future fields include `direction_context`, `direction_reason`, `entry_reference_price`, diagnostic bar OHLC, ATR/volatility context, and optional exported OHLC lookahead data.
- Checkpoint AU decision: `PAF_DIAGNOSTIC_FIELD_REQUIREMENTS_DEFINED`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint AU recommendation: next safe checkpoint can request a narrow diagnostic-logging-only EA change, still with no market orders, no pending orders, no position modification, no optimization, and no demo/live approval.
- Checkpoint AV adds diagnostic-logging-only fields to the Price Action / Fibo strategy and updates the shadow outcome parser to read `direction_context`.
- Checkpoint AV changed MQL5 diagnostic logging only; `CPriceActionFiboStrategy::Evaluate()` still returns `SIGNAL_NONE`.
- Checkpoint AV added diagnostic fields: `direction_context`, `direction_reason`, `entry_reference_price`, `bar_open`, `bar_high`, `bar_low`, `bar_close`, `atr`, `ema_fast`, `ema_slow`, and `bb_width_percent`.
- Checkpoint AV compile result: `0 errors, 0 warnings`.
- Checkpoint AV did not run MT5 or Strategy Tester and did not change presets.
- Checkpoint AV decision: `PAF_DIAGNOSTIC_LOGGING_FIELDS_ADDED`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint AV recommendation: next safe checkpoint should be an approval package for one no-trade diagnostic run to verify the new fields appear in `ea_mirror.log`.
- Checkpoint AW creates an approval package for exactly one future no-trade PAF diagnostic field verification run.
- Checkpoint AW does not run MT5 or Strategy Tester and does not change source code or presets beyond the already-open Checkpoint AV PR branch.
- Checkpoint AW proposed future verification scope: `GOLD#` H1 from `2026-03-01` to `2026-03-08`.
- Checkpoint AW requires the future run to confirm new fields in `ea_mirror.log`: `direction_context`, `direction_reason`, `entry_reference_price`, bar OHLC, `atr`, `ema_fast`, `ema_slow`, and `bb_width_percent`.
- Checkpoint AW execution remains blocked until the user provides the exact approval phrase.
- Checkpoint AW decision: `PAF_FIELD_VERIFICATION_APPROVAL_PACKAGE_CREATED`, `EXECUTION_STILL_BLOCKED_UNTIL_USER_APPROVAL`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- User provided the exact approval phrase for Checkpoint AX.
- Checkpoint AX executed exactly one approved `GOLD#` H1 PAF no-trade diagnostic field verification run.
- Checkpoint AX RunId: `run_20260707_172236`.
- Checkpoint AX date range: `2026-03-01` to `2026-03-08`.
- Checkpoint AX installed latest merged source into the XM MT5 data folder and compiled the active EA before execution.
- Checkpoint AX compile result: `0 errors, 0 warnings`.
- Checkpoint AX runner spawned MT5 PID `15108` and closed only that spawned process after detecting the report artifact.
- Checkpoint AX result: `PASS`.
- Checkpoint AX report artifact status: `FOUND`.
- Checkpoint AX total trades: `0`.
- Checkpoint AX authoritative PAF diagnostic source: `ea_mirror.log`.
- Checkpoint AX PAF diagnostic count: `97`.
- Checkpoint AX required diagnostic fields were present in all 97 PAF diagnostic lines: `direction_context`, `direction_reason`, `entry_reference_price`, bar OHLC, `atr`, `ema_fast`, `ema_slow`, and `bb_width_percent`.
- Checkpoint AX direction context counts across diagnostic lines: `BUY_CONTEXT=9`, `SELL_CONTEXT=10`, `DIRECTION_UNKNOWN=78`.
- Checkpoint AX forbidden action marker count: `0`.
- Checkpoint AX baseline fallback marker count: `0`.
- Checkpoint AX shadow outcome parser rows: `33` possible setups.
- Checkpoint AX shadow outcome labels: `DATA_MISSING=19`, `DIRECTION_MISSING=14`.
- Checkpoint AX readiness: `BLOCKED_BY_MISSING_LOOKAHEAD_DATA`.
- Checkpoint AX decision: `PAF_FIELD_VERIFICATION_PASS`, `NO_TRADE_DIAGNOSTIC_CONFIRMED`, `SHADOW_OUTCOME_BLOCKED_BY_MISSING_LOOKAHEAD_DATA`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint AY defines a documentation-only plan for PAF OHLC/tick lookahead export.
- Checkpoint AY does not change EA/source code, presets, scripts, or tools.
- Checkpoint AY does not run MT5 or Strategy Tester.
- Checkpoint AY recommendation: prefer offline bar-series artifact export and parser matching rather than adding future-aware logic into EA `Evaluate()`.
- Checkpoint AY requires lookahead data to remain offline-only and never feed trading decisions.
- Checkpoint AY decision: `LOOKAHEAD_EXPORT_PLAN_DEFINED`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint AZ adds `tools/paf_lookahead_joiner.py`, an offline-only tool for joining PAF shadow rows with a provided OHLC bar CSV.
- Checkpoint AZ does not change EA/source code or presets.
- Checkpoint AZ does not run MT5 or Strategy Tester.
- Checkpoint AZ tool outputs enriched shadow rows and a lookahead summary when a valid `paf_lookahead_bars.csv` is provided.
- Checkpoint AZ keeps lookahead data outside the EA decision path and does not approve order implementation.
- Checkpoint AZ decision: `OFFLINE_LOOKAHEAD_JOINER_ADDED`, `ORDER_PATH_STILL_BLOCKED`, `NO_MT5_RUN`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BA defines the required `paf_lookahead_bars.csv` artifact checklist and schema for the first offline PAF lookahead join.
- Checkpoint BA does not run the offline joiner, MT5, or Strategy Tester.
- Checkpoint BA target context for the first offline join remains `run_20260707_172236`, `GOLD#`, `H1`, diagnostic range `2026-03-01` to `2026-03-08`.
- Checkpoint BA recommends bar coverage through at least `2026-03-10 23:59:59` to support 48 H1 bars of lookahead.
- Checkpoint BA adds `research/templates/paf_lookahead_bars_schema.csv` as a schema example only.
- Checkpoint BA future approval phrase: `Approved to execute Checkpoint BB offline PAF lookahead join with bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`
- Checkpoint BA decision: `LOOKAHEAD_BARS_CHECKLIST_DEFINED`, `OFFLINE_JOIN_NOT_RUN`, `MT5_STILL_BLOCKED`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BB-Prep runs `tools/paf_lookahead_joiner.py` against synthetic fixtures only.
- Checkpoint BB-Prep does not use real market data, does not run MT5, and does not run Strategy Tester.
- Checkpoint BB-Prep self-test result: `PASS`.
- Checkpoint BB-Prep expected labels were confirmed: `TP_FIRST`, `SL_FIRST`, `AMBIGUOUS_SAME_BAR`, and `DIRECTION_MISSING`.
- Checkpoint BB-Prep decision: `LOOKAHEAD_JOINER_SELFTEST_PASS`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `MT5_STILL_BLOCKED`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BC adds `tools/paf_lookahead_bars_validator.py`, an offline-only validator for `paf_lookahead_bars.csv`.
- Checkpoint BC validator checks required columns, timestamp parsing, OHLC numeric parsing, exact diagnostic event timestamp matching, lookahead horizon coverage, and large timeframe gaps.
- Checkpoint BC self-test used synthetic Checkpoint BB-Prep fixtures only.
- Checkpoint BC self-test result: `PASS`.
- Checkpoint BC self-test matched events: `4/4`, missing events: `0`, gap count: `0`.
- Checkpoint BC decision: `LOOKAHEAD_BARS_VALIDATOR_ADDED`, `VALIDATOR_SELFTEST_PASS`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `MT5_STILL_BLOCKED`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BD defines a documentation-only approval/preflight package for future creation or export of real `paf_lookahead_bars.csv`.
- Checkpoint BD target context remains `run_20260707_172236`, `GOLD#`, `H1`, diagnostic range `2026-03-01` to `2026-03-08`.
- Checkpoint BD requires bar coverage through at least `2026-03-10 23:59:59` for the 48 H1 lookahead horizon.
- Checkpoint BD does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, and does not run the offline join.
- Checkpoint BD future export approval phrase: `Approved to execute Checkpoint BE one-time GOLD# H1 bars export for PAF lookahead with date range 2026-03-01 to 2026-03-10 using verified XM MT5 history only.`
- Checkpoint BD keeps the Checkpoint BB offline join approval phrase unchanged for after a validated CSV exists.
- Checkpoint BD decision: `BARS_EXPORT_APPROVAL_PACKAGE_DEFINED`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `OFFLINE_JOIN_NOT_RUN`, `MT5_STILL_BLOCKED_UNTIL_EXPLICIT_EXPORT_APPROVAL`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BE defines a manual export guide for creating `paf_lookahead_bars.csv` from XM MT5 `GOLD#` H1 history.
- Checkpoint BE does not run MT5 by Codex, does not run Strategy Tester, does not change EA/source code, does not change presets, and does not run the offline join.
- Checkpoint BE target artifact remains `paf_lookahead_bars.csv` for RunId `run_20260707_172236`, `GOLD#`, `H1`, with required coverage from `2026-03-01 00:00:00` through at least `2026-03-10 23:59:59`.
- Checkpoint BE decision: `MANUAL_EXPORT_GUIDE_DEFINED`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `OFFLINE_JOIN_NOT_RUN`, `MT5_NOT_RUN_BY_CODEX`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BF defines a docs-only intake and validation gate for a future real `paf_lookahead_bars.csv`.
- Checkpoint BF requires validator execution before any offline joiner attempt.
- Checkpoint BF classifications include `INTAKE_BLOCKED_NO_FILE`, `SCHEMA_CONVERSION_REQUIRED`, `VALIDATOR_FAIL_NEEDS_FIX`, `NON_BROKER_COMPARABLE_DIAGNOSTIC_ONLY`, and `VALIDATOR_PASS_READY_FOR_JOIN`.
- Checkpoint BF does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, does not run validator, and does not run joiner.
- Checkpoint BF decision: `CSV_INTAKE_VALIDATION_GATE_DEFINED`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `VALIDATOR_NOT_RUN`, `JOINER_NOT_RUN`, `MT5_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BG defines a documentation-only schema normalization plan for future MT5-exported OHLC bar files.
- Checkpoint BG allows only format-level transformations such as column renaming, date/time combining, delimiter conversion, and timestamp formatting without timezone shift.
- Checkpoint BG forbids OHLC price edits, unsourced missing-bar fills, undocumented timezone shifts, resampling without a separate checkpoint, and any use of lookahead data inside EA decisions.
- Checkpoint BG proposes a future offline-only tool candidate `tools/paf_bars_schema_normalizer.py`, but does not implement it in this checkpoint.
- Checkpoint BG decision: `SCHEMA_NORMALIZATION_PLAN_DEFINED`, `NORMALIZER_TOOL_NOT_IMPLEMENTED`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `VALIDATOR_NOT_RUN`, `JOINER_NOT_RUN`, `MT5_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BH adds `tools/paf_bars_schema_normalizer.py`, an offline-only schema normalizer for MT5-style OHLC CSV exports.
- Checkpoint BH supports MT5-style columns such as `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, and `<CLOSE>`.
- Checkpoint BH preserves the raw CSV copy, writes a normalized `time,open,high,low,close` CSV, and writes JSON/Markdown normalization summaries.
- Checkpoint BH self-test uses synthetic fixture data only, not real market data.
- Checkpoint BH self-test result: syntax check `PASS`, normalization verdict `PASS`, and validator verdict on normalized synthetic fixture `PASS`.
- Checkpoint BH does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, and does not run joiner on real data.
- Checkpoint BH decision: `SCHEMA_NORMALIZER_TOOL_ADDED`, `SCHEMA_NORMALIZER_SELFTEST_PASS`, `NORMALIZED_OUTPUT_VALIDATOR_PASS_ON_SYNTHETIC_FIXTURE`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `JOINER_NOT_RUN_ON_REAL_DATA`, `MT5_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BI runs an offline synthetic end-to-end self-test of raw MT5-style bars CSV -> schema normalizer -> bars validator -> lookahead joiner.
- Checkpoint BI self-test result: syntax check `PASS`, normalization verdict `PASS`, validation verdict `PASS`, and joiner `JOINED=2` on synthetic fixture rows.
- Checkpoint BI outcome labels on synthetic fixture: horizon 1 `TP_FIRST=1`, `SL_FIRST=1`; horizon 2 `TP_FIRST=1`, `SL_FIRST=1`.
- Checkpoint BI does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, and does not process real market data.
- Checkpoint BI decision: `OFFLINE_PIPELINE_SELFTEST_PASS`, `NORMALIZER_VALIDATOR_JOINER_CHAIN_PASS_ON_SYNTHETIC_FIXTURE`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `JOINER_NOT_RUN_ON_REAL_DATA`, `MT5_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BJ adds `tools/paf_offline_pipeline_runner.py`, an offline-only runner for raw/normalized bars CSV -> normalize -> validate -> join.
- Checkpoint BJ self-test uses synthetic fixture data only.
- Checkpoint BJ self-test result: syntax check `PASS`, runner verdict `PASS`, normalize stage `PASS`, validate stage `PASS`, join stage `PASS`, and `JOINED=2`.
- Checkpoint BJ runner stop gate: if normalization or validation fails, downstream stages are not run.
- Checkpoint BJ does not run MT5, does not run Strategy Tester, does not change EA/source code, does not change presets, and does not process real market data.
- Checkpoint BJ decision: `OFFLINE_PIPELINE_RUNNER_ADDED`, `OFFLINE_PIPELINE_RUNNER_SELFTEST_PASS`, `NORMALIZE_VALIDATE_JOIN_CHAIN_PASS_ON_SYNTHETIC_FIXTURE`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `JOINER_NOT_RUN_ON_REAL_DATA`, `MT5_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BK defines a documentation-only approval package for a future offline pipeline run against a real `GOLD#` H1 CSV path.
- Checkpoint BK target context remains RunId `run_20260707_172236`, `GOLD#`, `H1`, diagnostic range `2026-03-01` to `2026-03-08`, with required lookahead coverage through at least `2026-03-10 23:59:59`.
- Checkpoint BK does not run the offline pipeline, does not run MT5, does not run Strategy Tester, does not change EA/source code, and does not change presets.
- Checkpoint BK future approval phrase: `Approved to execute Checkpoint BL offline PAF pipeline on real GOLD# H1 bars CSV <absolute_path_to_csv> for RunId run_20260707_172236.`
- Checkpoint BK decision: `REAL_CSV_OFFLINE_RUN_APPROVAL_PACKAGE_DEFINED`, `REAL_MARKET_LOOKAHEAD_CSV_STILL_MISSING`, `OFFLINE_RUN_NOT_EXECUTED`, `MT5_NOT_RUN`, `STRATEGY_TESTER_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BL-Prep defines a documentation-only handoff guide for preparing the real `GOLD#` H1 CSV file required before Checkpoint BL can run the offline pipeline.
- Checkpoint BL-Prep recommends placing the CSV under `G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_exports\` with a filename such as `GOLD_HASH_H1_20260301_20260310_raw_mt5.csv`.
- Checkpoint BL-Prep does not run MT5, does not run Strategy Tester, does not run the offline pipeline, does not change EA/source code, and does not change presets.
- Checkpoint BL-Prep decision: `REAL_CSV_HANDOFF_GUIDE_DEFINED`, `REAL_CSV_PATH_STILL_REQUIRED`, `OFFLINE_PIPELINE_NOT_RUN`, `MT5_NOT_RUN`, `STRATEGY_TESTER_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Checkpoint BM defines a documentation-only review plan for future offline PAF pipeline outputs after a real `GOLD#` H1 CSV is provided and Checkpoint BL is explicitly approved.
- Checkpoint BM defines review classifications such as `OFFLINE_PIPELINE_PASS_REVIEWABLE`, `VALIDATOR_FAIL_NEEDS_FIX`, `COVERAGE_INSUFFICIENT`, `EVENT_MATCH_INSUFFICIENT`, `DIRECTION_CONTEXT_INSUFFICIENT`, `AMBIGUITY_TOO_HIGH`, `SAMPLE_TOO_SMALL`, and `REJECT_ORDER_PATH_FOR_NOW`.
- Checkpoint BM explicitly prohibits interpreting shadow outcomes as `PROFITABLE`, `LIVE_READY`, `DEMO_READY`, `ORDER_APPROVED`, or `OPTIMIZATION_READY`.
- Checkpoint BM does not run MT5, does not run Strategy Tester, does not run the offline pipeline, does not change EA/source code, and does not change presets.
- Checkpoint BM decision: `OFFLINE_RESULT_REVIEW_PLAN_DEFINED`, `REAL_CSV_PATH_STILL_REQUIRED`, `OFFLINE_PIPELINE_NOT_RUN`, `MT5_NOT_RUN`, `STRATEGY_TESTER_NOT_RUN`, `ORDER_PATH_STILL_BLOCKED`, `NO_OPTIMIZATION_APPROVED`, `NO_PROFITABILITY_CLAIM`.
- Current progress estimate: research-system readiness around `79%`; PAF diagnostic readiness around `70%`; PAF shadow-outcome readiness around `68%`; real-money bot readiness around `10-15%`; demo/live readiness remains `0%`.
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
6. After Checkpoint BM, the next safe step is to receive a real raw or normalized `GOLD#` H1 bars CSV absolute path from the user and run the offline pipeline runner only under explicit Checkpoint BL approval. Do not run Strategy Tester or implement entries/pending orders yet.
