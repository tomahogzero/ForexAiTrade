# Checkpoint EB: Diagnostic Rule-Candidate Specification

วันที่: 2026-07-11

## ขอบเขต

Checkpoint EB เป็นเอกสาร specification-only ต่อจากคำตัดสิน EA `READY_TO_DEFINE_DIAGNOSTIC_RULE_CANDIDATE` โดยใช้ field และหลักฐานที่ commit แล้วเท่านั้น

ไม่มีการรัน MT5 หรือ Strategy Tester ไม่มีการ optimize ไม่มีการแก้ EA/MQL5 หรือ preset ไม่มีการเพิ่ม order logic ไม่มีการเพิ่ม lot/risk ไม่มี demo/live forward test และไม่มีการอ้าง profitability

## Candidate ที่ตรึง

- ชื่อ: `PAF_FIBO_USABLE_DIRECTION_V1`
- ประเภท: diagnostic row-eligibility candidate
- สถานะ: specification defined, not implemented, not validated
- ค่าเริ่มต้นในอนาคต: disabled
- ขอบเขต symbol/runtime: ใช้ symbol ที่ artifact ระบุและต้องรักษา broker-specific symbol; ห้าม hardcode `XAUUSD`

Candidate นี้ตอบเพียงว่าแถว `POSSIBLE_FIBO_PULLBACK` มี direction context ครบพอสำหรับการวิเคราะห์ diagnostic ภายหลังหรือไม่ Candidate นี้ไม่ใช่ entry signal, trade direction, setup-quality score หรือ order permission

## Input Contract

Field บังคับ:

| Field | Allowed value |
|---|---|
| `classification` | `POSSIBLE_FIBO_PULLBACK` หรือ classification อื่นที่ parser รู้จัก |
| `paf_candidate_direction` | `BUY`, `SELL`, `DIRECTION_UNKNOWN` |
| `paf_direction_is_usable_for_first_touch` | `true`, `false` |
| `paf_direction_source` | non-empty diagnostic source |
| `paf_direction_reason` | non-empty reason code |
| `paf_fibo_direction_gap_reason` | `NONE`, `PRICE_BETWEEN_EMAS`, `TREND_ALIGNMENT_CONFLICT`, `EMA_SLOPE_FLAT` หรือ reason ที่ประกาศใน schema |

Metadata บังคับสำหรับ audit/validation: runtime symbol, timeframe, event time, run/case identity และ authoritative source path หรือ identifier

Field เสริมเพื่อ explainability แต่ห้ามใช้ปรับผลแบบ post hoc: `paf_fibo_ema_slope_state`, `paf_fibo_price_vs_ema_state`, `paf_fibo_trend_alignment_state`, `paf_fibo_pullback_side`, EMA values และ EMA gap points

ห้าม infer direction จาก `classification` เพียงอย่างเดียว และห้ามเติม missing direction แบบ silent fallback

## Frozen Output Contract

Candidate ส่งออกได้เพียงหนึ่งค่า:

- `ELIGIBLE_DIAGNOSTIC_ROW`
- `REJECTED_DIRECTION_GAP`
- `NOT_APPLICABLE`
- `INVALID_DATA`

ทุก output ต้องมี reason code และ input provenance ไม่มี output ใด map เป็น `SIGNAL_BUY`, `SIGNAL_SELL`, market order, pending order หรือ position modification

## Frozen Precedence

ประเมินตามลำดับและหยุดที่ผลแรก:

1. ถ้า field/metadata บังคับหาย, parse ไม่ได้ หรือค่าขัดแย้งกัน ให้ `INVALID_DATA`
2. ถ้า `classification != POSSIBLE_FIBO_PULLBACK` ให้ `NOT_APPLICABLE`
3. ถ้า usable ไม่ใช่ `true`, direction ไม่ใช่ `BUY/SELL` หรือ gap reason ไม่ใช่ `NONE` ให้ `REJECTED_DIRECTION_GAP`
4. เมื่อ classification ถูกต้อง, usable=`true`, direction เป็น `BUY/SELL`, source/reason ครบ และ gap reason=`NONE` เท่านั้น ให้ `ELIGIBLE_DIAGNOSTIC_ROW`

Fail-closed invariants:

- `DIRECTION_UNKNOWN` ห้ามเป็น eligible
- usable=`false` ห้ามเป็น eligible
- gap reason ใด ๆ ที่ไม่ใช่ `NONE` ห้ามเป็น eligible
- unknown enum หรือ field conflict ต้องเป็น `INVALID_DATA` ไม่ใช่ eligible
- legacy normalization ต้องถูกนับและรายงานแยก ห้ามซ่อนว่าเป็น native schema

## Validation Plan ที่ตรึง

Checkpoint validation ภายหลังต้องทำ offline/artifact-only และรายงานอย่างน้อย:

- จำนวน input rows และ output ทั้งสี่ประเภท
- conservation: output รวมต้องเท่ากับ input rows
- eligible rows ทุกแถวต้องผ่าน invariant ครบ
- gap rows ทุกแถวต้องไม่เป็น eligible และต้องมี reason
- missing/conflicting/unknown-enum fixtures ต้องได้ `INVALID_DATA`
- non-Fibo fixtures ต้องได้ `NOT_APPLICABLE`
- deterministic replay บน input เดิมต้องได้ output เหมือนเดิม
- native-schema และ legacy-normalized counts ต้องแยกกัน
- three-year PASS และ existing 20-window FAIL ต้องรายงานแยกเหมือนเดิม
- trades, forbidden markers และ baseline fallback markers ต้องคง `0` หาก artifact มี field เหล่านี้

ห้ามใช้ TP/SL, return, profit factor, drawdown, lot หรือ risk เป็น validation criterion ของ candidate นี้ และห้ามปรับ rule หลังเห็นผลเพื่อเพิ่ม eligible share

## Gates

- candidate specification: `DEFINED`
- candidate implementation: `NOT_IMPLEMENTED`
- candidate artifact validation: `NOT_RUN`
- candidate approval for research use: `NOT_APPROVED`
- order-logic gate: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- demo/live: `NOT_APPROVED`
- profitability claim: `NOT_ALLOWED`

three-year long-horizon gate ยังคง `PASS` และ existing 20-window historical gate ยังคง `FAIL_REPORTED_SEPARATELY`; EB ไม่แก้หรือรวมสอง gate นี้

## ขั้นถัดไปที่ปลอดภัย

Checkpoint EC ควรเป็น docs-only approval/readiness package สำหรับ offline candidate verifier โดยตรึง exact artifact inputs, fixture cases, output paths และคำอนุมัติแยกก่อนเพิ่มหรือรัน tool ใด ๆ

## Progress Estimate

- Research infrastructure readiness: `97%`
- PAF diagnostic pipeline readiness: `96%`
- PAF diagnostic interpretation readiness: `97%`
- Fibo Pullback interpretation readiness: `97%`
- PAF rule-candidate readiness: `92%`
- PAF order-logic readiness: `0%`
- Demo/live readiness: `0%`
