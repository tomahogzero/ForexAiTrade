# Execution Safety Checks

ForexAiTrade performs execution safety checks before any order send.

## Trade Permission Checks

Before opening a trade, the EA checks:

- `TERMINAL_TRADE_ALLOWED`
- `MQL_TRADE_ALLOWED`
- `ACCOUNT_TRADE_ALLOWED`
- `SYMBOL_TRADE_MODE`

If demo-safe mode is enabled on a real account, the EA blocks both order opening and position modification.

## SL/TP And Broker Limits

The EA validates:

- `SYMBOL_TRADE_STOPS_LEVEL`
- `SYMBOL_TRADE_FREEZE_LEVEL`
- SL distance
- TP distance
- Broker volume min/max/step
- Tick size and tick value
- Contract size

Gold and index symbols are not assumed to share contract metadata with any other broker.

## Margin Checks

Before sending an order, the EA calls `OrderCalcMargin` and compares required margin to free margin. If margin data is invalid or free margin is insufficient, the trade is rejected.

## Lot Sizing

Lot sizing is based on equity risk and stop-loss distance. If the raw calculated lot is below the broker minimum lot, the trade is rejected with:

`broker minimum lot exceeds configured risk budget`

The EA does not force the lot upward to meet broker minimums. After volume normalization, actual money risk is checked against the configured risk budget and rejected if it exceeds the allowed tolerance.

## Position Management

`ManageOpenPositions()` is gated by:

- `InpDemoSafeMode`
- `InpLiveTradingEnabled`
- `InpManageExistingPositions`

With default settings, the EA does not open or modify positions.
