# Checkpoint EW: XM Exact Evidence Collection Blocked

วันที่: 2026-07-13

## อนุมัติและขอบเขต

EW ได้รับอนุมัติให้เก็บ EQ layer A/B สำหรับ frozen `28` `GOLD#` H1 gaps แบบ evidence-only เท่านั้น โดยอนุญาตเฉพาะ MT5 instance ที่ EW เริ่มเองและหยุดได้เฉพาะ PID นั้น

ก่อนเริ่มจริงต้องมี safe export interface ที่สร้าง evidence ตาม EQ contract ได้ครบ หากไม่มีต้องหยุดและรายงาน blocker

## Preflight แบบ Read-Only

- worktree base: `a8a2b0c59c9fd16c35a94c13b619d063cf440dc0`
- ตรวจไม่พบ `terminal64.exe` ที่กำลังรันก่อน EW
- พบ executable: `C:\Program Files\XM Global MT5\terminal64.exe`
- ค้นหาใน repo แล้วไม่พบ UI automation หรือ non-UI exporter ที่สามารถสร้าง fresh `GOLD#` H1 history request, per-gap screenshot, และ EQ provenance manifest ได้
- runner ที่มีอยู่เป็น Strategy Tester/research runners หรือ offline intake; ไม่มี runner สำหรับ evidence bundle นี้

## Stop Gate

EW ไม่เริ่ม MT5 เพราะไม่มี export interface ที่ตรวจสอบได้สำหรับ Layer A ต่อ gap ซึ่งต้องมีอย่างน้อย:

1. fresh history/symbol-bars request หลัง force refresh
2. CSV ครอบคลุมอย่างน้อย 24 ชั่วโมงก่อนและหลัง gap
3. screenshot ที่เห็น `GOLD#`, H1, time axis และ bars ก่อน/หลัง gap
4. terminal path/build, XM server, timezone/DST, capture/export time และ SHA-256 ใน provenance manifest

การเปิด terminal เพียงอย่างเดียวไม่สร้างหลักฐานข้างต้น และห้ามใช้ yearly CSV เดิมแทน fresh layer A หรือเดา/สร้าง layer B จาก pattern

## ผลลัพธ์

- execution status: `BLOCKED`
- blocker: `BLOCKED_NO_SAFE_EXPORT_INTERFACE`
- EW-started MT5 PIDs: `0`
- MT5/Strategy Tester: `NOT_RUN`
- frozen population: `28`
- EQ layer A/B complete: `0/28`, `0/28`
- `EXACT_BROKER_EVIDENCE_COMPLETE`: `0/28`
- policy gate: `REVIEW_REQUIRED`
- strategy performance: `NOT_EVALUATED`
- order logic: `NOT_APPROVED`
- PAF: `NOT_READY_FOR_ORDER_LOGIC`

## ขอบเขตที่ไม่เปลี่ยนแปลง

- policy/validator, EA/MQL5 และ presets: `UNCHANGED_NOT_BYPASSED`
- joiner/shadow backtest/optimization/lot/risk/demo/live: `NOT_RUN`
- automatic gap release: `NOT_DONE`
- profitability claim: `NOT_ALLOWED`

## แนวทางถัดไป

ต้องมี safe export interface ที่ review ได้ก่อนทำ EW ใหม่ ตัวอย่างที่ยอมรับได้คือ user-provided evidence bundles ตาม EQ contract หรือ exporter ที่ระบุ output paths, per-gap capture, provenance manifest และการเริ่ม/หยุดเฉพาะ EW-owned PID ได้ครบ การอนุมัติใหม่ต้องอ้างขอบเขตนี้อีกครั้งก่อนเปิด MT5

Decision: `EW_BLOCKED_NO_SAFE_EXPORT_INTERFACE`.
