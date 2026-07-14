# Checkpoint FA Valid Shadow Population Review

Diagnostic interpretation only; no strategy-performance conclusion.

- execution_status: `PASS`
- method: `artifact-only valid-population coverage interpretation`
- total_events: `1600`
- event_key_conservation: `PASS`
- broker_history_completeness: `NOT_PROVEN`
- strategy_performance_status: `NOT_EVALUATED`
- order_logic_status: `NOT_APPROVED`
- paf_status: `NOT_READY_FOR_ORDER_LOGIC`
- profitability_claim: `False`
- Each horizon retains a large but non-identical valid population; comparisons across horizons are not like-for-like.
- Exclusion increases with lookahead because more windows intersect unverified gaps.
- TP_FIRST/SL_FIRST/AMBIGUOUS_SAME_BAR/NO_RESOLUTION are diagnostic labels only, not trading performance or profitability evidence.
- H6: `{'horizon': 'H6', 'total_events': 1600, 'included_events': 1588, 'excluded_events': 12, 'exclusion_rate_pct': 0.75, 'exclusion_reasons': {'DATA_INCOMPLETE_GAP': 12}, 'source_exclusion_reasons': {'BLOCKED_GAP_INSIDE_LOOKAHEAD': 12}, 'outcomes': {'TP_FIRST': 460, 'SL_FIRST': 750, 'AMBIGUOUS_SAME_BAR': 22, 'NO_RESOLUTION': 356}}`
- H12: `{'horizon': 'H12', 'total_events': 1600, 'included_events': 1561, 'excluded_events': 39, 'exclusion_rate_pct': 2.44, 'exclusion_reasons': {'DATA_INCOMPLETE_GAP': 39}, 'source_exclusion_reasons': {'BLOCKED_GAP_INSIDE_LOOKAHEAD': 39}, 'outcomes': {'TP_FIRST': 567, 'SL_FIRST': 854, 'AMBIGUOUS_SAME_BAR': 24, 'NO_RESOLUTION': 116}}`
- H24: `{'horizon': 'H24', 'total_events': 1600, 'included_events': 1534, 'excluded_events': 66, 'exclusion_rate_pct': 4.12, 'exclusion_reasons': {'DATA_INCOMPLETE_GAP': 66}, 'source_exclusion_reasons': {'BLOCKED_GAP_INSIDE_LOOKAHEAD': 66}, 'outcomes': {'TP_FIRST': 622, 'SL_FIRST': 878, 'AMBIGUOUS_SAME_BAR': 26, 'NO_RESOLUTION': 8}}`
- H48: `{'horizon': 'H48', 'total_events': 1600, 'included_events': 1471, 'excluded_events': 129, 'exclusion_rate_pct': 8.06, 'exclusion_reasons': {'DATA_INCOMPLETE_GAP': 129}, 'source_exclusion_reasons': {'BLOCKED_GAP_INSIDE_LOOKAHEAD': 129}, 'outcomes': {'TP_FIRST': 604, 'SL_FIRST': 843, 'AMBIGUOUS_SAME_BAR': 24, 'NO_RESOLUTION': 0}}`
