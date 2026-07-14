# Checkpoint FF: New Research Hypothesis Contract

วันที่: 2026-07-15

## Candidate

`MARKET_STRUCTURE_BREAK_RETEST_CONFIRMATION_V1` เป็น candidate ใหม่ แยกจาก PAF/Fibo candidate ที่ FE reject โดยสิ้นเชิง

## Allowed Inputs

ใช้เฉพาะ historical H1 OHLC bars ที่มี timestamp ต่อเนื่องและผ่าน validator เดิม; ห้ามเติม/interpolate/infer bars และห้ามใช้ PAF/Fibo rejected candidate เป็น input rule

## Frozen Definitions

- Swing high: high ของ center bar มากกว่า high ของ 2 bars ก่อนและ 2 bars หลัง
- Swing low: low ของ center bar น้อยกว่า low ของ 2 bars ก่อนและ 2 bars หลัง
- LONG break: close สูงกว่า most recent confirmed swing high; wick-only ไม่รับ
- SHORT break: close ต่ำกว่า most recent confirmed swing low; wick-only ไม่รับ
- Retest: price revisit broken swing price ภายใน fixed `12` H1 trading bars หลัง break; ไม่ทดสอบ window อื่น
- LONG confirmation: bullish candle และ close สูงกว่า previous candle high
- SHORT confirmation: bearish candle และ close ต่ำกว่า previous candle low
- entry reference: close ของ confirmation candle เพื่อ diagnostic only ไม่ใช่ order instruction

## Event and Duplicate Policy

event timestamp คือ close time ของ confirmation candle เมื่อข้อมูลทั้งหมดพร้อมแล้ว หนึ่ง break sequence emit ได้สูงสุดหนึ่ง event ต่อ direction; หลัง emit ต้องมี confirmed break ใหม่ก่อน event ใหม่ ห้าม duplicate จากหลาย retest/confirmation ของ break เดียวกัน

## Data Integrity and Anti-Leakage

- swing ใช้ได้หลัง right-side 2 bars ปิดแล้วเท่านั้น
- ห้าม future bar มีผลต่อ timestamp ก่อนหน้าหรือ hindsight relocation swing
- incomplete/gap window ที่แตะ required swing/break/retest/confirmation bars: exclude as `DATA_INCOMPLETE_GAP`
- no interpolation, inferred bars, post-outcome category creation หรือ outcome-driven filtering

## Prohibited Interpretation and Action

ห้าม generate events/calculations/outcomes ใน FF, profitability/edge claim, optimization/parameter search, TP/SL/entry tuning, EA/MQL5/preset/order logic/risk change, MT5/Strategy Tester, demo/live หรือ orders

## Next Checkpoint

FG (not created by FF) เป็น feature-availability audit: ตรวจว่าข้อมูล/fields ที่ต้องใช้มีอยู่และตรวจ timestamp-safe ได้หรือไม่ โดยไม่ generate events

## Status

- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
- profitability: `NOT_CLAIMED`

Decision: `FF_MARKET_STRUCTURE_HYPOTHESIS_CONTRACT_FROZEN`.
