# Checkpoint ET: Yearly CSV XM Evidence Intake

วันที่: 2026-07-12

## ขอบเขต

รับและตรวจ raw MT5-style `GOLD#` H1 CSV รายปี 2023-2025 แบบ offline ตาม EQ contract โดยไม่เปิด MT5 เนื่องจากผู้ใช้มี exports ใหม่แล้ว

ไฟล์ที่ตรวจ:

- `GOLD#_H1_202301030100_202312292300.csv`
- `GOLD#_H1_202401020100_202412312000.csv`
- `GOLD#_H1_202501020800_202512311900.csv`

ไม่ commit raw CSV หรือข้อมูลบัญชี

## CSV Gap Confirmation

- execution status: `PASS`
- frozen gaps: `28`
- yearly raw files: `3`
- CSV-confirmed gaps: `28/28`
- duplicate timestamps across yearly files: `0`
- 2023 rows: `5894`
- 2024 rows: `5928`
- 2025 rows: `5894`

สำหรับทุก gap มี bar ก่อนและหลังตรงกับ frozen timestamp และไม่มี H1 bar แทรกภายในช่วง gap

SHA-256:

- 2023: `BBE0C3B83439DBD223FF64F4E6FA75AF84981BEFFF3482CB00161936B56BD468`
- 2024: `883F5076CDC6EF6C30CAF8E995DD7E33F63E7F50E9E2A9F91F77D206FFBD4F0A`
- 2025: `368CE15FA4225C14BC1513D108EC75D1AB49274B82208B36DE03B1CBDC92195B`

## EQ Contract Boundary

CSV exports ยืนยัน absence pattern ใน broker-history dataset ได้ แต่ยังไม่ครบ EQ layer A เพราะไม่มี per-gap screenshot, force-refresh/provenance manifest, XM server/timezone/DST record และยังไม่ครบ layer B เพราะไม่มี exact XM schedule/session provenance

- EQ layer A complete: `0/28`
- EQ layer B complete: `0/28`
- `EXACT_BROKER_EVIDENCE_COMPLETE`: `0/28`
- acceptance state: `CONTEXT_ONLY` ทั้ง 28 rows

## Decision

Decision: `ET_CSV_GAP_CONFIRMATION_PASS_EQ_EVIDENCE_INCOMPLETE`

- policy gate: `REVIEW_REQUIRED`
- policy/validator: `UNCHANGED_NOT_BYPASSED`
- MT5/Strategy Tester: `NOT_RUN`
- joiner/shadow backtest: `NOT_RUN`
- EA/MQL5/presets: `UNCHANGED`
- optimization/order logic/demo-live: `NOT_RUN_NOT_APPROVED`
- strategy performance: `NOT_EVALUATED`
- profitability claim: `NOT_ALLOWED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

Shadow readiness remains `40%`. ขั้นถัดไปต้องขออนุมัติแยกสำหรับเก็บ EQ layer A/B ที่ขาด หรือคง gaps ทั้ง 28 เป็น blocked
