# Risk Management

ForexAiTrade is built around survival. Profitability is evaluated only after risk limits are satisfied.

## Core Controls

- Risk per trade is calculated as a percent of equity.
- Daily loss limit blocks new entries after the configured threshold.
- Weekly loss limit blocks new entries after the configured threshold.
- Total drawdown limit blocks new entries after the configured threshold.
- Equity kill switch blocks new entries after severe account deterioration.
- Maximum open orders limits exposure.
- Maximum spread blocks low-quality execution.
- Losing streak limit pauses trading after repeated losses.

## Defaults

The default risk per trade is 0.50% of equity. Live trading is disabled by default. These values are deliberately conservative and should be treated as research defaults, not production recommendations.

## Prohibited Behavior

The system does not use uncontrolled martingale or grid recovery. Position size is based on stop distance and account risk, not on recovering previous losses.
