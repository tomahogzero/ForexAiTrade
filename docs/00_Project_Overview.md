# ForexAiTrade Project Overview

ForexAiTrade is a MetaTrader 5 Expert Advisor and research pipeline for adaptive forex trading. The project is designed for capital preservation first: every trading decision passes through market regime detection and risk controls before an order can be sent.

The EA is modular:

- `ForexAiTrade.mq5` coordinates lifecycle, position management, regime selection, and trade execution.
- `RiskManager.mqh` enforces account-level and trade-level risk limits.
- `RegimeDetector.mqh` classifies market conditions.
- `Strategies/` contains trend following, breakout, and mean reversion logic.
- `tools/` contains Python scripts for parsing MT5 reports, scoring robustness, ranking parameter sets, and generating summaries.

Live trading is disabled by default. `InpLiveTradingEnabled=false` and `InpDemoSafeMode=true` are intentional defaults.
