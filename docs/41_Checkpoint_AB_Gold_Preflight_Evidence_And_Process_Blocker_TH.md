# Checkpoint AB: Gold Preflight Evidence And Process Blocker

วันที่จัดทำ: 2026-07-04

## วัตถุประสงค์

Checkpoint AB บันทึกหลักฐาน preflight ที่ผู้ใช้ส่งมาเพื่อเตรียม Gold no-trade diagnostic run ในอนาคต และบันทึก blocker สำคัญที่พบก่อนรันจริง

งานนี้ยังไม่รัน MT5 และยังไม่รัน Strategy Tester

## ขอบเขต

- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ runner
- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่ spawn `terminal64.exe`
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- ไม่อนุมัติ demo/live trading

## Evidence ที่ผู้ใช้ส่งมา

```text
MT5 Data Folder:
C:\Users\tomah\AppData\Roaming\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05

Terminal64:
C:\Program Files\XM Global MT5

Gold Symbol:
GOLD#

Gold H1 history:
yes

Report folder:
G:\AiServer\Codex\ForexAiTrade\mt5_artifacts

Other MT5 running:
no
```

## Codex Path Verification

Codex ตรวจแบบ filesystem-only แล้ว:

- MT5 Data Folder exists: `true`
- `C:\Program Files\XM Global MT5\terminal64.exe` exists: `true`
- Report folder exists / writable marker created: `true`

## Process Preflight Finding

Codex ตรวจ process list แบบไม่รัน MT5 และพบ:

```text
terminal64.exe still running
Path: C:\Program Files\XM Global MT5\terminal64.exe
```

ดังนั้นสถานะจริง ณ เวลาตรวจคือ:

```text
Other MT5 running: yes
```

แม้ผู้ใช้ตั้งใจส่งว่า `no`

หลังจากนั้นผู้ใช้แจ้งว่าเพิ่งปิด MT5 แล้ว Codex ตรวจซ้ำด้วย `Get-Process terminal64` แบบอ่านอย่างเดียว และไม่พบ process แล้ว

สถานะล่าสุด:

```text
Other MT5 running: no
Process blocker: RESOLVED_BY_USER
```

## Interpretation

การพบ `terminal64.exe` ที่เปิดอยู่เป็น blocker สำหรับ automation retry เพราะอาจทำให้:

- spawned `/config` process ถูก instance เดิม intercept
- terminal ที่ spawn ใหม่ exit code 0 แต่ Strategy Tester ไม่ได้รันจริง
- report/log ไม่ถูกสร้าง
- artifact ที่ขาดทำให้ผลเป็น `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`

นี่ตรงกับความเสี่ยงที่พบจาก Checkpoint T

## Retry Status

Retry ยังถูกบล็อก แม้ process blocker จะถูกแก้แล้ว

ยังไม่สามารถอนุมัติรัน Gold diagnostic ได้จนกว่า:

- Codex ตรวจ `Get-Process terminal64` แล้วไม่พบ process ที่เปิดอยู่ก่อนเริ่มอีกครั้งใน checkpoint execution จริง
- artifact paths ถูกยืนยัน
- date range ถูกกำหนดชัดเจนและไม่เกิน 1 เดือน
- มี explicit approval phrase รอบใหม่

## Recommended Future Approval Phrase

หลังปิด MT5 และกำหนดวันที่แล้ว ผู้ใช้ควรใช้รูปแบบ:

```text
Approved to execute Checkpoint AC Gold no-trade diagnostic with symbol GOLD# timeframe H1 date range YYYY-MM-DD to YYYY-MM-DD using verified artifact paths.
```

## Stop Conditions For Future Run

ต้องหยุดถ้า:

- ยังพบ `terminal64.exe` เปิดอยู่ก่อนเริ่ม
- terminal path หรือ data folder ไม่ตรง
- report folder เขียนไม่ได้
- symbol ไม่ใช่ `GOLD#` ตามที่อนุมัติ
- H1 history ไม่พร้อม
- date range เกิน 1 เดือน
- optimization เปิดอยู่
- effective config ไม่ตรง diagnostic/no-trade mode
- มี market order
- มี pending order
- มี position modification
- มี baseline fallback
- artifact ไม่ครบหลังรัน

## สรุป

หลักฐานสำคัญส่วนใหญ่ถูกต้องแล้ว และผู้ใช้ปิด MT5 จน process blocker ถูก resolve แล้ว

Checkpoint AB ยังเป็น diagnosis/preflight checkpoint เท่านั้น ไม่ใช่ execution approval
