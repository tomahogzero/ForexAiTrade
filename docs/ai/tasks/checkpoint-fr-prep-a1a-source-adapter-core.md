# Checkpoint FR-Prep-A1a — Generic Source Manifest Schema and Adapter Core

วันที่: 2026-07-18

สถานะ: `FR_PREP_A1A_SOURCE_ADAPTER_CORE`

## ขอบเขต

A1a implement เฉพาะ generic source manifest/schema, source validation core และ positive synthetic fixtures 4 ชุด ไม่มี gap-policy behavior/fixture, detector หรือ FI fixture execution, FJ replay, historical population, holdout preflight, event/ATR-event, TP/SL, outcome, candidate/parameter change, optimization, MT5/Strategy Tester, EA/order logic หรือ demo/live.

## Implemented interfaces

Schema `research/schemas/historical_source_manifest.v1.schema.json` freeze:

- `historical_source_manifest.v1`: explicit dataset ID, symbol, timeframe, frozen boundary, `NOT_PROVEN`, raw CSV flag, ordered sources และ expected deterministic timeline.
- `source_file_descriptor.v1`: explicit source ID, display filename, relocatable runtime path, SHA-256, optional byte size, rows, first/last timestamps และ `MT5_TSV_OHLC_V1`.

Module `tools/historical_source_adapter.py` normalize/validate ด้วย Python standard library เท่านั้น. Canonical output ไม่มี absolute/runtime path และ dataset identity hash ใช้ dataset ID, source IDs/hashes, symbol, timeframe และ boundaries; ไม่ใช้ filename/path.

## Explicit mappings

- `FP_SOURCE_CONTRACT_V1`: map FP `source_files[].rows`, hashes/ranges และ frozen contract fields ผ่าน explicit `dataset_context` กับ `source_identities`.
- `FJ_SOURCE_PROVENANCE_V1`: map FJ `sources[].row_count`, hashes/ranges ผ่าน explicit context/identities.

ทั้งสอง mapping ต้องรับ source ID, display filename และ runtime locator อย่าง explicit; ไม่มีการ parse symbol/timeframe/year/boundary จากชื่อไฟล์.

## Source validation

Adapter ตรวจ path exists, SHA-256, optional byte size, required MT5 TSV columns, parseable naive timestamps, finite/positive/internal-consistent OHLC, strict chronology, declared row count, exact first/last timestamps, every row inside boundary, unique source IDs, aggregate duplicate timestamps, source count, total rows, timeline range และ canonical timeline SHA-256.

`broker_history_completeness` ต้องเป็น `NOT_PROVEN` และ `raw_broker_csv_committed` ต้องเป็น `false`. Synthetic TSV เป็น test fixture ไม่ใช่ raw broker CSV.

## Positive fixtures and deterministic replay

| Fixture | Purpose | Result |
|---|---|---|
| A | valid minimal generic manifest | PASS |
| B | valid FP-style contract mapping | PASS |
| C | valid FJ-style provenance mapping | PASS |
| D | valid relocated runtime path, bytes/identity เดิม | PASS |

Harness รัน suite สองรอบในหนึ่ง invocation: run hashes และ golden hash เท่ากัน `717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b`; canonical outputs byte-identical, relocation output identical, runtime timestamps absent, mismatch count `0`.

## Frozen-file boundary

ไฟล์เหล่านี้ต้อง byte-for-byte unchanged และตรวจเทียบ Git blob baseline/final:

- `tools/market_structure_break_retest_detector.py`
- `tools/run_checkpoint_fi_detector_fixtures.py`
- `tests/fixtures/checkpoint_fi_detector_cases.json`
- `tests/fixtures/checkpoint_fi_detector_inputs.json`
- `tests/fixtures/checkpoint_fi_detector_expected.json`

## Deliverables

- `.gitattributes` — บังคับ LF เฉพาะ A1a synthetic TSV เพื่อให้ frozen byte hashes คงที่บน Windows
- `research/schemas/historical_source_manifest.v1.schema.json`
- `tools/historical_source_adapter.py`
- `tools/run_fr_prep_a1a_source_adapter_fixtures.py`
- `tests/fixtures/fr_prep_a1a/` — four manifests, synthetic TSV inputs, golden outputs
- `research/results/checkpoint_fr_prep_a1a_source_adapter_core/checkpoint_fr_prep_a1a_test_summary.json`
- เอกสารนี้และ A1a marker ใน `docs/ai/current-status.md`

## Validation

Required validation: JSON/Python syntax parse, normalized manifests ผ่าน JSON Schema `4/4`, four fixtures PASS, internal two-pass replay PASS, external rerun PASS, docs references resolve, `git diff --check`, frozen hashes unchanged, staged path audit และ no raw broker/event/outcome artifacts.

## FR-Prep-A1b boundary

A1b ทำเฉพาะ negative source-validation fixtures และ deterministic failure contract สำหรับ missing path, hash/optional bytes, schema, timestamp, OHLC, chronology, rows, first/last range, frozen-boundary escape, duplicate source ID/timestamp และ aggregate mismatch. ห้าม implement gap adapter, detector/FI/FJ replay, holdout preflight, event/outcome หรือเปลี่ยน FI core.

## Status

- execution status: `PASS` สำหรับ A1a positive source-adapter fixtures
- broker-history completeness: `NOT_PROVEN`
- detector/FI fixtures/FJ replay/events/outcomes/holdout preflight: `NOT_RUN`
- strategy performance: `NOT_EVALUATED`
- profitability: `NOT_CLAIMED`
- order logic: `NOT_APPROVED`
- candidate: `NOT_READY_FOR_ORDER_LOGIC`
