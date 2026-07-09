# Checkpoint CR: PAF Direction Gap Explainability Design

วันที่จัดทำ: 2026-07-09

## สถานะ

Checkpoint CR เป็นเอกสารออกแบบและ approval package เท่านั้น

ไม่ได้รัน MT5 ไม่ได้รัน Strategy Tester ไม่ได้แก้ EA/source code ไม่ได้แก้ preset ไม่ได้ optimize ไม่ได้เพิ่ม lot/risk และไม่ได้ตีความว่า strategy ทำกำไร

## ที่มาของงาน

Checkpoint CP ยืนยันว่า diagnostics-only `paf_*` direction context fields ถูกเขียนลง EA mirror log ได้จริง และไม่มีการเปิด trade:

- RunId: `run_20260709_155948`
- Symbol/timeframe: `GOLD#` H1
- Date range: `2026-03-01` ถึง `2026-03-08`
- PAF diagnostic rows: `97`
- Total trades: `0`
- Forbidden action marker count: `0`
- Baseline fallback marker count: `0`

Checkpoint CQ วิเคราะห์ artifact ต่อและพบว่า `DIRECTION_UNKNOWN=78` ไม่ใช่ปัญหาทั้งหมด:

| Bucket | Count |
|---|---:|
| `NO_SETUP_DIRECTION_NOT_REQUIRED` | 64 |
| `USABLE_DIRECTION` | 19 |
| `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING` | 10 |
| `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING` | 4 |

ดังนั้นช่องว่างจริงที่ต้องอธิบายเพิ่มคือ possible-setup rows จำนวน `14` แถวเท่านั้น

## เป้าหมาย CR

CR ไม่ได้ implement logic ใดๆ เป้าหมายคือกำหนดแบบแปลน diagnostics-only สำหรับ checkpoint ถัดไป เพื่ออธิบายว่าเหตุใด possible setup บางแถวจึงยังไม่มี usable direction

คำถามที่ต้องตอบในอนาคต:

- Fibo Pullback 10 แถว ขาด direction เพราะ EMA context ไม่ชัดเจนแบบใด
- Zone Rejection 4 แถว ขาด direction เพราะ candle/zone side ไม่ชัดเจนแบบใด
- ข้อมูลที่ขาดเป็น data issue, rule ambiguity, หรือ setup ที่ควรเป็น no-setup

## ขอบเขตที่อนุญาตสำหรับ checkpoint ถัดไป

อนุญาตเฉพาะ diagnostics-only fields หรือ parser/report fields ที่ช่วยอธิบาย root cause เท่านั้น

ห้าม:

- ส่ง `SIGNAL_BUY`
- ส่ง `SIGNAL_SELL`
- เปิด market order
- เปิด pending order
- แก้ไข position
- fallback ไป baseline strategy
- optimize parameter
- เพิ่ม lot/risk
- force broker minimum lot
- ใช้ข้อมูลอนาคตหรือ lookahead
- สรุปว่า strategy พร้อมเทรด

## Fibo Pullback Explainability Fields

สำหรับ `FIBO_PULLBACK_EMA_DIRECTION_CONTEXT_MISSING` ควรออกแบบ field เชิงวินิจฉัยเพื่อแยกสาเหตุ เช่น:

| Field | ความหมาย |
|---|---|
| `paf_fibo_ema_fast_value` | ค่า EMA fast ณ bar ที่วิเคราะห์ |
| `paf_fibo_ema_slow_value` | ค่า EMA slow ณ bar ที่วิเคราะห์ |
| `paf_fibo_ema_gap_points` | ระยะห่าง EMA fast/slow เป็น points |
| `paf_fibo_ema_slope_state` | `UP`, `DOWN`, `FLAT`, `UNKNOWN` |
| `paf_fibo_price_vs_ema_state` | `ABOVE_BOTH`, `BELOW_BOTH`, `BETWEEN`, `UNKNOWN` |
| `paf_fibo_trend_alignment_state` | `BULLISH`, `BEARISH`, `CONFLICT`, `UNKNOWN` |
| `paf_fibo_pullback_side` | `BUY_SIDE`, `SELL_SIDE`, `BOTH`, `NONE`, `UNKNOWN` |
| `paf_fibo_direction_gap_reason` | เหตุผลหลักที่ยังให้ direction ไม่ได้ |

ค่าที่ควรใช้ใน `paf_fibo_direction_gap_reason`:

