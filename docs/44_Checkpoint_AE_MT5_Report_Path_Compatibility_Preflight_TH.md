# Checkpoint AE: MT5 Report Path Compatibility Preflight and Runner Plan

วันที่จัดทำ: 2026-07-06

## สถานะของ Checkpoint นี้

Checkpoint AE เป็นงานเอกสารและแผน runner เท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk และไม่ได้ claim profitability

## เป้าหมาย

Checkpoint AC รัน Gold no-trade diagnostic แล้วได้ tester log และ EA mirror log แต่ไม่มี `mt5_report.htm`

Checkpoint AD สรุปว่าสาเหตุหลักน่าจะอยู่ที่ MT5 command-line report generation / report path behavior

Checkpoint AE จึงกำหนดแผน compatibility preflight และ runner behavior ก่อนจะมี retry รอบใหม่

## ขอบเขตที่อนุญาต

อนุญาตเฉพาะ:

- อ่านเอกสารและ artifact เดิม
- เปรียบเทียบ pattern ของ `Report=` จาก run เก่าที่อยู่ใน repo
- เขียนแผน runner/report path
- เขียน GPT review request

ไม่อนุญาต:

- รัน MT5
- รัน Strategy Tester
- เปิด order
- สร้าง pending order
- modify position
- optimize parameter
- เพิ่ม lot/risk
- เปลี่ยน EA/source code
- เปลี่ยน presets
- อ้างว่าระบบทำกำไรได้

## หลักฐานจาก Checkpoint AC

RunId:

`run_20260704_014343_checkpoint_ac_gold_no_trade`

ผล:

`PARTIAL_TESTER_PASS_REPORT_MISSING`

Checkpoint AC config ใช้:

```ini
Report=G:\AiServer\Codex\ForexAiTrade\mt5_artifacts\run_20260704_014343_checkpoint_ac_gold_no_trade\GOLD_HASH_H1_PAF_DIAG_20260601_20260701\mt5_report
ReplaceReport=1
ShutdownTerminal=1
```

ผลที่เกิดขึ้น:

- Strategy Tester log มี
- EA mirror log มี
- Price Action / Fibo diagnostic lines มี
- forbidden action marker count = 0
- baseline fallback marker count = 0
- `mt5_report.htm` ไม่มี

## Historical Report Pattern ที่พบใน repo

จาก checked-in research runs:

- PASS report examples จำนวน 52 รายการ ใช้ `Report=` แบบ relative ใต้ terminal data folder:

```ini
Report=ForexAiTradeResearch\run_xxx\case_xxx\mt5_report
```

และ MT5 สร้าง report เป็น:

```text
mt5_report.htm
```

ตัวอย่าง PASS:

```text
research\runs\run_20260619_221606\GOLD_HASH_H4_10000_out_of_sample
Report=ForexAiTradeResearch\run_20260619_221606\GOLD_HASH_H4_10000_out_of_sample\mt5_report
Output copied back as mt5_report.htm
```

```text
research\runs\run_20260621_173616\GOLD_HASH_H4_30000_validation
Report=ForexAiTradeResearch\run_20260621_173616\GOLD_HASH_H4_30000_validation\mt5_report
Output copied back as mt5_report.htm
```

NO_REPORT examples include absolute report paths:

```ini
Report=G:\AiServer\Codex\ForexAiTrade\research\runs\run_20260619_220639\GOLD_HASH_H4_10000_out_of_sample\mt5_report.html
```

```ini
Report=G:\AiServer\Codex\ForexAiTrade\research\runs\run_20260619_221044\GOLD_HASH_H4_10000_out_of_sample\mt5_report
```

ข้อสรุปแบบระมัดระวัง:

- Historical PASS evidence สนับสนุน `Report=ForexAiTradeResearch\...\mt5_report` แบบ relative ใต้ data folder
- Absolute `G:\...` path ยังไม่ควรถูกใช้เป็น default สำหรับ retry
- ยังไม่ควรสรุปว่า absolute path ใช้ไม่ได้ 100% เพราะ run เก่าบางตัวอาจ fail จากสาเหตุอื่นด้วย
- แต่สำหรับ safety/reliability retry รอบต่อไป ควรเลือก pattern ที่มีหลักฐาน PASS มากที่สุด

## Runner Plan สำหรับ report artifact

ถ้ามี runner-only change ใน checkpoint ถัดไป ควรทำตามแผนนี้:

### 1. ใช้ terminal-data-folder relative report request เป็น default

เมื่อรู้ `TerminalDataFolder` แล้ว ให้ตั้ง `Report=` ใน tester config เป็น:

```ini
Report=ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report
```

