# Price Action/Fibo Diagnostic Summary

Main totals use `ea_mirror.log` when available. Tester excerpts are counted separately to avoid duplicate diagnostics.

| Case | Source | Diagnostics | No-trade | Trades | Forbidden markers | Baseline fallback |
|---|---|---:|---:|---:|---:|---:|
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w1_20260329_20260405` | `ea_mirror.log` | 58 | 92 | 0 | 0 | 0 |
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w2_20260405_20260412` | `ea_mirror.log` | 94 | 115 | 0 | 0 | 0 |
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w3_20260412_20260419` | `ea_mirror.log` | 82 | 115 | 0 | 0 | 0 |
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w4_20260419_20260426` | `ea_mirror.log` | 113 | 115 | 0 | 0 | 0 |

## Direction Gap Explainability

| Case | Gap buckets | Fibo gap reasons | Zone gap reasons |
|---|---|---|---|
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w1_20260329_20260405` | `{"NO_SETUP_DIRECTION_NOT_REQUIRED": 47, "USABLE_DIRECTION": 5, "PRICE_BETWEEN_EMAS": 4, "WICK_TOO_SMALL": 2}` | `{"NONE": 54, "PRICE_BETWEEN_EMAS": 4}` | `{"NONE": 56, "WICK_TOO_SMALL": 2}` |
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w2_20260405_20260412` | `{"NO_SETUP_DIRECTION_NOT_REQUIRED": 70, "USABLE_DIRECTION": 12, "PRICE_BETWEEN_EMAS": 9, "WICK_TOO_SMALL": 3}` | `{"NONE": 85, "PRICE_BETWEEN_EMAS": 9}` | `{"NONE": 91, "WICK_TOO_SMALL": 3}` |
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w3_20260412_20260419` | `{"NO_SETUP_DIRECTION_NOT_REQUIRED": 60, "USABLE_DIRECTION": 13, "WICK_TOO_SMALL": 5, "PRICE_BETWEEN_EMAS": 4}` | `{"NONE": 78, "PRICE_BETWEEN_EMAS": 4}` | `{"NONE": 77, "WICK_TOO_SMALL": 5}` |
| `GOLD_HASH_H1_PAF_DATA_EXPANSION_DB_db_w4_20260419_20260426` | `{"NO_SETUP_DIRECTION_NOT_REQUIRED": 87, "USABLE_DIRECTION": 13, "PRICE_BETWEEN_EMAS": 6, "WICK_TOO_SMALL": 4, "TREND_ALIGNMENT_CONFLICT": 3}` | `{"NONE": 104, "PRICE_BETWEEN_EMAS": 6, "TREND_ALIGNMENT_CONFLICT": 3}` | `{"NONE": 109, "WICK_TOO_SMALL": 4}` |

Diagnostic classifications are observation labels only. They are not entry signals and do not approve trading.
