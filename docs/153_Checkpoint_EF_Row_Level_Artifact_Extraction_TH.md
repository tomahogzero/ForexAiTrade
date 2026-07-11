# Checkpoint EF: Row-Level Artifact Extraction

วันที่: 2026-07-11

## Execution Status

ดำเนินการ extraction-only จาก `ea_mirror.log` เดิมของ DZ runs `run_20260711_145612`, `run_20260711_152017`, `run_20260711_153941` ครบ ไม่มีการรัน MT5/Strategy Tester

ผล reconciliation:

- Fibo rows: `2353`
- usable: `1600`
- gaps: `753`
- `PRICE_BETWEEN_EMAS`: `554`
- `TREND_ALIGNMENT_CONFLICT`: `198`
- `EMA_SLOPE_FLAT`: `1`
- windows: `156`
- reconciliation: `PASS`

Artifacts: CSV row-level และ summary JSON/Markdown ภายใต้ `research/results/checkpoint_ef_*`

ผลนี้เป็นความครบถ้วนของ diagnostic artifact ไม่ใช่ performance หรือ profitability evidence

## Gates

- extraction execution: `PASS`
- ED contract reconciliation: `PASS`
- candidate verifier: `NOT_IMPLEMENTED`
- candidate validation: `NOT_RUN`
- existing 20-window gate: `FAIL_REPORTED_SEPARATELY`
- order logic: `FAIL_NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

ขั้นถัดไป: checkpoint แยกสำหรับ offline verifier readiness/implementation review; ห้ามตีความ CSV เป็น trading signal

## Progress

- Research infrastructure: `98%`
- PAF diagnostic pipeline: `98%`
- PAF diagnostic interpretation: `97%`
- Fibo Pullback interpretation: `97%`
- PAF rule-candidate: `94%`
- PAF order-logic: `0%`
- Demo/live: `0%`
