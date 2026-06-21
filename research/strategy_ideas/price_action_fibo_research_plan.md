# Price Action / Fibo Research Plan

This is a future research plan only. It does not implement a strategy and does not approve demo/live trading.

## Purpose

Evaluate whether a Price Action / Fibo Zone strategy branch can improve risk-adjusted behavior versus the current EURUSD H1 baseline without increasing lot size, bypassing risk controls, or becoming a grid/martingale system.

## Baseline Reference

Current reference baseline:

- Symbol: EURUSD
- Timeframe: H1
- Baseline: normal losing-streak gate
- Status: RESEARCH_MORE
- Annual target classification: BELOW_FOREX_RISK_PREMIUM
- Checkpoint J recommendation: KEEP_NORMAL_GATE_AS_BASELINE

The baseline remains the reference. A new strategy must be tested separately and must not replace the baseline until it passes validation gates.

## Symbol Profile Separation

### EURUSD Baseline Profile

- EURUSD H1 remains the first research baseline.
- Future Price Action/Fibo implementation should start with EURUSD only.
- EURUSD results must be compared against the current EURUSD H1 baseline.
- EURUSD success does not imply success on other symbols.

### Other Forex Pairs Profile

- Other pairs such as USDJPY#, GBPUSD, or other broker-specific forex symbols must be validated separately.
- They may reuse the same conceptual Price Action/Fibo rules, but must not automatically reuse EURUSD parameters.
- Each symbol must have its own train, validation, and out-of-sample results.
- Each symbol must pass annual target and risk-adjusted viability checks independently.

### Gold Profile

- GOLD# / GOLDm# must be treated as a separate instrument class.
- Do not reuse EURUSD SL/TP, ATR, zone width, pending order spacing, or lot assumptions directly.
- Gold must use actual runtime broker metadata from `_Symbol`.
- Gold research must respect broker minimum lot and risk budget.
- Do not force broker minimum lot if it violates configured risk.
- Gold may require a larger research deposit assumption, but this is not a recommendation to trade that capital.
- Gold is not approved for demo/live forward testing until risk-budget issues are resolved.

## Future Implementation Boundary

Future implementation must be isolated as a separate strategy module, for example:

- `MQL5/Include/ForexAiTrade/Strategies/PriceActionFiboStrategy.mqh`
- `presets/research/price_action_fibo/`

It must use the existing RiskManager and execution safety gates.

## Required Test Splits

Use the established periods unless a later checkpoint explicitly changes them:

- train: 2023-01-01 to 2024-12-31
- validation: 2025-01-01 to 2025-12-31
- out_of_sample: 2026-01-01 to 2026-06-18

Positive train result alone cannot approve the strategy.

Validation and out-of-sample must both pass before any risk-adjusted viability label above research-only status is considered.

## Required Outputs

Every future Price Action/Fibo run must output:

- execution_status
- net profit
- profit factor
- max drawdown
- relative drawdown
- annualized return
- CAGR approximation
- Calmar ratio
- return-to-drawdown ratio
- trade count
- win rate
- max consecutive losses
- largest win/loss
- setup rejection counts
- pending order fill/cancel counts
- risk block counts

## Annual Target Framework

Checkpoint K target profile must be applied:

- Conservative Forex: CAGR >= 12%, max DD <= 15%, Calmar >= 0.8, PF >= 1.15
- Balanced Worth-The-Risk: CAGR >= 20%, max DD <= 15%, Calmar >= 1.0, PF >= 1.20
- Aggressive Research: research/demo only
- Challenge Mode: not allowed as baseline

A result with positive net profit but annualized return below 12% remains below Forex risk premium.

## Comparison Rules

Compare new strategy against baseline on:

- validation + OOS net profit
- validation + OOS annualized return
- max relative drawdown
- Calmar ratio
- profit factor
- trade count
- max consecutive losses
- session concentration
- spread sensitivity
- risk gate behavior

The new strategy must not be considered better if it only improves train or relies on one or two large trades.

## Safety Gates

The future strategy must prove:

- no martingale
- no recovery lot multiplication
- no unlimited grid
- no hidden floating loss behavior
- no order stacking beyond configured max exposure
- hard SL on every market/pending order
- pending orders cancel on invalidation

## Research Sequence

1. Implement minimal strategy module with telemetry only after specification review.
2. Run no-trade compile/sanity checks.
3. Run one-symbol EURUSD H1 diagnostic only.
4. Compare train/validation/OOS against baseline.
5. Apply annual target scoring.
6. Reject, revise specification, or mark RESEARCH_MORE.

No optimization and no demo/live forward testing are allowed from this plan alone.
