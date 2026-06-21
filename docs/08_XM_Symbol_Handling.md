# XM Symbol Handling

XM MT5 may expose symbols with suffixes or broker-specific names, for example:

- `GOLDm#`
- `GOLD#`
- `USDJPY#`
- `USDCHF#`
- `US100Cash`
- `US200Cash`
- `US30Cash`

ForexAiTrade uses `_Symbol` as the actual runtime trading symbol. All `SymbolInfoDouble` and `SymbolInfoInteger` calls use the active chart symbol or the runtime symbol passed into the module.

## Inputs

- `InpAllowedSymbolsCsv`
- `InpCanonicalSymbolName`
- `InpBrokerGoldSymbolName`
- `InpPrintSymbolDiagnostics`

If `InpAllowedSymbolsCsv` is empty, the EA allows the current chart symbol. If it is not empty, `_Symbol` or its canonical reporting name must appear in the CSV list.

## Canonical Reporting

`SymbolHelper.mqh` separates:

- Actual broker symbol: the tradable runtime symbol, such as `GOLDm#`
- Canonical symbol: the reporting symbol, such as `GOLD`, `XAUUSD`, or `USDJPY`

The EA never converts canonical names back into tradable symbols. Trading and risk calculations use only the actual runtime symbol.

## Diagnostics

When `InpPrintSymbolDiagnostics=true`, `OnInit` prints:

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
- Trade mode
- Current spread

If metadata is invalid or missing, trading is blocked with a clear reason.

## XM Presets

XM-safe presets include:

- `presets/GOLDm#_H1_safe.set`
- `presets/GOLDm#_H4_safe.set`
- `presets/EURUSD_H1_safe.set`
- `presets/USDJPY#_H1_safe.set`

No strategy or risk module should hardcode `XAUUSD` as the tradable gold symbol.
