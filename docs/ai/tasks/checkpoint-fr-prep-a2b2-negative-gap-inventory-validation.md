# Checkpoint FR-Prep-A2b-2 — Negative Gap-Policy Inventory Validation

## ขอบเขต

Checkpoint นี้เพิ่มเฉพาะ validation ระดับ adapter สำหรับโครงสร้าง ความเป็นเอกลักษณ์ จำนวน allowlist identity และ normalized inventory identity/hash โดยใช้ข้อมูลสังเคราะห์เท่านั้น ไม่มีการเชื่อม detector หรือ FJ runner และไม่ได้อ่าน FQ inventory จริงของช่วง holdout

สถานะที่บันทึกคือ `FR_PREP_A2B2_GAP_VALIDATION_COMPLETE`

## สัญญาที่ตรึง

- schema manifest: `research/schemas/gap_policy_manifest.v1.schema.json`
- registry ครบ A2 จำนวน 37 codes: `research/schemas/gap_policy_validation_codes.v1.json`
- canonical identity/hash contract: `research/schemas/gap_policy_inventory_identity.v1.json`
- adapter: `tools/gap_policy_adapter.py`
- runner: `tools/run_fr_prep_a2b2_negative_gap_inventory_fixtures.py`
- fixtures/golden: `tests/fixtures/fr_prep_a2b2/negative_cases.json` และ `tests/fixtures/fr_prep_a2b2/expected_failures.json`
- summary: `research/results/checkpoint_fr_prep_a2b2_negative_gap_inventory/checkpoint_fr_prep_a2b2_test_summary.json`

Canonical ordering ใช้ `previous_bar_timestamp`, `next_bar_timestamp`, `gap_id`, `source_record_identity` ตามลำดับ การ hash ใช้ canonical JSON แบบ ASCII, sort keys และ separators `,` กับ `:` โดยไม่รวม runtime path, filename หรือ execution timestamp ใน identity payload

## Validation precedence

1. manifest และ artifact structure
2. entry field และ semantic
3. inventory shape รวม exact normalized duplicate
4. unique `gap_id`
5. unique `source_record_identity`
6. unique timestamp pair
7. classification/semantic conflict
8. canonical ordering
9. declared count reconciliation
10. exact classification allowlist และ allowlist hash
11. normalized inventory identity
12. normalized inventory SHA-256

กรณี timestamp pair ซ้ำแยกแบบ deterministic: semantic tuple ต่างกันให้ semantic conflict ก่อน; semantic เหมือนกันแต่ classification ต่างกันให้ classification conflict; ทั้งสองเหมือนกันให้ duplicate timestamp pair ส่วน exact normalized entry ซ้ำจะหยุดก่อน unique ID ตาม inventory-shape precedence

## ผล fixture

Negative fixtures ใหม่ผ่านตาม expected stable code `20/20`:

- inventory shape 3 กรณี
- duplicate/uniqueness และ EO/FJ/FQ mapping 5 กรณี
- timestamp-pair conflict 2 กรณี
- declared count reconciliation 5 กรณี
- allowlist identity/hash 2 กรณี
- normalized inventory identity/hash 2 กรณี
- canonical ordering 1 กรณี

ผล deterministic:

- unexpected pass: `0`
- wrong validation code: `0`
- unknown validation code: `0`
- mismatch: `0`
- run 1/run 2/golden SHA-256: `7b439bf5e716c60d6ba1c9fac8e26402bdba624cee7c8dc7de6c31d1cbd1dbae`
- canonical output byte-identical: `true`

## Regression

- A1a: `4/4 PASS`; SHA-256 `717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b`
- A1b-1: `9/9 PASS`; SHA-256 `97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8`
- A1b-2: `13/13 PASS`; SHA-256 `5bde1d04d27c67a089103c344ff17918a795d9dc14176fae6dffc58782b242a4`
- A2 positive: `8/8 PASS`; relocation identical; SHA-256 `7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff`
- A2b-1: `18/18 PASS`; 17 codes เดิมไม่เปลี่ยน; SHA-256 `e12d040363487ac48f972f86a976aacc72305940a08ce92c1d162544a89357a7`

## Safety

`broker_history_completeness=NOT_PROVEN`, strategy performance `NOT_EVALUATED`, profitability `NOT_CLAIMED`, order logic `NOT_APPROVED`, candidate `NOT_READY_FOR_ORDER_LOGIC`

ไม่ได้ execute detector/FI fixtures, FJ/FQ runner, real holdout, population, event, ATR-event, TP/SL หรือ outcome และไม่ได้ใช้ MT5/Strategy Tester

## Decision

`FR_PREP_A2B2_PASS_GAP_VALIDATION_COMPLETE`

ขั้นถัดไปคือ FR-Prep-A3 — Generic Adapter Contract Closure and Synthetic End-to-End Replay โดยต้องเป็น adapter-only และ synthetic เท่านั้น ห้าม integrate detector หรือ execute real holdout
