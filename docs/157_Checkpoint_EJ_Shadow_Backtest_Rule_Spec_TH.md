# Checkpoint EJ: Shadow Backtest Rule Specification

วันที่: 2026-07-11

## ขอบเขต

EJ เป็น docs-only specification สำหรับ offline shadow backtest ของ `PAF_FIBO_USABLE_DIRECTION_V1` ไม่มีการรัน MT5/Strategy Tester ไม่มีการแก้ EA/MQL5 หรือ preset ไม่มี order logic และไม่อ้าง profitability

## Frozen Population

- ใช้เฉพาะ EH rows ที่เป็น `ELIGIBLE_DIAGNOSTIC_ROW`
- direction ใช้ `paf_candidate_direction` เดิม (`BUY`/`SELL`) ห้าม infer ใหม่
- rejected/invalid/not-applicable rows ห้ามนำมาเป็น shadow entry
- runtime symbol ต้องรักษา broker-specific symbol เช่น `GOLD#`

## Frozen Shadow Rules

- entry reference: close ของ diagnostic/event bar (`entry_reference_price`)
- ATR: ค่า ATR ที่ event time เท่านั้น ห้ามใช้ future ATR
- hypothetical TP: `1.5 ATR`
- hypothetical SL: `1.0 ATR`
- horizons: `6`, `12`, `24`, `48` H1 bars
- BUY: TP เหนือ entry, SL ใต้ entry
- SELL: TP ใต้ entry, SL เหนือ entry
- ตรวจ future bars เริ่มจากแท่งถัดจาก event barเพื่อป้องกัน lookahead

Outcome:

- `TP_FIRST`
- `SL_FIRST`
- `NO_RESOLUTION`
- `AMBIGUOUS_SAME_BAR`
- `DATA_MISSING`

ถ้า TP และ SL ถูกแตะใน OHLC bar เดียวกัน ต้องเป็น `AMBIGUOUS_SAME_BAR` และห้ามนับเป็น win หากข้อมูล bar ขาดช่วงหรือ ATR/entry/direction ไม่ครบให้ `DATA_MISSING`

## Cost and Performance Boundary

รอบ shadow diagnostic แรกยังไม่จำลองเงินจริง, lot sizing หรือ order lifecycle และต้องรายงาน spread/slippage limitation แยก ห้ามแปลง outcome count เป็นกำไรสุทธิหรือ profitability claim

ห้าม optimize TP, SL, horizon, entry timing, session filter หรือ eligible population จากผลชุดเดียวกัน

## Required Inputs Before Execution

- EH eligible rows พร้อม event time, direction, entry price และ ATR
- broker-specific GOLD# H1 future OHLC ครอบคลุม 48 bars หลังแต่ละ event
- provenance, gap validation และ deterministic join

EF/EH artifacts ปัจจุบันยืนยัน eligibility แต่ยังไม่ได้ยืนยันว่า entry price, ATR และ future OHLC ครบสำหรับ 1,600 rows ดังนั้น shadow backtest ยัง `NOT_READY_TO_RUN`

## Gates

- shadow rule specification: `DEFINED`
- input readiness: `NOT_EVALUATED`
- shadow backtest: `NOT_RUN`
- Strategy Tester trade backtest: `NOT_APPROVED`
- EA/order logic: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- profitability claim: `NOT_ALLOWED`

## Next Safe Step

Checkpoint EK artifact-only input-readiness audit ตรวจว่า committed artifacts มี entry, ATR และ future OHLC ครบหรือไม่ หากไม่ครบให้หยุดและจัดทำ data contract/approval แยก

## Progress

- Research infrastructure: `98%`
- PAF diagnostic pipeline: `98%`
- PAF diagnostic interpretation: `98%`
- Fibo Pullback interpretation: `98%`
- PAF diagnostic rule-candidate: `100%`
- Shadow backtest readiness: `20%`
- PAF order-logic: `0%`
- Demo/live: `0%`
