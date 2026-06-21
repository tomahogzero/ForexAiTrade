# Controlled Research Pipeline

This phase separates MT5 execution reliability from strategy performance.

## Goals

- Do not optimize parameters yet.
- Do not tune entry or exit logic for profit yet.
- Run isolated MT5 research cases with unique artifacts.
- Parse MT5 reports into normalized JSON.
- Score results with survival-first gates.
- Keep train, validation, and out-of-sample results separate.

## Matrix

The research matrix is stored at:

```text
research/research_matrix.json
```

Each enabled case defines:

- actual broker symbol
- canonical symbol
- timeframe
- deposit
- leverage/model assumptions
- risk percent
- base preset reference

Initial symbols are:

- `EURUSD`
- `USDJPY#`
- `GOLD#`

Initial timeframes are:

- `H1`
- `H4`

Periods are:

- train: 2023-01-01 to 2024-12-31
- validation: 2025-01-01 to 2025-12-31
- out-of-sample: 2026-01-01 to 2026-06-18

## Run Artifacts

Every case is isolated under:

```text
research/runs/<RunId>/<CaseId>/
```

Expected files:

- `case.json`
- `generated_tester.ini`
- `effective_preset.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `mt5_report.html`
- `parsed_result.json`
- `status.json`

## Outputs

Research outputs are generated under:

```text
research/results/
```

Files:

- `all_results.csv`
- `all_scores.csv`
- `research_summary.md`

## Important

Execution status is not strategy performance. A losing but valid MT5 report is still `PASS` at the runner layer.

Profitability approval belongs only after validation and out-of-sample gates pass. These results are not proof of future profitability.
