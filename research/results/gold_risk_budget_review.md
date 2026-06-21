# GOLD# Risk-Budget Review

This note reviews the GOLD# no-risk-budget issue from Checkpoint D. It is a research note only, not a recommendation to trade GOLD# or increase live capital.

## Current Settings

- Actual broker symbol: `GOLD#`
- Canonical symbol: `GOLD`
- Current research risk: `0.05%`
- Broker minimum lot observed in diagnostics: `0.01`
- Research deposit tested: `30000`

## Estimated Minimum Deposit

| Phase | Estimated Minimum Deposit |
|---|---:|
| train | 44776.12 |
| validation | 71428.57 |
| out_of_sample | 130434.78 |

## Interpretation

- The `30000` deposit is below the estimated minimum needed for validation and out-of-sample when using the current risk percent, current stop distances, and broker minimum lot.
- This is a risk-budget constraint, not automatically a strategy failure.
- The EA should not force the broker minimum lot when doing so would violate the configured risk budget.
- The EA should not increase risk automatically to make a trade fit.

## Research-Only Deposit Assumption

For future diagnostics only, a `100000` or `150000` research deposit assumption may be tested if the goal is to evaluate GOLD# strategy behavior without violating the minimum-lot risk budget.

This is not a recommendation to deposit or trade with that capital. It is only a modeling assumption for controlled backtests.