- `EMA_VALUES_MISSING`
- `EMA_GAP_TOO_SMALL`
- `EMA_SLOPE_FLAT`
- `PRICE_BETWEEN_EMAS`
- `TREND_ALIGNMENT_CONFLICT`
- `PULLBACK_SIDE_UNKNOWN`
- `FIBO_ZONE_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`

## Zone Rejection Explainability Fields

สำหรับ `ZONE_REJECTION_CANDLE_DIRECTION_CONTEXT_MISSING` ควรออกแบบ field เชิงวินิจฉัยเพื่อแยกสาเหตุ เช่น:

| Field | ความหมาย |
|---|---|
| `paf_zone_side` | `SUPPORT`, `RESISTANCE`, `BOTH`, `UNKNOWN` |
| `paf_zone_touch_state` | `TOUCHED_SUPPORT`, `TOUCHED_RESISTANCE`, `TOUCHED_BOTH`, `NO_TOUCH`, `UNKNOWN` |
| `paf_rejection_candle_direction` | `BULLISH`, `BEARISH`, `DOJI`, `UNKNOWN` |
| `paf_rejection_wick_side` | `LOWER`, `UPPER`, `BOTH`, `NONE`, `UNKNOWN` |
| `paf_rejection_body_ratio` | body/range ratio ถ้าคำนวณได้ |
| `paf_rejection_wick_ratio` | wick/range ratio ถ้าคำนวณได้ |
| `paf_zone_direction_gap_reason` | เหตุผลหลักที่ยังให้ direction ไม่ได้ |

ค่าที่ควรใช้ใน `paf_zone_direction_gap_reason`:

- `ZONE_SIDE_UNKNOWN`
- `ZONE_TOUCH_MISSING`
- `TOUCHED_BOTH_SIDES`
- `REJECTION_CANDLE_DOJI`
- `WICK_TOO_SMALL`
- `BODY_DIRECTION_CONFLICT`
- `WICK_SIDE_CONFLICT`
- `INSUFFICIENT_BAR_CONTEXT`

## Parser / Report Requirement

checkpoint ถัดไปถ้ามี implementation ต้อง update parser แบบ backward-compatible:

- legacy logs ต้อง parse ได้เหมือนเดิม
- missing field ต้องเป็น `null` หรือ `UNKNOWN` ไม่ทำให้ parser crash
- output ต้องแยก `NO_SETUP_DIRECTION_NOT_REQUIRED` ออกจาก possible-setup gap
- summary ต้องนับ gap เฉพาะ possible setup เท่านั้น
- losing/invalid performance ต้องไม่ปะปนกับ execution status

## Future Validation Plan

หาก checkpoint ถัดไปเป็น implementation จริง ต้องมี guardrails:

1. แก้เฉพาะ diagnostics-only logging/parser
2. Compile EA และต้องได้ `0 errors, 0 warnings`
3. ห้ามรัน MT5 จนกว่าจะมี approval แยก
4. ถ้ามี run ภายหลัง ต้องเป็น Strategy Tester เท่านั้น
5. ต้องยืนยัน:
   - total trades = `0`
   - forbidden action markers = `0`
   - baseline fallback markers = `0`
   - diagnostic fields ใหม่ปรากฏใน log/parser

## Stop Conditions

หยุดทันทีถ้า checkpoint ถัดไปมีสิ่งต่อไปนี้:

- มี trade signal จาก PAF path
- มี order path เปิดใช้งาน
- มี pending order path เปิดใช้งาน
- มี position modification
- มี preset ที่ทำให้ PAF ส่ง order
- มี optimization
- มีการเพิ่ม risk/lot
- มีการตีความเป็นกำไรหรือพร้อม live

## Decision

Checkpoint CR สรุปว่า:

- `NO_SETUP` rows ไม่ควรถูกนับเป็น direction completeness failure
- true possible-setup gap = `14` rows
- งานถัดไปควรเป็น diagnostics-only explainability implementation หรือ approval package เท่านั้น
- order logic ยังถูก block
- PAF ยังไม่พร้อมสำหรับ demo/live หรือ forward test

## Next Safe Step

Checkpoint CS ควรเป็นหนึ่งในสองทางเลือก:

1. diagnostics-only implementation approval package สำหรับ fields ในเอกสารนี้
2. implementation จริงของ diagnostics-only fields พร้อม compile verification แต่ยังไม่รัน MT5

ทั้งสองทางเลือกยังต้องห้าม order logic, pending orders, optimization และ profitability claim
