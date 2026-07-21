# Checkpoint FR-Prep-A1b-1 — Negative Source Validation, Part 1

วันที่: 2026-07-18

สถานะ: `FR_PREP_A1B1_NEGATIVE_SOURCE_VALIDATION`

## ขอบเขต

A1b-1 เพิ่มเฉพาะ stable validation codes และ negative synthetic source fixtures 9 ประเภทให้ A1a adapter พร้อม rerun positive regression. ไม่มี gap-policy behavior/fixture, detector/FI execution, FJ replay, holdout preflight, historical population, event/ATR-event, TP/SL, outcome, candidate/parameter change, optimization, MT5/Strategy Tester, EA/order logic หรือ demo/live.

## Stable validation codes

| Case | Stable code | Result |
|---|---|---|
| missing source path | `SOURCE_PATH_MISSING` | PASS |
| SHA-256 mismatch | `SOURCE_SHA256_MISMATCH` | PASS |
| optional byte-size mismatch | `SOURCE_SIZE_MISMATCH` | PASS |
| invalid MT5 TSV columns | `MT5_TSV_SCHEMA_INVALID` | PASS |
| unparseable source timestamp | `SOURCE_TIMESTAMP_UNPARSEABLE` | PASS |
| non-finite/non-positive OHLC | `OHLC_NON_FINITE_OR_NON_POSITIVE` | PASS |
| inconsistent OHLC | `OHLC_INCONSISTENT` | PASS |
| non-chronological rows | `SOURCE_NOT_CHRONOLOGICAL` | PASS |
| declared row-count mismatch | `SOURCE_ROW_COUNT_MISMATCH` | PASS |

## Fixture and replay results

Negative fixtures `9/9 PASS`; unexpected-pass `0`; wrong-failure `0`; unknown-code `0`; mismatch `0`. Two internal runs and golden output are byte-identical with SHA-256 `97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8`.

## Positive regression

A1a fixtures `4/4 PASS`; golden SHA-256 คงเดิม `717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b`; mismatch `0`; relocated runtime-path output identical.

## Canonical failure contract

แต่ละ output มีเฉพาะ fixture-key กับ `status`, `validation_code`, `expected_code`, `broker_history_completeness=NOT_PROVEN`. ไม่ serialize exception message/traceback/path/runtime timestamp. Failure เกิดใน source adapter ก่อน detector boundary และ runner ไม่ import detector.

## Frozen files

- `tools/market_structure_break_retest_detector.py`
- `tools/run_checkpoint_fi_detector_fixtures.py`
- `tests/fixtures/checkpoint_fi_detector_cases.json`
- `tests/fixtures/checkpoint_fi_detector_inputs.json`
- `tests/fixtures/checkpoint_fi_detector_expected.json`

## Deliverables

- minimal code changes in `tools/historical_source_adapter.py`
- `tools/run_fr_prep_a1b1_negative_source_fixtures.py`
- `tests/fixtures/fr_prep_a1b1/negative_cases.json`, synthetic TSVs, and `expected_failures.json`
- `research/results/checkpoint_fr_prep_a1b1_negative_source_validation/checkpoint_fr_prep_a1b1_test_summary.json`
- เอกสารนี้และ A1b-1 marker ใน `docs/ai/current-status.md`

## Validation

Python/JSON/schema parse, internal/external deterministic replay, A1a regression, documentation references, `git diff --check`, frozen hashes, LF fixture policy, staged paths และ no raw broker/cache/event/outcome artifacts ต้อง PASS.

## Exact next step

FR-Prep-A1b-2 เท่านั้น: negative source validation ส่วนที่เหลือ—first/last timestamp mismatch, row outside boundary, duplicate source ID, duplicate aggregate timestamp, aggregate source count/rows/range/hash mismatch—พร้อม frozen failure codes และ A1a/A1b-1 regression. ยังห้าม gap policy และ detector.

## Status

- execution status: `PASS` สำหรับ A1b-1 source fixtures
- broker-history completeness: `NOT_PROVEN`
- detector/FI/FJ/population/events/outcomes/holdout preflight: `NOT_RUN`
- strategy performance: `NOT_EVALUATED`; profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`; candidate: `NOT_READY_FOR_ORDER_LOGIC`
