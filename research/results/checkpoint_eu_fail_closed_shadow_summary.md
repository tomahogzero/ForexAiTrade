# Checkpoint EU Fail-Closed Shadow Analysis

Offline diagnostic only. Strategy performance is not evaluated.

- execution_status: `PASS`
- method: `offline fail-closed event/horizon exclusion`
- events_total: `1600`
- bars_total: `17716`
- bars_from: `2023-01-03 01:00:00`
- bars_to: `2025-12-31 19:00:00`
- duplicate_bar_timestamps_ignored: `0`
- input_files: `['GOLD#_H1_202301030100_202312292300.csv', 'GOLD#_H1_202401020100_202412312000.csv', 'GOLD#_H1_202501020800_202512311900.csv']`
- gap_policy: `EO accepted daily/weekend gaps allowed; 28 blocked gaps excluded`
- accepted_gap_count: `745`
- blocked_gap_count: `28`
- tp_atr_multiple: `1.5`
- sl_atr_multiple: `1.0`
- strategy_performance_status: `NOT_EVALUATED`
- order_logic_status: `NOT_APPROVED`
- paf_status: `NOT_READY_FOR_ORDER_LOGIC`
- profitability_claim: `False`
- guardrails: `['offline only', 'no MT5 or Strategy Tester', 'no price filling/interpolation', 'no gap bridging', 'no order logic', 'no optimization', 'no profitability claim']`
