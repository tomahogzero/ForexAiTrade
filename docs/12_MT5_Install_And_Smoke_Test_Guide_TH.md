# คู่มือติดตั้ง ForexAiTrade ลง MT5 และรัน Smoke Test

เอกสารนี้ใช้สำหรับติดตั้ง EA ลง MetaTrader 5 และทดสอบพฤติกรรมใน Strategy Tester เท่านั้น ไม่ใช่การ optimize parameter และไม่ใช่หลักฐานว่า EA ทำกำไรได้

## คำเตือนสำคัญ

- ห้ามรัน smoke-test preset บนกราฟ live/demo ปกติ
- smoke-test preset ตั้ง `InpLiveTradingEnabled=true` เพื่อให้ Strategy Tester ทดสอบ flow ได้ แต่มี `InpRequireStrategyTester=true` เพื่อบล็อกการใช้นอก Strategy Tester
- smoke test เป็นการตรวจพฤติกรรม ไม่ใช่ profitability proof
- อย่าเปิดใช้บัญชีจริงจากผล smoke test

## วิธีเปิด MT5 Data Folder

1. เปิด XM MT5
2. ไปที่เมนู `File`
3. เลือก `Open Data Folder`
4. Windows Explorer จะเปิดโฟลเดอร์ Data Folder ของ terminal นั้น
5. จำ path นี้ไว้ เพราะต้องใช้กับ script ติดตั้ง

ตัวอย่าง path อาจหน้าตาประมาณนี้:

`C:\Users\<user>\AppData\Roaming\MetaQuotes\Terminal\<terminal-id>`

## วิธีติดตั้งด้วย Script

เปิด PowerShell ที่โฟลเดอร์โปรเจกต์ `ForexAiTrade` แล้วรัน:

```powershell
.\scripts\install_to_mt5.ps1
```

ถ้าต้องการส่ง path เข้าไปโดยตรง:

```powershell
.\scripts\install_to_mt5.ps1 -TargetMt5DataFolder "C:\Users\<user>\AppData\Roaming\MetaQuotes\Terminal\<terminal-id>"
```

Script จะตรวจว่า target folder มี:

- `MQL5\`
- `MQL5\Experts\`
- `MQL5\Include\`

จากนั้นจะ backup ไฟล์เดิมก่อน copy:

- `MQL5\Experts\ForexAiTrade\`
- `MQL5\Include\ForexAiTrade\`

Script จะ copy เฉพาะ active EA source:

- `MQL5\Experts\ForexAiTrade\`
- `MQL5\Include\ForexAiTrade\`

Script จะไม่ copy:

- `archive\`
- `.ex5`
- `__pycache__`
- `.pyc`

## วิธี Compile ใน MetaEditor

1. เปิด MetaEditor
2. เปิดไฟล์ `MQL5\Experts\ForexAiTrade\ForexAiTrade.mq5`
3. กด `Compile` หรือกด `F7`
4. ตรวจผลลัพธ์ด้านล่างของ MetaEditor
5. ต้องได้ `0 errors, 0 warnings`

ถ้ามี error หรือ warning ให้หยุดก่อน อย่ารัน smoke test จนกว่าจะตรวจสาเหตุ

## วิธีรัน No-Trade Sanity Test

เป้าหมายของ sanity test คือยืนยันว่า EA ไม่เปิด order และไม่ modify position เมื่อปิดการเทรดไว้

Preset ที่ใช้:

- `presets\sanity\GOLDm#_H1_no_trade_sanity.set`
- หรือ `presets\sanity\EURUSD_H1_no_trade_sanity.set`

ขั้นตอน:

