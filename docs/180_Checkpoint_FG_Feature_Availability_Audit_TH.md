# Checkpoint FG: Feature Availability Audit สำหรับ MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1

วันที่: 2026-07-15

## วัตถุประสงค์

FG เป็น offline feature-availability audit ของ hypothesis ที่ FF freeze เท่านั้น ใช้ตรวจว่า GOLD# H1 CSV และ tooling ที่มีอยู่รองรับ feature ทุกตัวอย่าง deterministic ได้หรือไม่ ไม่มีการ generate final event population และไม่มี TP/SL outcome calculation.

## ขอบเขตข้อมูลและผลการตรวจ

ตรวจ schema ของไฟล์ GOLD# H1 ที่ผู้ใช้จัดเตรียมไว้: `5894` rows, fields `<DATE>`, `<TIME>`, `<OPEN>`, `<HIGH>`, `<LOW>`, `<CLOSE>` ครบถ้วน. ตรวจพบ timestamp gap `256` ช่วงในไฟล์ตัวอย่าง การมีอยู่ของ gap ตรวจจับได้แบบ deterministic แต่ broker-history completeness ยัง `NOT_PROVEN` และ sequence ที่แตะ gap หรือข้อมูลไม่ครบต้อง exclude เป็น `DATA_INCOMPLETE_GAP` เสมอ ไม่มีการ fill, interpolate, reconstruct หรือ silent bridge.

## Feature Inventory

| Feature | Source/derivation | Availability | Determinism | Leakage risk | Exclusion rule |
|---|---|---|---|---|---|
| H1 timestamp และ OHLC | CSV DATE/TIME/OHLC | AVAILABLE | DETERMINISTIC | none | invalid/incomplete row หรือ gap exclude |
| Swing high / low | FF 2-left/2-right OHLC | AVAILABLE | DETERMINISTIC | ใช้ right side เร็วเกิน | ใช้ได้หลัง center+2 bars ปิดแล้ว |
| เวลาที่ swing knowable และ most-recent confirmed swing | ordered confirmed-swing state | AVAILABLE | DETERMINISTIC | future swing selection | state รับเฉพาะ confirmed swing |
| LONG/SHORT close break | close เทียบ confirmed swing | AVAILABLE | DETERMINISTIC | wick/future leak | wick-only หรือ unconfirmed level reject |
| 12-bar retest และ exact level | ordered bar index และ stored break level | AVAILABLE | DETERMINISTIC | level substitution | retest เกิน 12 bars reject; รักษาระดับเดิม |
| Bullish/bearish confirmation | OHLC และ previous-bar high/low | AVAILABLE | DETERMINISTIC | prior-bar ordering | condition ไม่ครบ reject |
| diagnostic entry reference | confirmation close | AVAILABLE | DETERMINISTIC | none | diagnostic only, never order instruction |
| ATR | approved `offline_atr_14` จาก completed bars ก่อน event | AVAILABLE | DETERMINISTIC | future ATR leak | ต้องมี prior completed 14 bars |
| year / direction / event-key | timestamp และ frozen state/provenance | AVAILABLE | DETERMINISTIC | provenance loss | exact source, bar time, direction, break id |
| gap / duplicate / sufficiency | timestamp delta, validation, break state, bar counts | AVAILABLE | DETERMINISTIC | silent bridge/duplicate | `DATA_INCOMPLETE_GAP`, one event per break/direction, insufficient history exclude |

รายละเอียด 20 feature ตาม requirement อยู่ใน `research/results/checkpoint_fg_feature_availability_audit/checkpoint_fg_feature_availability.json`.

## Anti-Leakage Controls

- swing ใช้ได้เมื่อ right-side 2 bars ปิดครบเท่านั้น
- break ใช้เฉพาะ swing ที่ confirmed แล้ว ณ break timestamp
- retest และ confirmation ต้องเกิดหลัง break ตามลำดับ
- future bars ไม่มีสิทธิ์แก้ decision ที่เกิดก่อนหน้า และไม่มี hindsight relocation
- ไม่มี interpolation, inferred bars หรือ silent gap bridging

## Deterministic Fixture Tests

ผ่านทั้งหมด `8/8`: valid LONG, valid SHORT, wick-only false break, swing not yet confirmed, retest after 12 bars, confirmation failure, gap inside required sequence, และ duplicate candidate sequence. Fixture เป็น state-machine ขนาดเล็ก ไม่ใช่ historical event run.

## Decision และ Blockers

Decision: `FG_PASS_FEATURES_AVAILABLE`.

ไม่มี blocker เชิง feature. ข้อจำกัดที่คงอยู่คือ broker-history completeness `NOT_PROVEN`; gap ที่ตรวจพบต้อง exclude แบบ fail-closed ไม่ใช่ถูก relabel เป็น market closure.

## Scope ที่อนุญาตสำหรับ FH (ยังไม่สร้าง)

หากมีการอนุมัติแยกต่างหาก FH อาจสร้าง deterministic event-generator prototype ด้วย FF definitions, FG anti-leakage controls, exact event keys, duplicate policy และ `DATA_INCOMPLETE_GAP` exclusions เท่านั้น. ห้ามสร้าง outcome/TP-SL, optimization, parameter search, order logic, EA/MQL5/preset change, MT5/Strategy Tester, demo/live หรือ order ใดๆ.

## Status

- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`

FG ไม่ได้อนุมัติ trading edge, profitability, execution design หรือ implementation.