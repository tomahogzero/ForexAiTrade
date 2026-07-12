# Checkpoint EQ: Exact XM GOLD# Gap Evidence Contract

วันที่: 2026-07-12

## วัตถุประสงค์

กำหนด contract แบบ fail-closed สำหรับรับหลักฐาน broker-specific ของ 28 gaps จาก EO/EP โดยยังไม่เก็บหลักฐานใหม่ ไม่เปิด MT5 ไม่แก้ policy/validator และไม่รัน joiner หรือ shadow backtest

## Frozen Population

- ใช้ 28 rows จาก `research/results/checkpoint_ep_gap_evidence_review/gap_evidence_review.csv` เท่านั้น
- exact key: `prev_time + next_time + delta_hours`
- symbol: `GOLD#`
- timeframe: `H1`
- source broker/server ต้องเป็น XM instance เดียวกับ raw history ของ EN
- ห้ามเพิ่ม/ลด rows หรือเปลี่ยน timestamps หลังเห็นผล

## Required Evidence ต่อ Gap

### A. Fresh Broker-History Confirmation

ต้องมีทั้งหมด:

- fresh MT5 History/Symbols Bars request สำหรับ `GOLD#` H1 หลัง force refresh
- CSV export ที่ครอบคลุมอย่างน้อย 24 ชั่วโมงก่อนและหลัง gap
- screenshot ที่เห็น exact symbol, H1, time axis, bar ก่อน gap และ bar หลัง gap
- terminal path, terminal build, account server name, export time และ server timezone/DST note
- SHA-256 ของ CSV และ screenshots
- raw files ต้องเก็บใน `mt5_artifacts/manual_gap_evidence/GOLD_HASH_H1/` และห้ามแก้ OHLC/timestamps

หลักฐานชั้น A ยืนยันว่า broker history ไม่มี bars ในช่วงนั้น แต่ยังไม่ยืนยันว่าเป็น scheduled closure

### B. Exact Broker Schedule/Session Provenance

ต้องมีอย่างน้อยหนึ่งแหล่งที่ระบุได้ตรงกับ gap:

- archived official XM notice/schedule ของปีนั้นที่ระบุ Gold/Gold and Silver พร้อม close/reopen time และ timezone หรือ
- official XM support response ที่ระบุ legal entity/account server, instrument, วันที่, close/reopen time และ timezone หรือ
- broker session specification ที่มี effective dates ครอบคลุม gap และอธิบาย DST mapping ได้

หลักฐาน CME/OPM หรือชื่อวันหยุดเพียงอย่างเดียวเป็น `CONTEXT_ONLY` และใช้แทนชั้น B ไม่ได้

## Provenance Manifest

ทุก evidence bundle ต้องมี manifest ต่อ gap:

- `gap_id`, `prev_time`, `next_time`, `delta_hours`
- `runtime_symbol=GOLD#`, `timeframe=H1`
- XM legal entity และ account server
- terminal executable path/build
- server timezone และ DST state ณ วันที่ gap
- source file paths และ SHA-256
- capture/export timestamp
- schedule source URL/file และ archived copy hash
- reviewer notes โดยห้ามแก้ข้อมูลต้นฉบับ

ห้าม commit account number, credentials, tokens หรือข้อมูลส่วนบุคคล ต้อง redact ก่อน staging โดยคง server/entity/symbol/timezone ที่จำเป็น

## Acceptance States

- `EXACT_BROKER_EVIDENCE_COMPLETE`: A และ B ครบ, key ตรง, hashes valid
- `BROKER_HISTORY_ONLY`: A ครบแต่ B ขาด
- `SCHEDULE_ONLY`: B ครบแต่ A ขาด
- `CONTEXT_ONLY`: มีเพียง CME/OPM/holiday context
- `CONFLICTING_EVIDENCE`: เวลา/symbol/server ไม่ตรงกัน
- `INVALID_OR_SENSITIVE`: provenance ไม่ครบหรือมีข้อมูลลับ
- `MISSING`: ไม่มีหลักฐาน

เฉพาะ `EXACT_BROKER_EVIDENCE_COMPLETE` เท่านั้นที่ส่งต่อไป checkpoint policy-decision แยกได้ สถานะนี้ยังไม่อนุมัติ policy change โดยอัตโนมัติ

## Global Gate

- ต้อง reconcile `28/28`
- duplicate/missing/unmapped/conflicting gap ต้องเป็น `0`
- ทุก row ต้องเป็น `EXACT_BROKER_EVIDENCE_COMPLETE`
- ถ้าไม่ครบให้หยุดเป็น `BLOCKED_EXACT_XM_EVIDENCE_INCOMPLETE`
- ห้ามใช้ majority, pattern extrapolation หรือวันหยุดปีอื่นแทน row ที่ขาด

## Guardrails

- EQ เป็น contract-only; evidence collection: `NOT_RUN`
- MT5/Strategy Tester: `NOT_RUN`
- policy/validator: `UNCHANGED_NOT_BYPASSED`
- joiner/shadow backtest: `NOT_RUN`
- EA/MQL5/presets: `UNCHANGED`
- optimization/order logic/demo-live: `NOT_RUN_NOT_APPROVED`
- strategy performance: `NOT_EVALUATED`
- profitability claim: `NOT_ALLOWED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

## Decision

Decision: `EQ_EXACT_XM_GAP_EVIDENCE_CONTRACT_DEFINED`

Shadow readiness คงที่ `40%` การเก็บ/รับหลักฐานจริงต้องได้รับอนุมัติ checkpoint แยกพร้อมระบุว่าจะเปิด MT5 หรือรับไฟล์จากผู้ใช้ ห้ามดำเนินการต่อโดยอัตโนมัติ
