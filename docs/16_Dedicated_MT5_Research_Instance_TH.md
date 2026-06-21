# การใช้ MT5 Research Instance แยกต่างหาก

เอกสารนี้แนะนำให้ใช้ MT5 แยกสำหรับ research เท่านั้น เพื่อลดความเสี่ยงกับบัญชี demo/live ที่ใช้งานจริง

## เหตุผล

Batch runner จะเปิด MT5 หลายรอบผ่าน command-line Strategy Tester

ไม่ควรใช้ terminal เดียวกับที่มี chart หรือ EA อื่นทำงานอยู่ เพราะอาจรบกวนการใช้งานหรือทำให้ log ปะปนกัน

## หลักความปลอดภัย

- ห้ามรันกับ MT5 ที่ใช้ live trading
- ใช้ MT5 installation แยกสำหรับ research
- ใช้ portable mode ถ้าเป็นไปได้
- runner จะควบคุมเฉพาะ process ID ที่มันเปิดเอง
- runner จะไม่ปิด `terminal64.exe` ตัวอื่นแบบเหมารวม

## ตัวอย่างคำสั่ง Integration Test

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_mt5_research_batch.ps1 `
  -IntegrationOnly `
  -DedicatedTerminalExe "C:\Path\To\ResearchMT5\terminal64.exe" `
  -UsePortableMode `
  -CaseTimeoutMinutes 10
```

## Output

แต่ละเคสจะอยู่ใน:

```text
research\runs\<RunId>\<CaseId>\
```

ไฟล์สำคัญ:

- `case.json`
- `generated_tester.ini`
- `effective_preset.set`
- `process_info.json`
- `runner.log`
- `tester_log_excerpt.log`
- `ea_mirror.log`
- `mt5_report.html`
- `parsed_result.json`
- `status.json`

## คำเตือน

ผล research/backtest ไม่ใช่หลักฐานว่ากำไรในอนาคต ต้องผ่าน validation, out-of-sample และ demo forward test ก่อนเสมอ
