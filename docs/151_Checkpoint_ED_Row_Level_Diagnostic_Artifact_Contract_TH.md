# Checkpoint ED: Row-Level Diagnostic Artifact Contract

วันที่: 2026-07-11

## เป้าหมาย

กำหนด contract สำหรับ artifact ที่ขาดตาม EC โดยยังไม่สร้าง artifact และไม่รัน MT5/Strategy Tester

ไฟล์เป้าหมายในอนาคต: `research/results/checkpoint_ee_paf_fibo_row_level_diagnostics.csv`

## Required Schema

ทุกแถวต้องมี:

- `run_id`, `window_index`, `phase`, `event_time`
- `runtime_symbol`, `timeframe`, `authoritative_source`
- `classification`
- `paf_candidate_direction`, `paf_direction_is_usable_for_first_touch`
- `paf_direction_source`, `paf_direction_reason`
- `paf_fibo_direction_gap_reason`
- `schema_origin` เป็น `NATIVE` หรือ `LEGACY_NORMALIZED`

ห้ามมี account credential, token, absolute user profile path หรือข้อมูลส่วนบุคคล และ release/review ต้องไม่รวม `.ex5`, `.pyc`, `__pycache__`, nested zip, `.git` หรือ `.agents`

## Completeness Gates

- rows รวมต้องเท่ากับ DZ Fibo rows `2353`
- usable=`true` ต้องเท่ากับ `1600`
- usable=`false` ต้องเท่ากับ `753`
- gap reasons: `PRICE_BETWEEN_EMAS=554`, `TREND_ALIGNMENT_CONFLICT=198`, `EMA_SLOPE_FLAT=1`
- gap reason attribution ต้องครบ `753/753`
- ครบทั้ง 156 windows และ window index `1..156` ไม่ซ้ำ/ไม่ขาด
- runtime symbol ต้องรักษา broker-specific `GOLD#`; ห้ามแปลงเป็น hardcoded `XAUUSD`
- provenance field ต้องไม่ว่างทุกแถว
- conservation และ aggregate reconciliation กับ DZ summary ต้อง PASS

ห้าม reconstruct แถวจาก aggregate counts, ห้ามสุ่มข้อมูล และห้ามแก้ threshold เพื่อให้ gate ผ่าน

## Decision

`ROW_LEVEL_ARTIFACT_CONTRACT_DEFINED`

- artifact production: `NOT_RUN`
- artifact acceptance: `NOT_EVALUATED`
- verifier implementation: `NOT_APPROVED`
- order logic: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- profitability claim: `NOT_ALLOWED`

## Next Safe Step

Checkpoint EE docs-only artifact-production approval package ต้องระบุ source runs เดิม, extraction-only workflow, exact output, validation commands และ approval phrase ก่อน execution แยกต่างหาก

## Progress

- Research infrastructure: `97%`
- PAF diagnostic pipeline: `96%`
- PAF diagnostic interpretation: `97%`
- Fibo Pullback interpretation: `97%`
- PAF rule-candidate: `92%`
- PAF order-logic: `0%`
- Demo/live: `0%`
