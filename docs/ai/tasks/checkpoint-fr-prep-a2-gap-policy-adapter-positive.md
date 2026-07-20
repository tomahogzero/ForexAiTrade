# Checkpoint FR-Prep-A2 — Generic Gap-Policy Adapter Core and Positive Fixtures

วันที่: 2026-07-20

สถานะ: `FR_PREP_A2_GAP_POLICY_ADAPTER_POSITIVE`

Decision: `FR_PREP_A2_PASS_GAP_ADAPTER_POSITIVE`

## ขอบเขต

A2 implement เฉพาะ `gap_policy_manifest.v1`, `gap_policy_entry.v1`, explicit EO/FJ CSV mapping, explicit FQ inventory mapping และ positive synthetic fixtures 8 ชุด Adapter แปลงคำสั่ง gap เป็น normalized representation เท่านั้น ไม่ execute detector state reset, detector/FI, FJ population, holdout preflight, historical population, event/ATR-event, TP/SL หรือ outcome

## Generic interfaces

- Schema: `research/schemas/gap_policy_manifest.v1.schema.json`
- Adapter: `tools/gap_policy_adapter.py`
- Manifest identity ใช้ policy ID, schema version, source contract type, artifact SHA-256, exact classification allowlist และ normalized-content SHA-256
- `runtime_path` เป็น locator เท่านั้นและไม่ปรากฏใน canonical output
- normalized entry เก็บ `gap_id`, timestamp pair, source classification, canonical closure disposition, semantic booleans ทั้ง 7 ค่า, source contract type และ source record identity
- canonical entries เรียงด้วย previous timestamp, next timestamp, gap ID และ source record identity

## Exact frozen classification allowlists

Adapter ใช้ exact membership เท่านั้น ห้าม prefix/substring inference และห้าม reclassify:

| Source contract | Accepted closure classifications | Known fail-closed classification |
|---|---|---|
| `GENERIC_GAP_POLICY_V1` | `ACCEPTED_CLOSURE` | `UNVERIFIED_GAP` |
| `EO_FJ_CSV_V1` | `ACCEPTED_DAILY_BROKER_SESSION_GAP`, `ACCEPTED_WEEKEND_MARKET_CLOSURE` | `BLOCKED_UNCLASSIFIED_GAP` |
| `FQ_GAP_INVENTORY_V1` | `ACCEPTED_ROUTINE_DAILY_SESSION_CLOSURE`, `ACCEPTED_ROUTINE_WEEKEND_CLOSURE` | `UNVERIFIED_GAP` |

Accepted closure มี `accepted_for_trading_bar_skip=true`, `fail_closed_required=false` และ reset/prohibit/warmup flags ทั้งหมดเป็น `false`; closure ถูก represent ว่า skip โดยไม่ consume valid trading-bar count. Known unverified classification มีค่าตรงข้ามและ reset/prohibit/warmup flags ทั้งหมดเป็น `true`.

## Explicit mappings

- EO/FJ: `prev_time -> previous_bar_timestamp`, `next_time -> next_bar_timestamp`, `policy_status -> policy_classification`; gap ID เป็น deterministic hash จาก frozen policy/row/pair/classification และ source record identity เป็น explicit contract/policy/CSV row number. Duplicate IDs, source identities หรือ timestamp pairs ถูก reject แทน silent overwrite
- FQ: preserve `gap_id` และ timestamp/classification fields; source identity ผูกกับ FQ contract และ gap ID. Adapter verify `accepted_for_trading_bar_skip` กับ `fail_closed_required` ว่าตรง exact frozen classification ก่อน derive reset/prohibit/warmup representation โดยไม่ reclassify gap

## Positive fixtures and deterministic replay

Fixtures A–H ครอบคลุม generic accepted, generic unverified, EO accepted, EO blocked/unverified, FQ accepted, FQ unverified, mixed ordered inventory และ runtime relocation. ผล `8/8 PASS`; mismatch `0`; relocation identical; canonical runtime paths/timestamps absent.

A2 run 1, run 2 และ golden SHA-256 เท่ากัน:

`7a6c6b95c1f1019be4f743906dfc633b26069f14a0df2e63236c121b33d7f6ff`

## A1 regression

- A1a: `4/4 PASS`; SHA-256 `717da59654afbab1a983a5444d65739df5541b593d6d393fa3bc2a363f57261b`
- A1b-1: `9/9 PASS`; SHA-256 `97cf9cc363d58615fab7f1c50f7c8535498a62aaf39485810d3975863c37cbb8`
- A1b-2: `13/13 PASS`; SHA-256 `5bde1d04d27c67a089103c344ff17918a795d9dc14176fae6dffc58782b242a4`
- stable source-validation codes และ precedence ไม่เปลี่ยน

## Frozen files

ไฟล์ detector/FI ทั้ง 5 และ runner ต่อไปนี้ต้อง byte-for-byte unchanged:

- `tools/run_checkpoint_fj_historical_event_population.py`
- `tools/run_checkpoint_fq_holdout_gap_boundary.py`

## Safety status

`broker_history_completeness=NOT_PROVEN`; strategy performance `NOT_EVALUATED`; profitability `NOT_CLAIMED`; order logic `NOT_APPROVED`; candidate `NOT_READY_FOR_ORDER_LOGIC`. ไม่มี real 2020–2022 population inspection/execution ใน A2.

## Exact next step

FR-Prep-A2b — Negative Gap-Policy Validation and Frozen Failure Codes.