1. เปิด MT5 Strategy Tester
2. Select Expert: `ForexAiTrade`
3. เลือก symbol เช่น `GOLDm#` หรือ `EURUSD`
4. เลือก timeframe `H1`
5. Load preset จาก `presets\sanity\`
6. Run test
7. เปิด Journal
8. ตรวจว่ามี safety block reason
9. ยืนยันว่าไม่มี order ถูกเปิด
10. ยืนยันว่าไม่มี position ถูก modify

ค่าที่คาดหวัง:

- `InpLiveTradingEnabled=false`
- `InpManageExistingPositions=false`
- Journal ควรมีข้อความประมาณว่า live trading disabled และ position management disabled

## วิธีรัน GOLDm# H1 Smoke Test

เป้าหมายคือทดสอบ behavior ใน Strategy Tester เท่านั้น

ค่าที่แนะนำ:

- Select Expert: `ForexAiTrade`
- Symbol: `GOLDm#`
- Timeframe: `H1`
- Model: `Every tick based on real ticks` ถ้ามี
- Period: เริ่มจาก 3 เดือนล่าสุด
- Deposit: ใช้เงินทดสอบจำนวนน้อย เช่น 1,000 หรือ 10,000
- Preset: `presets\tester\GOLDm#_H1_smoke_test.set`

ขั้นตอน:

1. เปิด Strategy Tester
2. เลือก Expert: `ForexAiTrade`
3. เลือก Symbol: `GOLDm#`
4. เลือก Timeframe: `H1`
5. เลือก Model: `Every tick based on real ticks` ถ้ามี
6. ตั้ง Period เป็น 3 เดือนล่าสุดก่อน
7. ตั้ง Deposit เป็นจำนวนเล็กสำหรับทดสอบ
8. Load preset `GOLDm#_H1_smoke_test.set`
9. Run test
10. Export report
11. ตรวจ Journal
12. ยืนยันว่าไม่มี runaway orders

## ผลลัพธ์ที่คาดหวัง

สิ่งที่ควรเห็น:

- EA compile ผ่านก่อนรัน
- Journal แสดง symbol diagnostics
- Actual symbol เป็น `GOLDm#`
- Canonical symbol เป็น `GOLD`
- ถ้า signal ถูก block ต้องมีเหตุผลชัดเจน
- ถ้ามี signal log ต้องมี entry, SL, TP, raw lot, normalized lot, risk money และ actual risk money
- ไม่มี order burst หรือ runaway behavior

สิ่งที่ไม่ควรเกิด:

- ห้ามมีการใช้งานบน live chart
- ห้ามมีการเปิด order จำนวนมากผิดปกติ
- ห้ามมี lot size ที่เกิน risk budget แบบเงียบๆ
- ห้ามสรุปว่า profitable จาก smoke test

## Screenshot, Log และ Report ที่ควรบันทึก

ควรเก็บ:

- Screenshot หน้า Strategy Tester settings
- Screenshot Inputs tab หลัง load preset
- Screenshot Results tab
- Screenshot Graph tab ถ้ามี
- Screenshot Journal tab ที่เห็นข้อความ ForexAiTrade
- Exported Strategy Tester report เป็น HTML/HTM/XML/CSV/TXT
- Journal หรือ Experts log ที่เกี่ยวข้องกับช่วงทดสอบ

## วิธีรวบรวม Artifacts ด้วย Script

หลัง export report หรือเตรียม screenshot/log แล้ว ให้รัน:

```powershell
.\scripts\collect_smoke_test_artifacts.ps1
```

Script จะสร้างโฟลเดอร์:

`smoke_test_artifacts\yyyyMMdd-HHmmss\`

ถ้า script เก็บไฟล์อัตโนมัติไม่ได้ ให้ copy report, screenshot และ log เข้าโฟลเดอร์นั้นเอง แล้วส่งทั้งโฟลเดอร์กลับมาให้ review

## สิ่งที่ต้องส่งกลับมาเพื่อ Review

- โฟลเดอร์ `smoke_test_artifacts\yyyyMMdd-HHmmss\`
- Exported report
- Journal/Experts logs
- Screenshot settings และ inputs
- หมายเหตุว่าทดสอบ symbol/timeframe/preset อะไร

ย้ำอีกครั้ง: smoke test ไม่ใช่หลักฐานกำไร เป็นแค่การตรวจว่า EA ทำงานถูกต้องใน Strategy Tester และ safety guard ทำงานตามที่ออกแบบไว้
