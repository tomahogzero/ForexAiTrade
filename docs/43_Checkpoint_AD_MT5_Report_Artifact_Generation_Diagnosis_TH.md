# Checkpoint AD: MT5 Report Artifact Generation Diagnosis

วันที่จัดทำ: 2026-07-06

## สถานะของ Checkpoint นี้

Checkpoint AD เป็นงานเอกสารและวิเคราะห์สาเหตุเท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk และไม่ได้ claim profitability

## ที่มา

Checkpoint AC รัน Gold no-trade diagnostic ตาม approval phrase แล้ว:

- RunId: `run_20260704_014343_checkpoint_ac_gold_no_trade`
- Symbol: `GOLD#`
- Timeframe: H1
- Date range: `2026-06-01` ถึง `2026-07-01`
- Result: `PARTIAL_TESTER_PASS_REPORT_MISSING`

Checkpoint AC ดีกว่า Checkpoint T เพราะครั้งนี้มี tester log และ EA mirror log จริง แต่ยังไม่ครบ artifact เพราะไม่มี MT5 report file

## สิ่งที่ Checkpoint AC ผลิตได้

Artifact folder:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701`

ไฟล์ที่มี:

- `generated_tester.ini`
- `effective_config_snapshot.set`
- `case.json`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `forbidden_action_grep_summary.txt`
- `status.json`
- `post_run_guardrail_summary.md`

ไฟล์ที่ยังขาด:

- `mt5_report.htm`
- `mt5_report.html`
- `mt5_report.xml`

## หลักฐานจาก log

`tester_log_excerpt.log` ระบุว่า:

- Strategy Tester ทำงานบน `GOLD#,H1`
- มีข้อความ `Test passed`
- final balance อยู่ที่ `10000.00 USD`
- EA diagnostic path ทำงานและมี Price Action / Fibo diagnostic lines

`forbidden_action_grep_summary.txt` ระบุว่า:

- forbidden action marker count = 0
- PriceActionFibo diagnostic count = 552
- no-trade reason found = true
- baseline fallback marker count = 0
- report found = false

## จุดผิดปกติหลัก

ใน `generated_tester.ini` ของ Checkpoint AC มี:

```ini
Report=G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701\mt5_report
ReplaceReport=1
ShutdownTerminal=1
```

MT5 process exited ด้วย code 0 และ tester log ถูกผลิต แต่ไม่มีไฟล์ report ใน path ที่ตั้งไว้

ดังนั้นปัญหาไม่ได้เหมือน Checkpoint T ที่ไม่มี artifact สำคัญเลย แต่แคบลงเป็น:

`Strategy Tester ran and logs were produced, but command-line report generation did not write the expected report file.`

## สมมติฐานสาเหตุ

### 1. MT5 อาจไม่เขียน report ไป absolute path นอก data folder

Checkpoint AC ใช้ absolute path ไปที่:

`G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\...`

แม้ folder นี้เขียนได้จาก PowerShell แต่ยังไม่พิสูจน์ว่า MT5 Strategy Tester ยอมเขียน report ไป path นี้ผ่าน `Report=`

### 2. MT5 อาจต้องการ relative report path ภายใต้ data folder

run เก่าหลายชุดใน `research/runs/` มี `mt5_report.htm` สำเร็จ โดยบาง config ใช้รูปแบบ:

```ini
Report=ForexAiTradeResearch\run_xxx\case_xxx\mt5_report
```

ควรตรวจให้ชัดว่า MT5 build นี้รองรับ:

- absolute path หรือไม่
- relative path ภายใต้ data folder หรือไม่
- ต้องใส่ `.htm` / `.html` ใน `Report=` หรือให้ MT5 เติมเอง

### 3. Runner อาจค้น report ไม่ตรงกับ path ที่ MT5 เขียนจริง

Checkpoint AC ตรวจหา report ที่ artifact folder หลัก แต่ MT5 อาจเขียนไป:

- terminal data folder
- tester agent folder
- current working directory ของ terminal
- path ที่ normalize ต่างจาก expected path

ต้องมี search map ที่เป็นระบบก่อน retry

### 4. `Report=` อาจต้องมี extension สำหรับบาง MT5 build

Checkpoint AC ใช้ report base path `mt5_report` ไม่มีนามสกุล

run เก่าที่สำเร็จบางชุดลงท้ายเป็น `mt5_report.htm` หรือ `mt5_report.html`

ยังไม่ควรสรุปว่าต้องใช้ extension แบบใด จนกว่าจะตรวจจาก historical successful run และ MT5 behavior อย่างเป็นระบบ

### 5. Timing หลัง process exit อาจยังไม่พอสำหรับ report flush

Checkpoint AC process exit แล้ว runner รอและค้น report แต่ควรตรวจว่า:

- report ถูกเขียนช้ากว่า log หรือไม่
- graph/image companion files ถูกสร้างแต่ html ไม่ถูกสร้างหรือไม่
- file stability wait ครอบคลุม report image files หรือไม่

จาก artifact ปัจจุบันยังไม่พบ report companion files เช่น `.png` เช่นกัน

## สิ่งที่ห้ามสรุปเกินหลักฐาน

ห้ามสรุปว่า:

- strategy มี profitability
- Gold strategy พร้อมใช้งาน
- no-trade diagnostic เป็น full pass
- report generation ใช้งานได้
- demo/live forward test เริ่มได้
- ควรเพิ่ม lot/risk เพื่อให้ผลดีขึ้น

Checkpoint AC ให้หลักฐานเฉพาะว่า tester/EA diagnostic logs เกิดขึ้น และไม่พบ forbidden action markers ใน logs ที่มี แต่ full artifact pass ยังไม่ครบเพราะ report หาย

## แผนวิเคราะห์ก่อน retry

ก่อนมีการรัน MT5 อีกครั้ง ต้องทำ Checkpoint AE หรือ checkpoint ถัดไปที่ได้รับ review แล้วเท่านั้น โดยควรตรวจ:

1. เปรียบเทียบ `generated_tester.ini` ของ run ที่สร้าง report สำเร็จกับ Checkpoint AC
2. ตรวจ pattern ของ `Report=` ที่เคยสำเร็จ:
   - absolute path
   - relative path
   - มี extension
   - ไม่มี extension
3. สร้างเอกสาร expected report path matrix
4. กำหนด search locations หลังรัน:
   - artifact folder
   - terminal data folder
   - tester agent folder
   - common files folder
5. ระบุ stale artifact guard เพื่อไม่ให้ไฟล์เก่าถูกใช้เป็นหลักฐาน
6. ระบุว่าถ้า report หายอีก ต้องจัด status เป็น partial/inconclusive ไม่ใช่ pass

## ข้อเสนอสำหรับ Checkpoint ถัดไป

Checkpoint AE ควรเป็น:

`MT5 Report Path Compatibility Preflight and Runner Plan`

ยังไม่ควรรัน Strategy Tester ซ้ำทันที

Checkpoint AE ควรเป็น docs/plan หรือถ้าจะเปลี่ยน runner ต้องเป็น runner-only safety change และต้องผ่าน review ก่อน ไม่ใช่เปลี่ยน strategy

## Guardrails

- No MT5 run
- No Strategy Tester run
- No EA/source change
- No preset change
- No optimization
- No lot/risk increase
- No profitability claim
- No demo/live approval
- No strategy tuning

