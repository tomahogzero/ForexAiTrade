# Checklist สำหรับ Forward Test

ก่อนเริ่ม demo forward test:

- ตรวจว่า `InpLiveTradingEnabled=true` เฉพาะบนบัญชี demo
- คง `InpDemoSafeMode=true` ไว้ ยกเว้นตั้งใจเตรียมใช้งานจริงอย่างเป็นระบบ
- ตรวจ contract size, tick value, minimum lot และพฤติกรรม spread ของ symbol บน XM MT5
- ตรวจว่า magic number ของ EA ไม่ซ้ำ
- ตรวจเวลา VPS, เวลา broker และความเสถียรของ terminal connection
- รัน visual test ย้อนหลังหลายสัปดาห์
- ตรวจ journal logs เพื่อดู rejected trades และ risk blocks

ระหว่าง demo forward test:

- เฝ้าดู spread spikes
- เฝ้าดู slippage
- บันทึกทุกการเปลี่ยน parameter
- เปรียบเทียบพฤติกรรม demo live กับ backtest ล่าสุด
- อย่าย้ายไป live trading จนกว่า EA จะผ่าน forward period ที่มีนัยสำคัญ
