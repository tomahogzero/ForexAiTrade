# Checkpoint FR-Prep-A1b-2 — Remaining Negative Source and Aggregate Validation

วันที่: 2026-07-18

สถานะ: `FR_PREP_A1B2_SOURCE_VALIDATION_COMPLETE`

## ขอบเขต

A1b-2 ทำเฉพาะ negative synthetic validation ที่เหลือของ generic historical source adapter: source first/last timestamp, frozen boundary, duplicate source ID/timestamp, conflicting OHLC และ aggregate count/range/hash รวม 13 กรณี ไม่ได้ implement หรือ execute gap policy, detector/FI, FJ replay, historical population, holdout preflight, event/ATR-event, TP/SL หรือ outcome

## Frozen validation precedence

1. ตรวจ manifest shape และ safety invariants ก่อน
2. `DUPLICATE_SOURCE_ID` ต้อง fail ก่อนเปิด source file ใด ๆ ของรายการซ้ำ
3. source แต่ละไฟล์ตรวจ path → SHA-256 → optional size → TSV schema → timestamp → OHLC → boundary → chronology → row count → declared first/last timestamp
4. source-level validation ทุกไฟล์ต้องเสร็จก่อน aggregate-level validation; boundary failure จึงเกิดก่อน aggregate metadata
5. เมื่อ timestamp ซ้ำ `AGGREGATE_TIMESTAMP_OHLC_CONFLICT` มี precedence เหนือ `AGGREGATE_DUPLICATE_TIMESTAMP`
6. aggregate duplicate/conflict ต้อง fail ก่อน source-count, total-row, first/last, exact boundary-range และ canonical hash
7. aggregate metadata ตรวจ source count → total rows → first timestamp → last timestamp → exact frozen-boundary range
8. `CANONICAL_TIMELINE_SHA256_MISMATCH` ตรวจเป็นลำดับสุดท้าย

`AGGREGATE_TIMELINE_RANGE_MISMATCH` หมายถึง observed aggregate first/last ไม่ครอบคลุม frozen manifest start/end แบบ exact หลังจาก declared aggregate first/last ตรงกับ observed แล้ว

## Validation-code registry

Machine-readable registry ที่ `research/schemas/historical_source_validation_codes.v1.json` บันทึก code, validation layer, meaning, precedence และ fixture proving the code ครบทั้ง A1b-1 และ A1b-2 โดย code A1b-1 ทั้ง 9 ค่าไม่ถูก rename หรือเปลี่ยนแปลง

## Fixture and regression contract

- A1a positive: `4/4 PASS`; golden SHA-256 ต้องคงเป็น `717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b`
- A1b-1 negative: `9/9 PASS`; golden SHA-256 ต้องคงเป็น `97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8`
- A1b-2 negative: `13/13 PASS`; unexpected pass, wrong code, unknown code และ mismatch ต้องเป็น `0`
- canonical failures มีเฉพาะ status/code/expected/completeness ไม่มี traceback, absolute path, runtime timestamp, random value หรือ platform exception text
- complete A1 suite และ A1b-2 replay ต้อง byte-identical อย่างน้อยสองรอบ

ผลการ replay: A1b-2 run 1/run 2/golden SHA-256 เท่ากันที่ `5bde1d04d27c67a089103c344ff17918a795d9dc14176fae6dffc58782b242a4`; complete A1 run 1/run 2 เท่ากันที่ `35acb26124507e5383030202ec2035dc835f391cb4fafa43a67651a25eae43f4`.

## Frozen files

- `tools/market_structure_break_retest_detector.py`
- `tools/run_checkpoint_fi_detector_fixtures.py`
- `tests/fixtures/checkpoint_fi_detector_cases.json`
- `tests/fixtures/checkpoint_fi_detector_inputs.json`
- `tests/fixtures/checkpoint_fi_detector_expected.json`

## Safety status

`broker_history_completeness=NOT_PROVEN`; detector, population, holdout preflight, events, ATR-events, TP/SL และ outcomes เป็น `NOT_RUN`; strategy performance `NOT_EVALUATED`; profitability `NOT_CLAIMED`; order logic `NOT_APPROVED`.

## Exact next step

FR-Prep-A2 — Generic Gap-Policy Adapter Design and Positive Fixtures ภายใต้ approval แยกต่างหาก
