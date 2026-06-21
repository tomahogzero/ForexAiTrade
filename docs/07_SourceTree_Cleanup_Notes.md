# Source Tree Cleanup Notes

## Active Source Tree

The only active EA source tree is:

- `MQL5/Experts/ForexAiTrade/ForexAiTrade.mq5`
- `MQL5/Include/ForexAiTrade/*.mqh`
- `MQL5/Include/ForexAiTrade/Strategies/*.mqh`

The old `mt5/` Phase 2 no-trade implementation has been moved to:

- `archive/phase2_no_trade/`

Archived code is retained for reference only and is not part of the release source.

## Release Cleanup

Build and cache artifacts are excluded from the release package:

- `*.ex5`
- `__pycache__/`
- `*.pyc`
- old compile logs outside `docs/verification/`

The active compile verification log is:

- `docs/verification/compile_mql5_main.log`

## Why This Matters

Keeping one active EA tree prevents accidental deployment of stale inputs, old no-trade placeholders, or mismatched preset files. Release builds should be made only from the active `MQL5/` tree.
