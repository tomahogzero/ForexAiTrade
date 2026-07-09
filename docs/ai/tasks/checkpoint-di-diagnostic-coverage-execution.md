# Checkpoint DI: Diagnostic Coverage Execution

Date: 2026-07-09

## Status

Executed exactly the approved Checkpoint DI diagnostic-only `GOLD#` H1 Strategy Tester coverage expansion.

RunId: `run_20260709_225603`

Artifact root: `G:\AiServer\Codex\ForexAiTrade\_checkpoint_di_diagnostic_coverage_exec_worktree\mt5_artifacts\run_20260709_225603\`

## Scope

- Symbol: `GOLD#`
- Timeframe: `H1`
- Windows:
  - `2026-04-26` to `2026-05-03`
  - `2026-05-03` to `2026-05-10`
  - `2026-05-10` to `2026-05-17`
  - `2026-05-17` to `2026-05-24`
  - `2026-05-24` to `2026-05-31`
  - `2026-05-31` to `2026-06-07`
  - `2026-06-07` to `2026-06-14`
- Strategy Tester only
- No optimization
- No demo/live forward test
- No EA/MQL5 change
- No preset change
- No order logic
- Total trades required to remain `0`

## Execution Result

All seven windows returned:

- `execution_status=PASS`
- report artifact `FOUND`
- `total_trades=0`
- PAF diagnostics `FOUND`
- forbidden action markers `0`
- baseline fallback markers `0`

DI totals:

- diagnostic rows: `678`
- possible setup rows: `210`
- usable direction rows: `143`
- Fibo Pullback rows: `114`
- Fibo usable first-touch rows: `99`
- Fibo direction gap rows: `15`

Combined CV + CY + DB + DI:

- diagnostic windows: `15`
- diagnostic rows: `1299`
- total usable direction rows: `249`
- Fibo Pullback rows: `242`
- Fibo usable first-touch rows: `184`
- Fibo direction gap rows: `58`

Gate decisions:

- window count >= `12`: `PASS`
- Fibo usable first-touch rows >= `150`: `PASS`
- total usable direction rows >= `300`: `FAIL`
- low-window weakness: `FAIL`
- rule-candidate gate: `FAIL`
- order-logic gate: `FAIL`

## Decision

- `DI_EXECUTION_PASS`
- `NO_TRADE_CONFIRMED_ALL_WINDOWS`
- `PAF_DIAGNOSTICS_FOUND_ALL_WINDOWS`
- `FORBIDDEN_MARKERS_ZERO`
- `BASELINE_FALLBACK_ZERO`
- `FIBO_USABLE_ROWS_GATE_PASS`
- `WINDOW_COVERAGE_GATE_PASS`
- `TOTAL_USABLE_DIRECTION_GATE_FAIL`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `NO_OPTIMIZATION_PERFORMED`
- `NO_PROFITABILITY_CLAIM`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## Next Safe Step

Checkpoint DJ should be artifact-only review of CV + CY + DB + DI. Do not run MT5, do not optimize, do not change EA/source code or presets, and do not add order logic.

