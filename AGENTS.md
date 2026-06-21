# ForexAiTrade Agent Guardrails

These rules are permanent project guardrails for Codex/agents working on ForexAiTrade.

- Never enable live trading by default.
- Never claim profitability from backtest or research artifacts.
- Never optimize parameters unless the checkpoint explicitly allows it.
- Never add martingale, uncontrolled grid recovery, or uncontrolled lot multiplication.
- Never increase lot or risk to make profit look better.
- Never kill unrelated `terminal64.exe` processes.
- MT5 runners must only stop the exact process ID they started.
- Keep Strategy Tester safety gates.
- Keep broker-specific symbol handling.
- Use the actual runtime symbol `_Symbol` for trading and risk.
- Do not hardcode `XAUUSD` when XM symbols may be `GOLD#` or `GOLDm#`.
- Exclude `.ex5`, `.pyc`, `__pycache__`, nested zip files, `.git`, and `.agents` from review/release zips.
- Every checkpoint must create a Thai checkpoint document under `docs/`.
- Every research run must separate execution status from strategy performance.
- Losing valid reports are still `execution_status=PASS`.
- No demo/live forward test until explicitly approved.
