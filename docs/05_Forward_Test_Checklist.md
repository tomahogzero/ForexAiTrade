# Forward Test Checklist

Before demo forward testing:

- Confirm `InpLiveTradingEnabled=true` only on a demo account.
- Keep `InpDemoSafeMode=true` unless intentionally preparing for live deployment.
- Verify symbol contract size, tick value, minimum lot, and spread behavior on XM MT5.
- Confirm the EA magic number is unique.
- Confirm VPS time, broker time, and terminal connection stability.
- Run a visual test for several weeks of historical data.
- Review journal logs for rejected trades and risk blocks.

During demo forward testing:

- Monitor spread spikes.
- Monitor slippage.
- Record all parameter changes.
- Compare live demo behavior with recent backtest expectations.
- Do not move to live trading until the EA survives a meaningful forward period.