ไม่ควรใช้ absolute `G:\...\mt5_artifacts\...\mt5_report` ใน `Report=` จนกว่าจะพิสูจน์ว่า MT5 build นี้รองรับ

### 2. Pre-create terminal report folder

ก่อนรันในอนาคต ให้สร้าง folder:

```text
<TerminalDataFolder>\ForexAiTradeResearch\<RunId>\<CaseId>\
```

และเขียน marker file เช่น:

```text
report_preflight_marker.txt
```

marker นี้ใช้พิสูจน์ว่า Codex เขียน folder ได้ ไม่ใช่ proof ว่า MT5 สร้าง report แล้ว

### 3. Search report ใน terminal report folder ก่อน

หลังรันในอนาคต ให้ค้นหา:

- `mt5_report`
- `mt5_report.htm`
- `mt5_report.html`
- `mt5_report.xml`
- `mt5_report.png`
- `mt5_report-hst.png`
- `mt5_report-mfemae.png`
- `mt5_report-holding.png`

ใต้:

```text
<TerminalDataFolder>\ForexAiTradeResearch\<RunId>\<CaseId>\
```

### 4. Copy report artifacts กลับไป case artifact folder

ถ้าเจอ report ใน terminal data folder ให้ copy กลับไป:

```text
<OutputRoot>\<RunId>\<CaseId>\
```

และบันทึกทั้ง:

- `terminal_report_path`
- `copied_report_path`
- `report_artifact_status`
- `report_companion_files`

### 5. ห้ามใช้ stale artifacts

ก่อน retry ในอนาคต ต้อง record:

- folder มีอยู่ก่อนหรือไม่
- มี `mt5_report*` เก่าอยู่ก่อนหรือไม่
- timestamp ของ marker
- timestamp ของ terminal/tester/EA logs

ถ้า report timestamp เก่ากว่า run start time ต้องไม่ถือว่า pass

### 6. Status rule ถ้า report หายอีก

ถ้า tester/EA logs มี แต่ report หาย:

```text
PARTIAL_TESTER_PASS_REPORT_MISSING
```

ถ้าไม่มี tester/EA logs และไม่มี report:

```text
FAILED_NO_TESTER_ARTIFACTS
```

ห้าม classify เป็น full pass ถ้า report artifact ยังขาด

## Path Compatibility Matrix

| Candidate | Example `Report=` | Evidence | Recommendation |
|---|---|---|---|
| Relative under data folder, no extension | `ForexAiTradeResearch\RunId\CaseId\mt5_report` | 52 PASS checked-in examples created `.htm` | Preferred default |
| Absolute path to repo artifact folder, no extension | `G:\...\mt5_artifacts\RunId\CaseId\mt5_report` | Checkpoint AC produced logs but no report | Do not use as default |
| Absolute path with `.html` | `G:\...\mt5_report.html` | Historical NO_REPORT examples exist | Avoid until proven |
| Relative path with explicit `.htm` | `ForexAiTradeResearch\RunId\CaseId\mt5_report.htm` | Not enough checked-in evidence | Candidate only after review |

## Stop Conditions สำหรับ future retry

ให้ block retry ถ้า:

- `TerminalDataFolder` ไม่ชัดเจน
- terminal report folder สร้างไม่ได้
- marker file เขียนไม่ได้
- มี `terminal64.exe` instance ที่อาจ intercept `/config`
- `Report=` ไม่ตรงกับ reviewed path mode
- `Optimization` ไม่เป็น `0`
- symbol/timeframe/date range ไม่ตรง approval
- EA/source หรือ presets drift จาก reviewed commit
- artifact search matrix ไม่ถูกกำหนด
- stale artifact guard ไม่ครบ

## Recommendation สำหรับ Checkpoint ถัดไป

Checkpoint AF ควรเป็นหนึ่งในสองทาง:

1. **Runner-only implementation**: ปรับ runner ให้ใช้ terminal-data-folder relative `Report=` เป็น default, copy report/companion files กลับ artifact folder, และบันทึก `terminal_report_path`/`copied_report_path`
2. **No-code reviewed retry approval**: ถ้า runner ปัจจุบันทำ pattern นี้ได้อยู่แล้ว ต้องสร้าง approval pack ที่บังคับใช้ `TerminalDataFolder` และ relative report path เท่านั้น

ยังไม่ควร retry MT5 จนกว่า GPT review เห็นว่า AE plan ปลอดภัยและ user อนุมัติ checkpoint ถัดไปอย่างชัดเจน

## Guardrails

- No MT5 run
- No Strategy Tester run
- No terminal spawn
- No EA/source change
- No preset change
- No optimization
- No lot/risk increase
- No profitability claim
- No demo/live approval

