# Checkpoint DF: รายงาน Row-Level Slice สำหรับ Fibo Pullback

วันที่: 2026-07-09

## สถานะ

Checkpoint DF เป็นการวิเคราะห์ artifact เดิมแบบ offline เท่านั้น

ไม่มีการรัน MT5 ไม่มีการรัน Strategy Tester ไม่มีการแก้ EA/MQL5 ไม่มีการแก้ preset ไม่มีการแก้ trading logic ไม่มีการ optimize ไม่มีการเพิ่ม lot/risk ไม่มีการเพิ่ม order logic และไม่มีการตีความกำไร

สิ่งที่เพิ่มคือ Python research tool สำหรับอ่าน `ea_mirror.log` เดิมและแยกเฉพาะแถว `POSSIBLE_FIBO_PULLBACK`

## แหล่งข้อมูล

อ่าน artifact เดิมจาก:

- `run_20260709_182444`
- `run_20260709_202415`
- `run_20260709_212026`

รวมทั้งหมด 8 case/window จากช่วง:

- 2026-03-01 ถึง 2026-04-26

## ผลรวม Row-Level

| Metric | Value |
|---|---:|
| Diagnostic rows scanned | 621 |
| Fibo Pullback rows | 128 |
| Fibo usable first-touch rows | 85 |
| Fibo direction gap rows | 43 |
| Forbidden action markers | 0 |
| Baseline fallback markers | 0 |

## Direction Distribution

| Direction | Count |
|---|---:|
| SELL | 53 |
| BUY | 32 |
| DIRECTION_UNKNOWN | 43 |

## Direction Source / Confidence

| Field | Value | Count |
|---|---|---:|
| Direction source | FIBO_PULLBACK_EMA | 85 |
| Direction source | NONE | 43 |
| Direction confidence | HIGH | 85 |
| Direction confidence | NONE | 43 |
| First-touch usable | true | 85 |
| First-touch usable | false | 43 |

## Gap Reasons

| Gap reason | Count |
|---|---:|
| NONE | 85 |
| PRICE_BETWEEN_EMAS | 28 |
| TREND_ALIGNMENT_CONFLICT | 15 |

## Context Distribution

| Context | Value | Count |
|---|---|---:|
| EMA slope | DOWN | 68 |
| EMA slope | UP | 32 |
| EMA slope | MIXED | 28 |
| Price vs EMA | BELOW_BOTH | 68 |
| Price vs EMA | ABOVE_BOTH | 32 |
| Price vs EMA | BETWEEN | 28 |
| Trend alignment | BEARISH | 53 |
| Trend alignment | BULLISH | 32 |
| Trend alignment | CONFLICT | 43 |
| Regime | trend | 92 |
| Regime | breakout | 36 |

## Window Distribution

| Window | Fibo rows | Usable rows |
|---|---:|---:|
| cv_field_presence_20260301_20260308 | 25 | 15 |
| cy_w1_20260308_20260315 | 20 | 15 |
| cy_w2_20260315_20260322 | 20 | 20 |
| cy_w3_20260322_20260329 | 4 | 2 |
| db_w1_20260329_20260405 | 6 | 2 |
| db_w2_20260405_20260412 | 19 | 10 |
| db_w3_20260412_20260419 | 13 | 9 |
| db_w4_20260419_20260426 | 21 | 12 |

## การตีความแบบระวัง

Fibo Pullback มีข้อมูล row-level แล้ว แต่ยังไม่พอสำหรับ rule-candidate เพราะ:

- Fibo usable first-touch rows มี 85 rows ยังต่ำกว่า gate 150 สำหรับ Fibo-specific diagnostic confidence
- total usable direction rows ยังต่ำกว่า gate 300 สำหรับ rule-candidate discussion
- จำนวนหน้าต่างข้อมูลยังมี 8 windows ต่ำกว่า gate 12 windows
- มี direction gap 43 rows
- ยังไม่มี shadow outcome หรือผลหลังสัญญาณที่พิสูจน์คุณภาพ entry

## Verdict

- `FIBO_ROW_LEVEL_SLICE_BUILT`
- `FIBO_USABLE_DIRECTION_BELOW_RULE_CANDIDATE_GATE`
- `RULE_CANDIDATE_GATE_FAIL`
- `ORDER_LOGIC_NOT_APPROVED`
- `PAF_NOT_READY_FOR_ORDER_LOGIC`

## ข้อห้าม

ผลนี้ยังห้ามใช้เป็น:

- buy signal
- sell signal
- pending order rule
- market order rule
- proof of edge
- proof of profitability
- เหตุผลเพิ่ม lot/risk
- เหตุผลเริ่ม demo/live

## ขั้นตอนถัดไปที่ปลอดภัย

Checkpoint DG ควรเป็น artifact-only interpretation ของ row-level Fibo slice:

- วิเคราะห์ว่า 85 usable rows กระจายตัวดีหรือไม่
- วิเคราะห์ 43 gap rows ว่าควรเพิ่ม diagnostics อะไรต่อ
- วิเคราะห์ว่า Fibo focus ควรเก็บไว้หรือควรถอย
- ไม่รัน MT5
- ไม่แก้ EA/MQL5
- ไม่แก้ preset
- ไม่เพิ่ม order logic

