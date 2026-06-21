# Annual Target Assessment

This assessment is a risk-adjusted research frame, not a profitability claim and not live/demo readiness.

Default target profile: `Balanced Worth-The-Risk`

## Target Tiers

| Tier | Min CAGR | Max DD | Min Calmar | Min PF | Notes |
|---|---:|---:|---:|---:|---|
| Survival Research | 0 | 10 | 0 |  | research only |
| Conservative Forex | 12 | 15 | 0.8 | 1.15 |  |
| Balanced Worth-The-Risk | 20 | 15 | 1.0 | 1.2 |  |
| Aggressive Research | 35 | 25 | 1.2 | 1.25 | demo/research only |
| Challenge Mode | 100 | 30 |  |  | research only, not baseline |

## Current Baseline: EURUSD H1 Normal Gate

| Phase | Net | PF | Rel DD | Trades | Days | Annualized | CAGR Approx | Calmar | Warning |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| train | -40.96 | 0.57 | 0.59 | 22 | 731 | -0.2045 | -0.2047 | -0.3466 | low_trade_count |
| validation | 61.38 | 1.16 | 0.63 | 105 | 365 | 0.6138 | 0.6138 | 0.9743 |  |
| out_of_sample | 41.03 | 1.18 | 0.59 | 62 | 169 | 0.8862 | 0.8883 | 1.502 | short_period |

## Validation + OOS Assessment

| Net | Min PF | Max Rel DD | Trades | Days | Annualized | CAGR Approx | Calmar | Classification |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 102.41 | 1.16 | 0.63 | 167 | 534 | 0.7 | 0.6989 | 1.1111 | BELOW_FOREX_RISK_PREMIUM |

## Interpretation

- Validation and out-of-sample are positive, but the absolute return is still small on a 10000 deposit.
- The baseline remains `RESEARCH_MORE`; it is not demo-forward ready and not a final candidate.
- The current result is not a reason to increase lot size or risk. Edge quality should improve before exposure size.
- Normal losing-streak gate remains the baseline after Checkpoint J.
- Annualized numbers can look attractive when drawdown is tiny, but they are still informational when trade count is limited or test windows are short.

## Verdict

The current baseline does not yet meet the minimum Forex risk premium target.

No optimization, lot increase, new strategy, or profitability claim was made.
