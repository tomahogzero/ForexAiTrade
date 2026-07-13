# Checkpoint EV: XM Exact Gap Evidence Collection Approval Package

วันที่: 2026-07-13

## วัตถุประสงค์

จัดทำ approval package สำหรับ Checkpoint EW ในอนาคต เพื่อเก็บหลักฐานตาม EQ contract ของ frozen `28` gaps เท่านั้น งาน EV เป็นเอกสาร-only: ไม่เปิด MT5, ไม่เก็บหลักฐานใหม่, และไม่เปลี่ยนสถานะ gap ใด

## สถานะก่อนเริ่ม EW

- frozen population: `28` gaps, exact key `prev_time + next_time + delta_hours`
- symbol/timeframe: `GOLD#` / `H1`
- ET ยืนยันจาก yearly CSV ว่าไม่มี interior H1 bar ครบ `28/28`
- EQ layer A complete: `0/28`
- EQ layer B complete: `0/28`
- `EXACT_BROKER_EVIDENCE_COMPLETE`: `0/28`
- policy gate: `REVIEW_REQUIRED`

CSV เดิมเป็นหลักฐาน absence pattern เท่านั้น ห้ามใช้แทน fresh per-gap broker-history evidence หรือ XM schedule/session provenance

## ขอบเขต EW ที่อนุญาตได้หลังได้รับอนุมัติแยก

1. เก็บหรือรับ evidence bundle สำหรับ frozen 28 gaps ตาม EQ contract เท่านั้น
2. Layer A ต่อ gap ต้องมี fresh `GOLD#` H1 broker-history confirmation, CSV coverage ก่อน/หลัง gap อย่างน้อย 24 ชั่วโมง, screenshot ที่เห็น symbol/H1/time axis/ก่อน-หลัง gap, และ manifest ที่มี terminal path/build, XM server, timezone/DST, capture time และ SHA-256
3. Layer B ต่อ gap ต้องมี archived official XM schedule/notice, official XM support response หรือ broker session specification ที่ระบุ instrument, วันที่, close/reopen time และ timezone/DST ตรงกับ gap
4. หาก Codex ต้องเปิด terminal: เริ่มได้เฉพาะ instance ที่ Codex เริ่มเอง, บันทึก exact PID, และหยุดได้เฉพาะ PID นั้น ห้าม attach, kill, restart หรือควบคุม terminal ที่ไม่ได้เริ่มเอง
5. หากไม่มี export interface ที่ตรวจสอบได้ ให้หยุดเป็น `BLOCKED_NO_SAFE_EXPORT_INTERFACE`; ห้ามสร้างหรือเดา evidence จาก CSV เดิม
6. เก็บ raw evidence ไว้นอก Git; ก่อน staging ต้อง redact account number, credentials, token และข้อมูลส่วนบุคคล

## สิ่งที่ EW ห้ามทำ

- ห้ามรัน Strategy Tester, optimization, joiner หรือ shadow backtest
- ห้ามเปลี่ยน policy/validator, EA/MQL5, presets, order logic, lot หรือ risk
- ห้ามเปิด demo/live, ส่งคำสั่ง BUY/SELL หรืออ้าง profitability
- ห้าม release gap แม้ evidence บางส่วนผ่าน

## Gate และผลลัพธ์

- acceptance ต่อ row: `EXACT_BROKER_EVIDENCE_COMPLETE` ต้องมี Layer A และ B ครบพร้อม key/provenance/hash ที่ตรงกัน
- global pass: `28/28` complete, missing/duplicate/unmapped/conflicting/sensitive rows เป็น `0`
- หากไม่ครบแม้เพียง row เดียว: `BLOCKED_EXACT_XM_EVIDENCE_INCOMPLETE`
- Checkpoint EW ต้องรายงาน execution status แยกจาก strategy performance เสมอ
- หลักฐานที่รับเข้ามาแล้วต้องผ่าน offline intake/review checkpoint แยกก่อน policy decision ใด ๆ

## ข้อความอนุมัติที่ต้องใช้สำหรับ EW

ผู้ใช้ต้องอนุมัติด้วยข้อความที่ระบุครบถ้วนในสาระสำคัญดังนี้:

`อนุมัติ Checkpoint EW ให้เก็บหลักฐาน EQ layer A และ B สำหรับ frozen 28 GOLD# H1 gaps เท่านั้น แบบ evidence-only โดยใช้เฉพาะ MT5 instance ที่ Codex เริ่มเองและหยุดได้เฉพาะ PID ที่เริ่มเอง; ห้าม Strategy Tester, order logic, policy/validator change, joiner, shadow backtest, EA/preset change, optimization, demo/live และห้าม release gap อัตโนมัติ หาก evidence ไม่ครบ 28/28 หรือไม่มี safe export interface ให้หยุดและรายงาน blocker`

การอนุมัติ EV หรือคำว่า "ต่อได้" เพียงอย่างเดียวไม่ใช่การเริ่ม EW และไม่ใช่อนุมัติ policy release/order logic

## Guardrails และผลสรุป

- EV execution status: `PASS`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`
- profitability claim: `NOT_ALLOWED`
- MT5/Strategy Tester: `NOT_RUN`
- policy/validator, EA/MQL5 และ presets: `UNCHANGED_NOT_BYPASSED`

Decision: `EV_EVIDENCE_COLLECTION_APPROVAL_PACKAGE_CREATED`.

Shadow readiness remains `40%`. EW remains `BLOCKED_UNTIL_EXACT_USER_APPROVAL`.
