# Checkpoint BV: PAF Gold H1 Evidence Intake Preflight

Checkpoint BV ตรวจรับหลักฐาน manual สำหรับ `GOLD#` H1 daily session gaps ตามคู่มือ Checkpoint BU

รอบนี้เป็น documentation / file-system preflight only:

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ production validator
- ไม่รัน joiner
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุป profitability

## Expected Evidence Folder

โฟลเดอร์ที่คาดว่าจะได้รับหลักฐาน:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_gap_evidence\GOLD_HASH_H1\`

## Preflight Result

ผลตรวจ:

`MISSING_EVIDENCE_FOLDER`

ยังไม่พบโฟลเดอร์หลักฐาน manual ตาม path ที่กำหนดไว้

## Evidence Status

`WAITING_FOR_USER_EVIDENCE`

## Required Evidence ที่ยังขาด

- Screenshot จาก MT5 chart สำหรับ `GOLD#` H1 รอบ daily gaps ทั้ง 5 จุด
- CSV export `GOLD#` H1 ช่วงยาวขึ้น เช่น `2026-02-01` ถึง `2026-04-01`
- การยืนยันว่า CSV เป็น H1 ไม่ใช่ M1
- Optional: symbol/session specification screenshot
- Manual notes ระบุ terminal, account type, exact symbol, timeframe, export date, server time ถ้ารู้

## Gate Status

| Gate | Status |
|---|---|
| Daily session gap approval | `BLOCKED` |
| Joiner | `BLOCKED` |
| Production validator change | `BLOCKED` |
| Optimization | `BLOCKED` |
| Demo/live | `BLOCKED` |

## Decision

- `EVIDENCE_INTAKE_PREFLIGHT_DONE`
- `MISSING_EVIDENCE_FOLDER`
- `WAITING_FOR_USER_EVIDENCE`
- `DAILY_SESSION_GAP_STILL_NOT_APPROVED`
- `JOINER_STILL_BLOCKED`
- `VALIDATOR_PRODUCTION_NOT_CHANGED`
- `MT5_NOT_RUN`
- `STRATEGY_TESTER_NOT_RUN`
- `EA_SOURCE_NOT_CHANGED`
- `PRESETS_NOT_CHANGED`
- `NO_OPTIMIZATION_APPROVED`
- `NO_PROFITABILITY_CLAIM`

## What User Should Do Next

ให้สร้างหรือวางไฟล์หลักฐานไว้ที่:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\manual_gap_evidence\GOLD_HASH_H1\`

โครงสร้างที่แนะนำ:

```text
GOLD_HASH_H1/
  screenshots/
  csv/
  notes/
```

หลังจากวางหลักฐานแล้ว ให้บอก Codex ว่า:

`หลักฐาน GOLD# H1 gap พร้อมแล้ว ตรวจ Checkpoint BV ต่อได้`

จากนั้น Codex จึงค่อยทำ evidence review รอบถัดไป
