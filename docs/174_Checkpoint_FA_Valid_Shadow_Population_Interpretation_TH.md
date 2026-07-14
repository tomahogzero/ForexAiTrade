# Checkpoint FA: Valid Shadow Population Interpretation

วันที่: 2026-07-14

FA อ่าน EZ merged review แบบ artifact-only และตรวจ conservation ซ้ำ

- total events/event-key conservation: `1600` / `PASS`
- broker-history completeness: `NOT_PROVEN`
- valid populations H6/H12/H24/H48: `1588/1561/1534/1471`
- exclusion rate: `0.75%/2.44%/4.12%/8.06%`
- exclusion reason: `DATA_INCOMPLETE_GAP` เท่านั้น

## Interpretation Boundary

1. valid population ของแต่ละ horizon ไม่เท่ากัน จึงห้ามเทียบ outcome ข้าม horizon แบบ like-for-like
2. exclusion เพิ่มตาม lookahead เพราะมีโอกาสพบ unverified gap มากขึ้น
3. `TP_FIRST`, `SL_FIRST`, `AMBIGUOUS_SAME_BAR` และ `NO_RESOLUTION` เป็น diagnostic labels เท่านั้น ไม่ใช่ strategy performance, win rate, expectancy หรือ profitability

- execution: `PASS`
- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`; PAF: `NOT_READY_FOR_ORDER_LOGIC`

ไม่มี MT5/Strategy Tester, validator bypass, EA/preset, optimization, parameter search, order/risk หรือ demo/live work

Decision: `FA_VALID_SHADOW_POPULATION_INTERPRETED_WITHOUT_PERFORMANCE_CLAIM`.
