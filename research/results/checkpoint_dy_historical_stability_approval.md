# Checkpoint DY Historical Stability Readiness and Approval

Date: 2026-07-11

DY corrects the DX future-date assumption. ForexAiTrade is backtest-only at this stage, so the independent stability block uses completed historical broker data instead of waiting for future dates.

The frozen holdout includes all 156 consecutive weekly GOLD# H1 windows from 2023-01-01 through 2025-12-28. No weekly sampling or post-result window selection is allowed.

Long-horizon criteria are frozen before execution: weak share at most 20%, maximum weak run 2, annual weak share at most 25%, median and average usable rows at least 7, total usable rows at least 1092, complete per-window attribution, and zero trades or forbidden markers.

No MT5 run or matrix is created. Future DZ remains blocked until the exact approval phrase is provided. A holdout pass could only allow a future rule-candidate review and would not approve order logic.

PAF remains `NOT_READY_FOR_ORDER_LOGIC`.
