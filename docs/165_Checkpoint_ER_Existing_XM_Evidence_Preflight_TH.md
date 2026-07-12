# Checkpoint ER: Existing XM Evidence Offline Preflight

วันที่: 2026-07-12

## ขอบเขต

ตรวจไฟล์ existing evidence แบบ read-only ตาม EQ contract โดยไม่เปิด MT5 และไม่สร้างหลักฐานใหม่

ไฟล์ที่พบใน `mt5_artifacts/manual_gap_evidence/GOLD_HASH_H1/` มี 4 ไฟล์:

- README 1 ไฟล์
- CSV ระยะยาว `GOLD#` H1 1 ไฟล์ ครอบคลุม 2020-03-02 ถึง 2026-07-10
- CSV ช่วงมีนาคม 2026 1 ไฟล์
- screenshot ช่วงมีนาคม 2026 1 ไฟล์

SHA-256 ของ CSV ระยะยาว:

`8CE8C11FD29DE0BC807E710DEE43ECE3570BEB1FA68B1693AA5FA6BC4532CAE6`

## EQ Contract Result

- execution status: `PASS`
- frozen/reviewed gaps: `28/28`
- CSV range ครอบคลุม gap timestamps: `28`
- exact screenshots สำหรับ 28 gaps: `0`
- fresh force-refresh manifests ที่มี server/timezone/DST/hash provenance: `0`
- exact archived XM schedule/session files: `0`
- `EXACT_BROKER_EVIDENCE_COMPLETE`: `0/28`
- acceptance state: `CONTEXT_ONLY` ทั้ง 28 rows

CSV ระยะยาวยืนยันว่ามี dataset ที่ครอบคลุมช่วงเวลา แต่ไม่ผ่าน EQ layer A เพราะไม่มี screenshot ต่อ gap, force-refresh record และ manifest ที่ผูก XM server/timezone/DST ส่วน CSV และภาพอีกชุดเป็นเดือนมีนาคม 2026 ซึ่งอยู่นอก frozen population ปี 2023-2025

## Decision

Decision: `ER_BLOCKED_EXISTING_EVIDENCE_INCOMPLETE_0_OF_28`

- policy/validator: `UNCHANGED_NOT_BYPASSED`
- policy gate: `REVIEW_REQUIRED`
- joiner/shadow backtest: `NOT_RUN`
- MT5/Strategy Tester: `NOT_RUN`
- EA/MQL5/presets: `UNCHANGED`
- optimization/order logic/demo-live: `NOT_RUN_NOT_APPROVED`
- strategy performance: `NOT_EVALUATED`
- profitability claim: `NOT_ALLOWED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

Shadow readiness คงที่ `40%` การเปิด MT5 เพื่อเก็บ fresh evidence ต้องได้รับอนุมัติอย่างชัดเจนแยกต่างหาก
