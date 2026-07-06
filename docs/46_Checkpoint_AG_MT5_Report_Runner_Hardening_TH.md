# Checkpoint AG: MT5 Report Runner Hardening

เอกสารนี้สรุปการปรับปรุง runner สำหรับการจัดการไฟล์รายงาน MT5 เท่านั้น ยังไม่มีการรัน MT5, ไม่มีการรัน Strategy Tester, ไม่มีการเปลี่ยน EA, ไม่มีการเปลี่ยน preset และไม่มีการปรับกลยุทธ์เพื่อกำไร

## เป้าหมาย

Checkpoint AG แก้ปัญหาจาก Checkpoint AC/AD/AE ที่ Strategy Tester และ EA mirror log เกิดขึ้น แต่ `mt5_report.htm` ไม่ถูกเก็บกลับเข้ามาใน case artifact folder

เป้าหมายคือทำให้ runner รองรับรูปแบบ report artifact ของ MT5 ได้ชัดเจนขึ้นก่อน retry ครั้งถัดไป

## สิ่งที่เปลี่ยน

- เพิ่มการค้นหา report artifact หลายรูปแบบ:
  - `mt5_report`
  - `mt5_report.htm`
  - `mt5_report.html`
  - `mt5_report.xml`
  - `mt5_report.png`
  - `mt5_report-hst.png`
  - `mt5_report-mfemae.png`
  - `mt5_report-holding.png`
- เมื่อใช้ `-TerminalDataFolder` runner จะยังใช้ report path แบบ relative ใต้ terminal data folder:
  - `ForexAiTradeResearch\<RunId>\<CaseId>\mt5_report`
- สร้าง marker file ใน report folder เพื่อยืนยันว่า path นั้นเขียนได้ก่อนเริ่ม run
- เพิ่ม stale artifact guard โดยยอมรับเฉพาะ report ที่มีเวลาแก้ไขหลังเวลาเริ่ม run
- copy report และ companion graph files กลับไปที่ case folder
- เพิ่ม status fields สำหรับ audit:
  - `report_request_path`
  - `report_search_base_path`
  - `terminal_report_base_path`
  - `terminal_report_path`
  - `copied_report_path`
  - `report_artifact_status`
  - `report_companion_files`
  - `report_preflight_marker_path`
  - `report_found_after_run_start`
  - `stale_report_detected`
- แยกสถานะเมื่อ tester/EA log มีอยู่แต่ report หาย:
  - `PARTIAL_TESTER_PASS_REPORT_MISSING`
- แยกสถานะเมื่อทั้ง report และหลักฐาน tester/EA artifact หาย:
  - `FAILED_NO_TESTER_ARTIFACTS`

## สิ่งที่ไม่ได้ทำ

- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่เปลี่ยน MQL5 EA
- ไม่เปลี่ยน preset
- ไม่ optimize parameters
- ไม่เพิ่ม lot/risk
- ไม่เพิ่มกลยุทธ์ใหม่
- ไม่ claim profitability

## เหตุผล

Checkpoint AE พบว่า report ที่เคย PASS ในอดีตใช้ `Report=ForexAiTradeResearch\...\mt5_report` ซึ่งเป็น relative path ใต้ MT5 data folder และ MT5 สร้างไฟล์จริงเป็น `mt5_report.htm`

Checkpoint AG จึงทำให้ runner ใช้แนวทางนี้อย่างเป็นระบบ และเก็บหลักฐานเพิ่มว่ารายงานที่พบเป็นไฟล์ใหม่จาก run ปัจจุบัน ไม่ใช่ artifact เก่าที่ค้างอยู่

## ข้อจำกัด

การเปลี่ยนนี้ยังไม่พิสูจน์ว่า retry จะสำเร็จ เพราะยังไม่ได้รัน MT5 จริง ต้องมี checkpoint ถัดไปที่ได้รับอนุมัติชัดเจนก่อน execution

## สถานะความปลอดภัย

- Live trading ยังไม่ถูกเปิด
- Strategy Tester safety gate ยังต้องคงอยู่
- Runner ยังต้องหยุดเฉพาะ process ID ที่ตัวเอง start เท่านั้น
- ห้าม kill `terminal64.exe` แบบรวมทั้งหมด
- ผลการวิจัยยังไม่ใช่ proof of profitability

