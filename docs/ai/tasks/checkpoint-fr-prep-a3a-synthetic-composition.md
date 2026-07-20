# Checkpoint FR-Prep-A3a — Synthetic Dataset Execution Descriptor and Positive Composition Replay

## ขอบเขต

Checkpoint นี้สร้าง `dataset_execution_descriptor.v1` จาก historical source manifest และ gap-policy inventory ที่ผ่าน validation แล้ว โดยใช้ fixture สังเคราะห์เท่านั้น ไม่มีการอ่าน FJ/FQ/holdout จริง และไม่มี detector integration

## สัญญาและผลลัพธ์

- schema: `research/schemas/dataset_execution_descriptor.v1.schema.json`
- composition adapter: `tools/dataset_execution_descriptor_adapter.py`
- deterministic runner: `tools/run_fr_prep_a3a_synthetic_composition_fixtures.py`
- fixtures/golden: `tests/fixtures/fr_prep_a3a/`
- summary: `research/results/checkpoint_fr_prep_a3a_synthetic_composition/checkpoint_fr_prep_a3a_test_summary.json`

Descriptor ระบุ dataset ID/role, symbol, timeframe, frozen boundaries, source manifest identity/SHA-256, canonical timeline identity/SHA-256/count/boundary, gap-policy identity/SHA-256, counts ตาม classification และ closure disposition, allowlist identity, completeness และ contract versions

ทุก descriptor ตรึง `execution_mode=ADAPTER_VALIDATION_ONLY`, `detector_execution_allowed=false` และ `outcome_execution_allowed=false`

## Cross-contract checks

- binding dataset, symbol, timeframe และ boundaries ต้องตรงกับ source contract
- previous/next timestamp ของ gap ทุกอันต้องอยู่ใน canonical synthetic timeline และอยู่ใน frozen boundary
- gap classification/disposition counts ต้องมาจาก normalized inventory
- identity ไม่ใช้ runtime path หรือ filename
- broker history completeness ต้องเป็น `NOT_PROVEN`

## Positive fixtures

ผ่าน `8/8`:

1. generic source + accepted closure
2. generic source + UNVERIFIED_GAP
3. FP-style source + FQ-style gaps
4. FJ-style source + EO/FJ-style gaps
5. multiple synthetic source files + mixed gaps
6. runtime-path relocation
7. EO/FJ และ FQ normalized semantics ที่เทียบเท่ากัน
8. repeated deterministic composition

Golden/replay SHA-256 คือ `743b528744ff03a33d6805099e1618dcafc8f426f7fd8bf7f885e79d5a7827bd`; mismatch `0`; relocation และ repeated composition เหมือนกันแบบ byte-identical

## Guard

`AdapterValidationOnlyGuard` บล็อกด้วย code `ADAPTER_VALIDATION_ONLY_EXECUTION_PROHIBITED` ก่อนทำงานทุกกรณี:

- detector execution
- event emission
- ATR-event emission
- TP/SL calculation
- outcome emission

ดังนั้น checkpoint นี้ไม่มี detector, event, ATR-event, TP/SL หรือ outcome ถูกสร้าง

## Regression และ safety

- A1a/A1b-1/A1b-2: `4/4`, `9/9`, `13/13 PASS`
- A2/A2b-1/A2b-2: `8/8`, `18/18`, `20/20 PASS`
- hashes และ stable codes เดิมไม่เปลี่ยน
- `broker_history_completeness=NOT_PROVEN`
- strategy performance `NOT_EVALUATED`; profitability `NOT_CLAIMED`; order logic `NOT_APPROVED`; candidate `NOT_READY_FOR_ORDER_LOGIC`

ไม่ได้ execute detector/FI, FJ replay, holdout preflight, real FQ inventory, population, events/outcomes หรือ MT5/Strategy Tester

## Decision

`FR_PREP_A3A_PASS_SYNTHETIC_COMPOSITION`

ขั้นถัดไป: FR-Prep-A3b — Synthetic Dataset Execution Descriptor Negative Cross-Contract Validation and Frozen Failure Codes. ขอบเขตยังเป็น adapter-only/synthetic และห้าม detector integration หรือ real holdout execution
