# Checkpoint AA: Gold Diagnostic User Evidence Checklist

วันที่จัดทำ: 2026-07-04

## วัตถุประสงค์

Checkpoint AA เป็นเอกสารเตรียมหลักฐานก่อนขออนุมัติรัน Gold no-trade diagnostic ใน MT5 Strategy Tester

งานนี้ยังไม่อนุญาตให้รัน MT5 และยังไม่ใช่การทดสอบกลยุทธ์จริง เป้าหมายคือทำให้หลักฐานที่ต้องใช้ก่อน retry มีความชัดเจน ตรวจสอบซ้ำได้ และไม่พึ่งการเดาว่า MT5 เขียน report/log ไว้ที่ไหน

## ขอบเขต

- ไม่แก้ EA/source code
- ไม่แก้ preset
- ไม่แก้ runner
- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่สรุปว่าทำกำไรได้
- ไม่อนุมัติ demo/live trading

## หลักฐานที่ต้องมีจากผู้ใช้ก่อน checkpoint ถัดไป

### 1. Terminal และ Data Folder

ต้องระบุให้ชัดเจน:

- path ของ `terminal64.exe` ที่ใช้จริง
- MT5 Data Folder จากเมนู `File > Open Data Folder`
- ยืนยันว่าเป็น terminal/account เดียวกับที่ manual Strategy Tester เคยรันได้
- ยืนยันว่าใช้ portable mode หรือไม่
- ระบุว่ามี MT5 instance อื่นเปิดอยู่หรือไม่

ถ้าไม่รู้ Data Folder หรือ terminal path ต้องบล็อกการรัน

### 2. Symbol และ History

ต้องยืนยัน:

- Gold symbol จริงใน XM คือ `GOLD#` หรือ `GOLDm#`
- symbol นั้นอยู่ใน Market Watch
- H1 history มีข้อมูลสำหรับช่วงวันที่ที่จะรัน
- date range ต้องไม่เกิน 1 เดือน

ห้าม assume ว่า Gold ทุก broker ใช้ point, tick value, contract size หรือ min lot เหมือนกัน

### 3. Report และ Log Paths

ต้องมี path แบบ absolute:

- report folder ที่สร้างไว้ล่วงหน้า
- marker file ใน report folder เพื่อพิสูจน์ว่าเขียนได้
- expected Strategy Tester report path
- expected terminal log folder
- expected tester agent log folder
- expected EA/mirror log folder

ห้ามใช้ artifact เก่ามาพิสูจน์ผล retry

### 4. Source / Preset Drift Guard

ก่อนรัน checkpoint จริง ต้องยืนยัน:

- exact source branch
- exact commit
- `MQL5/` ไม่มี drift จาก commit ที่ review แล้ว
- `presets/` ไม่มี drift จาก commit ที่ review แล้ว

ถ้า source หรือ preset เปลี่ยน ต้องหยุดและขอ GPT review + approval checkpoint ใหม่

### 5. Effective Config ที่ต้องเห็นก่อนรัน

สำหรับ future Gold no-trade diagnostic ต้องมี config snapshot ที่ยืนยัน:

- Strategy Tester only
- optimization disabled
- `InpRequireStrategyTester=true`
- diagnostics-only mode enabled สำหรับ path ที่จะตรวจ
- ไม่มี market order
- ไม่มี pending order
- ไม่มี position modification
- ไม่ fallback ไป baseline strategy
- no-trade reason ต้อง log ได้

ถ้า config ไม่ตรง ต้องหยุด

## Stop Conditions

ต้องหยุดทันทีถ้า:

- terminal path ไม่ชัดเจน
- data folder ไม่ชัดเจน
- report folder เขียนไม่ได้
- artifact path ไม่ absolute
- symbol Gold จริงยังไม่ยืนยัน
- H1 history ไม่พร้อม
- date range เกิน 1 เดือน
- effective config ไม่ตรง
- optimization เปิดอยู่
- เจอคำสั่ง trade เช่น `OrderSend`, `Buy`, `Sell`, `BuyLimit`, `SellLimit`, `BuyStop`, `SellStop`, `PositionModify`
- มี baseline fallback
- artifact หลังรันไม่ครบ

ถ้า artifact หลังรันไม่ครบ ต้องจัดเป็น `FAILED_NO_TESTER_ARTIFACTS / INCONCLUSIVE`

## สิ่งที่ผู้ใช้ควรส่งกลับมา

เพื่อเตรียม checkpoint ถัดไป ผู้ใช้ควรส่ง:

- screenshot หรือข้อความ path จาก `File > Open Data Folder`
- path ของ `terminal64.exe`
- screenshot Market Watch ที่เห็น `GOLD#` หรือ `GOLDm#`
- screenshot หรือ note ว่า H1 history โหลดได้
- path report folder ที่ต้องการให้ใช้
- ยืนยันว่า MT5 instance อื่นปิดอยู่ หรือระบุว่ามีตัวไหนเปิดอยู่

## ยังไม่ใช่คำอนุมัติรัน

Checkpoint AA ไม่ใช่คำอนุมัติให้รัน MT5

การรันจริงต้องรอ checkpoint ถัดไปที่ระบุ:

- symbol ที่แน่นอน
- timeframe
- date range แบบ `YYYY-MM-DD to YYYY-MM-DD`
- artifact paths ที่ verify แล้ว
- approval phrase ชัดเจนจากผู้ใช้

## คำเตือน

Gold 2-5% ต่อเดือนเป็น aggressive research target เท่านั้น ไม่ใช่คำสัญญาว่าจะทำได้ และไม่ใช่เหตุผลให้เพิ่ม lot หรือ risk

