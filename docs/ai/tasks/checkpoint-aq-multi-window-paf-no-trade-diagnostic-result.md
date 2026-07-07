# Checkpoint AQ: Multi-Window PAF No-Trade Diagnostic Result

## Objective

Execute the explicitly approved multi-window `GOLD#` H1 Price Action/Fibo diagnostic-only Strategy Tester run using the official AK runner/parser workflow.

## Approval

User approval phrase:

```text
Approved to execute Checkpoint AQ multi-window PAF no-trade diagnostics for GOLD# H1 with windows 2026-01-01 to 2026-02-01, 2026-02-01 to 2026-03-01, and 2026-03-01 to 2026-04-01 using official AK runner/parser workflow.
```

## Scope

Executed exactly:

- Symbol: `GOLD#`
- Timeframe: `H1`
- Windows:
  - `2026-01-01` to `2026-02-01`
  - `2026-02-01` to `2026-03-01`
  - `2026-03-01` to `2026-04-01`
- Strategy Tester only
- Diagnostic-only PAF path
- No optimization
- No demo/live/forward test
- No market orders
- No pending orders
- No position modification
- No lot/risk increase
- No profitability interpretation

## Result

RunId: `run_20260707_151857`

| Window | Execution | Report | Trades | Diagnostics | No-trade | Forbidden | Fallback |
|---|---|---|---:|---:|---:|---:|---:|
| AQ-W1 | PASS | FOUND | 0 | 386 | 474 | 0 | 0 |
| AQ-W2 | PASS | FOUND | 0 | 267 | 458 | 0 | 0 |
| AQ-W3 | PASS | FOUND | 0 | 301 | 506 | 0 | 0 |

No-trade confirmation: `PASS_FROM_REPORT_AND_EA_LOGS` for all windows.

Baseline fallback confirmation: `PASS_FROM_EA_LOGS` for all windows.

## Artifact Root

```text
G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260707_151857
```

## Notes

AQ-W3 has higher spread stats than AQ-W1/AQ-W2 and should be reviewed before any implementation-spec decision.

This result does not prove profitability and does not approve demo/live trading.

## Recommended Next Step

Checkpoint AR should be artifact review and diagnostic interpretation only. It should not implement market orders, pending orders, or optimization.
