# Phase 2 Implementation Notes

## Files Created

- `mt5/Experts/ForexAiTrade.mq5`
- `mt5/Include/RiskManager.mqh`
- `mt5/Include/SymbolHelper.mqh`
- `mt5/Include/RegimeDetector.mqh`
- `mt5/Include/TradeLogger.mqh`
- `mt5/Include/Strategies/IStrategy.mqh`
- `mt5/Include/Strategies/TrendStrategy.mqh`
- `mt5/Include/Strategies/BreakoutStrategy.mqh`
- `mt5/Include/Strategies/MeanReversionStrategy.mqh`
- `mt5/Presets/EURUSD_H1_safe.set`
- `mt5/Presets/GBPUSD_H1_safe.set`
- `mt5/Presets/USDJPY#_H1_safe.set`
- `mt5/Presets/GOLDm#_H1_safe.set`
- `mt5/Presets/GOLDm#_H4_safe.set`
- `mt5/Presets/GOLD#_H1_safe.set`
- `tools/README.md`

## Inputs Added

- `InpLiveTradingEnabled=false`
- `InpDemoSafeMode=true`
- `InpMagicNumber`
- `InpRiskPerTradePercent=0.50`
- `InpMaxSpreadPoints`
- `InpMaxOpenPositionsPerSymbol=1`
- `InpMaxDailyLossPercent`
- `InpMaxWeeklyLossPercent`
- `InpMaxTotalDrawdownPercent`
- `InpMaxConsecutiveLosses`
- `InpTradeOnlyOnNewBar=true`
- `InpSignalTimeframe=PERIOD_H1`
- `InpAllowedSymbolsCsv`
- `InpCanonicalSymbolName`
- `InpBrokerSymbolSuffix`
- `InpBrokerGoldSymbolName=GOLDm#`
- `InpSanityStopLossPoints`

## Safety Checks

The EA blocks trading when:

- Live trading is not explicitly enabled.
- Demo-safe mode is enabled on a real account.
- Spread is above the configured limit.
- The EA already has the maximum allowed open positions on the symbol.
- Daily loss limit is reached.
- Weekly loss limit is reached.
- Total drawdown limit is reached.
- Consecutive loss limit is reached.
- Current `_Symbol` is not listed in `InpAllowedSymbolsCsv`.
- Broker symbol metadata is invalid or missing.
- Regime detector returns `REGIME_UNSAFE`.
- Strategy placeholder returns no signal.

No martingale, grid recovery, or uncontrolled lot multiplication exists in Phase 2.

## Risk Manager

`RiskManager.mqh` calculates lot size from equity risk percent and stop-loss distance in points. It validates:

- Equity
- Risk percent
- Stop-loss distance
- Symbol point
- Tick size
- Tick value
- Contract size
- Minimum lot
- Maximum lot
- Lot step

It returns clear rejection reasons instead of silently failing.

## Broker Symbol Handling

The EA uses `_Symbol` as the actual runtime trading symbol. This supports XM names such as `GOLDm#`, `GOLD#`, `USDJPY#`, and `US100Cash` without hardcoding trade symbols in strategy or risk logic.

`SymbolHelper.mqh` records both:

- Actual broker symbol, for example `GOLDm#`
- Canonical reporting symbol, for example `XAUUSD`

On `OnInit`, the EA prints symbol diagnostics:

- Actual symbol
- Canonical symbol
- Digits
- Point
- Tick size
- Tick value
- Contract size
- Minimum lot
- Maximum lot
- Lot step
- Stops level
- Freeze level
- Spread

Risk calculations always query contract metadata from the actual runtime symbol.

## Compile In MT5

1. Copy the `mt5/Experts/ForexAiTrade.mq5` file into the MT5 `MQL5/Experts/` folder, or keep the same relative folder structure under your terminal data folder.
2. Copy `mt5/Include/*` into the matching `MQL5/Include/` location if you do not keep the repo layout intact.
3. Open `ForexAiTrade.mq5` in MetaEditor.
4. Press `F7` or click Compile.
5. Resolve broker-specific warnings if any appear, but Phase 2 should not require external libraries.

## No-Trade Sanity Test

1. Attach the EA to a demo chart such as EURUSD H1.
2. Keep `InpLiveTradingEnabled=false`.
3. Keep `InpDemoSafeMode=true`.
4. Confirm the Journal prints account state and a blocked reason.
5. Confirm no orders are opened.
6. Optional: set `InpLiveTradingEnabled=true` on demo only. The EA should still refuse to trade because the regime detector returns `REGIME_UNSAFE` by design.

Real account trading remains impossible unless `InpLiveTradingEnabled=true` and `InpDemoSafeMode=false` are both intentionally set. Even then, Phase 2 still does not execute orders.
